# Pakkam + Gnani voice: status

Last updated: 26 Oct 2026. Own target: 8 Nov (13 days left). Hard deadline: 10 Nov, 11:59 PM IST (15 days left).

## Done
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

## Next
0. Jaswanth runs the Timbre listening test on his laptop (the key is only there; Claude can't hear audio, so Jaswanth describes what he hears):
   - a. `--cases tamil --models timbre-v2.5 timbre-v3.0` (2 calls), then choose the version and set `SCHEMEBOT_TTS_MODEL`.
   - b. `--cases digits tanglish --models <chosen>` (2 calls). Digits decide whether deterministic number-to-words is needed (not built yet). For Tanglish, Claude proposes options and Jaswanth chooses.
1. Jaswanth: record clips into `data/voice/tanglish/` (5 to 10 Tanglish, plus a pure Tamil, a pure English and one noisy clip as controls) and run the compare script.
2. After the first few real calls, check credit use in the Gnani dashboard and set the daily cap to match.
3. Read the CSV together and decide Tanglish ta-IN vs en-IN.
4. Record the 32 eval clips from `script.csv` (plus 1-2 noisy takes) and run `eval` (retrieval-only first, free).
5. Mic UX polish, from the UI thread's spec (section 6 of /mnt/project-files/ui-ux/UX_RECOMMENDATIONS.md). Candidates: a big "Tap and speak" mic on phones, language buttons with Tanglish marked "(being tested)", denied-permission card, Stop/Cancel with a "5 seconds left" note, a slow-upload "Send again" option, and a TTS play/stop bar with no autoplay. Already done: the 0:30 cap, and an empty transcript gets "could not hear" and is never sent to /ask. Needs Jaswanth's go-ahead, and it touches runTurn in chat.js, which the UI thread also plans to change.

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

## Synthetic test clips
- Synthetic voices are for plumbing tests only (pipeline, CSV, counter, errors). File names and outputs carry "synthetic". Clips made with Gnani Timbre for Gnani STT are labelled "synthetic, same vendor". Results from them are never used as evidence in any doc or number.

## Rules for recording other people
- Get their verbal consent first, and use made-up questions only. No real names, phone numbers, Aadhaar or PAN.
- Keep recordings only as long as needed. They live in `data/voice/`, which is gitignored and never committed.

## Challenge facts re-checked (26 Oct, gnani.ai/internship)
- The submission must also say what each team member contributed.
- The TTS version is unclear: the page says Timbre v2.5 (Beta) in one place and v3.0 in another. Confirm in the dashboard.
