"""Compare Tesseract and Chitrapathak-2 OCR results side-by-side.

For each gated page:
1. Loads Tesseract text (from data/processed/ocr_cache or runs Tesseract).
2. Loads Chitrapathak-2 text (from data/processed/chitrapathak_text or runs inference).
3. Extracts all numbers/quantities deterministically from both texts.
4. If known_number is provided in the CSV, checks whether each engine found it.
5. Identifies numbers found in one engine but missing from the other.
6. Outputs a comparison CSV (docs/review/ocr_compare_results.csv) and prints a summary table.
No model-judged scoring.

Usage:
    python scripts/ocr_compare.py [--csv docs/review/ocr_gate_pages.csv]
"""

import argparse
import csv
import hashlib
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from schemebot.config import get_settings
from schemebot.ingest.extract import OCR_DPI, OCR_LANGUAGES
import json

# Regex to capture purely digits and numeric expressions (handling Indian grouping)
NUM_PATTERN = re.compile(r"\b[\d\u0BE6-\u0BEF]+(?:[,\.][\d\u0BE6-\u0BEF]+)*\b")
TAMIL_DIGITS = {"௦": "0", "௧": "1", "௨": "2", "௩": "3", "௪": "4", "௫": "5", "௬": "6", "௭": "7", "௮": "8", "௯": "9"}


def normalize_number(raw: str) -> str:
    cleaned = raw.strip()
    for t_digit, a_digit in TAMIL_DIGITS.items():
        cleaned = cleaned.replace(t_digit, a_digit)
    cleaned = cleaned.replace(",", "").replace("/-", "").strip()
    return cleaned


def extract_numbers(text: str) -> set[str]:
    found = set()
    for match in NUM_PATTERN.finditer(text):
        raw = match.group(0).strip()
        norm = normalize_number(raw)
        if norm and any(c.isdigit() for c in norm):
            found.add(norm)
    return found


def get_tesseract_cached_text(cache_root: Path, pdf_path: Path, language: str, page_num: int) -> str:
    # Compute hash key matching schemebot.ingest.ocr_cache
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
    parser = argparse.ArgumentParser(description="Side-by-side comparison of Tesseract vs Chitrapathak-2")
    parser.add_argument("--csv", default="docs/review/ocr_gate_pages.csv", help="Input gate CSV")
    parser.add_argument("--out-csv", default="docs/review/ocr_compare_results.csv", help="Output comparison CSV")
    parser.add_argument("--chitra-dir", default="data/processed/chitrapathak_text", help="Directory of Chitrapathak texts")
    args = parser.parse_args()

    settings = get_settings()
    manifest_path = settings.data_dir / "sources.json"
    sources = {s["doc_id"]: s for s in json.loads(manifest_path.read_text(encoding="utf-8"))}

    gate_csv = Path(args.csv)
    if not gate_csv.exists():
        print(f"Error: {gate_csv} not found", file=sys.stderr)
        sys.exit(1)

    with gate_csv.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    cache_root = settings.processed_dir / "ocr_cache"
    chitra_dir = Path(args.chitra_dir)

    results = []
    print(f"\nComparing {len(rows)} pages across engines...\n")

    for row in rows:
        doc_id = row["document"].strip()
        page_num = int(row["page"].strip())
        known_num = row.get("known_number", "").strip()
        notes = row.get("notes", "").strip()

        source_info = sources.get(doc_id, {})
        lang = source_info.get("language", "ta")
        pdf_file = source_info.get("file", f"{doc_id}.pdf")
        pdf_path = settings.raw_dir / pdf_file

        # 1. Tesseract text
        tess_text = ""
        if pdf_path.exists():
            tess_text = get_tesseract_cached_text(cache_root, pdf_path, lang, page_num)

        # 2. Chitrapathak text
        chitra_file = chitra_dir / f"{doc_id}_p{page_num}.txt"
        chitra_text = chitra_file.read_text(encoding="utf-8") if chitra_file.exists() else ""

        # Number extraction
        tess_nums = extract_numbers(tess_text)
        chitra_nums = extract_numbers(chitra_text)

        both_nums = tess_nums.intersection(chitra_nums)
        tess_only = tess_nums - chitra_nums
        chitra_only = chitra_nums - tess_nums

        norm_known = normalize_number(known_num) if known_num else ""
        tess_has_known = (norm_known in tess_nums) if norm_known else "N/A"
        chitra_has_known = (norm_known in chitra_nums) if norm_known else "N/A"

        results.append({
            "document": doc_id,
            "page": page_num,
            "known_number": known_num,
            "tess_has_known": tess_has_known,
            "chitra_has_known": chitra_has_known,
            "tess_chars": len(tess_text),
            "chitra_chars": len(chitra_text),
            "tess_num_count": len(tess_nums),
            "chitra_num_count": len(chitra_nums),
            "both_nums_count": len(both_nums),
            "tess_only_sample": "; ".join(sorted(list(tess_only))[:5]),
            "chitra_only_sample": "; ".join(sorted(list(chitra_only))[:5]),
            "notes": notes,
        })

    # Save to CSV
    out_csv_path = Path(args.out_csv)
    out_csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "document", "page", "known_number", "tess_has_known", "chitra_has_known",
        "tess_chars", "chitra_chars", "tess_num_count", "chitra_num_count",
        "both_nums_count", "tess_only_sample", "chitra_only_sample", "notes"
    ]
    with out_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved comparison results to {out_csv_path}\n")

    # Print summary table
    print(f"{'Document':<28} {'Pg':<4} {'Tess Chars':<11} {'Chitra Chars':<13} {'Tess #':<8} {'Chitra #':<9} {'Known Match (T/C)'}")
    print("-" * 88)
    for r in results:
        known_display = f"{r['tess_has_known']}/{r['chitra_has_known']}" if r['known_number'] else "-"
        print(f"{r['document'][:27]:<28} {r['page']:<4} {r['tess_chars']:<11} {r['chitra_chars']:<13} {r['tess_num_count']:<8} {r['chitra_num_count']:<9} {known_display}")


if __name__ == "__main__":
    main()
