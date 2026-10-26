# Project status, plan and structure

*Draft for the Pakkam project report (Word). Markdown first, for review. Nothing here has been copied into the .docx yet.*

**Snapshot taken: Mon 26 Oct 2026, 11:42 UTC (5:12 PM IST).** Other work is still going on, so this section describes the repository at these commits:

| Branch | What it holds | Commit |
|---|---|---|
| `main` | The text RAG system, web app, evaluation, project report | `35ba419` |
| `claude/project-thread-fpld2g` | Voice input (Gnani speech to text), `STATUS.md` | `36573ee` |
| `claude/project-thread-15p3u0` | Weakness review, plan, submission checklist, doc fixes, `CONTRIBUTIONS.md` | `8912cfa` |
| `claude/project-thread-i98lxh` | UI/UX audit and recommendations (PR #1) | `5494278` |

None of the three side branches has been merged into `main` yet.

**Labels used here.** UNKNOWN: not in the sources. UNVERIFIED: written down, but not yet checked against the source. ESTIMATE: a guess, not a measurement. All hours are estimates.

**Disclaimer (wording kept from the Word report):** an independent student project. It is not an official government service and is not affiliated with any government body. Answers are informational only and must be checked against the official source before acting on them.

---

## 1. Summary

Pakkam answers questions about Indian government welfare schemes using only 18 public scheme documents. Every sentence in an answer cites the document and page it comes from. When the documents do not answer the question, Pakkam says so and points to the official website or helpline. People can ask in Tamil, Hindi, English or Tanglish (Tamil written in English letters), and the answer comes back in the same language. It is for people who hear about a scheme, for example through a forwarded message, and want to check what the official document says. Pakkam is a student project built by a team of two for the Great Indian AI Internship Challenge by Gnani.ai. It is **not** an official or government service. It is **not** affiliated with any government body, and **not** affiliated with Gnani.ai: it uses Gnani's speech-to-text API as a challenge entrant. It does not process applications, store personal data or give official advice.

---

## 2. What is built today

"Tested" below means automated tests with no network calls, unless it says "live". On the snapshot date: **190 tests pass on `main`** and **235 pass on the voice branch** (both re-run for this section on 26 Oct, with the slow tests deselected as the project does by default).

### 2.1 Built and tested

| Feature | Where | Evidence |
|---|---|---|
| Reading PDFs, with OCR for broken Tamil and Hindi pages | `src/schemebot/ingest/` | `tests/test_extract.py`, `test_chunk.py`, `test_langid.py`, `test_ocr_cache.py`, `test_pipeline.py`. Real run: 18 documents, 2,688 pages, 1,353 pages through OCR, 2,785 chunks (`docs/report.md` §3) |
| Search index (bge-m3 dense and sparse vectors in Qdrant) | `src/schemebot/index/` | `tests/test_index.py` |
| Hybrid search, reranking, Tanglish gloss | `src/schemebot/retrieve/` | `tests/test_retrieve.py`, `test_tanglish.py`. Retrieval-only run on 194 draft questions (`docs/results.md`; see section 7 for why those numbers are provisional) |
| Refusal threshold (refuse if reranker confidence is below 0.35) | `src/schemebot/config.py` | `tests/test_config.py`; correct refusal and false refusal in `docs/results.md` |
| Answer with citations (Claude or Gemini) | `src/schemebot/generate/answer.py`, `prompt.py`, `gemini.py` | `tests/test_answer.py`, `test_gemini.py`. Live smoke test on 8 hand-picked questions (`docs/report.md` §8) |
| Guardrails (every sentence must cite a shown passage, its numbers must appear in that passage, a second model must agree) | `src/schemebot/generate/guardrails.py` | `tests/test_guardrails.py`; the 8-question live smoke test |
| API: `POST /ask`, `GET /health`, `GET /sources`, rate limits, audit log that stores a hash, never the question text | `src/schemebot/api/` | `tests/test_api.py`, `test_ratelimit.py` |
| Official contact for refusals | `data/contacts.json`, `generate/contacts.py` | `tests/test_contacts.py` |
| Evaluation script and native-speaker review sheet (export and import) | `src/schemebot/evaluation/` | `tests/test_evaluation.py`, `test_review.py`; `docs/review/questions-review.csv` (194 rows) |
| Web home page and chat page | `web/` | Screenshots on phone and desktop in the UI audit (`docs/ux/UI_AUDIT.md`, PR #1). Answers there were stubbed, because the index and an LLM key are not in the test container |
| CI (tests, ruff, mypy) | `.github/workflows/ci.yml` | Commit `04ca323` fixed a CI failure (mypy). Current CI state on GitHub: UNVERIFIED for this section |
| Gnani call cap (daily limit on speech calls, kept across restarts) | `src/schemebot/voice/budget.py` (voice branch) | `tests/test_voice_budget.py` (fake speech service, no credits used) |

### 2.2 Built but not tested live

| Feature | Where | What is missing |
|---|---|---|
| Ask by voice: mic button (16 kHz WAV, stops at 30 s), upload button, "I will speak in" picker | `web/assets/recorder.js`, `chat.js`, `web/chat/index.html` (voice branch) | Checked only in a headless browser with a fake mic and fake speech service (`STATUS.md`). No real phone, no iPhone Safari |
| Gnani speech to text client and `POST /ask/voice` | `src/schemebot/voice/stt.py`, `api/main.py` (voice branch) | `tests/test_stt.py`, `test_api.py` use a fake. **Never called against real Gnani** (`STATUS.md`) |
| Clip comparison script (`python -m schemebot.voice compare`) | `src/schemebot/voice/compare.py` (voice branch) | `tests/test_voice_compare.py` with a fake. Not yet run on real clips |
| Deployment files for Cloud Run and a Hugging Face Space | `deploy/cloudrun/`, `deploy/hf-space/`, `Dockerfile`, `compose.yaml` | Nothing is deployed. Public hosting was cut from the plan |

### 2.3 Not built

- Speech out (Gnani Timbre text to speech).
- End-to-end latency timing for each stage.
- Voice evaluation (transcript accuracy, spoken numbers).
- Converting spoken number words ("six thousand", "2.5 lakh") into digits.
- Tanglish transliteration before reranking (only if the speech test shows it is needed).
- An answer cache.
- The tiny public sample that lets a reviewer run Pakkam without the full PDFs.
- A `LICENSE` file.
- The UI fixes T0 to T7 (section 3).
- The fallback demo recording, the demo video and the post.

---

## 3. What is planned

Every remaining task from `WEAKNESS_PLAN.md` (§1 and §2) and `UX_RECOMMENDATIONS.md` (§2 and §4), merged so that nothing is counted twice. Rows that the plans mark done are included, so the percentages in section 4 can be checked. Owners and dates are copied from the plans. "Teammate" is the second team member, whose name and skills are UNKNOWN in the sources; the plan says teammate tasks can move to Jaswanth until skills are confirmed.

Status: **Done**, **Not done**. Anything in progress is counted as Not done.

### Voice

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| V1 | Real Gnani speech test: 5-10 Tanglish clips, ta-IN vs en-IN, compare by hand (WP #1) | Jaswanth | 3 | 27 Oct in the plan; `STATUS.md` moves clip recording to Wed 28 Oct, hard stop Sun 1 Nov | Not done. Script built; waiting on clips |
| V2 | 1-2 noisy or phone-quality clips in the test (WP #1b) | Jaswanth | 0.5 | 27 Oct | Not done |
| V3 | Timbre text to speech: confirm version, client, endpoint, play button, tests (WP #5) | Jaswanth | 8 | 31 Oct | Not done |
| V4 | Time every stage on live voice runs; report median and max with n (WP #6) | Jaswanth | 2 | 1 Nov | Not done |
| V5 | Separate daily cap on Gnani calls (WP #6b) | Jaswanth | 1.5 | 30 Oct | **Done** on the voice branch (`0b898fc`, tested with a fake). Not merged |
| V6 | Spoken numbers: what Gnani writes, how TTS reads amounts (WP #7) | Jaswanth | inside V7 (0 extra) | 1 Nov | Not done |
| V7 | Voice eval on 30-40 questions, plus the answer-quality run if spending is approved (WP #8) | Jaswanth | 4 | 2 Nov | Not done |
| V8 | Mic and composer polish from the UI spec (UX T6, `STATUS.md` Next #5) | Jaswanth (voice work) | UNKNOWN | UNKNOWN | Not done; waits for go-ahead |
| V9 | A visible mic on the chat page (UI audit #1, WP #13) | Jaswanth | not stated | (WP #13: 3 Nov) | **Done** on the voice branch (`3f48f57`). Not live-tested |

### Evaluation and testing

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| E1 | Check every demo and home-page number against its PDF page, including the three UNVERIFIED facts (WP #2, UX Day 1) | Teammate (reading Tamil and Hindi: skill UNKNOWN) | 3 | 28 Oct | Not done |
| E2 | Clean re-run of `docs/results.md` from a committed tree; list the cause of each Tanglish false refusal (WP #3) | Jaswanth | 2 | 28 Oct | Not done |
| E3 | Tanglish transliteration, only if V1 and E2 show it is needed (WP #9) | Jaswanth | 0 or 6 | 2 Nov | Not done (decision pending) |
| E4 | Tamil and Hindi native review of the questions (WP #10) | Teammate or a volunteer reviewer | 6 | 1 Nov | Not done |
| E5 | 3-person user test (WP #12; UX Day 3 is the same test) | Teammate | 4 | 2 Nov | Not done |

### UI (build scope: audit #1, #3, #6, #9 and a better refusal screen)

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| U1 | T0: remove UNVERIFIED facts from the site | Jaswanth | 0.5 | by 3 Nov (WP #13) | Not done |
| U2 | T1: proof you can see (page number on the chip, source line, phone sheet backdrop) | Jaswanth | 3.5 | 31 Oct | Not done |
| U3 | T2: honest waiting state (timer, slow note, cancel, retry) | Jaswanth | 2.5 | 1 Nov | Not done |
| U4 | T3: better "I don't know" with the official link and the covered-scheme list (also covers WP #15) | Jaswanth; teammate checks Tamil and Hindi wording | 2 | 3 Nov | Not done |
| U5 | T4: disclaimer on phones | Jaswanth | 0.5 | 1 Nov | Not done |
| U6 | T5: home hero "Ask by voice", after voice works end to end | Jaswanth | 1 | UNKNOWN | Not done (second to cut) |
| U7 | T7: hero sample answer card, from a real saved answer | Jaswanth | 1 | UNKNOWN | Not done (first to cut) |
| U8 | Native review of the key Tamil interface strings (UX §7) | Jaswanth (UX update, 26 Oct) | 1-2 | UNKNOWN | Not done |
| U9 | Run tests, ruff, mypy; check phone and desktop screenshots (UX Day 3) | Jaswanth | 1 | UNKNOWN | Not done |
| U10 | Merge the voice branch and the UX work (WP #13, schedule Sat 31 Oct; hours from `STEP1_VERIFY.md` E18) | Jaswanth | 2 | 31 Oct | Not done |

### Documentation

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| D1 | Say "model-judged", show n next to percentages (WP #4) | Jaswanth | 1 | 29 Oct | **Done** in README, `report.md`, `evaluation.md` (`2b75a55`, weakness branch). The Word report is tracked separately (section 3.1) |
| D2 | State Hindi coverage exactly (WP #17e) | Jaswanth | 0.5 | 28 Oct | **Done** in README and `report.md` §3 (`2b75a55`) |
| D3 | Write-up calls only held-out 2 (n=84) "held out"; one person wrote all questions (WP #11) | Jaswanth | 0.5 | 4 Nov | Not done. `report.md` already says it; the submission write-up does not exist yet |
| D4 | Licences: LICENSE file, refresh `docs/data_sources.md`, record source terms (WP #17c) | Jaswanth | 1 | 2 Nov | Not done. Licence choice (MIT or Apache-2.0) is Jaswanth's |
| D5 | README setup steps plus a tiny sample (WP #17d) | Jaswanth | 3 | 2 Nov | Not done. README part done; sample script deferred |

### Video and post

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| P1 | Fallback screen recording(s) of the demo (WP #14) | Either | 2 | first 30 Oct, second 3 Nov | Not done |
| P2 | Demo video with English subtitles, then the post (WP #18; includes UX's script and subtitle tasks) | Teammate (video editing: skill UNKNOWN) | 10 | video 2 Nov, post Tue 3 Nov (latest Thu 5 Nov) | Not done |

### Submission

| ID | Task | Owner | Hours (ESTIMATE) | Planned date | Status |
|---|---|---|---|---|---|
| S1 | Contribution log, one row the same day as the work (WP #16) | Both | 0.5 a day (left out of the hour totals) | daily | Not done. The log is empty |
| S2 | Interview practice (WP #17) | Both | 20 min a day (left out of the hour totals) | daily from 26 Oct | Not done. Status UNKNOWN beyond the checklist's open box |
| S3 | Repeat the key scan before the repo goes public (WP #17b) | Jaswanth | 0.25 | 4 Nov | Not done. First scan done 26 Oct, no match |
| S4 | Ask Gnani when engagement is counted (WP #17f) | Jaswanth | 0.25 | 27 Oct | Not done |
| S5 | Teammate accepts the terms email; agree who holds the key (WP #17g) | Jaswanth, Teammate | 0.25 | 27 Oct | Not done |
| S6 | Write-up and submission pack (WP schedule 4 Nov; hours from `STEP1_VERIFY.md` E18) | Jaswanth (drafted from the contribution log) | 3 | 4 Nov | Not done |
| S7 | Submit, after confirming the post is live (WP schedule) | Jaswanth only | not stated | Fri 6 Nov (buffer Sat 7, last resort Mon 9; deadline Tue 10 Nov, 11:59 PM IST) | Not done |

**Cut by Jaswanth's decision (not counted):** public hosting, the full 194-question voice eval, a 5-person test (now 3), UI work beyond the build scope, the full home page rewrite and full interface translation.

### 3.1 Also planned, but outside these two files (not counted)

From `SUBMISSION_CHECKLIST.md` and `DOCX_CHANGES.md`:
- Update the Word report with the 14 wording changes in `DOCX_CHANGES.md` (5 Nov). Hours: UNKNOWN.
- Decide the LLM budget: paid key, a 40-question subset, or caching (Jaswanth).
- Check the Gnani dashboard: what a credit buys, which Timbre version is current (Jaswanth).
- Re-read the challenge page before submitting.

---

## 4. Percent of work done

**As of Mon 26 Oct 2026, 11:42 UTC**, from the 38 tasks in section 3.

**Method**
1. Every task in section 3 counts once. Tasks that overlap between the two plans were merged first (for example, WP #13 is split into V9 and U1-U10, and WP #15 is inside U4).
2. A task is done only when its row says **Done**. In-progress work counts as not done. 4 tasks are done: V5, V9, D1, D2. V5 and V9 are on the voice branch and D1 and D2 on the weakness branch; none is merged into `main` yet.
3. **Tasks done %** = done tasks ÷ all tasks.
4. **Hours done %** = estimated hours of done tasks ÷ estimated hours of all tasks. These are the plans' estimates, not measured time. Tasks with no stated hours (V8, V9, S1, S2, S7) are counted in tasks but left out of hours. V6 is 0 extra hours because the plan puts it inside V7.
5. Two tasks have a range: E3 is 0 or 6 hours, U8 is 1-2 hours. So the hour totals are a range, and hours-done % is given for both ends.
6. Percentages are cut to one decimal place, never rounded up.

| Area | Tasks done | Tasks done % | Est. hours done | Est. hours total | Hours done % (ESTIMATE) |
|---|---|---|---|---|---|
| Voice | 2 of 9 | 22.2% | 1.5 | 19 | 7.8% |
| Evaluation and testing | 0 of 5 | 0.0% | 0 | 15 to 21 | 0.0% |
| UI | 0 of 10 | 0.0% | 0 | 15 to 16 | 0.0% |
| Documentation | 2 of 5 | 40.0% | 1.5 | 6 | 25.0% |
| Video and post | 0 of 2 | 0.0% | 0 | 12 | 0.0% |
| Submission | 0 of 7 | 0.0% | 0 | 3.75 | 0.0% |
| **Overall** | **4 of 38** | **10.5%** | **3** | **70.75 to 77.75** | **3.8% to 4.2%** |

Working for the overall row: 4 ÷ 38 = 0.1052, so 10.5%. Hours: 1.5 (V5) + 1 (D1) + 0.5 (D2) = 3. 3 ÷ 77.75 = 0.0385, so 3.8%. 3 ÷ 70.75 = 0.0424, so 4.2%.

**What these numbers do and do not measure.** They measure the remaining-work plan written on 26 Oct. They do **not** include the core system built before that plan (ingestion, retrieval, guardrails, API, web app, evaluation, voice input), which section 2 lists. So 10.5% means "10.5% of the final-stretch tasks", not "10.5% of Pakkam".

---

## 5. Project structure

### 5.1 Folder tree (top two levels)

```
pakkam/
├── .github/workflows/   CI: tests, ruff and mypy on every push
├── data/                Inputs: sources.json (document list and URLs), contacts.json (official websites and helplines)
│   ├── eval/            questions.jsonl: the 194 draft test questions with gold pages
│   ├── raw/             Source PDFs (downloaded locally, not in the repo)
│   └── processed/       Extracted text and chunks (made locally, not in the repo)
├── deploy/              Hosting files (not deployed)
│   ├── cloudrun/        Google Cloud Run with a GPU
│   └── hf-space/        Hugging Face Space (free CPU)
├── docs/                Report, evaluation method, results, data sources
│   ├── review/          questions-review.csv for native-speaker checks
│   ├── weakness/        Weakness review and plan (weakness branch only)
│   └── ux/              UI audit, references, story, recommendations (UX branch only)
├── src/schemebot/       The Python package
│   ├── ingest/          PDF to text (OCR when needed), language detection, chunking
│   ├── index/           Embeddings (bge-m3) and the Qdrant store
│   ├── retrieve/        Hybrid search, reranker, Tanglish gloss
│   ├── generate/        LLM answer, prompt, guardrails, refusal messages, contacts
│   ├── api/             FastAPI service, rate limits, audit log
│   ├── evaluation/      Evaluation runner, metrics, judge, review sheet
│   └── voice/           Gnani speech to text, call cap, clip compare (voice branch only)
├── tests/               Automated tests (no network, no credits)
└── web/                 The site
    ├── index.html       Home page (story)
    ├── chat/            Chat page
    └── assets/          CSS, JavaScript and images
```

Root files: `README.md`, `pyproject.toml` and `uv.lock` (dependencies), `Dockerfile` and `compose.yaml`, `.env.example` (setting names with empty values; the real `.env` is gitignored). `STATUS.md` (voice progress) is on the voice branch only.

### 5.2 From question to answer

Offline, once: each PDF page is read from its text layer, or through OCR when that layer is broken. The text is split into passages and stored in a search index. **Built.**

Then, for each question:

| # | Stage | What happens | Status |
|---|---|---|---|
| 1 | Speech in | The user taps the mic (or uploads a clip) and picks a language. The browser records up to 30 s of WAV. The server sends it to Gnani speech to text and gets the text back. | **Partly built**: in code with fake tests, never called live; Tanglish handling untested |
| 2 | Language detection | Tamil and Hindi by script; Tanglish by a word list and Tamil word endings. This sets the answer language. | Built |
| 3 | Clean-up and Tanglish gloss | Digits in Tamil or Devanagari become 0-9. Tanglish questions get an English gloss of their everyday words. | Built |
| 4 | Retrieval | The question is searched by meaning (dense) and by words (sparse), top 20 each, and the two lists are merged. | Built |
| 5 | Reranking | A second model rescores the candidates and keeps the best 5. | Built |
| 6 | Refusal threshold | If the best passage scores below 0.35, Pakkam refuses without calling the LLM, and gives the official contact. | Built |
| 7 | Answer with citations | The LLM (Claude or Gemini) writes the answer in the question's language. Each sentence lists the passages it relies on. | Built; seen live on 8 questions only |
| 8 | Guardrails | Each sentence must cite a passage that was shown, each number must appear in that passage, and a second model must agree. Failing sentences are removed. If none are left, Pakkam refuses. | Built |
| 9 | Speech out | The answer would be read aloud with Gnani Timbre text to speech. | **Not built** |

---

## 6. Gnani APIs used

| API | Status | Model and version | Details |
|---|---|---|---|
| Speech to text | Called in code today; **never called live** | Prisma v2.5 (as written in `stt.py` and `config.py`) | `POST https://api.vachana.ai/stt/v3`, multipart upload. Language codes: `ta-IN`, `hi-IN`, `en-IN`. Tanglish is sent as `ta-IN`, an untested choice, because Gnani documents no Tanglish code. Clip limit 30 s. Daily call cap, default 100 (a guess until credit use is measured) |
| Text to speech | Planned (V3), **not built** | Timbre, **version not yet confirmed**. The challenge page says "Timbre v2.5 (Beta)" in one place and v3.0 in another. To be checked in the Gnani dashboard | — |

No other Gnani API is used. The team has 5,000 free Gnani credits; what one call costs in credits is UNKNOWN.

---

## 7. Results so far

> **No clean run exists yet.** The header of `docs/results.md` says the run was made on "commit c050d23 (uncommitted changes)", so it cannot be traced to a commit. Task E2 re-runs it from a clean commit. **The figures below are provisional.** They are shown so the reviewer can see the shape of the results; they must be replaced from the clean run before they go into the Word report or the post.

All 194 questions are **draft questions, not yet native-speaker verified** (0 verified). One person wrote all the questions and the system.

**Retrieval and refusal, retrieval-only run** (run 2026-10-26T09-04-44Z; hybrid search, reranker and Tanglish gloss on; threshold 0.35; 18 documents, 2,785 chunks):

| Group | Answerable / unanswerable (n) | Recall@1 | Recall@5 | Correct refusal | False refusal |
|---|---|---|---|---|---|
| English | 39 / 10 | 85% | 100% | 90% | 5% |
| Tamil | 38 / 10 | 92% | 100% | 90% | 8% |
| Hindi | 38 / 10 | 79% | 100% | 100% | 8% |
| Tanglish | 39 / 10 | 82% | 92% | 100% | 44% (17 of 39) |
| **All** | 154 / 40 | 84% | 98% (151 of 154) | 95% (38 of 40) | 16% |

- Recall@5 means a correct source page was among the 5 retrieved passages. It measures retrieval, **not** whether the written answer is correct.
- Correct refusal is out of 10 unanswerable questions per group, so one question moves it by 10 points.
- In a retrieval-only run, "refused" means retrieval confidence was below the threshold; no LLM was called.
- Held-out 2 (q111-q194, n = 84) is the only batch untouched by any tuning.

**Hindi coverage:** 2 Hindi documents, 5 pages, 14 chunks. Most Hindi questions are answered from English or Tamil pages through cross-language retrieval, with the answer in Hindi.

**Answers (live smoke test, n = 8, hand-picked):** 5 cited answers and 3 correct refusals. Every answer sentence was **model-judged** faithful. The same model (Gemini 3.1 Flash-Lite) ran the in-pipeline check and the judging, so this is not an independent judge, and no person checked the verdicts. This is a smoke test, not an evaluation. The run's output is not saved in the repo (UNVERIFIED against a file).

**Latency:**
- Retrieval only: p50 533 ms, p95 720 ms, n = 194, on a laptop with an RTX 4060 (8 GB) (provisional run above).
- Full text answer: 13 to 52 s per answer on the Gemini free tier, including retries (n = 8; no saved output, UNVERIFIED).
- Voice end to end (speech in to answer): **not measured.**

**Voice results:** none yet. No real Gnani call has been made.

---

## 8. Known limits

Still open on the snapshot date (from `STEP1_VERIFY.md` and the plan):

- **Tanglish false refusals:** 44% of answerable Tanglish questions are refused (17 of 39, provisional run). Most have the right page retrieved but score under the threshold. The cause of each one is not yet listed (E2). Language detection also misses 3 of 49 Tanglish questions.
- **Tanglish speech is untested.** Gnani documents no Tanglish code; `ta-IN` is a guess until V1.
- **OCR digit errors:** Tamil OCR reads a leading 1 as 4 (for example Pudhumai Penn Rs.1,000 as 4,000). The guardrail cannot catch this, because the wrong number is in the cited passage. No demo number has been checked against its PDF page yet (E1).
- **Small samples:** 194 draft questions, 10 unanswerable per language group. All labels are unverified, and ten incomplete labels have already been found and fixed.
- **Answer quality seen on 8 questions only.** A full run needs a paid key; the free tier allows 20 requests a day per model.
- **Latency not yet measured** for voice, and the text answer time has no saved output.
- **No speech out** (TTS not built).
- **Spoken numbers:** number words are not converted to digits. The guardrail's number check matches digits only, so "2.5 lakh" against "2,50,000" would be wrongly removed. What Gnani writes for spoken amounts is UNKNOWN.
- **Mic tested only with a fake** in a headless browser; no real phone or iPhone Safari. The 30 s length check works for WAV only, so a long uploaded MP3 is not caught.
- **Near misses:** questions next to a covered topic (for example "next PM-KISAN instalment date") pass the retrieval check; only the LLM's own judgement refuses them.
- **Coverage is not shown to users:** the refusal text does not list the covered schemes (U4).
- **Results not reproducible yet:** `results.md` came from an uncommitted tree (E2).
- **UI blockers for the video:** the source page reads like a footnote, the waiting state looks frozen, and the disclaimer is hidden on phones (U2, U3, U5).
- **No fallback demo recording** (P1) and **no user test** (E5).
- **Reviewers cannot run it from the repo alone:** the PDFs and index are not in the repo (D5).
- **Scope:** 18 documents, one state plus three central schemes. Rules change, and answers reflect the documents' dates.
- **The Word report** still has the old wording listed in `DOCX_CHANGES.md`.

---

## 9. Team and contributions

Built only from `docs/CONTRIBUTIONS.md` (weakness branch) and `git log --all`, at the snapshot.

- **`docs/CONTRIBUTIONS.md`:** the log has its header row only. **No entries yet, for either team member.**
- **Teammate:** no commits under any name other than the ones below, and no log entries. The teammate's name is not in the sources (UNKNOWN). **The teammate's contribution cannot be stated from the record yet.**
- **Commits by author name** (all branches):

| Author name in git | Commits | Dates | What the commits change |
|---|---|---|---|
| jazz_716 (same account email as Jaswanth) | 12 | 25-26 Oct | The whole text system: ingestion, retrieval, answers, API, web app, evaluation, deployment files, CI fix, the Word report |
| Jaswanth | 2 | 26 Oct | Voice input: Gnani speech to text, call cap, compare script |
| Claude (an AI coding assistant) | 14 | 26 Oct | Documentation only: weakness review, plan, checklist, doc fixes, UX audit and recommendations, `STATUS.md` notes |

The commit for this file will add one more "Claude" documentation commit. Who wrote, reviewed or directed each commit beyond the author field is not recorded, so this section does not say.

---

## 10. Risks and what we will do about them

| Risk | Impact | Mitigation | Owner |
|---|---|---|---|
| Gnani gives poor transcripts for Tanglish | The headline voice demo fails for Tanglish | Test early (V1, clips by 28 Oct, hard stop 1 Nov). Transliteration only if needed (E3). Otherwise keep Tanglish demo questions to tested ones and state the 44% (n = 39) | Jaswanth |
| A wrong OCR amount reaches the demo or the site | A reviewer opens the PDF and finds a different number | Check every demo number against its page (E1); remove unverified facts (U1) | Teammate, Jaswanth |
| Gnani credits run out | No more voice tests or demo | Daily call cap (V5, done); never call Gnani in tests; ask before each real run; check credit use in the dashboard | Jaswanth |
| TTS (8 h, ESTIMATE) slips | No speech out in the video | Cut list in the plan; record a fallback demo as soon as voice in works (P1) | Jaswanth |
| LLM free tier (20 requests a day per model) | Answer quality stays at n = 8 | Paid key, a 40-question subset, or caching (plan §6). Spending is Jaswanth's decision | Jaswanth |
| Teammate's skills and registration are unconfirmed | Teammate tasks stall; the contribution section is empty | Confirm the terms email (S5); keep teammate tasks flexible; log work the same day (S1) | Jaswanth, Teammate |
| Post goes live too late | Engagement counts less or misses the cutoff | Post Tue 3 Nov, latest Thu 5 Nov; ask Gnani about the cutoff (S4) | Teammate, Jaswanth |
| Diwali week (Lakshmi Puja Sun 8 Nov; Sat 7 Nov may be a holiday in Tamil Nadu, UNKNOWN) | Less working time near the deadline | Submit Fri 6 Nov; Sat 7 and Mon 9 Nov as buffers | Jaswanth |
| Voice and UI branches both change `chat.js` | Merge conflicts, broken chat page | Merge the voice branch first (U10); UI work built on top of it | Jaswanth |
| Claims go beyond the evidence | Loss of trust with reviewers and interviewers | Follow the "do not claim" list (plan §4); show n with every percentage; replace provisional figures from the clean run (E2) | Both |

---

*Sources: `STATUS.md` (voice branch), `docs/weakness/WEAKNESS_PLAN.md`, `docs/weakness/STEP1_VERIFY.md`, `docs/SUBMISSION_CHECKLIST.md`, `docs/weakness/DOCX_CHANGES.md`, `docs/CONTRIBUTIONS.md` (weakness branch), `docs/ux/UX_RECOMMENDATIONS.md`, `docs/ux/STORY_AND_FLOW.md` (UX branch), `docs/results.md`, `docs/report.md`, the code, the Word report's disclaimer, and `git log --all`. Note: `STATUS.md` still says "Own target: 8 Nov"; the newer plan's target is Fri 6 Nov, which this section uses.*
