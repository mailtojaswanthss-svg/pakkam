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

## Next
1. Jaswanth: record clips into `data/voice/tanglish/` (5 to 10 Tanglish, plus a pure Tamil, a pure English and one noisy clip as controls) and run the compare script.
2. After the first few real calls, check credit use in the Gnani dashboard and set the daily cap to match.
3. Read the CSV together and decide Tanglish ta-IN vs en-IN.
4. Voice out (Timbre TTS).
5. Mic UX polish, from the UI thread's spec (section 6 of /mnt/project-files/ui-ux/UX_RECOMMENDATIONS.md). Candidates: a big "Tap and speak" mic on phones, language buttons with Tanglish marked "(being tested)", denied-permission card, Stop/Cancel with a "5 seconds left" note, a slow-upload "Send again" option, and a TTS play/stop bar with no autoplay. Already done: the 0:30 cap, and an empty transcript gets "could not hear" and is never sent to /ask. Needs Jaswanth's go-ahead, and it touches runTurn in chat.js, which the UI thread also plans to change.

## Blockers
- Tanglish clips (Jaswanth). The key is in his local `.env` (26 Oct).
- Unknown: what one credit buys. Check the dashboard before any bulk run.

## Decisions
- Tanglish speech goes to Gnani as `ta-IN` for now. Gnani documents no Tanglish code. This stays untested until the clip comparison is done.
- Max clip length 30 s. Gnani's docs say both 30 s and 60 s, so we use the safe value (`SCHEMEBOT_STT_MAX_SECONDS`).
- The browser records WAV, not WebM, because Gnani's STT REST docs don't list WebM.
- Without a Gnani key the server still runs, and `/ask/voice` answers 503.
- Credits: tests and CI never call Gnani. Only the live app and the clip script do, and both are under the daily cap.
- The cap's lock is per process, so the app and the script running at exactly the same moment could miss one count. That's fine for one person on one laptop.

## Challenge facts re-checked (26 Oct, gnani.ai/internship)
- The submission must also say what each team member contributed.
- The TTS version is unclear: the page says Timbre v2.5 (Beta) in one place and v3.0 in another. Confirm in the dashboard.
