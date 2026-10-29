"""Tests for Step 1 Reliability items:

- Model preload and warmup at application startup
"""

from pathlib import Path
from unittest.mock import MagicMock

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
