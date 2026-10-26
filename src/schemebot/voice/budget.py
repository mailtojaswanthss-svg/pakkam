"""A daily cap on Gnani calls, so a bug or a busy demo cannot use up the free credits.

The count is kept in a small JSON file (`{"date": "2026-10-26", "calls": 12}`), so it survives
restarts and is shared by the web app and the compare script. A call is counted before it is
sent, so failed calls count too: Gnani may still charge for them. The day changes at midnight
India time.
"""

import json
import threading
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))
CALLS_FILE_NAME = "gnani-calls.json"


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
        with self._lock:
            return self._read_count()

    def remaining(self) -> int:
        return max(self.max_per_day - self.used_today(), 0)

    def take(self) -> None:
        """Count one call, or raise BudgetExhausted if today's cap is reached."""
        with self._lock:
            used = self._read_count()
            if used >= self.max_per_day:
                raise BudgetExhausted(f"Daily Gnani limit of {self.max_per_day} calls reached.")
            self._write_count(used + 1)

    def _read_count(self) -> int:
        try:
            saved = json.loads(self._path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            return 0
        if saved.get("date") != self._today().isoformat():
            return 0
        calls = saved.get("calls", 0)
        return calls if isinstance(calls, int) else 0

    def _write_count(self, calls: int) -> None:
        # Write to a temporary file, then rename: a crash mid-write never leaves half a file.
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(".tmp")
        record = {"date": self._today().isoformat(), "calls": calls}
        temporary.write_text(json.dumps(record), encoding="utf-8")
        temporary.replace(self._path)


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
