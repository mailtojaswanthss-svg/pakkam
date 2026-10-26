import io
import json
import wave

import httpx
import pytest
from pydantic import SecretStr

from schemebot.config import Settings
from schemebot.voice.stt import (
    GNANI_LANGUAGE_CODES,
    GnaniStt,
    SttError,
    build_transcriber,
    check_audio,
    wav_seconds,
)

URL = "https://stt.example/stt/v3"


def make_wav(seconds: float, rate: int = 16000) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as clip:
        clip.setnchannels(1)
        clip.setsampwidth(2)
        clip.setframerate(rate)
        clip.writeframes(b"\x00\x00" * int(seconds * rate))
    return buffer.getvalue()


def client_replying(status: int, body: object, seen: list[httpx.Request]) -> GnaniStt:
    def reply(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(status, content=json.dumps(body).encode())

    return GnaniStt("test-key", URL, transport=httpx.MockTransport(reply))


def test_wav_seconds_reads_length() -> None:
    assert wav_seconds(make_wav(2.5)) == pytest.approx(2.5)


def test_wav_seconds_is_none_for_other_formats() -> None:
    assert wav_seconds(b"ID3 not a wav file") is None


def test_check_audio_accepts_short_wav() -> None:
    check_audio(make_wav(3), "q.wav", max_bytes=5_000_000, max_seconds=30)


@pytest.mark.parametrize(
    ("audio", "filename", "status"),
    [
        (b"", "q.wav", 400),
        (b"x" * 101, "q.mp3", 413),
        (b"webm bytes", "q.webm", 415),
        (make_wav(31, rate=8000), "q.wav", 400),
    ],
)
def test_check_audio_rejects_bad_clips(audio: bytes, filename: str, status: int) -> None:
    max_bytes = 100 if status == 413 else 5_000_000
    with pytest.raises(SttError) as caught:
        check_audio(audio, filename, max_bytes=max_bytes, max_seconds=30)
    assert caught.value.status_code == status


def test_transcribe_sends_key_language_and_file() -> None:
    seen: list[httpx.Request] = []
    stt = client_replying(200, {"success": True, "transcript": " PM Kisan evlo "}, seen)

    text = stt.transcribe(b"audio-bytes", "q.wav", "ta-IN")

    assert text == "PM Kisan evlo"
    request = seen[0]
    assert str(request.url) == URL
    assert request.headers["X-API-Key-ID"] == "test-key"
    body = request.read()
    assert b'name="language_code"' in body and b"ta-IN" in body
    assert b'name="audio_file"; filename="q.wav"' in body and b"audio-bytes" in body


@pytest.mark.parametrize(
    ("status", "body", "expected_status"),
    [
        (400, {"success": False, "error": {"type": "INVALID_REQUEST_ERROR"}}, 502),
        (403, {"success": False, "error": {"type": "FORBIDDEN"}}, 502),
        (429, {"success": False, "error": {"type": "RATE_LIMIT_ERROR"}}, 429),
        (200, {"success": True}, 502),
        (200, {"success": False}, 502),
    ],
)
def test_transcribe_turns_errors_into_stt_error(
    status: int, body: object, expected_status: int
) -> None:
    stt = client_replying(status, body, [])

    with pytest.raises(SttError) as caught:
        stt.transcribe(b"audio", "q.wav", "en-IN")
    assert caught.value.status_code == expected_status


def test_transcribe_handles_network_failure() -> None:
    def fail(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=request)

    stt = GnaniStt("k", URL, transport=httpx.MockTransport(fail))

    with pytest.raises(SttError, match="could not be reached"):
        stt.transcribe(b"audio", "q.wav", "hi-IN")


def test_tanglish_is_sent_as_tamil() -> None:
    assert GNANI_LANGUAGE_CODES["ta-Latn"] == "ta-IN"


def test_no_key_means_no_transcriber() -> None:
    assert build_transcriber(Settings(_env_file=None, gnani_api_key=None)) is None
    assert build_transcriber(Settings(_env_file=None, gnani_api_key=SecretStr("k"))) is not None
