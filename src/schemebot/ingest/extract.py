"""Page-level text extraction from PDFs, with an OCR fallback for pages that extract badly.

Many Tamil government PDFs are either scanned images or typeset in legacy (pre-Unicode)
Tamil fonts. Both extract as empty or garbage text, so every page goes through a quality
check and bad pages are sent to Tesseract instead.
"""

import logging
import os
import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pymupdf

from schemebot.ingest.langid import Language

logger = logging.getLogger(__name__)

ExtractionMethod = Literal["text", "ocr", "text-unverified"]
"""text-unverified: the page needed OCR but OCR was unavailable; the text may be garbage."""

MIN_PAGE_CHARS = 40
"""A page with fewer real characters than this is treated as a scanned image."""

MAX_ODD_TOKEN_SHARE = 0.25
"""Legacy-font Tamil extracts as Latin tokens full of symbols, e.g. 'jkpo;ehL'."""

MAX_BAD_CHAR_SHARE = 0.01
"""Replacement characters or private-use code points point to a broken font mapping."""

MAX_ORPHAN_MARK_SHARE = 0.03
"""Share of words allowed to start with a vowel sign (e.g. 'ि', 'ா'). Unicode never does
this, but broken Devanagari/Tamil font maps do: 'कृषि' extracts as 'िृषि'."""

DEVANAGARI_I_SIGN = 0x093F
I_SIGN_SHARE_RANGE = (0.02, 0.09)
"""Normal Hindi has the vowel sign 'ि' at ~4-5% of Devanagari characters. Broken font maps
push it out of range in either direction: 1.0% when the sign became a consonant
('प्रतिमाह' -> 'प्रततमाह'), 12.5% when a consonant became the sign ('कृषि' -> 'िृषि')."""

MIN_DEVANAGARI_FOR_SIGN_CHECK = 200
"""Below this many Devanagari characters the share is too noisy to judge."""

MIN_LETTER_SHARE = 0.5
"""Prose is ~90% letters. When a font's glyphs have no Unicode mapping they vanish from the
text layer, leaving pages of punctuation and numbers such as 'ii) . iii) .2.5 .'."""

TABLE_ALNUM_SHARE = 0.8
"""A page under MIN_LETTER_SHARE is still kept as text when letters plus digits make up at
least this share: that is a table, not residue. Measured on the corpus: broken-font residue
pages 0.45-0.74, real table pages 0.84-1.00. Tesseract cannot read tables, so sending them
to OCR lost their content."""

MIN_OCR_YIELD = 0.25
"""If OCR returns less than this share of the text layer's letters and digits (on a page
not set in a known legacy font), the OCR failed and the text layer is kept."""

# Pre-Unicode Tamil and Hindi font families. Text set in them is unreadable without OCR.
# Compared case-insensitively against the font name with its subset tag ("ABCDEE+") removed.
LEGACY_FONT_PREFIXES = (
    "tau-", "tam-", "tab-", "tscu", "tsc_", "bamini", "vanavil", "suntommy", "elango",
    "kruti", "devlys", "chanakya", "walkman-chanakya",
)  # fmt: skip

OCR_DPI = 300

# Tesseract models per document language. Loading Tamil and Hindi together makes Tesseract
# read Devanagari words as Tamil, so each document only gets its own script plus English.
OCR_LANGUAGES: dict[Language, str] = {
    "ta": "tam+eng",
    "hi": "hin+eng",
    "en": "eng",
    "ta-Latn": "eng",
    "unknown": "tam+hin+eng",
}

NO_BREAK_SPACE = 0x00A0
REPLACEMENT_CHAR = 0xFFFD
ZERO_WIDTH_CHARS = (0x200B, 0x200C, 0x200D)  # space, non-joiner, joiner
_ZERO_WIDTH = re.compile("[" + "".join(map(chr, ZERO_WIDTH_CHARS)) + "]")
PRIVATE_USE_RANGE = (0xE000, 0xF8FF)
BULLET = chr(0x2022)
_PRIVATE_USE = re.compile(f"[{chr(PRIVATE_USE_RANGE[0])}-{chr(PRIVATE_USE_RANGE[1])}]")
_ODD_INNER_CHARS = re.compile(r"[;\[\]{}\\`~^|<>=+]")
_LOWER_THEN_UPPER = re.compile(r"[a-z][A-Z]")


class OcrUnavailableError(RuntimeError):
    """Raised when Tesseract (or one of its language packs) is not installed."""


OcrFn = Callable[[pymupdf.Page], str]


@dataclass(frozen=True)
class PageText:
    page: int
    """1-based page number, as shown in a PDF viewer and used in citations."""
    text: str
    method: ExtractionMethod


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


def _is_bad_char(char: str) -> bool:
    return ord(char) == REPLACEMENT_CHAR or 0xE000 <= ord(char) <= 0xF8FF


