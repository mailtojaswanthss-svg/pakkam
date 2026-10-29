# Pakkam 2.0 - Teammate Handoff & Operations Manual

This document provides exact step-by-step instructions for teammates and evaluators.
All commands use `uv` and run on Windows PowerShell or Linux Bash.

---

## 1. Environment & Setup

Clone the repository and install all dependencies:
```powershell
# 1. Clone repository
git clone <repo-url> pakkam
cd pakkam

# 2. Environment file
cp .env.example .env
# Edit .env with your SCHEMEBOT_GEMINI_API_KEY and SCHEMEBOT_GNANI_API_KEY.
# If testing offline, the system defaults to mock fallbacks and local cached collections.

# 3. Install dependencies via uv (installs all pipeline extras without heavy torch)
uv sync --extra api --extra store --extra eval --extra generate --extra gemini --extra ingest

# 4. Verify test suite (521 automated unit and integration tests)
uv run pytest -q
```

---

## 2. Ingesting Teammate 50 Verified Questions (`BLK-02`)

When the 50 verified ground-truth questions are ready:
1. Place the file at:
   `data/eval/teammate_50_verified.jsonl`
2. Ensure each line matches the project JSONL format:
   ```json
   {
     "id": "t_q001",
     "group": "ta",
     "question": "புதுமைப்பெண் திட்டம் மாதம் எவ்வளவு தொகை?",
     "answerable": true,
     "gold": [{"doc_id": "tn-hedu-policy-note-2024-ta", "pages": [33]}],
     "reference": "மாதந்தோறும் ரூ. 1,000.",
     "fact": "pudhumai_amount",
     "status": "verified"
   }
   ```
3. Run the evaluation script:
   ```powershell
   uv run python scripts/answer_eval.py --dataset data/eval/teammate_50_verified.jsonl
   ```
4. The daily runner (`scripts/run_daily.py`) will automatically detect the file and unblock task `teammate_answer_eval`.

---

## 3. Field Audio Recordings & Consent Protocol (`BLK-03`)

To test real speech-to-text accuracy across noisy environments and regional accents:
1. Follow the protocol and consent script in [`docs/voice/CLIP_PLAN.md`](voice/CLIP_PLAN.md).
2. Collect the 30 audio clips (16 kHz mono WAV format).
3. Place them in:
   `data/voice/field_clips/clip_01.wav` ... `clip_30.wav`
   *(Note: `data/voice/field_clips/` is gitignored to protect speaker privacy).*
4. Verify matching prompts against [`docs/voice/field_clips_metadata.csv`](voice/field_clips_metadata.csv).
5. Run the evaluation:
   ```powershell
   uv run python scripts/eval_field_clips.py
   ```
   This computes Word Error Rate (WER) and retrieval Recall@3 across Tamil, Tanglish, Hindi, and English.

---

## 4. Helpline Verification Release Gate (`BLK-04`)

Helpline integrity is governed by a strict release gate: **No telephone number is published unless independently verified and cited from an official government page.**
1. Open [`docs/review/helpline_check.csv`](review/helpline_check.csv).
2. For each scheme:
   - Call the telephone number.
   - Verify it connects to the official government department or scheme helpline.
   - Record the government website URL where the number is officially published.
   - Fill `source_url`, `verified_by` (your name), and `verification_date` (YYYY-MM-DD).
   - If a number cannot be verified, set `helpline` to empty / null.
3. Run the automated release check:
   ```powershell
   uv run python scripts/check_helplines.py
   ```
   *Exit code 0 confirms all published helplines are verified. Non-zero blocks release.*

---

## 5. Blind Human Hand-Grading (`BLK-05`)

To measure answer factual correctness independently of automated LLM judges:
1. Open [`docs/review/grading_sheet.csv`](review/grading_sheet.csv) (generated with 194 randomized questions).
2. Score each answer:
   - `factuality_score`: 1 to 5 (5 = completely factual per official document).
   - `attribution_score`: 1 to 5 (5 = citation precisely pinpoints evidence snippet).
   - `period_correct`: `yes`, `no`, or `n/a` (checks monthly vs annual vs one-time clarity).
   - `graded_by`: evaluator name.
3. Run the scoring summary:
   ```powershell
   uv run python scripts/answer_eval_summary.py
   ```

---

## 6. Daily Evaluation Runner

The automated runner executes daily benchmarks and respects hard API budgets:
```powershell
# Run daily benchmarks (Speed re-test on gemini-3.8-flash, voice timing, gate checks)
uv run python scripts/run_daily.py

# Dry-run inspection without consuming live API calls
uv run python scripts/run_daily.py --dry-run
```
- Daily LLM budget is hard-capped at 20 calls/day (with $\ge 5$ calls reserved as spare).
- Daily Gnani speech budget is capped at 100 calls/day.
- All task outcomes are saved to `data/eval/daily_checkpoint.json`.

---

## 7. Launching the Live Application

To launch the web interface and API for live testing:
```powershell
$env:PYTHONPATH="src"
$env:SCHEMEBOT_QDRANT_COLLECTION="pakkam_chitra"
uv run python -m uvicorn schemebot.api.main:app --host 0.0.0.0 --port 8000
```
- Web Chat UI: [http://localhost:8000/chat/](http://localhost:8000/chat/)
- Interactive API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- System Diagnostics: [http://localhost:8000/health](http://localhost:8000/health)
