"""The official PDF page as an image, the cited lines marked in yellow: proof to show.

An answer's citation names a document and page. This renders that page from the PDF in
data/raw/ (the same file the answer was read from), marks the cited passage in yellow and
returns a PNG. On a phone, "show the officer" puts the government's own page on screen, not a
paragraph a model wrote.

Pages with a real text layer are searched directly. Scanned or legacy-font pages (most Tamil
Government Orders) have no usable text layer, so the page image is read with Tesseract, the
cited excerpt is located among the recognised words, and those words are painted yellow. When
Tesseract is missing or the passage cannot be found with confidence, the page comes back
unmarked: the page itself is still the proof, and a wrong mark would be worse than none.
"""

import difflib
import io
import logging
import os
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

logger = logging.getLogger(__name__)

RENDER_DPI = 110
OCR_DPI = 220
MAX_MARK_CHARS = 600
MAX_HIGHLIGHTS = 12
_MIN_PIECE = 12
YELLOW = (1.0, 0.92, 0.0)
YELLOW_RGBA = (255, 230, 0, 110)
MIN_MATCHED_WORDS = 4
MIN_MATCHED_SHARE = 0.4
OCR_LANGUAGES = {"ta": "tam+eng", "hi": "hin+eng", "en": "eng", "ta-Latn": "eng"}

_DIGITS = str.maketrans("௦௧௨௩௪௫௬௭௮௯०१२३४५६७८९", "01234567890123456789")
_PUNCT = re.compile(r"[^\w\u0B80-\u0BFF\u0900-\u097F]+")


class PageUnavailable(Exception):
    """The PDF or the renderer is missing, or the page is out of range."""


@dataclass(frozen=True)
class Word:
    """One word recognised on the page, with its box in image pixels."""

    text: str
    left: int
    top: int
    width: int
    height: int
    line: tuple[int, int, int]  # (block, paragraph, line) from Tesseract


def _pieces(mark: str) -> list[str]:
    """Search terms from the cited excerpt: its lines and clauses long enough to be unique."""
    text = re.sub(r"\s+", " ", mark[:MAX_MARK_CHARS]).strip()
    parts = re.split(r"(?<=[.;:!?])\s+|\s{2,}|\n", text)
    pieces: list[str] = []
    for part in parts:
        part = part.strip(" ,")
        if len(part) < _MIN_PIECE:
            continue
        # Long clauses rarely match across line breaks; search their first words instead.
        pieces.append(part if len(part) <= 60 else part[:60].rsplit(" ", 1)[0])
    return pieces


def _normalise(token: str) -> str:
    """A word as compared: NFC, lower case, Indic digits as ASCII, no punctuation or joiners.

    A word with digits is compared by its digits alone, so "ரூ.2.5" and an OCR'd "e.2.5" agree.
    """
    token = unicodedata.normalize("NFC", token).lower().translate(_DIGITS)
    token = _PUNCT.sub("", token.replace("\u200c", "").replace("\u200d", ""))
    digits = "".join(ch for ch in token if ch.isascii() and ch.isdigit())
    return digits or token


def _tokens(text: str) -> list[str]:
    return [t for t in (_normalise(w) for w in text.split()) if t]


def _match_span(words: list[str], excerpt: str) -> list[int]:
    """Indices of the recognised words that belong to the cited excerpt, or [] if unsure.

    Most of the excerpt's words reappear on the page in order (the excerpt was read from it,
    sometimes lightly reworded). The matching blocks of a sequence alignment are grouped into
    runs (gaps of a few words allowed for OCR errors); the run holding the excerpt's numbers
    wins, since the number is what the citizen needs to see. A weak match returns nothing.
    """
    needle = _tokens(excerpt[:MAX_MARK_CHARS])
    hay = [_normalise(w) for w in words]
    if len(needle) < 2 or not any(hay):
        return []
    numbers = {t for t in needle if t.isdigit()}
    matcher = difflib.SequenceMatcher(None, hay, needle, autojunk=False)
    runs: list[list[int]] = []
    last_end = -(10**9)
    for block in (b for b in matcher.get_matching_blocks() if b.size):
        indices = [i for i in range(block.a, block.a + block.size) if hay[i]]
        if not runs or block.a - last_end > 6:
            runs.append([])
        runs[-1] += indices
        last_end = block.a + block.size
    if not runs:
        return []

    def score(run: list[int]) -> tuple[int, int]:
        return (sum(hay[i] in numbers for i in run), len(run))

    best = max(runs, key=score)
    has_number = score(best)[0] > 0
    enough = len(best) >= 3 if has_number else len(best) >= min(MIN_MATCHED_WORDS, len(needle))
    if not enough or (not has_number and len(best) < MIN_MATCHED_SHARE * len(needle)):
        return []
    first, last = best[0], best[-1]
    return [i for i in range(first, last + 1) if hay[i]]


