# Backend review (read-only), 26 Oct 2026

Scope: `main` (35ba419) and the voice branch `claude/project-thread-fpld2g` (2491d46), which adds
`/ask/voice`, `/speak`, `voice/stt.py`, `voice/tts.py` and the daily Gnani cap. PR #3
(`claude/ui-proof-refusal`) changes only `web/` files and no error handling, so it is out of scope.

No code was changed. No Gnani or LLM call was made. The probes below are small offline Python
scripts run against the repo code (no network). Line numbers for `api/main.py` are from the voice
branch; every other file cited is identical on both branches.

Severity assumes what was decided for the challenge: a local demo and a recorded video, no
public hosting. Where a finding becomes worse if the app is ever hosted publicly (Cloud Run, HF
Space, Vercel plus tunnel), it says so.

## Summary

| # | Question | Verdict | Severity |
|---|---|---|---|
| 1a | Gnani STT/TTS have timeouts | CONFIRMED (30 s, no retries) | Low |
| 1b | LLM calls have timeouts and backoff for 429/5xx | CONFIRMED, but limits are far too long | High |
| 1c | User-facing error messages | CONFIRMED, two are misleading | Medium |
| 2 | Daily Gnani counter is safe with two requests at once | CONFIRMED in one process, NOT TRUE across processes | Medium |
| 3 | Upload validation: size, content type, duration for non-WAV | Size CONFIRMED; content type and non-WAV duration NOT TRUE | Medium |
| 4 | Verifier calls parallel? Answer cache? | One batched verifier call, run after the answer call; no cache | High (latency) |
| 5 | Behaviour when the 500/day limit is hit | Requests serialise behind one lock; user sees a wrong "wait a minute" message | High if hosted, Medium now |
| 6 | Per-visitor rate limit reads X-Forwarded-For correctly | NOT TRUE on Cloud Run and HF Space configs (spoofable) | High if hosted, Low now |
| 7 | "2.5 lakh" vs "2,50,000" wrongly removes a sentence | CONFIRMED (test below) | Medium |
| 8 | Ingestion checks amounts agree across Tamil/English pairs | NOT TRUE (no check); 5 known mismatches | High for the demo |
| 9 | Errors or logs reveal keys, paths or text; CORS | No leaks found; no CORS middleware (same-origin only) | Low |
| 10 | Dependencies pinned; results.md records commit and date | Lockfile CONFIRMED; results.md commit is not reproducible | Medium |

## 1. Timeouts, retries and error messages

**Gnani STT and TTS: CONFIRMED, Low.**
- One `httpx.Client` each with a 30 s timeout (`voice/stt.py:80-82`, `voice/tts.py:69-71`,
  default `stt_timeout_seconds = 30.0` at `config.py:87`; TTS reuses the STT timeout,
  `voice/tts.py:139`).
- No retries at all. Given the 5,000 free credits this is the right choice: a retry would spend
  another credit (the budget counts every attempt, `voice/budget.py:4-5`).
- 429 gives "The speech service is busy. Try again in a minute." (`stt.py:102-103`,
  `tts.py:92-93`).

**LLM calls: CONFIRMED, but the limits are too long. High.**
- Claude (`generate/llm.py:71`) uses the SDK defaults, since none are set: 10 minute timeout
  and 2 retries with backoff (0.5 s to 8 s) on 408, 409, 429 and 5xx (anthropic 2.3.0,
  `_constants.py:10-15`, `_base_client.py:945-960`). Worst case for one call is about 30 minutes.
- Gemini (`generate/gemini.py:30-62`) sets 8 attempts, 2 s doubling to 60 s, and 120 s per
  attempt, retrying 408, 429, 500, 502, 503 and 504 (google-genai 2.33.0,
  `_api_client.py:652-659`). The comment says "about three minutes in all", which is the backoff
  alone. With slow attempts, the worst case is about 18 minutes per call.
- Each answer makes two calls in a row (answer, then verifier), and both run inside the global
  lock (see item 5). One stuck call therefore blocks every other user for the whole time.
- Cloud Run cuts the request at 300 s (`deploy/cloudrun/deploy.sh`, `--timeout 300`) but the
  server thread keeps running and keeps holding the lock.

