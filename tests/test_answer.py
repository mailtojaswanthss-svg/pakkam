import re
from collections.abc import Callable
from typing import Any

import pytest

from schemebot.generate.answer import Answerer
from schemebot.generate.llm import LlmDeclinedError, LlmUnavailableError
from schemebot.generate.messages import DISCLAIMER, NOT_FOUND, UNAVAILABLE
from schemebot.index.store import build_index, open_client
from schemebot.ingest.models import Chunk
from schemebot.retrieve.hybrid import HybridRetriever
from schemebot.retrieve.retriever import Retriever
from tests.conftest import FakeEncoder, FakeReranker

COLLECTION = "test"
# FakeReranker scores = share of query words found in the passage.
THRESHOLD = 0.3


Response = dict[str, Any] | Exception | Callable[[str], dict[str, Any]]


class FakeLlm:
    """Returns a canned response, raises a canned error, or builds a response from the prompt."""

    def __init__(self, response: Response) -> None:
        self.response = response
        self.user_messages: list[str] = []

    def complete_json(self, system: str, user: str, schema: dict[str, object]) -> dict[str, Any]:
        self.user_messages.append(user)
        if isinstance(self.response, Exception):
            raise self.response
        if callable(self.response):
            return self.response(user)
        return self.response


def passage_number(prompt: str, snippet: str) -> int:
    """The [n] the prompt gave to the passage containing `snippet`."""
    for block in prompt.split("\n\n"):
        match = re.search(r"^\[(\d+)\]", block, re.MULTILINE)
        if match and snippet in block:
            return int(match.group(1))
    raise AssertionError(f"{snippet!r} not in prompt")


def answer_with(llm: FakeLlm, corpus: list[Chunk], question: str) -> Any:
    client = open_client(None)
    encoder = FakeEncoder()
    build_index(client, COLLECTION, corpus, encoder)
    retriever = Retriever(
        HybridRetriever(client, COLLECTION, encoder, 10), FakeReranker(), candidates=5, keep=3
    )
    return Answerer(retriever, llm, verifier=None, refusal_threshold=THRESHOLD).answer(question)


def sentences(*items: tuple[str, list[int]]) -> dict[str, Any]:
    return {"answerable": True, "sentences": [{"text": t, "sources": s} for t, s in items]}


QUESTION = "How much does PM-KISAN pay per year?"


def test_answer_cites_the_passages_it_used(corpus: list[Chunk]) -> None:
    llm = FakeLlm(sentences(("PM-KISAN pays Rs 6000 per year.", [1])))

    answer = answer_with(llm, corpus, QUESTION)

    assert not answer.refused
    assert answer.text == "PM-KISAN pays Rs 6000 per year. [1]"
    [citation] = answer.citations
    assert citation.doc_id == "pmkisan-en"
    assert citation.number == 1
    assert answer.disclaimer == DISCLAIMER["en"]


def test_passages_are_numbered_in_the_prompt(corpus: list[Chunk]) -> None:
    llm = FakeLlm(sentences(("PM-KISAN pays Rs 6000 per year.", [1])))

    answer_with(llm, corpus, QUESTION)

    [prompt] = llm.user_messages
    assert "[1] Test Scheme | pmkisan-en | page 1" in prompt
    assert "Answer in English." in prompt


def test_citations_are_renumbered_in_order_of_use(corpus: list[Chunk]) -> None:
    def respond(prompt: str) -> dict[str, Any]:
        tax = passage_number(prompt, "Income tax payers")
        amount = passage_number(prompt, "Rs 6000")
        assert tax != amount
        return sentences(("Income tax payers are excluded.", [tax]), ("It pays Rs 6000.", [amount]))

    answer = answer_with(FakeLlm(respond), corpus, "PM-KISAN per year income tax payers excluded")

    # Whatever numbers the prompt used, the user sees [1] then [2] in order of use.
    assert [s.citations for s in answer.sentences] == [[1], [2]]
    assert answer.text.endswith("It pays Rs 6000. [2]")
    assert [c.number for c in answer.citations] == [1, 2]


def test_low_retrieval_confidence_refuses_without_calling_the_llm(corpus: list[Chunk]) -> None:
    llm = FakeLlm(sentences(("Anything.", [1])))

    # No word in common with any passage, so the fake reranker scores it 0.
    answer = answer_with(llm, corpus, "Capital city France?")

    assert answer.refused and answer.refusal_reason == "low_confidence"
    assert llm.user_messages == []
    assert answer.text == NOT_FOUND["en"]


def test_model_saying_not_answerable_is_a_refusal(corpus: list[Chunk]) -> None:
    answer = answer_with(FakeLlm({"answerable": False, "sentences": []}), corpus, QUESTION)

    assert answer.refused and answer.refusal_reason == "not_in_documents"


def test_answer_with_only_unbacked_numbers_is_refused(corpus: list[Chunk]) -> None:
    llm = FakeLlm(sentences(("PM-KISAN pays Rs 500 per month.", [1])))

    answer = answer_with(llm, corpus, QUESTION)

    assert answer.refused and answer.refusal_reason == "unsupported"
    assert [r.reason for r in answer.rejected] == ["number_not_in_source"]


def test_unbacked_sentence_is_dropped_but_the_rest_answered(corpus: list[Chunk]) -> None:
    llm = FakeLlm(sentences(("PM-KISAN pays Rs 6000 per year.", [1]), ("Or Rs 700 monthly.", [1])))

    answer = answer_with(llm, corpus, QUESTION)

    assert not answer.refused
    assert answer.text == "PM-KISAN pays Rs 6000 per year. [1]"
    assert len(answer.rejected) == 1


