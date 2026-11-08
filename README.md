<div align="center">

# Pakkam · பக்கம்

### Ask about a government welfare scheme in your own language, by voice.<br>Get the answer with the exact page of the official document as proof, or an honest "I don't know".

Tamil · Tanglish · Hindi · English &nbsp;|&nbsp; Voice by Gnani Prisma + Timbre &nbsp;|&nbsp; **No page, no answer.**

[![CI](https://github.com/mailtojaswanthss-svg/pakkam/actions/workflows/ci.yml/badge.svg)](https://github.com/mailtojaswanthss-svg/pakkam/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-3776AB)
![Tests](https://img.shields.io/badge/tests-651%20passing-2E7D32)
![License](https://img.shields.io/badge/code-MIT-5A36A3)
![Status](https://img.shields.io/badge/status-research%20prototype-E3A33B)

[**Live site**](https://pakkam-alpha.vercel.app) · [**One-page pitch**](PITCH.md) · [Demo video](docs/judge/pakkam-90s.mp4) · [Pitch deck](docs/judge/pakkam-pitch-deck.pdf) · [Test report](docs/review/LIVE_BENCHMARK.md) · [Project report](docs/report.md)

</div>

<p align="center"><img src="docs/img/home-desktop.png" alt="Pakkam home page: Speak. Hear. See the proof." width="100%"></p>

> **Disclaimer.** An independent student research prototype, built for the Great Indian AI
> Internship Challenge 2026 by Gnani.ai. It is **not** an official service and is **not
> affiliated with any government body**. Answers are informational only: check the official
> source before acting. Pakkam uses only public documents ([docs/sources.csv](docs/sources.csv))
> and stores no personal data ([docs/PRIVACY.md](docs/PRIVACY.md)).

---

## Contents

[Demo](#demo) · [The problem](#the-problem) · [Features](#features) · [How it works](#how-it-works) ·
[Documents covered](#documents-covered) · [Results](#results) · [Tech stack](#tech-stack) ·
[Run it](#run-it-locally) · [API](#api) · [Testing](#testing-and-ci) · [Repository](#repository-layout) ·
[Limitations](#limitations) · [Roadmap](#roadmap) · [Team](#team) · [Licences](#licences)

---

## Demo

| | |
|---|---|
| **Videos** (live site, narrated with Gnani Timbre) | [90 s](docs/judge/pakkam-90s.mp4) · [60 s](docs/judge/pakkam-60s.mp4) · [full, with test results](docs/judge/pakkam-full.mp4) |
| **One-page solution pitch** | [PITCH.md](PITCH.md) · [PDF](docs/judge/pakkam-solution-pitch.pdf) |
| **Pitch deck** | [docs/judge/pakkam-pitch-deck.pdf](docs/judge/pakkam-pitch-deck.pdf) |
| **Try it in 60 seconds** | 1. Open *Check a forward* and paste "Magalir Urimai increased to Rs.2,000! Share OTP" → it is wrong, the order says Rs.1,000, and the scam signs are flagged. 2. Tap the orb and ask in Tamil: *"மகளிர் உரிமைத் தொகைக்கு வருமான வரம்பு எவ்வளவு?"* → Rs.2.5 lakh, G.O.(Ms) No.15, page 10. 3. Tap **Show proof**: the real page, the line highlighted. 4. Ask *"When will the next PM-KISAN installment come?"* → Pakkam says it is not in the documents and gives the official contact. |

<p align="center">
  <img src="docs/img/chat-dark.png" alt="An answer with its sources" width="64%">
  <img src="docs/img/home-phone.png" alt="Pakkam on a phone" width="30%">
</p>

---

## The problem

A forwarded message says *"₹2,000 every month for women. Register today, share your OTP."*
Is it true? Is it meant for you? The real rule is written in a 40-page Government Order in formal
Tamil or official English that few people at home will read. So families trust forwards, pay
middlemen, or never apply.

When it is someone's ₹1,000 a month, **a confident wrong answer is worse than no answer**.
General chatbots answer anyway. Pakkam answers only from 18 official documents, shows the page each
sentence comes from, and says so when the documents don't cover the question.

*Pakkam* (பக்கம்) is Tamil for *page*: the page number is the product.

---

## Features

| Feature | What it does |
|---|---|
| **Proof card ("show the officer")** | "📄 Show proof" opens the official PDF page as an image with the cited lines highlighted, the G.O. number and date, *"Checked against the printed page by …"*, next steps, read aloud, share and the PDF link. Something to hold up at a government counter. |
| **Every sentence is cited** | Each sentence links to its document and page. Answers are grouped as *How much · Who can get it · Documents · How to apply*. |
| **Numbers are checked, not trusted** | Every amount, age and income limit must appear in the cited text (2.5 lakh = 2.5 laksham = 2,50,000). A second model checks support. Known OCR misreads are blocked or corrected after a person confirms them ([data/corrections.json](data/corrections.json)). |
| **Honest refusals, then help** | When the documents don't say it, Pakkam says so, gives the official contact, and offers **Ask an officer**: the question goes to a help-desk queue with a reference number. |
| **Signed fact cards** | 26 common facts, each checked by hand against the printed page and signed by a named person. Answered instantly, with no model call. |
| **Rumour Shield** | Paste or read out a WhatsApp forward: each claim is marked ✅ true / ❌ wrong / ⚠️ not in the documents, with its proof. Scam signs (non-government link, OTP, money, Aadhaar, "today only") are flagged by fixed rules; the correction can be sent back on WhatsApp. |
| **What can my family get?** | "Any scheme for women?" lists matching schemes with signed amounts and eligibility, plus the yearly total *if* each scheme's conditions are met. |
| **Visit checklist** | What to carry and how to apply, each item with its page; tick, read aloud, share or print. |
| **Rejected? → appeal note** | Give the scheme and the rejection reason; Pakkam shows the rule with its proof and fills a fixed appeal template quoting that rule and page. The note is never written by a model. |
| **Voice with Gnani** | **Prisma v3.0** speech to text with language hints for code-mixed speech and scheme names as key terms. **Timbre** speaks the answer and its source, with an instant *"checking the government order…"* line so silence never feels like a crash. Talk mode is hands-free. |
| **Four languages** | Tamil, Tanglish (Tamil in English letters), Hindi and English, for both questions and answers. |
| **Phone-call mode** | Turns a recording into 8 kHz telephone-quality audio with line noise before Pakkam hears it. |
| **Easy mode** | Bigger text and buttons, every answer read aloud, slower speech: for elderly people and the volunteers who help them. |
| **Pakkam Desk** | A department dashboard ([/dashboard/](https://pakkam-alpha.vercel.app/dashboard/)): most-asked schemes, gaps in the official documents (refusals by scheme), rumours checked, languages, questions waiting for an officer. Counts only, no personal data. |

---

## How it works

<p align="center"><img src="docs/judge/architecture.png" alt="Pipeline: question, Gnani Prisma, hybrid search over 18 official documents, reranker, answer from those pages, sentence and number checks, answer with page or honest refusal, Gnani Timbre" width="100%"></p>

```
Question (typed, or spoken -> Gnani Prisma v3.0, scheme names as key terms)
   │
   ├─ normalise (Unicode, numerals, Tanglish gloss)
   ├─ broad question ("any scheme for women?") ──► matching schemes + signed amounts (no model call)
   ├─ matches a signed fact card? ──────────────► card answer (no model call)
   ▼
Hybrid search in Qdrant: BGE-M3 dense + learned sparse, fused
   │
Rerank with BGE-reranker-v2-m3
   ├─ confidence < 0.35 ──► refuse, show the official contact (no model call)
   ▼
The model writes the answer in the question's language, one source list per sentence
   │
Checks: valid citation · every number must appear in the cited text · a second model confirms support
   ├─ unsupported sentences removed; nothing left ──► refuse
   ▼
Answer + citations + proof card (page image) + checklist  (+ Gnani Timbre speech, ending with the source)
```

| Stage | Code |
|---|---|
| PDF text and OCR (Tesseract, plus Krutrim Chitrapathak-2 for hard numerals) | `src/schemebot/ingest/` |
| Search index (Qdrant, BGE-M3) | `src/schemebot/index/` |
| Search and reranking | `src/schemebot/retrieve/` |
| Answers, fact cards, checks, Rumour Shield | `src/schemebot/generate/` |
| Web API | `src/schemebot/api/` |
| Speech in and out (Gnani) | `src/schemebot/voice/` |
| Evaluation | `src/schemebot/evaluation/` |

---

## Documents covered

18 official PDFs (Tamil Nadu and central schemes), in Tamil, English and Hindi. Full list with URLs and dates: [docs/sources.csv](docs/sources.csv) and [docs/data_sources.md](docs/data_sources.md).

| Scheme or area | Document | Issuer |
|---|---|---|
| Kalaignar Magalir Urimai Thittam | G.O.(Ms) No.15, 10 July 2023 | Tamil Nadu |
| Chief Minister's Breakfast Scheme | G.O.(Ms) No.43, 27 July 2022 | Tamil Nadu |
| Social Welfare, Health, Higher Education, Adi Dravidar and Tribal Welfare, BC/MBC and Minorities Welfare | Policy notes 2024-25 (Tamil and English) | Tamil Nadu |
| PM-KISAN | Operational guidelines (2020), e-KYC note (2023) | India |
| Atal Pension Yojana | Subscriber brochure (English and Hindi) | India |
| Pradhan Mantri Ujjwala Yojana | Procedure for 75 lakh connections (2023) | India |

---

## Results

**Live, end to end through the website** (3 Nov 2026; `scripts/live_benchmark.py`; full report with every miss: [docs/review/LIVE_BENCHMARK.md](docs/review/LIVE_BENCHMARK.md)):

| | Result |
|---|---|
| Questions | 194 in Tamil, Tanglish, Hindi and English (154 covered by the documents, 40 deliberately outside them) |
| Covered questions answered | 88% (136/154) |
| Answers citing the correct page | **98%** (133/136) |
| Out-of-scope questions refused | **98%** (39/40). The one miss: a Hindi question about the next PM-KISAN instalment date was answered instead of refused. |
| Median response time | 4.8 s |

By language: English 97% answered / 100% correct page, Tamil 92% / 94%, Hindi 84% / 100%, Tanglish 79% / 97%.
All 18 unanswered covered questions were refusals, not wrong answers.

| Other measurements | Result | Report |
|---|---|---|
| Retrieval Recall@5 (dense + sparse + reranker) | 98.7% (sparse only 67.5%, dense only 94.8%) | [RETRIEVAL_ABLATION_REPORT.md](docs/review/RETRIEVAL_ABLATION_REPORT.md) |
| Spoken question → right document / right page | 90.3% / 87.1% (31 Kathbath clips) | [LANGUAGE_TABLE.md](docs/review/LANGUAGE_TABLE.md) |
| OCR numerals on known problem pages | Chitrapathak-2 7/7, Tesseract 0/7 | [ocr_benchmark_report.md](docs/review/ocr_benchmark_report.md) |
| Fact cards: false matches | 0 of 40 out-of-scope questions | [FACT_CARD_EVAL.md](docs/review/FACT_CARD_EVAL.md) |
| Live feature check | 11/11 features pass through the website | `scripts/live_feature_check.py` |
| Voice loop (laptop, RTX 4060) | about 8.4 s to first spoken audio; cited pages show in about 0.4 s | [VOICE_LOOP_TIMING.md](docs/review/VOICE_LOOP_TIMING.md) |

The questions are drafts written by the team and not yet reviewed by native speakers, and the
refusal threshold was tuned on them; treat these as development numbers.

---

## Tech stack

| Layer | What |
|---|---|
| Documents | 18 official PDFs; Tesseract OCR + Krutrim Chitrapathak-2 crop OCR for hard numerals |
| Search | BAAI `bge-m3` dense + learned sparse vectors in Qdrant, `bge-reranker-v2-m3` |
| Answers | Gemini (Flash, with Flash-Lite on rate limits) or the Claude API; structured JSON with per-sentence citations, optional failover between providers, a daily call budget |
| Voice | Gnani Prisma v3.0 (speech to text), Gnani Timbre (text to speech), ffmpeg |
| API | FastAPI, rate limits, privacy-preserving request log |
| Web | Plain HTML, CSS and JavaScript; Vercel; design in Figma |
| Quality | pytest, ruff, mypy, GitHub Actions; live checks against the deployed site |

---

## Run it locally

Needs [uv](https://docs.astral.sh/uv/), Python 3.11–3.12 and [ffmpeg](https://ffmpeg.org/). Tesseract (with `tam` and `hin`) only to rebuild the index. A GPU makes the models faster.

```bash
cp .env.example .env        # add SCHEMEBOT_GEMINI_API_KEY (or a Claude key), and a Gnani key for voice
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

Every setting is in [.env.example](.env.example). Docker: `docker compose up`.

**How the live site runs.** The website is on Vercel; the backend runs on a laptop behind a
Cloudflare tunnel. On Windows, `scripts/start_pakkam.ps1` starts the backend, opens the tunnel and
redeploys Vercel with the new address. Voice setup: [docs/GNANI_RUNBOOK.md](docs/GNANI_RUNBOOK.md).
Demo script: [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md).

---

## API

Full schema: [docs/API_CONTRACT.md](docs/API_CONTRACT.md).

| Method | Path | What it does |
|---|---|---|
| POST | `/ask` | A question → answer sentences, citations, status and timings (follow-ups keep the previous scheme) |
| POST | `/ask/sources` | The cited pages only, no model call (shown while the answer is written) |
| POST | `/ask/voice` | Audio + language → transcript and answer |
| POST | `/transcribe` | Speech to text only |
| POST | `/speak` | Text → 24 kHz WAV via Gnani Timbre |
| POST | `/check-forward` | A forwarded message → each claim checked, plus scam signs |
| GET | `/page?doc=…&p=…` | The cited PDF page as a PNG, passage highlighted |
| GET | `/checklist?scheme=…` | Documents to carry and how to apply, signed |
| GET | `/sources` | The 18 documents |
| POST | `/officer-request` | Leave an unanswered question for the help desk → reference number |
| POST | `/feedback` | Thumbs up or down with a reason |
| GET | `/dashboard/stats` | Pakkam Desk counts (no text, no contacts) |
| GET | `/health` | Model and budget status (no secrets) |

A refusal is a normal `200` response with its reason. `/ask` is rate limited per visitor (10 a
minute) and in total (500 a day). Requests are logged **without the question text**: only a hash,
length, language, citations and timings.

---

## Testing and CI

```bash
uv run pytest -q           # 651 tests with fake models; no network, no keys
uv run ruff check . && uv run ruff format --check . && uv run mypy src
uv run python scripts/live_feature_check.py --url https://pakkam-alpha.vercel.app
uv run python scripts/live_benchmark.py --url https://pakkam-alpha.vercel.app
```

GitHub Actions runs lint, types and tests on every pull request. Evaluation scripts for retrieval,
refusals, OCR, speech and fact cards are in `scripts/`; method: [docs/evaluation.md](docs/evaluation.md).

---

## Repository layout

```
src/schemebot/   ingest, index, retrieve, generate, api, voice, evaluation
web/             the website (HTML, CSS, JavaScript) and the Pakkam Desk dashboard
data/            sources, signed fact cards, OCR corrections, evaluation questions
tests/           pytest suite
scripts/         evaluation, live benchmark, live start-up, demo video
docs/judge/      demo videos, pitch deck, architecture diagram, LinkedIn post
docs/review/     test and evaluation reports
docs/            project report, API contract, runbooks, privacy, licences
```

---

## Limitations

- Evaluation questions are drafts by the team; native-speaker review and an independent held-out set are pending.
- The one out-of-scope miss (Hindi PM-KISAN instalment date) is not yet fixed.
- Spoken Tanglish and real noisy phone audio are not yet measured on recorded field clips.
- Page highlighting needs a text layer: scanned Tamil pages are shown without the yellow mark.
- Hindi coverage is thin (2 Hindi documents).
- 263 OCR number disagreements still need review by a person.
- Voice is about 8 s to first audio; the 5-second target is not met yet.
- The backend runs on a laptop; when it is off, the live site says so.

## Roadmap

- **Always up to date:** read and check new Government Orders as they are published, and mark replaced orders.
- **Bigger questions, same proof:** "What schemes are there for unemployed youth in Tamil Nadu?" answered with every matching scheme, each with its order and page.
- **The real world:** field tests with elderly speakers, regional dialects, budget phones and background noise.
- Fix the Hindi refusal miss; add more Hindi and central-scheme documents; faster first audio.

---

## Team

| | Role |
|---|---|
| **Jaswanth S S** · [GitHub](https://github.com/mailtojaswanthss-svg) · [LinkedIn](https://www.linkedin.com/in/jaswanthss) | Idea, AI, backend and frontend |
| **Mohit K** · [GitHub](https://github.com/mxhxt010-code) · [LinkedIn](https://www.linkedin.com/in/mohit-k-575947371/) | Design and frontend |

Built for the **Great Indian AI Internship Challenge 2026** by Gnani.ai.

## Licences

- **Code:** [MIT](LICENSE).
- **Government documents:** belong to their publishing departments and are not redistributed here ([docs/sources.csv](docs/sources.csv)).
- **Chitrapathak-2** by Krutrim AI Labs, under the Krutrim Community License Agreement 1.0, used for non-commercial research ([docs/LICENSE_NOTES.md](docs/LICENSE_NOTES.md)).
- **Models:** `BAAI/bge-m3` (MIT), `BAAI/bge-reranker-v2-m3` (Apache 2.0).
- **Speech data:** evaluation clips from AI4Bharat Kathbath (CC BY 4.0).
- **Images:** see [CREDITS.md](CREDITS.md).
