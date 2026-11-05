# Pakkam: status

Last updated: 3 Nov 2026. Deadline: **10 Nov 2026, 11:59 PM IST** (Gnani.ai Great Indian AI
Internship Challenge). Target submission: 8 Nov.

## Where things stand

| Area | State |
|---|---|
| Live site | https://pakkam-alpha.vercel.app (new design, 5 Nov: voice orb, answers with proof cards, schemes and official documents from `/sources`); backend on the developer's laptop through a Cloudflare tunnel, started with `scripts/start_pakkam.ps1` |
| Tests | 634 passing; ruff, format and mypy clean; CI on every push |
| Live feature check | **11/11** through the website on 3 Nov (`scripts/live_feature_check.py`) |
| Live benchmark | 3 Nov, **all 194 questions**: 88% answered, **98% cite a correct page**, 98% correct refusals, median 4.8 s, no errors ([LIVE_BENCHMARK.md](docs/review/LIVE_BENCHMARK.md)) |
| Fact cards | 26 cards, **all signed** by Jaswanth S S against the printed pages ([FACT_CARD_CHECK.md](docs/review/FACT_CARD_CHECK.md)) |
| OCR corrections | KMUT G.O. 15 pp.10-11 ("25 lakh" read for 2.5 lakh) confirmed and applied; 3 suspected BC/MBC pages blocked until checked |
| Voice | Gnani Prisma v3.0 (key terms, language hints, v2.5 fallback) and Timbre, live; Timbre → Prisma round trip passes |
| LLM | Gemini (Flash → Flash-Lite backup). Evon not used: Gnani confirmed its hosted API comes after the deadline and another LLM is fine |

## Features (all merged into `main`)

- Cited answers grouped as How much / Who / Documents / How to apply; honest refusals.
- **Proof card**: the official page image with the cited lines highlighted, who checked it,
  next steps, read aloud, share, PDF.
- **Rumour Shield**: claims in a WhatsApp forward checked against the documents, scam signs
  by fixed rules, correction shared back on WhatsApp.
- **What can I get?**: matching schemes with signed amounts and a yearly total.
- **Visit checklist** and **rejected → appeal note** (fixed template quoting the cited rule).
- **Ask an officer**, **Remind me** (calendar), **Pakkam Desk** dashboard.
- **Voice**: instant "checking the government order" line, spoken source, Talk mode,
  **phone-call mode** (simulated 8 kHz telephone audio), **Easy mode** for elderly users.

## Next

| When | What | Who |
|---|---|---|
| 3-4 Nov | Move the backend to Hugging Face Spaces (only if it passes 11/11 there too) | Both |
| 3 Nov | Teaser post on LinkedIn/X (tag Gnani, #GnaniAI #GreatIndianAIInternshipChallenge) | Jaswanth |
| 3-4 Nov | Record 20 voice clips (`docs/voice/CLIP_PLAN.md`) for spoken Tanglish and noise numbers | Jaswanth |
| 4 Nov | Spoken Tanglish / noisy-audio evaluation on the clips | Claude |
| 5 Nov | 60-second video script | Claude |
| 6 Nov | Record the video and post it | Jaswanth |
| 7 Nov | Written explanation (problem, users, models used, contributions) | Both |
| 8 Nov | Submit | Jaswanth |

## Open decisions

- **Gemini billing**: the free Flash quota runs out within hours; billing (a few hundred
  rupees at most) gives faster, better answers through the demo and judging.
- **Hosting during judging**: keep the laptop on, or move the backend to a cloud VM.
- Teammate name and role for the README and contribution log.

## Blocked on people

| Item | Needs |
|---|---|
| Field voice clips | 20 recordings (Tamil, Tanglish, Hindi, one noisy) |
| Answer grading | Human scores in `docs/review/grading_sheet.csv` |
| OCR review | 263 pages in `docs/review/ocr_disagreements.csv`; BC/MBC pp.34, 36, 43 |
| Helplines | Phone checks in `docs/review/helpline_check.csv` |
