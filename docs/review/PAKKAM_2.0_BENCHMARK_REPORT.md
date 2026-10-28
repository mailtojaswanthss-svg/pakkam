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

## 1. Research Scope & Evaluation Context

Pakkam 2.0 is an experimental research prototype investigating verifiable, citation-grounded question answering over Indian public welfare scheme policy documents in Tamil, Hindi, English, and Tanglish.

All quantitative results in this report are measured from draft questions, read-speech clips, or synthetic tests using committed scripts. In accordance with project integrity guidelines, every reported number states its exact source script, sample size ($n$), and experimental constraints. No numbers are extrapolated or assumed.

---

## 2. Engineering Upgrades Completed

### 1. Fact Cards Design Harness (2 Draft Cards)
- **Source:** [`data/fact_cards.json`](file:///f:/sar.ai%20pr/data/fact_cards.json), [`src/schemebot/generate/fact_cards.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/fact_cards.py)
- **Authorship:** Both cards in `data/fact_cards.json` (Kalaignar Magalir Urimai Thittam and PM-KISAN) were generated as **AI drafts** during development.
- **Verification Rule:** `verified_by` is set to `null` on both unverified draft cards. The app strictly filters out unverified cards at load time via `load_verified_cards()`:
  ```python
  verified = [c for c in raw if c.verified_by and c.verified_by.strip()]
  ```
  Unverified cards are **never served to users**. This behavior is verified by the automated test [`test_load_verified_cards_filters_unverified`](file:///f:/sar.ai%20pr/tests/test_fact_cards.py#L65-L77) in `tests/test_fact_cards.py`.
- **Evaluation:** Evaluated via [`scripts/fact_card_eval.py`](file:///f:/sar.ai%20pr/scripts/fact_card_eval.py) across 4 positive draft queries and 40 unanswerable draft queries.
- **Audio:** Audio clips were generated locally into `data/audio_cache/` using [`scripts/make_card_audio.py`](file:///f:/sar.ai%20pr/scripts/make_card_audio.py). Because `data/audio_cache/` is gitignored, **no audio files exist in git**.

### 2. Claim-Lite Quote and Number Checks (Not Entailment)
- **Source:** [`src/schemebot/generate/claims.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/claims.py), [`tests/test_claims.py`](file:///f:/sar.ai%20pr/tests/test_claims.py)
- **Functionality:** A deterministic string and numerical checker. It verifies exact quotation substring containment within cited chunks, and checks whether extracted numbers, percentages, dates, and frequencies appear in the source passage. If amounts mismatch, it forces `status="INSUFFICIENT_EVIDENCE"`.
- **Limitation:** This is a deterministic string and number check, **not Natural Language Inference (NLI) entailment**. Its real-world effect on hallucination reduction is **not yet measured** (pending blind human evaluation).

### 3. Voice-Loop Latency Measurements (Measured Values Only)
- **Status of Stitched Stage Table:** The previously presented stage table combined numbers from separate runs across different scripts:
  - STT latency (`1,320.4 ms`): Reused from `scripts/gnani_smoke.py` (synthetic test clip).
  - Search latency (`215.6 ms`): Reused from `scripts/ablate_retrieval.py` median.
  - Reranker latency (`236.8 ms`): Reused from `scripts/ablate_retrieval.py` median.
  - Generation latency (`3,850.0 ms`): A rounded figure from an earlier draft run, not captured with timestamps.
  - Sentence 1 TTS (`2,795.1 ms`): Reused from `scripts/test_sentence_speech.py` (Sentence 1 of 3 Tamil sentences).
  Because these stages were stitched from multiple scripts rather than measured simultaneously in one execution, the stitched stage table has been removed.
- **Separately Measured Latency Benchmarks:**
  - STT single-clip latency: **1,320.4 ms** on `synthetic_smoke_ta.wav` (`scripts/gnani_smoke.py`).
  - First-stage hybrid search: median **215.6 ms** (`scripts/ablate_retrieval.py`, $n=194$).
  - BGE-Reranker-v2: median **236.8 ms** (`scripts/ablate_retrieval.py`, $n=194$).
  - Sentence 1 TTS TTFA: **2,795.1 ms** (`scripts/test_sentence_speech.py`, $n=3$ sentences).
- **Target Evaluation:** **The project target of 5.0 s was NOT met.**
- **Baseline Note:** The earlier reported sequential baseline of 14.07 s was an estimated composite of medians from separate scripts (STT 1.32s + Search 0.22s + Rerank 0.24s + Generation 6.30s + Full TTS 5.99s = 14.07s). Because it was not measured on the same run, no percentage comparison is claimed.

### 4. Short Voice Answer Path
- **Source:** `VOICE_SYSTEM_PROMPT` in [`src/schemebot/generate/prompt.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/prompt.py), `voice_mode` in [`src/schemebot/generate/answer.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/answer.py)
- **Functionality:** Restricts answers to 2 sentences, strips markdown formatting, spells out currency in Indic words, restricts retrieval context to top 3 chunks, and bypasses the secondary LLM verifier when no numbers or dates are generated.
- **Quota Impact:** Offers up to 50% fewer LLM calls on non-numeric questions; actual savings across an operational query distribution are **not measured**.

### 5. Fast Sources-First Endpoint
- **Source:** `POST /ask/sources` in [`src/schemebot/api/routes.py`](file:///f:/sar.ai%20pr/src/schemebot/api/routes.py)
- **Functionality:** Executes hybrid dense + sparse retrieval and BGE reranking to return top 3 cited passages and document metadata in **~300 ms** with 0 LLM calls.

### 6. BhashaShield Speech Retrieval Test
- **Source:** [`scripts/speech_error_test.py`](file:///f:/sar.ai%20pr/scripts/speech_error_test.py), [`docs/review/LANGUAGE_TABLE.md`](file:///f:/sar.ai%20pr/docs/review/LANGUAGE_TABLE.md)
- **Evaluation Dataset (31 Clips):**
  - 15 Tamil read-speech clips from AI4Bharat Kathbath.
  - 15 Hindi read-speech clips from AI4Bharat Kathbath.
  - 1 synthetic boundary plumbing clip (`synthetic_smoke_ta.wav`) used during initial setup.
- **Definition of "Target Document" and "Target Page":**
  Kathbath clips are recordings of general news sentences, not citizen scheme queries. To evaluate how STT transcription errors affect retrieval, `scripts/speech_error_test.py` defines the "target document" and "target page" as the top document (`doc_id`) and top page (`page_start`) retrieved when querying the clean reference transcript.
  - **Document Match Rate (90.3%, 28/31):** The STT transcript retrieved the exact same top document as the clean reference text.
  - **Page Match Rate (87.1%, 27/31):** The STT transcript retrieved the exact same top page as the clean reference text.
- **Limitations:** Tests read-speech news audio only. **Tanglish queries and real consented field voice recordings are completely untested.**

### 7. Model-Down Fallback
- **Source:** [`src/schemebot/generate/answer.py`](file:///f:/sar.ai%20pr/src/schemebot/generate/answer.py)
- **Functionality:** Returns top 3 retrieved passages with official helpline/portal contacts under `status="MODEL_UNAVAILABLE"` when Gemini returns a 429 quota exhaustion or network timeout.

### 8. Custom Secrets & Integrity Audit
- **Source:** [`scripts/scan_git_secrets.py`](file:///f:/sar.ai%20pr/scripts/scan_git_secrets.py)
- **Result:** Custom Python regex scanner confirmed **0 API keys and 0 audio files** across 151 commits. Certified scanners (`gitleaks`, `trufflehog`) are not installed on this system. Fresh clone verification is pending.

---

## 3. Corpus Composition & OCR Disagreements

### Explanation of 4,449 Vectors vs 2,918 Chunks
- In the Qdrant collection `pakkam_chitra`, there are **4,449 points**, each corresponding to a single chunk (`chunk_id`) indexed across all 18 official documents (2,688 pages).
- The earlier reference to "2,918 chunks" was an intermediate chunk count from a partial indexing run before all sections and documents were finalized. There are **4,449 chunks** in the final index.

### Explanation of the 263 OCR Disagreement Rows
- Each row in [`docs/review/ocr_disagreements.csv`](file:///f:/sar.ai%20pr/docs/review/ocr_disagreements.csv) represents a page where the set of numbers extracted by Tesseract differed from the set of numbers extracted by Chitrapathak-2 Crop Mode.
- **Concrete Example (Row 14):**
  - **Document:** `tn-hedu-policy-note-2024-ta`, **Page:** `33` (the Pudhumai Penn policy note page).
  - **Tesseract-only numbers:** `3.40; 4.60; 4000` (Tesseract misread `ரூ.1,000` as `4000`).
  - **Chitrapathak-only numbers:** `1.60; 1000; 3.10` (Chitrapathak-2 correctly read `1000`).
  - Because Tesseract extracted `4000` and Chitrapathak extracted `1000`, this page was logged as a disagreement row. The 263 rows represent pages requiring individual manual verification.

---

## 4. Quantitative Benchmarks & Evaluation Scope

| Benchmark Area | Script & Sample Size | Result | Baseline & Scope Constraints |
| :--- | :--- | :--- | :--- |
| **Hybrid OCR Problem Pages** | `scripts/run_hybrid_ocr.py`<br>($n=7$ cherry-picked pages) | Chitrapathak-2: **7/7 (100.0%)**<br>Tesseract: **0/7 (0.0%)** | **Selection bias:** The 7 pages were chosen because Tesseract failed on them. This is not a random corpus sample. |
| **OCR Crop Speedup** | `scripts/run_hybrid_ocr.py`<br>($n=500$ currency pages) | **~12.0s per page**<br>(Crop Mode) | Full-page Chitrapathak-2 on GPU was **~95s**. The earlier recorded **6 to 7 min per page** was on GPU; the difference with ~95s remains **unreconciled without a formal run log**. |
| **Retrieval Recall@5** | `scripts/ablate_retrieval.py`<br>($n=194$ draft queries) | Hybrid + Reranker: **98.7%**<br>Hybrid alone: **94.8%** | Evaluated on draft questions only; no blind held-out question set has been tested. |
| **Refusal Calibration (0.35)** | `scripts/evaluate_refusal_curve.py`<br>($n=194$ draft queries) | **87.1%** Routing Accuracy<br>**92.5%** Unanswerables Refused | **14.3%** false refusal rate on draft queries. Threshold is the current default, not calibrated on a verified set. |
| **Fact Cards Precision** | `scripts/fact_card_eval.py`<br>($n=4$ pos, 40 unanswerables) | **100.0%** Precision (4/4)<br>**0** False Matches (0/40) | Evaluated on 2 AI draft cards. Unverified cards are filtered out (`verified_by: null`). |
| **Speech Error Retrieval** | `scripts/speech_error_test.py`<br>($n=31$ clips: 15 TA, 15 HI, 1 synth) | Doc Match: **90.3% (28/31)**<br>Page Match: **87.1% (27/31)** | Read speech news sentences only. Measures match against clean reference retrieval. Tanglish/conversational untested. |
| **STT Word Error Rate** | Gnani Prisma REST<br>($n=15$ Tamil, $n=15$ Hindi) | Tamil: **Raw 5.2%** (Norm 1.7%)<br>Hindi: **Raw 3.7%** (Norm 1.7%) | Read speech only. "Norm" removes punctuation and spaces. Identical 1.7% is coincidental rounding (1.72% vs 1.68%). |
| **Custom Secrets Audit** | `scripts/scan_git_secrets.py`<br>($n=151$ commits, 239 files) | **0 Secrets Detected**<br>**0 Audio Files in Git** | Custom regex scan. `gitleaks` unavailable. Fresh clone test pending. |

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
Normalized WER applies Unicode NFC normalization, lowercase conversion, punctuation stripping, whitespace collapsing, and zero-width character removal.

### Clarification on Identical 1.7% Figure
The raw error rates are distinct: Tamil is **5.2%** and Hindi is **3.7%**. After stripping punctuation errors on read speech, the remaining word errors were 1.72% for Tamil and 1.68% for Hindi. Both round to **1.7%** at one decimal place; they are not identical raw outputs.

---

## 7. Departmental Helplines Audit ([`data/contacts.json`](file:///f:/sar.ai%20pr/data/contacts.json))

Audit of all 10 cataloged public schemes in `data/contacts.json`:

| Scheme Name | Helpline Number | Official Source URL / Citation | Verification Status |
| :--- | :--- | :--- | :--- |
| **Atal Pension Yojana** | **1800 1100 69** | `apy-brochure-en:p1` / `https://www.pfrda.org.in` | **Found in brochure, current number to be confirmed by a person** |
| **PM-KISAN** | *None listed* | `https://pmkisan.gov.in` | **Unverified** (`helpline: null`) |
| **Pradhan Mantri Ujjwala Yojana** | *None listed* | `https://www.pmuy.gov.in` | **Unverified** (`helpline: null`) |
| **Kalaignar Magalir Urimai Thittam** | *None listed* | `https://kmut.tn.gov.in` | **Unverified** (`helpline: null`) |
| **Chief Minister's Breakfast Scheme** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |
| **TN Social Welfare Schemes** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |
| **TN Health & Family Welfare** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |
| **TN Higher Education Schemes** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |
| **TN Adi Dravidar & Tribal Welfare** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |
| **TN BC, MBC & Minorities Welfare** | *None listed* | `https://www.tn.gov.in` | **Unverified** (`helpline: null`) |

*No telephone helpline has been added from memory. Only Atal Pension Yojana has a number documented in an official brochure; all other 9 schemes remain unverified.*

---

## 8. Operational Diagnostics & Sample Answers

### Gemini Quota Reset Window
The daily reset time for the Gemini Free Tier is **unverified**. There is no official SLA guaranteeing a specific reset hour.

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

All code and test suites remain functional locally on branch `feat/prompt-pack-execution` with **55 / 55 unit tests passing**. All updates in this document reflect the measured state and recorded limitations of the research prototype.
