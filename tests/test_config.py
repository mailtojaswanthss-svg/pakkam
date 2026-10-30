from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from schemebot.config import Settings


def make_settings(**overrides: Any) -> Settings:
    # _env_file=None keeps a developer's local .env from leaking into tests.
    return Settings(_env_file=None, **overrides)


def test_defaults_are_valid() -> None:
    settings = make_settings()

    assert settings.embedding_model == "BAAI/bge-m3"
    assert settings.rerank_top_k <= settings.retrieval_top_k
    assert settings.anthropic_api_key is None


def test_env_variables_override_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCHEMEBOT_RETRIEVAL_TOP_K", "30")
    monkeypatch.setenv("SCHEMEBOT_ANTHROPIC_API_KEY", "test-key")

    settings = make_settings()

    assert settings.retrieval_top_k == 30
    assert settings.anthropic_api_key is not None
    assert settings.anthropic_api_key.get_secret_value() == "test-key"


def test_api_key_is_hidden_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCHEMEBOT_ANTHROPIC_API_KEY", "test-key")

    assert "test-key" not in repr(make_settings())


def test_rerank_larger_than_retrieval_is_rejected() -> None:
    with pytest.raises(ValidationError, match="rerank_top_k"):
        make_settings(retrieval_top_k=5, rerank_top_k=10)


@pytest.mark.parametrize("threshold", [-0.1, 1.5])
def test_refusal_threshold_must_be_a_probability(threshold: float) -> None:
    with pytest.raises(ValidationError):
        make_settings(refusal_threshold=threshold)


def test_derived_paths_live_under_data_dir(tmp_path: Path) -> None:
    settings = make_settings(data_dir=tmp_path)

    assert settings.raw_dir == settings.data_dir / "raw"
    assert settings.eval_questions_path.name == "questions.jsonl"


def test_env_file_is_found_from_any_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    env_file = Settings.model_config.get("env_file")

    assert isinstance(env_file, Path)
    assert env_file.is_absolute()
    assert env_file.name == ".env"


def test_ocr_engine_setting(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = make_settings()
    assert settings.ocr_engine == "tesseract"
    assert settings.qdrant_collection == "schemes"

    monkeypatch.setenv("SCHEMEBOT_OCR_ENGINE", "chitrapathak")
    monkeypatch.setenv("SCHEMEBOT_QDRANT_COLLECTION", "pakkam_chitra")
    settings = make_settings()
    assert settings.ocr_engine == "chitrapathak"
    assert settings.qdrant_collection == "pakkam_chitra"