**User-facing messages: CONFIRMED, two misleading. Medium.**
- LLM failure becomes a normal refusal with "The answering service is not available right now"
  in the question's language (`generate/answer.py:149-151`, `generate/messages.py:44-49`). Good.
- Unexpected errors return a generic 500 with a request ID (`api/main.py:179-188`). Good.
- Gnani 5xx says "could not read this recording" (`stt.py:104-105`), which blames the user's
  clip for a server fault.
- The chat page has no client-side timeout on `fetch` (`web/assets/chat.js:316-325`, no
  `AbortController`), so a stuck answer shows the waiting bar until the server or proxy gives up.

## 2. Daily Gnani counter (`logs/gnani-calls.json`)

**One process: CONFIRMED safe.** `CallBudget.take()` reads, checks and writes under a
`threading.Lock` (`voice/budget.py:43-49`), and `shared_budget()` gives STT and TTS the same
object (`budget.py:74-81`). The write is atomic (temp file, then `replace`, `budget.py:61-67`).
Probe: 4 threads x 300 calls on one object gave exactly 1200.

**Two processes (app and the `compare` script at the same time, or more than one worker):
NOT TRUE. Medium.**
- The lock is per process. There is no file lock.
- All processes write the same temp name `gnani-calls.tmp` (`budget.py:64`), so one process can
  rename another's temp file away.
- Probe: 4 processes x 300 calls on one file. Expected 1200; the file said 23, and 644 calls
  raised `FileNotFoundError` (which in the app becomes a generic 500). The cap undercounts, so it
  can be overshot.
- An unreadable or corrupt file counts as 0 calls (`budget.py:53-55`): the cap fails open.
- On Windows, `replace` can also fail while another process has the file open (not tested here).
- Today only one worker runs, so this needs the app and `compare` running together. The risk is
  real during clip testing.

## 3. Audio upload validation

`check_audio` (`voice/stt.py:58-68`), called at `api/main.py:219`:

| Check | Verdict | Evidence |
|---|---|---|
| Max size | CONFIRMED: 5 MB (`config.py:85`), read with a cap (`main.py:213`) | But see the note below |
| Content type | NOT TRUE | Only the file name's extension is checked (`stt.py:64`); `UploadFile.content_type` and the file's bytes are never looked at |
| Duration, WAV | CONFIRMED (`stt.py:47-55`, 66-68) | A 45 s WAV is rejected with 400 |
| Duration, MP3/OGG/FLAC/AAC/M4A | NOT TRUE | `wav_seconds` returns None and the clip passes |

Probe results (`check_audio` with the default limits):

```
rejected: 45 s real WAV -> 400 Keep the question under 30 seconds.
ACCEPTED (would spend a Gnani credit): 4.9 MB of random bytes named .mp3 (~5 min at 128 kbps)
ACCEPTED (would spend a Gnani credit): plain text renamed .wav
ACCEPTED (would spend a Gnani credit): PDF bytes named .m4a
```

Also: a broken WAV passes too, because an unreadable WAV also gives None. FastAPI parses the
whole multipart body before the rate-limit dependency runs (fastapi `routing.py:455` before
`:511`), and Starlette puts no size limit on file parts, so a huge upload is stored to disk
before the 5 MB check. Cloud Run caps requests at 32 MB; a local or tunnelled server has no cap.
Severity Medium: the mic records WAV, so the main path is checked; the upload button is not.

## 4. Latency

- **Verifier: one call, not per sentence.** `check_answer` sends all kept sentences in a single
  verifier request (`generate/guardrails.py:125-128`). It runs after the answer call, so each
  answer is retrieval, then LLM answer, then LLM verify, in sequence (`answer.py:137-146`).
  "Sequential per-sentence calls" is NOT TRUE; "parallel" is also NOT TRUE.
- **Answer cache: NOT TRUE.** No cache of answers or retrieval anywhere in `src/` (the only
  caches are settings, `config.py:139`, and OCR at ingest time).
