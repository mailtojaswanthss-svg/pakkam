import csv
from pathlib import Path

GATE_PAGES = [
    # data/corrections.json
    {"document": "tn-hedu-policy-note-2024-ta", "page": 33, "notes": "Pudhumai Penn monthly amount (corrections.json: OCR read 4,000 vs 1,000)"},
    {"document": "tn-swwe-policy-note-2024-ta", "page": 11, "notes": "Pudhumai Penn monthly amount (corrections.json: OCR read 7000 vs 1000)"},
    {"document": "tn-hfw-policy-note-2024-ta", "page": 421, "notes": "Insurance family income limit (corrections.json: OCR read 4,20,000 vs 1,20,000)"},
    {"document": "apy-brochure-hi", "page": 1, "notes": "APY minimum pension (corrections.json: OCR read 000 vs 1000)"},
    {"document": "tn-swwe-policy-note-2024-ta", "page": 88, "notes": "Senior helpline (corrections.json: OCR read Tamil digit 14௧67 vs 14567)"},
    {"document": "tn-bcmbc-policy-note-2024-ta", "page": 59, "notes": "Hostel food charge per month (corrections.json: OCR read 4400 vs 1400)"},
    {"document": "tn-adtw-policy-note-2024-ta", "page": 53, "notes": "Hostel food subsidy (corrections.json: OCR read 44007- vs 1400/-)"},

    # docs/review/demo-numbers.csv & key demo numbers
    {"document": "kmut-go15-2023-ta", "page": 3, "notes": "KMUT G.O.: eligibility age cutoff 21, Rs.12,000 per annum"},
    {"document": "kmut-go15-2023-ta", "page": 4, "notes": "KMUT G.O.: annual family income below Rs. 2.5 lakh"},
    {"document": "kmut-go15-2023-ta", "page": 9, "notes": "KMUT G.O. Tamil: 21 வயது, ஆண்டுக்கு 12 ஆயிரம் ரூபாய்"},
    {"document": "kmut-go15-2023-ta", "page": 10, "notes": "KMUT G.O. Tamil: ஆண்டு வருமானம் ரூ.2.5 இலட்சம்"},
    {"document": "kmut-go15-2023-ta", "page": 11, "notes": "KMUT G.O. Tamil: வருமான விலக்கு ரூ.2.5 இலட்சத்திற்கு மேல்"},
    {"document": "pmkisan-ekyc-note-2023-hi", "page": 1, "notes": "PM-KISAN Hindi: प्रति वर्ष 6,000 रुपये"},
    {"document": "apy-brochure-hi", "page": 2, "notes": "APY Hindi: contribution amounts / pension slabs"},
    {"document": "tn-swwe-policy-note-2024-ta", "page": 10, "notes": "SWWE Tamil: Pudhumai Penn scheme coverage"},
    {"document": "tn-swwe-policy-note-2024-ta", "page": 21, "notes": "SWWE Tamil: Moovalur Ramamirtham marriage assistance amounts"},
    {"document": "tn-swwe-policy-note-2024-ta", "page": 22, "notes": "SWWE Tamil: Dr. Dharmambal marriage assistance amounts"},
    {"document": "tn-hedu-policy-note-2024-ta", "page": 5, "notes": "HEDU Tamil: Higher education budget outlay"},
    {"document": "tn-hedu-policy-note-2024-ta", "page": 6, "notes": "HEDU Tamil: Pudhumai Penn scheme fund allocation"},
    {"document": "tn-hedu-policy-note-2024-ta", "page": 20, "notes": "HEDU Tamil: Annamalai University grant"},
    {"document": "cmbfs-go43-2022-ta", "page": 1, "notes": "CM Breakfast scheme: G.O. number 43 and date"},
    {"document": "cmbfs-go43-2022-ta", "page": 2, "notes": "CM Breakfast scheme: Rs. 33.56 crore sanction amount"}
]

def main():
    out_path = Path("docs/review/ocr_gate_pages.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["document", "page", "known_number", "notes"])
        for item in GATE_PAGES:
            writer.writerow([item["document"], item["page"], "", item["notes"]])
    print(f"Wrote {len(GATE_PAGES)} rows to {out_path}")

if __name__ == "__main__":
    main()
