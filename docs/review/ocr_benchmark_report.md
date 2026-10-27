# OCR Benchmark Report: Tesseract vs. Chitrapathak-2

**Project:** indic-scheme-rag (Pakkam)  
**Date:** 27 October 2026  
**Hardware:** NVIDIA GeForce RTX 4060 Laptop GPU (8 GB VRAM), Intel Core CPU, Windows 11  
**Pinned Model:** `krutrim-ai-labs/Chitrapathak-2` (Revision: `e21a8b2983fdf6fbf335c9e5ae6a3e52ba9e5e3b`)  
**Tesseract Version:** 5.5.0 (`tam` + `hin` + `eng` language packs)  

---

## 1. Executive Summary

This report evaluates **Chitrapathak-2** against **Tesseract OCR** across the 18 official government scheme documents used in the Pakkam project. 

- **Accuracy on Scheme Numbers:** **Chitrapathak-2 achieved 100.0% (7/7 on the 7 known-problem pages)** on known ground-truth numerical values, whereas **Tesseract achieved 0.0% (0/7)**, corrupting all 7 critical eligibility thresholds and financial amounts (e.g., misreading Rs. 1,000 as 4,000 or 7,000). *(Note: Selection bias applies; these 7 pages were chosen specifically because Tesseract failed on them).*
- **Speed & Hardware:** **Tesseract is ~60× faster** (~1.2s vs. ~95s per page) and runs entirely on CPU with zero VRAM. Chitrapathak-2 requires an 8 GB GPU.
- **Decision:** **Adopt a Hybrid Architecture for Research Prototype.** Retain Tesseract as the default for fast local development and CPU-bound pipelines. Use Chitrapathak-2 (`SCHEMEBOT_OCR_ENGINE=chitrapathak`) in our research prototype index (`pakkam_chitra`) for policy documents containing financial amounts to eliminate errors without brittle manual regex overrides (`data/corrections.json`). Given Krutrim Community License v1.0 is research-only, this pipeline serves as a research prototype.

---

## 2. Corpus Statistics (Verified via `scripts/report_ocr_stats.py`)

Ingestion of the 18 official scheme PDFs yielded the following exact page and chunk distribution:

| Metric | Count | Percentage |
| :--- | :--- | :--- |
| **Total Corpus Pages** | **2,688** | 100.0% |
| **Pages Requiring OCR** | **1,353** | **50.3%** |
| **Native Digital Text Pages** | **1,335** | 49.7% |
| **Total Chunks in Index** | **2,785** | 100.0% |
| - English Chunks (`en`) | 1,390 | 49.9% |
| - Tamil Chunks (`ta`) | 1,382 | 49.6% |
| - Hindi Chunks (`hi`) | 13 | 0.5% |

### Per-Document Breakdown

