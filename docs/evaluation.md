# Evaluation

How the per-language evaluation works, how to extend and verify the labelled questions, and
what the error analysis has found so far. Results live in [results.md](results.md) and are
produced only by `python -m schemebot.evaluation`; nothing there is typed by hand.

## Running it

```bash
uv run python -m schemebot.evaluation --retrieval-only   # no API key needed
uv run python -m schemebot.evaluation                    # full pipeline: needs the API key
uv run python -m schemebot.evaluation --retrieval-only --mode dense   # ablations:
uv run python -m schemebot.evaluation --retrieval-only --mode sparse  #   dense / sparse only
uv run python -m schemebot.evaluation --retrieval-only --no-rerank    #   without reranker
```

Each run rewrites `docs/results.md` (stamped with the git commit, models, threshold and
corpus size) and writes every question's details to `data/eval/runs/` for error analysis.

## The question set

`data/eval/questions.jsonl`, one JSON object per line:

| Field | Meaning |
|---|---|
| `id` | Unique, e.g. `q017` |
| `group` | `en`, `ta`, `hi` or `ta-Latn` (Tanglish) |
| `question` | As a citizen would type it |
| `answerable` | `false` if the documents do not answer it; the system should refuse |
| `gold` | Documents and **page numbers** that answer it; empty when not answerable |
| `reference` | Short correct answer, for the person checking answers |
| `status` | `draft` until a person has checked it, then `verified` |

Gold answers are pages, not chunk ids, so labels survive changes to chunking. A retrieved
passage counts as correct when it comes from a gold document and overlaps a gold page. When
a fact appears in both language versions of a document, list both.

### Verifying a draft

For each question: open the PDF at the gold pages and confirm (1) the pages really answer
the question, (2) no other page answers it better (add it if so), (3) the reference answer
matches the document's wording and numbers, (4) the Tamil/Hindi/Tanglish reads naturally.
Then set `"status": "verified"`. The report shows how many labels are verified and warns
while any are drafts.

The current 48 questions (12 per group, 3 unanswerable in each) were drafted from the first
10 documents. The abstract's target is about 200 (about 50 per group). The 8 policy notes
added later (health, higher education, Adi Dravidar and tribal welfare, BC/MBC welfare) are
not yet covered by any question.

## Metrics

- **Recall@1, Recall@5, MRR**: on answerable questions, whether a gold page is among the
  top 1 / top 5 retrieved passages, and the mean reciprocal rank of the first gold page.
- **Correct refusal**: share of unanswerable questions the system refused.
- **False refusal**: share of answerable questions it refused. In `--retrieval-only` runs
  "refused" means retrieval confidence was below the threshold (the pipeline's first check).
- **Faithfulness** (full runs): share of answer sentences that an independent judge
  (`judge_model`, different from the in-pipeline verifier) finds supported by the passages
  they cite. It is an LLM judge: check a sample of its verdicts by hand and report that.
- **Citation accuracy** (full runs): share of citations on answerable questions that point
  to a gold page.
- **Latency**: p50 and p95 of retrieval alone and of the full answer.

## Error analysis so far

Findings from development runs on draft labels; to be re-checked on verified labels.

1. **Tanglish gets low reranker confidence.** The right page is usually in the top 5, but
   the reranker scores it low (e.g. 0.015 for "breakfast scheme endha class pasangalukku"),
   so most answerable Tanglish questions fall under the refusal threshold. Candidate fixes
   to test: transliterating Tanglish to Tamil script before reranking, or a lower threshold
   for Tanglish only.
2. **OCR corrupts numbers in Tamil and Hindi text.** The Tamil policy note's OCR text reads
   "ரூ.7000" per month for Pudhumai Penn where the English version says Rs.1000; the Hindi
   APY brochure reads "co वर्ष" for 60 years and "रु.000" for Rs.1000. The guardrail's number
   check cannot catch these because the wrong number is in the cited passage. Questions q020
   (Pudhumai Penn, Tamil) and q029 (APY pension, Hindi) exercise this.
3. **Near-miss unanswerable questions pass the confidence check.** "When is the next
   PM-KISAN instalment?" (the guidelines describe instalment periods but no dates) and
   "How do I get a new ration card?" (the Magalir Urimai G.O. discusses ration cards at
   length) score 0.44 and 0.85. Only the LLM's "not answerable" judgement can refuse these,
   so they need full-pipeline runs.
4. **A draft label was wrong.** The Magalir Urimai yearly amount is stated on the English
   page 3 and also on the Tamil page 9; the draft listed only page 3, so a correct retrieval
   was scored as a miss until the label was fixed. This is why drafts must be verified.
