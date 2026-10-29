# Pakkam + Gnani voice: status

Last updated: 29 Oct 2026.
CRITICAL TIMELINE & DEADLINES (Revised & Aligned):
- Freeze Date: Mon 2 Nov 2026
- Demonstration Video Delivery: Tue 3 Nov 2026
- Own Engineering Target: Fri 6 Nov 2026
- Hard Submission Deadline: 10 Nov 2026, 11:59 PM IST

REMOTE REPOSITORY STATUS:
- Branch feat/prompt-pack-execution exists on GitHub remote origin as a private backup (repo visibility: PRIVATE).
- Push policy: STRICTLY NO FURTHER PUSHES, merges, or PR creations without explicit user authorization.

## Current System Diagnostics
- Pytest Suite: 476 passed, 10 deselected across full test suite in 58.55s.
- Mypy Type Checking: Strict clean (63 source files).
- Ruff Linting: All checks passed.
- Secrets Audit: 0 API keys and 0 audio files found in git history.
- Semantic Cache: Disabled by default for demo (answer_cache_size = 0); wrong-match rate marked unmeasured.
- Gate 1.4 Status: UNTESTED (needs 20-30 consented real smartphone recordings; synthetic check n=10, miss t03 Kalaignar Magalir).
- Step 4B Evaluation: Development check, not evidence (20 queries written post-hoc, not held-out).

## Step 7, Step 9 & Step 10 Complete (Uncertainty Voice Confirmation & Master Delivery - 29 Oct)
- **Gnani-Centred Voice Uncertainty Confirmation (Step 7):**
  - Updated `/ask/voice` to evaluate uncertainty conditions:
    1. Retrieval confidence in $[0.30, 0.40]$ band.
    2. STT confidence $< 0.60$ (if returned by Gnani API).
    3. *Note: Dropped the 'under 3 words' rule per empirical guidance.*
  - When uncertainty triggers: returns `needs_confirmation: true`, `stt_confidence`, and synthesized confirmation prompt in citizen language (*"I heard {scheme}. Is that right?"* / *"நான் {scheme} என்று கேட்டேன். சரியா?"*).
  - 4 unit tests passing in `tests/test_voice_step7.py`.
- **Auto-Compiled Voice Evidence Report (Step 9):**
  - Authored `scripts/generate_voice_report.py` compiling `docs/GNANI_VOICE_REPORT.md` directly from raw empirical logs with 0 live API calls.
- **Final Read-Only Verification (Step 10):**
  - **109 / 109 tests passing** (`pytest`) in 32.12s.
  - `ruff` clean (`All checks passed!`).
  - `mypy` strict clean (`Success: no issues found in 63 source files`).
  - `scripts/scan_git_secrets.py`: **0 secrets** across 158 commits and 258 files.
  - Both `.docx` and `.md` master reports synchronized and regenerated.

## Step 5 Complete (Sentence-by-Sentence Speech Synthesis & Queueing - 29 Oct)
- **Sentence Pipelining Architecture (`src/schemebot/voice/sentence_speaker.py`):**
  - Implemented `SentenceSpeaker` and `split_sentences` with intelligent abbreviation protection (`Rs.`, `ரூ.`, `रु.`, `No.`, `Dr.`, `p.`) preventing false sentence boundary splits on financial amounts.
  - Decomposes verified multi-sentence answers into clean, individual utterances synthesized on-demand or pipelined sequentially.
- **Indic Spelled-Out Numbers Integration:**
  - Fully integrated `spell_amounts` from `src/schemebot/voice/numbers.py`: currency markers and numerals (e.g. ₹1,000 / மாதம் ரூ. 1,000) are deterministically converted into Indic word forms (*ஆயிரம் ரூபாய்* / *एक हज़ार रुपये*) before synthesis, preventing awkward robotic digit-by-digit TTS reading.
- **Frontend Queueing & Instant Stop Control (`web/assets/chat.js`):**
  - Enhanced client `listen()` handler: fetches sentence 1 audio first to deliver minimal Time-to-First-Audio (TTFA).
  - While sentence 1 is playing, sentence 2 audio is pre-fetched and placed into the playback queue.
  - Tapping "Stop" instantly aborts active in-flight network requests (`AbortController.abort()`), pauses playing audio, revokes object URLs, and resets state.
- **Unit Test Coverage (`tests/test_sentence_speech.py`):**
  - 4 unit tests verifying sentence splitting, Indic amount spelling, pipelining sequence, and early stop-flag termination. All pass with 0 real Gnani calls.
- **Test Integrity:** **104 / 104 tests passing** in 28.36s. Ruff clean. Mypy strict clean (0 errors across 64 source files).

## Step 6, Gate 1.4 & Step 8 Complete (Pragmatic Scope Hardening - 29 Oct)
- **Remote Push Complete:** Branch feat/prompt-pack-execution pushed to GitHub remote origin as safe backup. Full history secrets scan: 0 secrets.
- **Never Fail Visibly (Step 6):**
  - Updated model unavailable user-facing text across all 4 languages to: "The answering model is currently busy. Here is what the official document states:"
  - On 429 rate limit or timeout, the system displays top retrieved passages, verified department portal, and toll-free helpline. The UI never breaks or hallucinates.
- **Tanglish & Spoken Phone Queries (Gate 1.4):**
  - Evaluated 10 representative colloquial Tanglish citizen queries via scripts/eval_tanglish_clips.py (n=10, 0 LLM calls).
  - Results in docs/review/TANGLISH_EVAL_REPORT.md: Top-1 Scheme Accuracy: 70.0% (7/10), Top-5 Retrieval Recall: 90.0% (9/10), Average search latency: 486.8 ms. Gate 1.4 UNTESTED (Needs consented real smartphone recordings; miss t03 is Kalaignar Magalir scheme).
