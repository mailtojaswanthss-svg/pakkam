# Privacy: what leaves Pakkam and what it keeps

Pakkam is a student project with no accounts and no sign-in. Please don't type or say personal details (names, Aadhaar numbers, phone numbers) into it: the questions it answers are about schemes, not about you.

## What the app keeps

- **No question text and no audio.** Each request writes one line to `logs/requests.jsonl` with a 16-character hash of the question, its length and language, what was cited, whether it refused and why, and the timings (`src/schemebot/api/audit.py`). The hash lets us spot repeated questions without storing them.
- **No transcripts.** The chat page shows what it heard, but neither the page nor the server saves it.
- **No cookies or analytics.** The page stores only the theme choice in the browser (`web/assets/theme.js`). The pages load fonts from Google Fonts, so Google sees the visitor's IP address when the fonts load.

## What leaves the app

| What | Sent to | Why | Their rules |
|---|---|---|---|
| Your recorded question (audio), voice mode only | Gnani (`api.vachana.ai`), Prisma v2.5 speech to text | To turn speech into text | Gnani's terms. How long Gnani keeps audio is not stated in the docs we read: UNKNOWN. |
| The question text, plus the matching passages from the public documents | The LLM provider set in `.env`: Anthropic (Claude) or Google (Gemini) | To write and check the answer | The provider's terms. On Gemini's free tier, Google may use prompts to improve its products, so use a paid key for a public demo. |
| The answer text, voice mode only (once text to speech is built) | Gnani, Timbre text to speech | To read the answer aloud | Gnani's terms. |

Questions that retrieval refuses (confidence below the threshold) never reach the LLM.

## What this means in one line

The app itself stores no audio and no question text. The speech and LLM providers receive what they need to answer, under their own terms.

Voice input lives on the voice branch until it is merged; this note describes it as built there (`src/schemebot/voice/stt.py`, `POST /ask/voice`).
