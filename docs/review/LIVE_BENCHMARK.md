# Live benchmark (2026-11-02)

Questions sent to `https://pakkam-alpha.vercel.app` one at a time, as a visitor would. Times are end to end
(network, tunnel, search, answer writing, checks). Answers come from Gemini (free plan).

| Language | Answered (covered questions) | Cited a correct page | Refused when not covered | Busy | Median | p90 |
|---|---|---|---|---|---|---|
| English | 78% (7/9) | 100% (7/7) | 67% (2/3) | 0 | 27.8 s | 60.4 s |
| Tamil | 100% (9/9) | 100% (9/9) | 100% (3/3) | 0 | 24.1 s | 50.9 s |
| Hindi | 43% (3/7) | 100% (3/3) | – | 0 | 38.4 s | 43.6 s |
| **All** | 76% (19/25) | 100% (19/19) | 83% (5/6) | 0 | 30.1 s | 57.9 s |

## To look at

- `q005` (en) **error** The read operation timed out: Is a retired pensioner eligible for PM-KISAN?
- `q009` (en) **error** HTTP 502: What is the senior citizen helpline number in Tamil Nadu?
- `q010` (en) **error** HTTP 530: What is the interest rate on Sukanya Samriddhi Yojana deposits?
- `q028` (hi) **error** HTTP 502: ओटीपी आधारित ई-केवाईसी के लिए क्या चाहिए?
- `q029` (hi) **error** HTTP 502: अटल पेंशन योजना में कितनी पेंशन मिलती है?
- `q030` (hi) **error** HTTP 530: अटल पेंशन योजना में शामिल होने की उम्र क्या है?
- `q031` (hi) **error** HTTP 530: उज्ज्वला योजना में गैस कनेक्शन के लिए कौन पात्र है?

Raw replies: `data/eval/live_benchmark.json`. Questions: `data/eval/questions.jsonl`
(the reference answers are drafts; correctness of wording is graded separately).
