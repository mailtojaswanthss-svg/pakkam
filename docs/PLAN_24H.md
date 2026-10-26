# Pakkam: the next 24 hours

Written Mon 26 Oct 2026, 11:55 UTC (5:25 PM IST). Covers Mon 26 Oct evening to Tue 27 Oct evening (IST).
Task IDs come from [REPORT_STATUS_SECTION.md](REPORT_STATUS_SECTION.md). All hours are ESTIMATES.

**Goal:** finish the three tasks that decide what we can honestly claim, and clear the small tasks that block other work. The goal is not a percentage.

## Must do (in this order)

| # | Task | Who | Hours | Why now | Needs |
|---|---|---|---|---|---|
| 1 | **V1 + V2: record 5-10 Tanglish clips** plus one pure Tamil, one pure English and one noisy clip into `data/voice/tanglish/`. Then run `uv run python -m schemebot.voice compare data/voice/tanglish/` (it shows the call count and waits for `yes`). | Jaswanth | 3.5 | The result decides whether the 6-hour transliteration work (E3) is needed, and what the demo can show in Tanglish | Gnani key in `.env`; verbal consent; made-up questions only; never commit the clips |
| 2 | **E2: clean re-run of `results.md`.** Commit everything first, then `uv run python -m schemebot.evaluation --retrieval-only`, then commit `docs/results.md` and the `runs/` file. Read the Tanglish rows and note why each one was refused. | Jaswanth (laptop) | 2 | Every number in the report, site and post must come from this run. Section 7 of the status section is provisional until then | Index and models on the laptop. Free: no LLM or Gnani calls |
| 3 | **E1: demo number check.** Open each PDF page listed in `docs/review/demo-numbers.csv` (weakness branch, guide in `docs/review/DEMO_NUMBERS_GUIDE.md`) and fill `pdf_shows_exactly` and `matches_expected`. Start with Pudhumai Penn, Magalir Urimai 12,000 and Atal Pension 1,000-5,000. | Teammate (or Jaswanth if the teammate can't read Tamil) | 3 | A wrong amount in the demo is the biggest credibility risk | PDFs on the laptop |

## Should do (small tasks that unblock others)

| # | Task | Who | Hours | Unblocks |
|---|---|---|---|---|
| 4 | **Gnani dashboard:** check what one credit buys, and which Timbre version is current (v2.5 Beta or v3.0). Set `SCHEMEBOT_TTS_MODEL`. Or compare both first: `uv run python -m schemebot.voice tts-samples --cases tamil --models timbre-v2.5 timbre-v3.0` (synthetic sentences, yes prompt) and listen. | Jaswanth | 1 | V3 (TTS) is built on the branch but switched off until the version is set; also the voice eval budget |
| 5 | **Review the UI branch `claude/ui-proof-refusal`:** T0 (hide unverified facts), T1 (source page under every answer), T3 (clearer "I don't know") and T4 (disclaimer on phones). | Jaswanth | 0.5 | Marking U1, U2, U4, U5 done |
| 6 | **S5:** teammate confirms the terms email is accepted; agree who holds the key and credits. **S4:** ask Gnani (Discord or FAQ contact) when engagement is counted. | Jaswanth, Teammate | 0.5 | The submission, and the post date |
| 7 | **D4:** choose the licence (MIT or Apache-2.0). | Jaswanth | 0.1 to decide | A LICENSE file |
| 8 | **S1:** first rows in `docs/CONTRIBUTIONS.md`, for both people, with links. **S2:** 20 minutes of interview practice. | Both | 0.5 | The contribution section, which is empty today |

## If there is time

| # | Task | Who | Hours | Needs |
|---|---|---|---|---|
| 9 | **V4: latency.** The voice branch now records per-stage timings (`5b4b542`). Run 3-5 live voice questions and report median and max with n. | Jaswanth | 2 | Items 1 and 4; Gnani credits and an LLM key; your OK before the calls |
| 10 | **U8:** native review of the Tamil interface strings (UX_RECOMMENDATIONS.md §7). | Jaswanth | 1-2 | — |
| 11 | **U10 preparation:** decide the merge order. The voice branch and `claude/ui-proof-refusal` conflict in 4 files: `api/schemas.py`, `generate/answer.py`, `tests/test_api.py`, `web/assets/chat.js` (checked with `git merge-tree`, 26 Oct 11:55 UTC). Suggestion: merge voice first, then rebase the UI branch on it. | Jaswanth decides; Claude can do the rebase with a go-ahead | 2 | Your go-ahead for merging |

## Not in these 24 hours (and why)

- **Voice eval (V7), 3-person test (E5):** need TTS on and items 1 and 4 done.
- **Video and post (P1, P2):** planned for 2 and 3 Nov; the fallback recording needs voice working end to end.
- **Transliteration (E3):** only if item 1 shows it is needed.
- **Word report:** planned for 5 Nov, after the clean re-run.

## End of the 24 hours: what "done" looks like

- A CSV of real Gnani transcripts for the Tanglish clips, and a decision: `ta-IN` or `en-IN`, transliteration yes or no.
- A clean `results.md` that names its commit, with no "uncommitted changes".
- Every demo number marked yes or no against its PDF page.
- The Timbre version confirmed and TTS switched on.
- The contribution log has its first entries.

If all of this is done, the task count rises a lot (ESTIMATE: to about 15-19 of 38), but the real gain is that the main claims become checkable.
