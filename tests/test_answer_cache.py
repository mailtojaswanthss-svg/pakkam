from dataclasses import replace

import pytest

from schemebot.generate.answer import Answer
from schemebot.generate.cache import CachedAnswerer, cache_key
from schemebot.generate.messages import RefusalReason

ANSWER = Answer(
    question="Who can join APY?",
    language="en",
    text="Citizens aged 18 to 40 can join. [1]",
    sentences=[],
    citations=[],
    refused=False,
    refusal_reason=None,
    confidence=0.9,
    disclaimer="Informational only.",
    timings_ms={"retrieval": 300.0, "llm_answer": 4000.0, "total": 4500.0},
)


class CountingService:
    def __init__(self, answer: Answer = ANSWER) -> None:
        self.answer_to_give = answer
        self.calls: list[str] = []

    def answer(self, question: str) -> Answer:
        self.calls.append(question)
        return replace(self.answer_to_give, question=question)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def make(service: CountingService, size: int = 10, ttl: float = 60.0) -> CachedAnswerer:
    return CachedAnswerer(service, size, ttl)


@pytest.mark.parametrize(
    "first, second",
    [
        ("Who can join APY?", "who can join apy"),
        ("Who  can join\nAPY ?", "Who can join APY"),
        ("PM kisan amount ௨௦௨௪", "pm kisan amount 2024"),
        ("पीएम किसान में कितना पैसा मिलता है।", "पीएम किसान में कितना पैसा मिलता है?"),
    ],
)
def test_same_question_in_small_variations_shares_a_key(first: str, second: str) -> None:
    assert cache_key(first) == cache_key(second)


def test_different_questions_get_different_keys() -> None:
    assert cache_key("PM-KISAN amount") != cache_key("PM-KISAN eligibility")
    assert cache_key("income below 2 lakh") != cache_key("income below 2.5 lakh")


def test_repeat_question_does_not_call_the_service_again() -> None:
    service = CountingService()
    cache = make(service)

    first = cache.answer("Who can join APY?")
    second = cache.answer("who can join apy")

    assert service.calls == ["Who can join APY?"]
    assert second.text == first.text
    assert second.question == "who can join apy"  # the visitor's own wording comes back


def test_cached_answer_reports_its_own_time_not_the_first_answers_stages() -> None:
    cache = make(CountingService())
    cache.answer("Who can join APY?")

    again = cache.answer("Who can join APY?")

    assert set(again.timings_ms) == {"cache", "total"}
    assert again.timings_ms["total"] < 100


@pytest.mark.parametrize("reason", ["service_unavailable", "model_declined"])
def test_passing_failures_are_not_kept(reason: RefusalReason) -> None:
    failed = replace(ANSWER, refused=True, refusal_reason=reason)
    service = CountingService(failed)
    cache = make(service)

    cache.answer("Who can join APY?")
    cache.answer("Who can join APY?")

    assert len(service.calls) == 2


@pytest.mark.parametrize("reason", ["low_confidence", "not_in_documents", "unsupported"])
def test_lasting_refusals_are_kept(reason: RefusalReason) -> None:
    refused = replace(ANSWER, refused=True, refusal_reason=reason)
    service = CountingService(refused)
    cache = make(service)

    cache.answer("What is the weather?")
    cache.answer("What is the weather?")

    assert len(service.calls) == 1


def test_old_answers_expire() -> None:
    service = CountingService()
    clock = FakeClock()
    cache = CachedAnswerer(service, max_entries=10, ttl_seconds=60.0, clock=clock)

    cache.answer("Who can join APY?")
    clock.now = 59.0
    cache.answer("Who can join APY?")
    clock.now = 61.0
    cache.answer("Who can join APY?")

    assert len(service.calls) == 2


def test_least_recently_used_answer_is_dropped_when_full() -> None:
    service = CountingService()
    cache = make(service, size=2)

    cache.answer("a")
    cache.answer("b")
    cache.answer("a")  # "a" is now the most recently used
    cache.answer("c")  # full: "b" goes
    cache.answer("a")
    cache.answer("b")

    assert service.calls == ["a", "b", "c", "b"]


@pytest.mark.parametrize("size, wrapped", [("256", True), ("0", False)])
def test_api_wraps_the_answerer_unless_the_cache_is_off(
    monkeypatch: pytest.MonkeyPatch, size: str, wrapped: bool
) -> None:
    from schemebot.api import main
    from schemebot.config import get_settings
    from schemebot.generate import factory

    monkeypatch.setenv("SCHEMEBOT_ANSWER_CACHE_SIZE", size)
    monkeypatch.setattr(factory, "build_answerer", lambda settings: CountingService())
    get_settings.cache_clear()
    try:
        service = main._default_service()
    finally:
        get_settings.cache_clear()

    assert isinstance(service, CachedAnswerer) is wrapped
