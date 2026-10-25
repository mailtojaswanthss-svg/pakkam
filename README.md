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
query ──► normalise (Unicode, numerals, transliteration) ──► hybrid search ──► rerank
                                                 │
                         confidence < threshold? ──► refuse (no LLM call)
                                                 │
                         Claude answers in the user's language, one source list per sentence
                                                 │
                         guardrail: valid citation? numbers in source? second model agrees?
                         unsupported sentences removed; nothing left ──► refuse
```

## Results

_No results yet._ Every number here will be produced by `eval/run_eval.py` on
`data/eval/questions.jsonl` and can be re-run.

| Language | Recall@5 | Faithfulness | Citation acc. | Correct refusal | p50 / p95 latency |
|---|---|---|---|---|---|
| Tamil | – | – | – | – | – |
| Hindi | – | – | – | – | – |
| English | – | – | – | – | – |
| Tanglish | – | – | – | – | – |

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and Docker. Tesseract (with `tam` and `hin` language packs)
is needed for OCR during ingestion.

```bash
cp .env.example .env                  # then fill in the Tesseract paths (and later your API key)
uv sync --extra ingest --extra index --extra generate --extra api  # + PyTorch (CUDA), Claude SDK, FastAPI
uv run pytest                         # fast tests, no models or API calls
uv run python -m schemebot.ingest     # PDFs in data/raw + data/sources.json -> data/processed/
uv run python -m schemebot.index      # chunks -> search index in data/index/
uv run python -m schemebot.retrieve "PM Kisan ku evlo panam kidaikum?"   # passages only
uv run python -m schemebot.generate "PM Kisan ku evlo panam kidaikum?"   # cited answer
uv run fastapi run                    # site + API on http://localhost:8000 (chat at /chat/, API docs at /docs)
```

`schemebot.generate` and the API need a Claude API key to answer: set
`SCHEMEBOT_ANTHROPIC_API_KEY` in `.env`, or `ANTHROPIC_API_KEY` in the environment. Without one,
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

## Project layout

```
src/schemebot/   ingest/ index/ retrieve/ generate/ api/   pipeline stages
                 evaluation/   question set loader, metrics, judge, runner, report
data/            raw/ (not committed), processed/ (rebuilt), eval/questions.jsonl,
                 sources.json (documents), contacts.json (official helplines/websites)
docs/            data sources, results, technical report
web/             Pakkam: home page (index.html) and chat app (chat/), plain HTML/CSS/JS,
                 photos in assets/img/ (Unsplash License, see CREDITS.md)
tests/           unit tests per module
```

## Status

- [x] Phase 1: scaffold, config, data-source list
- [x] Phase 2: ingestion of 18 official PDFs (Tamil, Hindi, English; 8 language pairs)
- [x] Phase 3: indexing (bge-m3 dense + sparse in Qdrant) and hybrid retrieval with reranking
- [x] Phase 4: cited answers in the question's language, refusal on low confidence, and a
  three-layer guardrail (valid citation, numbers match the source, second-model support check);
  not yet run against the live API
- [x] Phase 5: FastAPI service (`/ask`, `/health`), audit log without personal data
- [~] Phase 6: evaluation pipeline done (`python -m schemebot.evaluation`, see
  [docs/evaluation.md](docs/evaluation.md)); 48 draft questions, to be verified and grown to ~200
- [~] Phase 7: web chat UI **Pakkam** done (`web/`, served by `uv run fastapi run` at
  http://localhost:8000; design in [docs/design-package.md](docs/design-package.md));
  Docker, CI and the write-up still to do

## Limitations

Public documents only. It does not process applications or personal data, it is not an official
service, and its answers need human verification. Scheme rules change, so answers reflect the
document dates listed in the data-source file.

## License

MIT for the code. Source documents remain the property of their publishers.
