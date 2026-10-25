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
                         confidence < threshold? ──► refuse + helpline
                                                 │
                         LLM answers in user's language with [S1] citations
                                                 │
                         NLI guardrail: does each cited passage support its claim?
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
cp .env.example .env          # then fill in the Tesseract paths (and later your API key)
uv sync --extra ingest        # creates .venv with Python 3.12 + ingestion deps
uv run pytest
uv run python -m schemebot.ingest   # PDFs in data/raw + data/sources.json -> data/processed/
```

Each pipeline stage has its own extra (`ingest`, `index`, `generate`, `api`, `eval`), so you
only install the heavy ML libraries once you reach the stage that needs them.

## Project layout

```
src/schemebot/   ingest/ index/ retrieve/ generate/ api/   pipeline stages
eval/            evaluation scripts and metrics
data/            raw/ (not committed), processed/ (rebuilt), eval/questions.jsonl
docs/            data sources, results, technical report
web/             chat UI
tests/           unit tests per module
```

## Status

- [x] Phase 1: scaffold, config, data-source list
- [x] Phase 2: ingestion code (`python -m schemebot.ingest`); waiting on real documents
- [ ] Phase 3: indexing and hybrid retrieval
- [ ] Phase 4: answer generation and guardrails
- [ ] Phase 5: FastAPI service
- [ ] Phase 6: per-language evaluation
- [ ] Phase 7: UI, Docker, CI, write-up

## Limitations

Public documents only. It does not process applications or personal data, it is not an official
service, and its answers need human verification. Scheme rules change, so answers reflect the
document dates listed in the data-source file.

## License

MIT for the code. Source documents remain the property of their publishers.
