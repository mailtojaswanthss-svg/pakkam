"""Text normalization shared by indexing and querying.

Queries and passages must go through the same function, otherwise "௨.௫ லட்சம்" in a
document and "2.5 லட்சம்" in a question would never match.
"""

import unicodedata

from schemebot.ingest.extract import normalize_text

TAMIL_DIGIT_ZERO = 0x0BE6
DEVANAGARI_DIGIT_ZERO = 0x0966

_INDIC_DIGITS = str.maketrans(
    {chr(zero + offset): str(offset) for zero in (TAMIL_DIGIT_ZERO, DEVANAGARI_DIGIT_ZERO)
     for offset in range(10)}
)  # fmt: skip


def normalize_for_search(text: str) -> str:
    """NFC, invisible characters removed, whitespace tidied, Indic digits as 0-9."""
    text = normalize_text(text).translate(_INDIC_DIGITS)
    return unicodedata.normalize("NFC", text)
