"""A daily cap on LLM calls to prevent unexpected usage or credit exhaustion.

Features:
- Configurable daily limit (default 20, overridable via SCHEMEBOT_DAILY_LLM_CAP_OVERRIDE).
- Configurable reset time (default "unknown").
- A real 429 pauses that model for a short cooldown (60 s by default), not the whole day:
  free-tier 429s are usually per-minute limits.
- Per-model counters and failed attempts counted (fail-closed before dispatch).
- Low-quota warning when remaining <= 5.
- Atomic file-locking with stale lock cleanup and IST midnight rollover.
- Zero external dependencies.
"""

import json
import logging
import os
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

IST = timezone(timedelta(hours=5, minutes=30))
CALLS_FILE_NAME = "llm-calls.json"
LOCK_WAIT_S = 5.0
STALE_LOCK_S = 30.0
LOW_QUOTA_THRESHOLD = 5
RATE_LIMIT_COOLDOWN_S = 60.0
"""How long a model is paused after an HTTP 429 before calls to it are tried again."""

logger = logging.getLogger(__name__)


def today_in_india() -> date:
    return datetime.now(UTC).astimezone(IST).date()


class BudgetExhausted(Exception):
    pass


class LlmBudget:
    def __init__(
        self,
        path: Path,
        max_per_day: int = 20,
        reset_time: str = "unknown",
        today: Callable[[], date] = today_in_india,
        clock: Callable[[], float] = time.time,
        cooldown_s: float = RATE_LIMIT_COOLDOWN_S,
    ) -> None:
        self._path = path
        # Check environment override
        env_override = os.environ.get("SCHEMEBOT_DAILY_LLM_CAP_OVERRIDE")
        if env_override:
            try:
                self.max_per_day = int(env_override)
            except ValueError:
                self.max_per_day = max_per_day
        else:
            self.max_per_day = max_per_day

        self.reset_time = os.environ.get("SCHEMEBOT_LLM_RESET_TIME", reset_time)
        self._today = today
        self._clock = clock
        self._cooldown_s = cooldown_s
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path

    def used_today(self) -> int:
        with self._lock, self._file_lock():
            data = self._read_data()
            return int(data.get("calls", 0))

    def remaining(self) -> int:
        return max(self.max_per_day - self.used_today(), 0)

    def is_rate_limited(self, model: str) -> bool:
        with self._lock, self._file_lock():
            data = self._read_data()
            return self._paused_for(data, model) > 0

    def record_429(self, model: str) -> None:
        """Mark a model as rate-limited (HTTP 429 is authoritative)."""
        with self._lock, self._file_lock():
            data = self._read_data()
            rate_limited = data.setdefault("rate_limited", {})
            rate_limited[model] = self._clock() + self._cooldown_s
            self._write_data(data)
            logger.warning(
                "Model %s received HTTP 429; paused for %.0f s.", model, self._cooldown_s
            )

    def stats(self) -> dict[str, Any]:
        with self._lock, self._file_lock():
            data = self._read_data()
            used = int(data.get("calls", 0))
            return {
                "daily_limit": self.max_per_day,
                "daily_llm_limit": self.max_per_day,
                "used_today": used,
                "remaining_today": max(self.max_per_day - used, 0),
                "reset_time": self.reset_time,
                "by_model": data.get("by_model", {}),
                "rate_limited": data.get("rate_limited", {}),
            }

    def take(self, model: str = "default") -> None:
        """Count one attempt before dispatch. Raises BudgetExhausted if cap reached or model 429."""
        with self._lock, self._file_lock():
            data = self._read_data()
            paused = self._paused_for(data, model)
            if paused > 0:
                raise BudgetExhausted(
                    f"Model {model} is rate-limited (HTTP 429); retry in {paused:.0f} s."
                )

            used = int(data.get("calls", 0))
            if used >= self.max_per_day:
                today_iso = self._today().isoformat()
                raise BudgetExhausted(
                    f"Daily LLM cap reached ({self.max_per_day} calls on {today_iso}). "
                    f"Resets at {self.reset_time}."
                )

            # Count attempt
            used += 1
            data["calls"] = used
            data["date"] = self._today().isoformat()
            by_model = data.setdefault("by_model", {})
            by_model[model] = int(by_model.get(model, 0)) + 1
            self._write_data(data)

            rem = max(self.max_per_day - used, 0)
            if rem <= LOW_QUOTA_THRESHOLD:
                logger.warning("Low LLM quota warning: only %d calls remaining today!", rem)

    def _paused_for(self, data: dict[str, Any], model: str) -> float:
        """Seconds left in this model's 429 cooldown; 0 when it may be called.

        Files written by older versions hold `true` instead of a time: treat those as a
        cooldown that has already ended."""
        until = data.get("rate_limited", {}).get(model)
        if not isinstance(until, (int, float)) or isinstance(until, bool):
            return 0.0
        return max(float(until) - self._clock(), 0.0)

    @contextmanager
    def _file_lock(self) -> Iterator[None]:
        lock = self._path.with_suffix(".lock")
        deadline = time.time() + LOCK_WAIT_S
        while True:
            try:
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.close(fd)
                break
            except FileExistsError:
                if _older_than(lock, STALE_LOCK_S):
                    lock.unlink(missing_ok=True)
                    continue
                if time.time() > deadline:
                    raise BudgetExhausted(f"Could not take the LLM lock {lock}.") from None
                time.sleep(0.01)
        try:
            yield
        finally:
            lock.unlink(missing_ok=True)

    def _read_data(self) -> dict[str, Any]:
        try:
            saved = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {
                "date": self._today().isoformat(),
                "calls": 0,
                "by_model": {},
                "rate_limited": {},
            }
        except ValueError:
            logger.warning("%s is unreadable; failing closed.", self._path)
            return {
                "date": self._today().isoformat(),
                "calls": self.max_per_day,
                "by_model": {},
                "rate_limited": {},
            }

        if not isinstance(saved, dict) or not isinstance(saved.get("calls"), int):
            logger.warning("%s has invalid structure; failing closed.", self._path)
            return {
                "date": self._today().isoformat(),
                "calls": self.max_per_day,
                "by_model": {},
                "rate_limited": {},
            }

        # Rollover check
        if saved.get("date") != self._today().isoformat():
            return {
                "date": self._today().isoformat(),
                "calls": 0,
                "by_model": {},
                "rate_limited": {},
            }

        return saved

    def _write_data(self, data: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary.replace(self._path)


def _older_than(path: Path, seconds: float) -> bool:
    try:
        return time.time() - path.stat().st_mtime > seconds
    except OSError:
        return False


_shared_llm_budgets: dict[Path, LlmBudget] = {}
_shared_llm_lock = threading.Lock()


def shared_llm_budget(path: Path, max_per_day: int = 20, reset_time: str = "unknown") -> LlmBudget:
    with _shared_llm_lock:
        b = _shared_llm_budgets.get(path)
        if b is None or b.max_per_day != max_per_day:
            b = LlmBudget(path, max_per_day, reset_time)
            _shared_llm_budgets[path] = b
        return b
