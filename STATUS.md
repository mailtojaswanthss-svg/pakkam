# Pakkam + Gnani voice: status

Last updated: 28 Oct 2026. Own target: 8 Nov (11 days left). Hard deadline: 10 Nov, 11:59 PM IST (13 days left).

## Done
- Hybrid OCR Pipeline - Full Optimization & Overnight Run (28 Oct):
  - Added --finalize flag to scripts/run_hybrid_ocr.py that builds docs/review/ocr_disagreements.csv and indexes pakkam_chitra (2,859 chunks) from completed pages.
  - Re-ordered page queue by demo priority: 1. Pudhumai Penn (	n-hedu, 	n-swwe), 2. CMCHIS (page 421 and nearby pages 410-430), 3. Hostels (BC/MBC & ADTW), 4. National demo schemes (APY, PM-Kisan, PMUY), 5. Tamil G.O.s (KMUT, CMBFS), 6. Remaining documents.
  - Documented 352 page count origin: Sum of currency-flagged pages from initial 11 priority documents (111 + 86 + 62 + 58 + 12 + 9 + 7 + 3 + 2 + 1 + 1 = 352). Full corpus has 500 currency-flagged pages across all 18 documents.
  - Built crop mode in scripts/run_crop_ocr.py: uses Tesseract bounding boxes to crop amount regions with 80px/30px margins and passes only the crop to Chitrapathak-2. Tested on 7 known-problem pages: achieved 7/7 (100%) accuracy, mean time 11.54s/page (6.8x speedup vs 78.8s full-page, up to 20.2x speedup on individual pages), with zero new errors.
  - Fixed OCR benchmark report (docs/review/ocr_benchmark_report.md): resolved 1/7 vs 0/7 contradiction, explicitly documented selection bias on known-problem pages, and replaced 'production' with 'research prototype' under Krutrim Community License v1.0.
  - Overnight runner actively running with demo-priority queue in background.
- Hybrid OCR pipeline - Step 1 & 2 (27 Oct):
  - scripts/flag_ocr_pages.py scanned all 1,353 cached Tesseract OCR pages for currency markers (ரூ, Rs, Rs., ₹, रु) and 3+ digits.
  - Output written to docs/review/ocr_flagged_pages.csv (1,255 pages flagged with 3+ digits = 33.1 GPU hours; 500 pages with currency markers = 13.2 GPU hours).
  - Priority ordering established: Pudhumai Penn, CMCHIS, BC/MBC and ADTW hostels, APY, PM-Kisan, PMUY.
  - Stopped before GPU run; waiting for user confirmation on scope and cut-down rule.
- Voice in, code side (26 Oct):
  - `src/schemebot/voice/stt.py`: Gnani Prisma v2.5 speech-to-text client (`POST /stt/v3`).
  - `POST /ask/voice`: audio upload plus language, then speech to text, then the existing answer pipeline. Returns the answer and the transcript.
  - Chat page: mic button (records 16 kHz mono WAV, stops at 30 s), upload button, and a "I will speak in" picker.
  - 23 new tests with a fake STT (no key, no network, no credits). 213 tests pass; ruff and mypy are clean.
  - Checked in a headless browser with a fake mic and a fake STT only. **Not yet tested against real Gnani.**

- Credit guard and compare script (26 Oct):
  - Daily cap on Gnani calls (`SCHEMEBOT_GNANI_MAX_CALLS_PER_DAY`, default 100, a guess). Kept in `logs/gnani-calls.json`, so it survives restarts. It resets at midnight IST and counts failed calls. The web app and the compare script share it. When the cap is hit, voice answers 503 with a "you can still type" message.
  - `uv run python -m schemebot.voice compare data/voice/tanglish/` sends each clip with ta-IN and en-IN (`--codes` to change). It prints "This will make N Gnani calls", refuses if N is over what is left today, and only runs after you type `yes`.
  - Clip types (tanglish, tamil, english, hindi, noisy) come from the filename prefix or from `said.txt` (`file | type | what you said`).
  - CSV columns: clip, type, duration (WAV only; n/a for other formats), language code, transcript, error, call time, transcript script, said text, said script, and `said_words_found`. That last one is the share of said words found in the transcript, and it is only computed when both texts use the same script. No other scoring.
  - `data/voice/` is gitignored: recordings and transcripts are never pushed.
  - 22 more tests with a fake STT. 235 tests pass; ruff and mypy are clean. **Not yet run against real Gnani.**