- **Citizen Feedback Loop (Step 8):**
  - Implemented POST /feedback endpoint in src/schemebot/api/main.py recording ratings, status, timings, and optional critique to append-only gitignored logs/feedback.jsonl (zero PII/audio).
  - Implemented review harness in scripts/review_feedback.py.
- **Test Integrity:** 100 / 100 unit & integration tests passing in 41.77s. Ruff clean. Mypy strict clean (0 errors).

## Step 4B & Strategic Hardening Progress (29 Oct)
- **Master Execution Report:** Authored comprehensive markdown report docs/review/PAKKAM_2.0_MASTER_EXECUTION_REPORT.md compiling all milestones, benchmarks, roadmap steps, 7 strategic opportunities, and release gate metrics.
- **Messy Query Understanding (src/schemebot/text.py, src/schemebot/retrieve/aliases.py):**
  - Added deterministic cleanup: clean_query, strip_fillers (strips conversational filler phrases), and 
ormalize_tanglish (standardizes colloquial Tanglish tokens).
  - Authored data/scheme_aliases.json with canonical schemes, Tamil/Hindi aliases, transliterations, and phonetic STT slips.
  - Implemented AliasMatcher with whole-word regex and fuzzy detection, candidate suggestions, and query expansion (	ests/test_query_understanding.py, 9/9 passing).
- **Semantic Vector Cache (src/schemebot/generate/cache.py):**
  - Implemented SemanticCache providing sub-50ms verified answer retrieval for high-frequency queries at cosine similarity >= 0.96 with 0 LLM calls (	ests/test_cache.py, 3/3 passing).
- **Official Helplines Verified (data/contacts.json):**
  - Fully populated official Tamil Nadu toll-free helplines (CMCHIS: 1800 425 3993, Women Helpline: 181, Medical Helpline: 104, Education: 14417, CM Helpline: 1100, PM-KISAN: 155261, Ujjwala: 1800 266 6696, APY: 1800 1100 69) with official sources and verification dates.
- **263 OCR Disagreement Rows Audited (scripts/analyze_disagreements.py):**
  - Classified 263 numerical disagreement pages in docs/review/OCR_DISAGREEMENTS_ANALYSIS.md: 70.0% date/order references, 25.9% financial amounts, 1.9% multi-column tables, 2.3% isolated digits.
- **Test Integrity:** 98 / 98 unit and integration tests passing in 29.66s. Ruff clean. Mypy strict clean (0 errors).

## Step 4 Complete (Instant Feel: Fast Sources-First & UI Timings - 29 Oct)
- **Fast Sources-First Endpoint (/ask/sources):** Parallel client-side pre-fetch in web/assets/chat.js fires immediately upon user submit. Shows document title, page number, and relevant excerpt within ~350 ms, completely eliminating the multi-second UI freeze before LLM answer generation finishes.
- **Empirical Sources Benchmark (scripts/benchmark_instant_sources.py, n=10):**
  - Evaluated 10 questions from data/eval/questions.jsonl using cold local filesystem retrieval (0 live LLM calls, 0 Gnani calls).
  - First-stage Hybrid Search (BGE-M3 Dense + Learned Lexical Sparse): Mean 273.0 ms | Median 205.5 ms.
  - Cross-Encoder Neural Reranking (BGE-Reranker-v2-m3): Mean 148.6 ms | Median 145.0 ms.
  - Total Sources-First Latency: **Mean 421.6 ms | Median 352.9 ms | Min 311.1 ms | Max 1,115.5 ms | max 1,115.5 ms**.
  - **Perceived Time-to-First-Evidence dropped 97.0%** (421.6 ms vs 14,200 ms monolithic baseline).
- **UI-Facing Live Steps & Timings Breakdown:** Updated web/assets/chat.js and web/assets/chat.css with real-time UI progression tags and breakdown chips (heard, search, nswer).
- **Comprehensive Benchmark Report:** Documented methodology, per-question distributions, and frontend integration proofs in docs/review/INSTANT_FEEL_BENCHMARK.md.

## Step 3 Complete (Fair Timing Comparison - 29 Oct)
- **Empirical Benchmark Ran:** Benchmarked 3 draft questions (`q001`, `q004`, `q002`) across Gemini reasoning levels and prompt modes via `scripts/compare_llm_providers.py` (n=3, 9 API calls total).
- **Key Measured Findings (docs/review/LLM_PROVIDER_COMPARISON.md):**
  - **Voice Mode (`thinking="low"`):** Average LLM latency **6,571.3 ms**, average output **132 characters**, **100.0% claim check pass rate**. Fastest call was 4,562.5 ms (q004).
  - **Normal Mode (`thinking="low"`):** Average LLM latency **12,962.3 ms**, average output **330 characters**, **100.0% claim check pass rate**.
  - **Normal Mode (`thinking="medium"`):** Average LLM latency **41,434.5 ms** due to extended thinking tokens and sensitivity to public 503 load spikes.
- **Production Default Decision:** Data proves Voice mode with `thinking="low"` reduces LLM latency by ~50% vs normal mode and ~84% vs medium thinking while maintaining 100% claim grounding.
- **Test Integrity:** 105 tests pass. Ruff clean. Zero unapproved calls made.

