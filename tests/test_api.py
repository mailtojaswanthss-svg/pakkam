import json
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from schemebot.api.audit import question_hash
from schemebot.api.main import REQUEST_ID_HEADER, create_app
from schemebot.api.ratelimit import AskLimiter
from schemebot.api.schemas import MAX_QUESTION_CHARS
from schemebot.generate.answer import Answer, AnswerSentence, Citation
from schemebot.generate.contacts import Contact
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
        self.retriever: Any = None

    def answer(self, question: str, voice_mode: bool = False) -> Answer:
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
    assert response.json()["status"] == "ok"


class MeetingService(FakeService):
    """Each answer waits until a second one is running too; fails if answers take turns."""

    def __init__(self) -> None:
        super().__init__()
        self._both_running = threading.Barrier(2, timeout=5)

    def answer(self, question: str, voice_mode: bool = False) -> Answer:
        self._both_running.wait()
        return super().answer(question)


def test_two_questions_are_answered_at_the_same_time(tmp_path: Path) -> None:
    # The GPU lock lives in the retriever; the API must not hold a lock over the LLM calls.
    app = create_app(MeetingService, log_dir=tmp_path)
    statuses: list[int] = []
    with TestClient(app, raise_server_exceptions=False) as test_client:

        def ask() -> None:
            statuses.append(test_client.post("/ask", json={"question": QUESTION}).status_code)

        threads = [threading.Thread(target=ask) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    assert statuses == [200, 200]


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
    assert body["contact"] is None


def test_refusal_carries_the_scheme_contact(tmp_path: Path) -> None:
    contact = Contact(
        scheme="PM-KISAN", helpline=None, helpline_source=None, website="https://pmkisan.gov.in"
    )
    refused = Answer(
        question=QUESTION,
        language="en",
        text="I couldn't find this. For help with PM-KISAN, visit https://pmkisan.gov.in/.",
        sentences=[],
        citations=[],
        refused=True,
        refusal_reason="not_in_documents",
        confidence=0.6,
        disclaimer="Informational only.",
        contact=contact,
    )
    app = create_app(lambda: FakeService(refused), log_dir=tmp_path)
    with TestClient(app) as client:
        body = client.post("/ask", json={"question": QUESTION}).json()

    assert body["contact"] == {
        "scheme": "PM-KISAN",
        "website": "https://pmkisan.gov.in/",
        "helpline": None,
    }


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
    assert health.json()["status"] == "ok"


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


def test_daily_limit_says_come_back_tomorrow(service: FakeService, tmp_path: Path) -> None:
    # "Wait a minute" would be wrong here: the next slot can be many hours away.
    limiter = AskLimiter(per_client_per_minute=10, total_per_day=1)
    app = create_app(lambda: service, log_dir=tmp_path, limiter=limiter)
    with TestClient(app) as test_client:
        test_client.post("/ask", json={"question": QUESTION})
        response = test_client.post("/ask", json={"question": QUESTION})

    assert response.status_code == 429
    assert "tomorrow" in response.json()["detail"]
    assert int(response.headers["Retry-After"]) > 3600


# ---------- POST /ask/voice ----------


class FakeStt:
    def __init__(self, transcript: str = "APY age limit?", error: Exception | None = None) -> None:
        self.calls: list[tuple[str, str]] = []
        self._transcript = transcript
        self._error = error
        self.retriever: Any = None

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
        self.retriever: Any = None

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
    assert set(entry["timings_ms"]) == {"retrieval", "generation", "total", "stt"}  # type: ignore[call-overload]


def test_speak_logs_tts_timing_without_text(service: FakeService, tmp_path: Path) -> None:
    with speak_client(service, FakeTts(), tmp_path) as client:
        response = client.post("/speak", json={"text": "Citizens can join. [1]", "language": "ta"})

    assert response.headers["Server-Timing"].startswith("tts;dur=")
    [entry] = audit_lines(tmp_path)
    assert entry["kind"] == "speech"
    assert entry["chars"] == len("Citizens can join.")
    assert entry["language_code"] == "ta-IN"
    assert set(entry["timings_ms"]) == {"tts"}  # type: ignore[call-overload]
    assert "Citizens" not in (tmp_path / "requests.jsonl").read_text()


def test_speak_spells_amounts_only_when_switched_on(
    service: FakeService, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import schemebot.api.main as main_module
    from schemebot.config import Settings

    body = {"text": "Rs.6000 a year. [1]", "language": "ta"}
    tts = FakeTts()
    with speak_client(service, tts, tmp_path) as client:
        client.post("/speak", json=body)
        monkeypatch.setattr(
            main_module, "get_settings", lambda: Settings(_env_file=None, tts_spell_amounts=True)
        )
        client.post("/speak", json=body)

    assert [text for text, _ in tts.calls] == ["Rs.6000 a year.", "ஆறு ஆயிரம் ரூபாய் a year."]


# ---------- /transcribe: speech to text on its own, so the page shows it at once ----------


def test_transcribe_returns_the_text_without_answering(
    service: FakeService, tmp_path: Path
) -> None:
    stt = FakeStt("  APY age limit?  ")
    with voice_client(service, stt, tmp_path) as client:
        response = client.post(
            "/transcribe",
            files={"audio": ("q.wav", short_wav(), "audio/wav")},
            data={"language": "ta-Latn"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["transcript"] == "APY age limit?"
    assert body["stt_language_code"] == "ta-IN"
    assert body["stt_ms"] >= 0
    assert stt.calls == [("q.wav", "ta-IN")]
    assert service.questions == []  # no answer, no LLM call
    [entry] = audit_lines(tmp_path)
    assert entry["kind"] == "transcript"
    timings = entry["timings_ms"]
    assert isinstance(timings, dict) and set(timings) == {"stt"}
    assert "APY" not in (tmp_path / "requests.jsonl").read_text()


@pytest.mark.parametrize(
    ("stt", "status"),
    [(None, 503), (FakeStt("a"), 422), (FakeStt(error=SttError("Gnani is down.", 502)), 502)],
)
def test_transcribe_errors_match_ask_voice(
    service: FakeService, tmp_path: Path, stt: FakeStt | None, status: int
) -> None:
    with voice_client(service, stt, tmp_path) as client:
        response = client.post("/transcribe", files={"audio": ("q.wav", short_wav(), "audio/wav")})

    assert response.status_code == status
    assert isinstance(response.json()["detail"], str)


def test_transcribe_has_its_own_rate_limit(service: FakeService, tmp_path: Path) -> None:
    app = create_app(
        lambda: service,
        build_stt=FakeStt,
        log_dir=tmp_path,
        limiter=AskLimiter(per_client_per_minute=1, total_per_day=100),
        transcribe_limiter=AskLimiter(per_client_per_minute=1, total_per_day=100),
    )
    clip = {"audio": ("q.wav", short_wav(), "audio/wav")}
    with TestClient(app) as client:
        # One voice question is one /transcribe and one /ask: both pass.
        assert client.post("/transcribe", files=clip).status_code == 200
        assert client.post("/ask", json={"question": QUESTION}).status_code == 200
        assert client.post("/transcribe", files=clip).status_code == 429


def test_ask_model_unavailable_returns_fallback_passages(tmp_path: Path) -> None:
    import datetime

    from schemebot.ingest.models import Chunk
    from schemebot.retrieve.retriever import RetrievedPassage

    chunk = Chunk(
        chunk_id="apy-brochure-en:p1:c0",
        doc_id="apy-brochure-en",
        scheme="Atal Pension Yojana",
        source_url="https://pfrda.org.in/apy",
        page_start=1,
        page_end=1,
        section="Eligibility",
        language="en",
        doc_date=datetime.date(2024, 1, 1),
        text="Sample official passage text",
        extraction="original",
    )
    passage = RetrievedPassage(chunk=chunk, relevance=0.95)
    unavailable_answer = Answer(
        question="What is APY?",
        language="en",
        text="Model is temporarily down. Please refer to official sources.",
        sentences=[],
        citations=[],
        refused=True,
        refusal_reason="service_unavailable",
        confidence=0.95,
        disclaimer="Informational only.",
        contact=Contact(
            scheme="Atal Pension Yojana",
            helpline="1800-110-069",
            helpline_source="apy-brochure-en:p1",
            website="https://pfrda.org.in",
        ),
        passages=[passage],
    )
    svc = FakeService(answer=unavailable_answer)
    with TestClient(create_app(lambda: svc, log_dir=tmp_path)) as client:
        res = client.post("/ask", json={"question": "What is APY?"})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "MODEL_UNAVAILABLE"
        assert data["path"] == "fallback"
        assert len(data["passages"]) == 1
        assert data["passages"][0]["scheme"] == "Atal Pension Yojana"
        assert data["passages"][0]["text"] == "Sample official passage text"
        assert data["contact"]["scheme"] == "Atal Pension Yojana"


def test_ask_sources_returns_passages(tmp_path: Path) -> None:
    import datetime

    from schemebot.ingest.models import Chunk
    from schemebot.retrieve.retriever import RetrievalResult, RetrievedPassage

    class FakeRetriever:
        def retrieve(self, question: str) -> RetrievalResult:
            chunk = Chunk(
                chunk_id="apy-brochure-en:p1:c0",
                doc_id="apy-brochure-en",
                scheme="Atal Pension Yojana",
                source_url="https://pfrda.org.in/apy",
                page_start=1,
                page_end=1,
                section="Eligibility",
                language="en",
                doc_date=datetime.date(2024, 1, 1),
                text="Direct retrieval passage",
                extraction="original",
            )
            passage = RetrievedPassage(chunk=chunk, relevance=0.95)
            return RetrievalResult(
                query=question, passages=[passage], timings_ms={"retrieval": 15.0}
            )

    svc = FakeService()
    svc.retriever = FakeRetriever()
    with TestClient(create_app(lambda: svc, log_dir=tmp_path)) as client:
        res = client.post("/ask/sources", json={"question": "What is APY?"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["passages"]) == 1
        assert data["passages"][0]["scheme"] == "Atal Pension Yojana"
        assert data["passages"][0]["text"] == "Direct retrieval passage"
        assert "retrieval" in data["timings_ms"]


def test_ask_sources_503_when_no_retriever(tmp_path: Path) -> None:
    svc = FakeService()
    with TestClient(create_app(lambda: svc, log_dir=tmp_path)) as client:
        res = client.post("/ask/sources", json={"question": "What is APY?"})
        assert res.status_code == 503
