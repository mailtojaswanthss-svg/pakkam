# Pakkam Backend Target State: Master Overnight Run Report

**Date:** 28 October 2026 (05:30 IST)  
**Target Milestone:** Submission 6 Nov 2026 (Feature Freeze 1 Nov 2026)  
**Scope:** Backend, Hybrid Data Indexing, Gnani Voice, Speed Benchmarks, Evidence Reports, Definition of Done  
**Git Branch:** `feat/ocr-step1-chitrapathak-gate`  
**Hardware:** NVIDIA GeForce RTX 4060 Laptop GPU (8 GB VRAM), Windows 11  

---

## Executive Summary

During the overnight execution window, the Pakkam backend underwent data pipeline processing, benchmark evaluations, and safety calibration:

1. **Hybrid OCR Processing:** All **500 currency-flagged pages** across 18 official documents finished in Crop Mode (~12s/page vs ~95s full-page). A clean Qdrant collection, **`pakkam_chitra`** (2,918 chunks, 4,449 vectors - marked "unexplained" discrepancy pending Qdrant internal point/segment audit), was created and indexed.
2. **Numerical Accuracy:** Tested on **4 specific ground-truth scheme queries** (Pudhumai Penn Rs. 1,000, CMCHIS Rs. 1,20,000, APY Rs. 1,000, PM-KISAN Rs. 6,000). "Correct" means the exact expected numerical string appeared in the live `/ask` response text citing the correct policy document. 3 additional hostel and welfare amounts failed during rate-limiting on the free tier.
3. **Voice Pipeline (Gnani STT & Timbre TTS):** STT latency of **1,320.4 ms** came from **one synthetic test clip (`synthetic_smoke_ta.wav`), not real speech**. Real read speech accuracy is evaluated separately on the AI4Bharat Kathbath dataset (Tamil WER 5.2% raw / 1.7% normalized, n=15; Hindi WER 3.7% raw / 1.7% normalized, n=15, read speech). Credit guards and daily caps were verified. Evon STT: **not used, not available on the public API**.
4. **Speed & Latency:** Search and reranking run in **636 ms** locally. LLM generation (`gemini-3.5-flash`) took a median of **6,300.7 ms**, with a **1,378.5 ms** verifier guardrail.
5. **Retrieval & Safety Calibration:** Evaluated on **194 draft questions, not yet verified by a person**. Hybrid Search + BGE Reranker v2 achieved **98.7% Recall@5** on draft questions. The refusal threshold **0.35 is the current default; the curve shows the trade-off on draft questions** (87.1% overall routing accuracy, 92.5% refusal of ungrounded questions).
6. **Definition of Done:** Automated test script `scripts/verify_dod.py` ran. DoD item 1 is **pytest only, no real fresh clone yet**. DoD item 6 is **git ls-files check only; real secrets scan pending**.

---

## 1. Hybrid OCR & Document Corpus Ingestion

### Corpus & Flagging Breakdown
- **Total Corpus Pages:** 2,688 across 18 official PDFs.
- **Pages with Printed Digit Sequences:** 1,255.
- **Currency-Flagged Pages Processed Overnight:** **500 pages** (containing markers: ரூ, Rs, Rs., ₹, रु).
- **Processing Architecture:** Tesseract bounding boxes locate currency regions -> tight bounding crops (with table headers) passed to `krutrim-ai-labs/Chitrapathak-2` -> fall back to full-page only if Tesseract confidence is 0.

### Disagreement Analysis & Safety
- **Disagreements Found:** `docs/review/ocr_disagreements.csv` cataloged **263 disagreement rows**.
- **What a Row Means:** Each row represents a page where the set of extracted numbers differed between Tesseract and Chitrapathak-2.
- **Digit / Currency Breakdown:** **263 of 263 rows** involve at least one digit in the difference set. **0 rows** contain raw isolated currency symbol strings in the disagreement column because currency markers attach directly to numbers or are stripped to digits during extraction.
- **Vector Count vs Chunks:** `pakkam_chitra` contains **2,918 chunks**, but Qdrant reports **4,449 vectors**; this is marked **unexplained** pending a low-level segment point/payload inspection.
- **Baseline Protection:** The baseline collection `schemes` was preserved untouched. All evaluations and live tests operated exclusively on `pakkam_chitra`.

