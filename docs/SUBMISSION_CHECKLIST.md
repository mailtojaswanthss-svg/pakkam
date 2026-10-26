# Pakkam submission checklist

Gnani AI internship challenge. Final submission closes **10 Nov 2026, 11:59 PM IST**. Target: submit **Fri 6 Nov** (Diwali is Sun 8 Nov; Sat 7 Nov may be Deepavali in Tamil Nadu), post live **Tue 3 Nov** (latest Thu 5 Nov), video done **Mon 2 Nov**.
Teammate tasks stay flexible until Jaswanth confirms their skills.
This is the master list, built from Jaswanth's checklist (26 Oct) and [WEAKNESS_PLAN.md](weakness/WEAKNESS_PLAN.md). The plan has the schedule, hours and reasoning.

**Who** column:
- **Claude (docs):** Claude can do it with no code change and no credits. It still waits for Jaswanth's go-ahead.
- **Voice thread / UI thread:** code work, done in those threads.
- **Jaswanth / Teammate:** needs a person.
- **Blocked:** waiting on the thing named.

Status: ☐ open, ◐ partly done, ☑ done (with evidence).

## 1. Now (26-27 Oct): unblock everything

| Sev. | Item | Who | Status |
|---|---|---|---|
| High | Teammate accepts the terms email; agree who holds the API key and credits (primary registrant only; never in chat or git) | Jaswanth, Teammate | ☐ |
| High | Agree the split; start the contribution log (date, person, what they did); both read all the code | Jaswanth, Teammate. `docs/CONTRIBUTIONS.md` created (empty) | ◐ Log file ready; the split still needs agreeing |
| High | Test 5-10 real Tanglish clips on Gnani STT, ta-IN vs en-IN; save both transcripts | Jaswanth (clips, key, OK to spend), then the voice thread (script) | ☐ Blocked on the key and the clips |
| Med | Gnani dashboard: what credits cover, which Timbre version is current | Jaswanth | ☐ |
| Med | Ask Gnani (Discord or FAQ contact) what the engagement cutoff time is | Jaswanth | ☐ |
| High | Interview practice: 20 minutes every day from 26 Oct, rotating through the modules | Jaswanth, Teammate | ☐ |
| Med | Re-read the challenge page every few days | Jaswanth; Claude can re-check the public page when asked | ◐ Last checked 26 Oct |

## 2. Make the claims true (27-30 Oct)

| Sev. | Item | Who | Status |
|---|---|---|---|
| High | Check every demo number against its PDF page; start with Pudhumai Penn on the home page | Teammate (reading Tamil/Hindi: skill UNKNOWN) | ☐ PDFs are on Jaswanth's laptop, not in the repo |
| High | Commit the code and re-run the evaluation cleanly (`results.md` says "uncommitted changes") | Jaswanth (laptop; needs the index and models; no credits) | ☐ |
| High | Show n next to every percentage | Claude (docs): README table and the batch table in `report.md` | ☑ 26 Oct: n columns added to both, plus a note that correct refusal is out of 10 |
| Med | Describe the judge accurately: "model-judged", same model verified and judged in the live test | Claude (docs): README, `report.md`, `evaluation.md` | ☑ 26 Oct: all three say model-judged and note that one model verified and judged in the live test. The Word report (`docs/Pakkam-Project-Report.docx`) still has the old wording. |
| Med | State Hindi coverage exactly: 2 Hindi documents, 5 pages, 14 chunks (`report.md` §3); most Hindi answers come through cross-language retrieval | Claude (docs) | ☑ 26 Oct: README and `report.md` §3 |
| Med | Say what the 8 live answers and the 98% do and do not show (98% = gold page in the top 5, draft questions, not answer correctness) | Claude (docs) | ☑ 26 Oct: README results and `report.md` §8; README now calls the 8 live answers a smoke test |
| High | Tamil and Hindi speakers review a sample of the drafts with `docs/review/questions-review.csv`; open the PDF for any number | Teammate or volunteer reviewers | ☐ |

## 3. Build and prove it (28 Oct - 2 Nov)

