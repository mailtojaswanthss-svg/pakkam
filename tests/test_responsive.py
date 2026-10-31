"""Follow-up questions, search reuse, voice answers and the separate endpoint limits."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from schemebot.api.main import create_app
from schemebot.api.ratelimit import AskLimiter
from schemebot.generate.answer import Answer, Answerer, FollowUp
from schemebot.generate.cache import CachedAnswerer
from schemebot.index.store import build_index, open_client
from schemebot.ingest.models import Chunk
from schemebot.retrieve.hybrid import HybridRetriever
from schemebot.retrieve.retriever import Retriever
from tests.conftest import FakeEncoder, FakeReranker
from tests.test_answer import FakeLlm, sentences


class CountingRetriever:
    def __init__(self, inner: Retriever) -> None:
        self.inner = inner
        self.queries: list[str] = []

    def retrieve(self, query: str) -> Any:
        self.queries.append(query)
        return self.inner.retrieve(query)


def make_answerer(corpus: list[Chunk], llm: FakeLlm) -> tuple[Answerer, CountingRetriever]:
    client = open_client(None)
    encoder = FakeEncoder()
    build_index(client, "test", corpus, encoder)
    retriever = CountingRetriever(
        Retriever(HybridRetriever(client, "test", encoder, 10), FakeReranker(), 5, 3)
    )
    return Answerer(retriever, llm, verifier=None, refusal_threshold=0.3), retriever  # type: ignore[arg-type]


def test_sources_then_answer_searches_once(corpus: list[Chunk]) -> None:
    llm = FakeLlm(sentences(("PM-KISAN pays Rs 6000 per year.", [1])))
    answerer, retriever = make_answerer(corpus, llm)
    question = "How much does PM-KISAN pay per year?"

    answerer.sources(question)
    answer = answerer.answer(question)

    assert not answer.refused
    assert len(retriever.queries) == 1  # /ask reused what /ask/sources found


def test_follow_up_searches_with_the_previous_scheme(corpus: list[Chunk]) -> None:
    llm = FakeLlm(sentences(("PM-KISAN pays Rs 6000 per year.", [1])))
    answerer, retriever = make_answerer(corpus, llm)

    answerer.answer(
        "how much per year?",
        follow_up=FollowUp(question="Who can get PM-KISAN?", scheme="PM-KISAN"),
    )

    assert "PM-KISAN" in retriever.queries[-1]
    assert "<earlier_question>\nWho can get PM-KISAN?" in llm.user_messages[-1]


def test_follow_up_that_names_its_own_scheme_is_left_alone(corpus: list[Chunk]) -> None:
    answerer, _ = make_answerer(corpus, FakeLlm(sentences(("x", [1]))))
    query = answerer.search_query("Atal Pension age limit", FollowUp(scheme="PM-KISAN"))
    # No alias table in this test, so the previous scheme is appended unless already named.
    assert query.endswith("PM-KISAN")
    assert (
        answerer.search_query("PM-KISAN amount", FollowUp(scheme="PM-KISAN")).count("PM-KISAN") == 1
    )


class TypeErrorService:
    def __init__(self) -> None:
        self.calls = 0

    def answer(self, question: str, voice_mode: bool = False) -> Answer:
        self.calls += 1
        raise TypeError("a bug inside the pipeline")


def test_cache_does_not_rerun_the_pipeline_on_an_internal_type_error() -> None:
    service = TypeErrorService()
    with pytest.raises(TypeError):
        CachedAnswerer(service).answer("q", voice_mode=True)
    assert service.calls == 1


def test_cache_key_depends_on_the_follow_up_scheme() -> None:
    seen: list[FollowUp | None] = []

    class Service:
        def answer(
            self, question: str, voice_mode: bool = False, follow_up: FollowUp | None = None
        ) -> Answer:
            seen.append(follow_up)
            return _answer(question)

    cached = CachedAnswerer(Service())
    cached.answer("how do I apply?", follow_up=FollowUp(scheme="PM-KISAN"))
    cached.answer("how do I apply?", follow_up=FollowUp(scheme="Ujjwala"))
    cached.answer("how do I apply?", follow_up=FollowUp(scheme="PM-KISAN"))  # cached
    assert [f.scheme for f in seen if f] == ["PM-KISAN", "Ujjwala"]


def _answer(question: str, confidence: float = 0.9) -> Answer:
    return Answer(
        question=question,
        language="en",
        text="ok [1]",
        sentences=[],
        citations=[],
        refused=False,
        refusal_reason=None,
        confidence=confidence,
        disclaimer="Informational only.",
        timings_ms={"total": 1.0},
    )


class RecordingService:
    def __init__(self, confidence: float = 0.9) -> None:
        self.calls: list[dict[str, Any]] = []
        self.confidence = confidence
        self.retriever = None

    def answer(
        self, question: str, voice_mode: bool = False, follow_up: FollowUp | None = None
    ) -> Answer:
        self.calls.append({"question": question, "voice_mode": voice_mode, "follow_up": follow_up})
        return _answer(question, self.confidence)


class FakeSpeaker:
    def __init__(self) -> None:
        self.calls = 0

    def speak(self, text: str, language_code: str) -> bytes:
        self.calls += 1
        return b"RIFF....WAVE"


@pytest.fixture
def parts(tmp_path: Path) -> Iterator[tuple[TestClient, RecordingService, FakeSpeaker]]:
    service, speaker = RecordingService(confidence=0.33), FakeSpeaker()
    app = create_app(
        lambda: service,
        build_stt=lambda: None,
        build_tts=lambda: speaker,  # type: ignore[arg-type,return-value]
        log_dir=tmp_path,
        limiter=AskLimiter(2, 100),
    )
    with TestClient(app) as client:
        yield client, service, speaker


def test_ask_passes_voice_mode_and_follow_up(
    parts: tuple[TestClient, RecordingService, FakeSpeaker],
) -> None:
    client, service, _ = parts
    body = {
        "question": "how do I apply?",
        "voice_mode": True,
        "follow_up": {"question": "Who can get PM-KISAN?", "scheme": "PM-KISAN"},
    }
    response = client.post("/ask", json=body)

    assert response.status_code == 200
    call = service.calls[-1]
    assert call["voice_mode"] is True
    assert call["follow_up"] == FollowUp("Who can get PM-KISAN?", "PM-KISAN")


def test_plain_question_sends_no_options(
    parts: tuple[TestClient, RecordingService, FakeSpeaker],
) -> None:
    client, service, _ = parts
    client.post("/ask", json={"question": "PM-KISAN amount"})
    assert service.calls[-1]["voice_mode"] is False
    assert service.calls[-1]["follow_up"] is None


def test_uncertain_voice_answer_asks_for_confirmation(
    parts: tuple[TestClient, RecordingService, FakeSpeaker],
) -> None:
    client, _, _ = parts
    # confidence 0.33 is in the confirm band, but the answer has no scheme to name
    data = client.post("/ask", json={"question": "pm kisan amount", "voice_mode": True}).json()
    assert data["confirmation_text"] is None
    text = client.post("/ask", json={"question": "pm kisan amount"}).json()
    assert text["confirmation_text"] is None


def test_speaking_does_not_use_the_question_limit_and_is_cached(
    parts: tuple[TestClient, RecordingService, FakeSpeaker],
) -> None:
    client, _, speaker = parts
    for _ in range(3):  # the question limit in this test is 2 a minute
        response = client.post("/speak", json={"text": "PM-KISAN pays Rs 6000.", "language": "en"})
        assert response.status_code == 200
    assert speaker.calls == 1  # the same sentence is spoken once, then served from memory
    assert client.post("/ask", json={"question": "PM-KISAN amount"}).status_code == 200


def test_feedback_rejects_huge_text(
    parts: tuple[TestClient, RecordingService, FakeSpeaker],
) -> None:
    client, _, _ = parts
    body = {"status": "SUPPORTED", "thumbs": "up", "reason": "x" * 5000, "include_text": True}
    assert client.post("/feedback", json=body).status_code == 422