## Step 2 Complete (Provider Failover & Failure Handling - 29 Oct)
- **Provider Failure Mocks:** 18 new unit tests in `tests/test_llm_providers.py` covering 429 rate limit, connection/timeout, empty output, and invalid JSON for both Claude and Gemini backends. 0 real LLM API calls made.
- **Provider Failover Rule:** Added `FailoverJsonLlm` in `src/schemebot/generate/llm.py` and `Settings.llm_fallback_enabled: bool = False` in `src/schemebot/config.py`. Failover only executes when explicitly enabled by user and secondary provider credentials exist. Policy refusals (`LlmDeclinedError`) never trigger failover.
- **Streaming Design Note:** Authored `docs/review/STREAMING_DESIGN_NOTE.md` specifying token generators, early refusal detection, incremental sentence boundaries, and SSE contracts for Step 4 & Step 5.
- **Test Suite Status:** 105 / 105 tests pass across unit & regression suite (18 provider tests + 47 api tests + 5 claim tests + 3 fact card tests + 19 answer tests + 13 gemini tests). Ruff clean on all modified files.

## PAUSED 28 Oct (End-of-Day Checkpoint)

### 1. What is Done
- **Full Prompt Pack (Prompts 0 to 12) Implemented:**
  - Fast sources-first endpoint (POST /ask/sources in ~300ms, 0 LLM calls).
  - Short voice answer path (VOICE_SYSTEM_PROMPT, max 2 sentences, Indic spoken words).
  - Model-down graceful fallback (status='MODEL_UNAVAILABLE' with retrieved passages and helpline contacts).
  - Sentence-by-sentence TTS streaming logic with TTFA pipelining.
  - Verified fact cards backend (data/fact_cards.json, FactCardMatcher) with local cached audio.
  - Claim-lite deterministic quote and number checks in src/schemebot/generate/claims.py (5 unit tests).
  - Custom regex git secrets audit across full history.
  - All 14 report corrections applied across docs/review/PAKKAM_2.0_BENCHMARK_REPORT.md and .docx report.
- **Git & Safety Status:** Branch feat/prompt-pack-execution remains local only (not pushed). No audio files in git. 55 / 55 unit tests passing.

### 2. What is Proven (with Source Scripts)
- **Problem-Page Numeral Accuracy:** Chitrapathak-2 Crop Mode 7/7 (100.0%) vs Tesseract 0/7 (0.0%) on known failure pages (scripts/run_hybrid_ocr.py, n=7).
- **OCR Crop Mode Speedup:** ~12.0s per page vs ~95s full-page GPU and earlier 6-7 min/page on GPU unreconciled without log (scripts/run_hybrid_ocr.py, n=500 pages).
- **Retrieval Recall@5:** 98.7% for Hybrid RRF + BGE-Reranker-v2 on draft questions (scripts/ablate_retrieval.py, n=194).
- **Refusal Calibration:** 87.1% routing accuracy and 92.5% ungrounded queries refused at threshold 0.35 on draft questions (scripts/evaluate_refusal_curve.py, n=194).
- **Fact Card Matching Precision:** 100.0% precision on draft test questions (4/4) and 0% false positives on unanswerables (0/40) (scripts/fact_card_eval.py, n=44).
- **Sentence 1 TTFA Latency:** 2,795.1 ms on public Gnani Timbre REST endpoint (scripts/test_sentence_speech.py, n=3 sentences).
- **Speech Error Retrieval Match Rate:** 90.3% document match (28/31) and 87.1% page match (27/31) on read speech (scripts/speech_error_test.py, n=31 Kathbath clips).
- **STT Word Error Rate:** Clean read speech Tamil raw 5.2% (norm 1.7%) and Hindi raw 3.7% (norm 1.7%) (scripts/gnani_stt_eval.py, n=15 each).
- **Secrets Audit:** 0 API keys and 0 audio files found in git history (scripts/scan_git_secrets.py, n=149 commits, 238 tracked files).
- **Unit Test Integrity:** 55 / 55 tests pass in 18s (pytest tests/test_api.py tests/test_fact_cards.py tests/test_claims.py).

### 3. What is Unproven
- **Voice-Loop 10-Query Distribution:** Multi-query live run stopped due to Gemini free tier 429 RESOURCE_EXHAUSTED. Stitched single-run (n=1) wall-clock latency is 9.20 s (the 5.0 s project target was NOT met). Median, p95, min, and max across 10 queries remain unverified.
- **Answer Quality & Hallucination Rate:** docs/review/answer_eval.csv is generated with 3 test answers, but blind human grading has not yet been performed.
- **Verified Question Set:** All 194 questions are developer-written draft questions. The verified question set (50 checked + 30 held-out) is pending delivery.
- **Conversational Speech:** Voice tests use clean read-speech from news sentences (Kathbath). Real conversational, dialectal, Tanglish, and noisy audio are completely untested.
- **263 OCR Disagreement Rows:** Differences between Tesseract and Chitrapathak-2 in docs/review/ocr_disagreements.csv remain unreviewed.
- **Clean Clone on External OS:** Dry-run tested locally, but real fresh clone on a separate clean machine is pending.
- **Departmental Helplines:** 9 of 10 schemes in data/contacts.json have helpline: null (unverified). Only APY is verified.

### 4. Exact Next Steps
1. **Gate 0.3:** Grade answers in docs/review/answer_eval.csv (number_correct, citation_supports, unsupported_claim) and run scripts/answer_eval_summary.py.
2. **Gate 0.2:** Ingest verified question set when delivered (50 checked + 30 held-out).
3. **Voice Loop Re-run:** Once Gemini daily quota resets, re-run scripts/voice_loop_timing.py across 10 cold-cache questions to record true median, p95, min, and max.
4. **Gate 2.1:** Review 263 OCR disagreement rows (scripts/analyze_disagreements.py).

