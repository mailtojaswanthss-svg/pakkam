"""Text normalization shared by indexing and querying.

Queries and passages must go through the same function, otherwise "௨.௫ லட்சம்" in a
document and "2.5 லட்சம்" in a question would never match.
"""

import re
import unicodedata

NO_BREAK_SPACE = 0x00A0
ZERO_WIDTH_CHARS = (0x200B, 0x200C, 0x200D)  # space, non-joiner, joiner
_ZERO_WIDTH = re.compile("[" + "".join(map(chr, ZERO_WIDTH_CHARS)) + "]")


def normalize_text(text: str) -> str:
    """NFC-normalise and tidy whitespace without changing the words."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace(chr(NO_BREAK_SPACE), " ")
    # Zero-width space / non-joiner / joiner: OCR inserts them after Tamil virama, and they
    # silently break keyword matching while changing nothing a reader can see.
    text = _ZERO_WIDTH.sub("", text)
    # Re-join English words hyphenated across a line break.
    text = re.sub(r"([a-z])-\n([a-z])", r"\1\2", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


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


CONVERSATIONAL_FILLERS = (
    r"\bcan you please tell me\b",
    r"\bcan you tell me\b",
    r"\bplease tell me\b",
    r"\btell me about\b",
    r"\btell me\b",
    r"\bdetails sollu\b",
    r"\bdetails sollunga\b",
    r"\bpaththi sollu\b",
    r"\bpaththi sollunga\b",
    r"\bpatthi sollu\b",
    r"\bpatthi sollunga\b",
    r"\benna scheme\b",
    r"\benna thittam\b",
    r"\bke baare mein batao\b",
    r"\bke bare me batao\b",
    r"\bkya hai\b",
    r"\bdetails please\b",
    r"\bhelp pannunga\b",
)

TANGLISH_REPLACEMENTS = [
    (r"\bponnungaluku\b", "பெண்கள்"),
    (r"\bponnungalukku\b", "பெண்கள்"),
    (r"\bponnukku\b", "பெண்கள்"),
    (r"\bmaruthuvam\b", "மருத்துவம்"),
    (r"\bkaapeedu\b", "காப்பீடு"),
    (r"\bkappidu\b", "காப்பீடு"),
    (r"\bthittam\b", "திட்டம்"),
    (r"\bthittathuku\b", "திட்டம்"),
    (r"\bthittathukku\b", "திட்டம்"),
    (r"\burimai\b", "உரிமை"),
    (r"\bpanam\b", "பணம்"),
    (r"\bkedaikuma\b", "கிடைக்குமா"),
    (r"\bkedaikkuma\b", "கிடைக்குமா"),
    (r"\byojna\b", "yojana"),
]


def strip_fillers(query: str) -> str:
    """Remove conversational prefixes and suffixes to isolate the semantic core."""
    cleaned = query.strip()
    for filler in CONVERSATIONAL_FILLERS:
        cleaned = re.sub(filler, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else query.strip()


def normalize_tanglish(query: str) -> str:
    """Normalize common Tanglish and speech-slips into canonical search terms."""
    normalized = query
    for pattern, replacement in TANGLISH_REPLACEMENTS:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", normalized).strip()


def clean_query(query: str) -> str:
    """Comprehensive query cleanup: normalization, filler removal, and Tanglish normalization."""
    base = normalize_for_search(query)
    without_fillers = strip_fillers(base)
    tanglish_normalized = normalize_tanglish(without_fillers)
    return tanglish_normalized
