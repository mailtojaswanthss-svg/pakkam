# Evaluation results

> **48 of 48 questions are unverified drafts.** These numbers are for development only until every label has been checked by a person.

- **Run:** 2026-10-25T12-01-24Z, commit 070eb8d (uncommitted changes)
- **Mode:** retrieval only, hybrid search, reranker on
- **Models:** BAAI/bge-m3, BAAI/bge-reranker-v2-m3
- **Refusal threshold:** 0.35
- **Corpus:** 18 documents, 2785 chunks
- **Questions:** 48 (0 verified)

| Group | Ans/Unans | Recall@1 | Recall@5 | MRR | Correct refusal | False refusal | Retrieval ms p50 / p95 |
|---|---|---|---|---|---|---|---|
| English | 9/3 | 67% | 100% | 0.76 | 67% | 11% | 403 / 1,864 |
| Tamil | 9/3 | 89% | 100% | 0.92 | 67% | 0% | 430 / 451 |
| Hindi | 9/3 | 78% | 100% | 0.87 | 100% | 0% | 447 / 506 |
| Tanglish | 9/3 | 67% | 100% | 0.79 | 100% | 56% | 407 / 516 |
| **All** | 36/12 | 75% | 100% | 0.83 | 83% | 17% | 430 / 514 |

Recall@k and MRR: share of answerable questions with a gold page in the top k passages, and mean reciprocal rank of the first one. Correct refusal: share of unanswerable questions refused. False refusal: share of answerable questions refused.
Retrieval-only run: refusal means retrieval confidence was below the threshold; answer metrics need a Claude API key.
