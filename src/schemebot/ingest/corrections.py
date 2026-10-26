"""Known OCR misreadings, and fixes a person has checked against the printed PDF page.

OCR sometimes misreads digits in Tamil and Hindi pages (Rs.1,000 read as 4,000). The number
guardrail cannot catch that, because the wrong number really is in the passage. Each entry
in data/corrections.json names one misreading:

- Unconfirmed (no `confirmed_by`): the text is left alone, but answers may not use the wrong
  number from that document (generate/answer.py removes such sentences).
- Confirmed (a person compared it with the PDF page and wrote their name): ingestion replaces
  the misreading with what the page shows, and marks those chunks "ocr-corrected" so the UI
  can say the text was corrected by hand.

Applying is strict: the misreading must appear exactly once on its page, otherwise ingestion
stops. A re-run of OCR or a new PDF version therefore cannot silently skip a fix.
"""

import unicodedata
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from schemebot.ingest.extract import ExtractionMethod, PageText
from schemebot.ingest.models import DOC_ID_PATTERN

CORRECTIONS_NAME = "corrections.json"
CORRECTED: Final[ExtractionMethod] = "ocr-corrected"


class CorrectionError(ValueError):
    """A confirmed correction could not be applied exactly as written."""


class OcrCorrection(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    doc_id: str = Field(pattern=DOC_ID_PATTERN)
    page: int | None = Field(default=None, ge=1, description="PDF page, as in a PDF viewer")
    ocr_reads: str = Field(min_length=1, description="The wrong text, exactly as extracted")
    pdf_shows: str = Field(min_length=1, description="What the printed page shows")
    confirmed_by: str | None = Field(
        default=None, description="The person who checked the printed page; empty = unconfirmed"
    )
    confirmed_on: date | None = None
    note: str = ""

    @model_validator(mode="after")
    def _confirmed_needs_page_and_date(self) -> "OcrCorrection":
        if self.confirmed_by is not None:
            if not self.confirmed_by.strip():
                raise ValueError(f"{self.doc_id}: confirmed_by is blank; use null instead")
            if self.page is None or self.confirmed_on is None:
                raise ValueError(f"{self.doc_id}: a confirmed correction needs page and date")
        return self

    @property
    def confirmed(self) -> bool:
        return self.confirmed_by is not None


def load_corrections(path: Path) -> list[OcrCorrection]:
    """A missing file means no known misreadings, not an error."""
    if not path.is_file():
        return []
    return TypeAdapter(list[OcrCorrection]).validate_json(path.read_bytes())


def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def apply_corrections(
    doc_id: str, pages: list[PageText], corrections: list[OcrCorrection]
) -> tuple[list[PageText], list[OcrCorrection]]:
    """Pages with the confirmed fixes for `doc_id` applied, and the fixes that were applied."""
    mine = [c for c in corrections if c.confirmed and c.doc_id == doc_id]
    by_number = {page.page: page for page in pages}
    for correction in mine:
        page = by_number.get(correction.page or 0)
        if page is None:
            raise CorrectionError(f"{doc_id}: page {correction.page} does not exist")
        wrong = _nfc(correction.ocr_reads)
        found = page.text.count(wrong)
        if found != 1:
            raise CorrectionError(
                f"{doc_id} p{page.page}: {correction.ocr_reads!r} found {found} times, "
                "expected exactly once; check the entry in corrections.json"
            )
        by_number[page.page] = replace(
            page, text=page.text.replace(wrong, _nfc(correction.pdf_shows)), method=CORRECTED
        )
    return [by_number[page.page] for page in pages], mine
