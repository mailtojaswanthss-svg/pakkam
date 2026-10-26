import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from schemebot.api.audit import question_hash
from schemebot.api.main import REQUEST_ID_HEADER, create_app
from schemebot.api.ratelimit import AskLimiter
from schemebot.api.schemas import MAX_QUESTION_CHARS
from schemebot.generate.answer import Answer, AnswerSentence, Citation
from schemebot.voice.stt import SttError
from schemebot.voice.tts import TtsError
from tests.test_stt import make_wav

QUESTION = "Who can join Atal Pension Yojana? My Aadhaar is 1234 5678 9012"

CITED = Answer(
    question=QUESTION,
    language="en",
    text="Citizens aged 18 to 40 can join. [1]",
    sentences=[AnswerSentence("Citizens aged 18 to 40 can join.", [1])],
    citations=[
        Citation(
            1,
            "apy-brochure-en",
            "Atal Pension Yojana",
            1,
            1,
            "https://pfrda.org.in/apy",
            "Citizens aged 18 to 40 can join the Atal Pension Yojana.",
        )
    ],
    refused=False,
    refusal_reason=None,
    confidence=0.97,
    disclaimer="Informational only.",
    timings_ms={"retrieval": 40.0, "generation": 900.0, "total": 950.0},
)


class FakeService:
    def __init__(self, answer: Answer | None = None, error: Exception | None = None) -> None:
        self.questions: list[str] = []
        self._answer = answer or CITED
        self._error = error

    def answer(self, question: str) -> Answer:
        self.questions.append(question)
        if self._error:
            raise self._error
        return self._answer


@pytest.fixture
def service() -> FakeService:
    return FakeService()


@pytest.fixture
def client(service: FakeService, tmp_path: Path) -> Iterator[TestClient]:
    app = create_app(lambda: service, log_dir=tmp_path)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_returns_cited_answer(client: TestClient) -> None:
    response = client.post("/ask", json={"question": QUESTION})

    assert response.status_code == 200
    body = response.json()
    assert body["refused"] is False
    assert body["sentences"] == [{"text": "Citizens aged 18 to 40 can join.", "citations": [1]}]
    assert body["citations"][0]["doc_id"] == "apy-brochure-en"
    assert body["latency_ms"] == 950.0
    assert response.headers[REQUEST_ID_HEADER]


def test_question_is_trimmed_before_answering(client: TestClient, service: FakeService) -> None:
    client.post("/ask", json={"question": "   APY age limit?  "})

    assert service.questions == ["APY age limit?"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"question": ""},
        {"question": "  a "},
        {"question": "x" * (MAX_QUESTION_CHARS + 1)},
        {"question": 42},
    ],
)
def test_invalid_questions_are_rejected(
    client: TestClient, service: FakeService, payload: dict[str, object]
) -> None:
    response = client.post("/ask", json=payload)

    assert response.status_code == 422
    assert service.questions == []


def test_refusal_is_a_normal_200_response(tmp_path: Path) -> None:
    refused = Answer(
        question=QUESTION,
        language="en",
        text="I couldn't find this in the official scheme documents.",
        sentences=[],
        citations=[],
        refused=True,
        refusal_reason="low_confidence",
        confidence=0.01,
        disclaimer="Informational only.",
        timings_ms={"total": 30.0},
    )
    app = create_app(lambda: FakeService(refused), log_dir=tmp_path)
    with TestClient(app) as client:
        body = client.post("/ask", json={"question": QUESTION}).json()

    assert body["refused"] is True
    assert body["refusal_reason"] == "low_confidence"
    assert body["citations"] == []


def test_internal_error_hides_details(tmp_path: Path) -> None:
    secret = "connection string postgres://admin:hunter2@db"
    app = create_app(lambda: FakeService(error=RuntimeError(secret)), log_dir=tmp_path)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/ask", json={"question": QUESTION})

    assert response.status_code == 500
    assert "hunter2" not in response.text
    assert "Traceback" not in response.text
    assert response.json()["request_id"] == response.headers[REQUEST_ID_HEADER]