def _has_abnormal_i_sign_share(visible: list[str]) -> bool:
    devanagari = [char for char in visible if 0x0900 <= ord(char) <= 0x097F]
    if len(devanagari) < MIN_DEVANAGARI_FOR_SIGN_CHECK:
        return False
    share = sum(ord(char) == DEVANAGARI_I_SIGN for char in devanagari) / len(devanagari)
    low, high = I_SIGN_SHARE_RANGE
    return not low <= share <= high


def replace_symbol_bullets(text: str) -> str:
    """Turn private-use characters into a plain bullet.

    Bullets set in Symbol or Wingdings fonts extract as private-use code points that no
    font can draw, so they would show up as empty boxes in the source slip. Applied only
    after a page passes `needs_ocr`, which counts these characters to detect broken fonts.
    """
    return _PRIVATE_USE.sub(BULLET, text)


def _starts_with_mark(token: str) -> bool:
    """True for a word starting with a combining vowel sign or virama (Unicode Mn/Mc)."""
    return unicodedata.category(token[0]) in ("Mn", "Mc")


def _is_odd_token(token: str) -> bool:
    inner = token[1:-1]
    return bool(_ODD_INNER_CHARS.search(inner) or _LOWER_THEN_UPPER.search(token))


def needs_ocr(text: str) -> bool:
    """True if the text layer looks empty, scanned or produced by a legacy font."""
    visible = [char for char in text if not char.isspace()]
    if len(visible) < MIN_PAGE_CHARS:
        return True

    if sum(_is_bad_char(char) for char in visible) / len(visible) > MAX_BAD_CHAR_SHARE:
        return True

    letter_share = sum(char.isalpha() for char in visible) / len(visible)
    alnum_share = sum(char.isalnum() for char in visible) / len(visible)
    if letter_share < MIN_LETTER_SHARE and alnum_share < TABLE_ALNUM_SHARE:
        return True

    if _has_abnormal_i_sign_share(visible):
        return True

    tokens = [token for token in text.split() if any(char.isalpha() for char in token)]
    if not tokens:
        return True
    orphan_share = sum(_starts_with_mark(token) for token in tokens) / len(tokens)
    if orphan_share > MAX_ORPHAN_MARK_SHARE:
        return True
    odd_share = sum(_is_odd_token(token) for token in tokens) / len(tokens)
    return odd_share > MAX_ODD_TOKEN_SHARE


def is_legacy_font(font_name: str) -> bool:
    base = font_name.split("+", 1)[-1].lower()
    return base.startswith(LEGACY_FONT_PREFIXES)


def uses_legacy_font(page: pymupdf.Page) -> bool:
    # get_fonts() rows are (xref, ext, type, basefont, name, encoding, ...).
    return any(is_legacy_font(font[3]) for font in page.get_fonts())


def make_tesseract_ocr(
    language: Language,
    tesseract_cmd: str | None = None,
    tessdata_dir: Path | None = None,
) -> OcrFn:
    """Build a Tesseract OCR function for documents in `language`."""
    import pytesseract
    from PIL import Image

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    if tessdata_dir:
        # Passed via the environment: pytesseract's `config` string mangles quoted Windows paths.
        os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)

    def ocr_page(page: pymupdf.Page) -> str:
        pixmap = page.get_pixmap(dpi=OCR_DPI)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        try:
            return str(pytesseract.image_to_string(image, lang=OCR_LANGUAGES[language]))
        except (pytesseract.TesseractNotFoundError, pytesseract.TesseractError) as error:
            raise OcrUnavailableError(str(error)) from error

    return ocr_page


def extract_pages(
    pdf_path: Path, ocr: OcrFn | None = None, force_ocr: bool = False
) -> list[PageText]:
    """Extract normalised text for every page, falling back to OCR where needed.

    `force_ocr` is for documents known to use a legacy font that slips past the heuristic.
    """
    pages: list[PageText] = []
    with pymupdf.open(pdf_path) as document:
        for index, page in enumerate(document):
            page_number = index + 1
            text = normalize_text(page.get_text("text"))
            legacy_font = uses_legacy_font(page)
            if not (force_ocr or legacy_font or needs_ocr(text)):
                pages.append(PageText(page_number, replace_symbol_bullets(text), "text"))
                continue

            if ocr is None:
                logger.warning("%s p%d needs OCR but none configured", pdf_path.name, page_number)
                pages.append(PageText(page_number, text, "text-unverified"))
                continue

            try:
                ocr_text = normalize_text(ocr(page))
            except OcrUnavailableError as error:
                logger.warning("%s p%d OCR failed: %s", pdf_path.name, page_number, error)
                pages.append(PageText(page_number, text, "text-unverified"))
                continue
            if not (force_ocr or legacy_font) and _content(ocr_text) < MIN_OCR_YIELD * _content(
                text
            ):
                # OCR read far less than the text layer holds (tables are the usual case):
                # never let a failed OCR wipe out good text.
                logger.info(
                    "%s p%d: OCR yielded little, keeping text layer", pdf_path.name, page_number
                )
                pages.append(PageText(page_number, replace_symbol_bullets(text), "text"))
                continue
            pages.append(PageText(page_number, ocr_text, "ocr"))
    return pages


def _content(text: str) -> int:
    return sum(char.isalnum() for char in text)
