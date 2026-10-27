"""Show for each entry in data/corrections.json the old text vs new text and flag mismatches.

Strictly read-only: does NOT modify data/corrections.json.

Usage:
    python scripts/check_corrections.py
"""

import hashlib
import json
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from schemebot.config import get_settings
from schemebot.ingest.extract import OCR_DPI, OCR_LANGUAGES


def get_tesseract_text(cache_root: Path, pdf_path: Path, language: str, page_num: int) -> str:
    digest = hashlib.sha256()
    with pdf_path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    pdf_hash = digest.hexdigest()[:16]

    lang_code = OCR_LANGUAGES.get(language, "tam+eng")
    folder_name = f"{pdf_hash}-{lang_code}-{OCR_DPI}dpi"
    cache_file = cache_root / folder_name / f"p{page_num}.txt"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")
    return ""


def main():
    settings = get_settings()
    corrections_file = settings.data_dir / "corrections.json"
    manifest_file = settings.data_dir / "sources.json"

    if not corrections_file.exists():
        print(f"Error: {corrections_file} not found", file=sys.stderr)
        return 1

    corrections = json.loads(corrections_file.read_text(encoding="utf-8"))
    sources = {s["doc_id"]: s for s in json.loads(manifest_file.read_text(encoding="utf-8"))}

    cache_root = settings.processed_dir / "ocr_cache"
    chitra_dir = settings.processed_dir / "chitrapathak_text"

    print(f"\nEvaluating {len(corrections)} entries in {corrections_file.name} against Old (Tesseract) vs New (Chitrapathak-2):\n")
    print("=" * 100)

    for idx, c in enumerate(corrections, 1):
        doc_id = c["doc_id"]
        page = c["page"]
        ocr_reads = c["ocr_reads"]
        pdf_shows = c["pdf_shows"]
        note = c.get("note", "")

        source = sources.get(doc_id, {})
        lang = source.get("language", "ta")
        pdf_path = settings.raw_dir / source.get("file", f"{doc_id}.pdf")

        old_text = get_tesseract_text(cache_root, pdf_path, lang, page)
        new_file = chitra_dir / f"{doc_id}_p{page}.txt"
        new_text = new_file.read_text(encoding="utf-8") if new_file.exists() else ""

        old_has_wrong = ocr_reads in old_text
        old_has_right = pdf_shows in old_text
        new_has_wrong = ocr_reads in new_text
        new_has_right = pdf_shows in new_text or (pdf_shows.replace(',', '') in new_text.replace(',', ''))

        print(f"[{idx}] {doc_id} (Page {page})")
        print(f"    Expected Fix:   '{ocr_reads}' (old misreading) -> '{pdf_shows}' (true PDF text)")
        print(f"    Old (Tesseract): Contains Wrong: {old_has_wrong:<5} | Contains Right: {old_has_right}")
        print(f"    New (Chitra-2):  Contains Wrong: {new_has_wrong:<5} | Contains Right: {new_has_right}")

        if new_has_right and not new_has_wrong:
            print("    -> STATUS: [RESOLVED] Chitrapathak-2 matches true PDF text; manual correction unneeded.")
        elif new_has_right and new_has_wrong:
            print("    -> STATUS: [PARTIAL] Both tokens found in Chitrapathak-2 text.")
        elif not new_has_right and not new_has_wrong:
            print("    -> STATUS: [INSPECT] Neither token matched verbatim; check surrounding formatting.")
        else:
            print("    -> STATUS: [UNRESOLVED] Still matches old misreading.")
        print(f"    Note: {note}")
        print("-" * 100)


if __name__ == "__main__":
    main()