---

## 2. LLM Pipeline & Latency Benchmark

Evaluated across 10 prepared citizen questions across Tamil, Hindi, English, and Tanglish (`docs/review/SPEED_REPORT.md`):

### Per-Stage Latency Breakdown

| Pipeline Stage | Sample Count (n) | Median Latency | p95 Latency | Min | Max | Component |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. First-Stage Search** | 10 | **399.1 ms** | 984.0 ms | 347.2 ms | 984.0 ms | Dense + Sparse (BGE-M3) |
| **2. BGE Reranker v2** | 10 | **236.8 ms** | 491.6 ms | 197.2 ms | 491.6 ms | Local GPU cross-encoder |
| **3. Answer LLM Generation** | 9 | **6,300.7 ms** | 13,416.6 ms | 3,776.5 ms | 13,416.6 ms | `gemini-3.5-flash` |
| **4. Grounding Verifier** | 9 | **1,378.5 ms** | 1,430.7 ms | 1,003.3 ms | 1,430.7 ms | `gemini-3.5-flash-lite` |
| **5. Full End-to-End Pipeline** | 10 | **8,246.5 ms** | 16,276.0 ms | 5,631.4 ms | 16,276.0 ms | Complete answer cycle |

---

## 3. Voice Integration (Gnani STT & Timbre TTS)

Evaluated using official API credentials, credit guardrails, and real speech samples (`docs/GNANI_RESULTS.md`):

### STT Performance (Gnani Prisma v2.5 / `POST /stt/v3`)
- **Latency Measurement:** STT latency of **1,320.4 ms** came from **one synthetic test clip (`synthetic_smoke_ta.wav`), not real speech**.
- **Real Speech Accuracy (Kathbath):**
  - **Tamil (n=15, read speech):** Raw WER **5.2%**, Normalized WER **1.7%**, Median Latency **0.95s**.
  - **Hindi (n=15, read speech):** Raw WER **3.7%**, Normalized WER **1.7%**, Median Latency **0.92s**.
- **Evon STT:** **Not used, not available on the public API**.
- **Audio Conditioning:** Normalization enforced at 16 kHz mono WAV, capped at 30 seconds.
- **Language Routing:** Spoken Tanglish queries (`ta-Latn`) route to Tamil STT (`ta-IN`) by default.

### TTS Performance & Safety (Gnani Timbre / `POST /api/v1/tts/inference`)
- **Spelling Out Amounts:** Number-to-words module (`voice/numbers.py`) converts currency markers into phonetically readable Indic strings (e.g., `ரூ.1,000` -> "ஆயிரம் ரூபாய்", `रु.1000` -> "एक हज़ार रुपये") to prevent TTS synthesizers from swallowing digits.
- **Credit Guard:** All STT and TTS calls track through `logs/gnani-calls.json`. Daily caps prevent unexpected credit consumption.

---

## 4. Retrieval & Refusal Safety Calibration

### Retrieval Ablation (`docs/review/RETRIEVAL_ABLATION_REPORT.md`)
Tested across **194 draft questions, not yet verified by a person**:
- **Keyword Only (Sparse BM25/BGE Sparse):** 67.5% Recall@5 (195.6 ms).
- **Dense Vector Only (BGE-M3):** 94.8% Recall@5 (52.1 ms).
- **Hybrid Search (Dense + Sparse):** 94.8% Recall@5 (215.6 ms).
- **Hybrid + BGE Reranker v2:** **98.7% Recall@5** (384.3 ms).  
  *Finding: Cross-encoder reranking intercepts near-miss false negatives on draft questions.*

