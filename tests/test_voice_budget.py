import json
import multiprocessing
import os
import time
from datetime import date
from pathlib import Path

import pytest

from schemebot.voice import budget as budget_module
from schemebot.voice.budget import BudgetExhausted, CallBudget
from schemebot.voice.stt import BudgetedTranscriber, SttError

DAY_ONE = date(2026, 10, 26)
DAY_TWO = date(2026, 10, 27)


class Day:
    def __init__(self, day: date) -> None:
        self.day = day

    def __call__(self) -> date:
        return self.day


class FailingStt:
    def __init__(self) -> None:
        self.calls = 0

    def transcribe(self, audio: bytes, filename: str, language_code: str) -> str:
        self.calls += 1
        raise SttError("The speech service could not read this recording.")


def test_take_counts_until_the_cap(tmp_path: Path) -> None:
    budget = CallBudget(tmp_path / "calls.json", 2, Day(DAY_ONE))

    budget.take()
    budget.take()

    assert budget.remaining() == 0
    with pytest.raises(BudgetExhausted):
        budget.take()


def test_count_survives_a_restart(tmp_path: Path) -> None:
    path = tmp_path / "calls.json"
    CallBudget(path, 5, Day(DAY_ONE)).take()

    restarted = CallBudget(path, 5, Day(DAY_ONE))

    assert restarted.used_today() == 1
    assert json.loads(path.read_text()) == {"date": "2026-10-26", "calls": 1}


def test_count_resets_on_a_new_day(tmp_path: Path) -> None:
    today = Day(DAY_ONE)
    budget = CallBudget(tmp_path / "calls.json", 1, today)
    budget.take()

    today.day = DAY_TWO

    assert budget.remaining() == 1


@pytest.mark.parametrize("content", ["not json", "[]", '{"date": "2026-10-26"}'])
def test_broken_file_stops_calls(tmp_path: Path, content: str) -> None:
    # Fail closed: a count we cannot read must not reset the cap to zero.
    path = tmp_path / "calls.json"
    path.write_text(content)

    budget = CallBudget(path, 3, Day(DAY_ONE))

    assert budget.remaining() == 0
    with pytest.raises(BudgetExhausted):
        budget.take()


def _take_many(args: tuple[Path, int]) -> list[str]:
    """Run in a separate process: take `count` calls, return the errors of those that failed."""
    path, count = args
    budget = CallBudget(path, 10_000, Day(DAY_ONE))
    errors = []
    for _ in range(count):
        try:
            budget.take()
        except Exception as error:
            errors.append(repr(error))
    return errors


def test_processes_sharing_the_file_lose_no_calls(tmp_path: Path) -> None:
    # The web app and the compare script can run at the same time.
    path = tmp_path / "calls.json"
    # "spawn", as on Windows, also avoids forking a process that runs threads.
    with multiprocessing.get_context("spawn").Pool(4) as pool:
        errors = pool.map(_take_many, [(path, 50)] * 4)

    assert errors == [[], [], [], []]
    assert CallBudget(path, 10_000, Day(DAY_ONE)).used_today() == 200
    assert not path.with_suffix(".lock").exists()


def test_lock_being_deleted_on_windows_is_waited_for(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Windows refuses to create a file another process is still deleting.
    real_open = os.open
    refusals = [PermissionError(13, "Access is denied")]

    def open_like_windows(path: str, flags: int, mode: int = 0o777) -> int:
        if refusals and str(path).endswith(".lock"):
            raise refusals.pop()
        return real_open(path, flags, mode)

    monkeypatch.setattr(budget_module.os, "open", open_like_windows)
    budget = CallBudget(tmp_path / "calls.json", 3, Day(DAY_ONE))

    budget.take()

    assert budget.used_today() == 1


def test_lock_left_by_a_crashed_process_is_removed(tmp_path: Path) -> None:
    path = tmp_path / "calls.json"
    lock = path.with_suffix(".lock")
    lock.touch()
    old = time.time() - 60
    os.utime(lock, (old, old))

    CallBudget(path, 3, Day(DAY_ONE)).take()

    assert json.loads(path.read_text())["calls"] == 1


def test_lock_held_too_long_stops_the_call(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(budget_module, "LOCK_WAIT_S", 0.05)
    path = tmp_path / "calls.json"
    path.with_suffix(".lock").touch()  # fresh: another process is using the file

    with pytest.raises(BudgetExhausted):
        CallBudget(path, 3, Day(DAY_ONE)).take()


def test_failed_calls_are_counted(tmp_path: Path) -> None:
    budget = CallBudget(tmp_path / "calls.json", 3, Day(DAY_ONE))
    stt = BudgetedTranscriber(FailingStt(), budget)

    with pytest.raises(SttError):
        stt.transcribe(b"audio", "q.wav", "ta-IN")

    assert budget.used_today() == 1


def test_no_call_is_sent_once_the_cap_is_reached(tmp_path: Path) -> None:
    inner = FailingStt()
    stt = BudgetedTranscriber(inner, CallBudget(tmp_path / "calls.json", 0, Day(DAY_ONE)))

    with pytest.raises(SttError) as caught:
        stt.transcribe(b"audio", "q.wav", "ta-IN")

    assert caught.value.status_code == 503
    assert "today's limit" in caught.value.message
    assert inner.calls == 0
