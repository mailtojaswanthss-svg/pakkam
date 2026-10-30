"""Tests for Step 1 Reliability items:

- Model preload and warmup at application startup
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from schemebot.api.main import create_app
from schemebot.generate.answer import Answerer
from schemebot.generate.cache import CachedAnswerer
from schemebot.retrieve.retriever import RetrievalResult, RetrievedPassage
from tests.conftest import make_chunk
from tests.test_answer import FakeLlm


def test_answerer_preload_triggers_retriever_warmup() -> None:
    """Verifies that Answerer.preload executes a warmup retrieve query."""
    retriever_mock = MagicMock()
    chunk = make_chunk("c1", "test chunk")
    retriever_mock.retrieve.return_value = RetrievalResult(
        query="warmup",
        passages=[RetrievedPassage(chunk=chunk, relevance=0.9)],
        timings_ms={"search": 1.0},
    )

    answerer = Answerer(
        retriever=retriever_mock,
        llm=FakeLlm({}),
        verifier=None,
        refusal_threshold=0.35,
    )

    answerer.preload()
    retriever_mock.retrieve.assert_called_once_with("warmup")


def test_answerer_preload_handles_retrieval_error_gracefully() -> None:
    """Verifies that preload does not crash if retrieval models fail or index is empty."""
    retriever_mock = MagicMock()
    retriever_mock.retrieve.side_effect = RuntimeError("Index not ready")

    answerer = Answerer(
        retriever=retriever_mock,
        llm=FakeLlm({}),
        verifier=None,
        refusal_threshold=0.35,
    )

    # Should not raise
    answerer.preload()
    retriever_mock.retrieve.assert_called_once_with("warmup")


def test_cached_answerer_forwards_preload() -> None:
    """Verifies that CachedAnswerer forwards preload to the wrapped service."""
    inner_mock = MagicMock()
    cached = CachedAnswerer(service=inner_mock, max_entries=10)

    cached.preload()
    inner_mock.preload.assert_called_once()


def test_fastapi_lifespan_invokes_service_preload(tmp_path: Path) -> None:
    """Verifies that FastAPI startup lifespan invokes service.preload()."""
    service_mock = MagicMock()

    app = create_app(lambda: service_mock, log_dir=tmp_path)
    with TestClient(app):
        # Entering TestClient triggers lifespan
        service_mock.preload.assert_called_once()


def test_llm_budget_limits_and_records(tmp_path: Path) -> None:
    from schemebot.generate.budget import BudgetExhausted, LlmBudget

    budget_file = tmp_path / "llm-calls.json"
    budget = LlmBudget(budget_file, max_per_day=3, reset_time="00:00 IST")

    assert budget.remaining() == 3
    assert budget.used_today() == 0

    budget.take(model="gemini-3.8-flash")
    budget.take(model="gemini-3.8-flash")
    assert budget.used_today() == 2
    assert budget.remaining() == 1

    budget.take(model="gemini-3.5-flash-lite")
    assert budget.remaining() == 0

    import pytest

    with pytest.raises(BudgetExhausted):
        budget.take(model="gemini-3.8-flash")

    stats = budget.stats()
    assert stats["daily_limit"] == 3
    assert stats["used_today"] == 3
    assert stats["remaining_today"] == 0
    assert stats["by_model"]["gemini-3.8-flash"] == 2
    assert stats["by_model"]["gemini-3.5-flash-lite"] == 1


def test_llm_budget_authoritative_429(tmp_path: Path) -> None:
    from schemebot.generate.budget import BudgetExhausted, LlmBudget

    budget_file = tmp_path / "llm-calls.json"
    budget = LlmBudget(budget_file, max_per_day=20)

    assert not budget.is_rate_limited("gemini-3.8-flash")
    budget.record_429("gemini-3.8-flash")
    assert budget.is_rate_limited("gemini-3.8-flash")

    import pytest

    with pytest.raises(BudgetExhausted, match="authoritative 429"):
        budget.take(model="gemini-3.8-flash")


def test_llm_budget_env_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from schemebot.generate.budget import LlmBudget

    monkeypatch.setenv("SCHEMEBOT_DAILY_LLM_CAP_OVERRIDE", "50")
    budget = LlmBudget(tmp_path / "llm-calls.json", max_per_day=20)
    assert budget.max_per_day == 50


def test_health_endpoint_diagnostics_and_no_secrets(tmp_path: Path) -> None:
    service_mock = MagicMock()
    service_mock.retriever = MagicMock()

    app = create_app(lambda: service_mock, log_dir=tmp_path)
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("ok", "degraded")
        assert "models" in data
        assert "answer" in data["models"]
        assert "retrieval_ready" in data
        assert "quota" in data
        assert "daily_llm_limit" in data["quota"]
        assert "remaining_today" in data["quota"]
        assert "by_model" in data["quota"]

        # Crucial security assertion: verify zero secrets or tokens appear in health payload
        text = resp.text.lower()
        for forbidden in ("key", "secret", "token", "password", "aizasy", "sk-"):
            assert f'"{forbidden}"' not in text


def test_input_validation_empty_and_oversized(tmp_path: Path) -> None:
    service_mock = MagicMock()
    app = create_app(lambda: service_mock, log_dir=tmp_path)
    with TestClient(app) as client:
        # Empty
        resp = client.post("/ask", json={"question": ""})
        assert resp.status_code == 422

        # Whitespace
        resp = client.post("/ask", json={"question": "   \n\t  "})
        assert resp.status_code == 422

        # Oversized (> 500 chars)
        oversized = "a" * 501
        resp = client.post("/ask", json={"question": oversized})
        assert resp.status_code == 422
        detail_str = str(resp.json()["detail"])
        assert "500 characters" in detail_str or "exceeds maximum length" in detail_str


def test_unsupported_language_clean_refusal() -> None:
    retriever_mock = MagicMock()
    answerer = Answerer(
        retriever=retriever_mock,
        llm=FakeLlm({}),
        verifier=None,
        refusal_threshold=0.35,
    )
    # Cyrillic / Russian query:
    ans = answerer.answer("Какая схема поддержки доступна?")
    assert ans.refused
    assert ans.status == "UNSUPPORTED_LANGUAGE"
    assert ans.refusal_reason == "unsupported_language"
    assert "Tamil, Hindi, English" in ans.text
    # Retrieval was not even called
    retriever_mock.retrieve.assert_not_called()
