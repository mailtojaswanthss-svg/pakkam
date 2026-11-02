"""Answer caching and semantic vector cache for instant response feel.

Provides:
1. `CachedAnswerer`: In-memory LRU cache keyed on question text and index fingerprint.
2. `SemanticCache`: Vector similarity cache (cosine >= threshold) for sub-50ms verified answers.
"""

import hashlib
import json
import logging
import math
import pickle
import re
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Protocol, Self

from pydantic import BaseModel, ConfigDict

from schemebot.config import Settings
from schemebot.generate.answer import Answer, Citation, FollowUp
from schemebot.generate.messages import RefusalReason
from schemebot.ingest.corrections import CORRECTIONS_NAME
from schemebot.ingest.langid import Language, detect_language
from schemebot.text import normalize_for_search

logger = logging.getLogger(__name__)

# Not cached: an outage passes, and a draft the checks rejected may pass on the next try.
_PASSING_FAILURES: frozenset[RefusalReason] = frozenset(
    {"service_unavailable", "model_declined", "unsupported"}
)
_SPACES = re.compile(r"\s+")
_END_PUNCTUATION = "?？.!।॥ "


class AnswerService(Protocol):
    def answer(self, question: str, voice_mode: bool = False) -> Answer: ...


def _call_answer(
    service: AnswerService, question: str, voice_mode: bool, follow_up: FollowUp | None
) -> Answer:
    """Pass only the options the caller set, so simple services (and test fakes) that take
    just the question keep working. Never retries on a TypeError raised inside the service:
    that would run the whole pipeline, LLM calls included, a second time."""
    options: dict[str, Any] = {}
    if voice_mode:
        options["voice_mode"] = True
    if follow_up is not None:
        options["follow_up"] = follow_up
    return service.answer(question, **options)


def normalize_question(question: str) -> str:
    """'PM Kisan  amount?' and 'pm kisan amount' give the same text."""
    text = _SPACES.sub(" ", normalize_for_search(question)).casefold()
    return text.strip().rstrip(_END_PUNCTUATION)


def cache_key(
    question: str, fingerprint: str = "", voice_mode: bool = False, context: str = ""
) -> str:
    """`context`: the previous turn's scheme for a follow-up, since "how do I apply?" means
    something different after each scheme."""
    language = detect_language(question)
    parts = [fingerprint, "voice"] if voice_mode else [fingerprint]
    if context:
        parts.append("after:" + normalize_question(context))
    return "\x1f".join((*parts, language, normalize_question(question)))


