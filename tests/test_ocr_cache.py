from pathlib import Path

import pymupdf

from schemebot.ingest.extract import extract_pages
from schemebot.ingest.ocr_cache import cached_ocr
from tests.test_extract import make_pdf


class CountingOcr:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, page: pymupdf.Page) -> str:
        self.calls += 1
        return f"தகுதி பக்கம் {page.number + 1} வசிப்பவர் " * 3


def test_each_page_is_read_once_and_then_served_from_disk(tmp_path: Path) -> None:
    pdf = make_pdf(tmp_path / "scanned.pdf", ["", ""])
    ocr = CountingOcr()

    first = extract_pages(pdf, ocr=cached_ocr(ocr, tmp_path / "cache", pdf, "ta"))
    second = extract_pages(pdf, ocr=cached_ocr(ocr, tmp_path / "cache", pdf, "ta"))

    assert ocr.calls == 2  # two pages, each read once across both runs
    assert [p.text for p in first] == [p.text for p in second]
    assert all(p.method == "ocr" for p in second)


def test_a_changed_pdf_is_read_again(tmp_path: Path) -> None:
    pdf = make_pdf(tmp_path / "doc.pdf", [""])
    ocr = CountingOcr()
    extract_pages(pdf, ocr=cached_ocr(ocr, tmp_path / "cache", pdf, "ta"))

    make_pdf(pdf, ["", ""])  # replaced with a different file at the same path
    extract_pages(pdf, ocr=cached_ocr(ocr, tmp_path / "cache", pdf, "ta"))

    assert ocr.calls == 3


def test_another_language_gets_its_own_results(tmp_path: Path) -> None:
    pdf = make_pdf(tmp_path / "doc.pdf", [""])
    ocr = CountingOcr()

    extract_pages(pdf, ocr=cached_ocr(ocr, tmp_path / "cache", pdf, "ta"))
    extract_pages(pdf, ocr=cached_ocr(ocr, tmp_path / "cache", pdf, "hi"))

    assert ocr.calls == 2
