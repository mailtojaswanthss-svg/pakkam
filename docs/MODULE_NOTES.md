# Module notes for interview practice

A starting point only. Each of you should rewrite every section in your own words after reading the code it points to; interviewers will ask follow-ups that these notes don't cover. Practise 20 minutes a day: one person explains a module, the other asks the "likely questions".

The pipeline in one line: **PDF → text (OCR when needed) → chunks → search index → hybrid search → rerank → refuse if unsure → LLM answer with citations → guardrail → answer (→ speech).**

## 1. Ingestion and OCR (`src/schemebot/ingest/`)

- **What:** reads each PDF in `data/sources.json` page by page. Uses the PDF's own text layer when it is clean, otherwise Tesseract OCR in the document's languages (`tam+eng`, `hin+eng`, `eng`). Splits text into chunks of at most 1,000 characters (`chunk.py`, `MAX_CHUNK_CHARS`) that never cross a section, with a small overlap.
- **Why OCR at all:** many Tamil PDFs use legacy fonts that map Tamil glyphs to Latin letters, and the Hindi PDFs have broken Devanagari. 1,353 of 2,688 pages went through OCR (`report.md` §3).
- **Known weakness:** OCR misreads digits (a leading 1 as 4 in Tamil). The guardrail can't catch it because the wrong number is in the source passage.
- **Likely questions:** How do you decide a page needs OCR? Why not OCR every page? What happens to a wrong amount in an OCR page?

## 2. Retrieval (`retrieve/hybrid.py`, `retrieve/retriever.py`, `index/`)

- **What:** the question is embedded with **bge-m3**, which gives a dense vector (meaning, works across languages) and sparse weights (exact words like scheme names and numbers). Qdrant searches both, takes the top 20 from each, and fuses them with **Reciprocal Rank Fusion** (RRF): it combines by rank, so the two scores never need the same scale.
- **Normalisation:** Unicode tidy-up, and Tamil/Devanagari digits mapped to 0-9 on both sides (`text.py`).
- **Likely questions:** Why hybrid and not dense only? Be honest here: in the ablation (`report.md` §8, draft questions) dense-only matched hybrid (recall@5 99% vs 98%) and was faster, so sparse added nothing measurable; hybrid stays for exact names and numbers that the question set barely tests. Sparse alone is weak across languages (29% recall@5 for Hindi). What is RRF? How does a Hindi question find an English page? (Dense vectors from bge-m3 are multilingual.)
- **Also know:** the reranker is the only source of a usable refusal signal; without it every unanswerable question passed the threshold.

## 3. Reranker (`retrieve/rerank.py`)

- **What:** **bge-reranker-v2-m3**, a cross-encoder. It reads the question and each candidate passage *together* and gives a 0-1 relevance score. Too slow for the whole corpus, so it only rescores the first stage's candidates and keeps the best 5.
- **Tanglish gloss (`retrieve/tanglish.py`):** the reranker reads romanised Tamil poorly, so a fixed list of about 169 Tanglish words gets an English gloss appended ("evlo" → "how much"). Scheme names are left alone.
- **Numbers to know:** recall@1 rises from 68% to 84% with the reranker, at about 250 ms (`report.md` §8, draft questions, n=154 answerable).
- **Likely questions:** Bi-encoder vs cross-encoder? Why append the gloss instead of replacing the question? Why is Tanglish still 44% false refusal (n=39)?

## 4. Refusal threshold (`config.py:69`, `generate/answer.py`)

- **What:** the reranker's score for the best passage is the **confidence**. Below **0.35** the system refuses without calling the LLM, which saves cost and avoids guessing.
- **How chosen:** on the first 110 questions; held-out 2 (n=84) was not used for it.
- **Two more refusal points after it:** the LLM can say "not answerable", and the guardrail can remove every sentence.
- **Likely questions:** Why not a lower threshold for Tanglish? (Answerable and unanswerable Tanglish scores overlap.) What is the trade-off between correct refusal and false refusal? Why do near misses ("next PM-KISAN instalment date") pass it?

