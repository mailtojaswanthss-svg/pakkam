import csv
import json
import re
from pathlib import Path
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from schemebot.config import get_settings
from schemebot.ingest.extract import OCR_DPI, OCR_LANGUAGES
from schemebot.ingest.ocr_cache import HASH_PREFIX, file_sha256

CURRENCY_PATTERN = re.compile(r"(?:ரூ|Rs\.?|₹|रु)", re.IGNORECASE)
DIGITS_3_PATTERN = re.compile(r"\b\d{3,}\b")

# Target demo schemes in priority order:
# Pudhumai Penn, CMCHIS, BC/MBC and ADTW hostels, APY, PM-Kisan, PMUY, followed by others.
SCHEME_ORDER = [
    # 1. Pudhumai Penn
    "tn-hedu-policy-note-2024-ta",
    "tn-swwe-policy-note-2024-ta",
    # 2. CMCHIS
    "tn-hfw-policy-note-2024-ta",
    "tn-hfw-policy-note-2024-en",
    # 3. BC/MBC and ADTW hostels
    "tn-bcmbc-policy-note-2024-ta",
    "tn-bcmbc-policy-note-2024-en",
    "tn-adtw-policy-note-2024-ta",
    "tn-adtw-policy-note-2024-en",
    # 4. APY
    "apy-brochure-hi",
    "apy-brochure-en",
    # 5. PM-Kisan
    "pmkisan-ekyc-note-2023-hi",
    "pmkisan-ekyc-note-2023-en",
    "pmkisan-guidelines-2020-en",
    # 6. PMUY
    "pmuy-sop-2023-en",
    # Other documents
    "kmut-go15-2023-ta",
    "cmbfs-go43-2022-ta",
    "tn-hedu-policy-note-2024-en",
    "tn-swwe-policy-note-2024-en",
]


def get_scheme_category(doc_id: str) -> str:
    if doc_id in ("tn-hedu-policy-note-2024-ta", "tn-swwe-policy-note-2024-ta"):
        return "Pudhumai Penn / Women & Higher Ed"
    if "hfw" in doc_id:
        return "CMCHIS (Health)"
    if "bcmbc" in doc_id or "adtw" in doc_id:
        return "BC/MBC & ADTW Hostels"
    if "apy" in doc_id:
        return "APY (Pension)"
    if "pmkisan" in doc_id:
        return "PM-Kisan"
    if "pmuy" in doc_id:
        return "PMUY (Ujjwala)"
    if "kmut" in doc_id:
        return "KMUT (Magalir Urimai)"
    if "cmbfs" in doc_id:
        return "CM Breakfast Scheme"
    return "Other English Notes"


def main():
    settings = get_settings()
    manifest_file = settings.data_dir / "sources.json"
    sources_list = json.loads(manifest_file.read_text(encoding="utf-8"))
    sources_by_id = {s["doc_id"]: s for s in sources_list}

    cache_root = settings.processed_dir / "ocr_cache"
    out_csv = Path("docs/review/ocr_flagged_pages.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    flagged_rows = []
    stats_per_doc = {}

    for doc_id in SCHEME_ORDER:
        if doc_id not in sources_by_id:
            continue
        s = sources_by_id[doc_id]
        pdf_path = settings.raw_dir / s["file"]
        if not pdf_path.exists():
            continue

        lang_code = OCR_LANGUAGES[s["language"]]
        key = f"{file_sha256(pdf_path)[:HASH_PREFIX]}-{lang_code}-{OCR_DPI}dpi"
        folder = cache_root / key
        if not folder.exists():
            continue

        txt_files = sorted(folder.glob("p*.txt"), key=lambda p: int(p.stem[1:]))
        doc_total = len(txt_files)
        doc_flagged = 0
        doc_currency_only = 0

        for tf in txt_files:
            page_num = int(tf.stem[1:])
            text = tf.read_text(encoding="utf-8")

            curr_matches = list(set(CURRENCY_PATTERN.findall(text)))
            dig_matches = DIGITS_3_PATTERN.findall(text)

            reasons = []
            if curr_matches:
                reasons.append(f"currency: {', '.join(curr_matches)}")
                doc_currency_only += 1
            if dig_matches:
                sample_digs = list(dict.fromkeys(dig_matches))[:5]
                reasons.append(f"3+ digits: {', '.join(sample_digs)}")

            if reasons:
                doc_flagged += 1
                flagged_rows.append({
                    "document": doc_id,
                    "page": page_num,
                    "reason": "; ".join(reasons),
                    "has_currency": bool(curr_matches),
                    "category": get_scheme_category(doc_id),
                })

        stats_per_doc[doc_id] = {
            "total_ocr": doc_total,
            "flagged": doc_flagged,
            "currency_flagged": doc_currency_only,
            "category": get_scheme_category(doc_id),
        }

    # Write CSV
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["document", "page", "reason"])
        for r in flagged_rows:
            writer.writerow([r["document"], r["page"], r["reason"]])

    total_flagged = len(flagged_rows)
    total_currency = sum(s["currency_flagged"] for s in stats_per_doc.values())
    SEC_PER_PAGE = 95.0

    print("=" * 85)
    print(f"HYBRID OCR FLAGGING REPORT (Total OCR Pages: 1,353)")
    print(f"Flagging Rule: Contains currency marker (ரூ, Rs, Rs., ₹, रु) OR 3+ digits")
    print(f"Wrote flagged pages to: {out_csv.as_posix()}")
    print("=" * 85)
    print(f"{'Scheme / Category':<32} {'Document ID':<28} {'Flagged':<9} {'(Currency)':<11} {'Est. Time'}")
    print("-" * 85)

    current_cat = None
    for doc_id, st in stats_per_doc.items():
        if st["category"] != current_cat:
            current_cat = st["category"]
            print(f"\n[{current_cat}]")
        est_gpu_hours = (st["flagged"] * SEC_PER_PAGE) / 3600.0
        print(f"  {doc_id:<36} {st['flagged']:>4}/{st['total_ocr']:<4} ({st['currency_flagged']:>4} curr)   {est_gpu_hours:>6.1f} hrs")

    print("=" * 85)
    all_gpu_hours = (total_flagged * SEC_PER_PAGE) / 3600.0
    curr_gpu_hours = (total_currency * SEC_PER_PAGE) / 3600.0
    print(f"TOTAL FLAGGED (Currency OR 3+ Digits): {total_flagged} pages  (~{all_gpu_hours:.1f} GPU hours)")
    print(f"TOTAL WITH CURRENCY MARKERS ONLY:       {total_currency} pages  (~{curr_gpu_hours:.1f} GPU hours)")
    print("=" * 85)


if __name__ == "__main__":
    main()
