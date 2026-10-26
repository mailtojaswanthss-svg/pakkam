# Pakkam weakness plan

Date: 26 Oct 2026. Based on [STEP1_VERIFY.md](STEP1_VERIFY.md) and Jaswanth's priorities from 26 Oct.
Submission target **8 Nov**, buffer **9 Nov**, hard deadline **10 Nov, 11:59 PM IST**. The post must go live by **5 Nov**, which is 5 days before the deadline.

All hours are estimates. "Me" = Jaswanth. "Teammate" = the second team member. Where a task needs a skill nobody has confirmed the teammate has, it says **skill UNKNOWN**.

## 1. Weaknesses, fixes and owners

Priority order follows Jaswanth's list. Items that were NOT TRUE in Step 1 (A3 mic format, A6 storage, E22 shared files) are left out.

| # | Weakness (Step 1 item) | Sev. | Fix | Owner | Hours | Due |
|---|---|---|---|---|---|---|
| 1 | Tanglish speech untested (A2); Gnani STT never called live (A1) | High | Record 5-10 synthetic Tanglish clips. Send each through `ta-IN` and `en-IN`, save transcripts to CSV, and compare by hand. Show the call count and get my OK before spending credits. | Me | 3 | 27 Oct |
| 2 | Wrong OCR amounts can reach answers; no demo number checked (B9) | High | Fix a demo list of 8-10 questions. For every number in their answers and on the home page, open the PDF page, compare, and log page and result in a sheet. Swap any question whose source page is wrong for one that reads cleanly, or cite the English page. | Teammate (reading Tamil and Hindi: **skill UNKNOWN**) | 3 | 28 Oct |
| 3 | `results.md` came from an uncommitted tree; live-answer output not saved (C16) | Medium | Commit everything, re-run `--retrieval-only` on the laptop from a clean commit, and commit `results.md` plus the `runs/` file. Read the Tanglish rows to list each false refusal's cause (B8). | Me | 2 | 28 Oct |
| 4 | Faithfulness wording; same model verified and judged (C14) | Medium | Say "model-judged" in the README, report and site. State that the 8-question test used one model for both, and fix the contradiction with `evaluation.md`. Add n to the README and the batch table (C12). Docs only. | Me | 1 | 29 Oct |
| 5 | No TTS; Timbre version unclear (A1, A7) | High | Confirm the Timbre version in the dashboard. Add a TTS client, endpoint and play button with fake-TTS tests, following the STT pattern. | Me | 8 | 31 Oct |
| 6 | End-to-end latency unmeasured (A5) | High | Time every stage (STT, retrieval, LLM, verifier, TTS) on a few live voice runs, and log stage times without any text. Report median and max with n. | Me | 2 | 1 Nov |
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
| 17 | Interview readiness (E20) | High | Each person explains every module in their own words to the other. Practise on the list in Step 1 item 20. | Both | 3 each | 7 Nov |
| 18 | Video and post (delivery) | High | Section 8. | Teammate (video editing: **skill UNKNOWN**) | 9 | 5 Nov |

**Cut (Jaswanth's decisions):** public hosting; the full 194-question voice eval; the 5-person test (now 3); transliteration unless needed; UI work beyond #1, #3, #6, #9.

## 2. Day-by-day schedule

Two people working in parallel. Every Gnani or paid LLM run needs Jaswanth's OK first.

| Day | Me (voice, latency, eval) | Teammate (numbers, review, test, video, post) |
|---|---|---|
| Mon 26 Oct | Put the Gnani key in `.env`. Record synthetic Tanglish clips. | Agree the 8-10 demo questions with me. Start the PDF number sheet. |
| Tue 27 Oct | **STT test ta-IN vs en-IN** (#1). Decide the Tanglish code. | PDF number checks (#2). |
| Wed 28 Oct | Clean commit and re-run `results.md`; list Tanglish causes (#3). Confirm the Timbre version. | Finish number checks and swap any bad demo questions. Start Tamil review (#10). |
| Thu 29 Oct | Judge wording and n fixes (#4). Start TTS (#5). | Tamil review. |
| Fri 30 Oct | TTS endpoint and play button, with tests. | Hindi review. Write the 3-person test sheet; recruit testers. |
| Sat 31 Oct | End-to-end voice flow working. **First fallback recording** (#14). | Import the reviews. Draft the video script. |
| Sun 1 Nov | Latency per stage (#6). Voice eval script, then run 30-40 questions with OK (#7, #8). | 3-person test (#12). |
| Mon 2 Nov | Answer-quality run if spending is approved. Transliteration only if needed (#9). | Write up the test notes. Draft the post. |
| Tue 3 Nov | Merge voice and UX work. UI #1, #3 (#13). | UI #6, #9 if able (skill UNKNOWN), else check the refusal wording (#15). **Second fallback recording.** |
| Wed 4 Nov | Freeze numbers: final clean re-run; check every figure in the post and video against it. | Record and edit the demo video. |
| Thu 5 Nov | Review the post and video for the "do not claim" list. | **Publish the post** (Jaswanth reviews and approves first). Share with real contacts. |
| Fri 6 Nov | Write-up and submission pack. | Contribution log tidy-up. Reply to comments. |
| Sat 7 Nov | Interview practice: explain every module to each other (#17). | Same. |
| Sun 8 Nov | **Submission target.** Re-check the challenge page; Jaswanth submits himself. | Final read of the write-up. |
| Mon 9 Nov | Buffer. | Buffer. |
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

**Option A: paid key for one full run.** Estimate, assuming about 4,000 input and 500 output tokens per call. Five 1,000-character passages and the prompt fit that size, but Tamil and thinking tokens could make it 2-3 times higher. Prices are from the providers' pricing pages, checked 26 Oct 2026.

| Setup (models in `config.py`) | Per answered question | ~131 questions | With 3x token margin |
|---|---|---|---|
| Gemini: 3.8 Flash answers ($0.75 / $3.75 per 1M), 3.5 Flash-Lite verifies ($0.30 / $2.50), 3.6 Flash judges ($0.75 / $3.75) | about $0.012 | about $1.60 | about $5 |
| Claude: Opus 5.5 answers and judges ($4 / $20), Haiku 5.5 verifies ($0.10 / $0.50) | about $0.053 | about $7 | about $21 |
| Claude with Sonnet 5.5 ($2 / $10) answering and judging, Haiku verifying | about $0.027 | about $3.50 | about $11 |

These are estimates, not quotes. Set a budget cap on the key before running.

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

- **Publish:** Thu 5 Nov on LinkedIn (and X if the challenge allows both), after Jaswanth approves the final text. Jaswanth or the teammate posts it; Claude never posts.
- **Content:** a 60-90 s clip from the demo video, then 4-5 lines: the problem, what Pakkam does, one measured figure with its n, what it cannot do yet, and the repo link. Tag Gnani as the challenge asks. Check every line against section 4.
- **Honest engagement:** share with real classmates, faculty, family and friends who might care, and ask for feedback, not likes. Post in relevant college or club groups where that is allowed. Reply to every real comment within the day. Add a follow-up comment on 7 Nov with one thing learned from the user test.
- **Never:** bots, paid promotion, engagement pods, like-swapping, or asking people to like without looking.