## 5. Answer generation (`generate/answer.py`, `prompt.py`, `llm.py`, `gemini.py`)

- **What:** the LLM (Claude by default, or Gemini) gets the question and the 5 passages, and must reply in JSON: whether the question is answerable, and a list of sentences, each with the passage numbers it uses. It answers in the question's language.
- **On refusal:** a fixed message in the user's language (`messages.py`), plus the scheme's official contact when retrieval found the scheme (`contacts.json`).
- **Likely questions:** Why structured JSON instead of free text? How do you make it answer in Tanglish? What happens when the API fails?

## 6. Guardrails (`generate/guardrails.py`)

Three checks on every sentence, cheapest first. A sentence that fails any check is removed; if none are left, the answer is refused.
1. **Citation check:** it cites at least one passage that was actually shown.
2. **Number check:** every number in the sentence appears in a cited passage (after removing thousands separators).
3. **Support check:** a second, cheaper model reads each sentence with its passages and says whether they state it. A sentence it skips counts as unsupported ("fail closed").

- **Limits:** a wrong OCR number in the source passes check 2; "2.5 lakh" vs "2,50,000" would fail check 2 even though they are equal.
- **Likely questions:** Why check numbers separately? What does "fail closed" mean? What can still get through?

## 7. Speech to text (`voice/stt.py`, `POST /ask/voice`, voice branch)

- **What:** the browser records 16 kHz mono WAV (`web/assets/recorder.js`; WAV because Gnani's REST docs don't list WebM). The server checks size, format and length (30 s cap), then sends it to **Gnani Prisma v2.5** (`POST https://api.vachana.ai/stt/v3`) with a language code. The transcript then goes through the same pipeline as a typed question.
- **Tanglish:** sent as `ta-IN` for now. Gnani documents no Tamil-English code, and this is **untested** until the clip test.
- **No key, no voice:** `/ask/voice` returns 503; tests use a fake transcriber, so they never spend credits.
- **Likely questions:** Why WAV? Why 30 s and not 60 s? How do you know Tanglish works? What is stored? (Nothing: see `docs/PRIVACY.md`.)

## 8. Text to speech (not built yet)

- To fill in once Timbre TTS is added: which version (v2.5 or v3.0), which voice and language codes, how numbers like "Rs.6,000" are read, and how long it takes.

## 9. Evaluation (`evaluation/`)

- **Question set:** 194 questions in `data/eval/questions.jsonl`: 4 groups (English, Tamil, Hindi, Tanglish), 38-39 answerable and 10 unanswerable each, in 3 batches. All are still **drafts**. Gold labels are pages.
- **Runner (`runner.py`):** retrieves every question; with an LLM key it also answers and asks a judge model whether each sentence is supported. `python -m schemebot.evaluation --retrieval-only` needs no key and writes `docs/results.md` plus a per-question file in `runs/`.
- **Metrics (`metrics.py`):** recall@1/@5 and MRR (is a gold page in the top passages), correct refusal (unanswerable refused), false refusal (answerable refused), faithfulness (**model-judged**), citation accuracy, latency p50/p95.
- **Review (`review.py`):** exports a spreadsheet for native speakers and imports their checks.
- **Likely questions:** What does 98% recall@5 mean, and what does it not mean? (A gold page is in the top 5; it is not answer correctness.) Why is n=10 per group a problem for refusal rates? Who wrote the questions? Is the judge independent? (No: it is model-judged, and the live test used one model for verifying and judging.)

## 10. API and logging (`api/`)

- **What:** FastAPI app serving the site and `POST /ask` (and `/ask/voice`). Rate limits: 10 a minute per visitor, 500 a day in total. The audit log keeps a hash of the question, never its text.
- **Likely questions:** What do you log and why not the question? What happens over the limit? (429 with `Retry-After`.)
