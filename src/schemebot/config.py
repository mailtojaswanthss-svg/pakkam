"""Central settings for every pipeline stage.

Values come from environment variables prefixed with SCHEMEBOT_ (or a local .env file),
so no model name, threshold or secret is hardcoded elsewhere in the code.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SUPPORTED_LANGUAGES = ("en", "ta", "hi", "ta-Latn")
"""English, Tamil, Hindi, and Tamil written in Latin script (Tanglish)."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SCHEMEBOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Paths
    data_dir: Path = PROJECT_ROOT / "data"
    log_dir: Path = PROJECT_ROOT / "logs"

    # LLM
    anthropic_api_key: SecretStr | None = None
    llm_model: str = "claude-sonnet-5-5"

    # Models
    embedding_model: str = "BAAI/bge-m3"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"

    # Vector store
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "schemes"

    # Retrieval and refusal. The threshold is a starting point, tuned on the dev split later.
    retrieval_top_k: int = Field(default=20, ge=1, le=100)
    rerank_top_k: int = Field(default=5, ge=1, le=20)
    refusal_threshold: float = Field(default=0.35, ge=0.0, le=1.0)

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
    def eval_questions_path(self) -> Path:
        return self.data_dir / "eval" / "questions.jsonl"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance; also usable as a FastAPI dependency."""
    return Settings()
