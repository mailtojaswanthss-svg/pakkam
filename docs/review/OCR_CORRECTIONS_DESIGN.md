# Stopping known-bad OCR amounts from reaching answers (design only)

Written 26 Oct 2026. Nothing here is built. You pick an option once the PDF pages are checked by
a person.

## The problem in one paragraph

Some Tamil and Hindi pages were read by OCR, and OCR misread digits. The worst case is Pudhumai
Penn: the Tamil higher-education note's text reads "ரூ.4,000" a month, but the English notes say
Rs.1,000. Claude's first pass over the PDFs on your laptop suggests the printed Tamil page (p33)
also says ரூ.1,000, so the 4,000 is only in our extracted text. **No person has checked this
yet.** The number guardrail cannot catch it, because the wrong number really is in the cited
passage, so the answer looks fully supported.

## Known bad readings

| Document, page | Our text reads | Should be | Checked by a person? |
|---|---|---|---|
| tn-hedu-policy-note-2024-ta, p33 (Pudhumai Penn) | ரூ.4,000 | ரூ.1,000 | No (Claude first pass: 1,000) |
| tn-swwe-policy-note-2024-ta, p11 (Pudhumai Penn) | ரூ.7000 | ரூ.1000 | No (Claude first pass: 1000) |
| apy-brochure-hi, p1 | रु.000; "co वर्ष" | रु.1000; 60 वर्ष | No (Claude first pass: 1000) |
| tn-hfw-policy-note-2024-ta (insurance income limit) | ரூ.4,20,000 | Rs.1,20,000 | No, page not found yet |
| Tamil note, hostel food charge | 4400 | Rs.1,400 | No, page not found yet |
| Tamil note, senior-citizen helpline | 14167 | 14567 | No, page not found yet |

The source for the list is `docs/report.md` (Known damage) and `docs/evaluation.md`. The first
three rows are in `docs/review/demo-numbers.csv`, which also gives the pages to open.

## Three options

### A. A corrections file applied at ingestion (recommended)

A new file, `data/corrections.json`, lists each fix:

```json
{
  "doc_id": "tn-hedu-policy-note-2024-ta",
  "page": 33,
  "ocr_reads": "ரூ.4,000",
  "pdf_shows": "ரூ.1,000",
  "checked_by": "<the person who looked at the printed page>",
  "checked_on": "2026-10-27"
}
```

Ingestion applies these after OCR and before chunking. Here is how it works:

- **Only person-checked rows are applied.** A row with an empty `checked_by` is refused, so a
  Claude first pass can never change the text by itself.
- **It fails loudly.** If `ocr_reads` is not found on that page exactly once, ingestion stops with
  an error. So a re-OCR or a new PDF version can't silently skip a fix.
- **The OCR cache is untouched.** It keeps the raw reading, and the fix is applied on top, so
  the original is always there to compare.
- **Fixed chunks are marked.** They get `extraction = "ocr-corrected"`, and the ingest report
  lists each fix it applied.
- **The guardrail just works.** After this, the passage says 1,000, so it backs a 1,000 answer
  and rejects a 4,000 one.

Cost:
- About 2.5 hours of code and tests.
- Then you re-run ingestion and indexing on your laptop. OCR is cached, so it is not redone.
  Re-embedding takes as long as your last index build. I haven't measured it here, because the
  PDFs and index are not in this container.

The weak point: the citation then shows text we edited. To be honest about that, the source
line could say "corrected by hand from the printed page", which is a small UI change.

### B. A "do not trust" list checked at answer time

The same kind of file, but nothing in the index changes. If a sentence uses a listed number
(for example 4000) and cites the listed page, the sentence is removed, the same way the
guardrail removes unsupported sentences.

- About 1.5 hours, and no re-index needed.
- It only removes. It never puts the right number in, so a Pudhumai Penn question in Tamil might
  get a refusal, or an answer from the English page, instead of a Tamil answer with ₹1,000.
- It is safe even before anyone checks the PDFs, because removing a sentence never adds a wrong
  number.

### C. A paired-document check (finds new problems; fixes nothing)

A report-only script. For each Tamil or Hindi document that has an English counterpart, it
lists the amounts that appear in one and not the other. This would help find the hostel and
helpline pages, and any errors we don't know about yet.

- About 2 hours.
- Expect noise, because the documents are not line-by-line translations, so a person reads the
  list. It does not change answers.

## Recommendation

1. **Now:** B for the first three rows. It is safe without a PDF check and needs no re-index.
2. **Once a person has checked p33, p11 and APY p1:** A for those rows, with the "corrected by
   hand" note on the source line. Then remove them from B's list.
3. **C only if there's time after the video.** The three demo rows matter most.

All of these fit in the 8 days. A and B together are about 4 hours plus your re-index.

## What I need from you

- Pick one: B now, A after the check, or both (my suggestion).
- Who checks p33, p11 and APY p1 by eye, and which name goes in `checked_by`.
- Whether the source line should say "corrected by hand" (I suggest yes).
