<div align="center">

# Pakkam · பக்கம்

**Ask about a government welfare scheme in your own language, by voice.<br>
Get the answer with the exact page of the official document as proof, or an honest "I don't know".**

Tamil · Tanglish · Hindi · English &nbsp;|&nbsp; Voice by Gnani Prisma + Timbre &nbsp;|&nbsp; **No page, no answer.**

[![CI](https://github.com/mailtojaswanthss-svg/pakkam/actions/workflows/ci.yml/badge.svg)](https://github.com/mailtojaswanthss-svg/pakkam/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-3776AB)
![License](https://img.shields.io/badge/code-MIT-5A36A3)

[**Live site**](https://pakkam-alpha.vercel.app) · [Demo video](docs/judge/pakkam-90s.mp4) · [Pitch deck](docs/judge/pakkam-pitch-deck.pdf) · [Test report](docs/review/LIVE_BENCHMARK.md)

</div>

<p align="center"><img src="docs/img/home-desktop.png" alt="Pakkam home page" width="100%"></p>

> Independent student research prototype for the Great Indian AI Internship Challenge 2026 by Gnani.ai.
> Not an official service and not affiliated with any government body. Check the official source
> before acting. Uses only public documents ([sources](docs/sources.csv)); stores no personal data
> ([privacy](docs/PRIVACY.md)).

## Why

The real rules of welfare schemes sit in 40-page Government Orders that few people read, so families
rely on WhatsApp forwards. When it's someone's ₹1,000 a month, a confident wrong answer is worse
than no answer. *Pakkam* is Tamil for *page*: the page is the product.

## What it does

| | |
|---|---|
| **Answers with proof** | Every sentence cites a page in one of 18 official documents. One tap opens that page with the line highlighted. |
| **Refuses honestly** | If the documents don't say it, Pakkam says so and gives the official helpline. |
| **Checks numbers** | Every amount, age and income limit must appear on the cited page; 26 common facts are checked by hand and signed. |
| **Voice first** | Gnani Prisma hears Tamil, Tanglish, Hindi and English; Gnani Timbre speaks the answer. |
| **Rumour Shield** | Paste a WhatsApp forward: each claim is checked against the order, and scam signs (fake links, OTP, "today only") are flagged. |
| **Helps you act** | Schemes for your family with yearly totals, a visit checklist, and an appeal note quoting the rule after a rejection. |

## Results (live site, 194 questions)

| | |
|---|---|
| Covered questions answered | 88% (136/154) |
| Answers citing the correct page | **98%** (133/136) |
| Out-of-scope questions refused | **98%** (39/40); the one miss is in the report |
| Median response time | 4.8 s |

Full method and every miss: [docs/review/LIVE_BENCHMARK.md](docs/review/LIVE_BENCHMARK.md).

## How it works

<p align="center"><img src="docs/judge/architecture.png" alt="Question, Gnani Prisma, hybrid search over 18 official documents, reranker, answer from those pages, sentence and number checks, answer with page or refusal, Gnani Timbre" width="100%"></p>

Search: `bge-m3` dense + sparse vectors in Qdrant with `bge-reranker-v2-m3`. Answers: Gemini or the
Claude API, as structured JSON with per-sentence citations, then checked sentence by sentence.
Backend: FastAPI. Frontend: plain HTML, CSS and JavaScript on Vercel.

## Run it

Needs [uv](https://docs.astral.sh/uv/), Python 3.11–3.12 and ffmpeg.

```bash
cp .env.example .env            # add an LLM key and, for voice, a Gnani key
uv sync --extra ingest --extra index --extra generate --extra gemini --extra api
uv run pytest -q                # tests, no API calls
uv run python -m schemebot.ingest && uv run python -m schemebot.index   # PDFs from data/sources.json in data/raw/
uv run fastapi run              # http://localhost:8000
```

The live site runs the backend on a laptop behind a Cloudflare tunnel: `scripts/start_pakkam.ps1`.

## Repository

```
src/schemebot/   search, answers, checks, voice, API
web/             the website
data/            sources, fact cards, corrections, evaluation questions
tests/           pytest suite
scripts/         evaluation, live benchmark, demo video
docs/judge/      demo videos, pitch deck, architecture, LinkedIn post
docs/review/     test and evaluation reports
```

## Team

| | |
|---|---|
| **Jaswanth S S** · [GitHub](https://github.com/mailtojaswanthss-svg) · [LinkedIn](https://www.linkedin.com/in/jaswanthss) | Idea, AI, backend and frontend |
| **Mohit K** · [GitHub](https://github.com/mxhxt010-code) · [LinkedIn](https://www.linkedin.com/in/mohit-k-575947371/) | Design and frontend |

## Licences

Code: [MIT](LICENSE). Government documents belong to their departments and are not redistributed.
Models: `BAAI/bge-m3` (MIT), `bge-reranker-v2-m3` (Apache 2.0), Krutrim Chitrapathak-2 (Krutrim Community
License, non-commercial research). Speech clips: AI4Bharat Kathbath (CC BY 4.0). Details:
[docs/LICENSE_NOTES.md](docs/LICENSE_NOTES.md), [CREDITS.md](CREDITS.md).
