from pathlib import Path

import pymupdf
import pytest

from schemebot.ingest.extract import (
    OcrUnavailableError,
    extract_pages,
    is_legacy_font,
    needs_ocr,
    normalize_text,
)

ENGLISH_PARAGRAPH = (
    "Eligibility: The applicant must be a resident of Tamil Nadu and the annual family "
    "income must not exceed Rs. 2.5 lakh. Documents required: Aadhaar card, ration card."
)


def make_pdf(path: Path, pages: list[str]) -> Path:
    """Write a PDF with one page per string; an empty string makes a blank (scanned-like) page."""
    document = pymupdf.open()
    for text in pages:
        page = document.new_page()
        if text:
            page.insert_textbox(pymupdf.Rect(50, 50, 550, 800), text, fontsize=11)
    document.save(path)
    document.close()
    return path


def test_text_pdf_is_extracted_without_ocr(tmp_path: Path) -> None:
    pdf = make_pdf(tmp_path / "scheme.pdf", [ENGLISH_PARAGRAPH, ENGLISH_PARAGRAPH])

    pages = extract_pages(pdf, ocr=lambda page: pytest.fail("OCR should not run"))

    assert [page.page for page in pages] == [1, 2]
    assert all(page.method == "text" for page in pages)
    assert "Aadhaar card" in pages[0].text


def test_blank_page_goes_to_ocr(tmp_path: Path) -> None:
    pdf = make_pdf(tmp_path / "scanned.pdf", [ENGLISH_PARAGRAPH, ""])

    pages = extract_pages(pdf, ocr=lambda page: "தகுதி: தமிழ்நாட்டில் வசிப்பவர்")

    assert pages[0].method == "text"
    assert pages[1].method == "ocr"
    assert pages[1].text.startswith("தகுதி")


def test_force_ocr_overrides_a_good_text_layer(tmp_path: Path) -> None:
    pdf = make_pdf(tmp_path / "legacy.pdf", [ENGLISH_PARAGRAPH])

    pages = extract_pages(pdf, ocr=lambda page: "ocr text", force_ocr=True)

    assert pages[0].method == "ocr"


def test_missing_ocr_marks_page_unverified_instead_of_crashing(tmp_path: Path) -> None:
    def broken_ocr(page: pymupdf.Page) -> str:
        raise OcrUnavailableError("tesseract not installed")

    pdf = make_pdf(tmp_path / "scanned.pdf", [""])

    assert extract_pages(pdf, ocr=broken_ocr)[0].method == "text-unverified"
    assert extract_pages(pdf, ocr=None)[0].method == "text-unverified"


def test_good_english_and_tamil_text_do_not_need_ocr() -> None:
    tamil = "இத்திட்டத்தின் கீழ் தகுதியுள்ள குடும்பத் தலைவிகளுக்கு மாதம் ரூ.1000 வழங்கப்படும்."

    assert not needs_ocr(ENGLISH_PARAGRAPH)
    assert not needs_ocr(tamil)


def test_legacy_font_garbage_needs_ocr() -> None:
    # What Bamini-style legacy Tamil fonts typically look like after text extraction.
    garbled = "jkpo;ehL muR [hjpfs; ky;yhUf;F nkhopapy; tpz;zg;gq;fs; ngwg;gLk;"

    assert needs_ocr(garbled)


def test_replacement_characters_need_ocr() -> None:
    # Long enough to pass the length check, so only the bad characters can trigger OCR.
    assert needs_ocr(("Eligibility " + chr(0xFFFD) * 3 + " ") * 5)


def test_normalize_text_tidies_whitespace_and_hyphenation() -> None:
    no_break_space = chr(0xA0)
    raw = f"Docu-\nments  required:{no_break_space}Aadhaar\n\n\n\nRation   card"

    assert normalize_text(raw) == "Documents required: Aadhaar\n\nRation card"


def test_normalize_text_composes_tamil_to_nfc() -> None:
    decomposed = chr(0x0B95) + chr(0x0BC6) + chr(0x0BBE)  # KA + E + AA

    assert normalize_text(decomposed) == chr(0x0B95) + chr(0x0BCA)  # KA + O


def test_normalize_text_removes_zero_width_characters() -> None:
    zwnj = chr(0x200C)
    ocr_output = f"விண்ணப்பதாரர்{zwnj} தமிழ்நாட்டில்{zwnj}"

    assert normalize_text(ocr_output) == "விண்ணப்பதாரர் தமிழ்நாட்டில்"


def test_page_of_punctuation_left_by_unmapped_font_needs_ocr() -> None:
    # Real output from a TAU-Marutham page: the Tamil glyphs vanished, numbering stayed.
    residue = ". ii) . iii) . iv) , . v) , . 21 , , . vi) , . 2.1.3. . i) .2.5 . ii) . iii) ."

    assert needs_ocr(residue * 2)


@pytest.mark.parametrize(
    ("font_name", "expected"),
    [
        ("ABCDEE+TAU-Marutham", True),
        ("Bamini", True),
        ("KrutiDev010", True),
        ("CAAAAA+MeeraInimai-Regular", False),
        ("BAAAAA+Verdana", False),
        ("Arial,Bold", False),
    ],
)
def test_detects_legacy_indic_fonts(font_name: str, expected: bool) -> None:
    assert is_legacy_font(font_name) is expected


def test_devanagari_with_broken_font_map_needs_ocr() -> None:
    # Real text layer of a pmkisan.gov.in note: "क" was mapped to the vowel sign "ि".
    broken = "पीएम-किसान योजना िृषि एवं किसान िल्याण मंत्रालय िृषि एवं किसान िल्याण षवभाग "

    assert needs_ocr(broken * 3)


def test_correct_devanagari_does_not_need_ocr() -> None:
    correct = "पीएम-किसान योजना कृषि एवं किसान कल्याण मंत्रालय कृषि एवं किसान कल्याण विभाग "

    assert not needs_ocr(correct * 3)
