# PAKKAM 2.0: SYSTEM BENCHMARK, EXECUTION AUDIT & ROADMAP REPORT

> **Document Status:** Working Engineering Report  
> **Repository:** `mailtojaswanthss-svg/pakkam`  
> **Active Branch:** `feat/prompt-pack-execution` (Local Backup Only)  
> **Date of Evaluation:** 29 October 2026  
> **Test Suite Health:** **476 Passed, 10 Deselected** across full test suite (`pytest -q`) | `ruff` clean (0 errors) | `mypy` strict clean (0 errors across 63 files)  
> **Git Secrets Audit:** **0 secrets found** across full history (158 commits) and 258 tracked files  

---

## 1. Project Overview & Deadlines

Pakkam is an Indic voice-first, citation-grounded Retrieval-Augmented Generation (RAG) assistant purpose-built to answer citizen inquiries regarding public welfare schemes across **Tamil**, **Hindi**, and **English**.

### 1.1 Submission & Engineering Timelines
To guarantee execution discipline without operational instability, the roadmap is aligned to three milestones:
1. **Code Freeze:** **Monday 2 November 2026** — All code changes frozen for demonstration video capture.
2. **Demonstration Video Delivery:** **Tuesday 3 November 2026** — Video recorded demonstrating sources pre-fetch, Indic speech synthesis, and graceful fallback.
3. **Own Internal Target:** **Friday 6 November 2026** — Final code and documentation review.
4. **Hard Submission Deadline:** **Tuesday 10 November 2026, 11:59 PM IST** — Final submission handover.

### 1.2 Pragmatic Scope Prioritization

- **Completed Pre-Freeze Scope:**
  - **Step 4 (Fast Sources-First):** Client pre-fetch endpoint (`POST /ask/sources`) returning top 3 official document excerpts in 421.8 ms mean latency.
  - **Step 4B (Query Understanding & Scheme Aliases):** Deterministic cleanup (`clean_query`, `strip_fillers`, `normalize_tanglish`), scheme alias database (`data/scheme_aliases.json`), and alias expansion matcher (`AliasMatcher`). Development check (n=20, not held-out): 100% Top-5 recall, 5% false refusal rate, 379.0 ms average latency.
  - **Step 5 (Sentence-by-Sentence Speech Synthesis):** Pipelined TTS with abbreviation protection (`Rs.`, `ரூ.`, `रु.`, `No.`, `Dr.`), Indic amount spelling (`spell_amounts` -> *ஆயிரம் ரூபாய்*), and client-side playback queue with instant abort control (`AbortController.abort()`).
  - **Step 6 (Never Fail Visibly):** Graceful fallback on LLM 429 quota exhaustion or timeout. Returns top 3 retrieved passages, verified official contacts, and toll-free helpline with wording: *"The answering model is currently busy. Here is what the official document states:"*.
  - **Step 7 (Gnani-Centred Voice Uncertainty Confirmation):** Rule uses retrieval score only; Prisma returns no confidence (verified from codebase implementation and evaluation logs). Ambiguous band $[0.30, 0.40]$ triggers spoken confirmation prompt. Prompts citizen in 4 languages (*"I heard {scheme}. Is that right?"* / *"நான் {scheme} என்று கேட்டேன். சரியா?"*). The "under 3 words" rule was dropped per empirical guidance.
  - **Step 8 (Citizen Feedback Loop):** `POST /feedback` endpoint writing ratings, status, and critique to append-only gitignored `logs/feedback.jsonl` + inspection harness in `scripts/review_feedback.py`.
  - **Step 9 (Voice Evidence Report):** Auto-compilation of `docs/GNANI_VOICE_REPORT.md` from raw empirical logs with 0 live API calls.
  - **Step 10 (Verification Sweep):** Full test suite execution (476 passed, 10 deselected), ruff clean, mypy strict clean, secrets scan clean, Word report synchronized.

- **Deferred Post-Submission Enhancements:**
  - Local SLM Quantization (Gemma-2-2B / Qwen2.5 4-bit local GPU fallback).
  - WebSocket / SSE token-level streaming audio pipeline.
  - Stateful multi-turn conversational session memory.

---

## 2. Implementation Audit Matrix

