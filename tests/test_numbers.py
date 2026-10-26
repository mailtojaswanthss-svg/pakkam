import json
import random
import re

import pytest

from schemebot.config import get_settings
from schemebot.voice.numbers import (
    HI_UNDER_100,
    RUPEES,
    amount_shape,
    find_amounts,
    number_to_words,
    spell_amounts,
    words_to_number,
)


@pytest.mark.parametrize(
    ("n", "en", "ta", "hi"),
    [
        (0, "zero", "பூஜ்ஜியம்", "शून्य"),
        (1, "one", "ஒன்று", "एक"),
        (21, "twenty-one", "இருபத்து ஒன்று", "इक्कीस"),
        (100, "one hundred", "நூறு", "एक सौ"),
        (1000, "one thousand", "ஆயிரம்", "एक हज़ार"),
        (1500, "one thousand five hundred", "ஆயிரத்து ஐநூறு", "एक हज़ार पाँच सौ"),
        (6000, "six thousand", "ஆறு ஆயிரம்", "छह हज़ार"),
        (12000, "twelve thousand", "பன்னிரண்டு ஆயிரம்", "बारह हज़ार"),
        (72000, "seventy-two thousand", "எழுபத்து இரண்டு ஆயிரம்", "बहत्तर हज़ार"),
        (100000, "one lakh", "ஒரு லட்சம்", "एक लाख"),
        (120000, "one lakh twenty thousand", "ஒரு லட்சத்து இருபது ஆயிரம்", "एक लाख बीस हज़ार"),
        (250000, "two lakh fifty thousand", "இரண்டு லட்சத்து ஐம்பது ஆயிரம்", "दो लाख पचास हज़ार"),
        (10000000, "one crore", "ஒரு கோடி", "एक करोड़"),
    ],
)
def test_known_values(n: int, en: str, ta: str, hi: str) -> None:
    assert number_to_words(n, "en") == en
    assert number_to_words(n, "ta") == ta
    assert number_to_words(n, "hi") == hi


def test_hindi_table_has_every_number_below_100() -> None:
    assert len(HI_UNDER_100) == len(set(HI_UNDER_100)) == 100
    assert (HI_UNDER_100[19], HI_UNDER_100[49], HI_UNDER_100[67], HI_UNDER_100[99]) == (
        "उन्नीस",
        "उनचास",
        "सड़सठ",
        "निन्यानवे",
    )


@pytest.mark.parametrize("language", ["en", "ta", "hi"])
def test_words_always_read_back_as_the_same_number(language: str) -> None:
    rng = random.Random(7)
    numbers = [*range(0, 3000), *(rng.randrange(0, 10**11) for _ in range(5000))]
    for n in numbers:
        assert words_to_number(number_to_words(n, language)) == n


@pytest.mark.parametrize(
    ("text", "code", "spoken"),
    [
        ("PM-KISAN pays Rs.6000 a year.", "en-IN", "PM-KISAN pays six thousand rupees a year."),
        ("ரூ.1,000 உதவித்தொகை", "ta-IN", "ஆயிரம் ரூபாய் உதவித்தொகை"),
        ("ரூ.1000/- வழங்கப்படும்", "ta-IN", "ஆயிரம் ரூபாய் வழங்கப்படும்"),
        ("ரூபாய் 1,000 உதவி", "ta-IN", "ஆயிரம் ரூபாய் உதவி"),
        ("₹12,000 मिलेंगे", "hi-IN", "बारह हज़ार रुपये मिलेंगे"),
        ("6,000 रुपये", "hi-IN", "छह हज़ार रुपये"),
        ("Rs. 1,20,000", "en-IN", "one lakh twenty thousand rupees"),
        ("Rs.2.5 lakh", "ta-IN", "இரண்டு புள்ளி ஐந்து லட்சம் ரூபாய்"),
        ("Rs.3.50 lakh", "en-IN", "three point five zero lakh rupees"),
        ("2.5 லட்சம் வருமானம்", "ta-IN", "இரண்டு புள்ளி ஐந்து லட்சம் வருமானம்"),
        ("Rs.18,000, then", "en-IN", "eighteen thousand rupees, then"),
        ("Rs.1 only", "ta-IN", "ஒரு ரூபாய் only"),
        ("Rs.1 only", "hi-IN", "एक रुपया only"),
    ],
)
def test_money_is_spoken_in_the_voice_language(text: str, code: str, spoken: str) -> None:
    assert spell_amounts(text, code) == spoken


@pytest.mark.parametrize(
    "text",
    [
        "Women aged 21 to 60 born before 2002 can apply.",  # ages and years
        "Call 1098 or 181, or 14567.",  # helplines
        "Rs.1,0000 is a typo",  # unusual grouping: never guess
        "Rs.12,00 is a typo",
        "Rs.14.50 per kg",  # rupees and paise
        "A 14.2 kg cylinder",
        "G.O.(Ms) No.15 dated 23.01.2023",
    ],
)
def test_anything_unclear_is_left_as_written(text: str) -> None:
    for code in ("ta-IN", "hi-IN", "en-IN"):
        assert spell_amounts(text, code) == text


def amounts_in_eval_references() -> list[str]:
    path = get_settings().eval_questions_path
    lines = path.read_text(encoding="utf-8").splitlines()
    return [
        a for line in lines if line.strip() for a in find_amounts(json.loads(line)["reference"])
    ]


def test_every_amount_format_in_the_eval_set_keeps_its_value() -> None:
    amounts = amounts_in_eval_references()
    assert len({amount_shape(a) for a in amounts}) >= 5

    for amount in amounts:
        value = re.sub(r"[^\d.]", "", amount.split(" ")[0].replace("Rs.", ""))
        for code, language in (("en-IN", "en"), ("ta-IN", "ta"), ("hi-IN", "hi")):
            spoken = spell_amounts(amount, code)
            assert spoken != amount, amount
            whole = spoken.split(" point ")[0] if language == "en" else spoken
            if "." not in value:
                expected = int(value) * (100_000 if "lakh" in amount else 1)
                number_words = whole.removesuffix(" " + RUPEES[language][1])
                assert words_to_number(number_words) == expected, (amount, spoken)
