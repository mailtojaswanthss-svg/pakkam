import json
from datetime import date
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr, ValidationError

from schemebot.config import Settings
from schemebot.voice.budget import CallBudget
from schemebot.voice.stt import BudgetedTranscriber
from schemebot.voice.tts import (
    BudgetedSpeaker,
    GnaniTts,
    TtsError,
    build_speaker,
    language_code_for,
    voices_for,
)

URL = "https://tts.example/api/v1/tts/inference"
VOICES = {"ta-IN": "Asmita", "hi-IN": "Nalini", "en-IN": "Kaveri"}
FAKE_WAV = b"RIFF....WAVEfmt "


def client_replying(
    status: int, content: bytes, content_type: str, seen: list[httpx.Request]
) -> GnaniTts:
    def reply(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(status, content=content, headers={"content-type": content_type})

    return GnaniTts("test-key", URL, "timbre-v2.5", VOICES, transport=httpx.MockTransport(reply))


def test_speak_sends_model_voice_and_language() -> None:
    seen: list[httpx.Request] = []
    tts = client_replying(200, FAKE_WAV, "audio/wav", seen)

    audio = tts.speak("வணக்கம்", "ta-IN")

    assert audio == FAKE_WAV
    request = seen[0]
    assert request.headers["X-API-Key-ID"] == "test-key"
    body = json.loads(request.content)
    assert body["text"] == "வணக்கம்"
    assert body["model"] == "timbre-v2.5"
    assert body["voice"] == "Asmita"
    assert body["language"] == "ta-IN"
    assert body["audio_config"]["container"] == "wav"


@pytest.mark.parametrize(
    ("status", "content", "content_type", "expected_status"),
    [
        (400, b'{"success": false}', "application/json", 502),
        (429, b'{"success": false}', "application/json", 429),
        (200, b'{"success": true}', "application/json", 502),
        (200, b"", "audio/wav", 502),
    ],
)
def test_speak_turns_errors_into_tts_error(
    status: int, content: bytes, content_type: str, expected_status: int
) -> None:
    tts = client_replying(status, content, content_type, [])

    with pytest.raises(TtsError) as caught:
        tts.speak("hello", "en-IN")
    assert caught.value.status_code == expected_status


def test_speak_handles_network_failure() -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    tts = GnaniTts("k", URL, "timbre-v3.0", VOICES, transport=httpx.MockTransport(fail))

    with pytest.raises(TtsError, match="could not be reached"):
        tts.speak("hello", "en-IN")


@pytest.mark.parametrize(
    ("language", "code"),
    [("ta", "ta-IN"), ("ta-Latn", "ta-IN"), ("hi", "hi-IN"), ("en", "en-IN"), ("unknown", "en-IN")],
)
def test_tanglish_answers_are_spoken_in_tamil(language: str, code: str) -> None:
    assert language_code_for(language) == code


def test_voices_follow_the_model_and_overrides() -> None:
    settings = Settings(_env_file=None, tts_voice_hi="Deepak")

    assert voices_for(settings, "timbre-v2.5") == {
        "ta-IN": "Asmita",
        "hi-IN": "Deepak",
        "en-IN": "Kaveri",
    }
    assert voices_for(Settings(_env_file=None), "timbre-v3.0")["ta-IN"] == "Shivani"


def test_tts_is_off_until_a_model_is_chosen() -> None:
    key = SecretStr("k")
    assert build_speaker(Settings(_env_file=None, gnani_api_key=key)) is None
    assert build_speaker(Settings(_env_file=None, tts_model="timbre-v2.5")) is None
    chosen = Settings(_env_file=None, gnani_api_key=key, tts_model="timbre-v2.5")
    assert build_speaker(chosen) is not None


def test_empty_env_values_mean_not_set() -> None:
    settings = Settings(_env_file=None, gnani_api_key="", tts_model="", tts_voice_ta=" ")

    assert settings.gnani_api_key is None
    assert settings.tts_model is None
    assert settings.tts_voice_ta is None


def test_unknown_model_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, tts_model="timbre-v9")


class CountingFake:
    def __init__(self) -> None:
        self.calls = 0

    def speak(self, text: str, language_code: str) -> bytes:
        self.calls += 1
        return FAKE_WAV

    def transcribe(self, audio: bytes, filename: str, language_code: str) -> str:
        self.calls += 1
        return "text"


def test_speech_in_and_out_share_one_daily_cap(tmp_path: Path) -> None:
    budget = CallBudget(tmp_path / "calls.json", 2, lambda: date(2026, 10, 26))
    fake = CountingFake()
    stt = BudgetedTranscriber(fake, budget)
    tts = BudgetedSpeaker(fake, budget)

    stt.transcribe(b"a", "q.wav", "ta-IN")
    tts.speak("answer", "ta-IN")

    with pytest.raises(TtsError) as caught:
        tts.speak("again", "ta-IN")
    assert caught.value.status_code == 503
    assert fake.calls == 2