### Refusal-Threshold Operating Curve (`docs/review/REFUSAL_THRESHOLD_CURVE.md`)
Swept across confidence thresholds [0.20, 0.50] on **194 draft questions, not yet verified by a person**:
- Threshold `0.20`: 87.6% Routing Accuracy | 77.5% Correct Refusals | 9.7% False Refusals
- Threshold `0.25`: 88.1% Routing Accuracy | 82.5% Correct Refusals | 10.4% False Refusals
- Threshold `0.30`: 86.1% Routing Accuracy | 85.0% Correct Refusals | 13.6% False Refusals
- **Threshold `0.35`:** **0.35 is the current default; the curve shows the trade-off on draft questions** (87.1% Routing Accuracy | 92.5% Correct Refusals | 14.3% False Refusals)
- Threshold `0.40`: 84.5% Routing Accuracy | 92.5% Correct Refusals | 17.5% False Refusals
- Threshold `0.50`: 81.4% Routing Accuracy | 95.0% Correct Refusals | 22.1% False Refusals

---

## 5. Definition of Done Compliance Matrix

Audited automatically via `scripts/verify_dod.py`:

| # | DoD Requirement | Command / Test | Result |
| :---: | :--- | :--- | :---: |
| 1 | Fresh clone runs on Windows | `pytest tests/test_api.py` | **pytest only, no real fresh clone yet** (44/44 passed) |
| 2 | 7 known amounts correct via `/ask` | Live `/ask` against `pakkam_chitra` | **4/7 verified** (Pudhumai Penn, CMCHIS, APY, PM-KISAN; remaining 3 hit free-tier rate limit) |
| 3 | Out-of-domain safe refusal | Live `/ask` out-of-domain query | **PASS** (`status: INSUFFICIENT_EVIDENCE`) |
| 4 | `/ask/voice` audio & timings | Live `/ask/voice` upload with synthetic clip | **PASS** (`stt: 1320.4 ms` from one synthetic clip, `retrieval: 486.0 ms`) |
| 5 | Evidence reports exist & script-backed | File provenance & size audit | **PASS** (Reports verified) |
| 6 | Zero keys, audio, or PII in git | `git ls-files` check only | **git ls-files check only; real secrets scan pending** |
| 7 | Clean git working tree | `git status` | **PASS** (working tree clean) |

---

## 6. What Is Not Claimed (Honest Disclosures)

- **Research Prototype Status:** Chitrapathak-2 weights are distributed under Krutrim Community License v1.0 (research use). Consequently, `pakkam_chitra` is designated as a research prototype index.
- **Selection Bias in OCR Comparison:** The 7 known-problem pages were selected specifically because Tesseract failed on them. The 0/7 vs 7/7 result reflects robustness on adversarial digit layouts, not whole-document character error rate on clear text.
- **Draft Question Set:** The 194 questions in `questions-review.csv` are draft questions, not yet verified by a person; formal native-speaker verification remains to be performed.
- **Speech Evaluation Limitations:** STT latency was measured on a single synthetic audio clip. The Kathbath WER numbers (Tamil 5.2% raw, Hindi 3.7% raw) are from clean read speech, not conversational or noisy citizen queries. Evon STT is not used and not available on the public API.
- **Vector Count vs Chunks:** 4,449 vectors vs 2,918 chunks is marked unexplained.
- **Safety Threshold:** 0.35 is the current default; the curve shows the trade-off on draft questions.
- **DoD Status:** DoD item 1 is pytest only, no real fresh clone yet. DoD item 6 is git ls-files check only; real secrets scan pending.
- **Local Workstation Hardware:** All latency figures reflect an RTX 4060 Laptop GPU under warm cache conditions; multi-tenant cloud deployments will exhibit different concurrency profiles.
