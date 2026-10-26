"""Speech to text with Gnani Prisma v2.5 (`POST https://api.vachana.ai/stt/v3`).

The request is multipart form data with two fields, `audio_file` and `language_code`, and an
`X-API-Key-ID` header. A successful reply looks like
`{"success": true, "request_id": "...", "transcript": "..."}`; an error reply looks like
`{"success": false, "error": {"type": "...", "message": "..."}}`.

Gnani documents no Tanglish language code. Tanglish speech goes to `ta-IN` by default; the
comparison with `en-IN` on real clips is still to be done.
"""

import io
import wave
from typing import Literal, Protocol

import httpx  # installed with fastapi[standard] (the `api` extra)

from schemebot.config import Settings
from schemebot.voice.budget import CALLS_FILE_NAME, BudgetExhausted, CallBudget, shared_budget

VoiceLanguage = Literal["ta", "hi", "en", "ta-Latn"]

GNANI_LANGUAGE_CODES: dict[VoiceLanguage, str] = {
    "ta": "ta-IN",
    "hi": "hi-IN",
    "en": "en-IN",
    "ta-Latn": "ta-IN",  # untested choice; see the module docstring
}

AUDIO_EXTENSIONS = (".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a")
"""The formats Gnani's STT REST docs list. Browser WebM recordings are not on the list."""


class SttError(Exception):
    """Speech could not be turned into text. `message` is safe to show to the user."""

    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class Transcriber(Protocol):
    def transcribe(self, audio: bytes, filename: str, language_code: str) -> str: ...


def wav_seconds(audio: bytes) -> float | None:
    """Length of a WAV clip in seconds, or None if the bytes are not a readable WAV file."""
    try:
        with wave.open(io.BytesIO(audio)) as clip:
            frames: int = clip.getnframes()
            rate: int = clip.getframerate()
            return frames / rate
    except (wave.Error, EOFError, ZeroDivisionError):
        return None


def flac_seconds(audio: bytes) -> float | None:
    """Length of a FLAC clip from its STREAMINFO header, or None if it cannot be read."""
    # "fLaC", a 4-byte block header, then STREAMINFO; its bytes 10-17 hold the sample rate
    # (20 bits), channels (3), bits per sample (5) and the total number of samples (36).
    if len(audio) < 26 or not audio.startswith(b"fLaC"):
        return None
    packed = int.from_bytes(audio[18:26], "big")
    rate = packed >> 44
    samples = packed & ((1 << 36) - 1)
    if rate == 0 or samples == 0:
        return None
    return samples / rate


def _looks_like(audio: bytes, extension: str) -> bool:
    """Whether the first bytes are those of the format the file name claims."""
    if extension == ".wav":
        return audio[:4] == b"RIFF" and audio[8:12] == b"WAVE"
    if extension == ".flac":
        return audio.startswith(b"fLaC")
    if extension == ".ogg":
        return audio.startswith(b"OggS")
    if extension == ".m4a":
        return audio[4:8] == b"ftyp"
    # MP3 starts with an ID3 tag or a frame sync (11 set bits); AAC with ADTS or ADIF.
    frame_sync = len(audio) > 1 and audio[0] == 0xFF and audio[1] & 0xE0 == 0xE0
    if extension == ".mp3":
        return audio.startswith(b"ID3") or frame_sync
    return audio.startswith(b"ADIF") or frame_sync  # .aac


COMPRESSED_BYTES_PER_SECOND = 48_000
"""384 kbps, above any normal voice recording. MP3, OGG, AAC and M4A lengths are not read
from the file, so a clip larger than this rate allows for `max_seconds` is too long."""


def check_audio(audio: bytes, filename: str, max_bytes: int, max_seconds: float) -> None:
    """Reject clips Gnani would refuse, before spending a credit on them."""
    if not audio:
        raise SttError("The recording is empty.", 400)
    if len(audio) > max_bytes:
        raise SttError("The recording is too large.", 413)
    extension = "." + filename.lower().rpartition(".")[2]
    if extension not in AUDIO_EXTENSIONS:
        raise SttError("Use a WAV, MP3, OGG, FLAC, AAC or M4A file.", 415)
    if not _looks_like(audio, extension):
        raise SttError("This file is not a recording in the format its name says.", 415)
    too_long = SttError(f"Keep the question under {max_seconds:.0f} seconds.", 400)
    if extension in (".wav", ".flac"):
        seconds = wav_seconds(audio) if extension == ".wav" else flac_seconds(audio)
        if seconds is None:
            raise SttError("This recording could not be read. Try recording again.", 415)
        if seconds > max_seconds:
            raise too_long
    elif len(audio) > max_seconds * COMPRESSED_BYTES_PER_SECOND:
        raise too_long


class GnaniStt:
    def __init__(
        self,
        api_key: str,
        url: str,
        timeout_seconds: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        # `transport` lets tests answer requests without touching the network.
        self._client = httpx.Client(
            headers={"X-API-Key-ID": api_key}, timeout=timeout_seconds, transport=transport
        )
        self._url = url

    def transcribe(self, audio: bytes, filename: str, language_code: str) -> str:
        try:
            response = self._client.post(
                self._url,
                data={"language_code": language_code},
                files={"audio_file": (filename, audio)},
            )
        except httpx.HTTPError as error:
            raise SttError("The speech service could not be reached.") from error
        return _read_transcript(response)


def _read_transcript(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        body = {}
    if response.status_code == 429:
        raise SttError("The speech service is busy. Try again in a minute.", 429)
    if response.status_code != 200 or not body.get("success"):
        raise SttError("The speech service could not read this recording.")
    transcript = body.get("transcript")
    if not isinstance(transcript, str):
        raise SttError("The speech service sent an unexpected reply.")
    return transcript.strip()


class BudgetedTranscriber:
    """Counts every call against the daily cap before passing it on to Gnani."""

    def __init__(self, inner: Transcriber, budget: CallBudget) -> None:
        self._inner = inner
        self.budget = budget

    def transcribe(self, audio: bytes, filename: str, language_code: str) -> str:
        try:
            self.budget.take()
        except BudgetExhausted as error:
            raise SttError(
                "Voice input has reached today's limit. You can still type your question.", 503
            ) from error
        return self._inner.transcribe(audio, filename, language_code)


def build_budget(settings: Settings) -> CallBudget:
    """The daily Gnani cap shared by speech to text and text to speech."""
    return shared_budget(settings.log_dir / CALLS_FILE_NAME, settings.gnani_max_calls_per_day)


def build_transcriber(settings: Settings) -> BudgetedTranscriber | None:
    """The capped Gnani client, or None when no key is set (voice input is then off)."""
    if settings.gnani_api_key is None:
        return None
    gnani = GnaniStt(
        settings.gnani_api_key.get_secret_value(),
        settings.gnani_stt_url,
        settings.stt_timeout_seconds,
    )
    return BudgetedTranscriber(gnani, build_budget(settings))
