"""Markdown results table, stamped with what produced it so it can be re-run."""

import math
import subprocess
from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from schemebot.evaluation.dataset import GROUPS
from schemebot.evaluation.metrics import RECALL_KS, QuestionResult, Summary, summarize

GROUP_NAMES = {"en": "English", "ta": "Tamil", "hi": "Hindi", "ta-Latn": "Tanglish"}


def git_revision(repo: Path) -> str:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return f"{commit}{' (uncommitted changes)' if dirty else ''}"


def _pct(value: float) -> str:
    return "–" if math.isnan(value) else f"{value * 100:.0f}%"


def _ms(value: float) -> str:
    return "–" if math.isnan(value) else f"{value:,.0f}"


def _row(name: str, s: Summary, full: bool) -> str:
    cells = [
        name,
        f"{s.answerable}/{s.unanswerable}",
        *(_pct(s.recall[k]) for k in RECALL_KS),
        f"{s.mrr:.2f}" if not math.isnan(s.mrr) else "–",
        _pct(s.correct_refusal),
        _pct(s.false_refusal),
    ]
    if full:
        cells += [_pct(s.faithfulness), _pct(s.citation_accuracy)]
    cells += [f"{_ms(s.retrieval_p50)} / {_ms(s.retrieval_p95)}"]
    if full:
        cells += [f"{_ms(s.total_p50)} / {_ms(s.total_p95)}"]
    return "| " + " | ".join(cells) + " |"


def render(results: Sequence[QuestionResult], run_info: dict[str, str], full: bool) -> str:
    header = ["Group", "Ans/Unans", *(f"Recall@{k}" for k in RECALL_KS), "MRR",
              "Correct refusal", "False refusal"]  # fmt: skip
    if full:
        header += ["Faithfulness", "Citation acc."]
    header += ["Retrieval ms p50 / p95"]
    if full:
        header += ["End-to-end ms p50 / p95"]

    lines = ["# Evaluation results", ""]
    drafts = sum(r.status == "draft" for r in results)
    if drafts:
        lines += [
            f"> **{drafts} of {len(results)} questions are unverified drafts.** These numbers "
            "are for development only until every label has been checked by a person.",
            "",
        ]
    lines += [f"- **{key}:** {value}" for key, value in run_info.items()]
    lines += ["", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for group in GROUPS:
        group_results = [r for r in results if r.group == group]
        if group_results:
            lines.append(_row(GROUP_NAMES[group], summarize(group_results), full))
    lines.append(_row("**All**", summarize(results), full))
    lines += [
        "",
        "Recall@k and MRR: share of answerable questions with a gold page in the top k "
        "passages, and mean reciprocal rank of the first one. Correct refusal: share of "
        "unanswerable questions refused. False refusal: share of answerable questions refused.",
    ]
    if full:
        lines.append(
            "Faithfulness: share of answer sentences an independent judge found supported by "
            "their cited passages. Citation accuracy: share of citations pointing to a gold page."
        )
    else:
        lines.append(
            "Retrieval-only run: refusal means retrieval confidence was below the threshold; "
            "answer metrics need a Claude API key."
        )
    return "\n".join(lines) + "\n"


def run_stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%SZ")


def per_question_rows(results: Sequence[QuestionResult]) -> list[dict[str, object]]:
    return [asdict(result) for result in results]
