"""Request limits for the public demo: every /ask can cost two LLM calls.

In memory and per process, which suits the single-worker deployment (one GPU, one model
copy). Behind a reverse proxy, run uvicorn with --proxy-headers so the client address is the
visitor's, not the proxy's.
"""

import threading
import time
from collections import deque
from collections.abc import Callable

MAX_TRACKED_CLIENTS = 10_000
"""Above this many remembered clients, forget the ones with no recent requests."""

MINUTE_S = 60.0
DAY_S = 86_400.0
TOTAL_KEY = "*"


class RateLimiter:
    """Sliding window: at most `limit` requests per `window_s` seconds for each key."""

    def __init__(
        self, limit: int, window_s: float, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self._limit = limit
        self._window = window_s
        self._clock = clock
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str) -> float | None:
        """Count a request. None when allowed, else the seconds until a slot frees up."""
        now = self._clock()
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and hits[0] <= now - self._window:
                hits.popleft()
            if len(hits) >= self._limit:
                return hits[0] + self._window - now
            hits.append(now)
            if len(self._hits) > MAX_TRACKED_CLIENTS:
                self._forget_idle(now)
            return None

    def _forget_idle(self, now: float) -> None:
        idle = [key for key, hits in self._hits.items() if hits[-1] <= now - self._window]
        for key in idle:
            del self._hits[key]


class AskLimiter:
    """A per-client limit per minute, and a total per day that caps the API bill."""

    def __init__(
        self,
        per_client_per_minute: int,
        total_per_day: int,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._per_client = RateLimiter(per_client_per_minute, MINUTE_S, clock)
        self._total = RateLimiter(total_per_day, DAY_S, clock)

    def check(self, client: str) -> float | None:
        wait = self._per_client.check(client)
        if wait is None:
            wait = self._total.check(TOTAL_KEY)
        return wait