| Document ID | Language | OCR Pages | Total Pages | OCR % | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `kmut-go15-2023-ta` | Tamil | 36 | 43 | 83.7% | Scanned Tamil G.O. annexures |
| `pmkisan-guidelines-2020-en` | English | 0 | 12 | 0.0% | Native digital PDF |
| `pmkisan-ekyc-note-2023-hi` | Hindi | 3 | 3 | 100.0% | Scanned Hindi notification |
| `pmkisan-ekyc-note-2023-en` | English | 0 | 2 | 0.0% | Native digital PDF |
| `apy-brochure-en` | English | 1 | 2 | 50.0% | Image table |
| `apy-brochure-hi` | Hindi | 2 | 2 | 100.0% | Scanned Hindi brochure |
| `pmuy-sop-2023-en` | English | 1 | 6 | 16.7% | Scanned signature page |
| `tn-swwe-policy-note-2024-en` | English | 2 | 255 | 0.8% | Scanned diagram pages |
| `tn-swwe-policy-note-2024-ta` | Tamil | 297 | 297 | 100.0% | Scanned Tamil policy note |
| `cmbfs-go43-2022-ta` | Tamil | 18 | 18 | 100.0% | Scanned Tamil G.O. |
| `tn-hfw-policy-note-2024-en` | English | 2 | 649 | 0.3% | Scanned diagram pages |
| `tn-hfw-policy-note-2024-ta` | Tamil | 568 | 568 | 100.0% | Scanned Tamil policy note |
| `tn-hedu-policy-note-2024-en` | English | 5 | 189 | 2.6% | Scanned budget tables |
| `tn-hedu-policy-note-2024-ta` | Tamil | 122 | 122 | 100.0% | Scanned Tamil policy note |
| `tn-adtw-policy-note-2024-en` | English | 12 | 154 | 7.8% | Scanned budget tables |
| `tn-adtw-policy-note-2024-ta` | Tamil | 172 | 172 | 100.0% | Scanned Tamil policy note |
| `tn-bcmbc-policy-note-2024-en` | English | 5 | 87 | 5.7% | Scanned tables |
| `tn-bcmbc-policy-note-2024-ta` | Tamil | 107 | 107 | 100.0% | Scanned Tamil policy note |
| **TOTAL** | — | **1,353** | **2,688** | **50.3%** | — |

---

## 3. Side-by-Side Benchmark Matrix

| Dimension | Tesseract OCR (v5.5) | Chitrapathak-2 (4B VLM) | Winner |
| :--- | :--- | :--- | :--- |
| **Target Number Accuracy** | **0.0% (0 / 7)** | **100.0% (7 / 7 on the 7 known-problem pages)** | **Chitrapathak-2 (+100.0%)** |
| **Resolution of `corrections.json`** | 0 / 7 without manual patch | **7 / 7 automatically resolved** | **Chitrapathak-2** |
| **Average Page Latency** | **~1.2 seconds** | ~95.0 seconds (~1.6 min) | **Tesseract (~60× faster)** |
| **Estimated 1,353 Pages Time** | **~27 minutes** | ~35.7 hours | **Tesseract** |
| **Hardware Required** | Any standard CPU | Dedicated GPU (≥ 8 GB VRAM) | **Tesseract** |
| **VRAM Consumption** | 0 MB | 7.78 GB (at 150 DPI) | **Tesseract** |
| **Disk Storage** | ~50 MB traineddata | 11.6 GB model weights | **Tesseract** |
| **Indic Unicode Extraction** | Frequent token/digit splitting | Verbatim fluent Indic script | **Chitrapathak-2** |
| **Licensing** | Apache License 2.0 (Commercial OK) | Krutrim Community License v1.0 (Research only) | **Tesseract** |

---

## 4. Ground-Truth Numerical Accuracy (`data/corrections.json`)

