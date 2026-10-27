import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pymupdf
from schemebot.config import get_settings
from schemebot.ingest.extract import needs_ocr, uses_legacy_font


def main():
    settings = get_settings()
    manifest_path = settings.data_dir / "sources.json"
    sources = json.loads(manifest_path.read_text(encoding="utf-8"))

    results = []
    total_ocr = 0
    total_all = 0

    for s in sources:
        pdf_path = settings.raw_dir / s["file"]
        if not pdf_path.exists():
            continue
        doc_id = s["doc_id"]
        ocr_count = 0
        total_pages = 0
        with pymupdf.open(pdf_path) as pdf:
            total_pages = len(pdf)
            for i, page in enumerate(pdf, start=1):
                text = page.get_text("text")
                if needs_ocr(text) or uses_legacy_font(page):
                    ocr_count += 1
        total_ocr += ocr_count
        total_all += total_pages
        results.append({
            "doc_id": doc_id,
            "file": s["file"],
            "language": s["language"],
            "ocr_pages": ocr_count,
            "total_pages": total_pages,
            "pct": f"{ocr_count / total_pages * 100:.1f}%" if total_pages else "0%",
        })

    print(f"{'Document ID':<32} {'Lang':<6} {'OCR Pages':<10} {'Total':<8} {'OCR %'}")
    print("-" * 65)
    for r in results:
        print(f"{r['doc_id']:<32} {r['language']:<6} {r['ocr_pages']:<10} {r['total_pages']:<8} {r['pct']}")
    print("-" * 65)
    print(f"{'TOTAL':<32} {'':<6} {total_ocr:<10} {total_all:<8} {total_ocr / total_all * 100:.1f}%")


if __name__ == "__main__":
    main()