- **Where the time goes** (existing results only):
  - Retrieval p50 533 ms, p95 720 ms on a laptop RTX 4060 (`docs/results.md`, all 194 questions).
  - End to end 13 to 52 s per answer for the 8 live Gemini free-tier answers, including retries
    (`docs/report.md:320`).
  - So retrieval is about 1 to 4 % of the time; the two LLM calls are the rest.
  - The split between answer and verifier is UNKNOWN: `timings_ms["generation"]` covers both
    (`answer.py:135-153`), and the audit log (`logs/requests.jsonl`) is not in the repo.
- **Settings that add latency:** answer model default `claude-opus-5-5` at effort `medium` with
  16,000 max output tokens (`config.py:46-47`, `llm.py:17`); Gemini thinking level MEDIUM.
- **The lock** (`api/main.py:197` and `:232`) wraps `service.answer()`, which includes both LLM
  calls, not only GPU work. Two users at once means the second waits for the first's full answer.

## 5. Behaviour under traffic

- One uvicorn worker (`Dockerfile:58-61`); Cloud Run allows 4 concurrent requests on one instance
  (`deploy.sh`, `--concurrency 4 --max-instances 1`).
- Requests run one at a time behind `state.lock`. At 13 to 52 s per answer that is about 70 to
  280 answers an hour at most, and the fourth user in a queue can wait over 2 minutes; past 300 s
  Cloud Run returns 504.
- **500/day limit** (`config.py:78`, `api/ratelimit.py:53-69`): a sliding 24-hour window kept in
  memory. It resets on every restart; on Cloud Run with `--min-instances 0` that is every cold
  start, so it is not a true daily cap there.
- `/speak` uses the same limiter (`main.py:242`), so "Listen" uses up question slots too.
- **When the limit is hit:** the server returns 429 with "Too many questions. Wait a little and
  ask again." and `Retry-After` in seconds, which can be many hours (`main.py:134-142`). The
  page ignores both and shows "Pakkam is getting a lot of questions. Wait a minute, then ask
  again." (`chat.js:15`, `:337`). For the daily cap that is wrong: the user retries and fails
  again. The per-visitor and daily limits give the same message.
- The Gnani cap file lives in `logs/`, which on Cloud Run is the container's own disk, so that
  cap also resets on every cold start (the docstring at `voice/budget.py:3-4` says it survives
  restarts, which holds only on a laptop).

## 6. Per-visitor rate limit

- The visitor is `request.client.host` (`api/main.py:135`): the IP address uvicorn reports.
- Uvicorn takes it from X-Forwarded-For only for proxies listed in `FORWARDED_ALLOW_IPS`
  (`Dockerfile:58-61`, default 127.0.0.1).
- **Cloud Run and HF Space set `FORWARDED_ALLOW_IPS="*"`** (`Dockerfile:82-86`,
  `deploy/hf-space/Dockerfile`). With `*`, uvicorn 0.54 takes the **first** entry of
  X-Forwarded-For (`uvicorn/middleware/proxy_headers.py`, `get_trusted_client_address`), and the
  first entry is whatever the visitor sent. Probe:
  `_TrustedHosts("*").get_trusted_client_address("6.6.6.6, 203.0.113.7")` returns `6.6.6.6`.
- So a visitor who sends a different fake X-Forwarded-For each time gets a fresh 10/minute
  bucket each time, and one person can use up the 500/day for everyone. NOT TRUE that it is read
  correctly. This assumes Google's front end appends to the header rather than replacing it, as
  Google documents for its load balancers; not tested on Cloud Run.
- Locally with the default 127.0.0.1, uvicorn walks the list from the right and takes the first
  untrusted address, which is correct behind a local tunnel that appends.
- Through Vercel's rewrite, the result depends on whether Vercel replaces the header: UNKNOWN.
- Severity: Low now (no public hosting), High if the server is ever public.

## 7. Number guardrail: "2.5 lakh" vs "2,50,000"

**CONFIRMED. Medium.** `numbers_in` removes commas and compares digit strings
(`generate/guardrails.py:22`, `46-52`, `116-119`). It has no idea of lakh, crore or financial
years. Probe with `check_answer(..., verifier=None)`:

