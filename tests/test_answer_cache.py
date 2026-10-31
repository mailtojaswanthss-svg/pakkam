from dataclasses import replace
from pathlib import Path

import pytest

from schemebot.config import Settings
from schemebot.generate.answer import Answer
from schemebot.generate.cache import CachedAnswerer, answer_fingerprint, cache_key
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


@pytest.mark.parametrize("reason", ["service_unavailable", "model_declined", "unsupported"])
def test_passing_failures_are_not_kept(reason: RefusalReason) -> None:
    failed = replace(ANSWER, refused=True, refusal_reason=reason)
    service = CountingService(failed)
    cache = make(service)

    cache.answer("Who can join APY?")
    cache.answer("Who can join APY?")

    assert len(service.calls) == 2


@pytest.mark.parametrize("reason", ["low_confidence", "not_in_documents"])
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


def test_key_holds_fingerprint_language_and_question() -> None:
    assert cache_key("Who can join APY?", "fp1").split("\x1f") == ["fp1", "en", "who can join apy"]
    assert cache_key("Who can join APY?", "fp1") != cache_key("Who can join APY?", "fp2")


def test_different_fingerprint_does_not_reuse_answers() -> None:
    service = CountingService()
    CachedAnswerer(service, 10, 60.0, fingerprint="old").answer("Who can join APY?")
    CachedAnswerer(service, 10, 60.0, fingerprint="new").answer("Who can join APY?")

    assert len(service.calls) == 2


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    (tmp_path / "index").mkdir()
    (tmp_path / "index" / "collection.sqlite").write_bytes(b"vectors v1")
    (tmp_path / "corrections.json").write_text("[]", encoding="utf-8")
    return tmp_path


def fingerprint(data_dir: Path, **changes: object) -> str:
    settings = Settings(_env_file=None, data_dir=data_dir, **changes)  # type: ignore[arg-type]
    return answer_fingerprint(settings, "answer-model", "verifier-model")


def test_fingerprint_changes_with_index_corrections_and_settings(data_dir: Path) -> None:
    base = fingerprint(data_dir)
    assert fingerprint(data_dir) == base

    (data_dir / "index" / ".lock").write_text("held", encoding="utf-8")
    assert fingerprint(data_dir) == base  # the store's lock file is not content

    assert fingerprint(data_dir, refusal_threshold=0.5) != base
    assert fingerprint(data_dir, verify_answers=False) != base

    (data_dir / "corrections.json").write_text('[{"x": 1}]', encoding="utf-8")
    after_corrections = fingerprint(data_dir)
    assert after_corrections != base

    (data_dir / "index" / "collection.sqlite").write_bytes(b"vectors v2")
    assert fingerprint(data_dir) != after_corrections


def test_model_change_changes_the_fingerprint(data_dir: Path) -> None:
    settings = Settings(_env_file=None, data_dir=data_dir)
    assert answer_fingerprint(settings, "model-a", "v") != answer_fingerprint(
        settings, "model-b", "v"
    )


def test_cache_hit_still_counts_against_the_rate_limit(tmp_path: Path) -> None:
    from fastapi.testclient import TestClient

    from schemebot.api.main import create_app
    from schemebot.api.ratelimit import AskLimiter

    service = CountingService()
    app = create_app(
        lambda: CachedAnswerer(service, 10, 60.0),
        log_dir=tmp_path,
        limiter=AskLimiter(per_client_per_minute=1, total_per_day=100),
    )
    with TestClient(app) as client:
        first = client.post("/ask", json={"question": "Who can join APY?"})
        second = client.post("/ask", json={"question": "Who can join APY?"})

    assert first.status_code == 200
    assert second.status_code == 429
    assert len(service.calls) == 1
