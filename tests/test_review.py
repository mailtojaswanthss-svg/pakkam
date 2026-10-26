import csv
import json
from pathlib import Path

from schemebot.evaluation.dataset import load_questions
from schemebot.evaluation.review import export_sheet, import_sheet
from tests.conftest import make_chunk

QUESTIONS = [
    {"id": "q1", "group": "ta", "question": "அடல் ஓய்வூதியம் வயது?", "answerable": True,
     "gold": [{"doc_id": "apy-en", "pages": [1]}], "reference": "18 to 40.", "fact": "apy_age",
     "status": "draft"},
    {"id": "q2", "group": "en", "question": "PPF rate?", "answerable": False, "gold": [],
     "reference": "Not covered.", "fact": None, "status": "draft"},
]  # fmt: skip


def write_inputs(tmp_path: Path) -> tuple[Path, Path]:
    questions = tmp_path / "questions.jsonl"
    questions.write_text(
        "".join(json.dumps(q, ensure_ascii=False) + "\n" for q in QUESTIONS), encoding="utf-8"
    )
    chunks = tmp_path / "chunks.jsonl"
    chunk = make_chunk("apy-en-001", "Citizens aged 18 to 40 can join APY.")
    chunks.write_text(chunk.model_dump_json() + "\n", encoding="utf-8")
    return questions, chunks


def test_export_shows_question_reference_and_gold_page_text(tmp_path: Path) -> None:
    questions, chunks = write_inputs(tmp_path)
    sheet = tmp_path / "review.csv"

    assert export_sheet(questions, chunks, sheet) == 2

    with sheet.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    assert rows[0]["question"] == "அடல் ஓய்வூதியம் வயது?"
    assert rows[0]["gold_pages"] == "apy-en p1"
    assert "aged 18 to 40" in rows[0]["gold_text"]
    assert rows[1]["gold_text"] == ""


def test_import_marks_verified_rows_and_applies_corrections(tmp_path: Path) -> None:
    questions, chunks = write_inputs(tmp_path)
    sheet = tmp_path / "review.csv"
    export_sheet(questions, chunks, sheet)
    with sheet.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    rows[0]["verified"] = "Yes"
    rows[0]["corrected_question"] = "அடல் ஓய்வூதியத் திட்டத்தில் சேர வயது வரம்பு என்ன?"
    with sheet.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    assert import_sheet(questions, sheet) == 1

    loaded = {q.id: q for q in load_questions(questions)}
    assert loaded["q1"].status == "verified"
    assert loaded["q1"].question.startswith("அடல் ஓய்வூதியத் திட்டத்தில்")
    assert loaded["q2"].status == "draft"
