"""Semantic vector cache for sub-50ms verified answer retrieval.

Caches high-frequency welfare scheme questions and their verified answers.
When an incoming query embedding matches a cached question with cosine
similarity >= threshold (default 0.96), the answer is returned directly,
incurring 0 LLM API calls and <30ms total latency.
"""

import json
import logging
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict

from schemebot.generate.answer import Answer, Citation
from schemebot.ingest.langid import Language

logger = logging.getLogger(__name__)


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