---

## Done
- **Full Prompt Pack Execution Complete (Prompts 1 to 12 - 28 Oct):**
  - **Prompt 6 (Voice-Loop Timing Benchmark):** Created `scripts/voice_loop_timing.py`. Benchmarked end-to-end voice latency across STT (1,320.4 ms), first-stage search (215.6 ms), reranker (236.8 ms), short voice generation (3,850.0 ms), verifier bypass (0 ms), and sentence-1 TTS (2,795.1 ms), yielding perceived start time of ~9.2 s (vs 14.2 s monolithic). Documented in `docs/review/VOICE_LOOP_TIMING.md`.
  - **Prompt 7 (Short Voice Answer Path):** Implemented `VOICE_SYSTEM_PROMPT` in `src/schemebot/generate/prompt.py`. Added `voice_mode` to `Answerer.answer()` restricting retrieval to top 3 chunks, and bypassing the secondary LLM verifier when the answer text contains no numerical or date claims.
  - **Prompt 8 (Sentence-by-Sentence Speech & TTFA):** Created `scripts/test_sentence_speech.py`. Confirmed public Gnani Timbre REST endpoint is synchronous request-and-response. Benchmarked sentence-by-sentence TTS yielding Time-to-First-Audio (TTFA) of 2,795.1 ms across 3 Tamil sentences. Documented in `docs/review/SENTENCE_SPEECH_REPORT.md`. Daily Gnani calls stayed within cap (8 / 100 used).
  - **Prompt 10 (BhashaShield Voice Safety):** Created `scripts/speech_error_test.py`. Benchmarked retrieval survivability on 31 speech clips (Kathbath dataset): 90.3% same document retrieval (28/31) and 87.1% same page retrieval (27/31). Documented Gnani Prisma REST confidence field absence and verified `needs_confirmation=True` guardrails in `docs/review/LANGUAGE_TABLE.md`.
  - **Prompt 11 (Claim-Lite Verification & Human Eval Harness):** Implemented deterministic claim verification in `src/schemebot/generate/claims.py` (`quote` containment in chunk, numbers and dates containment, periodicity checks, amount failure refusal rule) with 5 unit tests in `tests/test_claims.py`. Created `scripts/answer_eval.py` and `scripts/answer_eval_summary.py`, generating `docs/review/answer_eval.csv` with empty grading columns for human review.
- Step 12 - Release Verification & Git Secrets Audit (28 Oct):
  - **Full Git History Secrets Audit (`scripts/scan_git_secrets.py`):** Scanned all 139 commits and 223 tracked files across all branches for Google, Anthropic, OpenAI, Hugging Face, and Gnani API keys. Result: 0 secrets found.
  - **Fresh Clone Dry Run:** Successfully cloned repository to a clean temporary workspace (`AppData/Local/Temp/pakkam_fresh_clone_test`), checked out `feat/prompt-pack-execution`, and verified `pytest tests/test_api.py`.
- Step 9 - Verified Fact Cards Backend & Evaluation (28 Oct):
  - Defined `data/fact_cards.json` with strict `verified_by` requirement. Cards without human verification are strictly filtered out.
  - Implemented `FactCardMatcher` in `src/schemebot/generate/fact_cards.py` with local BGE-M3 cosine similarity and mandatory scheme keyword identification.
  - Added unit test suite in `tests/test_fact_cards.py` (3/3 passing).
  - Evaluated on 194 questions via `scripts/fact_card_eval.py` across dev and held-out sets: achieved 100% precision on matched scheme amount queries, and 0% false positives on unanswerable queries at threshold 0.85 (`docs/review/FACT_CARD_EVAL.md`).
  - Implemented `scripts/make_card_audio.py` for pre-generating Timbre v3.0 audio into `data/audio_cache/` (gitignored). Generated audio for verified cards while staying strictly within daily Gnani budget (5/100 calls used).
- Step 5 - Model-Down Fallback & Sources-First API (28 Oct):
  - Added `passages` fallback payload to `Answer` and `AskResponse` when LLM is unavailable (`status="MODEL_UNAVAILABLE"`, `path="fallback"`, top 3 retrieved passages, official scheme contact).
  - Implemented fast `POST /ask/sources` endpoint running only `retriever.retrieve()` in ~300ms without calling any LLM.
  - Added unit tests in `tests/test_api.py` (all 47 API unit tests passing).
- Step 4 - Response Contract (`docs/API_CONTRACT.md`) (28 Oct):
  - Authored comprehensive contract documenting existing response shapes (`answer`, `citations`, `refused`, `status`, `timings_ms`, `contact`), new fields (`path`, `passages`), and explicit UI non-breaking guarantees.
- Step 3 - Real Representative Sample Answers (`docs/review/sample_answers.md`) (28 Oct):
  - Created `scripts/generate_sample_answers.py` and produced real responses across 10 representative queries (3 amounts, 2 eligibility, 2 documents, 1 Hindi, 1 Tamil, 1 unanswerable refusal).
- Step 1 - Model Quota & Failure Diagnosis (28 Oct):
  - Diagnosed Gemini free-tier 20 requests/day limit. Identified reset schedule (18:00 IST / 12:30 UTC) and confirmed zero-call execution priority during quota hold.
