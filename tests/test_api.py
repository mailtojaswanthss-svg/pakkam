import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from schemebot.api.audit import question_hash
from schemebot.api.main import REQUEST_ID_HEADER, create_app
from schemebot.api.schemas import MAX_QUESTION_CHARS
from schemebot.generate.answer import Answer, AnswerSentence, Citation

QUESTION = "Who can join Atal Pension Yojana? My Aadhaar is 1234 5678 9012"

CITED = Answer(
    question=QUESTION,
    language="en",
    text="Citizens aged 18 to 40 can join. [1]",
    sentences=[AnswerSentence("Citizens aged 18 to 40 can join.", [1])],
    citations=[
        Citation(1, "apy-brochure-en", "Atal Pension Yojana", 1, 1, "https://pfrda.org.in/apy")
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
