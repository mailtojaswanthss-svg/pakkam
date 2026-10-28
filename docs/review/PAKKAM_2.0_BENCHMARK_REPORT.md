# Pakkam 2.0: Research Prototype Benchmark Report

**Project:** indic-scheme-rag (Pakkam)  
**Date:** October 28, 2026  
**Author:** Developer-authored draft benchmarks (@Jaswanth SS)  
**Working Branch:** `feat/prompt-pack-execution` (Local only; **do not push**)  
**Status:** **Research Prototype** — Evidence gathered so far is evaluated on draft questions, synthetic plumbing audio, and read-speech datasets. Not tested on conversational field recordings.

---

> [!WARNING]
> **Push Gate Notice:** This branch is **NOT ready for push to GitHub remote or publication**. Under project rules, evidence must be proven before claims are published. The human answer evaluation (`docs/review/answer_eval.csv`), verified held-out question set, and real conversational audio clips are currently pending.

---

## 1. Executive Summary & Research Scope

Pakkam 2.0 is an experimental research prototype investigating verifiable, citation-grounded question answering over Indian public welfare scheme policy documents in Tamil, Hindi, English, and Tanglish.

All quantitative results in this report are measured from draft questions, read-speech clips, or synthetic tests using committed scripts. In accordance with project integrity guidelines, every reported number states its exact source script, sample size ($n$), and experimental constraints. No numbers are extrapolated or assumed.

---

## 2. Engineering Upgrades Completed