Evaluated directly with [`scripts/check_corrections.py`](file:///f:/sar.ai%20pr/scripts/check_corrections.py) comparing extracted text against true printed PDF values:

| # | Document & Page | Scheme & Field | True PDF Text | Tesseract Reading | Chitrapathak-2 Reading | Impact of Tesseract Error |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | `tn-hedu-policy-note-2024-ta` (p.33) | Pudhumai Penn monthly aid | **`ரூ.1,000`** | `ரூ.4,000` ❌ | `ரூ.1,000` ✅ | User told benefit is 4× higher than reality |
| 2 | `tn-swwe-policy-note-2024-ta` (p.11) | Pudhumai Penn monthly aid | **`ரூ.1000`** | `ரூ.7000` ❌ | `ரூ.1000` ✅ | User told benefit is 7× higher than reality |
| 3 | `tn-hfw-policy-note-2024-ta` (p.421) | CMCHIS family income limit | **`ரூ.1,20,000`** | `ரூ.4,20,000` ❌ | `ரூ.1,20,000` ✅ | Ineligible citizens wrongly told they qualify |
| 4 | `apy-brochure-hi` (p.1) | APY minimum guaranteed pension | **`रु.1000`** | `रु.000` ❌ | `रु.1000` ✅ | Digits completely erased |
| 5 | `tn-swwe-policy-note-2024-ta` (p.88) | Senior citizen helpline | **`14567`** | `14௧67` ❌ | `14567` ✅ | Corrupted with Tamil digit '௧' (14167 dialed) |
| 6 | `tn-bcmbc-policy-note-2024-ta` (p.59) | BC/MBC Hostel monthly food charge | **`ரூ.1,400`** | `ரூ.4400` ❌ | `ரூ.1,400` ✅ | Overreported fee by Rs. 3,000 |
| 7 | `tn-adtw-policy-note-2024-ta` (p.53) | ADTW Hostel monthly food subsidy | **`ரூ.1400/-`** | `ரூ.44007-` ❌ | `ரூ.1400/-` ✅ | Corrupted digits and punctuation |

**Summary Score:**
- **Tesseract Accuracy:** **0 / 7 (0.0%)** on known failure points
- **Chitrapathak-2 Accuracy:** **7 / 7 (100.0%) on the 7 known-problem pages**

> **Selection Bias Note:** The 7 evaluation pages were intentionally selected because they were known failure points for Tesseract (originating from `data/corrections.json` where citizen-critical monetary values had been misread). Consequently, the 0/7 Tesseract score reflects performance on these adversarial edge cases, not overall document character accuracy (where Tesseract succeeds on clear prose). Chitrapathak-2's 7/7 result verifies that vision-language modeling effectively resolves these specific numeral segmentation errors on known failure pages.

---

## 5. Technical Analysis: Why Tesseract Fails on Indic Numbers

1. **Character Segmentation in Indic Ligatures:**
   Tesseract's LSTM segmenter struggles with Tamil glyphs preceding numerals (e.g. `ரூ.1000`). The rupee symbol `ரூ` (`\u0bb0` + `\u0bc2`) is often merged into the following digit `1`, transforming it into glyph patterns resembling `4` or `7`.
2. **Font Kerning and Punctuation Confusion:**
   In Tamil policy notes, the slash-hyphen suffix `/-` is frequently mapped to `7-` (e.g. `44007-`), and commas are discarded or joined with digits.
3. **Vision Language Model Superiority:**
   Chitrapathak-2 uses a Vision Transformer encoder with patch dynamic resolution (`max_pixels=1280*28*28`) conditioned on the Qwen-2.5 language model. It decodes the whole word context (`மாதமொன்றுக்கு ரூ.1,400`), recognizing numerals syntactically and visually in context.

---

## 6. Project Recommendation & Implementation Architecture

### **Which is Good to Use?**

| Use Case | Recommended Engine | Rationale |
| :--- | :--- | :--- |
| **Research Prototype Indexing of Policy Documents** | **Chitrapathak-2** | 100% numerical accuracy ensures citizen answers are factually correct on problem pages; serves as an offline research prototype (`pakkam_chitra`). Note: Krutrim Community License v1.0 restricts use to non-commercial research. |
| **CI / Automated Test Environments** | **Tesseract** | Runs in seconds, requires no GPU/CUDA, fits within standard GitHub Actions runners. |
| **Rapid Iteration / Development** | **Tesseract** | Rebuilds the full 1,353 OCR page corpus in under 30 minutes. |

### **How to Use It in the Codebase:**

The implementation is complete and non-breaking:
```bash
# To run fast default with Tesseract:
uv run python -m schemebot.ingest

# To run with high-precision Chitrapathak-2:
SCHEMEBOT_OCR_ENGINE=chitrapathak uv run python -m schemebot.ingest

# To build a separate Qdrant collection without touching baseline data:
SCHEMEBOT_OCR_ENGINE=chitrapathak SCHEMEBOT_QDRANT_COLLECTION=pakkam_chitra uv run python -m schemebot.index
```
