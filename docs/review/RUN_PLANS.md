# Live run plans (nothing has run yet; each one waits for your yes)

## A. Per-stage latency: 4 questions, 8 LLM calls, 2 Gnani calls

Every answer already records its stages in `timings_ms`: search, rerank, retrieval, llm_answer,
verifier, generation, total, plus stt for voice. The API's audit log
(`logs/requests.jsonl`) saves them, but never the question text. So one short session gives
the whole breakdown.

| # | What | Paid calls |
|---|---|---|
| 1 | English typed: "How much does PM-KISAN pay per year?" | 2 LLM (answer + verifier) |
| 2 | Tamil typed: the q016 Magalir Urimai amount question | 2 LLM |
| 3 | Tamil spoken (record q016 yourself, about 5 s) | 1 Gnani STT + 2 LLM |
| 4 | Listen to answer 2 (TTS), only if a Timbre model is chosen | 1 Gnani TTS |
| 5 | Ask question 1 again | 0 (answer cache; shows the cache time) |
| 6 | Hindi typed q025 (PM-KISAN), only if you want a third language | 2 LLM (optional) |

Steps on the laptop:
1. `uv run fastapi run`
2. Ask in the chat page in the order above.
3. `python -c "import json;[print(json.loads(l)['timings_ms']) for l in open('logs/requests.jsonl', encoding='utf-8')][-6:]"`

Free first: retrieval p50/p95 per language already come from the retrieval-only eval.

What I write up from this:
- a table of the stage times;
- which stage dominates (expected: llm_answer, but not measured yet);
- the one change to try next (for example, verifier off for short answers).

These are single measurements, so they are labelled n=1 each, not averages.

## B. Voice eval: 32 clips (or 40), 32-40 Gnani STT calls, 0 LLM calls

The tool exists already (`python -m schemebot.voice`):

```
uv run --frozen python -m schemebot.voice eval-script        # writes the reading list (32 rows)
#   --answerable 8 --unanswerable 2 gives 40 rows; the default is 6 + 2 per language
# record each row as the file name it gives (q001.wav ...), quiet room, phone mic, 16 kHz WAV
uv run --frozen python -m schemebot.voice eval data/voice/eval/     # asks yes before calling Gnani
```

- **Cost.** One STT call per clip, run once. Transcripts are cached next to the clips, so
  re-runs are free. That's 32-40 of the 100-a-day cap. How many credits one call uses isn't
  measured yet: check the Gnani dashboard after the first 2 clips and stop if it's more than
  expected (5,000 credits in total).
- **The report** compares typed and spoken questions on the same items, per language: Recall@5,
  refusals and transcript problems. It is retrieval-only, so there are no LLM calls. `--full`
  would add 2 LLM calls per clip, and needs a separate yes.
- **Tanglish.** Sent as ta-IN by default. A second pass with `--tanglish-code en-IN` costs one
  more call per Tanglish clip (8-10), so only do it if the first pass shows Tanglish problems.
- **Speakers.** Two people reading half each makes the result less about one voice. Write down
  who read which clips.
- **Honesty note.** The picker takes the first questions of each language, which are dev
  questions, so the voice result is "spoken vs typed on the same questions", not a held-out
  score. That is how it will be described.

## Order I suggest

B before A. The voice clips are the bigger unknown for the Gnani challenge. A takes 10 minutes
whenever you want a latency table for the report.
