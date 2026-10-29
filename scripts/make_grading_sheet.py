"""Generates a standardized human grading sheet for answer-level evaluation.

Columns:
- question_id
- language
- question
- answer_text
- cited_passages
- number_correct (y / n / na)
- citation_supports (y / n)
- unsupported_claim (y / n)
- notes

Source:
Accepts a JSON file of generated answers or pulls questions from data/eval/questions.json.
Writes to docs/review/grading_sheet.csv.
"""

import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT_ROOT / "docs" / "review" / "grading_sheet.csv"


def make_sheet(source_json: Path | None = None, output_csv: Path = DEFAULT_OUT) -> int:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    items = []
    if source_json and source_json.is_file():
        data = json.loads(source_json.read_text(encoding="utf-8"))
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "answers" in data:
            items = data["answers"]
    else:
        # Fallback to dev questions
        q_file_json = PROJECT_ROOT / "data" / "eval" / "questions.json"
        q_file_jsonl = PROJECT_ROOT / "data" / "eval" / "questions.jsonl"
        if q_file_jsonl.is_file():
            for idx, line in enumerate(q_file_jsonl.read_text(encoding="utf-8").splitlines()):
                if not line.strip():
                    continue
                q = json.loads(line)
                items.append({
                    "question_id": q.get("id", f"q_{idx:03d}"),
                    "language": q.get("language", "en"),
                    "question": q.get("question", ""),
                    "answer_text": "PENDING_RUN",
                    "cited_passages": "PENDING_RUN",
                })
        elif q_file_json.is_file():
            questions = json.loads(q_file_json.read_text(encoding="utf-8"))
            for idx, q in enumerate(questions):
                items.append({
                    "question_id": q.get("id", f"q_{idx:03d}"),
                    "language": q.get("language", "en"),
                    "question": q.get("question", ""),
                    "answer_text": "PENDING_RUN",
                    "cited_passages": "PENDING_RUN",
                })

    fieldnames = [
        "question_id",
        "language",
        "question",
        "answer_text",
        "cited_passages",
        "number_correct",
        "citation_supports",
        "unsupported_claim",
        "notes",
    ]

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for it in items:
            writer.writerow({
                "question_id": it.get("question_id", it.get("id", "")),
                "language": it.get("language", ""),
                "question": it.get("question", ""),
                "answer_text": it.get("answer_text", it.get("text", "")),
                "cited_passages": it.get("cited_passages", ""),
                "number_correct": it.get("number_correct", ""),
                "citation_supports": it.get("citation_supports", ""),
                "unsupported_claim": it.get("unsupported_claim", ""),
                "notes": it.get("notes", ""),
            })

    print(f"Generated human grading sheet at {output_csv} with {len(items)} items.")
    return len(items)


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    make_sheet(src, out)


if __name__ == "__main__":
    main()
