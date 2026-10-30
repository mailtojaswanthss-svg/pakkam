# Pakkam + Gnani voice: status

Last updated: 30 Oct 2026.
CRITICAL TIMELINE & DEADLINES (Revised & Aligned):
- Freeze Date: Mon 2 Nov 2026
- Demonstration Video Delivery: Tue 3 Nov 2026
- Own Engineering Target: Fri 6 Nov 2026
- Hard Submission Deadline: 10 Nov 2026, 11:59 PM IST

REMOTE REPOSITORY STATUS:
- Branch `feat/prompt-pack-execution` exists on GitHub remote origin as a private backup (repo visibility: PRIVATE).
- Push policy: STRICTLY NO PUSHES without explicit authorization (`PUSH_BRANCH_NOW: no`). All commits are strictly local.

---

## Master Prompt 2 Run-to-Completion: Execution Status (30 Oct 2026)

- **Test Suite Status**: **521 passed, 10 deselected** (100% pass rate).
- **Mypy Strict Status**: Strict clean across all 65 source files (`src/schemebot`, `scripts/`, `tests/`).
- **Ruff Lint Status**: All checks passed across codebase.
- **Git Secrets Audit**: **0 secrets found** in full git history and working tree (`scripts/scan_git_secrets.py`).
- **Clean Clone Audit**: Verified in pristine temp clone: `uv sync` installs all dependencies cleanly; 521/521 tests pass; 0 secrets.
- **LLM Budget Guard**: Daily cap enforced at 20 calls/day; minimum reserve of 5 spare calls maintained. Today: 3 calls used on pinned `gemini-3.8-flash` (17 spare calls available).
- **Gnani Speech Budget**: Daily cap enforced at 100 calls/day. Today: 1 call used for Prisma empirical verification (99 calls remaining).

---

## Completed Engineering Steps (Master Prompt 2)

### Step 1: Model Preload & Lifespan Warmup (`2481e3c`, `121ff83`)
- Added `Answerer.preload()` and FastAPI lifespan warmup to eliminate cold-start latency.
- Decoupled `schemebot.text` from `pymupdf`/`extract.py` so core text normalization and API imports never trigger `pymupdf`.
- Added `httpx`, `filelock`, and `soundfile` to base dependencies.

### Step 2: Reliability Enhancements (`97ef596`)
- Implemented `LlmBudget` (`src/schemebot/generate/budget.py`) with persistent atomic file locking, IST midnight rollover, low-quota warning ($\le 5$), authoritative 429 lock-out, and environment override.
- Integrated budget guard into `GeminiJsonLlm` and `ClaudeJsonLlm`.
- Enhanced `/health` diagnostics returning status, models, retrieval readiness, Gnani readiness, preload status, and quota with zero secret leakage.
- Added input length validation (500 chars) on `/ask` and file size validation on `/ask/voice`.
- Added unsupported script / language refusal (`UNSUPPORTED_LANGUAGE`).
- Added configurable CORS middleware.

### Step 3: Kits & Release Gates (`167546a`)
- Added `verify_helplines()` release-gate audit with `docs/review/helpline_check.csv` and `scripts/check_helplines.py`.
- Formulated 30 synthetic field clip protocol and consent plan (`docs/voice/CLIP_PLAN.md`, `docs/voice/field_clips_metadata.csv`, `scripts/eval_field_clips.py`).
- Created 194-question blind human grading sheet and evaluator (`scripts/make_grading_sheet.py`, `docs/review/grading_sheet.csv`, `scripts/answer_eval_summary.py`).

### Step 4: Daily Evaluation Runner (`d0e9f9d`)
- Implemented `scripts/run_daily.py` with queue management and checkpointing (`data/eval/daily_checkpoint.json`).
- Executed today's speed re-test on pinned model `gemini-3.8-flash` within pre-approved budget (3 calls used, 17 spare).
- Executed voice-loop timing benchmark ($n=10$, perceived start latency 8,417.9 ms).
- Automated blocker gating for missing datasets (`BLK-01`, `BLK-02`, `BLK-03`).