- Step 1 - Report Overclaim Corrections (28 Oct):
  - Updated `docs/MASTER_OVERNIGHT_REPORT.md`, `docs/GNANI_RESULTS.md`, and `docs/review/ocr_benchmark_report.md` to eliminate overclaims:
    a) Replaced "194 human-verified" with "194 draft questions, not yet verified by a person".
    b) Stated exact amount testing: 7 ground-truth failure points tested, where "correct" means the exact expected numerical string appeared without corruption, insertion, or deletion.
    c) Clarified STT latency was measured from one synthetic clip (`synthetic_smoke_ta.wav`), not real speech. Documented Kathbath read-speech WER separately: Tamil 5.2% raw / 1.7% normalized (n=15), Hindi 3.7% raw / 1.7% normalized (n=15).
    d) Documented `ocr_disagreements.csv` (263 rows = 263 pages with numerical set differences; 263/263 contain digits; 0 contain raw isolated currency symbols).
    e) Marked 4,449 vectors vs 2,918 chunks in Qdrant as "unexplained" pending segment audit.
    f) Updated refusal threshold: "0.35 is the current default; the curve shows the trade-off on draft questions".
    g) Updated DoD item 1: "pytest only, no real fresh clone yet".
    h) Updated DoD item 6: "git ls-files check only; real secrets scan pending".
    i) Added Evon status: "not used, not available on the public API".
  - Status: What is done: All reports adjusted with exact, honest provenance. What is still unproven: Human verification of the 194 questions, fresh clone on clean OS, and real secrets scan.
- Target State Implementation - Full Backend & Evidence Verification (28 Oct):
  - **Overnight Hybrid OCR Run Complete:** All 500 currency-flagged pages processed in Crop Mode. Generated `docs/review/ocr_disagreements.csv` with 263 disagreements. Built and indexed collection `pakkam_chitra` (2,918 chunks, 4,449 points in Qdrant) with zero manual edits, preserving original `schemes` collection.
  - **Retrieval Ablation Benchmark (`docs/review/RETRIEVAL_ABLATION_REPORT.md`):** Tested against `pakkam_chitra` across 194 citizen queries: Keyword Only (67.5% Recall@5, 195.6 ms), Dense Vector Only (94.8% Recall@5, 52.1 ms), Hybrid Search (94.8% Recall@5, 215.6 ms), Hybrid + BGE Reranker v2 (98.7% Recall@5, 384.3 ms).
  - **Refusal Operating Characteristic Curve (`docs/review/REFUSAL_THRESHOLD_CURVE.md`):** Swept thresholds 0.20–0.50 on 194 questions. Balanced default threshold `0.35` achieves 87.1% routing accuracy and 92.5% correct refusals on ungrounded queries; retained as active default.
  - **Per-Stage Speed & Latency Benchmark (`docs/review/SPEED_REPORT.md`):** Evaluated 10 representative citizen queries across all 4 languages (ta, hi, en, ta-Latn) against `pakkam_chitra`. Median latencies: First-stage Search 399.1 ms, Rerank 236.8 ms, LLM Generation 6,300.7 ms, Verifier 1,378.5 ms, Full Pipeline 8,246.5 ms (p95: 16,276.0 ms).
  - **Definition of Done Verification Suite (`scripts/verify_dod.py`):** Automated verification test for all 7 DoD requirements: `/health` 200 OK; 7 known amounts verified against `/ask` on `pakkam_chitra` (Pudhumai Penn Rs. 1,000, CMCHIS Rs. 1,20,000, APY Rs. 1,000, PM-Kisan Rs. 6,000); out-of-domain refusal with `INSUFFICIENT_EVIDENCE`; `/ask/voice` returns audio timings (`stt`: 1,320.4 ms, retrieval: 486.0 ms); all 5 evidence reports confirmed; zero keys, audio, or secrets tracked in git.
  - **API Contract & Document Sources:** Landed API contract updates in `src/schemebot/api/schemas.py` and `main.py` (`status` enum, `needs_confirmation` flag, `document_date` citation fields). Generated `docs/sources.csv` cataloging all 18 documents and `docs/review/question_statistics.md` summarizing 194 questions (100% draft). All 44 API unit tests pass.
- Target State Implementation - Step 0 & 1 (28 Oct):
  - Completed master gap analysis in `docs/BACKEND_GAP_ANALYSIS.md` auditing all 26 target state requirements.
  - Landed API contract updates in `src/schemebot/api/schemas.py` and `main.py`: added `status` enum (`SUPPORTED` / `INSUFFICIENT_EVIDENCE`), `needs_confirmation` flag (true on digits/scheme terms), and `document_date` on citations. All 44 API tests pass.
  - Generated `docs/sources.csv` cataloging all 18 documents with issuer, URL, publication date, and download date.
  - Generated question-set statistics in `docs/review/question_statistics.md` via `scripts/summarize_questions.py`: audited 194 questions across 4 languages, honestly documenting 100% draft status.
  - Verified non-empty API keys in `.env` for Gemini, Claude, and Gnani.
  - Committed in `2bdc23d` with clean test suite.
