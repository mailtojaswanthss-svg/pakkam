"""Per-language results of one evaluation run, and the questions it got wrong.

    uv run python -m schemebot.evaluation.summary                 (latest run)
    uv run python -m schemebot.evaluation.summary RUN.jsonl --split dev --failures

Reads a per-question file from data/eval/runs/ (written by `python -m schemebot.evaluation`)
and the run information saved next to it, so the commit printed is the one the run used.

Splits: the refusal threshold and other settings were tuned on q001-q110 ("dev"), so only
q111-q194 ("held-out") is untouched by tuning. Look at dev failures when changing things;
report held-out numbers.
"""

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from schemebot.config import get_settings
from schemebot.evaluation.dataset import GROUPS, EvalQuestion, load_questions
from schemebot.evaluation.metrics import QuestionResult, summarize
from schemebot.evaluation.report import GROUP_NAMES

LAST_DEV_QUESTION = 110
SPLITS = ("all", "dev", "held-out")
INFO_SUFFIX = ".info.json"


def info_path(run_path: Path) -> Path:
    return run_path.with_suffix(INFO_SUFFIX)


def in_split(question_id: str, split: str) -> bool:
    if split == "all":
        return True
    dev = int(question_id.lstrip("q")) <= LAST_DEV_QUESTION
    return dev if split == "dev" else not dev


def load_run(path: Path) -> list[QuestionResult]:
    with path.open(encoding="utf-8") as file:
        return [QuestionResult(**json.loads(line)) for line in file if line.strip()]


def _pct(hits: float) -> str:
    return "  -" if hits != hits else f"{hits * 100:3.0f}%"  # NaN when n is 0


def table(results: Sequence[QuestionResult]) -> list[str]:
    full = any(r.total_ms is not None for r in results)
    header = f"{'Language':<9} {'n ans/unans':>11} {'R@1':>5} {'R@5':>5} {'false ref.':>10} "
    header += f"{'correct ref.':>12}"
    if full:
        header += f" {'model-judged faithfulness (sentences)':>38}"
    lines = [header]
    for name, group in [*((GROUP_NAMES[g], [r for r in results if r.group == g]) for g in GROUPS),
                        ("All", list(results))]:  # fmt: skip
        if not group:
            continue
        s = summarize(group)
        row = (
            f"{name:<9} {f'{s.answerable}/{s.unanswerable}':>11} {_pct(s.recall[1]):>5} "
            f"{_pct(s.recall[5]):>5} {_pct(s.false_refusal):>10} {_pct(s.correct_refusal):>12}"
        )
        if full:
            sentences = sum(len(r.sentences_supported) for r in group)
            row += f" {f'{_pct(s.faithfulness).strip()} of {sentences}':>38}"
        lines.append(row)
    return lines


def failures(results: Sequence[QuestionResult], questions: dict[str, EvalQuestion]) -> list[str]:
    """Answerable questions missed in the top 5 or refused, and unanswerable ones answered."""
    lines = []
    for r in results:
        if r.answerable and not any(r.relevant[:5]):
            kind = "gold page not in top 5"
        elif r.answerable and r.refused:
            kind = f"refused ({r.refusal_reason or 'low confidence'})"
        elif not r.answerable and not r.refused:
            kind = "answered, should refuse"
        else:
            continue
        question = questions.get(r.id)
        gold = (
            ", ".join(f"{g.doc_id}:p{','.join(map(str, g.pages))}" for g in question.gold)
            if question
            else "?"
        )
        lines += [
            f"{r.id} [{r.group}] {kind}, confidence {r.confidence:.2f}",
            f"    question: {question.question if question else '?'}",
            f"    gold:     {gold or '-'}",
            f"    top 3:    {', '.join(r.retrieved[:3]) or '-'}",
        ]
    return lines


def latest_run(runs_dir: Path) -> Path | None:
    runs = sorted(runs_dir.glob("*.jsonl"))
    return runs[-1] if runs else None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("run", nargs="?", help="per-question file; default: the latest run")
    parser.add_argument("--split", choices=SPLITS, default="all")
    parser.add_argument("--failures", action="store_true", help="list the questions it missed")
    args = parser.parse_args(argv)

    settings = get_settings()
    run_path = Path(args.run) if args.run else latest_run(settings.data_dir / "eval" / "runs")
    if run_path is None or not run_path.is_file():
        print("No run found. Run `python -m schemebot.evaluation --retrieval-only` first.",
              file=sys.stderr)  # fmt: skip
        return 1

    results = [r for r in load_run(run_path) if in_split(r.id, args.split)]
    info_file = info_path(run_path)
    info = json.loads(info_file.read_text(encoding="utf-8")) if info_file.is_file() else {}
    print(f"Run file: {run_path.name}")
    print(f"Run: {info.get('Run', 'unknown (no run information saved with this file)')}")
    print(f"Mode: {info.get('Mode', 'unknown')}")
    print(f"Split: {args.split} ({len(results)} questions)")
    drafts = sum(r.status == "draft" for r in results)
    if drafts:
        print(f"Labels: {drafts} of {len(results)} are unverified drafts (development only)")
    print()
    print("\n".join(table(results)))
    if args.failures:
        questions = {q.id: q for q in load_questions(settings.eval_questions_path)}
        missed = failures(results, questions)
        print(f"\nMissed ({len(missed) // 4}):")
        print("\n".join(missed) if missed else "    none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