| Milestone / Component | Implementation Details | Measured Metric & Empirical Proof | Source Script / Evidence |
| :--- | :--- | :--- | :--- |
| **Git Safety & Audit** | Full working tree backed up. Secrets scan across 158 commits and 258 tracked files. | **0 API keys and 0 audio files** in git history. Clean tree. | `scripts/scan_git_secrets.py` |
| **Step 4: Fast Sources-First** | Client pre-fetch endpoint (`POST /ask/sources`) returning top 3 official document excerpts in parallel. | **421.8 ms mean latency** ($n=10$, median: 352.9 ms, max: 1115.5 ms). | `scripts/benchmark_instant_sources.py`<br>`docs/review/INSTANT_FEEL_BENCHMARK.md` |
| **Step 4B: Query Understanding** | Deterministic normalizer, scheme aliases (`data/scheme_aliases.json`), near-threshold clarification ($[0.30, 0.35)$). | **Development check, not evidence** ($n=20$, not held-out): **100.0% Top-5 Recall (20/20)**, **5.0% False Refusal Rate**, **379.0 ms average latency**. | `scripts/paraphrase_eval.py`<br>`docs/review/PARAPHRASE_EVAL_REPORT.md` |
| **Step 5: Sentence Speech Synthesis** | Abbreviation-safe sentence splitter (`Rs.`, `ரூ.`), Indic amount spelling (`spell_amounts`), client playback queue & instant abort. | **4 / 4 unit tests pass**. Verified sentence queueing with zero audio overlap. | `src/schemebot/voice/sentence_speaker.py`<br>`web/assets/chat.js`<br>`tests/test_sentence_speech.py` |
| **Step 6: Never Fail Visibly** | Model-busy fallback on 429 quota exhaustion or network timeout; returns top 3 passages + verified helpline. | `status="MODEL_UNAVAILABLE"`, `path="fallback"`; rendered gracefully in UI with tap-to-call helpline. | `src/schemebot/generate/messages.py`<br>`src/schemebot/generate/answer.py`<br>`web/assets/chat.js` |
| **Step 7: Voice Uncertainty Confirmation** | Rule uses retrieval score only; Prisma returns no confidence (verified from codebase implementation and evaluation logs). Prompts citizen: *"I heard {scheme}. Is that right?"*. | **4 / 4 unit tests pass**. Under 3 words rule dropped. | `src/schemebot/api/main.py`<br>`src/schemebot/voice/stt.py`<br>`tests/test_voice_step7.py` |
| **Step 8: Citizen Feedback Loop** | `POST /feedback` endpoint recording rating, status, and critique without audio. | **2 / 2 unit tests pass**. Stores status, language, timings, and thumbs rating by default; question text and critique stored ONLY if citizen opts in via checkbox (default off). | `src/schemebot/api/main.py`<br>`scripts/review_feedback.py`<br>`tests/test_feedback.py` |
| **Step 9: Voice Evidence Report** | Automated compilation of voice benchmark metrics from empirical logs with 0 live API calls. | Compiled `docs/GNANI_VOICE_REPORT.md` capturing STT, TTS, Tanglish check, and safety guards. | `scripts/generate_voice_report.py`<br>`docs/GNANI_VOICE_REPORT.md` |
| **Step 10: Final Verification** | Full test suite execution, ruff lint, mypy strict type check, secrets audit, docx generation. | **476 passed, 10 deselected**. Ruff clean. Mypy clean. | `tests/`<br>`scripts/generate_docx_report.py` |
| **Gate 1.4: Tanglish Text Check** | 10 synthetic code-mixed text queries evaluated against local Qdrant collection (`pakkam_chitra`). | **Synthetic check (n=10, written by AI)**: **90.0% Top-5 Recall (9/10)**, **70.0% Top-1 Accuracy**, **486.8 ms average latency**. Miss `t03` was Kalaignar Magalir scheme. | `scripts/eval_tanglish_clips.py`<br>`docs/review/TANGLISH_EVAL_REPORT.md` |
| **Semantic Vector Cache** | Exact match cache at cosine $\ge 0.96$. | **Wrong-match rate unmeasured**; **disabled for demo** (`answer_cache_size = 0`). | `src/schemebot/generate/cache.py`<br>`src/schemebot/config.py` |
| **Official Helplines Status** | In `data/contacts.json`, only Atal Pension Yojana has a cited brochure source URL. | **Other 9 schemes remain null/unverified** pending manual source URL confirmation. | `data/contacts.json`<br>`tests/test_contacts.py` |
| **OCR Disagreements Audit** | Complete classification of 263 numerical discrepancy pages between Tesseract & Chitrapathak-2. | **70.0% order dates, 25.9% amounts, 1.9% tables, 2.3% digits**. Evaluated crop mode on 7 problem pages (7/7). | `scripts/analyze_disagreements.py`<br>`docs/review/OCR_DISAGREEMENTS_ANALYSIS.md` |
| **Claim Guardrails** | Deterministic quote, amount, date, and periodicity containment verification in `claims.py`. | **5 / 5 unit tests pass**. Rejects out-of-context amounts and unsupported assertions. | `tests/test_claims.py` |

---

## 3. Deep Dive into Empirical Metrics

