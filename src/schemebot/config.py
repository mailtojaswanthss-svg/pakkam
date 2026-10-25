"""Central settings for every pipeline stage.

Values come from environment variables prefixed with SCHEMEBOT_ (or a local .env file),
so no model name, threshold or secret is hardcoded elsewhere in the code.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

Effort = Literal["low", "medium", "high", "xhigh", "max"]
"""Reasoning effort: how much the model thinks before answering (a thinking level on Gemini)."""

LlmProvider = Literal["claude", "gemini"]

SUPPORTED_LANGUAGES = ("en", "ta", "hi", "ta-Latn")
"""English, Tamil, Hindi, and Tamil written in Latin script (Tanglish)."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SCHEMEBOT_",
        # Anchored to the project root so commands work from any working directory.
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths
    data_dir: Path = PROJECT_ROOT / "data"
    log_dir: Path = PROJECT_ROOT / "logs"

    # LLM provider for answers, the verifier and the evaluation judge
    llm_provider: LlmProvider = "claude"

    # Claude. With no key set, the SDK falls back to ANTHROPIC_API_KEY or `ant auth login`.
    anthropic_api_key: SecretStr | None = None
    llm_model: str = "claude-opus-5-5"
    llm_effort: Effort = "medium"
    verify_answers: bool = True
    """Run the second-model support check on every answer (one extra, cheap API call)."""
    verifier_model: str = "claude-haiku-5-5"
    judge_model: str = "claude-opus-5-5"
    """Evaluation only: grades faithfulness independently of the in-pipeline verifier."""

    # Gemini (llm_provider = "gemini"). With no key set, the SDK falls back to GEMINI_API_KEY.
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.8-flash"
    gemini_verifier_model: str = "gemini-3.5-flash-lite"
    gemini_judge_model: str = "gemini-3.6-flash"
    """A different model from the one answering, so it is not grading its own output."""

    # Models
    embedding_model: str = "BAAI/bge-m3"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"

    # Vector store (Qdrant local mode, persisted under data/index/)
    qdrant_collection: str = "schemes"
    embed_batch_size: int = Field(default=16, ge=1, le=256)

    # Retrieval and refusal. The threshold is a starting point, tuned on the dev split later.
    retrieval_top_k: int = Field(default=20, ge=1, le=100)
    rerank_top_k: int = Field(default=5, ge=1, le=20)
    refusal_threshold: float = Field(default=0.35, ge=0.0, le=1.0)
    gloss_tanglish: bool = True
    """Give the reranker an English gloss of Tanglish questions (retrieve/tanglish.py)."""

    # Public demo limits on POST /ask (each question can cost two LLM calls)
    ask_limit_per_client_per_minute: int = Field(default=10, ge=1)
    ask_limit_total_per_day: int = Field(default=500, ge=1)

    # OCR
    tesseract_cmd: str | None = None
    tessdata_dir: Path | None = None
    """Folder holding tam/hin/eng .traineddata, when not the install's own tessdata folder."""

    @model_validator(mode="after")
    def _rerank_within_retrieval(self) -> "Settings":
        if self.rerank_top_k > self.retrieval_top_k:
            raise ValueError("rerank_top_k cannot be larger than retrieval_top_k")
        return self

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def index_dir(self) -> Path:
        return self.data_dir / "index"

    @property
    def eval_questions_path(self) -> Path:
        return self.data_dir / "eval" / "questions.jsonl"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance; also usable as a FastAPI dependency."""
    return Settings()