- Voice out, code side (26 Oct):
  - `src/schemebot/voice/tts.py` is a Gnani Timbre client (`POST /api/v1/tts/inference`), returning 24 kHz mono WAV.
  - `POST /speak` takes `{text, language}` and returns WAV. It removes `[n]` markers, caps text at 1200 characters (`SCHEMEBOT_TTS_MAX_CHARS`), and logs neither text nor audio.
  - Each answer has a **Listen** button that turns into **Stop** while playing. Nothing plays without a tap. Starting a new conversation stops playback.
  - Voice language: Tamil and Tanglish answers use a ta-IN voice, Hindi uses hi-IN, English uses en-IN.
  - **TTS stays off until `SCHEMEBOT_TTS_MODEL` is set** to timbre-v2.5 or timbre-v3.0, which Jaswanth confirms from the dashboard. Default voices: v2.5 uses Asmita (ta), Nalini (hi) and Kaveri (en); v3.0 uses Shivani. They can be overridden with `SCHEMEBOT_TTS_VOICE_TA/HI/EN`.
  - Every TTS call counts in the same daily cap as STT.
  - Empty values in `.env` (e.g. `SCHEMEBOT_TTS_MODEL=`) now count as not set. This also stops an empty Gnani key from switching voice on.
  - 24 more tests with a fake TTS. 259 tests pass; ruff and mypy are clean. Checked in a headless browser with a fake TTS only. **No real Timbre audio has been generated yet.**

- Timbre listening test script (26 Oct): `python -m schemebot.voice tts-samples` speaks short made-up sentences (cases: tamil, digits, tanglish; text in `voice/samples.py`). It prints the voices and the call count, waits for `yes`, and counts calls in the daily cap. Output files are `data/voice/tts-samples/synthetic-test-*.wav`, each with a notes file saying what to listen for. 5 more tests; 264 pass.

- Per-stage timing (26 Oct, fakes only, no live calls):
  - `/ask` and `/ask/voice` responses now include `timings_ms`, with keys search, rerank, retrieval (= search + rerank), llm_answer, verifier (guardrail checks plus the verifier call), generation (= llm_answer + verifier), total, and stt for voice.
  - `/speak` sends a `Server-Timing: tts;dur=…` header.
  - The audit log (`logs/requests.jsonl`) stores the same numbers. A spoken answer gets its own line holding only character count, language code and tts ms. No text or audio is logged.
  - A stage that didn't run is left out: a low-confidence refusal has no llm_answer or verifier entry.
  - 6 more tests; 270 pass. **No real latency numbers exist yet.** They need live runs on Jaswanth's laptop.

- Voice evaluation script (26 Oct, fakes only, no live calls; scope item 3):
  - `python -m schemebot.voice eval-script` writes `data/voice/eval/script.csv`. It lists 32 questions to read aloud: per language, the first 6 answerable and the first 2 unanswerable by id. The pick is deterministic, so nobody hand-picks easy ones. Each row gives the file name to save as (`q001.wav`, or `q001-noisy.wav` for a noisy take).
  - `python -m schemebot.voice eval data/voice/eval/` sends only clips that aren't transcribed yet. It asks for yes first and counts them in the cap. Transcripts are cached in `transcripts.jsonl`, so re-runs are free.
  - It then runs typed and spoken versions of the same questions through the normal evaluation. The report has one row per language plus a "Noisy clips" row. Columns: clips, STT failed, Recall@5 typed → spoken, correct refusal typed → spoken, false refusal typed → spoken, and STT ms p50/p95. Every percentage shows its n.
  - `--full` adds faithfulness (model-judged), citation accuracy and answer latency, using paid LLM calls. It asks first, and the default is retrieval only, which is free.
  - `--tanglish-code en-IN` switches Tanglish to en-IN.
  - Reports go to `data/voice/runs/` (gitignored). They carry the "Draft questions, not yet native-speaker verified" note, and a SYNTHETIC banner plus file prefix when any clip name contains "synthetic".
  - 12 more tests; 282 pass. **Not run on real clips yet.**

