# Hidden until checked against the PDFs

Items taken off the site on 26 Oct 2026 until Jaswanth confirms them against the PDF page. Restore an item only when he says so.

The original text of every item is in commit `b30177d` (branch `claude/ui-proof-refusal`). To see it: `git show b30177d:web/index.html` or `git show b30177d:web/assets/home.js`.

## Hidden

| # | Item | Was shown as | Source to check | How to restore |
|---|---|---|---|---|
| 1 | Pudhumai Penn amount | "₹1,000 a month, paid into the student's bank account." (`web/index.html`, people section) | SWWE policy note 2024-25 (English) p7; Higher Education policy note (English) p6. The Tamil OCR text reads 4,000 | Put "₹1,000 a month" back in place of "a monthly amount" |
| 2 | Hindi example answer (PM-KISAN e-KYC) | The Hindi demo tab and its answer, with the slip "PM-KISAN, page 1" (`web/assets/home.js` `DEMOS.hi`, and the tab button in `web/index.html`) | PM-KISAN e-KYC note (Hindi) p1 | Restore `DEMOS.hi` and the two tab buttons from `b30177d`, and set `current` back to `'hi'` |
| 3 | "43 pages" | The big number on the story tile (`web/index.html`, `.tile-paper`) | G.O.(Ms) No.15: the page count of the PDF (the repo's `docs/data_sources.md` says en pp 1-7, ta pp 8-43) | Re-add `<p class="big-number">43 <span>pages</span></p>` above the tile heading |
| 4 | Tanglish demo citation | The slip "PM-KISAN, page 1" with the quote "Rs 6,000/- per year in three equal instalments…", the "p. 1" chip, and the step "Reading page 1 of the e-KYC note" (`web/assets/home.js` `DEMOS.tl`) | PM-KISAN e-KYC note (English) p1 | Add `slipTitle`, `slipLine`, `slipLang: 'en'` back to `DEMOS.tl`, and set `read` to "Reading page 1 of the e-KYC note". `fill()` shows the slip and chip again when `slipTitle` is set |

Removed earlier in T0 (commit `af190c6`), and on no hero or demo list until confirmed:
- Magalir Urimai ₹12,000 a year / page 9 (the hero slip and the Tamil demo)
- Atal Pension ₹1,000 to ₹5,000 a month
- PM-KISAN page 10 / ₹2,000 each instalment

## Still shown, labelled "Example answer", until confirmed

- PM-KISAN ₹6,000 a year, in three equal instalments: the people card on the home page, and the Tanglish demo answer.

## Still shown, from data the server sends (needs the same check)

- **Source lines in chat** show each document's title from `data/sources.json` exactly as written. Two titles include a day: "G.O.(Ms) No.15, 10 July 2023" and "G.O.(Ms) No.43, 27 July 2022". The others have month and year only, or no date. No date is added from `doc_date`.
- **Refusal links in chat** come from `data/contacts.json`: pfrda.org.in, pmkisan.gov.in, pmuy.gov.in, kmut.tn.gov.in, tn.gov.in and the rest of that file.