def _digest_files(paths: list[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(str(path.relative_to(root)).encode())
        with path.open("rb") as file:
            for block in iter(lambda: file.read(1 << 20), b""):
                digest.update(block)
    return digest.hexdigest()


def _answer_format() -> str:
    from dataclasses import fields

    from schemebot.generate.answer import AnswerSentence

    names = [
        f"{cls.__name__}:{','.join(f.name for f in fields(cls))}"
        for cls in (Answer, Citation, AnswerSentence)
    ]
    return hashlib.sha256("|".join(names).encode()).hexdigest()[:12]


def _complete(answer: object) -> bool:
    """A saved answer with every field of today's Answer (an older one would crash replace())."""
    from dataclasses import fields

    if not isinstance(answer, Answer):
        return False
    return all(hasattr(answer, f.name) for f in fields(Answer)) and all(
        hasattr(c, f.name) for c in answer.citations for f in fields(Citation)
    )


def answer_fingerprint(settings: Settings, answer_model: str, verifier_model: str) -> str:
    """Hash of what an answer depends on besides the question. Read once at startup."""
    index = settings.index_dir
    found = index.rglob("*") if index.is_dir() else []
    # Skip lock files: the store writes one while it is open, which is not a content change.
    index_files = [p for p in found if p.is_file() and not p.name.startswith(".")]
    corrections = settings.data_dir / CORRECTIONS_NAME
    parts = {
        # The shape of a saved answer: new fields (e.g. scheme_facts) make old saved answers
        # unusable, so they must not be reused after an upgrade.
        "answer_format": _answer_format(),
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
    """LRU cache wrapping an AnswerService. With `path`, answers survive a restart: the
    laptop backend restarts with every new tunnel, and repeated questions should stay instant.
    The file holds hashed keys and answers only, never the question text, and is only reused
    while the fingerprint (index, corrections, models, settings) is unchanged."""

    def preload(self) -> None:
        """Forwards preload call to the underlying service."""
        if hasattr(self._service, "preload"):
            self._service.preload()

    def __init__(
        self,
        service: AnswerService,
        max_entries: int = 128,
        ttl_seconds: float = 3600.0,
        fingerprint: str = "",
        clock: Callable[[], float] = time.monotonic,
        path: Path | None = None,
        wall_clock: Callable[[], float] = time.time,
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
        self._path = path
        self._wall_clock = wall_clock
        self._load()

    @property
    def retriever(self) -> object:
        return getattr(self._service, "retriever", None)

    def checklist(self, scheme: str, language: str) -> object:
        checklist = getattr(self._service, "checklist", None)
        return checklist(scheme, language) if checklist is not None else []

    def sources(self, question: str, follow_up: FollowUp | None = None) -> object:
        sources = getattr(self._service, "sources", None)
        if sources is None:
            raise AttributeError("the wrapped service has no sources()")
        return sources(question, follow_up)

    def answer(
        self, question: str, voice_mode: bool = False, follow_up: FollowUp | None = None
    ) -> Answer:
        started = self._clock()
        context = (follow_up.scheme or "") if follow_up else ""
        key = hashlib.sha256(
            cache_key(question, self._fingerprint, voice_mode=voice_mode, context=context).encode()
        ).hexdigest()
        cached = self._get(key)
        if cached is not None:
            # Replaced question so subtle differences like whitespace match the caller
            elapsed = (self._clock() - started) * 1000
            timings = {"cache": elapsed, "total": elapsed}
            return replace(cached, question=question, timings_ms=timings)

        answer = _call_answer(self._service, question, voice_mode, follow_up)
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
        # Kept without the question text and the retrieved passages (not needed to reply).
        stored = replace(answer, question="", understood_query=None, passages=[])
        with self._lock:
            self._entries[key] = _Entry(stored, self._clock())
            self._entries.move_to_end(key)
            while len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)
            self._save()

    def _save(self) -> None:
        """Called with the lock held. A failed write only costs the cache after a restart."""
        if self._path is None:
            return
        now, wall = self._clock(), self._wall_clock()
        saved = [(key, e.answer, wall - (now - e.stored_at)) for key, e in self._entries.items()]
        temporary = self._path.with_suffix(".tmp")
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with temporary.open("wb") as file:
                pickle.dump({"fingerprint": self._fingerprint, "entries": saved}, file)
            temporary.replace(self._path)
        except OSError as error:
            logger.warning("could not save the answer cache: %s", error)

    def _load(self) -> None:
        if self._path is None or not self._path.is_file():
            return
        try:
            with self._path.open("rb") as file:
                # Our own file in the data folder, written by _save above.
                data = pickle.load(file)  # noqa: S301
        except (OSError, pickle.UnpicklingError, EOFError, AttributeError, ImportError) as error:
            logger.warning("ignoring an unreadable answer cache: %s", error)
            return
        if not isinstance(data, dict) or data.get("fingerprint") != self._fingerprint:
            return  # the index, corrections, models or settings changed: old answers may be wrong
        now, wall = self._clock(), self._wall_clock()
        for key, answer, saved_at in data.get("entries", [])[-self._max_entries :]:
            age = wall - saved_at
            if 0 <= age <= self._ttl_seconds and _complete(answer):
                self._entries[key] = _Entry(answer, now - age)


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