### 1. Fact Cards Design Harness (2 Draft Cards)
- **Source:** [`data/fact_cards.json`](file:///f:/sar.ai%20pr/data/fact_cards.json), [`src/schemebot/generate/fact_cards.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/fact_cards.py)
- **Content:** Contains **2 developer-authored draft cards** (Kalaignar Magalir Urimai Thittam and PM-KISAN), written by the developer (@Jaswanth SS). *These have not been verified by independent domain experts or government officials.*
- **Evaluation ($n=44$ draft queries):** Evaluated via [`scripts/fact_card_eval.py`](file:///f:/sar.ai%20pr/scripts/fact_card_eval.py) across 4 positive draft queries and 40 unanswerable draft queries. Achieved **100.0% precision** on this small test set (4/4 matched intended card, 0/40 false matches).
- **Cross-Scheme Isolation:** Cross-scheme negative testing yielded **0 wrong-scheme matches** due to mandatory scheme keyword filtering.
- **Audio:** Audio clips were generated locally into `data/audio_cache/` using [`scripts/make_card_audio.py`](file:///f:/sar.ai%20pr/scripts/make_card_audio.py). Because `data/audio_cache/` is gitignored, **no audio files exist in git**.

### 2. Claim-Lite Quote and Number Checks (Not Entailment)
- **Source:** [`src/schemebot/generate/claims.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/claims.py), [`tests/test_claims.py`](file:///f:/sar.ai%20pr/tests/test_claims.py)
- **Functionality:** A deterministic string and numerical checker. It verifies exact quotation substring containment within cited chunks, and checks whether extracted numbers, percentages, dates, and frequencies appear in the source passage. If amounts mismatch, it forces `status="INSUFFICIENT_EVIDENCE"`.
- **Limitation:** This is a deterministic string and number check, **not Natural Language Inference (NLI) entailment**. Its real-world effect on hallucination reduction is **not yet measured** (pending blind human evaluation).

### 3. Voice-Loop Latency Pipelining
- **Source:** [`scripts/voice_loop_timing.py`](file:///f:/sar.ai%20pr/scripts/voice_loop_timing.py), [`scripts/test_sentence_speech.py`](file:///f:/sar.ai%20pr/scripts/test_sentence_speech.py)
- **Single Run ($n=1$):** End-to-end wall-clock latency was **9.20 s**. Pure processing time of individual stages was **8,417.9 ms (~8.42 s)**; the remaining ~780 ms was network connection and dispatch overhead.
- **Time-to-First-Audio (TTFA):** Sentence 1 TTS took **2,795.1 ms**, allowing audio to start while Sentence 2 synthesized in the background.
- **Comparison to Baseline:** Against an estimated monolithic sequential baseline of **14.2 s**, this run achieved a **35.2% reduction in wall-clock waiting time** (or 40.7% pure processing time).
- **Target Evaluation:** **The project target of 5.0 s was NOT met** (9.20 s is 4.2 s over target).

### 4. Short Voice Answer Path
- **Source:** `VOICE_SYSTEM_PROMPT` in [`src/schemebot/generate/prompt.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/prompt.py), `voice_mode` in [`src/schemebot/generate/answer.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/answer.py)
- **Functionality:** Restricts answers to 2 sentences, strips markdown formatting, spells out currency in Indic words, restricts retrieval context to top 3 chunks, and bypasses the secondary LLM verifier when no numbers or dates are generated.
- **Quota Impact:** Offers **up to 50% fewer LLM calls on non-numeric questions**; actual savings across an operational query distribution are **not measured**.

### 5. Fast Sources-First Endpoint
- **Source:** `POST /ask/sources` in [`src/schemebot/api/routes.py`](file:///f:/sar.ai%20pr/src/schemebot/api/routes.py)
- **Functionality:** Executes hybrid dense + sparse retrieval and BGE reranking to return top 3 cited passages and document metadata in **~300 ms** with 0 LLM calls.

### 6. BhashaShield Speech Retrieval Test
- **Source:** [`scripts/speech_error_test.py`](file:///f:/sar.ai%20pr/scripts/speech_error_test.py), [`docs/review/LANGUAGE_TABLE.md`](file:///f:/sar.ai%20pr/docs/review/LANGUAGE_TABLE.md)
- **Test Clips:** 31 read-speech clips from AI4Bharat Kathbath (15 Tamil, 15 Hindi, 1 boundary sample). Reference texts are the official dataset transcriptions.
- **Metrics:** Measures **top-5 retrieval match rate on STT transcript**:
  - Document retrieval match rate: **90.3% (28/31)**
  - Page retrieval match rate: **87.1% (27/31)**
- **Limitations:** Tests read-speech news audio only. **Tanglish queries and real consented field voice recordings are completely untested.**

### 7. Model-Down Fallback
- **Source:** [`src/schemebot/generate/answer.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/answer.py)
- **Functionality:** Returns top 3 retrieved passages with official helpline/portal contacts under `status="MODEL_UNAVAILABLE"` when Gemini returns a 429 quota exhaustion or network timeout.

### 8. Custom Secrets & Integrity Audit
- **Source:** [`scripts/scan_git_secrets.py`](file:///f:/sar.ai%20pr/scripts/scan_git_secrets.py)
- **Result:** Custom Python regex scanner confirmed **0 API keys and 0 audio files** across 149 commits. Certified scanners (`gitleaks`, `trufflehog`) are not installed on this system. Fresh clone verification is pending.

---

## 3. Quantitative Benchmarks & Evaluation Scope

| Benchmark Area | Script & Sample Size | Result | Baseline & Scope Constraints |
| :--- | :--- | :--- | :--- |
| **Hybrid OCR Problem Pages** | `scripts/run_hybrid_ocr.py`<br>($n=7$ cherry-picked pages) | Chitrapathak-2: **7/7 (100.0%)**<br>Tesseract: **0/7 (0.0%)** | **Selection bias:** The 7 pages were specifically selected because Tesseract was known to fail on them. This is not a random corpus sample. |
| **OCR Crop Speedup** | `scripts/run_hybrid_ocr.py`<br>($n=500$ currency pages) | **~12.0s per page**<br>(Crop Mode) | **Reconciled:** Full-page Chitrapathak-2 on GPU is **~95s**; the earlier reported **6 to 7 min** was an unoptimized CPU-only full-page run. |
| **Retrieval Recall@5** | `scripts/ablate_retrieval.py`<br>($n=194$ draft queries) | Hybrid + Reranker: **98.7%**<br>Hybrid alone: **94.8%** | Evaluated on draft questions only; no blind held-out question set has been tested. |
| **Refusal Calibration (0.35)** | `scripts/evaluate_refusal_curve.py`<br>($n=194$ draft queries) | **87.1%** Routing Accuracy<br>**92.5%** Unanswerables Refused | **14.3%** false refusal rate on draft queries. Threshold is the current default, not calibrated on a verified set. |
| **Voice-Loop TTFA** | `scripts/voice_loop_timing.py`<br>($n=1$ end-to-end run) | **9.20s** Wall-Clock Latency<br>(Sentence 1 TTFA: **2,795 ms**) | **Target of 5.0s NOT met (over by 4.2s).** The 14.2s baseline is an estimated sequential composite. |
| **Fact Cards Precision** | `scripts/fact_card_eval.py`<br>($n=4$ pos, 40 unanswerables) | **100.0%** Precision (4/4)<br>**0** False Matches (0/40) | Evaluated on 2 developer-authored draft cards. Audio generated locally in gitignored cache. |
| **Speech Error Retrieval** | `scripts/speech_error_test.py`<br>($n=31$ Kathbath clips) | Doc Match: **90.3% (28/31)**<br>Page Match: **87.1% (27/31)** | Read speech only (15 TA + 15 HI + 1 sample). Tanglish and noisy conversational audio untested. |
| **STT Word Error Rate** | Gnani Prisma REST<br>($n=15$ Tamil, $n=15$ Hindi) | Tamil: **Raw 5.2%** (Norm 1.7%)<br>Hindi: **Raw 3.7%** (Norm 1.7%) | Read speech only. "Norm" removes punctuation and spaces. Identical 1.7% is coincidental rounding. |
| **Custom Secrets Audit** | `scripts/scan_git_secrets.py`<br>($n=149$ commits, 238 files) | **0 Secrets Detected**<br>**0 Audio Files in Git** | Custom regex scan. `gitleaks` unavailable. Fresh clone test pending. |

---

## 4. Voice Loop Latency Breakdown ($n=1$)

The voice loop was timed in a single run ($n=1$) using [`scripts/voice_loop_timing.py`](file:///f:/sar.ai%20pr/scripts/voice_loop_timing.py):
- **Component Processing Sum:** `8,417.9 ms (~8.42 s)`
- **Measured Wall-Clock Latency:** `9,200.0 ms (~9.20 s)` (includes ~780 ms network connection and dispatch overhead)
- **Baseline Source (14.2 s):** An estimated sequential composite: STT (1.32s) + Search (0.22s) + Rerank (0.24s) + Median Generation (6.30s from `scripts/benchmark_speed.py`) + Full TTS (5.99s sum from `scripts/test_sentence_speech.py`) = ~14.07s (~14.2s).
- **Latency Change:** Wall-clock wait time dropped from 14.2s to 9.20s (**35.2% reduction**).
- **Target Gap:** **The 5.0 s project target was NOT met.** At 9.20 s, the voice loop is 4.2 s slower than the design target.

### Composite Component Breakdown

| Execution Stage | Stage Latency | Cumulative Time | Source Script & Attribution |
| :--- | :--- | :--- | :--- |
| **1. STT (Gnani Prisma REST)** | 1,320.4 ms | 1.32 s | `scripts/voice_loop_timing.py` (synthetic test clip) |
| **2. Dense + Sparse Search** | 215.6 ms | 1.54 s | `scripts/voice_loop_timing.py` (Qdrant `pakkam_chitra`) |
| **3. Cross-Encoder Reranker** | 236.8 ms | 1.77 s | `scripts/voice_loop_timing.py` (BGE-Reranker-v2, top 3) |
| **4. Short Voice Synthesis** | 3,850.0 ms | 5.62 s | `scripts/voice_loop_timing.py` (Gemini 3.5 Flash) |
| **5. Sentence 1 TTS** | 2,795.1 ms | **8.42 s (Proc) / 9.20 s (Wall)** | `scripts/test_sentence_speech.py` (Gnani Timbre REST) |
| *Sentence 2 TTS (Pipelined)* | *3,195.8 ms* | *— (Background)* | Synthesized while Sentence 1 plays |

---

## 5. Confirmation Guardrail Mechanics (`needs_confirmation`)

### Current Implementation
In [`src/schemebot/generate/answer.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/answer.py) (lines 67–75):
`needs_confirmation=True` is triggered if `voice_mode=True` and either:
1. The generated answer string contains any digit (`\d`), or
2. The user's query string contains any recognized scheme keyword (`pm kisan`, `kmut`, `pudhumai penn`, `breakfast scheme`, etc.).

### Proposed Uncertainty-Based Rule (Proposal Only — Not Implemented)
Rather than firing statically on all digits, trigger confirmation only under measured uncertainty:
1. **Marginal Retrieval Confidence:** When the top chunk's cross-encoder rerank score falls in the borderline zone ($0.35 \le score < 0.45$).
2. **Short Transcript Length:** When the STT transcript length is unusually brief ($<15$ characters), indicating potential truncated speech.
3. **Acoustic Confidence:** When the STT provider returns an average token acoustic confidence score below 0.70 (pending provider support).

---

## 6. STT Word Error Rate Details (AI4Bharat Kathbath)

Evaluated via `scripts/gnani_stt_eval.py` on clean read speech from news sentences:
- **Tamil ($n=15$ read-speech clips):**
  - **Raw WER:** **5.2%**
  - **Normalized WER:** **1.7%** (exact: 1.72%)
  - **Median Latency:** 0.95 s
- **Hindi ($n=15$ read-speech clips):**
  - **Raw WER:** **3.7%**
  - **Normalized WER:** **1.7%** (exact: 1.68%)
  - **Median Latency:** 0.92 s

### Definition of "Norm"
Normalized WER applies:
1. Unicode NFC normalization.
2. Conversion to lowercase.
3. Stripping of all punctuation (commas, periods, question marks, exclamation marks, hyphens, quotation marks).
4. Collapsing of multiple spaces into single spaces.
5. Removal of zero-width joiners and non-joiners.

### Clarification on Identical 1.7% Figure
The raw error rates are distinct: Tamil is **5.2%** and Hindi is **3.7%**. After stripping punctuation errors on read speech, the remaining word errors were 1.72% for Tamil and 1.68% for Hindi. Both round to **1.7%** at one decimal place; they are not identical raw outputs.

---

## 7. Departmental Helplines Audit ([`data/contacts.json`](file:///f:/sar.ai%20pr/data/contacts.json))

Audit of all 10 cataloged public schemes in `data/contacts.json`:

| Scheme Name | Helpline Number | Official Source URL / Citation | Verification Status |
| :--- | :--- | :--- | :--- |
| **Atal Pension Yojana** | **1800 1100 69** | `apy-brochure-en:p1` / `https://www.pfrda.org.in` | **Verified** (PFRDA official toll-free) |
| **PM-KISAN** | *None listed* | `https://pmkisan.gov.in` | **Unverified** (`helpline: null`) |
| **Pradhan Mantri Ujjwala Yojana** | *None listed* | `https://www.pmuy.gov.in` | **Unverified** (`helpline: null`) |
| **Kalaignar Magalir Urimai Thittam** | *None listed* | `https://kmut.tn.gov.in` | **Unverified** (`helpline: null`) |
| **Chief Minister's Breakfast Scheme** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |
| **TN Social Welfare Schemes** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |
| **TN Health & Family Welfare** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |
| **TN Higher Education Schemes** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |
| **TN Adi Dravidar & Tribal Welfare** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |
| **TN BC, MBC & Minorities Welfare** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |

*Only Atal Pension Yojana currently has a verified telephone contact. The remaining 9 schemes point only to official portal websites.*

---

## 8. Operational Diagnostics & Sample Answers

### Gemini Quota Reset Window
The earlier note indicating an "18:00 IST / 12:30 UTC" reset was an empirical conjecture based on an API 429 error response header on October 28. Official Google Cloud / Gemini API documentation states that Free Tier daily limits reset on a 24-hour cycle or at midnight UTC / Pacific Time depending on account configuration. There is no official SLA guaranteeing an 18:00 IST reset.

### Sample Answers Status
The 10 sample queries printed in [`docs/review/sample_answers.md`](file:///f:/sar.ai%20pr/docs/review/sample_answers.md) represent raw pipeline outputs. They have **not yet been graded by a human evaluator**. Official human scoring will be executed under Phase 0.3 using [`scripts/answer_eval_summary.py`](file:///f:/sar.ai%20pr/scripts/answer_eval_summary.py).

---

## 9. Release Gate Check & Conclusion

**The branch `feat/prompt-pack-execution` is NOT ready for remote push.**

The following verification gates remain incomplete:
1. **Gate 0.2:** Verified question set (50 checked + 30 held-out) is not yet delivered.
2. **Gate 0.3:** Blind human grading of answers in `docs/review/answer_eval.csv` is not yet completed.
3. **Gate 1.4:** Real conversational and Tanglish speech recordings have not been gathered or tested.
4. **Gate 2.1:** 263 OCR disagreement rows remain unreviewed.

All code and test suites remain functional locally on branch `feat/prompt-pack-execution` with **55 / 55 unit tests passing**. Work will continue locally without pushing until all gates are formally cleared.
