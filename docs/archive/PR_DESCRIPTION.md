# Pull Request: Pakkam 2.0 Backend Evidence, Fallback, Fact Cards & Release Readiness

**Branch:** `feat/prompt-pack-execution`  
**Target:** `feat/ocr-step1-chitrapathak-gate` (or `main`)  
**Status:** Ready for Review (Do not merge without user go-ahead)

---

## Summary of Changes

This pull request implements the backend components and evidence verification pipeline specified in the **Pakkam 2.0 Roadmap & Prompt Pack** (Oct 28, 2026):

1. **Model-Down Fallback & Sources-First API (Prompt 5)**:
   - When the LLM is down (e.g. 429 quota exhaustion or network timeout), the API returns `status="MODEL_UNAVAILABLE"` and `path="fallback"` along with the top 3 retrieved official passages and official scheme contact info.
   - Introduced `POST /ask/sources` endpoint to surface official source documents in ~300ms using only the local retriever without burning LLM quota.
   - Added 3 comprehensive tests in `tests/test_api.py` (all 47 API unit tests passing).

2. **Verified Fact Cards Backend & Evaluation (Prompt 9)**:
   - Defined `data/fact_cards.json` with strict human-verification gate (`verified_by` required).
   - Implemented `FactCardMatcher` in `src/schemebot/generate/fact_cards.py` with local `bge-m3` cosine similarity and mandatory scheme keyword identification (zero LLM calls).
   - Created `scripts/fact_card_eval.py` and evaluated on dev (n=137) and held-out (n=57) question sets: achieved 100% precision on matched amount queries and 0% false positives on unanswerable questions (`docs/review/FACT_CARD_EVAL.md`).
   - Implemented `scripts/make_card_audio.py` for pre-generating Timbre v3.0 cached speech into `data/audio_cache/` (gitignored), operating safely within the daily Gnani budget.

3. **Release Integrity & Secrets Audit (Prompt 12)**:
   - Executed full commit history scan (`scripts/scan_git_secrets.py`) across 139 commits and 223 tracked files. Verified: **0 secrets found**.
   - Verified fresh-clone dry run in a clean temporary directory with pytest passing.

4. **API Contract & Report Provenance (Prompts 2, 3, 4)**:
   - Authored `docs/API_CONTRACT.md` guaranteeing UI non-breaking compatibility.
   - Generated 10 representative answers in `docs/review/sample_answers.md`.
   - Updated all overnight and OCR reports to eliminate overclaims.

---

## Verification & Test Results

- `pytest tests/test_api.py`: **47 passed**
- `pytest tests/test_fact_cards.py`: **3 passed**
- `pytest tests/test_claims.py`: **5 passed** (Total: **55 tests passed**)
- `python scripts/scan_git_secrets.py`: **0 secrets found across 139 commits**
- `python scripts/fact_card_eval.py`: **100% precision, 0% unanswerable false positives**
- `python scripts/make_card_audio.py`: **2 audio files generated, 5/100 daily Gnani calls used**

---

## Preserved Project Rules
- Public documents only. Public synthetic audio only.
- Every metric backed by a re-runnable script named in reports.
- Keys stay strictly in `.env`; zero audio tracked in git.
- No PRs opened or branches merged without explicit user authorization.
