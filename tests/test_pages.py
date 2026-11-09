from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from schemebot.api.main import create_app
from schemebot.api.pages import PageUnavailable, _pieces, render_page

pymupdf = pytest.importorskip("pymupdf")


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    path = tmp_path / "order.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 100), "Families with annual income below Rs.2.5 lakh are eligible.")
    page.insert_text((72, 130), "The entitlement is Rs.1,000 per month to the woman head.")
    doc.save(path)
    doc.close()
    return path


def test_renders_the_page_as_png_and_marks_the_passage(pdf: Path) -> None:
    plain = render_page(pdf, 1)
    marked = render_page(pdf, 1, "Families with annual income below Rs.2.5 lakh are eligible.")

    assert plain.startswith(b"\x89PNG")
    assert marked.startswith(b"\x89PNG") and marked != plain  # the highlight changes pixels


def test_out_of_range_page_or_missing_file_is_unavailable(pdf: Path) -> None:
    with pytest.raises(PageUnavailable):
        render_page(pdf, 2)
    with pytest.raises(PageUnavailable):
        render_page(pdf.with_name("missing.pdf"), 1)


def test_search_pieces_skip_fragments_and_shorten_long_clauses() -> None:
    pieces = _pieces("i) Rs.2.5 lakh. ok. " + "word " * 30)
    assert "ok." not in pieces
    assert all(len(p) <= 60 for p in pieces)


class NoService:
    def answer(self, question: str, voice_mode: bool = False) -> object:
        raise AssertionError("not used")


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    with TestClient(create_app(lambda: NoService(), log_dir=tmp_path)) as test_client:
        yield test_client


def test_only_documents_in_sources_json_can_be_requested(client: TestClient) -> None:
    assert client.get("/page", params={"doc": "../../etc/passwd", "p": 1}).status_code == 404


def test_a_known_document_without_its_pdf_on_disk_is_404(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SCHEMEBOT_DATA_DIR", str(tmp_path))
    response = client.get("/page", params={"doc": "apy-brochure-en", "p": 1})
    assert response.status_code == 404


# --- Scanned pages: the excerpt is found among OCR words and painted yellow ---

from schemebot.api import pages as pages_module  # noqa: E402
from schemebot.api.pages import Word, _line_boxes, _match_span, _normalise  # noqa: E402

OCR_LINE = [
    "குடும்பங்களாக",
    "இருத்தல்\u200c",
    "வேண்டும்\u200c.",
    "i)",
    "ஆண்டு",
    "வருமானம்\u200c",
    "e.2.5",
    "இலட்சத்திற்குக்\u200c",
    "கீழ்\u200c",
    "வருமானம்\u200c",
    "ஈட்டும்\u200c",
    "குடும்பங்கள்\u200c.",
]
EXCERPT = "குடும்பத்தின் ஆண்டு வருமானம் ரூ.2.5 இலட்சத்திற்குக் கீழ் இருக்க வேண்டும்."


def test_normalise_drops_joiners_and_compares_numbers_by_digits() -> None:
    assert _normalise("வருமானம்‌") == "வருமானம்"
    assert _normalise("ரூ.2.5") == _normalise("e.2.5") == "25"
    assert _normalise("௨௫") == "25"


def test_match_span_finds_the_cited_words_despite_ocr_noise() -> None:
    found = [OCR_LINE[i] for i in _match_span(OCR_LINE, EXCERPT)]
    assert found[0] == "ஆண்டு" and "e.2.5" in found and found[-1].startswith("கீழ்")


def test_match_span_refuses_a_weak_match() -> None:
    assert _match_span(OCR_LINE, "Atal Pension Yojana subscriber gets a monthly pension") == []


def test_line_boxes_merge_words_on_the_same_line() -> None:
    words = [
        Word("a", 10, 20, 30, 10, (1, 1, 1)),
        Word("b", 50, 22, 20, 10, (1, 1, 1)),
        Word("c", 10, 60, 30, 10, (1, 1, 2)),
    ]
    boxes = _line_boxes(words, [0, 1, 2])
    assert len(boxes) == 2 and boxes[0][0] < 10 and boxes[0][2] > 70


def test_scanned_page_is_painted_yellow_from_ocr_words(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "scan.pdf"
    doc = pymupdf.open()
    doc.new_page()  # no text layer, like a scanned order
    doc.save(path)
    doc.close()
    fake = [Word(w, 100 + 60 * i, 300, 50, 20, (1, 1, 1)) for i, w in enumerate(OCR_LINE)]
    monkeypatch.setattr(pages_module, "_ocr_words", lambda *args: fake)
    from PIL import Image

    png = render_page(path, 1, EXCERPT, "ta")
    image = Image.open(__import__("io").BytesIO(png)).convert("RGB")
    yellow = sum(1 for r, g, b in image.getdata() if r > 240 and g > 220 and b < 160)
    assert yellow > 100
