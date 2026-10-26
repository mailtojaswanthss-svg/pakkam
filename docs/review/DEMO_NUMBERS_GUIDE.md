# Demo number check (plan item #2)

**Sheet:** [demo-numbers.csv](demo-numbers.csv), 24 rows. It opens in Excel or Google Sheets (UTF-8, so the Tamil and Hindi text shows).
**Who:** the teammate, or Jaswanth. It needs someone who can read Tamil and Hindi numbers on a scanned page. **Time:** about 2-3 hours.

## Why

Tamil OCR sometimes reads a leading 1 as 4 (Rs.1,000 as 4,000), and the guardrail can't catch it because the wrong number is in the source passage. No number shown in the demo, on the site or in the video goes out until a person has seen it on the PDF page.

## The candidate demo questions (Jaswanth confirms the final list)

| Question | Why it's a candidate |
|---|---|
| q001 Who can apply for Magalir Urimai? (English) | Answered in the live test |
| q016 Magalir Urimai yearly amount (Tamil) | Answered in the live test; same number as the home page |
| Magalir Urimai income limit | The answer to the chat's first suggestion can include it |
| q025 PM-KISAN amount (Hindi) | Answered in the live test; chat suggestion |
| q040 PM-KISAN amount (Tanglish) | Answered in the live test |
| Atal Pension age limit | Chat suggestion |
| Atal Pension amount | Shown on the home page |
| Pudhumai Penn amount | Shown on the home page; **known OCR risk** in Tamil |
| q043 Ujjwala documents (Tanglish) | Answered in the live test; no numbers |
| q011 / q023 (refusals) | Correctly refused in the live test; no numbers, so no rows |

The last six rows are the numbers typed on the home page.

## How to check each row

1. Download the PDF from `source_url` (they are public government sites).
2. Go to each page in `pdf_pages_to_open`. These are the **page numbers in the PDF viewer** (the first page of the file is 1), not the numbers printed on the page.
3. Find the fact. In `pdf_shows_exactly`, type exactly what the page says, number and unit included (for example `ரூ.1,000`). Read Tamil and Hindi pages by eye: don't copy from the PDF's text layer, which can be wrong.
4. Fill `matches_expected` (yes/no), `checked_by` (your name) and `date`. Put anything odd in `notes`, such as "page 9 says per month, not per year".
5. You only need one matching page per document. Write `not on this page` for pages that don't state it.

## What happens with a "no"

- If the English PDF is right and only the Tamil or Hindi OCR is wrong: keep the question, but make sure the demo answer cites the English page, or swap the question.
- If the expected answer itself is wrong: fix the reference in `data/eval/questions.jsonl` and the home page text, and log it in `docs/CONTRIBUTIONS.md`.
- Never show a number in the demo that has a "no" or an empty row.
