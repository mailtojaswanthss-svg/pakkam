"""Disk cache for OCR results, so re-running ingestion does not re-read the same pages.

OCR is by far the slowest step (about 40 minutes for the Tamil policy notes). A page's OCR
result depends only on the PDF's bytes, the page and the OCR language, so it is cached under
those: data/processed/ocr_cache/<pdf sha256 prefix>-<language>/p<page>.txt. Replacing a PDF
changes its hash, so stale results are never reused. Delete the folder to force a full re-read.
"""

import hashlib
from pathlib import Path

import pymupdf

from schemebot.ingest.extract import OCR_DPI, OCR_LANGUAGES, OcrFn
from schemebot.ingest.langid import Language

CACHE_DIR_NAME = "ocr_cache"
HASH_PREFIX = 16


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def cached_ocr(ocr: OcrFn, cache_root: Path, pdf_path: Path, language: Language) -> OcrFn:
    """Wrap `ocr` so each page is read once per (PDF content, language, DPI)."""
    key = f"{file_sha256(pdf_path)[:HASH_PREFIX]}-{OCR_LANGUAGES[language]}-{OCR_DPI}dpi"
    folder = cache_root / key

    def read(page: pymupdf.Page) -> str:
        path = folder / f"p{page.number + 1}.txt"
        if path.is_file():
            return path.read_text(encoding="utf-8")
        text = ocr(page)
        folder.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return text

    return read