def _line_boxes(words: list[Word], indices: list[int]) -> list[tuple[int, int, int, int]]:
    """One rectangle (x0, y0, x1, y1) per OCR line covering the chosen words."""
    lines: dict[tuple[int, int, int], list[Word]] = {}
    for i in indices:
        lines.setdefault(words[i].line, []).append(words[i])
    boxes = []
    for line_words in lines.values():
        x0 = min(w.left for w in line_words)
        y0 = min(w.top for w in line_words)
        x1 = max(w.left + w.width for w in line_words)
        y1 = max(w.top + w.height for w in line_words)
        pad = max(2, (y1 - y0) // 6)
        boxes.append((x0 - pad, y0 - pad, x1 + pad, y1 + pad))
    return boxes


def _ocr_words(
    image: Any, language: str, tesseract_cmd: str | None, tessdata_dir: Path | None
) -> list[Word]:
    """Words and boxes from Tesseract; [] when Tesseract is not available."""
    try:
        import pytesseract
    except ImportError:
        return []
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    if tessdata_dir:
        os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)
    try:
        data = pytesseract.image_to_data(
            image,
            lang=OCR_LANGUAGES.get(language, "tam+hin+eng"),
            output_type=pytesseract.Output.DICT,
        )
    except (pytesseract.TesseractNotFoundError, pytesseract.TesseractError, OSError) as error:
        logger.warning("highlight OCR unavailable: %s", error)
        return []
    words = []
    for i, text in enumerate(data["text"]):
        if str(text).strip():
            words.append(
                Word(
                    str(text),
                    int(data["left"][i]),
                    int(data["top"][i]),
                    int(data["width"][i]),
                    int(data["height"][i]),
                    (int(data["block_num"][i]), int(data["par_num"][i]), int(data["line_num"][i])),
                )
            )
    return words


def _highlight_scanned(
    pdf_page: Any, mark: str, language: str, tesseract_cmd: str | None, tessdata_dir: Path | None
) -> bytes | None:
    """The page as PNG with the excerpt painted yellow from OCR word boxes, or None if not found."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    pixmap = pdf_page.get_pixmap(dpi=OCR_DPI)
    image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    words = _ocr_words(image, language, tesseract_cmd, tessdata_dir)
    indices = _match_span([w.text for w in words], mark)
    if not indices:
        return None
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for box in _line_boxes(words, indices):
        draw.rectangle(box, fill=YELLOW_RGBA)
    marked = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    scale = RENDER_DPI / OCR_DPI
    marked = marked.resize(
        (max(1, round(marked.width * scale)), max(1, round(marked.height * scale)))
    )
    out = io.BytesIO()
    marked.save(out, format="PNG", optimize=True)
    logger.info("highlighted %d words on a scanned page", len(indices))
    return out.getvalue()


@lru_cache(maxsize=48)
def render_page(
    pdf_path: Path,
    page: int,
    mark: str = "",
    language: str = "unknown",
    tesseract_cmd: str | None = None,
    tessdata_dir: Path | None = None,
) -> bytes:
    """PNG bytes of a 1-based page, with the cited passage highlighted in yellow where found."""
    try:
        import pymupdf
    except ImportError as error:  # the API image without the ingest extra
        raise PageUnavailable("PDF rendering needs pymupdf (uv sync --extra ingest)") from error
    if not pdf_path.is_file():
        raise PageUnavailable(f"{pdf_path.name} is not in data/raw/")
    # cast: pymupdf ships no types, and CI may type-check without it installed.
    with cast(Any, pymupdf).open(pdf_path) as doc:
        if not 1 <= page <= doc.page_count:
            raise PageUnavailable(f"page {page} is outside 1-{doc.page_count}")
        pdf_page = doc[page - 1]
        found = 0
        for piece in _pieces(mark):
            for rect in pdf_page.search_for(piece)[:2]:
                annot = pdf_page.add_highlight_annot(rect)
                annot.set_colors(stroke=YELLOW)
                annot.update()
                found += 1
            if found >= MAX_HIGHLIGHTS:
                break
        if not found and mark.strip():
            scanned = _highlight_scanned(pdf_page, mark, language, tesseract_cmd, tessdata_dir)
            if scanned is not None:
                return scanned
        image: bytes = pdf_page.get_pixmap(dpi=RENDER_DPI, annots=True).tobytes("png")
    logger.info("rendered %s p%d (%d highlights)", pdf_path.name, page, found)
    return image
