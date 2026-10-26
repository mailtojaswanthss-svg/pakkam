"""Text to speech with Gnani Timbre (`POST https://api.vachana.ai/api/v1/tts/inference`).

The request is JSON (`text`, `model`, `voice`, `language`, `audio_config`) with an
`X-API-Key-ID` header. A successful reply is the audio itself (WAV here), not JSON; an error
reply is JSON: `{"success": false, "error": {"type": "...", "message": "..."}}`.

Voice IDs belong to one model: a timbre-v2.5 voice sent with timbre-v3.0 is a 400 error.
Nothing is sent until `SCHEMEBOT_TTS_MODEL` is set, so the model is always a deliberate choice.

Tanglish answers are spoken with a Tamil (ta-IN) voice. Whether a Tamil voice reads Tamil
written in Latin letters well is untested.
"""

from typing import Protocol

import httpx  # installed with fastapi[standard] (the `api` extra)

from schemebot.config import Settings, TimbreModel
from schemebot.voice.budget import BudgetExhausted, CallBudget
from schemebot.voice.stt import build_budget

ANSWER_LANGUAGE_CODES = {"ta": "ta-IN", "ta-Latn": "ta-IN", "hi": "hi-IN", "en": "en-IN"}
"""Answer language -> Gnani language. Anything else (e.g. "unknown") is spoken as en-IN."""

# A default voice per language for each model, from Gnani's voice list (26 Oct 2026).
# Override with SCHEMEBOT_TTS_VOICE_TA / _HI / _EN.
DEFAULT_VOICES: dict[TimbreModel, dict[str, str]] = {
    "timbre-v2.5": {"ta-IN": "Asmita", "hi-IN": "Nalini", "en-IN": "Kaveri"},
    "timbre-v3.0": {"ta-IN": "Shivani", "hi-IN": "Shivani", "en-IN": "Shivani"},
}

AUDIO_CONFIG = {
    "sample_rate": 24000,
    "num_channels": 1,
    "sample_width": 2,
    "encoding": "linear_pcm",
    "container": "wav",
}


class TtsError(Exception):
    """Speech could not be made. `message` is safe to show to the user."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class Speaker(Protocol):
    def speak(self, text: str, language_code: str) -> bytes: ...


def language_code_for(answer_language: str) -> str:
    return ANSWER_LANGUAGE_CODES.get(answer_language, "en-IN")


class GnaniTts:
    def __init__(
        self,
        api_key: str,
        url: str,
        model: TimbreModel,
        voices: dict[str, str],
        timeout_seconds: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        # `transport` lets tests answer requests without touching the network.
        self._client = httpx.Client(
            headers={"X-API-Key-ID": api_key}, timeout=timeout_seconds, transport=transport
        )
        self._url = url
        self._model = model
        self._voices = voices

    def speak(self, text: str, language_code: str) -> bytes:
        body = {
            "text": text,
            "model": self._model,
            "voice": self._voices[language_code],
            "language": language_code,
            "audio_config": AUDIO_CONFIG,
        }
        try:
            response = self._client.post(self._url, json=body)
        except httpx.HTTPError as error:
            raise TtsError("The speech service could not be reached.") from error
        return _read_audio(response)


def _read_audio(response: httpx.Response) -> bytes:
    if response.status_code == 429:
        raise TtsError("The speech service is busy. Try again in a minute.", 429)
    content_type = response.headers.get("content-type", "")
    if response.status_code != 200 or not content_type.startswith("audio/"):
        raise TtsError("The speech service could not read this answer aloud.")
    if not response.content:
        raise TtsError("The speech service sent empty audio.")
    return response.content


class BudgetedSpeaker:
    """Counts every call against the daily cap (shared with speech to text) first."""

    def __init__(self, inner: Speaker, budget: CallBudget) -> None:
        self._inner = inner
        self.budget = budget

    def speak(self, text: str, language_code: str) -> bytes:
        try:
            self.budget.take()
        except BudgetExhausted as error:
            raise TtsError(
                "Spoken answers have reached today's limit. The answer is still on screen.", 503
            ) from error
        return self._inner.speak(text, language_code)


def voices_for(settings: Settings, model: TimbreModel) -> dict[str, str]:
    voices = dict(DEFAULT_VOICES[model])
    overrides = {
        "ta-IN": settings.tts_voice_ta,
        "hi-IN": settings.tts_voice_hi,
        "en-IN": settings.tts_voice_en,
    }
    voices.update({code: voice for code, voice in overrides.items() if voice})
    return voices


def build_speaker(settings: Settings) -> BudgetedSpeaker | None:
    """The capped Timbre client, or None when there is no key or no model chosen yet."""
    if settings.gnani_api_key is None or settings.tts_model is None:
        return None
    gnani = GnaniTts(
        settings.gnani_api_key.get_secret_value(),
        settings.gnani_tts_url,
        settings.tts_model,
        voices_for(settings, settings.tts_model),
        settings.stt_timeout_seconds,
    )
    return BudgetedSpeaker(gnani, build_budget(settings))
