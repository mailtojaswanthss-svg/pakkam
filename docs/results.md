# Evaluation results

> **110 of 110 questions are unverified drafts.** These numbers are for development only until every label has been checked by a person.

- **Run:** 2026-10-25T15-42-18Z, commit b438e85 (uncommitted changes)
- **Mode:** retrieval only, hybrid search, reranker on, Tanglish gloss on
- **Models:** BAAI/bge-m3, BAAI/bge-reranker-v2-m3
- **Refusal threshold:** 0.35
- **Corpus:** 18 documents, 2785 chunks
- **Questions:** 110 (0 verified)

| Group | Ans/Unans | Recall@1 | Recall@5 | MRR | Correct refusal | False refusal | Retrieval ms p50 / p95 |
|---|---|---|---|---|---|---|---|
| English | 21/7 | 86% | 100% | 0.91 | 86% | 5% | 435 / 523 |
| Tamil | 20/7 | 100% | 100% | 1.00 | 86% | 0% | 459 / 543 |
| Hindi | 20/7 | 80% | 100% | 0.89 | 100% | 0% | 471 / 545 |
| Tanglish | 21/7 | 90% | 95% | 0.92 | 100% | 29% | 420 / 499 |
| **All** | 82/28 | 89% | 99% | 0.93 | 93% | 9% | 444 / 543 |

Recall@k and MRR: share of answerable questions with a gold page in the top k passages, and mean reciprocal rank of the first one. Correct refusal: share of unanswerable questions refused. False refusal: share of answerable questions refused.
Retrieval-only run: refusal means retrieval confidence was below the threshold; answer metrics need a Claude API key.
