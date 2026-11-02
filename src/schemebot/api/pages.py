"""The official PDF page as an image, with the cited lines marked: proof a citizen can show.

An answer's citation names a document and page. This renders that page from the PDF in
data/raw/ (the same file the answer was read from), highlights the passage where the text
layer allows it, and returns a PNG. On a phone, "show the officer" puts the government's own
page on screen, not a paragraph a model wrote. Scanned Tamil pages have no usable text layer,
so they come back unmarked; the page itself is still the proof.
"""

import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

logger = logging.getLogger(__name__)

RENDER_DPI = 110
MAX_MARK_CHARS = 600
MAX_HIGHLIGHTS = 12
_MIN_PIECE = 12


class PageUnavailable(Exception):
    """The PDF or the renderer is missing, or the page is out of range."""


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


@lru_cache(maxsize=48)
def render_page(pdf_path: Path, page: int, mark: str = "") -> bytes:
    """PNG bytes of a 1-based page, with the cited passage highlighted where found."""
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
                annot.set_colors(stroke=(1.0, 0.86, 0.2))
                annot.update()
                found += 1
            if found >= MAX_HIGHLIGHTS:
                break
        image: bytes = pdf_page.get_pixmap(dpi=RENDER_DPI, annots=True).tobytes("png")
    logger.info("rendered %s p%d (%d highlights)", pdf_path.name, page, found)
    return image
