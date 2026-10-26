# Evaluation results

> **194 of 194 questions are unverified drafts.** These numbers are for development only until every label has been checked by a person.

- **Run:** 2026-10-26T09-04-44Z, commit c050d23 (uncommitted changes)
- **Mode:** retrieval only, hybrid search, reranker on, Tanglish gloss on
- **Models:** BAAI/bge-m3, BAAI/bge-reranker-v2-m3
- **Refusal threshold:** 0.35
- **Corpus:** 18 documents, 2785 chunks
- **Questions:** 194 (0 verified)

| Group | Ans/Unans | Recall@1 | Recall@5 | MRR | Correct refusal | False refusal | Retrieval ms p50 / p95 |
|---|---|---|---|---|---|---|---|
| English | 39/10 | 85% | 100% | 0.91 | 90% | 5% | 495 / 921 |
| Tamil | 38/10 | 92% | 100% | 0.96 | 90% | 8% | 532 / 644 |
| Hindi | 38/10 | 79% | 100% | 0.88 | 100% | 8% | 578 / 691 |
| Tanglish | 39/10 | 82% | 92% | 0.87 | 100% | 44% | 525 / 775 |
| **All** | 154/40 | 84% | 98% | 0.90 | 95% | 16% | 533 / 720 |

Recall@k and MRR: share of answerable questions with a gold page in the top k passages, and mean reciprocal rank of the first one. Correct refusal: share of unanswerable questions refused. False refusal: share of answerable questions refused.
Retrieval-only run: refusal means retrieval confidence was below the threshold; answer metrics need a Claude API key.
