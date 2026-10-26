import json
from datetime import date
from pathlib import Path

import pytest

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


def test_broken_file_counts_as_zero(tmp_path: Path) -> None:
    path = tmp_path / "calls.json"
    path.write_text("not json")

    assert CallBudget(path, 3, Day(DAY_ONE)).remaining() == 3


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
