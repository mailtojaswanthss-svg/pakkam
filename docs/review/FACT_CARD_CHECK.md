# Fact card check against the official PDFs (1 Nov 2026)

Each card was compared with the page it cites in the official PDF, downloaded from the
URL in `data/sources.json`. Tamil government orders were read as page images, because their
text layer uses a legacy font that does not extract.

**This check does not replace the human sign-off.** A card is only served once a person
signs it with `scripts/sign_fact_cards.py --by "Name" <ids>`. This report records what was
checked, so signing is a quick confirmation.

## Result

| Card(s) | Cited page | Finding | Action |
|---|---|---|---|
| `apy_pension_en/ta` | APY brochure p.1 | Matches: "minimum monthly pension … of Rs. 1000, Rs 2000, Rs 3000, Rs 4000, Rs. 5000 per month after 60 years of age" | None. Ready to sign |
| `apy_age_en/ta` | APY brochure p.1 | Matches: "between 18 and 40 years of age"; "From 1st October, 2022, any citizen who is or has been an income-tax payer … shall not be eligible" | None. Ready to sign |
| `kmut_income_en/ta` | KMUT G.O. 15 p.10 | Matches: "ஆண்டு வருமானம் ரூ.2.5 இலட்சத்திற்குக் கீழ்" (section 2.1.3 i) | None. Ready to sign |
| `kmut_amount_en/ta` | p.9 → **p.3** | p.9 states only "ஆண்டுக்கு 12 ஆயிரம் ரூபாய்" (Rs.12,000 a year); the card said Rs.1,000 a month, a conversion the page does not make. p.3 states both: "one thousand rupees per month" and "Rs.12,000/- per annum" | **Fixed:** page → 3, text now gives both amounts |
| `breakfast_classes_en/ta` | p.14 → **p.1** | p.14 is only a table of school and beneficiary counts. p.1 states breakfast for "அரசுத் தொடக்கப் பள்ளிகளில் 1 முதல் 5-ஆம் வகுப்பு வரை பயிலும் மாணவ, மாணவியருக்கு" | **Fixed:** page → 1 |
| `ujjwala_docs_en/ta` | p.1 → **p.2** | p.1 is a blank cover; the list is on p.2. The card **left out** "Proof of Identity (PoI)" and "Proof of Address (PoA)" | **Fixed:** page → 2, both documents added |
| `kmut_exclusions_en/ta` (new) | KMUT G.O. 15 p.11 | Written from the page: the eight exclusions in section 2.2.1, including "மாநில, ஒன்றிய அரசு ஊழியர்கள்" (State and Union government employees) | New card; added because the live benchmark showed "central government employee" questions being refused |
| `ujjwala_eligibility_en/ta` (new) | PMUY SoP p.2 | Written from the page: "Adult woman belonging to any of the following categories" and the 10 categories | New card; the Hindi eligibility question was refused |
| `pmkisan_amount_en/ta`, `pmkisan_ekyc_en/ta` | PM-KISAN e-KYC note p.1 | **Not checked here:** pmkisan.gov.in serves an incomplete certificate chain, so the PDF could not be downloaded safely | Check on the laptop (`data/raw/`) |
| `pudhumai_amount_en/ta` | Social Welfare policy note 2024-25 p.18 | **Not checked here:** cms.tn.gov.in reset the connection | Check on the laptop (`data/raw/`) |

**Summary:** 12 of the first 18 cards were checked. 6 of those were already right, and 6 had a wrong
page and/or missing detail, now fixed. The remaining 6 need a look on the laptop.

## Why this matters

A card cited to the wrong page fails the "every claim is on the cited page" promise, even
when its fact is right: a judge who opens the citation would not find the claim. Before
this check, 6 of the 12 cards examined had that problem, and the Ujjwala card would have
sent people to the gas agency without two required documents.

## Signing (laptop)

```powershell
uv run python scripts/sign_fact_cards.py --list
uv run python scripts/sign_fact_cards.py --by "YourName" apy_pension_en apy_pension_ta apy_age_en apy_age_ta kmut_income_en kmut_income_ta kmut_amount_en kmut_amount_ta breakfast_classes_en breakfast_classes_ta ujjwala_docs_en ujjwala_docs_ta kmut_exclusions_en kmut_exclusions_ta ujjwala_eligibility_en ujjwala_eligibility_ta
```

For the last 6, open the PDFs in `data/raw/` at the cited page, confirm the text, then sign:

```powershell
uv run python scripts/sign_fact_cards.py --by "YourName" pmkisan_amount_en pmkisan_amount_ta pmkisan_ekyc_en pmkisan_ekyc_ta pudhumai_amount_en pudhumai_amount_ta
```
