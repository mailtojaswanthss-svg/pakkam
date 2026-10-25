from datetime import date

import pytest

from schemebot.ingest.chunk import chunk_document, is_heading
from schemebot.ingest.extract import PageText
from schemebot.ingest.models import Chunk, SourceDoc

DOC = SourceDoc(
    doc_id="test-scheme-en",
    scheme="Test Scheme",
    file="test.pdf",
    source_url="https://example.gov.in/test.pdf",
    language="en",
    doc_date=date(2024, 1, 15),
    accessed=date(2026, 10, 25),
)

PAGE_ONE = """TEST SCHEME GUIDELINES

1. Objective
The scheme provides monthly financial assistance to women heads of families.

2. Eligibility
The applicant must be a resident of the state.
Annual family income must not exceed Rs. 2.5 lakh.

Page 1 of 2"""

PAGE_TWO = """3. Documents required:
Aadhaar card and ration card of the family.

4. How to apply
Apply at the nearest ration shop camp with the documents listed above."""


def sections(chunks: list[Chunk]) -> list[str | None]:
    return [chunk.section for chunk in chunks]


def test_chunks_follow_document_sections() -> None:
    pages = [PageText(1, PAGE_ONE, "text"), PageText(2, PAGE_TWO, "text")]

    chunks = chunk_document(DOC, pages)

    assert sections(chunks) == ["Objective", "Eligibility", "Documents required", "How to apply"]
    assert chunks[1].text == (
        "The applicant must be a resident of the state. "
        "Annual family income must not exceed Rs. 2.5 lakh."
    )


def test_chunks_carry_page_and_document_metadata() -> None:
    pages = [PageText(1, PAGE_ONE, "text"), PageText(2, PAGE_TWO, "ocr")]

    chunks = chunk_document(DOC, pages)
    how_to_apply = chunks[-1]

    assert how_to_apply.page_start == 2
    assert how_to_apply.doc_id == "test-scheme-en"
    assert how_to_apply.doc_date == date(2024, 1, 15)
    assert how_to_apply.extraction == "ocr"
    assert how_to_apply.chunk_id == "test-scheme-en-p2-003"


def test_page_numbers_are_not_part_of_any_chunk() -> None:
    chunks = chunk_document(DOC, [PageText(1, PAGE_ONE, "text")])

    assert all("Page 1 of 2" not in chunk.text for chunk in chunks)


def test_long_section_is_split_within_limit_with_overlap() -> None:
    short_para = "Short note on eligibility."
    long_para = "Income must be below the limit set by the department. " * 10
    page = "Eligibility\n\n" + "\n\n".join([long_para, short_para, long_para])

    chunks = chunk_document(DOC, [PageText(1, page, "text")], max_chars=700)

    assert len(chunks) >= 2
    assert all(len(chunk.text) <= 700 for chunk in chunks)
    assert all(chunk.section == "Eligibility" for chunk in chunks)
    # The short paragraph closes one chunk and is repeated at the start of the next.
    assert sum(short_para in chunk.text for chunk in chunks) == 2


def test_section_spanning_two_pages_records_page_range() -> None:
    pages = [
        PageText(1, "Eligibility\n\nResident of the state.", "text"),
        PageText(2, "Income below Rs. 2.5 lakh.", "text"),
    ]

    [chunk] = chunk_document(DOC, pages)

    assert (chunk.page_start, chunk.page_end) == (1, 2)


def test_chunk_language_is_detected_per_chunk() -> None:
    page = "தகுதி\n\nவிண்ணப்பதாரர் தமிழ்நாட்டில் வசிப்பவராக இருக்க வேண்டும்."

    [chunk] = chunk_document(DOC, [PageText(1, page, "text")])

    assert chunk.language == "ta"
    assert chunk.section == "தகுதி"


@pytest.mark.parametrize(
    "line",
    ["Eligibility", "2. Eligibility:", "HOW TO APPLY", "தேவையான ஆவணங்கள்", "पात्रता", "IV) Benefits"],
)
def test_recognises_headings(line: str) -> None:
    assert is_heading(line)


@pytest.mark.parametrize(
    "line",
    [
        "1. Aadhaar card",
        "The eligibility criteria are listed below.",
        "Benefits are paid monthly to the bank account of the beneficiary, as notified.",
        "",
        "DDDDDDD",
        ">DDDBDDDD",
        "BDO/ MC/",
        "பயோமெட்ரிக் | | OTP | தகுதி",
    ],
)
def test_ordinary_lines_are_not_headings(line: str) -> None:
    assert not is_heading(line)


def test_wrapped_sentence_fragment_is_not_a_heading() -> None:
    # OCR wraps mid-sentence; the second line starts with a heading keyword but continues
    # the sentence above it.
    page = (
        "Eligibility\n\n"
        "Officers at the district level should maintain\n"
        "contact with the applicants\n"
        "throughout the camp period."
    )

    [chunk] = chunk_document(DOC, [PageText(1, page, "ocr")])

    assert chunk.section == "Eligibility"
    assert chunk.text.startswith("Officers at the district level should maintain contact")