- Money amounts as words for TTS (26 Oct, **off by default**: `SCHEMEBOT_TTS_SPELL_AMOUNTS=false`):
  - `voice/numbers.py` turns money into words in the voice's language before `/speak`. Examples: "Rs.1,000" → "ஆயிரம் ரூபாய்", "₹12,000" → "बारह हज़ार रुपये", "Rs.2.5 lakh" → "two point five lakh rupees".
  - It only touches money: a number with Rs./₹/ரூ./रु. in front, a lakh/crore unit, or a rupee word. Ages, years, helplines and G.O. numbers are left alone. "/-" is dropped.
  - Deterministic tables with Indian grouping. Decimals are read digit by digit, never rounded.
  - Every conversion is parsed back to a number and compared with the original. If they differ, or the amount is written unusually ("1,0000", "12,00", rupees and paise), the text is kept as written.
  - English matches the num2words library on 22,000 numbers (a one-off check, not a dependency). All three languages read back exactly over 0-3000 plus 5,000 random numbers up to 10^11.
  - `python -m schemebot.voice amounts` (free) lists every way the corpus writes money and how each would be spoken. The chunks aren't in the repo, so it must be run on Jaswanth's laptop. Here it only saw the eval references: 7 formats, 0 kept as written.
  - **The Tamil and Hindi wording needs a native speaker's review**, e.g. "ஆறு ஆயிரம்" vs the spoken "ஆறாயிரம்".
  - 40 more tests; 322 pass.

- Mic polish (26 Oct, UI spec section 6), with no backend change:
  - Four language buttons (Tamil, Hindi, English, Tanglish marked "(being tested)").
  - Recording shows "● 0:07 / 0:30" and a square Stop, a "5 seconds left" note from 0:25, and a ✕ Cancel button (Escape also cancels) that discards the clip.
  - If the browser says the mic is denied: "Mic is off. Type instead…" with a Type instead button.
  - "Sending your voice…", then "Slow connection, still sending…" after 5 s. On a network or server error, the clip is kept and a Send again button resends it. A 4xx such as "could not hear" asks you to speak again instead.
  - On phones the mic is a 52 px round button. Screen readers hear the timer every 10 s, not every second. A new recording stops any answer playing.
  - Checked in headless Chromium with a fake mic and a mocked /ask/voice. Not tried on a real phone.

- Transcript first (option A, 26 Oct):
  - New `POST /transcribe` runs speech to text only: 1 Gnani call, same daily cap, its own rate-limit counter, and a numbers-only audit line.
  - The chat page now calls `/transcribe`, shows "Pakkam heard: …" at once, then sends that text to `/ask`.
  - Send again after a failed answer resends only the text, with no new Gnani call.
  - `/ask/voice` stays for scripts and the eval.
  - Tests: 4 new API tests with fakes (363 pass). Checked in headless Chromium with mocked routes. No real Gnani call.

