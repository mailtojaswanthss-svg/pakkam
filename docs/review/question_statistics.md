# Question-Set Statistics & Verification Audit

**Generated:** 2026-10-28 02:50:12 IST  
**Git Commit:** `7ff73af` (uncommitted changes ⚠️)  
**Dataset Source:** `docs/review/questions-review.csv`  

---

## 1. Executive Summary

- **Total Corpus Questions:** **194**
- **Human-Verified Questions:** **0** (0.0%)
- **Unverified (Draft) Questions:** **194** (100.0%)

> [!IMPORTANT]
> **Honest Evidence Disclosure:** All 194 benchmark questions are currently marked as **draft / unverified** by external native speakers. While questions are grounded in official scheme documents (kmut, pmkisan, apy, cmchis, pmuy), they have not yet received formal double-blind human verification. All downstream retrieval and refusal metrics report against this draft set.

---

## 2. Language Breakdown

| Language Code | Language Description | Question Count | Share (%) | Verified Count | Draft Count |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `en` | English | 49 | 25.3% | 0 | 49 |
| `ta` | Tamil | 48 | 24.7% | 0 | 48 |
| `ta-Latn` | Tanglish (Tamil in Latin script) | 49 | 25.3% | 0 | 49 |
| `hi` | Hindi | 48 | 24.7% | 0 | 48 |
| **Total** | **All 4 Languages** | **194** | **100.0%** | **0** | **194** |

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
