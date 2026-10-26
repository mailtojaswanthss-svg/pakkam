# indic-scheme-rag

**Multilingual Citizen-Scheme Assistant**: a citation-grounded RAG assistant that answers questions
about public Indian government schemes in **Tamil, Hindi, English and Tamil-English mixed (Tanglish)**
text, and measures how well it does in each language.

> **Disclaimer.** This is an independent student project. It is **not** an official service and is
> **not affiliated with any government body**. Answers are informational only and must be verified
> with the official source or office before acting on them. It uses only publicly available documents
> (listed in [docs/data_sources.md](docs/data_sources.md)) and stores no personal data.

## Why

Scheme information (eligibility, required documents, how to apply) sits in long PDFs, mostly in formal
English or Tamil, while people ask in their own language, often code-mixed. General chatbots can state
wrong eligibility or amounts with no source. This assistant:

- answers **only** from official public documents,
- cites the exact source passage (document, page) for every claim,
- says it doesn't know, and points to the official helpline, when the documents don't cover the question.

## How it works

```
PDF / web page ──► extract + language ID ──► section chunks (+ metadata)
                                                 │
                                    bge-m3 dense + sparse ──► Qdrant
                                                 │
query ──► normalise (Unicode, numerals) ──► hybrid search ──► rerank (+ English gloss of Tanglish)
                                                 │
                         confidence < threshold? ──► refuse (no LLM call)
                                                 │
                         Claude answers in the user's language, one source list per sentence
                                                 │
                         guardrail: valid citation? numbers in source? second model agrees?
                         unsupported sentences removed; nothing left ──► refuse
```

## Results

Retrieval on 194 **draft** questions (not yet checked by a native speaker), from
`python -m schemebot.evaluation --retrieval-only`. One person wrote all the questions and the
system. The refusal threshold was chosen on the first 110, so only the last 84 (held-out 2)
were untouched by any tuning. Full table in
[docs/results.md](docs/results.md), ablations and error analysis in the
[technical report](docs/report.md).

| Language | Answerable / unanswerable (n) | Recall@5 | MRR | Correct refusal | False refusal | Retrieval p50 / p95 |
|---|---|---|---|---|---|---|
| English | 39 / 10 | 100% | 0.91 | 90% | 5% | 495 / 921 ms |
| Tamil | 38 / 10 | 100% | 0.96 | 90% | 8% | 532 / 644 ms |
| Hindi | 38 / 10 | 100% | 0.88 | 100% | 8% | 578 / 691 ms |
| Tanglish | 39 / 10 | 92% | 0.87 | 100% | 44% | 525 / 775 ms |

Recall@5 and false refusal are out of the answerable questions; correct refusal is out of the
10 unanswerable ones, so one question moves it by 10 points. Recall@5 (98% overall, 151 of 154)
means a correct source page was among the 5 passages retrieved. It says nothing about whether
the written answer is correct. Latency is retrieval only, on a laptop RTX 4060.

**Hindi coverage is thin:** the corpus has 2 Hindi documents (5 pages, 14 chunks). Most Hindi
questions are answered from English or Tamil pages through cross-language retrieval, with the
answer written in Hindi.

Answers were checked live on 8 hand-picked questions with Gemini's free tier (one per
language plus the hardest cases): 5 cited answers and 3 correct refusals. All 8 answer
sentences were judged faithful by an LLM judge (model-judged, not by a person), and that judge
was the same model that ran the in-pipeline check, so it is not an independent judge. Eight
questions are a smoke test, not an accuracy figure. The full answer-quality evaluation needs a
paid key. The labels still need checking by native
speakers: `python -m schemebot.evaluation.review export review.csv` gives them a spreadsheet
with each question beside its gold-page text, and `import` marks the checked ones verified.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/). Tesseract (with `tam` and `hin` language packs) is
needed for OCR during ingestion; Docker only for the container.