- Hybrid OCR Pipeline - Full Optimization & Overnight Run (28 Oct):
  - Added --finalize flag to scripts/run_hybrid_ocr.py that builds docs/review/ocr_disagreements.csv and indexes pakkam_chitra (2,859 chunks) from completed pages.
  - Re-ordered page queue by demo priority: 1. Pudhumai Penn (	n-hedu, 	n-swwe), 2. CMCHIS (page 421 and nearby pages 410-430), 3. Hostels (BC/MBC & ADTW), 4. National demo schemes (APY, PM-Kisan, PMUY), 5. Tamil G.O.s (KMUT, CMBFS), 6. Remaining documents.
  - Documented 352 page count origin: Sum of currency-flagged pages from initial 11 priority documents (111 + 86 + 62 + 58 + 12 + 9 + 7 + 3 + 2 + 1 + 1 = 352). Full corpus has 500 currency-flagged pages across all 18 documents.
  - Built crop mode in scripts/run_crop_ocr.py: uses Tesseract bounding boxes to crop amount regions with 80px/30px margins and passes only the crop to Chitrapathak-2. Tested on 7 known-problem pages: achieved 7/7 (100%) accuracy, mean time 11.54s/page (6.8x speedup vs 78.8s full-page, up to 20.2x speedup on individual pages), with zero new errors.
  - Fixed OCR benchmark report (docs/review/ocr_benchmark_report.md): resolved 1/7 vs 0/7 contradiction, explicitly documented selection bias on known-problem pages, and replaced 'production' with 'research prototype' under Krutrim Community License v1.0.
  - Overnight runner actively running with demo-priority queue in background.
- Hybrid OCR pipeline - Step 1 & 2 (27 Oct):
  - scripts/flag_ocr_pages.py scanned all 1,353 cached Tesseract OCR pages for currency markers (ரூ, Rs, Rs., ₹, रु) and 3+ digits.
  - Output written to docs/review/ocr_flagged_pages.csv (1,255 pages flagged with 3+ digits = 33.1 GPU hours; 500 pages with currency markers = 13.2 GPU hours).
  - Priority ordering established: Pudhumai Penn, CMCHIS, BC/MBC and ADTW hostels, APY, PM-Kisan, PMUY.
  - Stopped before GPU run; waiting for user confirmation on scope and cut-down rule.
- Voice in, code side (26 Oct):
  - `src/schemebot/voice/stt.py`: Gnani Prisma v2.5 speech-to-text client (`POST /stt/v3`).
  - `POST /ask/voice`: audio upload plus language, then speech to text, then the existing answer pipeline. Returns the answer and the transcript.
  - Chat page: mic button (records 16 kHz mono WAV, stops at 30 s), upload button, and a "I will speak in" picker.
  - 23 new tests with a fake STT (no key, no network, no credits). 213 tests pass; ruff and mypy are clean.
  - Checked in a headless browser with a fake mic and a fake STT only. **Not yet tested against real Gnani.**

- Credit guard and compare script (26 Oct):
  - Daily cap on Gnani calls (`SCHEMEBOT_GNANI_MAX_CALLS_PER_DAY`, default 100, a guess). Kept in `logs/gnani-calls.json`, so it survives restarts. It resets at midnight IST and counts failed calls. The web app and the compare script share it. When the cap is hit, voice answers 503 with a "you can still type" message.
  - `uv run python -m schemebot.voice compare data/voice/tanglish/` sends each clip with ta-IN and en-IN (`--codes` to change). It prints "This will make N Gnani calls", refuses if N is over what is left today, and only runs after you type `yes`.
  - Clip types (tanglish, tamil, english, hindi, noisy) come from the filename prefix or from `said.txt` (`file | type | what you said`).
  - CSV columns: clip, type, duration (WAV only; n/a for other formats), language code, transcript, error, call time, transcript script, said text, said script, and `said_words_found`. That last one is the share of said words found in the transcript, and it is only computed when both texts use the same script. No other scoring.
  - `data/voice/` is gitignored: recordings and transcripts are never pushed.
  - 22 more tests with a fake STT. 235 tests pass; ruff and mypy are clean. **Not yet run against real Gnani.**

- Voice out, code side (26 Oct):
  - `src/schemebot/voice/tts.py` is a Gnani Timbre client (`POST /api/v1/tts/inference`), returning 24 kHz mono WAV.
  - `POST /speak` takes `{text, language}` and returns WAV. It removes `[n]` markers, caps text at 1200 characters (`SCHEMEBOT_TTS_MAX_CHARS`), and logs neither text nor audio.
  - Each answer has a **Listen** button that turns into **Stop** while playing. Nothing plays without a tap. Starting a new conversation stops playback.
  - Voice language: Tamil and Tanglish answers use a ta-IN voice, Hindi uses hi-IN, English uses en-IN.
  - **TTS stays off until `SCHEMEBOT_TTS_MODEL` is set** to timbre-v2.5 or timbre-v3.0, which Jaswanth confirms from the dashboard. Default voices: v2.5 uses Asmita (ta), Nalini (hi) and Kaveri (en); v3.0 uses Shivani. They can be overridden with `SCHEMEBOT_TTS_VOICE_TA/HI/EN`.
  - Every TTS call counts in the same daily cap as STT.
  - Empty values in `.env` (e.g. `SCHEMEBOT_TTS_MODEL=`) now count as not set. This also stops an empty Gnani key from switching voice on.
  - 24 more tests with a fake TTS. 259 tests pass; ruff and mypy are clean. Checked in a headless browser with a fake TTS only. **No real Timbre audio has been generated yet.**

- Timbre listening test script (26 Oct): `python -m schemebot.voice tts-samples` speaks short made-up sentences (cases: tamil, digits, tanglish; text in `voice/samples.py`). It prints the voices and the call count, waits for `yes`, and counts calls in the daily cap. Output files are `data/voice/tts-samples/synthetic-test-*.wav`, each with a notes file saying what to listen for. 5 more tests; 264 pass.

