"""Central settings for every pipeline stage.

Values come from environment variables prefixed with SCHEMEBOT_ (or a local .env file),
so no model name, threshold or secret is hardcoded elsewhere in the code.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

Effort = Literal["low", "medium", "high", "xhigh", "max"]
"""Reasoning effort: how much the model thinks before answering (a thinking level on Gemini)."""

LlmProvider = Literal["claude", "gemini"]

TimbreModel = Literal["timbre-v2.5", "timbre-v3.0"]
"""Gnani text-to-speech models. Voice names differ between them."""

OcrEngine = Literal["tesseract", "chitrapathak"]
"""OCR engine for extracting text from scanned PDF pages."""

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
    llm_fallback_enabled: bool = False
    """When True, switches to secondary provider on unavailable error (429/timeout)."""

    # Claude. With no key set, the SDK falls back to ANTHROPIC_API_KEY or `ant auth login`.
    anthropic_api_key: SecretStr | None = None
    llm_model: str = "claude-opus-5-5"
    llm_effort: Effort = "low"
    """Thinking depth for the answer. Short cited answers do as well at "low", and it is
    several times faster (docs/review/LLM_PROVIDER_COMPARISON.md)."""
    verify_answers: bool = True
    rewrite_unclear_questions: bool = True
    """When search is unsure, the verifier model restates the question (English, Tamil, scheme
    name) and search runs again. One small extra call, only on uncertain questions."""
    """Run the second-model support check on every answer (one extra, cheap API call)."""
    verifier_model: str = "claude-haiku-5-5"
    judge_model: str = "claude-opus-5-5"
    """Evaluation only: grades faithfulness independently of the in-pipeline verifier."""

    # Limits for every LLM call (Claude and Gemini), so one stuck call cannot hold a visitor
    # for many minutes. Retries cover rate limits (429), server errors (5xx) and timeouts.
    # For a long evaluation run on Gemini's free tier, raise the retries (e.g. 7).
    # The defaults keep the worst case (timeout x (retries + 1)) well under the 2-minute limit
    # of the chat page and of the Vercel proxy.
    llm_timeout_seconds: float = Field(default=30.0, gt=0)
    llm_retries: int = Field(default=1, ge=0, le=10)
    max_daily_llm_calls: int = Field(default=200, ge=1)
    """Answer and verifier calls together (about 100 answered questions a day). A cost guard:
    on Gemini's free tier set it near the free quota."""
    llm_reset_time: str = Field(default="unknown")
    max_question_length: int = Field(default=500, ge=10, le=5000)
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # Gemini (llm_provider = "gemini"). With no key set, the SDK falls back to GEMINI_API_KEY.
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.8-flash"
    gemini_verifier_model: str = "gemini-3.5-flash-lite"
    gemini_backup_model: str | None = "gemini-3.5-flash-lite"
    """Answers when the main Gemini model hits its per-minute limit (it has its own free
    allowance), so visitors see an answer instead of the "busy" card. Empty turns it off."""
    gemini_judge_model: str = "gemini-3.6-flash"
    """A different model from the one answering, so it is not grading its own output."""

    # Models
    embedding_model: str = "BAAI/bge-m3"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    embedding_revision: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    reranker_revision: str | None = Field(default=None, pattern=r"^[0-9a-f]{40}$")
    """Hugging Face commit hashes. Set them so a rebuilt index or a new machine uses exactly
    the model versions the results were measured with; empty means the latest version."""

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
    # Exact-match only: the same words (ignoring case, spaces and a final "?") in the same
    # language, with the same models, settings, index and corrections.
    answer_cache_size: int = Field(default=256, ge=0)
    """Answers kept in memory so a repeated question costs no LLM call; 0 turns it off."""
    answer_cache_ttl_seconds: float = Field(default=6 * 3600, gt=0)

    # Gnani voice (Prisma v2.5 speech to text). The key lives only in .env.
    gnani_api_key: SecretStr | None = None
    gnani_stt_url: str = "https://api.vachana.ai/stt/v3"
    stt_max_seconds: float = Field(default=30.0, gt=0, le=60)
    """Gnani's docs say both 30 s and 60 s; 30 s is the safe limit until tested."""
    stt_max_bytes: int = Field(default=5_000_000, ge=1)
    """Upload size cap: 30 s of 16 kHz mono WAV is about 1 MB."""
    stt_timeout_seconds: float = Field(default=30.0, gt=0)
    gnani_max_calls_per_day: int = Field(default=100, ge=0)
    """Speech to text and text to speech together, web app and compare script together.

    A guess until credit use is measured in the Gnani dashboard."""

    # Gnani Timbre text to speech. Spoken answers stay off until a model is chosen.
    tts_model: TimbreModel | None = None
    gnani_tts_url: str = "https://api.vachana.ai/api/v1/tts/inference"
    tts_voice_ta: str | None = None
    tts_voice_hi: str | None = None
    tts_voice_en: str | None = None
    """Leave empty for the default voice of the chosen model (voice/tts.py)."""
    tts_spell_amounts: bool = False
    """Write money amounts as words before TTS (voice/numbers.py). Off until the listening
    test shows Timbre misreads digits."""
    tts_max_chars: int = Field(default=1200, ge=1)
    """Longest answer read aloud; Gnani documents no limit, so this bounds credit use."""

    # OCR
    tesseract_cmd: str | None = None
    tessdata_dir: Path | None = None
    ocr_engine: OcrEngine = "tesseract"
    """Folder holding tam/hin/eng .traineddata, when not the install's own tessdata folder."""

    @field_validator(
        "gnani_api_key",
        "tts_model",
        "tts_voice_ta",
        "tts_voice_hi",
        "tts_voice_en",
        "embedding_revision",
        "reranker_revision",
        mode="before",
    )
    @classmethod
    def _empty_means_unset(cls, value: object) -> object:
        # `SCHEMEBOT_TTS_MODEL=` (empty, as in .env.example) means "not set", not "".
        return None if isinstance(value, str) and not value.strip() else value

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
