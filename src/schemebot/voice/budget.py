"""A daily cap on Gnani calls, so a bug or a busy demo cannot use up the free credits.

The count is kept in a small JSON file (`{"date": "2026-10-26", "calls": 12}`), so it survives
restarts and is shared by the web app and the compare script. A call is counted before it is
sent, so failed calls count too: Gnani may still charge for them. The day changes at midnight
India time.

Several processes can share the file (the web app and the compare script), so every read and
write happens while holding a lock file next to it (`gnani-calls.lock`), made with an
exclusive create, which works the same on Windows and Linux. When in doubt the cap fails
closed: a broken count file or a lock that cannot be taken means no call is sent.
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

IST = timezone(timedelta(hours=5, minutes=30))
CALLS_FILE_NAME = "gnani-calls.json"
LOCK_WAIT_S = 5.0
STALE_LOCK_S = 30.0
"""A lock file older than this was left by a process that crashed; it is removed."""

logger = logging.getLogger(__name__)


def today_in_india() -> date:
    return datetime.now(UTC).astimezone(IST).date()


class BudgetExhausted(Exception):
    pass


class CallBudget:
    def __init__(
        self, path: Path, max_per_day: int, today: Callable[[], date] = today_in_india
    ) -> None:
        self._path = path
        self.max_per_day = max_per_day
        self._today = today
        self._lock = threading.Lock()

    def used_today(self) -> int:
        with self._lock, self._file_lock():
            return self._read_count()

    def remaining(self) -> int:
        return max(self.max_per_day - self.used_today(), 0)

    def take(self) -> None:
        """Count one call, or raise BudgetExhausted if today's cap is reached."""
        with self._lock, self._file_lock():
            used = self._read_count()
            if used >= self.max_per_day:
                raise BudgetExhausted(f"Daily Gnani limit of {self.max_per_day} calls reached.")
            self._write_count(used + 1)

    @contextmanager
    def _file_lock(self) -> Iterator[None]:
        lock = self._path.with_suffix(".lock")
        lock.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + LOCK_WAIT_S
        while True:
            try:
                os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
                break
            except FileExistsError:
                if _older_than(lock, STALE_LOCK_S):
                    lock.unlink(missing_ok=True)
                elif time.monotonic() > deadline:
                    raise BudgetExhausted(f"Could not take the lock {lock}.") from None
                else:
                    time.sleep(0.01)
        try:
            yield
        finally:
            lock.unlink(missing_ok=True)

    def _read_count(self) -> int:
        try:
            saved = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return 0
        except ValueError:
            saved = None
        calls = saved.get("calls") if isinstance(saved, dict) else None
        if not isinstance(calls, int):
            logger.warning("%s is unreadable; no Gnani calls until it is deleted", self._path)
            return self.max_per_day
        if saved.get("date") != self._today().isoformat():
            return 0
        return calls

    def _write_count(self, calls: int) -> None:
        # Write to a temporary file, then rename: a crash mid-write never leaves half a file.
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(f".{os.getpid()}.tmp")
        record = {"date": self._today().isoformat(), "calls": calls}
        temporary.write_text(json.dumps(record), encoding="utf-8")
        temporary.replace(self._path)


def _older_than(path: Path, seconds: float) -> bool:
    try:
        return time.time() - path.stat().st_mtime > seconds
    except FileNotFoundError:
        return False


_shared: dict[Path, CallBudget] = {}
_shared_lock = threading.Lock()


def shared_budget(path: Path, max_per_day: int) -> CallBudget:
    """One budget object per file in this process, so STT and TTS share one lock."""
    with _shared_lock:
        budget = _shared.get(path)
        if budget is None or budget.max_per_day != max_per_day:
            budget = CallBudget(path, max_per_day)
            _shared[path] = budget
        return budget
