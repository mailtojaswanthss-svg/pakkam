"""Ingestion pipeline: data/sources.json + data/raw/*.pdf -> data/processed/chunks.jsonl."""

import json
import logging
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import pymupdf
from pydantic import BaseModel, Field, TypeAdapter

from schemebot.config import Settings
from schemebot.ingest.chunk import chunk_document
from schemebot.ingest.extract import OcrFn, extract_pages
from schemebot.ingest.langid import Language, detect_language
from schemebot.ingest.models import Chunk, SourceDoc
from schemebot.ingest.ocr_cache import CACHE_DIR_NAME, cached_ocr

OcrFactory = Callable[[Language], OcrFn]
"""Builds an OCR function for a document's language."""

logger = logging.getLogger(__name__)

MANIFEST_NAME = "sources.json"
CHUNKS_NAME = "chunks.jsonl"
REPORT_NAME = "ingest_report.json"


class DocReport(BaseModel):
    doc_id: str
    pages: int
    pages_by_method: dict[str, int]
    pages_by_language: dict[str, int]
    chunks: int
    chunks_by_language: dict[str, int]


class IngestReport(BaseModel):
    documents: list[DocReport]
    missing_files: list[str]
    unreadable_files: dict[str, str] = Field(description="file name -> error message")
    total_chunks: int

    @property
    def has_errors(self) -> bool:
        return bool(self.missing_files or self.unreadable_files)


def load_manifest(path: Path) -> list[SourceDoc]:
    docs = TypeAdapter(list[SourceDoc]).validate_json(path.read_bytes())
    duplicates = [doc_id for doc_id, n in Counter(d.doc_id for d in docs).items() if n > 1]
    if duplicates:
        raise ValueError(f"duplicate doc_id in {path.name}: {', '.join(duplicates)}")
    return docs


def write_chunks(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(chunk.model_dump_json() + "\n")


def read_chunks(path: Path) -> list[Chunk]:
    with path.open(encoding="utf-8") as file:
        return [Chunk.model_validate_json(line) for line in file if line.strip()]


def run_ingest(settings: Settings, ocr_factory: OcrFactory | None) -> IngestReport:
    docs = load_manifest(settings.data_dir / MANIFEST_NAME)
    all_chunks: list[Chunk] = []
    reports: list[DocReport] = []
    missing: list[str] = []
    unreadable: dict[str, str] = {}

    for doc in docs:
        pdf_path = settings.raw_dir / doc.file
        if not pdf_path.is_file():
            logger.error("missing file for %s: %s", doc.doc_id, pdf_path)
            missing.append(doc.file)
            continue

        ocr = ocr_factory(doc.language) if ocr_factory else None
        if ocr is not None:
            ocr = cached_ocr(ocr, settings.processed_dir / CACHE_DIR_NAME, pdf_path, doc.language)
        try:
            pages = extract_pages(pdf_path, ocr=ocr, force_ocr=doc.force_ocr)
        except pymupdf.FileDataError as error:
            # One corrupt download should not stop the rest of the corpus from being ingested.
            logger.error("cannot read %s: %s", pdf_path.name, error)
            unreadable[doc.file] = str(error)
            continue

        chunks = chunk_document(doc, pages)
        all_chunks.extend(chunks)
        reports.append(
            DocReport(
                doc_id=doc.doc_id,
                pages=len(pages),
                pages_by_method=dict(Counter(page.method for page in pages)),
                pages_by_language=dict(Counter(detect_language(page.text) for page in pages)),
                chunks=len(chunks),
                chunks_by_language=dict(Counter(chunk.language for chunk in chunks)),
            )
        )
        logger.info("%s: %d pages -> %d chunks", doc.doc_id, len(pages), len(chunks))

    write_chunks(all_chunks, settings.processed_dir / CHUNKS_NAME)
    report = IngestReport(
        documents=reports,
        missing_files=missing,
        unreadable_files=unreadable,
        total_chunks=len(all_chunks),
    )
    (settings.processed_dir / REPORT_NAME).write_text(
        json.dumps(report.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return report