### 3.1 Step 3: LLM Provider & Reasoning Mode Latency Comparison ($n=3$)
*Sample:* 3 draft questions (`q001`: Pudhumai Penn amount, `q004`: CMCHIS hospital eligibility, `q002`: Moovalur marriage assistance) with live claim verification:

| Operational Mode | Average Latency | Output Chars | Claim Check Pass Rate |
| :--- | :---: | :---: | :---: |
| **Voice Mode (`thinking="low"`)** | **6,571.3 ms** | **132 chars** | **100.0% (3/3)** |
| **Normal Mode (`thinking="low"`)** | **12,962.3 ms** | **330 chars** | **100.0% (3/3)** |
| **Normal Mode (`thinking="medium"`)** | **41,434.5 ms** | **248 chars** | **100.0% (3/3)** |

---

### 3.2 Step 4: Fast Sources-First Latency Breakdown ($n=10$)
*Sample:* 10 cold-retrieval queries executed through local filesystem Qdrant index (`pakkam_chitra`) via `scripts/benchmark_instant_sources.py` (0 LLM calls):

| Retrieval Component | Mean Duration | Median Duration | Max Duration | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **Hybrid Search (Dense + Sparse)** | 273.1 ms | 205.6 ms | 931.8 ms | BGE-M3 Dense (1024-d) + learned lexical sparse |
| **Neural Cross-Encoder Rerank** | 148.6 ms | 145.0 ms | 183.2 ms | BGE-Reranker-v2-m3 on top candidates |
| **Total `/ask/sources` Latency** | **421.8 ms** | **352.9 ms** | **358.9 ms** | Min: 311.1 ms, Max: 1,115.5 ms |

---

### 3.3 Gate 1.4: Tanglish Text Retrieval Check (Synthetic, n=10, Written by AI)
*Sample:* 10 synthetic code-mixed text queries evaluated via `scripts/eval_tanglish_clips.py` (0 LLM calls, 0 audio, 0 STT):

| ID | Synthetic Tanglish Text Query | Target Scheme | Top-1 Match | Top-5 Match | Latency |
| :---: | :--- | :--- | :---: | :---: | :---: |
| `t01` | *college padikira ponnungalukku monthly 1000 scheme* | Higher Education | **Yes** | **Yes** | 1,188.9 ms |
| `t02` | *maruthuva kaapeedu card apply panna annual income limit evalo?* | CMCHIS | No | **Yes** | 414.4 ms |
| `t03` | *kudumbathula oru penukku 1000 tharanga la adhu epdi apply panradhu?* | **Kalaignar Magalir Urimai Thittam** | **No** | **No** | 374.2 ms |
| `t04` | *atal pension scheme la 60 age appo 5000 pension varuma?* | Atal Pension Yojana | **Yes** | **Yes** | 405.2 ms |
| `t05` | *vivasayigalukku 6000 kidaikira pm kisan scheme la ekyc compulsory-aa?* | PM-KISAN | **Yes** | **Yes** | 431.2 ms |
| `t06` | *free gas cylinder connect panna pm ujjwala scheme apply panna documents enna thevai?* | PM Ujjwala Yojana | **Yes** | **Yes** | 425.7 ms |
| `t07` | *govt school pasangalukku kaalai unavu thittam entha class varaikkum tharanga?* | Breakfast Scheme | No | **Yes** | 421.4 ms |
| `t08` | *moovalur ramamirtham thirumana nala thittam marriage scheme amount evalo?* | Social Welfare | **Yes** | **Yes** | 370.7 ms |
| `t09` | *sc st students hostel allowance scholarship eligibility enna?* | Adi Dravidar Welfare | **Yes** | **Yes** | 424.5 ms |
| `t10` | *bc mbc welfare hostel admission process rules enna?* | BC, MBC Welfare | **Yes** | **Yes** | 411.4 ms |

**Empirical Summary:**
- **Top-1 Retrieval Accuracy:** **7 / 10 (70.0%)**
- **Top-5 Retrieval Recall:** **9 / 10 (90.0%)**
- **Average Search Latency:** **486.8 ms**
- **Miss Note:** Query `t03` missed because the colloquial question lacked the keyword 'magalir'.
- **Gate 1.4 Status:** **UNTESTED** (needs consented real recordings).

---

### 3.4 Step 4B: Query Understanding Sanity Check ($n=20$)
*Sample:* 20 developer-authored queries across 5 schemes evaluated via `scripts/paraphrase_eval.py` (0 LLM calls):

- **Status:** **Development check, not evidence** (queries were written after the aliases and are not held-out).
- **Top-5 Retrieval Recall:** **100.0% (20 / 20)**
- **Top-1 Scheme Accuracy:** **85.0% (17 / 20)**
- **False Refusal Rate ($< 0.35$):** **5.0% (1 / 20)** *(Query `p20` routed to candidate clarification)*
- **Average Pipeline Latency:** **379.0 ms**

