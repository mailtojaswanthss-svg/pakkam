"""deploy/hf-space/push.py: which .env settings reach the Space, and how."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("push", ROOT / "deploy" / "hf-space" / "push.py")
assert spec and spec.loader
push = importlib.util.module_from_spec(spec)
spec.loader.exec_module(push)


def test_read_env_keeps_only_set_schemebot_settings(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(
        "\ufeff# comment\n"
        "SCHEMEBOT_LLM_PROVIDER=gemini\n"
        'SCHEMEBOT_GEMINI_API_KEY="abc 123"\n'
        "SCHEMEBOT_TTS_MODEL=\n"
        "SCHEMEBOT_MAX_DAILY_LLM_CALLS=1000  # raised\n"
        "SCHEMEBOT_TESSERACT_CMD=C:\\Program Files\\Tesseract\\tesseract.exe\n"
        "HF_TOKEN=nope\n",
        encoding="utf-8",
    )
    assert push.read_env(env) == {
        "SCHEMEBOT_LLM_PROVIDER": "gemini",
        "SCHEMEBOT_GEMINI_API_KEY": "abc 123",
        "SCHEMEBOT_MAX_DAILY_LLM_CALLS": "1000",
    }


def test_keys_become_secrets_and_the_rest_variables() -> None:
    secrets, variables = push.split_settings(
        {
            "SCHEMEBOT_GEMINI_API_KEY": "k1",
            "SCHEMEBOT_GNANI_API_KEY": "k2",
            "SCHEMEBOT_LLM_PROVIDER": "gemini",
        }
    )
    assert secrets == {"SCHEMEBOT_GEMINI_API_KEY": "k1", "SCHEMEBOT_GNANI_API_KEY": "k2"}
    assert variables == {"SCHEMEBOT_LLM_PROVIDER": "gemini"}


def test_model_revisions_are_baked_into_the_dockerfile() -> None:
    text = push.dockerfile({"SCHEMEBOT_EMBEDDING_REVISION": "a" * 40})
    assert f"ARG EMBEDDING_REVISION={'a' * 40}" in text
    assert "ARG RERANKER_REVISION=\n" in text


def test_dockerfile_installs_what_the_api_imports() -> None:
    # The API imports pymupdf (proof-card pages): the ingest extra must be installed.
    text = (ROOT / "deploy" / "hf-space" / "Dockerfile").read_text(encoding="utf-8")
    assert "--extra ingest" in text and "--extra api" in text
    assert "whl/cpu" in text
