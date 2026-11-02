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

## Notes on this run

- The 3 "clarified" replies came from a backend still running code from before the
  discovery fix (merged as #34): the replies took about 1 ms and were not cache hits. They
  are specific questions and will be answered once the laptop runs the latest main.
- `q038` (Tanglish income limit): a correct "2.5 laksham" answer was rejected by the number
  check. Fixed: Tanglish lakh and crore spellings are now read.
- `q003`, `q039` (central government employee and Magalir Urimai), `q031` (Hindi Ujjwala
  eligibility): the rule is in the documents (G.O. 15 p.11 "மாநில, ஒன்றிய அரசு ஊழியர்கள்";
  PMUY SoP p.2). New fact cards cover them once signed.

---

# Final live benchmark (2026-11-02)

60 questions (15 per language) through the website, after the corrections were confirmed,
the index rebuilt and the review fixes merged (voice always verified, card citations open
the PDF page).

| Language | Answered (covered questions) | Cited a correct page | Refused when not covered | Busy | Median | p90 |
|---|---|---|---|---|---|---|
| English | 92% (11/12) | 100% (11/11) | 100% (3/3) | 0 | 6.6 s | 44.6 s |
| Tamil | 92% (11/12) | 91% (10/11) | 100% (3/3) | 0 | 6.8 s | 22.4 s |
| Hindi | 75% (9/12) | 100% (9/9) | 67% (2/3) | 0 | 13.4 s | 29.2 s |
| Tanglish | 67% (8/12) | 100% (8/8) | 100% (3/3) | 0 | 8.4 s | 13.8 s |
| **All** | **81% (39/48)** | **97% (38/39)** | **92% (11/12)** | 0 | 9.2 s | 29.2 s |

Stage medians: retrieval 0.9 s, answer 3.0 s, verifier 1.7 s, question rewrite 2.7 s (when it
ran). The free Gemini tier was slower this morning than on 1 Nov (median 4.1 s then); the
pipeline did not change between the two runs except that the verifier now always runs.

**Question rewrite (review item A1).** It ran on 12 of 60 questions: 2 were then answered with
a correct page (q005, q044), 9 were correctly refused, 1 was missed (q039). It never caused a
wrong answer, so it stays on.

**Wrong or missed, and what was done:**

- `q016` (Tamil, "how much per year?") was answered with the **income-limit** fact card: a
  wrong answer. Fixed: a card now answers only its own kind of question.
- `q003` never reached the signed exclusions card: query cleaning turned "Urimai" into Tamil
  script, hiding the scheme name. Fixed: cards match the question as typed.
- `q036` (Hindi, "when is the next PM-KISAN instalment?"): answered with the instalment
  periods (April-July, August-November, December-March), cited and faithful, while the label
  expects a refusal because no date is given. Counted as a wrong pass.
- `q029`, `q032`, `q038` (Hindi APY pension, Hindi and Tanglish KMUT income limit): drafts
  dropped by the number check; `q066`, `q045`: dropped by the verifier; `q031`, `q039`,
  `q097`: the model judged the passages insufficient. To investigate with the drafts logged.

The raw replies of this run were not kept (overwritten by a branch reset); the numbers
above are from the run's printed report.
