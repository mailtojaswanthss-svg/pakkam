# Live benchmark (2026-11-01)

Questions sent to `https://pakkam-alpha.vercel.app` one at a time, as a visitor would. Times are end to end
(network, tunnel, search, answer writing, checks). Answers come from Gemini (free plan).

| Language | Answered (covered questions) | Cited a correct page | Refused when not covered | Busy | Median | p90 |
|---|---|---|---|---|---|---|
| English | 88% (7/8) | 86% (6/7) | 100% (2/2) | 0 | 5.5 s | 17.9 s |
| Tamil | 75% (6/8) | 83% (5/6) | 100% (2/2) | 0 | 5.3 s | 10.9 s |
| Hindi | 75% (6/8) | 100% (6/6) | 100% (2/2) | 0 | 8.0 s | 42.9 s |
| Tanglish | 88% (7/8) | 100% (7/7) | 100% (2/2) | 0 | 5.2 s | 14.8 s |
| **All** | 81% (26/32) | 92% (24/26) | 100% (8/8) | 0 | 5.5 s | 12.8 s |

## To look at

- `q003` (en) **missed** not_in_documents: Can a family with a central government employee get Magalir Urimai Thogai?
- `q031` (hi) **missed** not_in_documents: उज्ज्वला योजना में गैस कनेक्शन के लिए कौन पात्र है?
- `q039` (ta-Latn) **missed** not_in_documents: govt job la irukavanga family ku magalir urimai thogai kidaikuma

Raw replies: `data/eval/live_benchmark.json`. Questions: `data/eval/questions.jsonl`
(the reference answers are drafts; correctness of wording is graded separately).

## Fixed after this run

The 3 "clarified" replies were a bug: specific questions naming a scheme in an inflected
form (அடல் ஓய்வூதியத் **திட்டத்தில்** … வயது **வரம்பு**, मगलिर उरिमै … आय **सीमा**) were
treated as "find me a scheme" and given a list. Discovery now only answers explicit browsing
("find", "any scheme", "which schemes", "என்ன திட்டங்கள் உள்ளன", "कौन सी योजनाएँ"); 0 of the
194 evaluation questions trigger it.