def test_audit_log_records_outcome_without_question_text(
    client: TestClient, tmp_path: Path
) -> None:
    response = client.post("/ask", json={"question": QUESTION})

    log = (tmp_path / "requests.jsonl").read_text(encoding="utf-8")
    entry = json.loads(log)
    assert QUESTION not in log
    assert "1234 5678 9012" not in log
    assert entry["question_hash"] == question_hash(QUESTION)
    assert entry["request_id"] == response.headers[REQUEST_ID_HEADER]
    assert entry["cited"] == ["apy-brochure-en:p1"]
    assert entry["refused"] is False


def test_models_are_built_once_at_startup(tmp_path: Path) -> None:
    builds: list[int] = []

    def build() -> FakeService:
        builds.append(1)
        return FakeService()

    with TestClient(create_app(build, log_dir=tmp_path)) as client:
        client.post("/ask", json={"question": QUESTION})
        client.post("/ask", json={"question": QUESTION})

    assert len(builds) == 1


def test_citation_carries_excerpt_language_and_readable_title(client: TestClient) -> None:
    citation = client.post("/ask", json={"question": QUESTION}).json()["citations"][0]

    assert citation["excerpt"] == "Citizens aged 18 to 40 can join the Atal Pension Yojana."
    assert citation["language"] == "unknown"
    assert citation["document"] == "Subscriber information brochure"  # from data/sources.json


def test_sources_lists_every_document_with_a_title(client: TestClient) -> None:
    response = client.get("/sources")

    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 10
    assert all(doc["title"] and doc["source_url"].startswith("https://") for doc in docs)
    assert {"en", "ta", "hi"} <= {doc["language"] for doc in docs}


def test_web_page_is_served_and_api_routes_still_win(service: FakeService, tmp_path: Path) -> None:
    web = tmp_path / "web"
    web.mkdir()
    (web / "index.html").write_text("<!doctype html><title>Pakkam</title>", encoding="utf-8")
    app = create_app(lambda: service, log_dir=tmp_path, web_dir=web)

    with TestClient(app) as client:
        page = client.get("/")
        health = client.get("/health")

    assert page.status_code == 200
    assert "Pakkam" in page.text
    assert health.json() == {"status": "ok"}


def test_webp_photos_are_served_as_images(service: FakeService, tmp_path: Path) -> None:
    web = tmp_path / "web"
    web.mkdir()
    (web / "index.html").write_text("<!doctype html>", encoding="utf-8")
    (web / "photo.webp").write_bytes(b"RIFF\x00\x00\x00\x00WEBP")
    app = create_app(lambda: service, log_dir=tmp_path, web_dir=web)

    with TestClient(app) as client:
        response = client.get("/photo.webp")

    assert response.headers["content-type"] == "image/webp"


def test_too_many_questions_get_429_with_retry_after(service: FakeService, tmp_path: Path) -> None:
    limiter = AskLimiter(per_client_per_minute=2, total_per_day=100)
    app = create_app(lambda: service, log_dir=tmp_path, limiter=limiter)
    with TestClient(app) as test_client:
        for _ in range(2):
            assert test_client.post("/ask", json={"question": QUESTION}).status_code == 200

        response = test_client.post("/ask", json={"question": QUESTION})
        health = test_client.get("/health")

    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0
    assert "Too many questions" in response.json()["detail"]
    assert len(service.questions) == 2
    assert health.status_code == 200


# ---------- POST /ask/voice ----------


class FakeStt:
    def __init__(self, transcript: str = "APY age limit?", error: Exception | None = None) -> None:
        self.calls: list[tuple[str, str]] = []
        self._transcript = transcript
        self._error = error

    def transcribe(self, audio: bytes, filename: str, language_code: str) -> str:
        self.calls.append((filename, language_code))
        if self._error:
            raise self._error
        return self._transcript


