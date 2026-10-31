"""Tests for daily evaluation runner (scripts/run_daily.py)."""

import json
from pathlib import Path

from schemebot.generate.budget import LlmBudget, today_in_india
from scripts.run_daily import (
    MAX_SPARE_RESERVE,
    check_field_clips,
    check_held_out,
    check_teammate_eval,
    run_speed_retest,
    run_voice_loop_benchmark,
)


def test_speed_retest_skips_when_remaining_at_or_below_reserve(tmp_path: Path) -> None:
    calls_file = tmp_path / "llm-calls.json"
    budget = LlmBudget(calls_file, max_per_day=20)
    # Simulate 16 calls already used -> 4 remaining (<= 5 reserve)
    calls_file.write_text(
        json.dumps({"date": today_in_india().isoformat(), "calls": 16}), encoding="utf-8"
    )

    res = run_speed_retest(budget, dry_run=False)
    assert res["status"] == "SKIPPED"
    assert f"<={MAX_SPARE_RESERVE}" in res["reason"].replace(" ", "")


def test_speed_retest_dry_run_respects_reserve(tmp_path: Path) -> None:
    calls_file = tmp_path / "llm-calls.json"
    budget = LlmBudget(calls_file, max_per_day=20)
    # Simulate 10 calls used -> 10 remaining -> 5 usable above reserve
    calls_file.write_text(
        json.dumps({"date": today_in_india().isoformat(), "calls": 10}), encoding="utf-8"
    )

    res = run_speed_retest(budget, dry_run=True)
    assert res["status"] == "DRY_RUN"
    assert res["queries_planned"] == 3
    assert res["calls_available"] == 5


def test_blocker_detection() -> None:
    # Held out eval without .freeze -> BLK-01
    held_out = check_held_out()
    assert held_out["status"] == "BLOCKED"
    assert held_out["blocker_id"] == "BLK-01"

    # Teammate eval without file -> BLK-02
    teammate = check_teammate_eval()
    assert teammate["status"] == "BLOCKED"
    assert teammate["blocker_id"] == "BLK-02"

    # Field clip eval without audio -> BLK-03
    clips = check_field_clips()
    assert clips["status"] == "BLOCKED"
    assert clips["blocker_id"] == "BLK-03"


def test_voice_loop_timing_dry_run() -> None:
    res = run_voice_loop_benchmark(dry_run=True)
    assert res["status"] == "DRY_RUN"
    assert res["iterations"] == 10
