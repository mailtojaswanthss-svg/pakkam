import json
from pathlib import Path

import pymupdf
import pytest

from schemebot.config import Settings
from schemebot.ingest.pipeline import load_manifest, read_chunks, run_ingest

GUIDELINES = """Eligibility
Women heads of families with annual income below Rs. 2.5 lakh.

How to apply
Submit the application form at the camp with Aadhaar and ration card."""


def make_entry(doc_id: str, file: str) -> dict[str, object]:
    return {
        "doc_id": doc_id,
        "scheme": "Test Scheme",
        "file": file,
        "source_url": "https://example.gov.in/guidelines.pdf",
        "language": "en",
        "doc_date": "2024-01-15",
        "accessed": "2026-10-25",
    }


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    (tmp_path / "raw").mkdir()
    document = pymupdf.open()
    page = document.new_page()
    page.insert_textbox(pymupdf.Rect(50, 50, 550, 800), GUIDELINES, fontsize=11)
    document.save(tmp_path / "raw" / "guidelines.pdf")
    document.close()
    return tmp_path


def write_manifest(data_dir: Path, entries: list[dict[str, object]]) -> None:
    (data_dir / "sources.json").write_text(json.dumps(entries), encoding="utf-8")


def test_ingest_writes_chunks_and_report(data_dir: Path) -> None:
    write_manifest(data_dir, [make_entry("test-guidelines-en", "guidelines.pdf")])
    settings = Settings(_env_file=None, data_dir=data_dir)

    report = run_ingest(settings, ocr_factory=None)

    chunks = read_chunks(data_dir / "processed" / "chunks.jsonl")
    assert report.total_chunks == len(chunks) == 2
    assert [chunk.section for chunk in chunks] == ["Eligibility", "How to apply"]
    assert report.documents[0].pages_by_method == {"text": 1}
    assert (data_dir / "processed" / "ingest_report.json").is_file()


def test_missing_file_is_reported_not_fatal(data_dir: Path) -> None:
    write_manifest(
        data_dir,
        [make_entry("test-guidelines-en", "guidelines.pdf"), make_entry("gone-en", "gone.pdf")],
    )
    settings = Settings(_env_file=None, data_dir=data_dir)

    report = run_ingest(settings, ocr_factory=None)

    assert report.missing_files == ["gone.pdf"]
    assert report.total_chunks == 2


def test_manifest_rejects_duplicate_ids(data_dir: Path) -> None:
    entry = make_entry("dup-en", "guidelines.pdf")
    write_manifest(data_dir, [entry, entry])

    with pytest.raises(ValueError, match="duplicate doc_id"):
        load_manifest(data_dir / "sources.json")


def test_manifest_rejects_bad_doc_id(data_dir: Path) -> None:
    write_manifest(data_dir, [make_entry("Not A Slug", "guidelines.pdf")])

    with pytest.raises(ValueError):
        load_manifest(data_dir / "sources.json")
