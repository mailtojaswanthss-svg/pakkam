"""In-memory answer cache, so a repeated question costs no LLM calls.

Demo visitors often ask the same few questions. An answer depends only on the question and
the index, and the index does not change while the server runs, so a repeat can reuse the
first answer. The cache lives in one process's memory: a restart empties it.

Questions match after light tidying: Indic digits as 0-9, case, spaces and a trailing "?"
do not matter. Answers that failed for a passing reason (LLM down, model declined) are not
kept, so the next try asks again.
"""

import re
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Protocol

from schemebot.generate.answer import Answer
from schemebot.generate.messages import RefusalReason
from schemebot.text import normalize_for_search

_PASSING_FAILURES: frozenset[RefusalReason] = frozenset({"service_unavailable", "model_declined"})
_SPACES = re.compile(r"\s+")
_END_PUNCTUATION = "?？.!।॥ "


class AnswerService(Protocol):
    def answer(self, question: str) -> Answer: ...


def cache_key(question: str) -> str:
    """'PM Kisan  amount?' and 'pm kisan amount' give the same key."""
    text = _SPACES.sub(" ", normalize_for_search(question)).casefold()
    return text.strip().rstrip(_END_PUNCTUATION)


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
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._service = service
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._entries: OrderedDict[str, _Entry] = OrderedDict()
        self._lock = threading.Lock()

    def answer(self, question: str) -> Answer:
        started = time.perf_counter()
        key = cache_key(question)
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
