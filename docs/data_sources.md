# Data sources

Every document in the corpus is a **public** document from an official government site. Raw files are
not committed (see `.gitignore`); this list is the record needed to re-download them.

**Status:** candidate list. The portals below are the official scheme sites, but the exact document
URL, language versions and access date must be filled in when each file is downloaded into
`data/raw/`. Don't mark a row `downloaded` until the file is saved and opens correctly.

Selection rules:

- 15–20 documents, a mix of Tamil Nadu and central schemes.
- Where possible, get the **same scheme in two languages** (e.g. Tamil + English G.O. or Hindi +
  English guidelines). This is what makes cross-lingual retrieval testable.
- Prefer text PDFs. Note scanned or legacy-font PDFs in the `notes` column; they need OCR.
- Record the document's own date (G.O. date / version) as well as the access date.

## Adding a downloaded document

The tables below are for research. The ingestion pipeline reads `data/sources.json`, which
lists only documents that are actually saved in `data/raw/`. Add one entry per file:

```json
{
  "doc_id": "kmut-guidelines-ta",
  "scheme": "Kalaignar Magalir Urimai Thogai",
  "file": "kmut-guidelines-ta.pdf",
  "source_url": "https://kmut.tn.gov.in/...",
  "language": "ta",
  "doc_date": "2023-07-01",
  "accessed": "2026-10-26",
  "force_ocr": false
}
```

- `doc_id`: lower-case words joined by hyphens; end with the language code.
- `language`: `ta`, `hi` or `en`. Each language version of a scheme is its own entry.
- `force_ocr`: set to `true` if `ingest_report.json` shows a legacy-font PDF slipped past
  the automatic check (its chunks look like `jkpo;ehL`).

Then run `uv run python -m schemebot.ingest` and check `data/processed/ingest_report.json`.

## Tamil Nadu schemes

| # | Scheme | Portal | Document URL | Lang | Doc date | Accessed | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | Kalaignar Magalir Urimai Thogai | https://tncdw.org/pages/go | [G.O.(Ms) No.15](https://tncdw.org/frontend/gos/Mahalir_Urimai_Thittam-GO.pdf) | en (pp 1-7), ta (pp 8-43) | 2023-07-10 | 2026-10-25 | downloaded | Tamil annexure uses legacy TAU-Marutham font, so it is OCR'd. kmut.tn.gov.in had an expired TLS certificate. |
| 2 | Pudhumai Penn | https://pudhumaipenn.tn.gov.in | TODO | ta, en | TODO | TODO | candidate | |
| 3 | Chief Minister's Comprehensive Health Insurance Scheme | https://www.cmchistn.com | TODO | ta, en | TODO | TODO | candidate | |
| 4 | Naan Mudhalvan | https://www.naanmudhalvan.tn.gov.in | TODO | ta, en | TODO | TODO | candidate | |
| 5 | Tamil Pudhalvan | TODO (find official G.O.) | TODO | ta, en | TODO | TODO | candidate | |
| 6 | Chief Minister's Breakfast Scheme | https://tncdw.org/pages/go | [G.O.(Ms) No.43](https://tncdw.org/frontend/gos/Breakfast_GO.43_(1).pdf) | ta | 2022-07-27 | 2026-10-25 | downloaded | Scanned, fully OCR'd. |
| 6b | Social Welfare & Women Empowerment Dept. policy note 2024-25 (covers Pudhumai Penn, the Breakfast Scheme and other department schemes; not KMUT, which sits under Special Programme Implementation) | https://cms.tn.gov.in | [English](https://cms.tn.gov.in/cms_migrated/document/docfiles/swwe_e_pn_2024_25.pdf), [Tamil](https://cms.tn.gov.in/cms_migrated/document/docfiles/swwe_t_pn_2024_25.pdf) | en, ta | 2024 | 2026-10-25 | downloaded | **Language pair.** Tamil version has no usable text layer and is OCR'd. Other departments follow the same `_e_` / `_t_` file naming. |
| 7 | TN e-Sevai service list | https://www.tnesevai.tn.gov.in | TODO | ta, en | TODO | TODO | candidate | where-to-apply info |

### Tamil Nadu department policy notes 2024-25 (English + Tamil pairs)