The source PDFs and the search index are not in the repository. Before ingesting, download
each document in [data/sources.json](data/sources.json) from its `source_url` into `data/raw/`,
saved under the name in its `file` field. Ingestion OCRs about 1,350 pages, so the first run is
slow; the OCR result is cached.

```bash
cp .env.example .env                  # then fill in the Tesseract paths (and later your API key)
uv sync --extra ingest --extra index --extra generate --extra gemini --extra api  # + PyTorch (CUDA), Claude and Gemini SDKs, FastAPI
uv run pytest                         # fast tests, no models or API calls
uv run python -m schemebot.ingest     # PDFs in data/raw + data/sources.json -> data/processed/
uv run python -m schemebot.index      # chunks -> search index in data/index/
uv run python -m schemebot.retrieve "PM Kisan ku evlo panam kidaikum?"   # passages only
uv run python -m schemebot.generate "PM Kisan ku evlo panam kidaikum?"   # cited answer
uv run fastapi run                    # site + API on http://localhost:8000 (chat at /chat/, API docs at /docs)
```

`schemebot.generate` and the API need an LLM key to answer. Claude is the default: set
`SCHEMEBOT_ANTHROPIC_API_KEY` in `.env`. To use Gemini instead, set
`SCHEMEBOT_LLM_PROVIDER=gemini` and `SCHEMEBOT_GEMINI_API_KEY`; switching back is that one
line. Both providers return the same structured answers and go through the same guardrail.
Each LLM call waits at most 60 s per attempt and is retried twice on rate limits and server
errors (`SCHEMEBOT_LLM_TIMEOUT_SECONDS`, `SCHEMEBOT_LLM_RETRIES`). For a long evaluation run on
Gemini's free tier, set `SCHEMEBOT_LLM_RETRIES=7`. On the free tier Google may
use the prompts to improve its products, so use a paid key for a public demo. Without a key,
questions are still retrieved and checked, but answerable ones are refused as
`service_unavailable`.
The API keeps up to 256 answers in memory for 6 hours, so a repeated question (same words,
ignoring case, spaces and a final "?") is answered without calling the LLM
(`SCHEMEBOT_ANSWER_CACHE_SIZE`, `0` turns it off; `SCHEMEBOT_ANSWER_CACHE_TTL_SECONDS`).
The key also covers the answer language, the models and settings, and a hash of the index and
`data/corrections.json`, so a rebuilt index or a new correction starts fresh. Service errors are
never kept, nothing cached is logged, and a cached answer still counts against the rate limit.
The evaluation never uses this cache.

### API

`POST /ask` with `{"question": "..."}` (3-500 characters, any of the four language groups)
returns the answer as cited sentences, the citations (document, pages, source URL), whether
it refused and why, the retrieval confidence, a disclaimer and the latency. A refusal is a
normal `200` response. `GET /health` returns `{"status": "ok"}` once the models are loaded.

What leaves the app and what it keeps is summarised in [docs/PRIVACY.md](docs/PRIVACY.md).

Each request is logged to `logs/requests.jsonl` for audit and evaluation **without the
question text**: only a hash, its length and language, what was cited, refusals and
timings. Unexpected errors return a generic `500` with a request ID, never internals.

Each pipeline stage has its own extra (`ingest`, `index`, `generate`, `api`, `eval`), so you
only install the heavy ML libraries once you reach the stage that needs them.

`uv run pytest -m models` runs the slower tests that use the real bge-m3 and reranker models
(about 4.5 GB, downloaded on first use; a GPU makes them much faster).

For a public demo, `/ask` is rate limited per visitor (10 a minute) and in total (500 a
day), since each question can cost two LLM calls; over the limit it returns `429` with a
`Retry-After` header. Both limits are settings (`.env.example`).

### Docker

```bash
docker compose up --build     # http://localhost:8000
```

The image (`Dockerfile`, two stages, non-root) holds the code, the web UI and PyTorch with
CUDA; it does not hold the data. Build the index on the host first, as above: `compose.yaml`
mounts `data/` and `logs/`, keeps the downloaded models in a volume, reads `.env`, and asks
for the NVIDIA GPU (delete its `deploy` block to run on the CPU). The CUDA image is about
8 GB.