| Sev. | Item | Who | Status |
|---|---|---|---|
| High | Voice end to end: speech in, answer, Timbre speech out | Voice thread | ◐ STT in code, untested live; no TTS |
| High | Measure latency for every stage and report the real number | Voice thread (Jaswanth runs it live) | ☐ |
| High | Voice test of 30-40 clips: transcript accuracy, spoken numbers, per language; include 1-2 noisy or phone-quality clips | Voice thread (script), Jaswanth and Teammate (synthetic clips) | ☐ |
| High | Decide the LLM budget: paid key, smaller subset, or caching (costs in the plan, section 6) | Jaswanth (estimates in the plan, section 6; verify on the pricing pages) | ☐ |
| High | UI fixes for the video: visible mic, visible source, real loading stages, disclaimer on phones (audit #1, #3, #6, #9) | UI thread (mic itself from the voice thread) | ☐ |
| Med | Better "I don't know": official site link and the list of covered schemes | UI thread (screen); Claude (docs) can draft the text; Teammate checks Tamil and Hindi | ☐ |
| Med | 3-person test, 10 minutes each, synthetic questions | Teammate (sheet in the plan, section 7) | ☐ |
| Med | Rate limit and credit guard on the voice endpoint | Voice thread | ◐ `/ask/voice` shares the `/ask` limits (10 a minute per visitor, 500 a day in total). There is no separate Gnani call cap, so 500 a day could burn 500 calls. |

## 4. Safe to share (by 2 Nov)

| Sev. | Item | Who | Status |
|---|---|---|---|
| High | Search the whole git history for API keys; keep `.env` ignored | Claude | ☑ 26 Oct: all branches scanned for Anthropic, Google, Hugging Face and generic `KEY=` value patterns, with no match. `.env` is in `.gitignore` (line 2), and only `.env.example` (empty values) was ever committed. The Gnani key format is unknown, so the scan can't rule out a Gnani key by pattern; none of the `SCHEMEBOT_GNANI_API_KEY` lines has a value. |
| Med | Licences for the photos and the government documents | Claude (check), Jaswanth (decide) | ◐ Photos: 5 Unsplash photos, credited in `web/assets/img/CREDITS.md` under the Unsplash License. Documents: PDFs are not redistributed (only URLs in `data/sources.json`), and the README says documents stay their publishers' property. Open: `docs/data_sources.md` still says "candidate list" with TODOs, though `sources.json` is complete; no per-document licence or terms are recorded; the code is MIT in `pyproject.toml` and the README, but there is no LICENSE file. |
| Med | README with setup steps and a tiny sample, so a reviewer can run it (PDFs and index not in the repo) | Claude (docs) drafts; Jaswanth picks the sample | ◐ 26 Oct: README now says the PDFs and index are not in the repo and how to download them from `sources.json`. The tiny sample needs a small download script (code), not done. |
| Med | Voice privacy note: audio goes to Gnani, text to the LLM provider; nothing stored by the app | Claude (docs) | ☑ 26 Oct: `docs/PRIVACY.md`, linked from the README |

## 5. Video and post (30 Oct - 3 Nov; post latest 5 Nov)

| Sev. | Item | Who | Status |
|---|---|---|---|
| High | Record a clean fallback demo first | Either, once voice works | ☐ |
| High | 60-second video with English subtitles on all Tamil and Tanglish audio; first 5 s: the forward and the question; show the source page; don't hide the wait | Teammate (editing: skill UNKNOWN); Claude (docs) can draft the script and subtitles | ☐ |
| High | Include one honest refusal and the source link | Teammate | ☐ |
| Med | 2-3 minute full demo with real per-language results and limits | Teammate | ☐ |
| High | Post on LinkedIn and X: English with a Tamil line; tag Gnani AI; #GreatIndianAIInternshipChallenge #GnaniAI | Teammate or Jaswanth posts; Claude (docs) can draft. Claude never posts. | ☐ |
| High | Post live by 5 Nov, then reply to every comment; real people only | Jaswanth, Teammate | ☐ |
| Med | Both teammates post or reshare from their own accounts | Jaswanth, Teammate | ☐ |

## 6. Submit (4-6 Nov; buffer 7 and 9 Nov; deadline 10 Nov)

| Sev. | Item | Who | Status |
|---|---|---|---|
| High | Written explanation names the models used and each member's real contribution | Claude (docs) drafts from the contribution log; Jaswanth edits | ☐ |
| High | Both can explain retrieval, reranker, refusal threshold, guardrails, STT, TTS and the evaluation script | Jaswanth, Teammate. Starting notes in `docs/MODULE_NOTES.md`; rewrite them in your own words. | ◐ Notes drafted 26 Oct |
| High | Re-check the page for rule changes, then submit once on Fri 6 Nov (post live first) | Jaswanth only | ☐ |

## Do not claim

- Anything that is new or the first of its kind.
- Any number that did not come from a script we can re-run, or a number without its n.
- That the judge is independent, or that questions are verified, until that is true.
- That Tanglish works, until the real voice test says so.
- Any government, Gnani or Sarvam affiliation.

The longer list is in the plan, section 4.