### Hosting and source checks (26-27 Oct, merged from main)
- Website live on Vercel at https://pakkam-alpha.vercel.app (`web/`). The backend runs on Jaswanth's laptop and is reached through a Cloudflare quick tunnel; `web/vercel.json` forwards `/ask`, `/sources`, `/transcribe` and `/speak`. The tunnel link changes on every restart, so vercel.json needs the new host each time. Plan: Cloud Run (CPU, trial credit) near the deadline.
- Vercel cannot run the backend (PyTorch + 4.5 GB models over its ~500 MB limit, no index). Hugging Face Docker Spaces now need PRO ($9/month), so that route was dropped.
- First live timings via the site: search + rerank 0.7-0.9 s on the RTX 4060, tunnel ~0.5 s, full answers 40 s to over 120 s on free Gemini (two calls per answer, 429 retries). Suggested `.env`: flash-lite models, 30 s timeout, 1 retry.
- OCR corrections: `apy-brochure-hi` p1 checked by rendering the PDF: it prints रु.1000, so the correction holds. The six Tamil Nadu entries could not be checked from the cloud (cms.tn.gov.in resets connections); Jaswanth checks them on the laptop.
- Ujjwala (#10): the PMUY SoP lists Aadhaar of the applicant and all adults, and bank account number with IFSC, so the reference answer matches the source.

### Step 5: Prisma Real Request Capture (`c032949`)
- Dispatched 1 pre-approved live Gnani STT request (`scripts/capture_prisma_raw.py`) on public Kathbath clip (`kathbath_ta_01.wav`).
- Captured raw JSON to gitignored `data/voice/prisma_raw_sample.json`.
- Empirically confirmed Prisma v2.5 returns `['success', 'request_id', 'transcript', 'model', 'processing_time', 'end_to_end_latency']` with `confidence` absent.
- Updated master execution report with empirical evidence.

### Step 6: Clean-Clone Verification (`5f34cd0`)
- Cloned repository into clean temp directory; verified zero uncommitted secrets / keys.
- Ran `uv sync` with extras and verified all 521 unit and integration tests pass cleanly.
- Updated `README.md` with verified setup commands.

### Step 7: Operations & Specification Drafts (`5458d70`)
- Authored `docs/HANDOFF.md` with complete instructions for teammate tasks.
- Authored `docs/DEMO_RUNBOOK.md` with pre-flight checklist, vetted 4-language queries, and failure contingencies.
- Authored `docs/PROJECT_SPECIFICATION.md` detailing abstract, contributions, model cards, and measured vs unmeasured boundaries.

---

## Blocked Items Tracker (Human & External Inputs Needed)

| ID | Item / Gate | Required From | Description | Status |
|---|---|---|---|---|
| **BLK-01** | Held-out Question Evaluation | User | Commit `.freeze` marker file on Mon 2 Nov before evaluating held-out set. | Blocked on `.freeze` |
| **BLK-02** | Teammate 50 Verified Questions | Teammate | Deliver 50 verified questions to `data/eval/teammate_50_verified.jsonl`. | Blocked on teammate data |
| **BLK-03** | Field Audio Recordings | User / Field | Collect 30 physical audio recordings into `data/voice/field_clips/`. | Blocked on field recording |
| **BLK-04** | Helpline Human Verification | User | Complete phone verification calls for 9 helplines in `docs/review/helpline_check.csv`. | Blocked on telephone calls |
| **BLK-05** | Answer-Level Human Grading | User | Complete manual scoring in `docs/review/grading_sheet.csv`. | Blocked on human evaluator |
| **BLK-06** | OCR Page Disagreement Review | User | Review 68 scanned Tamil PDF pages with numerical amount disagreements. | Blocked on human review |
| **BLK-07** | Remote Push / PR Creation | User | Explicit `PUSH_BRANCH_NOW: yes` decision to push feature branch to origin. | Gated on user decision |
| **BLK-08** | Cloud Hosting / Phone Test | User | Real phone network deployment (SIP / Twilio / Exotel). | Deferred post-submission |