To put it online on Google Cloud Run (one L4 GPU, scales to zero), the `cloudrun` build target
bakes the index and both models into the image, and `deploy/cloudrun/deploy.sh` builds it in
Cloud Build and deploys it; step-by-step instructions are in
[deploy/cloudrun/README.md](deploy/cloudrun/README.md).

### Website on Vercel

The site in `web/` is plain HTML, CSS and JavaScript, so Vercel's free plan can host it: import
the GitHub repository at vercel.com/new, set **Root Directory** to `web`, framework **Other**,
no build command. The home page then works fully. The chat needs the answer server, which is
too large for Vercel (about 4.5 GB of models); until one is connected it says the live chat is
offline. To connect one (Cloud Run, or a tunnel to a laptop), add `web/vercel.json`:

```json
{
  "rewrites": [
    { "source": "/ask", "destination": "https://YOUR-SERVER/ask" },
    { "source": "/sources", "destination": "https://YOUR-SERVER/sources" }
  ]
}
```

Vercel then forwards the chat's requests to that server, so no cross-site setup is needed.

### CI

`.github/workflows/ci.yml` runs ruff, the format check, mypy and the fast tests on every push
and pull request, installing everything except PyTorch (the tests use fake models), then
builds the Docker image on pushes.

## Project layout

```
src/schemebot/   ingest/ index/ retrieve/ generate/ api/   pipeline stages
                 evaluation/   question set loader, metrics, judge, runner, report
data/            raw/ (not committed), processed/ (rebuilt), eval/questions.jsonl,
                 sources.json (documents), contacts.json (official helplines/websites)
docs/            data sources, results, technical report
web/             Pakkam: home page (index.html) and chat app (chat/), plain HTML/CSS/JS,
                 light and dark themes, photos in assets/img/ (Unsplash License, see CREDITS.md)
tests/           unit tests per module
```

## Status

- [x] Phase 1: scaffold, config, data-source list
- [x] Phase 2: ingestion of 18 official PDFs (Tamil, Hindi, English; 7 language pairs)
- [x] Phase 3: indexing (bge-m3 dense + sparse in Qdrant) and hybrid retrieval with reranking,
  plus an English gloss of Tanglish questions for the reranker
- [x] Phase 4: cited answers in the question's language, refusal on low confidence, and a
  three-layer guardrail (valid citation, numbers match the source, second-model support check);
  **not yet run against the live API** (needs a key in `.env`)
- [x] Phase 5: FastAPI service (`/ask`, `/health`, `/sources`), audit log without personal
  data, rate limits for a public demo
- [~] Phase 6: evaluation pipeline, ablations and a review sheet done; 194 draft questions
  (146 held out) to be verified by native speakers; answer quality checked live on 8
  questions, the full run waits for a paid key
- [x] Phase 7: web UI **Pakkam** with light and dark themes, Docker image and compose file,
  GitHub Actions CI, [technical report](docs/report.md)

## Limitations

Public documents only. It does not process applications or personal data, it is not an official
service, and its answers need human verification. Scheme rules change, so answers reflect the
document dates listed in the data-source file.

OCR misreads some digits in Tamil and Hindi pages (Rs.1,000 read as 4,000). Known misreadings
are listed in `data/corrections.json`. An answer may never use a listed wrong number from a
passage covering that page. Only after a person has checked the printed PDF page and filled in `confirmed_by`,
`confirmed_on` and `page` does ingestion replace the text, and then the citation is flagged
`ocr_corrected` in the API. Re-run ingestion and indexing after confirming an entry.

## License

The code is under the [MIT License](LICENSE). The licence covers the code only: the source PDFs remain the property of their publishers (and are not in this repository), and the photos in `web/assets/img/` are under the Unsplash License (see `CREDITS.md`).
