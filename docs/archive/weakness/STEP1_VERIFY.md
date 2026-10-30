# Pakkam weakness review, Step 1: verification

Date: 26 Oct 2026. Read: `main` at 35ba419, voice branch `claude/project-thread-fpld2g` (3f48f57), UX branch `claude/project-thread-i98lxh`, `docs/results.md`, `docs/report.md`, `docs/evaluation.md`, the code, and Gnani's public STT docs. No code was changed. No Gnani or LLM calls were made.

**What I could not do in this container:** the source PDFs (`data/raw/`) and the search index are not in the repo, so I could not re-run retrieval or open the PDF pages. Items that need that are marked UNKNOWN, with how to check them for free on your laptop.

Status key: CONFIRMED = the weakness is real. NOT TRUE = the worry does not hold. UNKNOWN = not measured or not checkable here.

## Summary of High items

1. Gnani is only one STT call today, not live-tested, and there is no TTS (A1, A7).
2. Tanglish speech and Tanglish answers are both unproven (A2, B8).
3. Wrong OCR amounts can reach an answer, and no demo number has been checked against its PDF (B9).
4. Answer quality has been seen on 8 questions only, and the LLM free tier ran out during the last full run (B10).
5. No fallback demo recording, no measured end-to-end latency (E19, A5).
6. The repo shows no commits from your teammate (E20).

## A. Voice and Gnani

| # | Item | Status | Severity | Evidence |
|---|---|---|---|---|
| 1 | Gnani is integral | **CONFIRMED weakness**: thin today | High | The only Gnani use is one `POST /stt/v3` in `src/schemebot/voice/stt.py` (voice branch, 119 lines). The transcript then goes into the unchanged text pipeline (`api/main.py`, `ask_voice`). No TTS exists on any branch. STATUS.md: "Not yet tested against real Gnani." A reviewer would see "a speech box in front of a text RAG". It gets stronger with Timbre TTS for the answer, a voice eval (Tanglish clips, spoken numbers), and a real recorded test. |
| 2 | Tanglish speech works | **UNKNOWN** | High | Never tested. `stt.py:27` maps Tanglish to `ta-IN` with the comment "untested choice". Gnani's docs list code-mixing only for English-Hindi on `en-IN`; Tamil-English is not mentioned ([docs](https://docs.gnani.ai/api/STT/speech-to-text.md)). |
| 3 | Mic format matches Gnani | **NOT TRUE** (no mismatch, by design) | Medium | `web/assets/recorder.js` records 16 kHz mono PCM WAV, not WebM/MP4. `check_audio` (`stt.py`) only accepts the six listed formats and caps clips at 30 s. Gnani's docs give both 60 s and 30 s, so 30 s is the safe choice. Remaining risks: tested only with a fake mic in headless Chromium (no real phone, no iPhone Safari), and the length check only works for WAV (an uploaded MP3 over 30 s is not caught). |
| 4 | Spoken numbers handled | **CONFIRMED gap** (partly UNKNOWN) | Medium | Tamil and Devanagari digits are mapped to 0-9 (`text.py:11-22`). Number *words* ("six thousand", "ஆறாயிரம்", "2.5 lakh") are not converted anywhere. Whether Gnani writes digits or words is UNKNOWN. The guardrail number check uses `\d+` (`guardrails.py:22, 46-51`), so an answer saying "2.5 lakh" against a passage saying "2,50,000" would be wrongly removed. How TTS reads "Rs.6,000" is UNKNOWN (no TTS yet). |
| 5 | End-to-end latency measured | **CONFIRMED gap** | High | Not measured. Known pieces: retrieval p50 533 ms / p95 720 ms on the RTX 4060 laptop (`results.md`); full text answer 13 to 52 s per answer on Gemini free tier including retries (`report.md`, live-answer section). `stt_ms` is returned by `/ask/voice` but has never been measured live. TTS: none. **Estimate (not measured):** at least 15 s per voice answer on the free tier, dominated by the LLM; STT and TTS add an UNKNOWN amount. |
| 6 | Audio or transcripts stored | **NOT TRUE** | Low | `/ask/voice` reads the clip into memory and passes it to Gnani; nothing writes it to disk. The audit log stores a 16-char hash of the question, its length and language, never the text (`api/audit.py`). The chat page shows the transcript but does not save it (no localStorage in `chat.js`). Note: the clip goes to Gnani and the text goes to Gemini/Claude, whose retention rules are theirs; check their terms before saying "nothing is kept anywhere". |
| 7 | Timbre version | **CONFIRMED unresolved** | Medium | No TTS code exists, so the code uses neither version. STT uses Prisma v2.5 (`stt.py:1`, `config.py`). The challenge page says Timbre v2.5 (Beta) in one place and v3.0 in another (STATUS.md). Check the dashboard before building TTS. |

