# Project status, plan and structure

*Draft for the Pakkam project report (Word). Markdown first, for review. Nothing here has been copied into the .docx yet.*

**Snapshot: branches fetched Mon 26 Oct 2026, 12:36 UTC (6:06 PM IST).** This replaces the 11:37 UTC snapshot. Work is still going on, so this section describes the repository at these commits:

| Branch | What it holds | Commit | State |
|---|---|---|---|
| `main` | Text RAG system, web app, evaluation, report; plus voice (PR #5), backend fixes (PR #6), weakness docs (PR #2), UX docs (PR #1), this section (PR #4) | `2d5ea5f` | Merged on 26 Oct, 12:32 UTC |
| `claude/ui-proof-refusal` (PR #3, draft) | UI fixes T0, T1, T3, T4, with `main` merged into it | `f472301` | **Not merged** |
| tag `pre-voice-merge` | `main` before the merges | `35ba419` | Safety tag |

"**Done (main)**" below means merged into `main`. "**Done (branch)**" means built and tested on the PR #3 branch but not merged. The two are counted separately in section 4.

**Labels used here.** UNKNOWN: not in the sources. UNVERIFIED: written down, but not yet checked against the source. ESTIMATE: a guess, not a measurement. All hours are estimates.

**Disclaimer (wording kept from the Word report):** an independent student project. It is not an official government service and is not affiliated with any government body. Answers are informational only and must be checked against the official source before acting on them.

---

## 1. Summary

Pakkam answers questions about Indian government welfare schemes using only 18 public scheme documents. Every sentence in an answer cites the document and page it comes from. When the documents do not answer the question, Pakkam says so and points to the official website or helpline. People can ask in Tamil, Hindi, English or Tanglish (Tamil written in English letters), by typing or by voice, and the answer comes back in the same language. It is for people who hear about a scheme, for example through a forwarded message, and want to check what the official document says. Pakkam is a student project built by a team of two for the Great Indian AI Internship Challenge by Gnani.ai. It is **not** an official or government service. It is **not** affiliated with any government body, and **not** affiliated with Gnani.ai: it uses Gnani's speech APIs as a challenge entrant. It does not process applications, store personal data or give official advice.

---

## 2. What is built today

"Tested" below means automated tests with no network calls, unless it says "live". Re-run for this snapshot on 26 Oct: **358 tests pass on `main`** and **359 on the PR #3 branch** (slow tests deselected, as the project does by default). ruff and mypy were clean on the combined code in a trial merge (12:25 UTC).

### 2.1 Built and tested

| Feature | Where | Evidence |
|---|---|---|
| Reading PDFs, with OCR for broken Tamil and Hindi pages | `src/schemebot/ingest/` | `tests/test_extract.py`, `test_chunk.py`, `test_langid.py`, `test_ocr_cache.py`, `test_pipeline.py`. Real run: 18 documents, 2,688 pages, 1,353 through OCR, 2,785 chunks (`docs/report.md` §3) |
| Search index (bge-m3 dense and sparse vectors in Qdrant) | `src/schemebot/index/` | `tests/test_index.py` |
| Hybrid search, reranking, Tanglish gloss | `src/schemebot/retrieve/` | `tests/test_retrieve.py`, `test_tanglish.py`. Retrieval-only run on 194 draft questions (`docs/results.md`; provisional, see section 7) |
| Refusal threshold (refuse if reranker confidence is below 0.35) | `src/schemebot/config.py` | `tests/test_config.py`; correct and false refusal in `docs/results.md` |
| Answer with citations (Claude or Gemini), each LLM call capped at 60 s per attempt and 2 retries | `src/schemebot/generate/` | `tests/test_answer.py`, `test_gemini.py`. Live smoke test on 8 hand-picked questions (`docs/report.md` §8) |
| Guardrails (cite a shown passage; numbers must appear in it; a second model must agree). Now treats "2.5 lakh" and "2,50,000" as the same number | `src/schemebot/generate/guardrails.py` | `tests/test_guardrails.py` (includes tests that different amounts are still rejected); the 8-question live smoke test |
| API: `/ask`, `/health`, `/sources`, rate limits with a "come back tomorrow" message, audit log that stores a hash, never the question text | `src/schemebot/api/` | `tests/test_api.py`, `test_ratelimit.py` |
| Per-stage timings in every response and in the audit log (search, rerank, LLM, verifier, STT, TTS) | `api/`, `generate/answer.py` | Tests with fakes. **No real timings recorded yet** |
| Gnani call cap (daily limit on STT and TTS calls, correct across processes) | `src/schemebot/voice/budget.py` | `tests/test_voice_budget.py` (fake speech service, no credits used) |
| Evaluation script and native-speaker review sheet | `src/schemebot/evaluation/` | `tests/test_evaluation.py`, `test_review.py`; `docs/review/questions-review.csv` (194 rows) |
| Web home page and chat page; chat stops waiting after 2 minutes | `web/` | UI audit screenshots (`docs/ux/UI_AUDIT.md`; answers stubbed). Headless browser checks with mocked servers |
| CI (tests, ruff, mypy) | `.github/workflows/ci.yml` | Jaswanth merged each PR after CI was green (merge plan). Per-run results: UNVERIFIED for this section |

### 2.2 Built but not tested live

| Feature | Where | What is missing |
|---|---|---|
| Ask by voice: mic (16 kHz WAV, 30 s cap, cancel, "5 seconds left", mic-off card, Send again), upload, four language buttons | `web/assets/recorder.js`, `chat.js`, `web/chat/index.html` | Checked only in headless Chromium with a fake mic. No real phone, no iPhone Safari |
| Gnani speech to text and `POST /ask/voice` | `src/schemebot/voice/stt.py` | Fake tests only. **Never called against real Gnani** |
| Gnani text to speech: `POST /speak`, Listen/Stop button on each answer | `src/schemebot/voice/tts.py` | Fake tests only. **Switched off until the Timbre version is set; no real audio generated yet** |
| Money amounts spoken as words (off by default) | `src/schemebot/voice/numbers.py` | 40 tests. Tamil and Hindi wording needs native review |
| Clip comparison, Timbre listening test, voice evaluation scripts | `src/schemebot/voice/` | Fake tests only. Not run on real clips |
| Deployment files for Cloud Run and a Hugging Face Space | `deploy/` | Nothing is deployed. Public hosting was cut |

### 2.3 Built on the PR #3 branch, not merged

| Feature | Evidence |
|---|---|
| T0: unverified facts removed or hidden on the home page; demo labelled "Example answer" | Commits `af190c6`, `147693a`, `300469c` |
| T1: source line ("From: <document> · page N") under every answer; page number on the chip | `b30177d` |
| T3: calmer "I don't know" card with the official website and "What Pakkam can read" | `4f8dd8d` |
| T4: disclaimer visible on phones | `4f8dd8d`, `abe38b2` |

359 tests pass on the branch. Waiting for Jaswanth's review.

### 2.4 Not built

- Real measurements of anything voice: transcripts, latency, spoken numbers.
- Tanglish transliteration (only if the speech test shows it is needed).
- An answer cache (planned after the merges).
- A guard against known-bad OCR amounts (design asked for, not started).
- UI: T2 (timer, slow note, cancel, retry), T5 and T7.
- The mic pre-prompt, "Pakkam heard" before the answer, a fixed "Playing answer" bar.
- The tiny public sample for reviewers, and a `LICENSE` file.
- The fallback demo recording, the demo video and the post.

---

## 3. What is planned

Every remaining task from `WEAKNESS_PLAN.md` (§1, §2) and `UX_RECOMMENDATIONS.md` (§2, §4), merged so that nothing is counted twice. Rows that are done stay in the table, so section 4 can be checked. Owners and dates come from the plans. "Teammate" is the second team member, whose name and skills are UNKNOWN in the sources.

Status: **Done (main)**, **Done (branch)**, **Not done**. Work in progress counts as Not done, and the note says what exists.

### Voice

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| V1 | Real Gnani speech test: 5-10 Tanglish clips, ta-IN vs en-IN | Jaswanth | 3 | clips by Wed 28 Oct, hard stop Sun 1 Nov | Not done. Script built; waiting on clips |
| V2 | 1-2 noisy clips in the test | Jaswanth | 0.5 | with V1 | Not done |
| V3 | Timbre TTS: confirm version, client, endpoint, button, tests | Jaswanth | 8 | 31 Oct | Not done. Code merged (`84b14d6`); version not confirmed, no real audio |
| V4 | Time every stage on live voice runs; median and max with n | Jaswanth | 2 | 1 Nov | Not done. Timing code merged (`5b4b542`); no live runs |
| V5 | Daily cap on Gnani calls | Jaswanth | 1.5 | 30 Oct | **Done (main)** (`0b898fc`, `8c3c80a`) |
| V6 | Spoken numbers: what Gnani writes, how TTS reads amounts | Jaswanth | inside V7 (0 extra) | 1 Nov | Not done. Amount-to-words built (off); lakh/crore guardrail fix merged; nothing tested live |
| V7 | Voice eval on 30-40 questions (+ answer-quality run if spending is approved) | Jaswanth | 4 | 2 Nov | Not done. Script merged (`f0a8ddc`, 32 questions); no clips |
| V8 | Mic and composer polish from the UI spec | Jaswanth | UNKNOWN | UNKNOWN | Not done. Most merged (`60dc80c`); pre-prompt, "heard" first and playing bar not built |
| V9 | A visible mic on the chat page | Jaswanth | not stated | (3 Nov) | **Done (main)** (`3f48f57`); not live-tested |

### Evaluation and testing

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| E1 | Check demo and site numbers against their PDF pages | Teammate (Tamil and Hindi: skill UNKNOWN) | 3 | 28 Oct | Not done. Sheet of 24 rows; a first pass by Claude is in `claude_first_pass`; no person has confirmed any row |
| E2 | Clean re-run of `results.md` from a pushed commit; Tanglish causes | Jaswanth (laptop) | 2 | 28 Oct | Not done |
| E3 | Tanglish transliteration, only if needed | Jaswanth | 0 or 6 | 2 Nov | Not done (decision pending V1, E2) |
| E4 | Tamil and Hindi native review of the questions | Teammate or volunteer | 6 | 1 Nov | Not done |
| E5 | 3-person user test | Teammate | 4 | 2 Nov | Not done |

### UI

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| U1 | T0: remove unverified facts from the site | Jaswanth | 0.5 | by 3 Nov | **Done (branch)** |
| U2 | T1: proof you can see | Jaswanth | 3.5 | 31 Oct | **Done (branch)** |
| U3 | T2: honest waiting state | Jaswanth | 2.5 | 1 Nov | Not done. Only the 2-minute stop is merged (`11938f4`) |
| U4 | T3: better "I don't know" (includes WP #15) | Jaswanth; teammate checks wording | 2 | 3 Nov | **Done (branch)**. Tamil wording still needs review (U8) |
| U5 | T4: disclaimer on phones | Jaswanth | 0.5 | 1 Nov | **Done (branch)** |
| U6 | T5: home hero "Ask by voice", after voice works end to end | Jaswanth | 1 | UNKNOWN | Not done |
| U7 | T7: hero sample answer card from a real saved answer | Jaswanth | 1 | UNKNOWN | Not done |
| U8 | Native review of key Tamil interface strings | Jaswanth | 1-2 | UNKNOWN | Not done |
| U9 | Tests, ruff, mypy; phone and desktop screenshots | Jaswanth | 1 | UNKNOWN | Not done. Automated checks pass; the screenshot review against the audit is not done |
| U10 | Merge voice and UI work | Jaswanth | 2 | 31 Oct | Not done. Voice merged; PR #3 still a draft |

### Documentation

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| D1 | "Model-judged" wording, n next to percentages | Jaswanth | 1 | 29 Oct | **Done (main)** (`2b75a55`). Word report tracked separately |
| D2 | Hindi coverage stated exactly | Jaswanth | 0.5 | 28 Oct | **Done (main)** (`2b75a55`) |
| D3 | Write-up calls only held-out 2 (n=84) "held out" | Jaswanth | 0.5 | 4 Nov | Not done (write-up not written) |
| D4 | LICENSE, refresh `data_sources.md`, source terms | Jaswanth | 1 | 2 Nov | Not done |
| D5 | README setup plus a tiny sample | Jaswanth | 3 | 2 Nov | Not done. README part done; sample deferred |

### Video and post

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| P1 | Fallback screen recording(s) | Either | 2 | 30 Oct and 3 Nov | Not done |
| P2 | Demo video with English subtitles, then the post | Teammate (editing: skill UNKNOWN) | 10 | video 2 Nov, post Tue 3 Nov (latest Thu 5 Nov) | Not done |

### Submission

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| S1 | Contribution log, same day | Both | 0.5 a day (not in hour totals) | daily | Not done. The log is still empty |
| S2 | Interview practice | Both | 20 min a day (not in hour totals) | daily | Not done (status UNKNOWN) |
| S3 | Repeat the key scan before the repo goes public | Jaswanth | 0.25 | 4 Nov | Not done (first scan 26 Oct, no match) |
| S4 | Ask Gnani when engagement is counted | Jaswanth | 0.25 | 27 Oct | Not done |
| S5 | Teammate accepts the terms email; agree who holds the key | Jaswanth, Teammate | 0.25 | 27 Oct | Not done |
| S6 | Write-up and submission pack | Jaswanth | 3 | 4 Nov | Not done |
| S7 | Submit, after the post is live | Jaswanth only | not stated | Fri 6 Nov (buffer Sat 7, Mon 9; deadline Tue 10 Nov, 11:59 PM IST) | Not done |

**Cut by Jaswanth's decision (not counted):** public hosting, the full 194-question voice eval, a 5-person test, UI beyond the build scope.

### 3.1 Also planned, outside these two files (not counted)

- Update the Word report from `docs/weakness/DOCX_CHANGES.md` (5 Nov). Hours: UNKNOWN.
- Decide the LLM budget (paid key, 40-question subset, or caching).
- Gnani dashboard: credit cost per call; Timbre version.
- Answer cache and an OCR-amount guard design (Jaswanth: after the merges).

---

## 4. Percent of work done

**As of Mon 26 Oct 2026, 12:36 UTC**, from the 38 tasks in section 3.

**Method**
1. Every task counts once; overlapping tasks were merged first.
2. A task counts only when its row says Done. In-progress work counts as not done, even when much of the code is merged (V3, V4, V6, V7, V8, U3).
3. Two figures: **merged into main** only, and **main plus the PR #3 branch**.
4. Tasks done % = done tasks ÷ 38. Hours done % = plan-estimated hours of done tasks ÷ estimated hours of all tasks. Hours are the plans' estimates, not time measured.
5. Tasks with no stated hours (V8, V9, S1, S2, S7) are counted in tasks but not in hours. V6 has 0 extra hours. E3 (0 or 6 h) and U8 (1-2 h) make the hour total a range: 70.75 to 77.75.
6. Percentages are cut to one decimal place, never rounded up.

| Area | Tasks: main | Tasks: main + branch | Est. hours: main | Est. hours: main + branch | Est. hours total |
|---|---|---|---|---|---|
| Voice | 2 of 9 (22.2%) | 2 of 9 (22.2%) | 1.5 (7.8%) | 1.5 (7.8%) | 19 |
| Evaluation and testing | 0 of 5 (0.0%) | 0 of 5 (0.0%) | 0 (0.0%) | 0 (0.0%) | 15 to 21 |
| UI | 0 of 10 (0.0%) | 4 of 10 (40.0%) | 0 (0.0%) | 6.5 (40.6% to 43.3%) | 15 to 16 |
| Documentation | 2 of 5 (40.0%) | 2 of 5 (40.0%) | 1.5 (25.0%) | 1.5 (25.0%) | 6 |
| Video and post | 0 of 2 (0.0%) | 0 of 2 (0.0%) | 0 (0.0%) | 0 (0.0%) | 12 |
| Submission | 0 of 7 (0.0%) | 0 of 7 (0.0%) | 0 (0.0%) | 0 (0.0%) | 3.75 |
| **Overall** | **4 of 38 (10.5%)** | **8 of 38 (21.0%)** | **3 (3.8% to 4.2%)** | **9.5 (12.2% to 13.4%)** | **70.75 to 77.75** |

Working: 4 ÷ 38 = 0.105; 8 ÷ 38 = 0.210. Hours (main): 1.5 (V5) + 1 (D1) + 0.5 (D2) = 3; 3 ÷ 77.75 = 0.038, 3 ÷ 70.75 = 0.042. Hours (main + branch): 3 + 0.5 (U1) + 3.5 (U2) + 2 (U4) + 0.5 (U5) = 9.5; 9.5 ÷ 77.75 = 0.122, 9.5 ÷ 70.75 = 0.134.

**Change since the 11:37 UTC snapshot.** The four done tasks are now merged into `main` (they were on side branches). Four UI tasks are done on the PR #3 branch. Much voice code was added (TTS, timing, voice eval, mic polish), but none of those tasks is finished, because each needs a live run or a decision from Jaswanth.

**What these numbers measure.** Only the final-stretch plan written on 26 Oct, not the core system built before it (section 2).

---

## 5. Project structure

### 5.1 Folder tree (top two levels, `main`)

```
pakkam/
├── .github/workflows/   CI: tests, ruff and mypy on every push
├── data/                sources.json (document list and URLs), contacts.json (official websites and helplines)
│   ├── eval/            questions.jsonl: the 194 draft test questions with gold pages
│   ├── raw/             Source PDFs (downloaded locally, not in the repo)
│   └── processed/       Extracted text and chunks (made locally, not in the repo)
├── deploy/              Hosting files (not deployed)
│   ├── cloudrun/        Google Cloud Run with a GPU
│   └── hf-space/        Hugging Face Space (free CPU)
├── docs/                Report, evaluation method, results, plans, this section
│   ├── review/          Question review sheet, demo number sheet, backend review
│   ├── weakness/        Weakness review, plan, Word report changes
│   └── ux/              UI audit, references, story, recommendations
├── src/schemebot/       The Python package
│   ├── ingest/          PDF to text (OCR when needed), language detection, chunking
│   ├── index/           Embeddings (bge-m3) and the Qdrant store
│   ├── retrieve/        Hybrid search, reranker, Tanglish gloss
│   ├── generate/        LLM answer, prompt, guardrails, refusal messages, contacts
│   ├── api/             FastAPI service, rate limits, audit log
│   ├── evaluation/      Evaluation runner, metrics, judge, review sheet
│   └── voice/           Gnani speech to text and text to speech, call cap, voice scripts
├── tests/               Automated tests (no network, no credits)
└── web/                 The site
    ├── index.html       Home page (story)
    ├── chat/            Chat page
    └── assets/          CSS, JavaScript and images
```

Root files: `README.md`, `STATUS.md` (voice progress), `pyproject.toml` and `uv.lock` (dependencies), `Dockerfile`, `compose.yaml`, `.env.example` (setting names with empty values; the real `.env` is gitignored).

### 5.2 From question to answer

Offline, once: each PDF page is read from its text layer, or through OCR when that layer is broken, split into passages and indexed. **Built.**

| # | Stage | What happens | Status |
|---|---|---|---|
| 1 | Speech in | The user taps the mic (or uploads a clip) and picks a language. The browser records up to 30 s. The server sends it to Gnani speech to text. | **Partly built**: merged, fake tests only, never called live; Tanglish untested |
| 2 | Language detection | Tamil and Hindi by script; Tanglish by a word list and Tamil word endings. | Built |
| 3 | Clean-up and Tanglish gloss | Native digits become 0-9; Tanglish questions get an English gloss. | Built |
| 4 | Retrieval | Search by meaning (dense) and by words (sparse), top 20 each, merged. | Built |
| 5 | Reranking | A second model rescores and keeps the best 5. | Built |
| 6 | Refusal threshold | Below 0.35, Pakkam refuses without calling the LLM and gives the official contact. | Built |
| 7 | Answer with citations | The LLM answers in the question's language; each sentence lists its passages. | Built; seen live on 8 questions only |
| 8 | Guardrails | Cite check, number check (now with lakh/crore), second-model check; failing sentences removed. | Built |
| 9 | Speech out | Listen button sends the answer to Gnani text to speech. | **Partly built**: merged, off until the Timbre version is set, never called live |

---

## 6. Gnani APIs used

| API | Status | Model and version | Details |
|---|---|---|---|
| Speech to text | In code on `main`; **never called live** | Prisma v2.5 (as written in `stt.py` and `config.py`) | `POST https://api.vachana.ai/stt/v3`. Codes `ta-IN`, `hi-IN`, `en-IN`; Tanglish sent as `ta-IN` (untested; Gnani documents no Tanglish code). 30 s clip limit |
| Text to speech | In code on `main`; **switched off, never called live** | Timbre, **version not yet confirmed**: the code accepts `timbre-v2.5` or `timbre-v3.0`. The challenge page names both. Jaswanth chooses after a listening test | `POST /api/v1/tts/inference`, 24 kHz WAV. Voices by language (defaults in `STATUS.md`) |

Both share one daily call cap (default 100, a guess until credit use is measured). The team has 5,000 free Gnani credits; what one call costs is UNKNOWN. No other Gnani API is used.

---

## 7. Results so far

> **No clean run exists yet.** The header of `docs/results.md` still says "commit c050d23 (uncommitted changes)". Task E2 re-runs it from a pushed commit. **The figures below are provisional** and must be replaced before they go into the Word report or the post.

All 194 questions are **draft questions, not yet native-speaker verified** (0 verified). One person wrote all the questions and the system.

**Retrieval and refusal, retrieval-only run** (2026-10-26T09-04-44Z; hybrid, reranker, Tanglish gloss; threshold 0.35; 18 documents, 2,785 chunks):

| Group | Answerable / unanswerable (n) | Recall@1 | Recall@5 | Correct refusal | False refusal |
|---|---|---|---|---|---|
| English | 39 / 10 | 85% | 100% | 90% | 5% |
| Tamil | 38 / 10 | 92% | 100% | 90% | 8% |
| Hindi | 38 / 10 | 79% | 100% | 100% | 8% |
| Tanglish | 39 / 10 | 82% | 92% | 100% | 44% (17 of 39) |
| **All** | 154 / 40 | 84% | 98% (151 of 154) | 95% (38 of 40) | 16% |

- Recall@5: a correct source page was among the 5 retrieved passages. It measures retrieval, **not** answer correctness.
- Correct refusal is out of 10 per group, so one question moves it by 10 points.
- In a retrieval-only run, "refused" means confidence below the threshold; no LLM was called.
- Held-out 2 (q111-q194, n = 84) is the only batch untouched by any tuning.

**Hindi coverage:** 2 Hindi documents, 5 pages, 14 chunks. Most Hindi questions are answered from English or Tamil pages through cross-language retrieval.

**Answers (live smoke test, n = 8, hand-picked):** 5 cited answers, 3 correct refusals. Every answer sentence was **model-judged** faithful; the same model (Gemini 3.1 Flash-Lite) ran the in-pipeline check and the judging, so this is not an independent judge, and no person checked the verdicts. The run's output is not saved in the repo (UNVERIFIED against a file).

**Latency:** retrieval p50 533 ms, p95 720 ms (n = 194, RTX 4060 laptop, provisional run). Full text answer 13 to 52 s on the Gemini free tier (n = 8, no saved output, UNVERIFIED). Voice end to end: **not measured** (timing code exists, no live runs).

**Voice results:** none. No real Gnani call has been made.

---

## 8. Known limits

- **Tanglish false refusals:** 44% (17 of 39, provisional). Causes not yet listed per question (E2). Detection misses 3 of 49 Tanglish questions.
- **Tanglish speech untested;** `ta-IN` is a guess until V1. A ta-IN voice reading Latin Tanglish is also untested.
- **OCR digit errors:** Tamil OCR reads a leading 1 as 4 (Pudhumai Penn Rs.1,000 as 4,000). The guardrail cannot catch this, because the wrong number is in the cited passage. No demo number has been confirmed by a person (E1).
- **Small samples:** 194 draft questions, 10 unanswerable per group, all unverified; ten incomplete labels already found and fixed.
- **Answer quality seen on 8 questions only;** a full run needs a paid key.
- **Latency not measured** for voice; text answer time has no saved output.
- **Spoken numbers:** the guardrail now matches "2.5 lakh" with "2,50,000", but other number words ("six thousand") are not converted, and what Gnani writes for spoken amounts is UNKNOWN. How Timbre reads "Rs.1,000" is UNKNOWN.
- **Voice tested only with fakes** in a headless browser; no real phone or iPhone Safari.
- **Near misses** (for example "next PM-KISAN instalment date") pass retrieval; only the LLM refuses them.
- **Results not reproducible yet** (E2).
- **UI fixes not merged** (PR #3); waiting state (T2) not built.
- **No fallback recording** (P1), **no user test** (E5).
- **Reviewers cannot run it from the repo alone:** no PDFs or index in the repo (D5).
- **Scope:** 18 documents, one state plus three central schemes; answers reflect the documents' dates.
- **The Word report** still has the old wording listed in `DOCX_CHANGES.md`.

---

## 9. Team and contributions

Built only from `docs/CONTRIBUTIONS.md` and `git log` on `main`, at the snapshot.

- **`docs/CONTRIBUTIONS.md`:** header row only. **No entries yet, for either team member.**
- **Teammate:** no commits and no log entries. The teammate's name is not in the sources (UNKNOWN). **The teammate's contribution cannot be stated from the record yet.**

| Author name in git | Commits on `main` | What the commits change |
|---|---|---|
| jazz_716 (same account email as Jaswanth) | 12 | The text system: ingestion, retrieval, answers, API, web app, evaluation, deployment files, CI fix, the Word report |
| Jaswanth | 9 | Voice: speech to text, call cap, compare script, TTS, listening test, timings, voice eval, amounts to words, mic polish, a STATUS note |
| JASWANTH S S | 5 | Pull request merges (#1, #2, #4, #5, #6) |
| Claude (an AI coding assistant) | 31 | Documentation (reviews, plans, checklist, UX, this section) and the backend fixes from the review (PR #6) |

Who wrote, reviewed or directed each commit beyond the author field is not recorded, so this section does not say.

---

## 10. Risks and what we will do about them

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Gnani gives poor transcripts for Tanglish | The voice demo fails for Tanglish | Test early (V1, clips by 28 Oct, hard stop 1 Nov); transliteration only if needed (E3); otherwise keep Tanglish demo to tested questions and state the 44% (n = 39) | Jaswanth |
| A wrong OCR amount reaches the demo or the site | A reviewer finds a different number in the PDF | A person confirms every demo number (E1); T0 already hides unchecked facts (branch); OCR-amount guard design after the merges | Teammate, Jaswanth |
| Gnani credits run out | No more voice tests or demo | Daily cap (done); no Gnani in tests; ask before each real run; check credit cost in the dashboard | Jaswanth |
| TTS version or quality not settled | No speech out in the video | Listening test first; Tanglish options A-D in `STATUS.md`; fallback recording (P1) | Jaswanth |
| LLM free tier (20 requests a day per model) | Answer quality stays at n = 8 | Paid key, 40-question subset, or caching. Spending is Jaswanth's decision | Jaswanth |
| Teammate's skills and registration unconfirmed | Teammate tasks stall; contribution section empty | Confirm the terms email (S5); flexible tasks; same-day log (S1) | Jaswanth, Teammate |
| Post goes live too late | Engagement missed | Post Tue 3 Nov, latest Thu 5 Nov; ask Gnani about the cutoff (S4) | Teammate, Jaswanth |
| Diwali week (Sun 8 Nov; Sat 7 Nov in Tamil Nadu UNKNOWN) | Less time near the deadline | Submit Fri 6 Nov; Sat 7 and Mon 9 as buffers | Jaswanth |
| PR #3 drifts from `main` again | New merge conflicts in `chat.js` | Review and merge PR #3 soon; `main` is already merged into it | Jaswanth |
| Claims go beyond the evidence | Loss of trust | "Do not claim" list (plan §4); n with every percentage; replace provisional figures after E2 | Both |

---

*Sources: `STATUS.md`, `docs/weakness/WEAKNESS_PLAN.md`, `docs/weakness/STEP1_VERIFY.md`, `docs/SUBMISSION_CHECKLIST.md`, `docs/weakness/DOCX_CHANGES.md`, `docs/CONTRIBUTIONS.md`, `docs/ux/UX_RECOMMENDATIONS.md`, `docs/ux/STORY_AND_FLOW.md`, `docs/review/demo-numbers.csv`, `docs/review/BACKEND_REVIEW.md`, `docs/results.md`, `docs/report.md`, the code, the Word report's disclaimer, and `git log`. `STATUS.md` still says "Own target: 8 Nov"; the newer plan's target is Fri 6 Nov, which this section uses.*
