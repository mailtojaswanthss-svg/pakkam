# Pakkam weakness plan

Date: 26 Oct 2026 (revised the same day with Jaswanth's changes). Based on [STEP1_VERIFY.md](STEP1_VERIFY.md). The master checklist is [SUBMISSION_CHECKLIST.md](../SUBMISSION_CHECKLIST.md).

- **Submit: Fri 6 Nov.** Sat 7 Nov is the buffer. Lakshmi Puja (Diwali) is Sun 8 Nov 2026 ([BankBazaar holiday list](https://www.bankbazaar.com/indian-holiday/lakshmi-puja-holiday.html)). Tamil Nadu usually celebrates Deepavali a day earlier, so Sat 7 Nov may be a holiday too; that date is UNKNOWN until checked. Mon 9 Nov is a last-resort buffer.
- **Post: Tue 3 Nov**, at the latest Thu 5 Nov (5 days before the 10 Nov deadline).
- **Video: done by Mon 2 Nov**, so the post can carry it.
- Hard deadline: **10 Nov, 11:59 PM IST**.

All hours are estimates. "Me" = Jaswanth. "Teammate" = the second team member. **Teammate tasks are flexible until Jaswanth confirms their skills**: any of them can move to "Me" or "Either". Where a task needs a skill nobody has confirmed, it says **skill UNKNOWN**.

## 1. Weaknesses, fixes and owners

Priority order follows Jaswanth's list. Items that were NOT TRUE in Step 1 (A3 mic format, A6 storage, E22 shared files) are left out.

| # | Weakness (Step 1 item) | Sev. | Fix | Owner | Hours | Due |
|---|---|---|---|---|---|---|
| 1 | Tanglish speech untested (A2); Gnani STT never called live (A1) | High | Record 5-10 synthetic Tanglish clips. Send each through `ta-IN` and `en-IN`, save transcripts to CSV, and compare by hand. Show the call count and get my OK before spending credits. | Me | 3 | 27 Oct |
| 1b | Noisy speech untested (A1) | Medium | Include 1-2 noisy or phone-quality clips (synthetic content) in the STT test and in the voice eval. | Me | 0.5 | 27 Oct |
| 2 | Wrong OCR amounts can reach answers; no demo number checked (B9) | High | Fix a demo list of 8-10 questions. For every number in their answers and on the home page, open the PDF page, compare, and log page and result in a sheet. Swap any question whose source page is wrong for one that reads cleanly, or cite the English page. | Teammate (reading Tamil and Hindi: **skill UNKNOWN**) | 3 | 28 Oct |
| 3 | `results.md` came from an uncommitted tree; live-answer output not saved (C16) | Medium | Commit everything, re-run `--retrieval-only` on the laptop from a clean commit, and commit `results.md` plus the `runs/` file. Read the Tanglish rows to list each false refusal's cause (B8). | Me | 2 | 28 Oct |
| 4 | Faithfulness wording; same model verified and judged (C14) | Medium | Say "model-judged" in the README, report and site. State that the 8-question test used one model for both, and fix the contradiction with `evaluation.md`. Add n to the README and the batch table (C12). Docs only. | Me | 1 | 29 Oct |
| 5 | No TTS; Timbre version unclear (A1, A7) | High | Confirm the Timbre version in the dashboard. Add a TTS client, endpoint and play button with fake-TTS tests, following the STT pattern. | Me | 8 | 31 Oct |
| 6 | End-to-end latency unmeasured (A5) | High | Time every stage (STT, retrieval, LLM, verifier, TTS) on a few live voice runs, and log stage times without any text. Report median and max with n. | Me | 2 | 1 Nov |
| 6b | No Gnani call cap on `/ask/voice` (it shares `/ask`'s 10 a minute and 500 a day, so 500 STT calls a day are possible) | High | Add a separate daily cap on Gnani calls (and TTS calls) from `.env`, with tests. | Me | 1.5 | 30 Oct |
| 7 | Spoken numbers (A4) | Medium | Cover numbers in the voice eval: what Gnani writes for spoken amounts, and whether TTS reads "Rs.6,000" correctly. Fix only what fails. | Me | 2 (inside #8) | 1 Nov |
| 8 | Voice eval missing; answers seen on 8 questions only (B10) | High | Voice eval on 30-40 questions (spoken versions of eval questions, all four groups), plus the answer-quality run if spending is approved (section 6). | Me | 4 | 2 Nov |
| 9 | Tanglish false refusal 44% (B8) | High | Transliteration **only if** #1 and #3 show it is needed. Otherwise keep Tanglish demo questions to ones the eval answers, and state the 44% (n=39) honestly. | Me | 0 or 6 | 2 Nov |
| 10 | Labels unverified (C15) | High | Tamil and Hindi native review using `docs/review/questions-review.csv`, opening the PDF for any number, then `review import`. | Teammate (Tamil, Hindi: **skill UNKNOWN**; else find a volunteer reviewer) | 6 | 1 Nov |
| 11 | Held-out validity (C13) | Medium | No new data. Write the write-up so only held-out 2 (n=84) is called "held out", and say one person wrote all questions. | Me | 0.5 | 4 Nov |
| 12 | No user feedback (F24) | Medium | 3-person test (section 7). | Teammate | 4 | 2 Nov |
| 13 | Video blockers: audit #1 mic, #3 proof, #6 loading, #9 disclaimer (D17) | High | Fix only these 4. The mic comes from the voice branch. Merge the voice and UX work first. | Either | 10 | 3 Nov |
| 14 | No fallback demo (E19) | High | Record one clean screen take of the demo questions as soon as the voice flow works, and another after the UI fixes. | Either | 2 | 3 Nov |
| 15 | Coverage not shown in refusals (B11) | Medium | Add one line to the refusal text listing the covered schemes. Teammate checks the Tamil and Hindi wording. | Me (text), teammate (check) | 1 | 3 Nov |
| 16 | Teammate has no visible contribution (E20) | High | Keep the contribution log (section 5) from today. Teammate's work (number sheet, reviews, test notes, video, post) goes into the repo or project files under their name. | Both | 0.5/day | daily |
| 17 | Interview readiness (E20) | High | **20 minutes every day from 26 Oct:** each person explains one or two modules in their own words to the other, rotating through the list in Step 1 item 20. | Both | 20 min/day | daily |
| 17b | Key leak | High | Search the whole git history for keys; keep `.env` ignored. **Done 26 Oct: no match** (SUBMISSION_CHECKLIST.md §4). Repeat once before the repo goes public. | Me | 0.25 | 4 Nov |
| 17c | Licences (E21 follow-up) | Medium | Photos are fine (Unsplash, credited). Add a LICENSE file (MIT), update the stale "candidate list" in `docs/data_sources.md`, and record each source site's terms if stated. | Me | 1 | 2 Nov |
| 17d | Reviewer can't run it (PDFs and index not in the repo) | Medium | README setup steps plus a tiny sample: 1-2 public PDFs downloaded by a script from their official URLs, and a few questions that run on that sample. | Me | 3 | 2 Nov |
| 17e | Hindi coverage overstated by implication | Medium | State it exactly everywhere: 2 Hindi documents, 5 pages, 14 chunks (`report.md` §3); most Hindi answers come from English or Tamil pages through cross-language retrieval. | Me | 0.5 | 28 Oct |
| 17f | Engagement cutoff unknown | Medium | Ask Gnani (Discord or the FAQ contact) when engagement is counted. | Me | 0.25 | 27 Oct |
| 17g | Teammate may not be registered | High | Confirm the teammate has accepted the terms email; agree who holds the key and credits (primary registrant only). | Me, Teammate | 0.25 | 27 Oct |
| 18 | Video and post (delivery) | High | Section 8. English subtitles on all Tamil and Tanglish audio. | Teammate (video editing: **skill UNKNOWN**) | 10 | 2 Nov (video), 3 Nov (post) |

**Cut (Jaswanth's decisions):** public hosting; the full 194-question voice eval; the 5-person test (now 3); transliteration unless needed; UI work beyond #1, #3, #6, #9.

## 2. Day-by-day schedule

Two people working in parallel. Every Gnani or paid LLM run needs Jaswanth's OK first. **Both, every day: 20 minutes of interview practice** and a contribution-log entry.

| Day | Me (voice, latency, eval) | Teammate (flexible until skills confirmed) |
|---|---|---|
| Mon 26 Oct | Put the Gnani key in `.env`. Record synthetic Tanglish clips, including 1-2 noisy or phone-quality ones. | Confirm the terms email is accepted (#17g). Agree the split and the 8-10 demo questions. Start the PDF number sheet. |
| Tue 27 Oct | **STT test ta-IN vs en-IN** (#1, #1b). Ask Gnani about the engagement cutoff (#17f). Dashboard: credits, Timbre version. | PDF number checks (#2). |
| Wed 28 Oct | Clean commit and re-run `results.md`; list Tanglish causes (#3). Doc fixes: judge wording, n values, Hindi coverage (#4, #17e). Decide on transliteration. | Finish number checks; swap any bad demo questions. Start Tamil review (#10). |
| Thu 29 Oct | TTS client and endpoint with tests (#5). | Tamil review. Draft the video script and English subtitles. |
| Fri 30 Oct | TTS play button; end-to-end voice flow. Gnani call cap (#6b). **First fallback recording** (#14). | Hindi review. Recruit 3 testers. |
| Sat 31 Oct | Latency per stage (#6). Merge voice and UX work; UI #1 mic and #3 proof (#13). | 3-person test (#12). |
| Sun 1 Nov | UI #6 loading and #9 disclaimer. Voice eval on 30-40 clips, with OK (#7, #8). Transliteration only if needed (#9). | Record the demo video (the fallback take is the backup). Write up the test notes. |
| Mon 2 Nov | Freeze numbers: final clean re-run. Answer-quality run if spending is approved. README setup and sample; licence fixes (#17c, #17d). | **Video done**: edit, English subtitles on all Tamil and Tanglish audio. Draft the post. |
| Tue 3 Nov | Check the post and video against the "do not claim" list. | **Publish the post** after Jaswanth approves it (latest Thu 5 Nov). Share with real contacts. |
| Wed 4 Nov | Write-up and submission pack. Repeat the key scan (#17b). | Reply to comments. Reshare from own account. |
| Thu 5 Nov | Re-check the challenge page. Final read of the write-up. Last day for the post if it slipped. | Contribution log final. Final read. |
| Fri 6 Nov | **Submit.** Jaswanth submits himself, after confirming the post is live. | |
| Sat 7 Nov | Buffer (may be Deepavali in Tamil Nadu; check). | Buffer. |
| Sun 8 Nov | Lakshmi Puja (Diwali): no work planned. | |
| Mon 9 Nov | Last-resort buffer. | |
| Tue 10 Nov | Hard deadline 11:59 PM IST. | |

## 3. Cut list (what goes first if we fall behind)

1. UI #9, then #6 (keep #1 mic and #3 proof, which the video needs).
2. The second fallback recording (keep the first).
3. The refusal coverage line (#15).
4. The 3-person test, down to 2 people.
5. The answer-quality run (report the 8-question smoke test as it is).
6. The voice eval, down to 20 questions (5 per group).

Never cut: the real STT test, the PDF number checks, the clean `results.md` re-run, TTS and the end-to-end voice flow, one fallback recording, the post by 5 Nov, the contribution log.

## 4. Do not claim

The post, video and write-up must not say:

- That Pakkam is the first, only or a new kind of scheme assistant. Jugalbandi, Sarvam's scheme-agent example and others exist (STEP1_VERIFY.md, F23). Describe what it does instead.
- Any number that was not measured, or a number without its n. Examples: no latency before #6 is done, no voice accuracy before #8, no "accurate" or "reliable" without a figure.
- "Independent", "human-verified" or "verified" about faithfulness. It is model-judged, and in the 8-question test one model both verified and judged.
- "Verified" or "native-checked" about the question set until the review import is done, and then only for the questions marked verified.
- "Held out" about anything except held-out 2 (n=84).
- That Tanglish speech works, unless #1 shows it, and only for what was tested.
- "Real-time", "instant" or "fast".
- "Works for all schemes", "all of India" or "all Indian languages". It covers 18 documents and 4 language groups.
- That it is official, approved, or affiliated with any government or with Gnani.
- That Gnani is used for anything beyond what the code does: STT now, TTS once built.
- "Tested with users" beyond the 3-person test, with n stated.
- That nothing is stored anywhere. Say the app does not store audio or question text; the speech and LLM providers have their own terms.

## 5. Contribution log template

Keep it in `docs/CONTRIBUTIONS.md`. Add a row the same day the work is done. The write-up's contribution section is built only from these rows.

| Date | Person | What they did | Where it is (commit, file, link) | Hours |
|---|---|---|---|---|
| 2026-10-27 | Jaswanth | Ran the Gnani STT test on 8 Tanglish clips, ta-IN vs en-IN | `docs/voice/stt-tanglish.csv`, commit abc1234 | 3 |
| 2026-10-27 | Teammate name | Checked 14 demo numbers against their PDF pages | `docs/review/demo-numbers.csv` | 2.5 |

(The two rows are examples of the format, not records of work done.)

## 6. LLM free-tier limit and options (Jaswanth decides on spending)

**The limit.** Gemini's free tier allows 20 requests a day per model (`report.md` §8). Each answered question uses up to 3 calls (answer, verifier, judge), each on a different model. Questions refused at retrieval use none. On `results.md`, about 131 of 194 questions pass retrieval (129 answerable plus 2 unanswerable), so a full run is about 131 calls per model. At 20 a day that is **about 7 days** per full run, and any retry costs more.

**Option A: paid key for one full run.** These are estimates; verify on the pricing pages ([Gemini](https://ai.google.dev/gemini-api/docs/pricing), [Claude](https://claude.com/pricing)) before spending. Estimate, assuming about 4,000 input and 500 output tokens per call. Five 1,000-character passages and the prompt fit that size, but Tamil and thinking tokens could make it 2-3 times higher. Prices are from the providers' pricing pages, checked 26 Oct 2026.

| Setup (models in `config.py`) | Per answered question | ~131 questions | With 3x token margin |
|---|---|---|---|
| Gemini: 3.8 Flash answers ($0.75 / $3.75 per 1M), 3.5 Flash-Lite verifies ($0.30 / $2.50), 3.6 Flash judges ($0.75 / $3.75) | about $0.012 | about $1.60 | about $5 |
| Claude: Opus 5.5 answers and judges ($4 / $20), Haiku 5.5 verifies ($0.10 / $0.50) | about $0.053 | about $7 | about $21 |
| Claude with Sonnet 5.5 ($2 / $10) answering and judging, Haiku verifying | about $0.027 | about $3.50 | about $11 |

Estimates only; verify on the pricing pages above. Set a budget cap on the key before running.

**Option B: smaller subset on the free tier.** Run 40 questions (10 per group, mixed batches), about 2 days at 20 calls a day. Report it as n=40.

**Option C: caching.** No answer cache exists in the code today (nothing found by search). A small on-disk cache keyed by question, passages and model would let re-runs and the demo reuse earlier answers without new calls. About 2 hours of work, and the voice eval and demo rehearsals reuse it too.

**Gnani credits.** 5,000 per registration. What one call costs in credits is UNKNOWN, so check the dashboard after the first STT test and after the first TTS call, and plan the voice eval from that.

## 7. 3-person user test

- **Who:** 3 non-technical adults: at least 1 Tamil speaker, 1 Hindi speaker, and 1 who speaks Tanglish. Friends or family are fine. Get verbal consent and keep no recordings.
- **How:** 15 minutes each, on a laptop or phone, with the teammate watching and noting. Questions are synthetic: no real personal details.
- **Tasks:** (1) Speak a question about a covered scheme. (2) Find which document and page the answer came from. (3) Ask something not covered and say what you would do next.

Observation sheet (one row per task per person):

| Person (P1-P3) | Language | Task | Finished (yes/no) | Time (s) | Where they hesitated | What they said | Trust in the answer (1-5) | Would use again (yes/no) |
|---|---|---|---|---|---|---|---|---|

## 8. Post plan

- **Publish:** Tue 3 Nov (at the latest Thu 5 Nov) on LinkedIn (and X if the challenge allows both), after Jaswanth approves the final text. Jaswanth or the teammate posts it; Claude never posts.
- **Content:** a 60-90 s clip from the demo video, with English subtitles on all Tamil and Tanglish audio, then 4-5 lines in English with one Tamil line: the problem, what Pakkam does, one measured figure with its n, what it cannot do yet, and the repo link. Tag Gnani as the challenge asks. Check every line against section 4.
- **Honest engagement:** share with real classmates, faculty, family and friends who might care, and ask for feedback, not likes. Post in relevant college or club groups where that is allowed. Reply to every real comment within the day. Add a follow-up comment on 5 Nov with one thing learned from the user test.
- **Never:** bots, paid promotion, engagement pods, like-swapping, or asking people to like without looking.
