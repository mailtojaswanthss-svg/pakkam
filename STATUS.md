# Pakkam + Gnani voice: status

Last updated: 26 Oct 2026. Own target: 8 Nov (13 days left). Hard deadline: 10 Nov, 11:59 PM IST (15 days left).

## Done
- Voice in, code side (26 Oct):
  - `src/schemebot/voice/stt.py`: Gnani Prisma v2.5 speech-to-text client (`POST /stt/v3`).
  - `POST /ask/voice`: audio upload plus language, then speech to text, then the existing answer pipeline. Returns the answer and the transcript.
  - Chat page: mic button (records 16 kHz mono WAV, stops at 30 s), upload button, and a "I will speak in" picker.
  - 23 new tests with a fake STT (no key, no network, no credits). 213 tests pass; ruff and mypy are clean.
  - Checked in a headless browser with a fake mic and a fake STT only. **Not yet tested against real Gnani.**

## Next
1. Jaswanth: put the Gnani key in `.env` (`SCHEMEBOT_GNANI_API_KEY=...`) and record 5 to 10 Tanglish clips (synthetic content only).
2. Tanglish comparison script: each clip through `ta-IN` and `en-IN`, transcripts to CSV. It shows the call count and asks before spending credits.
3. Voice out (Timbre TTS).

## Blockers
- Gnani key and Tanglish clips (Jaswanth).
- Unknown: what one credit buys. Check the dashboard before any bulk run.

## Decisions
- Tanglish speech goes to Gnani as `ta-IN` for now. Gnani documents no Tanglish code. This stays untested until the clip comparison is done.
- Max clip length 30 s. Gnani's docs say both 30 s and 60 s, so we use the safe value (`SCHEMEBOT_STT_MAX_SECONDS`).
- The browser records WAV, not WebM, because Gnani's STT REST docs don't list WebM.
- Without a Gnani key the server still runs, and `/ask/voice` answers 503.
- Credits: tests and CI never call Gnani. Only the live app and the clip script do.

## Challenge facts re-checked (26 Oct, gnani.ai/internship)
- The submission must also say what each team member contributed.
- The TTS version is unclear: the page says Timbre v2.5 (Beta) in one place and v3.0 in another. Confirm in the dashboard.
