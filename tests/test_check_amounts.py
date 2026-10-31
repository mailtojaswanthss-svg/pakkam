"""The amount checker (scripts/check_amounts.py) finds misread amounts without any network."""

from scripts.check_amounts import amounts_in, common_sense_flags, find_suspects, pair_of


def test_reads_tamil_lakh_amounts() -> None:
    [(_, value, _)] = amounts_in("ஆண்டு வருமானம் ரூ.2.5 இலட்சத்திற்குக் கீழ்")
    assert value == 250_000


def test_flags_the_25_lakh_income_misread() -> None:
    [(_, value, context)] = amounts_in("ஆண்டு வருமானம் ரூ.25 இலட்சத்திற்குக் கீழ்")
    assert value == 2_500_000
    assert common_sense_flags(value, context) == ["income limit above Rs.1,000,000"]


def test_normal_amounts_are_not_flagged() -> None:
    [(_, value, context)] = amounts_in("Rs.1,000 per month to each girl student")
    assert common_sense_flags(value, context) == []


def test_tamil_amount_missing_from_the_english_version_is_flagged() -> None:
    chunks = [
        {"doc_id": "x-ta", "page_start": 3, "text": "மாதம் ரூ.4,000 உதவித்தொகை", "extraction": "ocr"},
        {
            "doc_id": "x-en",
            "page_start": 3,
            "text": "Rs.1,000 per month assistance",
            "extraction": "text",
        },
    ]
    [row] = find_suspects(chunks)
    assert row["rupees"] == 4000 and "not found in x-en" in str(row["reasons"])
    assert pair_of("x-en") == "x-ta"
