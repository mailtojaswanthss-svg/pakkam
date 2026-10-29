"""Answer caching and semantic vector cache for instant response feel.

Provides:
1. `CachedAnswerer`: In-memory LRU cache keyed on question text and index fingerprint.
2. `SemanticCache`: Vector similarity cache (cosine >= threshold) for sub-50ms verified answers.
"""

import hashlib
import json
import logging
import math
import re
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol, Self

from pydantic import BaseModel, ConfigDict

from schemebot.config import Settings
from schemebot.generate.answer import Answer, Citation
from schemebot.generate.messages import RefusalReason
from schemebot.ingest.corrections import CORRECTIONS_NAME
from schemebot.ingest.langid import Language, detect_language
from schemebot.text import normalize_for_search

logger = logging.getLogger(__name__)

_PASSING_FAILURES: frozenset[RefusalReason] = frozenset({"service_unavailable", "model_declined"})
_SPACES = re.compile(r"\s+")
_END_PUNCTUATION = "?？.!।॥ "


class AnswerService(Protocol):
    def answer(self, question: str, voice_mode: bool = False) -> Answer: ...


def normalize_question(question: str) -> str:
    """'PM Kisan  amount?' and 'pm kisan amount' give the same text."""
    text = _SPACES.sub(" ", normalize_for_search(question)).casefold()
    return text.strip().rstrip(_END_PUNCTUATION)


def cache_key(question: str, fingerprint: str = "", voice_mode: bool = False) -> str:
    language = detect_language(question)
    if voice_mode:
        return "\x1f".join((fingerprint, "voice", language, normalize_question(question)))
    return "\x1f".join((fingerprint, language, normalize_question(question)))


def _digest_files(paths: list[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(root)).encode())
        with path.open("rb") as file:
            for block in iter(lambda: file.read(1 << 20), b""):
                digest.update(block)
    return digest.hexdigest()


def answer_fingerprint(settings: Settings, answer_model: str, verifier_model: str) -> str:
    """Hash of what an answer depends on besides the question. Read once at startup."""
    index = settings.index_dir
    found = index.rglob("*") if index.is_dir() else []
    # Skip lock files: the store writes one while it is open, which is not a content change.
    index_files = [p for p in found if p.is_file() and not p.name.startswith(".")]
    corrections = settings.data_dir / CORRECTIONS_NAME
    parts = {
        "answer_model": answer_model,
        "verifier_model": verifier_model if settings.verify_answers else "off",
        "effort": settings.llm_effort,
        "embedding": f"{settings.embedding_model}@{settings.embedding_revision}",
        "reranker": f"{settings.reranker_model}@{settings.reranker_revision}",
        "retrieval_top_k": settings.retrieval_top_k,
        "rerank_top_k": settings.rerank_top_k,
        "refusal_threshold": settings.refusal_threshold,
        "gloss_tanglish": settings.gloss_tanglish,
        "index": _digest_files(index_files, index),
        "corrections": _digest_files([corrections], settings.data_dir)
        if corrections.is_file()
        else "none",
    }
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:16]


@dataclass(frozen=True)
class _Entry:
    answer: Answer
    stored_at: float


class CachedAnswerer:
    """In-memory LRU cache wrapping an AnswerService."""

    def __init__(
        self,
        service: AnswerService,
        max_entries: int = 128,
        ttl_seconds: float = 3600.0,
        fingerprint: str = "",
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_entries < 1:
            raise ValueError(f"max_entries must be >= 1, got {max_entries}")
        self._service = service
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._fingerprint = fingerprint
        self._clock = clock
        self._lock = threading.Lock()
        self._entries: OrderedDict[str, _Entry] = OrderedDict()

    @property
    def retriever(self) -> object:
        return getattr(self._service, "retriever", None)

    def answer(self, question: str, voice_mode: bool = False) -> Answer:
        started = self._clock()
        key = cache_key(question, self._fingerprint, voice_mode=voice_mode)
        cached = self._get(key)
        if cached is not None:
            # Replaced question so subtle differences like whitespace match the caller
            elapsed = (self._clock() - started) * 1000
            timings = {"cache": elapsed, "total": elapsed}
            return replace(cached, question=question, timings_ms=timings)

        try:
            answer = self._service.answer(question, voice_mode=voice_mode)
        except TypeError:
            answer = self._service.answer(question)
        if answer.refusal_reason not in _PASSING_FAILURES:
            self._put(key, answer)
        return answer

    def _get(self, key: str) -> Answer | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if self._clock() - entry.stored_at > self._ttl_seconds:
                del self._entries[key]
                return None
            self._entries.move_to_end(key)
            return entry.answer

    def _put(self, key: str, answer: Answer) -> None:
        with self._lock:
            self._entries[key] = _Entry(answer, self._clock())
            self._entries.move_to_end(key)
            while len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if len(v1) != len(v2) or not v1:
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2, strict=False))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)


class CacheEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    question: str
    embedding: list[float]
    answer_text: str
    scheme: str
    language: Language
    doc_id: str
    page: int
    source_url: str
    disclaimer: str


@dataclass
class CacheHit:
    entry: CacheEntry
    similarity: float
    duration_ms: float


class SemanticCache:
    def __init__(self, entries: list[CacheEntry], threshold: float = 0.96) -> None:
        self.entries = entries
        self.threshold = threshold

    @classmethod
    def load(cls, path: Path, threshold: float = 0.96) -> Self:
        if not path.is_file():
            return cls([], threshold=threshold)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            entries = [CacheEntry.model_validate(e) for e in data]
            return cls(entries, threshold=threshold)
        except Exception as exc:
            logger.warning("Failed to load semantic cache from %s: %s", path, exc)
            return cls([], threshold=threshold)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [e.model_dump() for e in self.entries]
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add(self, entry: CacheEntry) -> None:
        self.entries.append(entry)

    def lookup(self, query_embedding: list[float]) -> CacheHit | None:
        """Find the closest cached entry above similarity threshold."""
        start = time.perf_counter()
        best_entry: CacheEntry | None = None
        best_sim = -1.0

        for entry in self.entries:
            sim = cosine_similarity(query_embedding, entry.embedding)
            if sim > best_sim:
                best_sim = sim
                best_entry = entry

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        if best_entry and best_sim >= self.threshold:
            return CacheHit(entry=best_entry, similarity=best_sim, duration_ms=elapsed_ms)
        return None

    def to_answer(self, hit: CacheHit, raw_question: str) -> Answer:
        """Convert a CacheHit into a citation-grounded Answer."""
        entry = hit.entry
        citation = Citation(
            number=1,
            doc_id=entry.doc_id,
            scheme=entry.scheme,
            page_start=entry.page,
            page_end=entry.page,
            source_url=entry.source_url,
            text=entry.answer_text,
            language=entry.language,
        )
        return Answer(
            question=raw_question,
            language=entry.language,
            text=entry.answer_text,
            sentences=[],
            citations=[citation],
            refused=False,
            refusal_reason=None,
            confidence=round(hit.similarity, 4),
            disclaimer=entry.disclaimer,
            timings_ms={
                "semantic_cache": round(hit.duration_ms, 2),
                "total": round(hit.duration_ms, 2),
            },
            status="SUPPORTED",
            path="semantic_cache",
            understood_query=entry.question,
        )
