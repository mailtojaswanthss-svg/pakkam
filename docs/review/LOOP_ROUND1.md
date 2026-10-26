# Improvement loop, round 1 (26 Oct)

Input: your run `2026-10-26T09-04-44Z-hybrid.jsonl` (retrieval-only, commit c050d23 with
uncommitted changes), read-only from your laptop. Only dev questions (q001-q110) were studied.

## Dev results before the change

| Language | n ans/unans | R@1 | R@5 | False refusal | Correct refusal |
|---|---|---|---|---|---|
| English | 21/7 | 86% | 100% | 5% | 86% |
| Tamil | 20/7 | 100% | 100% | 0% | 86% |
| Hindi | 20/7 | 80% | 100% | 0% | 100% |
| Tanglish | 21/7 | 90% | 95% | **29%** | 100% |

## The 10 dev misses, by cause

| Cause | Questions | What I did |
|---|---|---|
| Tanglish: the right page is in the top 3, but the reranker's confidence is below 0.35 | q042, q044, q096, q101, q103 | Added the missing verbs (irukanum, padikra, tharaangala, padicha, ponaa, kudupaanga) and word pairs ("join panna" = to join, "age evlo" = what age) to the gloss |
| Tanglish: the wrong pages were retrieved | q099 | Same vocabulary fix (it had 3 unknown verbs); may need more |
| Tanglish: the gold page is at rank 6 or lower | q039 | Not changed in this round |
| English: the right page is at rank 3, low confidence | q005 | Not changed (a reranker limit, not a word problem) |
| Answered an unanswerable question in a retrieval-only run | q011, q023 | Not changed. In the full pipeline the LLM can still refuse these. Raising the threshold would cost real answers. |

The threshold stays at 0.35.

## Not measured yet

The models aren't in the cloud session, so the effect of this change is unknown until you
re-run. On your laptop, after pulling the branch (or merging PR #8):

```
git checkout claude/project-thread-vl8ipg && git pull
uv run --frozen python -m schemebot.evaluation --retrieval-only
uv run --frozen python -m schemebot.evaluation.summary --split dev --failures
uv run --frozen python -m schemebot.evaluation.summary --split held-out
```

I'll read the new run myself from `data/eval/runs` (read-only), so you don't need to send
anything.

## Result (laptop run 2026-10-26T13-26-50Z, commit a09846e, retrieval only, no paid calls)

Dev, before -> after: Tanglish R@5 95% -> 95%, false refusal 29% -> 29%. English, Tamil and Hindi unchanged.

- Fixed: q042 (confidence 0.26 -> above 0.35).
- Newly refused: q105 (0.38 -> 0.27). The gloss of "kudupaanga" as "they give" seems to pull the
  reranker away from "subsidy".
- q099 now has a gold page (hedu-en p6) in the top 3, but is still refused (0.04).
- Net: 0 dev questions fixed. Under the loop rule (fewer than 3 fixed), the gloss loop stops here.

Held-out (reported, not used for choices): Tanglish R@5 89%, false refusal 61%. English, Tamil and
Hindi R@5 100%, false refusal 6-17%.

What this says: for most Tanglish misses a right page is already in the top 3. The problem is the
reranker's confidence on romanised Tamil, not the search. Word glossing does not move it
reliably. The next lever is a separate cut-off for Tanglish, chosen on dev only. It needs your
OK, because it changes the refusal rule.

Laptop test run: ruff and mypy clean, 411 passed. 8 test_stt cases errored only on Windows
(test names too long for an environment variable), now fixed with short ids. One multiprocess
budget test failed once in the full suite and passed alone; left for a later look.
