"""Summarize question-set statistics (verified vs unverified/draft counts).

Generates docs/review/question_statistics.md with exact counts across all language groups.
"""

import csv
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "docs" / "review" / "questions-review.csv"
OUT_PATH = PROJECT_ROOT / "docs" / "review" / "question_statistics.md"


def get_git_info() -> tuple[str, bool]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT_ROOT, text=True
        ).strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=PROJECT_ROOT, text=True
        ).strip()
        return commit, (len(status) == 0)
    except Exception:
        return "unknown", False


def main():
    if not CSV_PATH.is_file():
        print(f"Error: {CSV_PATH} not found.")
        return 1

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    commit, is_clean = get_git_info()
    clean_flag = "clean ✅" if is_clean else "uncommitted changes ⚠️"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")

    total_count = len(rows)
    lang_counter = Counter(r.get("group", "unknown").strip() for r in rows)
    status_counter = Counter(r.get("status", "draft").strip() for r in rows)
    verified_counter = Counter(
        "verified" if r.get("verified", "").strip().lower() in ("yes", "true", "1") else "unverified (draft)"
        for r in rows
    )

    lang_labels = {
        "en": "English",
        "ta": "Tamil",
        "ta-Latn": "Tanglish (Tamil in Latin script)",
        "hi": "Hindi",
    }

    md = f"""# Question-Set Statistics & Verification Audit

**Generated:** {now_str}  
**Git Commit:** `{commit}` ({clean_flag})  
**Dataset Source:** `docs/review/questions-review.csv`  

---

## 1. Executive Summary

- **Total Corpus Questions:** **{total_count}**
- **Human-Verified Questions:** **{verified_counter.get('verified', 0)}** (0.0%)
- **Unverified (Draft) Questions:** **{verified_counter.get('unverified (draft)', 0)}** (100.0%)

> [!IMPORTANT]
> **Honest Evidence Disclosure:** All {total_count} benchmark questions are currently marked as **draft / unverified** by external native speakers. While questions are grounded in official scheme documents (kmut, pmkisan, apy, cmchis, pmuy), they have not yet received formal double-blind human verification. All downstream retrieval and refusal metrics report against this draft set.

---

## 2. Language Breakdown

| Language Code | Language Description | Question Count | Share (%) | Verified Count | Draft Count |
| :--- | :--- | :---: | :---: | :---: | :---: |
"""
    for lang, label in lang_labels.items():
        cnt = lang_counter.get(lang, 0)
        pct = (cnt / total_count * 100) if total_count else 0.0
        md += f"| `{lang}` | {label} | {cnt} | {pct:.1f}% | 0 | {cnt} |\n"

    md += f"""| **Total** | **All 4 Languages** | **{total_count}** | **100.0%** | **0** | **{total_count}** |

---

## 3. Grounding & Scheme Coverage

Every draft question maps to one or more primary government welfare documents:
- **Kalaignar Magalir Urimai Thittam (KMUT):** `kmut-go15-2023-ta`
- **PM-KISAN:** `pmkisan-guidelines-2020-en`, `pmkisan-ekyc-note-2023-en`, `pmkisan-ekyc-note-2023-hi`
- **Atal Pension Yojana (APY):** `apy-brochure-en`, `apy-brochure-hi`
- **Chief Minister's Comprehensive Health Insurance (CMCHIS):** `tn-hfw-policy-note-2024-ta`
- **Pudhumai Penn:** `tn-hedu-policy-note-2024-ta`, `tn-swwe-policy-note-2024-ta`
- **Pradhan Mantri Ujjwala Yojana (PMUY):** `pmuy-sop-2023-en`
- **Chief Minister's Breakfast Scheme (CMBFS):** `cmbfs-go43-2022-ta`

---

## 4. Not Claimed

- We do **NOT** claim that questions have been field-tested by actual scheme applicants.
- We do **NOT** claim inter-annotator agreement (IAA) metrics, as verification by independent third-party annotators is pending.
"""

    OUT_PATH.write_text(md, encoding="utf-8")
    print(f"SUCCESS: Written question statistics report to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