---

## 4. Strategic Opportunities: 7 Enhancements for Production Hardening

| # | Strategic Opportunity | Current State in System | Production Benefit | Execution Status |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Independent Blind Human Rubric Grading (Gate 0.3)** | 3 answers printed; 0 scored by independent bilingual human panel. | Evaluates factual grounding against official text against official source text. Scored on `number_correct`, `citation_supports`, `unsupported_claim`. | Ready for panel execution on `data/eval/questions.jsonl`. |
| **2** | **Acoustic & Tanglish Field Audio (Gate 1.4)** | Evaluated on AI4Bharat read speech (WER: 5.2% Ta, 3.7% Hi) and 10 synthetic text queries. | Validates resilience to street background noise, distance, and heavy colloquial Tanglish. | **Gate 1.4 UNTESTED** (needs consented real recordings). |
| **3** | **Semantic Vector Cache** | Repeated questions previously ran full neural retrieval & LLM (~7–13s). | Recurring inquiries return in **< 50 ms with 0 token cost**, conserving daily quota. | **Implemented in `cache.py`. Wrong-match rate unmeasured; disabled for demo (`answer_cache_size = 0`)**. |
| **4** | **Official Helplines Ingestion** | Only Atal Pension Yojana has a cited brochure source URL. | Directs citizens to official human authorities on fallback or refusal. | **9 of 10 schemes remain null/unverified** pending manual source URL confirmation. |
| **5** | **OCR Disagreements Audit** | 263 pages showed numerical divergence between Tesseract & Chitrapathak-2. | Audit script categorized 263 numerical divergence pages (70% order dates, 25.9% amounts). | **Categorized in `docs/review/OCR_DISAGREEMENTS_ANALYSIS.md`**. |
| **6** | **Local SLM Fallback** | Gemini Free Tier quota (~20 req/day) creates operational bottleneck. | Local execution via 4-bit Gemma-2-2B or Qwen2.5 on local GPU/Colab for zero-cost failover. | Architecture documented in `STREAMING_DESIGN_NOTE.md`; deferred to post-submission. |
| **7** | **SSE / WebSocket Audio Streaming** | Gnani Timbre HTTP POST operates synchronously per sentence. | Token generation and audio chunk synthesis execute concurrently, driving Time-to-First-Audio (TTFA) below 1.5 seconds. | Architecture documented; deferred to post-submission. |

---

## 5. Formal Release Gate Audit Checklist

| Gate ID | Verification Domain | Measured Status | Release Verdict |
| :---: | :--- | :--- | :---: |
| **Gate 0.1** | Code Hygiene, Unit Tests & Secrets Scan | **476 Passed, 10 Deselected** across full test suite (`pytest -q`)<br>`ruff` clean \| `mypy` strict clean \| 0 Secrets in Git History | **PASSED** |
| **Gate 0.2** | Verified Question Set (50 checked + 30 held-out) | 194 Draft Questions evaluated | **PENDING USER DELIVERY** |
| **Gate 0.3** | Blind Bilingual Human Rubric Grading | 3 Answers printed; scoring panel pending | **PENDING HUMAN PANEL** |
| **Gate 1.1** | Hybrid Retrieval Recall@5 $\ge$ 95% | **98.7% Recall@5** on draft set ($n=194$) | **PASSED (Draft Set)** |
| **Gate 1.2** | Refusal Routing Accuracy & Threshold Curve | **87.1% routing accuracy** at 0.35 threshold | **PASSED (Draft Set)** |
| **Gate 1.3** | STT Accuracy & Speech Error Retrieval | **90.3% doc / 87.1% page match** on Kathbath ($n=31$) | **PASSED (Read Speech)** |
| **Gate 1.4** | Conversational & Tanglish Spoken Query Testing | No real phone audio evaluated; text check only | **UNTESTED** |
| **Gate 2.1** | OCR Numeral Accuracy on Problem Pages | **100.0% (7/7)** on problem crops ($n=7$) | **PARTIAL (7 pages selected as Tesseract failures; 263 not reviewed)** |
| **Gate 3.1** | Perceived Time-to-First-Evidence (< 1.0s) | **median 353 ms; 1 of 10 runs 1.1 s** ($n=10$) | **PASSED** |
| **Gate 3.2** | End-to-End Voice Loop Latency (< 5.0s) | Stitched $n=1$: 9.20s \| Sentence pipelining active | **TARGET NOT MET** |

---

*Report authored locally on branch `feat/prompt-pack-execution`. All 476 unit and integration tests passing.*
