<div align="center">

# Pakkam · பக்கம்

**Ask about an Indian government scheme in your own language.<br>
See the exact page of the official document behind every sentence.**

Tamil · Hindi · English · Tanglish &nbsp;|&nbsp; text or voice (Gnani Prisma + Timbre) &nbsp;|&nbsp; the official page as proof, or honestly "I don't know"

[![CI](https://github.com/mailtojaswanthss-svg/pakkam/actions/workflows/ci.yml/badge.svg)](https://github.com/mailtojaswanthss-svg/pakkam/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-3776AB)
![Tests](https://img.shields.io/badge/tests-658%20passing-2E7D32)
![License](https://img.shields.io/badge/code-MIT-5A36A3)
![Status](https://img.shields.io/badge/status-research%20prototype-E3A33B)

[**Live site**](https://pakkam-alpha.vercel.app) · [For judges](#for-judges) · [How it works](#how-it-works) · [Results](#results) · [Quickstart](#quickstart) · [Status](STATUS.md)

</div>

<p align="center">
  <img src="docs/img/home-desktop.png" alt="Pakkam home page: Tap. Ask. See the proof. Ask in your language. Get the answer with its proof." width="100%">
</p>

> **Disclaimer.** An independent student research prototype. It is **not** an official
> service and is **not affiliated with any government body**. Answers are informational
> only: check the official source before acting on them. It uses only public documents
> (listed in [docs/sources.csv](docs/sources.csv)) and stores no personal data
> ([docs/PRIVACY.md](docs/PRIVACY.md)).

---

## For judges

| | |
|---|---|
| **60-second demo, in order** | 1. Paste the "Rs.2,000 + OTP" rumour into *Check a forward* → 2. ask about the scheme in Tamil, by voice → 3. read the answer and its sources → 4. open the Government Order page, line highlighted → 5. ask something the documents do not cover → 6. Pakkam refuses honestly. |
| **Backup video (40 s)** | [docs/judge/pakkam-demo.mp4](docs/judge/pakkam-demo.mp4), in case the live server is down |
| **Pitch deck (7 slides)** | [docs/judge/pakkam-pitch-deck.pdf](docs/judge/pakkam-pitch-deck.pdf) |
| **How an answer is made** | [docs/judge/architecture.png](docs/judge/architecture.png) (made in FigJam) |
| **How we tested** | [docs/review/LIVE_BENCHMARK.md](docs/review/LIVE_BENCHMARK.md): 194 questions, 98% cite the correct page, 39 of 40 out-of-scope refused, and the one miss explained |
| **Design** | Figma file "Pakkam Illustrations": variables (dark/light), text styles, components, every page, motion, the aurora shader |

<p align="center"><img src="docs/judge/architecture.png" alt="Pipeline: question, Gnani Prisma, language detection, hybrid search over 18 official documents, reranker, a check that the pages answer it, answer from those pages, sentence and number checks, answer with page or honest refusal, Gnani Timbre." width="100%"></p>

---

## Why Pakkam

A forwarded message says *"₹1,000 every month for women. Apply fast!"* Is it real? Is it
meant for you? The answer is written down, in a 43-page government order in formal Tamil
and official English that few people have time to read. So people guess, pay a middleman,
or never apply.

Pakkam reads those pages for you. Ask the way you would ask at home, and it answers from
**18 official documents** only, shows **the page each sentence comes from**, and when the
documents don't say, **tells you so and gives the official helpline** instead of guessing.

*Pakkam* (பக்கம்) is Tamil for *page*: the page number is the product.

## Highlights

**What Pakkam does that a general chatbot does not:** every answer ends with the government's
own page as proof, a named person stands behind the common facts, and it helps people act:
check a WhatsApp rumour, know what to carry, appeal a rejection.

| | |
|---|---|
| **Proof card ("show the officer")** | "📄 Show proof" opens the **official PDF page as an image with the cited lines highlighted**, the G.O. number and date, *"Checked against the printed page by …"*, the next steps, read aloud, share and the PDF link. Something to hold up at the counter. |
| **Rumour Shield** | "Is this WhatsApp forward true?": paste or read out a forward; each claim is marked ✅ true / ❌ wrong / ⚠️ not in the documents, with its proof card. **Scam signs** (non-government link, OTP, money, Aadhaar, "today only") are flagged by fixed rules, and the correction can be sent back on WhatsApp. |
| **Signed fact cards** | 26 common facts, each checked against the printed page and **signed by a named person**; answered instantly with no LLM call. A card only answers its own kind of question (amount, eligibility, documents, how to apply), in the question's language (English cards also serve Tanglish). |
| **What can I get?** | "Any scheme for women?" lists the matching schemes with their signed amounts and eligibility, and *"up to ₹24,000 a year, if you meet each scheme's conditions"*. |
| **Visit checklist** | "Before you go": what to carry and how to apply, each item with its page; tick, read aloud, share or print. |
| **Rejected? → appeal note** | Give the scheme and the rejection reason; Pakkam shows the rule from the G.O. with its proof and fills a fixed appeal template quoting that rule and page. The note is never written by a model. |
| **Every sentence is cited** | Each answer sentence links to the document and page it came from; answers are grouped as *How much · Who can get it · Documents · How to apply*. |
| **Numbers are checked, not trusted** | Every number (amounts, ages, income limits; 2.5 lakh = 2.5 laksham = 2,50,000) must appear in the cited text; a second model checks support; known OCR misreads are blocked or corrected after a person confirms them (`data/corrections.json`). |
| **Honest refusals, then help** | When the documents don't say, Pakkam says so, gives the official contact, and offers **"Ask an officer"**: the question goes to a help-desk queue with a reference number. |
| **Voice with Gnani** | **Prisma v3.0** speech to text with language hints for code-mixed speech and **scheme names as key terms**; **Timbre** speaks the answer, its source (*"Source: G.O. 15, page 10"*) and an instant *"checking the government order…"* line. Talk mode is hands-free. |
| **Phone-call mode** | One toggle turns a recording into 8 kHz telephone-codec audio with line noise before Pakkam hears it: a demo of phone-quality speech without a phone line. |
| **Easy mode** | Bigger text and buttons, every answer read aloud, slower speech: for elderly people and the volunteers who help them. |
| **Pakkam Desk** | A department dashboard ([/dashboard/](https://pakkam-alpha.vercel.app/dashboard/)): most asked schemes, **gaps in the official documents** (refusals by scheme), rumours checked and their scam signs, languages, questions waiting for an officer. Counts only. |
| **Private by design** | The audit log stores a hash of the question, never its text; Aadhaar and phone numbers in a question are refused before any model call; officer contacts are never shown. |
| **Built for cheap phones** | Plain HTML/CSS/JS, no framework, light and dark themes, reduced-motion support, large touch targets; "Remind me" saves next steps to the phone's calendar. |

## Screenshots

<table>
  <tr>
    <td width="70%"><img src="docs/img/chat-dark.png" alt="Pakkam chat in dark theme with suggestion cards in four languages"></td>
    <td width="30%"><img src="docs/img/home-phone.png" alt="Pakkam home page on a phone"></td>
  </tr>
  <tr>
    <td align="center"><sub>Chat app (dark theme): suggestions in four scripts, mic and language picker</sub></td>
    <td align="center"><sub>Home page on a phone</sub></td>
  </tr>
</table>

## Tech stack

| Layer | What |
|---|---|
| Documents | 18 official PDFs (Tamil Nadu and central schemes), Tesseract OCR + Krutrim Chitrapathak-2 crop OCR for hard numerals |
| Search | BAAI `bge-m3` dense + learned sparse vectors in Qdrant, `bge-reranker-v2-m3` |
| Answers | Gemini (Flash, with Flash-Lite as backup on rate limits) or Claude, structured JSON with per-sentence citations, optional failover to the other provider, a daily call budget. Gnani's Evon is not used: its hosted API launches after the deadline, and Gnani's team confirmed another LLM is fine for the submission |
| Voice | Gnani Prisma v3.0 (speech to text, key terms, language hints; falls back to v2.5), Gnani Timbre (text to speech), ffmpeg |
| API | FastAPI, rate limits, privacy-preserving audit log |
| Web | Plain HTML, CSS and JavaScript; Baloo 2 / Hind fonts; Vercel |
| Quality | pytest (634 tests), ruff, mypy, GitHub Actions; `scripts/live_feature_check.py` and `scripts/live_benchmark.py` test the deployed site |

---

## Contents

1. [How it works](#how-it-works)
2. [Results](#results)
3. [Quickstart](#quickstart)
4. [API](#api)
5. [Hosting](#hosting)
6. [Repository layout](#repository-layout)
7. [Documentation map](#documentation-map)
8. [Scripts](#scripts)
9. [Testing and CI](#testing-and-ci)
10. [Limitations](#limitations)
11. [Team and credits](#team-and-credits)
12. [Licences](#licences)

---

## How it works

```
Question (typed, or spoken -> Gnani Prisma v3.0 speech to text, scheme names as key terms)
   │
   ├─ normalise (Unicode, numerals, Tanglish gloss for the reranker)
   │
   ├─ broad ("any scheme for women?") ──► matching schemes + signed amounts, 0 LLM calls
   │
   ├─ signed fact card matches (same kind of question)? ── yes ──► card answer, 0 LLM calls
   │
   ▼
Hybrid search in Qdrant: BGE-M3 dense + BGE-M3 learned sparse, fused
   │
Rerank with BGE-reranker-v2-m3
   │
   ├─ confidence < 0.35 ──► refuse, show the official contact (no LLM call)
   │
   ├─ POST /ask/sources returns the cited pages at once (no LLM call)
   │
LLM writes the answer in the question's language, one source list per sentence
(Claude by default, Gemini supported; a short spoken-style answer for voice)
   │
Guardrails: citation is valid · every number (amount, age, date, income limit)
must appear in the cited chunk (guardrails.py) · a second model checks support
   │
   ├─ unsupported sentences removed; nothing left ──► refuse
   │
Answer + citations + proof card (official page image) + visit checklist
(+ Gnani Timbre speech, sentence by sentence, ending with the source)
```

The pipeline stages live in `src/schemebot/`: `ingest/` → `index/` → `retrieve/` →
`generate/` → `api/`, plus `voice/` and `evaluation/`. Module notes are in
[docs/MODULE_NOTES.md](docs/MODULE_NOTES.md).

---

## Results

All figures come from committed scripts and are on **draft questions written by the
developer, not yet checked by a native speaker**. The refusal threshold was tuned on the
same questions, so treat them as development numbers. Each links to its full report.

| What | Result | n | Script | Report |
|---|---|---|---|---|
| Retrieval Recall@5 (hybrid + reranker) | 98.7% | 154 answerable of 194 | `ablate_retrieval.py` | [ablation](docs/review/RETRIEVAL_ABLATION_REPORT.md) |
| Correct refusals at threshold 0.35 | 92.5% (37/40) | 40 unanswerable | `evaluate_refusal_curve.py` | [curve](docs/review/REFUSAL_THRESHOLD_CURVE.md) |
| False refusals at 0.35 | 14.3% (22/154) | 154 answerable | same | same |
| Spoken question → right document | 90.3% (28/31) | 31 Kathbath read-speech clips | `speech_error_test.py` | [language table](docs/review/LANGUAGE_TABLE.md) |
| Spoken question → right page | 87.1% (27/31) | 31 | same | same |
| OCR numerals on known problem pages | Chitrapathak-2 7/7, Tesseract 0/7 | 7 pages chosen *because* Tesseract failed | `run_hybrid_ocr.py` | [OCR report](docs/review/ocr_benchmark_report.md) |
| Fact cards: false matches | 0 of 40 unanswerable questions | 40 | `fact_card_eval.py` | [fact cards](docs/review/FACT_CARD_EVAL.md) |

**Live, end to end through the website** (`scripts/live_benchmark.py`, Gemini free tier,
laptop backend behind a Cloudflare tunnel; full report in
[LIVE_BENCHMARK.md](docs/review/LIVE_BENCHMARK.md)):

| Run | Questions | Answered (covered) | Cited a correct page | Refused when not covered | Median |
|---|---|---|---|---|---|
| 2 Nov | 60 (15 per language) | 81% | **97%** | 92% | 9.2 s |
| **3 Nov, full set** | **194** (all languages) | **88%** (136/154) | **98%** (133/136) | **98%** (39/40) | **4.8 s** |

By language on the full set: English 97% answered / 100% correct page, Tamil 92% / 94%,
Hindi 84% / 100%, Tanglish 79% / 97%. All 18 misses were refusals, not wrong answers: 11 where search
did not find the right page, 7 where the checks rejected a draft they could not verify. Each is
listed with its reason in the report.

**Live feature check** (`scripts/live_feature_check.py`, 3 Nov): **11/11 features pass** through
the website: cited answer, proof page image, Tanglish answer, honest refusal, "what can I get",
visit checklist, rumour shield with scam signs, ask an officer, dashboard, Timbre speech, and
**Prisma v3.0 hearing Timbre's Tamil back word for word**.

**Retrieval ablation** (`pakkam_chitra` collection, 194 draft questions):

| Mode | Recall@5 | Median retrieval time |
|---|---|---|
| Sparse only | 67.5% | 195.6 ms |
| Dense only | 94.8% | 52.1 ms |
| Dense + sparse | 94.8% | 215.6 ms |
| Dense + sparse + reranker | **98.7%** | 384.3 ms |

**Voice loop timing** (single runs on the developer's laptop, RTX 4060; see
[VOICE_LOOP_TIMING.md](docs/review/VOICE_LOOP_TIMING.md) and
[SENTENCE_SPEECH_REPORT.md](docs/review/SENTENCE_SPEECH_REPORT.md)):

| Stage | Time | Cumulative |
|---|---|---|
| Speech to text (Gnani Prisma) | 1.32 s | 1.32 s |
| Search | 0.22 s | 1.54 s |
| Rerank | 0.24 s | 1.77 s |
| Short voice answer (LLM) | 3.85 s | 5.62 s |
| First sentence spoken (Gnani Timbre) | 2.80 s | **8.42 s to first audio** |

The 5-second end-to-end voice target is **not met yet**. The cited pages appear in about
0.3-0.4 s through `POST /ask/sources`, before the answer is written.

OCR: 263 pages where Tesseract and Chitrapathak-2 read numbers differently are listed in
[ocr_disagreements.csv](docs/review/ocr_disagreements.csv) and are **not yet reviewed by a
person**.

---

## Quickstart

Needs [uv](https://docs.astral.sh/uv/), Python 3.11-3.12 and [ffmpeg](https://ffmpeg.org/) on
the PATH (voice uploads are converted with it). Tesseract (with `tam` and
`hin`) is needed only to rebuild the index. A GPU makes the models much faster.

```bash
cp .env.example .env        # add SCHEMEBOT_GEMINI_API_KEY (or Claude), optional Gnani key
uv sync --extra ingest --extra index --extra generate --extra gemini --extra api
uv run pytest -q            # fast tests, fake models, no API calls
```

The source PDFs and the search index are not in the repository. Download each document in
[data/sources.json](data/sources.json) into `data/raw/` under its `file` name, then:

```bash
uv run python -m schemebot.ingest     # PDFs -> chunks in data/processed/
uv run python -m schemebot.index      # chunks -> Qdrant index in data/index/
uv run fastapi run                    # site + API on http://localhost:8000
```

Open http://localhost:8000/ in the browser, not the `0.0.0.0` address the server prints (browsers reject it). API docs at `/docs`. To use the Chitrapathak OCR
collection, set `SCHEMEBOT_QDRANT_COLLECTION=pakkam_chitra`. Every setting is listed in
[.env.example](.env.example).

**Speed and limits.** Signed fact-card answers are instant and use no LLM call. Other
answers use Gemini Flash, switching to Flash-Lite at once when Flash replies 429 (a 429 is
not retried, so nothing waits on a back-off). Each LLM call waits at most 30 s, repeated
questions come from a saved answer cache (`data/answer-cache.pkl`, cleared automatically
when the answer format changes), and at most 200 LLM calls are made a day
(`SCHEMEBOT_MAX_DAILY_LLM_CALLS`; a full answer with its check uses two or three). On
Gemini's free tier the Flash daily quota is small; Google may use free-tier prompts to
improve its products. With a paid Claude key (`SCHEMEBOT_LLM_PROVIDER=claude`), Gemini can
serve as the backup: `SCHEMEBOT_LLM_FALLBACK_ENABLED=true` plus a Gemini key.

Windows step-by-step: [docs/HANDOFF.md](docs/HANDOFF.md) and
[docs/GNANI_RUNBOOK.md](docs/GNANI_RUNBOOK.md).

---

## API

Full schema: [docs/API_CONTRACT.md](docs/API_CONTRACT.md).

| Method | Path | What it does |
|---|---|---|
| POST | `/ask` | `{"question": "...", "voice_mode": false, "follow_up": {"question", "scheme"}}` → answer sentences, citations, status, timings; a follow-up like "how do I apply?" is read with the previous scheme |
| POST | `/ask/sources` | The cited pages only, no LLM call (shown while the answer is written) |
| POST | `/ask/voice` | Audio upload + language → transcript and answer |
| POST | `/transcribe` | Speech to text only ("Pakkam heard: ...") |
| POST | `/speak` | Text → 24 kHz WAV via Gnani Timbre |
| POST | `/feedback` | Thumbs up/down with an optional reason |
| GET | `/sources` | The 18 documents Pakkam reads |
| GET | `/page?doc=…&p=…&mark=…` | The cited page of the official PDF as a PNG, the passage highlighted (proof card) |
| POST | `/check-forward` | A forwarded message → claims marked supported / contradicted / not in the documents, each with a cited answer, plus `scam_signs` |
| GET | `/checklist?scheme=…&lang=…` | Signed "documents" and "how to apply" facts for a scheme (visit checklist) |
| POST | `/officer-request` | Leave an unanswered question for the help desk → reference `PKM-…` |
| GET | `/dashboard/stats` | Pakkam Desk counts: questions, gaps, rumours, officer requests (no text, no contacts) |
| GET | `/health` | Model and budget status (no secrets) |

A refusal is a normal `200` response with its reason. `/ask` is rate limited per visitor
(10 a minute) and in total (500 a day); `/ask/sources`, `/speak` and `/feedback` have their
own, larger limits, and a spoken sentence is cached so replaying it costs no new Gnani call. Each request is logged to `logs/requests.jsonl`
**without the question text**: only a hash, length, language, citations and timings.

---

## Hosting

| Part | Where | Notes |
|---|---|---|
| Website (`web/`) | Vercel, free | Plain HTML/CSS/JS, no build step (`web/index.html`, `web/js/app.js`) |
| Backend (FastAPI + models + index) | Developer's laptop, reached through a Cloudflare quick tunnel | `scripts/start_pakkam.ps1` starts it, opens the tunnel and points every API path at it (a test checks that each path the pages use is routed); the tunnel URL changes on every restart |
| Planned | Google Cloud Run (CPU) | [deploy/cloudrun/](deploy/cloudrun/README.md); the script asks for a GPU today |

Vercel cannot run the backend (PyTorch and about 4.5 GB of models exceed its function
limit), and Hugging Face Docker Spaces now need a paid plan. Docker: `docker compose up
--build` (see `compose.yaml`).

---

## Repository layout

```
src/schemebot/
  ingest/       PDF text, Tesseract OCR, Chitrapathak crop OCR, OCR corrections
  index/        BGE-M3 dense + sparse embeddings, Qdrant store
  retrieve/     hybrid search, reranker, Tanglish gloss
  generate/     answers, guardrails (number + support checks), fact cards, LLM providers,
                failover, daily budget, answer cache
  voice/        Gnani STT and TTS, amounts as words, daily call cap
  api/          FastAPI app, rate limits, audit log
  evaluation/   question set, metrics, judge, runner
data/           sources.json, contacts.json, corrections.json, fact_cards.json,
                eval/questions.jsonl (raw/, processed/, index/ are not committed)
web/            home page (index.html), chat app (chat/), Pakkam Desk (dashboard/), assets/
scripts/        benchmarks, evaluations and report generators (see below)
tests/          unit and integration tests (fake models, no network)
docs/           reports and guides (see below); docs/archive/ holds superseded notes
deploy/         Cloud Run and Hugging Face Space recipes
```

---

## Documentation map

| Need | Read |
|---|---|
| Current status and blocked items | [STATUS.md](STATUS.md), [docs/review/BLOCKED.md](docs/review/BLOCKED.md) |
| Main benchmark and roadmap report | [docs/review/PAKKAM_2.0_MASTER_EXECUTION_REPORT.md](docs/review/PAKKAM_2.0_MASTER_EXECUTION_REPORT.md) |
| Technical report (original pipeline) | [docs/report.md](docs/report.md), [docs/results.md](docs/results.md), [docs/evaluation.md](docs/evaluation.md) |
| Project specification | [docs/PROJECT_SPECIFICATION.md](docs/PROJECT_SPECIFICATION.md) |
| Voice (Gnani) results | [docs/GNANI_RESULTS.md](docs/GNANI_RESULTS.md), [docs/GNANI_VOICE_REPORT.md](docs/GNANI_VOICE_REPORT.md) |
| Running a demo | [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md), [docs/PHONE_TEST.md](docs/PHONE_TEST.md) |
| Teammate setup | [docs/HANDOFF.md](docs/HANDOFF.md) |
| Frontend design, story and motion | [docs/frontend-plan.md](docs/frontend-plan.md), [docs/design-package.md](docs/design-package.md), [docs/ux/](docs/ux/) |
| Data sources | [docs/data_sources.md](docs/data_sources.md), [docs/sources.csv](docs/sources.csv) |
| Submission | [docs/SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md), [docs/CONTRIBUTIONS.md](docs/CONTRIBUTIONS.md) |
| Per-topic benchmark reports | [docs/review/](docs/review/) |
| Superseded reports and old plans | [docs/archive/](docs/archive/) |

---

## Scripts

Run with `uv run python scripts/<name>.py`. Scripts that call paid or capped APIs ask
before they spend.

| Area | Scripts |
|---|---|
| Retrieval and refusal | `ablate_retrieval.py`, `evaluate_refusal_curve.py`, `benchmark_instant_sources.py`, `paraphrase_eval.py` |
| Answers and grading | `answer_eval.py`, `answer_eval_summary.py`, `make_grading_sheet.py`, `generate_sample_answers.py`, `fact_card_eval.py`, `compare_llm_providers.py`, `benchmark_speed.py`, `run_daily.py` |
| Voice (Gnani) | `gnani_doctor.py`, `gnani_smoke.py`, `gnani_stt_eval.py`, `capture_prisma_raw.py`, `speech_error_test.py`, `eval_tanglish_clips.py`, `eval_field_clips.py`, `fetch_kathbath_sample.py`, `voice_loop_timing.py`, `test_sentence_speech.py`, `make_card_audio.py` |
| OCR | `run_hybrid_ocr.py`, `run_crop_ocr.py`, `colab_chitrapathak.py`, `ocr_compare.py`, `flag_ocr_pages.py`, `generate_gate_pages.py`, `analyze_disagreements.py`, `report_ocr_stats.py`, `check_corrections.py` |
| Reports | `generate_gnani_report.py`, `generate_voice_report.py`, `generate_docx_report.py`, `summarize_questions.py` |
| Running | `start_pakkam.ps1` (one click: latest code, backend, tunnel, website pointed at it) |
| Checks | `scan_git_secrets.py`, `check_helplines.py`, `verify_dod.py`, `review_feedback.py`, `check_amounts.py` |
| Live site | `live_feature_check.py` (every feature, with a Timbre → Prisma round trip), `live_benchmark.py` (194 questions end to end, `--resume`) |
| Sign-off | `sign_fact_cards.py`, `confirm_corrections.py` |

The package also has its own commands: `python -m schemebot.evaluation`,
`python -m schemebot.voice` (compare, tts-samples, eval-script, eval, amounts) and
`python -m schemebot.retrieve` / `schemebot.generate` for one question.

---

## Testing and CI

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy src
uv run pytest -q              # 634 tests, fake models
uv run pytest -m models       # slower tests with the real models (~4.5 GB download)
```

`.github/workflows/ci.yml` runs lint, format, mypy and the fast tests on every push and
pull request, without PyTorch, and builds the Docker image on pushes.

---

## Limitations

- Questions are **drafts** by one person; native-speaker review and an independent held-out
  set are pending.
- Answer wording has not been graded by people yet (`docs/review/grading_sheet.csv`);
  live benchmarks score answered / cited page / refusal automatically.
- Spoken Tanglish and real noisy phone audio are not yet measured on recorded clips; the
  phone-call mode simulates phone audio but is not a phone line.
- Page highlighting needs a text layer: scanned Tamil pages are shown without the yellow mark.
- Hindi coverage is thin (2 Hindi documents).
- 263 OCR number disagreements still need review; three KMUT corrections are confirmed.
- The backend runs on the developer's laptop; when it is off, the live site says so.
- On Gemini's free tier, Flash's daily quota runs out quickly and answers fall back to
  Flash-Lite; a paid key gives faster, better answers for a public demo.

---

## Team and credits

| Person | Role |
|---|---|
| Jaswanth S S · [GitHub](https://github.com/mailtojaswanthss-svg) · [LinkedIn](https://www.linkedin.com/in/jaswanthss) | Project lead: idea, AI and backend, frontend, evaluation |
| Mohit K · [GitHub](https://github.com/mxhxt010-code) · [LinkedIn](https://www.linkedin.com/in/mohit-k-575947371/) | Design and frontend |

Day-by-day contributions are logged in [docs/CONTRIBUTIONS.md](docs/CONTRIBUTIONS.md).
Built with help from Claude (Anthropic) as a coding assistant.

---

## Licences

- **Code:** [MIT](LICENSE).
- **Government documents:** remain the property of their publishing departments and are not
  redistributed here; see [docs/sources.csv](docs/sources.csv).
- **Chitrapathak-2** (`krutrim-ai-labs/Chitrapathak-2`) by Krutrim AI Labs, under the
  Krutrim Community License Agreement 1.0, used for non-commercial research; OCR outputs
  are attributed to Krutrim. Details: [docs/LICENSE_NOTES.md](docs/LICENSE_NOTES.md).
- **Models:** `BAAI/bge-m3` (MIT) and `BAAI/bge-reranker-v2-m3` (Apache 2.0).
- **Speech data:** evaluation clips from AI4Bharat Kathbath (CC BY 4.0).
- **Photos:** Unsplash License ([CREDITS.md](CREDITS.md)).