## B. Answer quality and safety

| # | Item | Status | Severity | Evidence |
|---|---|---|---|---|
| 8 | Cause of Tanglish false refusals; transliteration tried | Per-question cause **UNKNOWN**; transliteration **NOT tried** | High | 44% = 17 of 39 answerable Tanglish questions. The per-question run file (`runs/*.jsonl`, written by `evaluation/__main__.py:105`) is not in the repo, so I can't list causes per question. The report's aggregate claim: "mostly with the right page retrieved but scored under the threshold" (`report.md` §8), and 61% on the fresh batch (11 of 18). Transliteration has no code anywhere; it is listed as a next step (`report.md` §11.3). Free to check: run `python -m schemebot.evaluation --retrieval-only` on your laptop and read the Tanglish rows of the new `runs/` file. |
| 9 | Wrong OCR amounts reach a spoken answer | **CONFIRMED** risk; demo-number check **UNKNOWN** | High | `report.md` §4: Tamil OCR reads a leading 1 as 4 (Pudhumai Penn Rs.1,000 as 4,000; health insurance limit Rs.1,20,000 as 4,20,000; hostel food Rs.1,400 as 4400; helpline 14567 as 14167); Hindi APY brochure reads "रु.000". The guardrail cannot catch this, since the wrong number is in the cited passage. There is no fixed demo question list yet. Numbers shown now: home page "ஆண்டுக்கு 12 ஆயிரம் ரூபாய்" (from the Tamil KMUT G.O., which is OCR), ₹6,000 PM-KISAN, ₹1,000/month Pudhumai Penn (the Tamil note's OCR says 4,000), APY ₹1,000-5,000; chat suggestions ask KMUT eligibility (Tamil), PM-KISAN amount (Hindi, partly from the Hindi OCR note), APY age (English). I could not check any of these against the PDF page: the PDFs are not in the repo. |
| 10 | Plan for more live answers | **CONFIRMED gap** | High | Only 8 hand-picked questions (`report.md` §8). The full run needs a paid key, and the free tier ran out (20 requests a day per model). No budget or plan is written down. |
| 11 | Coverage clear to users | **CONFIRMED gap** | Medium | Covered (`data/sources.json`, 18 docs): Kalaignar Magalir Urimai, PM-KISAN, Atal Pension Yojana, PM Ujjwala, CM Breakfast Scheme, and the 2024 TN policy notes for social welfare and women, health, higher education, Adi Dravidar and tribal welfare, BC/MBC. Not covered: everything else (e.g. ration cards, other states). The refusal text (`generate/messages.py`, `NOT_FOUND`) says "official scheme documents I have" but never lists them (also audit problem 7). |

## C. Evaluation validity

| # | Item | Status | Severity | Evidence |
|---|---|---|---|---|
| 12 | Every % shows its n | **CONFIRMED** partly | Medium | `results.md` shows Ans/Unans per row (good). The README table drops that column, and the per-batch table in `report.md` §8 has no n. Correct refusal per language is out of 10, so one question is 10 points. |
| 13 | Truly held-out batches | **CONFIRMED** limit | Medium | One author wrote all 194. Dev q001-q048 tuned the gloss. The threshold was chosen on the first 110 (`report.md` §8), so only held-out 2 (q111-q194, 84 questions) is untouched by both. None is independent of the author. |
| 14 | Faithfulness called "model-judged" | **CONFIRMED** partly | Medium | `evaluation.md:97-99` says LLM judge, different from the verifier. But the live test used Gemini 3.1 Flash-Lite as both verifier and judge (`report.md` §8 and §9), which contradicts that. README line 54 says "judged faithful" without saying by a model. |
| 15 | Label problems; sheet ready | **CONFIRMED** labels unverified; sheet **ready** | High | All 194 are `draft` (0 verified). Ten incomplete labels were already found and fixed (`report.md` §8.4), so more likely exist. `docs/review/questions-review.csv` (194 rows, columns for verified, corrected question/reference, notes) can go to a native speaker now. Caveat: its `gold_text` for Tamil/Hindi is OCR text, so the reviewer should open the PDF page for any number. |
| 16 | Figures trace to a re-runnable script | **CONFIRMED** partly | Medium | `results.md` comes from `python -m schemebot.evaluation --retrieval-only`, but its header says "commit c050d23 (uncommitted changes)", so it does not match a clean commit. The 8 live answers and "13 to 52 s" have no saved output in the repo. Site numbers are typed into the HTML (they match today, per the UI audit). The home page scheme facts (₹6,000 etc.) are typed by hand. |

## D. UX and story

| # | Item | Status | Severity | Evidence |
|---|---|---|---|---|
| 17 | Audit problems that block the video | See list | High | From `UI_AUDIT.md`. **Blocking:** 1 (no mic on screen; the voice branch adds it), 3 (the proof/citation is invisible in a short video), 6 (loading state looks frozen at real 15 s+ waits). **Should fix:** 2 (English-only interface text), 7 (refusal leaves people stuck), 9 (disclaimer hidden on phones). **Not blocking:** 4, 5 (picker comes with voice), 8, 10. |

## E. Delivery risks

**18. Undone work, estimated hours (estimates, not measured):**

| Work | Hours |
|---|---|
| Real Gnani STT test with 5-10 Tanglish clips (ta-IN vs en-IN) | 3 |
| Timbre TTS (client, endpoint, play button, tests) | 8 |
| Voice eval script (transcript accuracy, spoken numbers) | 4 |
| End-to-end latency timing (all stages) | 2 |
| Tanglish transliteration experiment + re-run | 6 |
| Fix demo question list, check every number against the PDF | 3 |
| Native-speaker review (Tamil, Hindi): reviewer time | 6 |
| Full answer eval (needs paid key, cost UNKNOWN) | 3 |
| 5-person user test and write-up | 6 |
| UI changes for the video (audit 1, 3, 6, plus 2, 7, 9) | 12-16 |
| Merge voice and UX work | 2 |
| Public hosting (HF Space or similar) | 4-6 |
| Fallback recording | 2 |
| Demo video | 6 |
| Post and engagement | 3 |
| Submission pack, contribution log, re-check challenge page | 3 |
| **Total** | **about 73-79** |

| # | Item | Status | Severity | Evidence |
|---|---|---|---|---|
| 19 | Fallback demo exists | **CONFIRMED gap** | High | No recorded take exists in the repo or project files. |
| 20 | Can both members explain every module | **UNKNOWN** (only you two know); one red flag **CONFIRMED** | High | `git log --all`: 13 commits by you, 2 authored "Claude", none by a teammate. The write-up must state each member's contribution, and both are interviewed. Modules to explain: retrieval (`retrieve/hybrid.py`, `retriever.py`), reranker (`retrieve/rerank.py`), refusal threshold (`config.py:69`, 0.35), Tanglish gloss (`retrieve/tanglish.py`), guardrails (`generate/guardrails.py`), answer flow (`generate/answer.py`, `prompt.py`), OCR choice (`ingest/extract.py`), STT call (`voice/stt.py`), TTS call (not built), evaluation (`evaluation/runner.py`, `metrics.py`, `judge.py`). |
| 21 | Runs on a laptop; cheapest public option | **CONFIRMED** laptop works (GPU), public **not set up** | Medium | Numbers were measured on an RTX 4060 laptop. An LLM key is needed for answers. `deploy/hf-space/` targets a free CPU Space ("first question after a quiet spell waits a minute or two"). `deploy/cloudrun/` uses an L4 GPU billed per second. Nothing is deployed yet. Cheapest: free HF Space, with slow answers. |
| 22 | Files both threads touch | **NOT TRUE today** | Low | The UX branch only adds `docs/ux/*`. The voice branch changes code. No shared files. Future risk: `web/assets/chat.js`, `chat.css`, `web/chat/index.html` once UX code changes start. |

## F. Positioning

**23. Prior art (found by search; I read titles and summaries only):**
- Jugalbandi (Microsoft, AI4Bharat and partners): government scheme information in Indian languages over WhatsApp, with voice. [Thoughtworks case study](https://www.thoughtworks.com/clients/jugalbandi)
- Sarvam AI's "Government Scheme Awareness Agent" voice-agent example. [Sarvam docs](https://docs.sarvam.ai/api-reference-docs/cookbook/example-voice-agents/government-scheme-agent)
- News of a government WhatsApp bot for farmers (2023). [MediaNama](https://www.medianama.com/2023/02/223-indian-govt-whatsapp-questions-chatgpt-bot/)
- IndiaAI AIKosh use case on conversational agents for rural e-governance. [AIKosh](https://aikosh.indiaai.gov.in/home/use-cases/details/ai_powered_conversational_agents_for_rural_e_governance.html)

What Pakkam does that is true in this repo (not a claim that others don't): every sentence must cite a page and pass a number check and a model support check, or it is removed (`guardrails.py`); it refuses below a measured threshold instead of guessing; Tanglish is a separate evaluated group with its own gloss; a per-language evaluation with refusal metrics is published; the audit log never stores question text.

**24. 5-person test:** none done (CONFIRMED gap, Medium). Proposal for Step 2: 5 non-technical people (at least 2 Tamil, 2 Hindi speakers, 1 Tanglish), 15 minutes each, 3 fixed tasks (speak a question, find the source page, react to a refusal), synthetic questions only, no recordings kept. Observation sheet: task, finished yes/no, time, where they hesitated, what they said, did they trust the answer (1-5), would they use it again (yes/no).