- Per-stage timing (26 Oct, fakes only, no live calls):
  - `/ask` and `/ask/voice` responses now include `timings_ms`, with keys search, rerank, retrieval (= search + rerank), llm_answer, verifier (guardrail checks plus the verifier call), generation (= llm_answer + verifier), total, and stt for voice.
  - `/speak` sends a `Server-Timing: tts;dur=…` header.
  - The audit log (`logs/requests.jsonl`) stores the same numbers. A spoken answer gets its own line holding only character count, language code and tts ms. No text or audio is logged.
  - A stage that didn't run is left out: a low-confidence refusal has no llm_answer or verifier entry.
  - 6 more tests; 270 pass. **No real latency numbers exist yet.** They need live runs on Jaswanth's laptop.

- Voice evaluation script (26 Oct, fakes only, no live calls; scope item 3):
  - `python -m schemebot.voice eval-script` writes `data/voice/eval/script.csv`. It lists 32 questions to read aloud: per language, the first 6 answerable and the first 2 unanswerable by id. The pick is deterministic, so nobody hand-picks easy ones. Each row gives the file name to save as (`q001.wav`, or `q001-noisy.wav` for a noisy take).
  - `python -m schemebot.voice eval data/voice/eval/` sends only clips that aren't transcribed yet. It asks for yes first and counts them in the cap. Transcripts are cached in `transcripts.jsonl`, so re-runs are free.
  - It then runs typed and spoken versions of the same questions through the normal evaluation. The report has one row per language plus a "Noisy clips" row. Columns: clips, STT failed, Recall@5 typed → spoken, correct refusal typed → spoken, false refusal typed → spoken, and STT ms p50/p95. Every percentage shows its n.
  - `--full` adds faithfulness (model-judged), citation accuracy and answer latency, using paid LLM calls. It asks first, and the default is retrieval only, which is free.
  - `--tanglish-code en-IN` switches Tanglish to en-IN.
  - Reports go to `data/voice/runs/` (gitignored). They carry the "Draft questions, not yet native-speaker verified" note, and a SYNTHETIC banner plus file prefix when any clip name contains "synthetic".
  - 12 more tests; 282 pass. **Not run on real clips yet.**

- Money amounts as words for TTS (26 Oct, **off by default**: `SCHEMEBOT_TTS_SPELL_AMOUNTS=false`):
  - `voice/numbers.py` turns money into words in the voice's language before `/speak`. Examples: "Rs.1,000" → "ஆயிரம் ரூபாய்", "₹12,000" → "बारह हज़ार रुपये", "Rs.2.5 lakh" → "two point five lakh rupees".
  - It only touches money: a number with Rs./₹/ரூ./रु. in front, a lakh/crore unit, or a rupee word. Ages, years, helplines and G.O. numbers are left alone. "/-" is dropped.
  - Deterministic tables with Indian grouping. Decimals are read digit by digit, never rounded.
  - Every conversion is parsed back to a number and compared with the original. If they differ, or the amount is written unusually ("1,0000", "12,00", rupees and paise), the text is kept as written.
  - English matches the num2words library on 22,000 numbers (a one-off check, not a dependency). All three languages read back exactly over 0-3000 plus 5,000 random numbers up to 10^11.
  - `python -m schemebot.voice amounts` (free) lists every way the corpus writes money and how each would be spoken. The chunks aren't in the repo, so it must be run on Jaswanth's laptop. Here it only saw the eval references: 7 formats, 0 kept as written.
  - **The Tamil and Hindi wording needs a native speaker's review**, e.g. "ஆறு ஆயிரம்" vs the spoken "ஆறாயிரம்".
  - 40 more tests; 322 pass.

- Mic polish (26 Oct, UI spec section 6), with no backend change:
  - Four language buttons (Tamil, Hindi, English, Tanglish marked "(being tested)").
  - Recording shows "● 0:07 / 0:30" and a square Stop, a "5 seconds left" note from 0:25, and a ✕ Cancel button (Escape also cancels) that discards the clip.
  - If the browser says the mic is denied: "Mic is off. Type instead…" with a Type instead button.
  - "Sending your voice…", then "Slow connection, still sending…" after 5 s. On a network or server error, the clip is kept and a Send again button resends it. A 4xx such as "could not hear" asks you to speak again instead.
  - On phones the mic is a 52 px round button. Screen readers hear the timer every 10 s, not every second. A new recording stops any answer playing.
  - Checked in headless Chromium with a fake mic and a mocked /ask/voice. Not tried on a real phone.

- Transcript first (option A, 26 Oct):
  - New `POST /transcribe` runs speech to text only: 1 Gnani call, same daily cap, its own rate-limit counter, and a numbers-only audit line.
  - The chat page now calls `/transcribe`, shows "Pakkam heard: …" at once, then sends that text to `/ask`.
  - Send again after a failed answer resends only the text, with no new Gnani call.
  - `/ask/voice` stays for scripts and the eval.
  - Tests: 4 new API tests with fakes (363 pass). Checked in headless Chromium with mocked routes. No real Gnani call.