def voice_client(service: FakeService, stt: FakeStt | None, log_dir: Path) -> TestClient:
    return TestClient(
        create_app(lambda: service, build_stt=lambda: stt, log_dir=log_dir),
        raise_server_exceptions=False,
    )


def short_wav() -> bytes:
    return make_wav(1)


def test_voice_question_is_transcribed_then_answered(service: FakeService, tmp_path: Path) -> None:
    stt = FakeStt("  APY age limit?  ")
    with voice_client(service, stt, tmp_path) as client:
        response = client.post(
            "/ask/voice",
            files={"audio": ("q.wav", short_wav(), "audio/wav")},
            data={"language": "hi"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["transcript"] == "APY age limit?"
    assert body["stt_language_code"] == "hi-IN"
    assert body["citations"][0]["doc_id"] == "apy-brochure-en"
    assert service.questions == ["APY age limit?"]
    assert stt.calls == [("q.wav", "hi-IN")]


def test_voice_tanglish_uses_tamil_stt(service: FakeService, tmp_path: Path) -> None:
    stt = FakeStt()
    with voice_client(service, stt, tmp_path) as client:
        client.post(
            "/ask/voice",
            files={"audio": ("q.wav", short_wav(), "audio/wav")},
            data={"language": "ta-Latn"},
        )

    assert stt.calls == [("q.wav", "ta-IN")]


def test_voice_is_503_without_a_gnani_key(service: FakeService, tmp_path: Path) -> None:
    with voice_client(service, None, tmp_path) as client:
        response = client.post("/ask/voice", files={"audio": ("q.wav", short_wav(), "audio/wav")})

    assert response.status_code == 503
    assert service.questions == []


def test_voice_rejects_unsupported_format_without_calling_gnani(
    service: FakeService, tmp_path: Path
) -> None:
    stt = FakeStt()
    with voice_client(service, stt, tmp_path) as client:
        response = client.post("/ask/voice", files={"audio": ("q.webm", b"webm", "audio/webm")})

    assert response.status_code == 415
    assert stt.calls == []


def test_voice_with_no_words_heard_is_422(service: FakeService, tmp_path: Path) -> None:
    with voice_client(service, FakeStt(""), tmp_path) as client:
        response = client.post("/ask/voice", files={"audio": ("q.wav", short_wav(), "audio/wav")})

    assert response.status_code == 422
    assert "could not hear" in response.json()["detail"]
    assert service.questions == []


def test_voice_stt_failure_is_reported(service: FakeService, tmp_path: Path) -> None:
    stt = FakeStt(error=SttError("The speech service could not read this recording."))
    with voice_client(service, stt, tmp_path) as client:
        response = client.post("/ask/voice", files={"audio": ("q.wav", short_wav(), "audio/wav")})

    assert response.status_code == 502
    assert response.json()["detail"] == "The speech service could not read this recording."


def test_voice_rejects_unknown_language(service: FakeService, tmp_path: Path) -> None:
    stt = FakeStt()
    with voice_client(service, stt, tmp_path) as client:
        response = client.post(
            "/ask/voice",
            files={"audio": ("q.wav", short_wav(), "audio/wav")},
            data={"language": "fr"},
        )

    assert response.status_code == 422
    assert stt.calls == []


# ---------- POST /speak ----------


class FakeTts:
    def __init__(self, error: Exception | None = None) -> None:
        self.calls: list[tuple[str, str]] = []
        self._error = error

    def speak(self, text: str, language_code: str) -> bytes:
        self.calls.append((text, language_code))
        if self._error:
            raise self._error
        return b"RIFF-fake-wav"


def speak_client(service: FakeService, tts: FakeTts | None, log_dir: Path) -> TestClient:
    return TestClient(
        create_app(lambda: service, build_stt=lambda: None, build_tts=lambda: tts, log_dir=log_dir),
        raise_server_exceptions=False,
    )


def test_speak_returns_wav_without_citation_markers(service: FakeService, tmp_path: Path) -> None:
    tts = FakeTts()
    with speak_client(service, tts, tmp_path) as client:
        response = client.post(
            "/speak", json={"text": "Citizens aged 18 to 40 can join. [1] [2]", "language": "en"}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert response.content == b"RIFF-fake-wav"
    assert tts.calls == [("Citizens aged 18 to 40 can join.", "en-IN")]


def test_speak_tanglish_uses_a_tamil_voice(service: FakeService, tmp_path: Path) -> None:
    tts = FakeTts()
    with speak_client(service, tts, tmp_path) as client:
        client.post("/speak", json={"text": "PM Kisan la 6000 kidaikum", "language": "ta-Latn"})

    assert tts.calls[0][1] == "ta-IN"


def test_speak_is_503_until_tts_is_set_up(service: FakeService, tmp_path: Path) -> None:
    with speak_client(service, None, tmp_path) as client:
        response = client.post("/speak", json={"text": "hello", "language": "en"})

    assert response.status_code == 503


@pytest.mark.parametrize(("text", "status"), [("[1]", 422), ("", 422), ("word " * 400, 413)])
def test_speak_rejects_empty_or_long_text(
    service: FakeService, tmp_path: Path, text: str, status: int
) -> None:
    tts = FakeTts()
    with speak_client(service, tts, tmp_path) as client:
        response = client.post("/speak", json={"text": text, "language": "en"})

    assert response.status_code == status
    assert tts.calls == []


def test_speak_reports_tts_failure(service: FakeService, tmp_path: Path) -> None:
    tts = FakeTts(TtsError("Spoken answers have reached today's limit.", 503))
    with speak_client(service, tts, tmp_path) as client:
        response = client.post("/speak", json={"text": "hello", "language": "en"})

    assert response.status_code == 503
    assert response.json()["detail"] == "Spoken answers have reached today's limit."


def test_speak_does_not_log_text(service: FakeService, tmp_path: Path) -> None:
    with speak_client(service, FakeTts(), tmp_path) as client:
        client.post("/speak", json={"text": "my secret question text", "language": "en"})

    logged = "".join(path.read_text() for path in tmp_path.rglob("*") if path.is_file())
    assert "secret" not in logged


# ---------- timings: numbers only ----------


def audit_lines(log_dir: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in (log_dir / "requests.jsonl").read_text().splitlines()]


def test_ask_returns_stage_timings(client: TestClient) -> None:
    body = client.post("/ask", json={"question": QUESTION}).json()

    assert body["timings_ms"] == {"retrieval": 40.0, "generation": 900.0, "total": 950.0}


def test_voice_adds_stt_timing_to_response_and_log(service: FakeService, tmp_path: Path) -> None:
    with voice_client(service, FakeStt(), tmp_path) as client:
        body = client.post(
            "/ask/voice", files={"audio": ("q.wav", short_wav(), "audio/wav")}
        ).json()

    assert body["timings_ms"]["stt"] == body["stt_ms"]
    assert body["timings_ms"]["total"] == 950.0
    [entry] = audit_lines(tmp_path)
    assert set(entry["timings_ms"]) == {"retrieval", "generation", "total", "stt"}  # type: ignore[arg-type]


def test_speak_logs_tts_timing_without_text(service: FakeService, tmp_path: Path) -> None:
    with speak_client(service, FakeTts(), tmp_path) as client:
        response = client.post("/speak", json={"text": "Citizens can join. [1]", "language": "ta"})

    assert response.headers["Server-Timing"].startswith("tts;dur=")
    [entry] = audit_lines(tmp_path)
    assert entry["kind"] == "speech"
    assert entry["chars"] == len("Citizens can join.")
    assert entry["language_code"] == "ta-IN"
    assert set(entry["timings_ms"]) == {"tts"}  # type: ignore[arg-type]
    assert "Citizens" not in (tmp_path / "requests.jsonl").read_text()
