"""Run ingestion: `uv run python -m schemebot.ingest [--no-ocr]`."""

import argparse
import logging
import sys
from functools import partial

from schemebot.config import get_settings
from schemebot.ingest.extract import make_tesseract_ocr
from schemebot.ingest.pipeline import MANIFEST_NAME, run_ingest


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract and chunk the scheme documents.")
    parser.add_argument("--no-ocr", action="store_true", help="skip OCR (pages get flagged)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    settings = get_settings()
    manifest = settings.data_dir / MANIFEST_NAME
    if not manifest.is_file():
        print(f"No manifest at {manifest}. See docs/data_sources.md.", file=sys.stderr)
        return 1

    ocr_factory = None
    if not args.no_ocr:
        ocr_factory = partial(
            make_tesseract_ocr,
            tesseract_cmd=settings.tesseract_cmd,
            tessdata_dir=settings.tessdata_dir,
        )
    report = run_ingest(settings, ocr_factory)
    if not report.documents and not report.has_errors:
        print(f"{manifest} lists no documents. See docs/data_sources.md.", file=sys.stderr)
        return 1

    for doc in report.documents:
        print(
            f"{doc.doc_id:<32} pages={doc.pages:<4} {doc.pages_by_method} "
            f"chunks={doc.chunks:<4} {doc.chunks_by_language}"
        )
    print(f"total chunks: {report.total_chunks}")
    for fix in report.corrections_applied:
        print(f"corrected by hand: {fix}")
    unverified = sum(d.pages_by_method.get("text-unverified", 0) for d in report.documents)
    if unverified:
        print(f"WARNING: {unverified} pages needed OCR but did not get it", file=sys.stderr)
    if report.missing_files:
        print(f"ERROR: missing files: {', '.join(report.missing_files)}", file=sys.stderr)
    for file, error in report.unreadable_files.items():
        print(f"ERROR: cannot read {file}: {error}", file=sys.stderr)
    return 1 if report.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