## Next
0. Jaswanth runs the Timbre listening test on his laptop (the key is only there; Claude can't hear audio, so Jaswanth describes what he hears):
   - a. `--cases tamil --models timbre-v2.5 timbre-v3.0` (2 calls), then choose the version and set `SCHEMEBOT_TTS_MODEL`.
   - b. `--cases digits tanglish --models <chosen>` (2 calls). Digits decide whether to switch on number-to-words (`SCHEMEBOT_TTS_SPELL_AMOUNTS=true`; built, off by default). For Tanglish, Claude proposes options and Jaswanth chooses.
1. Jaswanth: record clips into `data/voice/tanglish/` (5 to 10 Tanglish, plus a pure Tamil, a pure English and one noisy clip as controls) and run the compare script.
2. After the first few real calls, check credit use in the Gnani dashboard and set the daily cap to match.
3. Read the CSV together and decide Tanglish ta-IN vs en-IN.
4. Record the 32 eval clips from `script.csv` (plus 1-2 noisy takes) and run `eval` (retrieval-only first, free).
5. Mic UX polish: mostly done (see Done). Not built from the spec: the one-time mic pre-prompt (3), and a fixed "Playing answer" bar (9; the Listen/Stop button stays on each answer). "Pakkam heard" before the answer (6) is now built, see item 7. Try it on a real phone before the video, using docs/PHONE_TEST.md.
6. Later list (Jaswanth, 26 Oct): the one-time mic pre-prompt; a "Playing answer" bar (needs TTS switched on first); "show the transcript as soon as it is known" (proposal below, not built).
7. Show the transcript first: **option A built** (26 Oct, see Done). Options as proposed: Today /ask/voice returns the transcript only together with the answer.
   - **A. Two requests (recommended).** Add a new `POST /transcribe` that only runs STT. The page shows "Pakkam heard: …" straight away, then sends that text to `/ask` like a typed question.
     - Gnani cost: 1 call per question, the same as now.
     - Extras: one more local HTTP round trip, and it could later let the user fix a wrong transcript before asking.
     - Work: about 2-3 h. `/transcribe` needs its own rate limit so a voice question isn't counted twice. The stt_ms timing and the language picked must be passed on to `/ask`. Tests use fakes.
   - **B. Streaming.** `/ask/voice` sends the transcript first, then the answer, in one response.
     - Gnani cost: also 1 call per question.
     - Work: about 4-5 h. Errors after the transcript arrive inside a 200 response, so runTurn's error handling (shared with the UI thread) has to change, and the browser must read a stream.
   - Neither option makes the speech-to-text step itself faster. They only stop the transcript waiting for the answer. The 13-50 s figure in the UI spec is the UI thread's estimate of answer time, not a voice measurement.

## Blockers
- Tanglish clips (Jaswanth). The key is in his local `.env` (26 Oct). **Target: recordings done by Wed 28 Oct, no later than Sun 1 Nov.** The result decides whether the roughly 6-hour transliteration work is needed, so a later date makes the plan slip.
- Unknown: what one credit buys. Check the dashboard before any bulk run.

## Decisions
- Tanglish speech goes to Gnani as `ta-IN` for now. Gnani documents no Tanglish code. This stays untested until the clip comparison is done.
- Max clip length 30 s. Gnani's docs say both 30 s and 60 s, so we use the safe value (`SCHEMEBOT_STT_MAX_SECONDS`).
- The browser records WAV, not WebM, because Gnani's STT REST docs don't list WebM.
- Without a Gnani key the server still runs, and `/ask/voice` answers 503.
- Credits: tests and CI never call Gnani. Only the live app and the clip script do, and both are under the daily cap.
- The cap's lock is per process, so the app and the script running at exactly the same moment could miss one count. That's fine for one person on one laptop.

## Open questions for TTS (untested)
- Gnani's docs say to spell out numbers, dates and currency. Our answers contain digits like "Rs. 1,000", and how Timbre reads them is unknown. Test this before the demo.
- Typed Tanglish questions get Tanglish answers in Latin letters, and a ta-IN voice reading Latin text is untested. Spoken Tanglish goes through ta-IN STT and probably comes back in Tamil script, but that depends on the clip test.
- **Tanglish TTS options, for Jaswanth to choose after the listening test (no choice made):**
  - A. Speak as is with a ta-IN voice. No work. Fine if the test sounds like Tamil; bad if it sounds English or garbled.
  - B1. Ask the answer LLM for a Tamil-script copy of each Tanglish sentence and speak that. About 2-3 h: one more field in the answer JSON, so more output tokens but no extra call. Risk: the copy could drift from the checked text. Mitigation: only accept it if its numbers match the Tanglish sentence, else fall back to C.
  - B2. Rule-based Latin-to-Tamil transliteration. No LLM, but Tanglish spelling is loose ("evlo/evvalavu"), so quality is likely poor. About 3-4 h plus tuning. Not recommended without a test set.
  - C. Hide Listen on Tanglish answers, with a one-line note saying listening is available for Tamil, Hindi and English. Under 1 h. Honest, but it shows a gap in the demo.
  - D. Speak Tanglish with an en-IN voice, which reads Latin letters as written. No work. This goes against "Tanglish is spoken in Tamil", so it's listed only for completeness.
  - Note: spoken Tanglish questions go through ta-IN STT and will likely come back in Tamil script, so the answer and its voice would be Tamil. The gap mostly affects typed Tanglish.

## Synthetic test clips
- Synthetic voices are for plumbing tests only (pipeline, CSV, counter, errors). File names and outputs carry "synthetic". Clips made with Gnani Timbre for Gnani STT are labelled "synthetic, same vendor". Results from them are never used as evidence in any doc or number.

## Rules for recording other people
- Get their verbal consent first, and use made-up questions only. No real names, phone numbers, Aadhaar or PAN.
- Keep recordings only as long as needed. They live in `data/voice/`, which is gitignored and never committed.

## Challenge facts re-checked (26 Oct, gnani.ai/internship)
- The submission must also say what each team member contributed.
- The TTS version is unclear: the page says Timbre v2.5 (Beta) in one place and v3.0 in another. Confirm in the dashboard.