@pytest.mark.parametrize(
    ("error", "reason", "text"),
    [
        (LlmDeclinedError("declined"), "model_declined", NOT_FOUND["en"]),
        (LlmUnavailableError("down"), "service_unavailable", UNAVAILABLE["en"]),
    ],
)
def test_llm_failures_become_refusals(
    corpus: list[Chunk], error: Exception, reason: str, text: str
) -> None:
    answer = answer_with(FakeLlm(error), corpus, QUESTION)

    assert answer.refused and answer.refusal_reason == reason
    assert answer.text == text


def test_refusal_is_in_the_question_language(corpus: list[Chunk]) -> None:
    answer = answer_with(FakeLlm(sentences(("x", [1]))), corpus, "பிரான்சின் தலைநகரம் எது?")

    assert answer.language == "ta"
    assert answer.text == NOT_FOUND["ta"]


def test_timings_are_recorded(corpus: list[Chunk]) -> None:
    answer = answer_with(
        FakeLlm(sentences(("PM-KISAN pays Rs 6000 per year.", [1]))), corpus, QUESTION
    )

    assert {"retrieval", "generation", "total"} <= answer.timings_ms.keys()


def test_every_stage_that_ran_is_timed(corpus: list[Chunk]) -> None:
    answer = answer_with(
        FakeLlm(sentences(("PM-KISAN pays Rs 6000 per year.", [1]))), corpus, QUESTION
    )

    timings = answer.timings_ms
    assert {"search", "rerank", "llm_answer", "verifier", "total"} <= timings.keys()
    assert all(isinstance(ms, float) and ms >= 0 for ms in timings.values())
    assert timings["total"] >= timings["retrieval"] >= timings["search"]


def test_a_low_confidence_refusal_has_no_llm_timings(corpus: list[Chunk]) -> None:
    answer = answer_with(FakeLlm(sentences(("x", [1]))), corpus, "Capital city France?")

    assert answer.refused
    assert "llm_answer" not in answer.timings_ms
    assert "verifier" not in answer.timings_ms


class _FakeResponse:
    def __init__(self, text: str, stop_reason: str = "end_turn") -> None:
        self.stop_reason = stop_reason
        self.content = [type("Block", (), {"type": "text", "text": text})()]


class _RecordingMessages:
    def __init__(self, text: str) -> None:
        self.calls: list[dict[str, object]] = []
        self._text = text

    def create(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(kwargs)
        return _FakeResponse(self._text)


def _llm_with_fake_client(model: str, reply: str) -> tuple[object, _RecordingMessages]:
    from schemebot.generate.llm import ClaudeJsonLlm

    llm = ClaudeJsonLlm(model, api_key="test-key", effort="low")
    messages = _RecordingMessages(reply)
    llm._client = type(
        "Client",
        (),
        {
            "beta": type("Beta", (), {"messages": messages})(),
            "api_key": "test-key",
            "auth_token": None,
            "credentials": None,
        },
    )()
    return llm, messages


def test_fallback_is_only_requested_for_models_that_support_it() -> None:
    opus, opus_calls = _llm_with_fake_client("claude-opus-5-5", '{"ok": true}')
    haiku, haiku_calls = _llm_with_fake_client("claude-haiku-5-5", '{"ok": true}')

    opus.complete_json("system", "user", {})  # type: ignore[attr-defined]
    haiku.complete_json("system", "user", {})  # type: ignore[attr-defined]

    assert opus_calls.calls[0]["fallbacks"] == "default"
    assert "fallbacks" not in haiku_calls.calls[0]
    assert "betas" not in haiku_calls.calls[0]


def test_invalid_json_reply_becomes_unavailable_error() -> None:
    from schemebot.generate.llm import LlmUnavailableError

    llm, _ = _llm_with_fake_client("claude-opus-5-5", "not json")

    with pytest.raises(LlmUnavailableError):
        llm.complete_json("system", "user", {})  # type: ignore[attr-defined]


def test_missing_credentials_become_unavailable_error_without_calling_api() -> None:
    from schemebot.generate.llm import LlmUnavailableError

    llm, calls = _llm_with_fake_client("claude-opus-5-5", '{"ok": true}')
    llm._client.api_key = None  # type: ignore[attr-defined]

    with pytest.raises(LlmUnavailableError, match="credentials"):
        llm.complete_json("system", "user", {})  # type: ignore[attr-defined]
    assert calls.calls == []


@pytest.mark.parametrize(
    "reply",
    [{}, {"answerable": True}, {"answerable": True, "sentences": [{"text": "x"}]}],
)
def test_reply_with_wrong_shape_becomes_a_refusal(
    corpus: list[Chunk], reply: dict[str, Any]
) -> None:
    answer = answer_with(FakeLlm(reply), corpus, QUESTION)

    assert answer.refused
    assert answer.refusal_reason == "service_unavailable"


def test_aadhaar_and_phone_pii_interception(corpus: list[Chunk]) -> None:
    # 1. Aadhaar number interception
    llm = FakeLlm({"answerable": True, "sentences": [{"text": "Leaked"}]})
    ans_aadhaar = answer_with(llm, corpus, "My aadhaar is 2345 6789 0123 can I apply for scheme?")
    assert ans_aadhaar.refused
    assert ans_aadhaar.refusal_reason == "pii_detected"
    assert ans_aadhaar.status == "PII_DETECTED"
    assert "privacy and security" in ans_aadhaar.text
    assert len(llm.user_messages) == 0  # 0 LLM calls made!

    # 2. Indian Phone number interception
    llm2 = FakeLlm({"answerable": True, "sentences": [{"text": "Leaked"}]})
    ans_phone = answer_with(llm2, corpus, "Call me at 9876543210 for pension")
    assert ans_phone.refused
    assert ans_phone.refusal_reason == "pii_detected"
    assert ans_phone.status == "PII_DETECTED"
    assert len(llm2.user_messages) == 0
