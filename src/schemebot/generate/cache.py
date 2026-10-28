"""In-memory answer cache, so a repeated question costs no LLM calls.

Demo visitors often ask the same few questions. An answer depends only on the question and
the index, and the index does not change while the server runs, so a repeat can reuse the
first answer. The cache lives in one process's memory: a restart empties it.

Questions match after light tidying: Indic digits as 0-9, case, spaces and a trailing "?"
do not matter. The key also holds the answer language and a fingerprint of everything else an
answer depends on: the models, the retrieval and refusal settings, and the content of the
search index and data/corrections.json. Answers that failed for a passing reason (LLM down,
model declined) are not kept, so the next try asks again. Nothing here is logged, and the
rate limit runs before the cache, so a repeat still counts against it.
"""

import hashlib
import json
import re
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol

from schemebot.config import Settings
from schemebot.generate.answer import Answer
from schemebot.generate.messages import RefusalReason
from schemebot.ingest.corrections import CORRECTIONS_NAME
from schemebot.ingest.langid import detect_language
from schemebot.text import normalize_for_search

_PASSING_FAILURES: frozenset[RefusalReason] = frozenset({"service_unavailable", "model_declined"})
_SPACES = re.compile(r"\s+")
_END_PUNCTUATION = "?？.!।॥ "


class AnswerService(Protocol):
    @property
    def retriever(self):
        return getattr(self._service, "retriever", None)

    def answer(self, question: str) -> Answer: ...


def normalize_question(question: str) -> str:
    """'PM Kisan  amount?' and 'pm kisan amount' give the same text."""
    text = _SPACES.sub(" ", normalize_for_search(question)).casefold()
    return text.strip().rstrip(_END_PUNCTUATION)


def cache_key(question: str, fingerprint: str = "") -> str:
    language = detect_language(question)
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
    """Wraps an answer service; keeps up to `max_entries` answers for `ttl_seconds`."""

    def __init__(
        self,
        service: AnswerService,
        max_entries: int,
        ttl_seconds: float,
        fingerprint: str = "",
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._service = service
        self._fingerprint = fingerprint
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._entries: OrderedDict[str, _Entry] = OrderedDict()
        self._lock = threading.Lock()

    def answer(self, question: str) -> Answer:
        started = time.perf_counter()
        key = cache_key(question, self._fingerprint)
        cached = self._get(key)
        if cached is not None:
            # The stage timings of the first answer would be misleading here.
            took = (time.perf_counter() - started) * 1000
            return replace(cached, question=question, timings_ms={"cache": took, "total": took})

        # Two people asking the same new question at once both reach the service; the
        # second answer simply replaces the first. Not worth a per-question lock.
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
            self._entries.move_to_end(key)  # most recently used goes last
            return entry.answer

    def _put(self, key: str, answer: Answer) -> None:
        with self._lock:
            self._entries[key] = _Entry(answer, self._clock())
            self._entries.move_to_end(key)
            while len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)  # drop the least recently used
