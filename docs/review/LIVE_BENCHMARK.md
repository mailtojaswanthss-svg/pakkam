# Live benchmark (2026-11-01)

Questions sent to `https://pakkam-alpha.vercel.app` one at a time, as a visitor would. Times are end to end
(network, tunnel, search, answer writing, checks). Answers come from Gemini (free plan).

| Language | Answered (covered questions) | Cited a correct page | Refused when not covered | Busy | Median | p90 |
|---|---|---|---|---|---|---|
| English | 88% (7/8) | 86% (6/7) | 100% (2/2) | 0 | 3.9 s | 16.1 s |
| Tamil | 75% (6/8) | 83% (5/6) | 100% (2/2) | 0 | 3.9 s | 13.2 s |
| Hindi | 75% (6/8) | 100% (6/6) | 100% (2/2) | 0 | 4.1 s | 12.4 s |
| Tanglish | 75% (6/8) | 100% (6/6) | 100% (2/2) | 0 | 4.3 s | 7.0 s |
| **All** | 78% (25/32) | 92% (23/25) | 100% (8/8) | 0 | 4.1 s | 7.0 s |

## To look at

- `q003` (en) **missed** not_in_documents: Can a family with a central government employee get Magalir Urimai Thogai?
- `q031` (hi) **missed** not_in_documents: उज्ज्वला योजना में गैस कनेक्शन के लिए कौन पात्र है?
- `q038` (ta-Latn) **missed** unsupported: magalir urimai ku income limit evlo
- `q039` (ta-Latn) **missed** not_in_documents: govt job la irukavanga family ku magalir urimai thogai kidaikuma

Raw replies: `data/eval/live_benchmark.json`. Questions: `data/eval/questions.jsonl`
(the reference answers are drafts; correctness of wording is graded separately).