```
REMOVED | Eligible if family income is below 2.5 lakh.        | passage: Rs.2,50,000      | ['2.5'] vs ['250000']
REMOVED | Eligible if family income is below Rs.2,50,000.     | passage: Rs. 2.5 lakh     | ['250000'] vs ['2.5']
REMOVED | ஆண்டு வருமானம் 2.5 லட்சத்திற்குள் ...                 | passage: ரூ.2,50,000/-     | ['2.5'] vs ['250000']
REMOVED | The scheme started in 2023-24.                      | passage: year 2023-2024   | ['2023','24'] vs ['2023','2024']
KEPT    | You get Rs. 6,000 per year.                          | passage: Rs.6000/-        |
KEPT    | ஆண்டுக்கு ரூ.1,000 ...                                 | passage: ௧,௦௦௦ (Tamil digits) |
KEPT    | You get one thousand rupees a month.                 | passage: Rs.1000          | no digits, so not checked
```

A test case to add (fails today):

```python
def test_lakh_matches_full_number():
    passage = "Annual family income should not exceed Rs.2,50,000."
    result = check_answer([DraftSentence("Income must be below 2.5 lakh.", [1])], [passage])
    assert result.kept  # today: removed as number_not_in_source
```

The failure is safe (a sentence is removed, never a wrong number kept), and the prompt asks the
model to copy amounts as written (`generate/prompt.py:35-36`), which limits how often it happens.
It bites when the answer language differs from the passage (a Tamil answer from an English page).
The opposite gap: amounts written in words ("one thousand") skip the number check and rely on
the verifier alone.

## 8. Ingestion: do paired Tamil/English amounts agree?

**NOT TRUE: no check exists.** `data/sources.json` has no pairing field (keys: doc_id, scheme,
file, source_url, language, doc_date, accessed, force_ocr, title), and nothing in
`src/schemebot/ingest/` or `index/` compares documents. Severity High for the demo, because the
number guardrail cannot catch a wrong number that is in the cited passage
(`docs/report.md:98-99`).

Known mismatches already written down in the repo:

| Document | OCR reads | Correct (English or PDF) | Source |
|---|---|---|---|
| tn-hedu-policy-note-2024-ta, Pudhumai Penn | ரூ.4,000 a month | Rs.1,000 | `docs/report.md:94-96` |
| tn-swwe-policy-note-2024-ta, Pudhumai Penn | ரூ.7000 a month | Rs.1000 | `docs/evaluation.md:122-124` |
| tn-hfw-policy-note-2024-ta, insurance income limit | ரூ.4,20,000 | Rs.1,20,000 | `docs/report.md:95-96` |
| tn hostel food charge (Tamil note) | 4400 | Rs.1,400 | `docs/report.md:97` |
| apy-brochure-hi | रु.000; "co वर्ष" | Rs.1000; 60 years | `docs/report.md:96`, `docs/evaluation.md:124` |
| Tamil note, senior-citizen helpline | 14167 in body text | 14567 | `docs/report.md:98` |

Pattern noted in the report: a leading 1 read as 4 in Tamil OCR. The demo-number sheet on the
weakness branch (`docs/review/demo-numbers.csv`) flags the Pudhumai Penn and APY rows for a
by-eye check, but no row is checked yet.

## 9. Errors, logs and CORS

**No leak found. Low.**
- Keys are `SecretStr` (`config.py:45`, `55`, `81`) and are only read when building clients.
  No log line prints a key, header or URL with a key; Gnani keys go in a header, not the URL.
- Unhandled errors return only "Internal error" plus a request ID; the stack trace goes to the
  server log only (`main.py:179-188`). Library error text is replaced by fixed messages
  (`llm.py:116-122`, `gemini.py:95-99`, `stt.py:92-109`, `tts.py:86-99`).
- The audit log stores a hash and length of the question, never the text (`api/audit.py:1-5`,
  `29-46`). `/speak` logs nothing (`main.py:243`).
- Small notes: FastAPI's 422 replies echo the bad input back to the same caller (normal);
  `/docs` and `/openapi.json` are public (they describe routes only); uvicorn's access log keeps
  visitor IPs; the `compare` script writes transcripts to `data/voice/runs/`, which is gitignored
  (`.gitignore:36`).

