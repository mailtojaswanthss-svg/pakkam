import json
from dataclasses import asdict
from pathlib import Path

import pytest

from schemebot.evaluation.metrics import QuestionResult
from schemebot.evaluation.summary import in_split, info_path, main


def result(qid: str, group: str, answerable: bool, hit: bool, refused: bool) -> QuestionResult:
    return QuestionResult(
        id=qid,
        group=group,
        answerable=answerable,
        status="draft",
        retrieved=["doc-a:p1", "doc-b:p2"],
        relevant=[hit, False],
        confidence=0.5,
        retrieval_ms=100.0,
        refused=refused,
    )


@pytest.fixture
def run_file(tmp_path: Path) -> Path:
    results = [
        result("q001", "en", True, True, False),
        result("q002", "ta", True, False, True),  # dev miss
        result("q003", "ta", False, False, False),  # dev: answered, should refuse
        result("q150", "ta", True, True, False),  # held-out
    ]
    path = tmp_path / "2026-10-26T12-00-00Z-hybrid.jsonl"
    path.write_text("".join(json.dumps(asdict(r)) + "\n" for r in results), encoding="utf-8")
    info_path(path).write_text(
        json.dumps({"Run": "2026-10-26T12-00-00Z, commit abc1234", "Mode": "retrieval only"}),
        encoding="utf-8",
    )
    return path


def test_splits_follow_the_tuning_boundary() -> None:
    assert in_split("q110", "dev") and not in_split("q110", "held-out")
    assert in_split("q111", "held-out") and not in_split("q111", "dev")
    assert in_split("q194", "all")


def test_summary_prints_commit_n_and_per_language_rows(
    run_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([str(run_file)]) == 0
    out = capsys.readouterr().out

    assert "commit abc1234" in out
    assert "Split: all (4 questions)" in out
    assert "unverified drafts" in out
    tamil = next(line for line in out.splitlines() if line.startswith("Tamil"))
    assert "2/1" in tamil  # n answerable / unanswerable
    assert "model-judged" not in out  # retrieval-only run: no judge column


def test_held_out_split_leaves_dev_questions_out(
    run_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    main([str(run_file), "--split", "held-out"])
    out = capsys.readouterr().out

    assert "Split: held-out (1 questions)" in out


def test_failures_list_only_the_misses(run_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    main([str(run_file), "--split", "dev", "--failures"])
    out = capsys.readouterr().out

    assert "Missed (2):" in out
    assert "q002 [ta] gold page not in top 5" in out
    assert "q003 [ta] answered, should refuse" in out
    assert "q001 [" not in out


def test_full_run_names_the_faithfulness_as_model_judged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    full = result("q001", "en", True, True, False)
    full.total_ms = 4000.0
    full.sentences_supported = [True, True, False]
    path = tmp_path / "run.jsonl"
    path.write_text(json.dumps(asdict(full)) + "\n", encoding="utf-8")

    main([str(path)])
    out = capsys.readouterr().out

    assert "model-judged faithfulness" in out
    assert "67% of 3" in out
    assert "unknown (no run information" in out