All from `https://cms.tn.gov.in/cms_migrated/document/docfiles/`, accessed 2026-10-25. The
Tamil versions have no usable text layer and are fully OCR'd.

| Department | English | Tamil | Covers (for example) |
|---|---|---|---|
| Health and Family Welfare | `hfw_e_pn_2024_25.pdf` (649 pp) | `hfw_t_pn_2024_25.pdf` (568 pp) | CM's Comprehensive Health Insurance Scheme |
| Higher Education | `hedu_e_pn_2024_25.pdf` (189 pp) | `hedu_t_pn_2024_25.pdf` (122 pp) | scholarships, Tamil Pudhalvan |
| Adi Dravidar and Tribal Welfare | `adtw_e_pn_2024_25.pdf` (154 pp) | `adtw_t_pn_2024_25.pdf` (172 pp) | scholarships, hostels |
| BC, MBC and Minorities Welfare | `bcmbc_e_pn_2024_25.pdf` (87 pp) | `bcmbc_t_pn_2024_25.pdf` (107 pp) | scholarships, free bicycles |

## Central schemes

| # | Scheme | Portal | Document URL | Lang | Doc date | Accessed | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| 8 | PM-KISAN | https://pmkisan.gov.in | [Operational Guidelines (revised)](https://pmkisan.gov.in/Documents/RevisedPM-KISANOperationalGuidelines(English).pdf) | en | 2020-03-29 | 2026-10-25 | downloaded | |
| 8b | PM-KISAN e-KYC | https://pmkisan.gov.in | [Hindi](https://pmkisan.gov.in/Documents/Note-on-Modes-and-processes-of-ekyc-13th-Nov-Hindi.pdf), [English](https://pmkisan.gov.in/Documents/Note-on-Modes-and-processes-of-ekyc-13th-Nov-English.pdf) | hi, en | 2023-11-13 | 2026-10-25 | downloaded | **Language pair.** Hindi text layer has a broken Devanagari font map, so it is OCR'd. |
| 9 | Ayushman Bharat PM-JAY | https://pmjay.gov.in | TODO | en, hi | TODO | TODO | candidate | |
| 10 | PM Awas Yojana (Gramin / Urban) | https://pmayg.nic.in, https://pmay-urban.gov.in | TODO | en, hi | TODO | TODO | candidate | |
| 11 | PM Ujjwala Yojana | https://mopng.gov.in/hi/marketing/lpg | [SOP for 75 lakh connections](https://mopng.gov.in/files/marketing/lpg/75L-PMUY-SoP-10102023-(1).pdf) | en | 2023-10-10 | 2026-10-25 | downloaded | Eligibility categories and required documents. No Hindi version found on the ministry site. |
| 12 | PM Jan Dhan Yojana | https://pmjdy.gov.in | TODO | en, hi | TODO | TODO | candidate | |
| 13 | Atal Pension Yojana | https://www.pfrda.org.in | [English](https://www.pfrda.org.in/documents/33652/307349/APY%20Subscriber%20Information%20Brochure%20English), [Hindi](https://www.pfrda.org.in/documents/33652/307086/APY%20Subscriber%20Information%20Brochure%20(Hindi)) | en, hi | undated | 2026-10-25 | downloaded | **Language pair.** Subscriber information brochure. Hindi text layer has wrong letters ("प्रतिमाह" extracts as "प्रततमाह"); the vowel-sign check detects it and sends both pages to OCR. |
| 14 | Sukanya Samriddhi Yojana | TODO (India Post / DEA notification) | TODO | en, hi | TODO | TODO | candidate | |
| 15 | PM Vishwakarma | https://pmvishwakarma.gov.in | TODO | en, hi | TODO | TODO | candidate | |
| 16 | National Scholarship Portal schemes | https://scholarships.gov.in | TODO | en, hi | TODO | TODO | candidate | |

## Cross-scheme reference

| # | Source | Portal | Document URL | Lang | Accessed | Status | Notes |
|---|---|---|---|---|---|---|---|
| 17 | myScheme scheme pages | https://www.myscheme.gov.in | TODO | en, hi | TODO | candidate | check terms of use before scraping |

## Helplines

Refusal messages point users to the official helpline or office. These have to come from the
source documents, not from memory.

| Scheme | Helpline / office | Source (doc + page) |
|---|---|---|
| TODO | TODO | TODO |
