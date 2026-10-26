"""Hand the question set to a native speaker as a spreadsheet, and read their verdicts back.

    uv run python -m schemebot.evaluation.review export review.csv
    (open in Excel or Google Sheets: check each row, put "yes" in `verified`, fix wording)
    uv run python -m schemebot.evaluation.review import review.csv

Each row shows the question, the short reference answer and the text of its gold pages, so
the reviewer can check the label without opening the PDFs. Importing marks rows with
`verified = yes` as verified and applies any corrected question or reference text.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from schemebot.config import get_settings
from schemebot.evaluation.dataset import load_questions
from schemebot.ingest.pipeline import CHUNKS_NAME, read_chunks

EXCERPT_CHARS = 600
MISSING = "(page not indexed)"
COLUMNS = (
    "id", "group", "status", "question", "reference", "gold_pages", "gold_text",
    "verified", "corrected_question", "corrected_reference", "notes",
)  # fmt: skip
YES = {"yes", "y", "true", "1", "ok"}


def page_texts(chunks_path: Path) -> dict[tuple[str, int], str]:
    texts: dict[tuple[str, int], str] = defaultdict(str)
    for chunk in read_chunks(chunks_path):
        for page in range(chunk.page_start, chunk.page_end + 1):
            if chunk.text not in texts[(chunk.doc_id, page)]:
                texts[(chunk.doc_id, page)] += chunk.text + "\n"
    return texts


def export_sheet(questions_path: Path, chunks_path: Path, out: Path) -> int:
    texts = page_texts(chunks_path)
    questions = load_questions(questions_path)
    # utf-8-sig so Excel shows Tamil and Hindi correctly.
    with out.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        for q in questions:
            pages = [(g.doc_id, p) for g in q.gold for p in g.pages]
            writer.writerow({
                "id": q.id, "group": q.group, "status": q.status, "question": q.question,
                "reference": q.reference,
                "gold_pages": "; ".join(f"{doc} p{page}" for doc, page in pages),
                "gold_text": " | ".join(
                    f"[{doc} p{page}] {texts.get((doc, page), MISSING)[:EXCERPT_CHARS]}"
                    for doc, page in pages[:3]
                ),
                "verified": "yes" if q.status == "verified" else "",
            })  # fmt: skip
    return len(questions)


def import_sheet(questions_path: Path, sheet: Path) -> int:
    """Apply a reviewed sheet. Returns how many questions are now verified."""
    with sheet.open(encoding="utf-8-sig", newline="") as file:
        reviewed = {row["id"]: row for row in csv.DictReader(file)}
    rows = [json.loads(line) for line in questions_path.open(encoding="utf-8") if line.strip()]
    for row in rows:
        review = reviewed.get(row["id"])
        if review is None:
            continue
        if review.get("corrected_question", "").strip():
            row["question"] = review["corrected_question"].strip()
        if review.get("corrected_reference", "").strip():
            row["reference"] = review["corrected_reference"].strip()
        if review.get("verified", "").strip().lower() in YES:
            row["status"] = "verified"
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    questions_path.write_text(text, encoding="utf-8")
    load_questions(questions_path)  # fail loudly if the result is not a valid question set
    return sum(r["status"] == "verified" for r in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export or import a question review sheet.")
    parser.add_argument("action", choices=["export", "import"])
    parser.add_argument("sheet", type=Path, help="CSV file to write or read")
    args = parser.parse_args()
    settings = get_settings()
    if args.action == "export":
        count = export_sheet(
            settings.eval_questions_path, settings.processed_dir / CHUNKS_NAME, args.sheet
        )
        print(f"wrote {count} questions to {args.sheet}")
    else:
        verified = import_sheet(settings.eval_questions_path, args.sheet)
        print(f"applied {args.sheet}: {verified} questions now verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