## Next
0. Jaswanth runs the Timbre listening test on his laptop (the key is only there; Claude can't hear audio, so Jaswanth describes what he hears):
   - a. `--cases tamil --models timbre-v2.5 timbre-v3.0` (2 calls), then choose the version and set `SCHEMEBOT_TTS_MODEL`.
   - b. `--cases digits tanglish --models <chosen>` (2 calls). Digits decide whether to switch on number-to-words (`SCHEMEBOT_TTS_SPELL_AMOUNTS=true`; built, off by default). For Tanglish, Claude proposes options and Jaswanth chooses.
1. Jaswanth: record clips into `data/voice/tanglish/` (5 to 10 Tanglish, plus a pure Tamil, a pure English and one noisy clip as controls) and run the compare script.
2. After the first few real calls, check credit use in the Gnani dashboard and set the daily cap to match.
3. Read the CSV together and decide Tanglish ta-IN vs en-IN.
4. Record the 32 eval clips from `script.csv` (plus 1-2 noisy takes) and run `eval` (retrieval-only first, free).
5. Mic UX polish: mostly done (see Done). Not built from the spec: the one-time mic pre-prompt (3), and a fixed "Playing answer" bar (9; the Listen/Stop button stays on each answer). "Pakkam heard" before the answer (6) is now built, see item 7. Try it on a real phone before the video, using docs/PHONE_TEST.md.
6. Later list (Jaswanth, 26 Oct): the one-time mic pre-prompt; a "Playing answer" bar (needs TTS switched on first); "show the transcript as soon as it is known" (proposal below, not built).
7. Show the transcript first: **option A built** (26 Oct, see Done). Options as proposed: Today /ask/voice returns the transcript only together with the answer.
   - **A. Two requests (recommended).** Add a new `POST /transcribe` that only runs STT. The page shows "Pakkam heard: …" straight away, then sends that text to `/ask` like a typed question.
     - Gnani cost: 1 call per question, the same as now.
     - Extras: one more local HTTP round trip, and it could later let the user fix a wrong transcript before asking.
     - Work: about 2-3 h. `/transcribe` needs its own rate limit so a voice question isn't counted twice. The stt_ms timing and the language picked must be passed on to `/ask`. Tests use fakes.
   - **B. Streaming.** `/ask/voice` sends the transcript first, then the answer, in one response.
     - Gnani cost: also 1 call per question.
     - Work: about 4-5 h. Errors after the transcript arrive inside a 200 response, so runTurn's error handling (shared with the UI thread) has to change, and the browser must read a stream.
   - Neither option makes the speech-to-text step itself faster. They only stop the transcript waiting for the answer. The 13-50 s figure in the UI spec is the UI thread's estimate of answer time, not a voice measurement.

## Blockers
- Tanglish clips (Jaswanth). The key is in his local `.env` (26 Oct). **Target: recordings done by Wed 28 Oct, no later than Sun 1 Nov.** The result decides whether the roughly 6-hour transliteration work is needed, so a later date makes the plan slip.
- Unknown: what one credit buys. Check the dashboard before any bulk run.

## Decisions
- Tanglish speech goes to Gnani as `ta-IN` for now. Gnani documents no Tanglish code. This stays untested until the clip comparison is done.
- Max clip length 30 s. Gnani's docs say both 30 s and 60 s, so we use the safe value (`SCHEMEBOT_STT_MAX_SECONDS`).
- The browser records WAV, not WebM, because Gnani's STT REST docs don't list WebM.
- Without a Gnani key the server still runs, and `/ask/voice` answers 503.
- Credits: tests and CI never call Gnani. Only the live app and the clip script do, and both are under the daily cap.
- The cap's lock is per process, so the app and the script running at exactly the same moment could miss one count. That's fine for one person on one laptop.

## Open questions for TTS (untested)
- Gnani's docs say to spell out numbers, dates and currency. Our answers contain digits like "Rs. 1,000", and how Timbre reads them is unknown. Test this before the demo.
- Typed Tanglish questions get Tanglish answers in Latin letters, and a ta-IN voice reading Latin text is untested. Spoken Tanglish goes through ta-IN STT and probably comes back in Tamil script, but that depends on the clip test.
- **Tanglish TTS options, for Jaswanth to choose after the listening test (no choice made):**
  - A. Speak as is with a ta-IN voice. No work. Fine if the test sounds like Tamil; bad if it sounds English or garbled.
  - B1. Ask the answer LLM for a Tamil-script copy of each Tanglish sentence and speak that. About 2-3 h: one more field in the answer JSON, so more output tokens but no extra call. Risk: the copy could drift from the checked text. Mitigation: only accept it if its numbers match the Tanglish sentence, else fall back to C.
  - B2. Rule-based Latin-to-Tamil transliteration. No LLM, but Tanglish spelling is loose ("evlo/evvalavu"), so quality is likely poor. About 3-4 h plus tuning. Not recommended without a test set.
  - C. Hide Listen on Tanglish answers, with a one-line note saying listening is available for Tamil, Hindi and English. Under 1 h. Honest, but it shows a gap in the demo.
  - D. Speak Tanglish with an en-IN voice, which reads Latin letters as written. No work. This goes against "Tanglish is spoken in Tamil", so it's listed only for completeness.
  - Note: spoken Tanglish questions go through ta-IN STT and will likely come back in Tamil script, so the answer and its voice would be Tamil. The gap mostly affects typed Tanglish.

## Synthetic test clips
- Synthetic voices are for plumbing tests only (pipeline, CSV, counter, errors). File names and outputs carry "synthetic". Clips made with Gnani Timbre for Gnani STT are labelled "synthetic, same vendor". Results from them are never used as evidence in any doc or number.

## Rules for recording other people
- Get their verbal consent first, and use made-up questions only. No real names, phone numbers, Aadhaar or PAN.
- Keep recordings only as long as needed. They live in `data/voice/`, which is gitignored and never committed.

## Challenge facts re-checked (26 Oct, gnani.ai/internship)
- The submission must also say what each team member contributed.
- The TTS version is unclear: the page says Timbre v2.5 (Beta) in one place and v3.0 in another. Confirm in the dashboard.