**CORS: no CORS middleware at all** (no `CORSMiddleware` or `Access-Control` anywhere in `src/`).
So no other origin is allowed: browsers on other sites cannot read the API's replies. The chat
page is served from the same server (`main.py:277`) and the Vercel plan uses a rewrite
(`README.md:124-139`), so nothing needs CORS today. One gap: a multipart POST to `/ask/voice` is
a "simple" request that browsers send cross-site without a preflight, so another page could make
a visitor's browser spend Gnani credits (it cannot read the answer). Low, and capped by the
daily budget.

`/speak` reads aloud any text up to 1,200 characters, not only Pakkam's answers
(`api/schemas.py:91-95`, `main.py:243-252`). Low, also capped by the daily budget.

## 10. Reproducibility

- **Lockfile: CONFIRMED.** `uv.lock` pins every package (for example fastapi 0.162.0, uvicorn
  0.54.0, anthropic 2.3.0, google-genai 2.33.0, torch 2.11.0+cu128). CI and both Dockerfiles use
  `uv sync --frozen` (`.github/workflows/ci.yml:29`, `Dockerfile:24`, `:31`). uv 0.11.12 and
  Python 3.12 are pinned (`.python-version`).
- **Not pinned:** the base image is a tag, not a digest (`python:3.12-slim-trixie`); the models
  are downloaded without a revision (`Dockerfile:73-75`), so BAAI/bge-m3 or the reranker could
  change under the same name; source PDFs and the index are not in the repo, and
  `data/sources.json` has URLs and access dates but no file hashes.
- **results.md: commit and date are recorded, but not usefully.** It says
  `Run: 2026-10-26T09-04-44Z, commit c050d23 (uncommitted changes)` (`docs/results.md:5`).
  Commit c050d23 is not on any branch on GitHub (`git cat-file` fails after fetching all
  branches), and the run had uncommitted changes, so nobody can rerun that exact code. The stamp
  comes from `evaluation/report.py:16-34`, which records but does not refuse a dirty tree.

## Ranked fix list

Hours are estimates for one person including tests. "Fits" means it fits in the 8 days to
3 Nov next to the voice and video work; the total marked "fits" is about 15 hours.

| Rank | Fix | Items | Hours | Fits in 8 days |
|---|---|---|---|---|
| 1 | Check the demo amounts by eye against the PDFs (Pudhumai Penn, APY, insurance limit) and keep them out of the demo until checked. Already planned in demo-numbers.csv | 8 | 2-3 (person, no code) | Yes |
| 2 | Lock only retrieval (the GPU part), not the LLM calls | 4, 5 | 2 | Yes |
| 3 | Set explicit LLM limits: Claude timeout about 60 s with 2 retries; Gemini 3 attempts, 45 s each. One answer then ends within about 3 minutes | 1 | 1.5 | Yes |
| 4 | Number guardrail understands lakh/crore (English, Tamil லட்சம், Hindi लाख) and "2023-24" years; add the test above | 7 | 3 | Yes |
| 5 | Audio check: look at the first bytes to confirm the format matches the extension; for non-WAV files, reject anything larger than 30 s could be at a high bitrate (about 1.2 MB). No new dependency | 3 | 2 | Yes |
| 6 | Gnani counter: one temp file name per process, a simple lock file shared by processes (works on Windows), and fail closed if the file is unreadable | 2 | 2.5 | Yes |
| 7 | Daily-limit message: a separate 429 text for the daily cap ("today's limit is reached, try tomorrow"); the page shows the server's text for 429. Page change goes through the UI thread | 5 | 1 | Yes |
| 8 | Rerun the retrieval-only eval from a clean pushed commit (free, local GPU) so results.md names a commit on GitHub | 10 | 1 + run time | Yes |
| 9 | Answer cache: in memory, keyed on the normalised question, a few hours long. Saves LLM credit and time on repeated demo questions | 4 | 2 | Optional |
| 10 | Pin model revisions (Hugging Face commit hash) and the base image digest | 10 | 1 | Optional |
| 11 | Fix the Gnani 5xx wording and add a 2-minute timeout on the page's fetch (page part via the UI thread) | 1 | 1 | Optional |
| 12 | Script that compares numbers near the same scheme name across each Tamil/English pair and lists differences for a person to check | 8 | 6-8 | No |
| 13 | Rate limit by the correct X-Forwarded-For entry when hosted (or keep the server private) | 6 | 1.5 | No (only if hosting) |
| 14 | Reject uploads over 6 MB before parsing (check Content-Length) | 3 | 1 | No (local demo is fine) |
| 15 | Keep the 500/day and Gnani counts in lasting storage on Cloud Run | 5 | 3 | No (only if hosting) |
| 16 | `/speak` only reads text Pakkam produced (signed answer ID); CSRF check on `/ask/voice` | 9 | 3 | No |

