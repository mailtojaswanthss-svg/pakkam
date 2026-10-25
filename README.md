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

Retrieval on 110 **draft** questions (about 21 answerable and 7 unanswerable per group; 62
held out), from `python -m schemebot.evaluation --retrieval-only`. Full table in
[docs/results.md](docs/results.md), ablations and error analysis in the
[technical report](docs/report.md).

| Language | Recall@5 | MRR | Correct refusal | False refusal | Retrieval p50 / p95 |
|---|---|---|---|---|---|
| English | 100% | 0.91 | 86% | 5% | 435 / 523 ms |
| Tamil | 100% | 1.00 | 86% | 0% | 459 / 543 ms |
| Hindi | 100% | 0.89 | 100% | 0% | 471 / 545 ms |
| Tanglish | 95% | 0.92 | 100% | 29% | 420 / 499 ms |

Answers were checked live on 8 questions with Gemini's free tier (one per language plus the
hardest cases): 5 correct cited answers, 3 correct refusals, all sentences judged faithful.
The full answer-quality evaluation needs a paid key. The labels still need checking by native
speakers.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/). Tesseract (with `tam` and `hin` language packs) is
needed for OCR during ingestion; Docker only for the container.

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
On Gemini's free tier, rate-limited calls are retried for about three minutes, and Google may
use the prompts to improve its products, so use a paid key for a public demo. Without a key,
questions are still retrieved and checked, but answerable ones are refused as
`service_unavailable`.

### API

`POST /ask` with `{"question": "..."}` (3-500 characters, any of the four language groups)
returns the answer as cited sentences, the citations (document, pages, source URL), whether
it refused and why, the retrieval confidence, a disclaimer and the latency. A refusal is a
normal `200` response. `GET /health` returns `{"status": "ok"}` once the models are loaded.

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
- [~] Phase 6: evaluation pipeline and ablations done; 110 draft questions (62 held out),
  still to be verified by native speakers and grown to ~200; answer-quality metrics wait
  for the API key
- [x] Phase 7: web UI **Pakkam** with light and dark themes, Docker image and compose file,
  GitHub Actions CI, [technical report](docs/report.md)

## Limitations

Public documents only. It does not process applications or personal data, it is not an official
service, and its answers need human verification. Scheme rules change, so answers reflect the
document dates listed in the data-source file.

## License

MIT for the code. Source documents remain the property of their publishers.