Ranks 2-8 change code and need a go-ahead each, one step at a time.

## Fixes made on 26 Oct (with Jaswanth's go-ahead)

On branch `claude/project-thread-vl8ipg`, which has the voice branch merged in (several fixes touch
voice code). One commit per fix, each with tests; no Gnani or LLM call was made. Ruff, mypy and
all 306 fast tests pass.

| Rank | Fix | What changed |
|---|---|---|
| 2 | Lock only retrieval | `api/main.py`: the API lock is gone. The retriever's own lock (`retrieve/retriever.py`) still makes GPU work take turns; LLM calls now run side by side. Test: two questions are answered at the same time. |
| 3 | LLM limits | New settings `SCHEMEBOT_LLM_TIMEOUT_SECONDS` (60) and `SCHEMEBOT_LLM_RETRIES` (2), used by both Claude and Gemini. For a long eval run on Gemini's free tier set retries to 7 (README, `.env.example`). |
| 4 | Number check | `generate/guardrails.py`: "2.5 lakh", "2.5 லட்சம்", "2.5 लाख" and "1 crore" are written out in full before comparing; "2023-24" matches "2023-2024". Different amounts are still rejected (tests for both). |
| 5 | Audio check | `voice/stt.py`: first bytes must match the extension; WAV and FLAC lengths read from the header (unreadable files refused); MP3/OGG/AAC/M4A over 30 s at 384 kbps (about 1.4 MB) refused. |
| 6 | Gnani counter | `voice/budget.py`: lock file shared by processes, per-process temp file, stale lock removed after 30 s, a broken count file now stops calls (it used to reset the count to 0). The 4-process probe now gives exactly 1200. |
| 7 | Daily-limit message | `api/ratelimit.py`, `api/main.py`: the daily cap says "come back tomorrow"; the per-visitor limit says "wait a minute". The chat page still shows its own 429 text; showing the server's text is a one-line change in `web/assets/chat.js` for the UI thread. |
| 9 | Answer cache | `generate/cache.py`: up to 256 answers for 6 hours, keyed on the tidied question; temporary failures are not kept; the API only, never the eval. |
| 11 | Gnani 5xx wording | `voice/stt.py`: a Gnani server fault now says "The speech service is not working right now. Type your question instead." instead of blaming the recording. The page's 2-minute fetch timeout was done by the UI thread (`web/assets/chat.js`, now on main). |
| 10 | Pinned versions | New settings `SCHEMEBOT_EMBEDDING_REVISION` / `SCHEMEBOT_RERANKER_REVISION` (full commit hashes) load exactly that model version, in the app, the indexer and the Cloud Run image; the eval report prints them. The uv image is pinned by digest. The Python base image digest and the two commit hashes still have to be filled in from the laptop (Docker Hub and Hugging Face were not reachable from the cloud session). |
| 8b | Known OCR misreadings | `ingest/corrections.py`, `data/corrections.json`: listed wrong numbers can't be used in answers; person-confirmed fixes are applied at ingestion and flagged `ocr_corrected`. See `OCR_CORRECTIONS_DESIGN.md`. |

Not done here, because they need a person or the laptop:

- **Rank 1, demo amounts.** Open each PDF page in `docs/review/demo-numbers.csv` (weakness branch)
  and fill in what the page shows, starting with Pudhumai Penn (Tamil higher-education and social
  welfare notes), the APY Hindi brochure and the Rs.1,20,000 insurance limit. Leave a row out of
  the demo until it is checked.
- **Rank 8, clean results stamp.** On the laptop, with the index built: commit or stash any local
  changes, push, then run `uv run python -m schemebot.evaluation --retrieval-only` (free, no API
  key). Check that `docs/results.md` names a commit that is on GitHub and does not say
  "uncommitted changes", then commit it.
