"""Money amounts written out as words, so text to speech reads them correctly.

Gnani's TTS docs ask for numbers, dates and currency to be spelled out. This module only
touches money: a number with a currency mark (Rs., ₹, ரூ., रु.), a lakh/crore unit, or a
rupee word after it. Ages, years and helpline numbers are left alone.

Rules that keep amounts safe:
- Deterministic tables, no LLM.
- Indian grouping (thousand, lakh, crore), the way the documents write amounts.
- Decimals are read digit by digit ("2.5 lakh" -> "two point five lakh"), never rounded.
- Every conversion is parsed back to a number and compared with the original. If they
  differ, or the number is written in an unusual way (e.g. "1,0000"), the text is kept.

The Tamil and Hindi wording needs a native speaker's review before the demo.
"""

import re
from decimal import Decimal

# ---------- number words ----------

EN_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
           "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
           "seventeen", "eighteen", "nineteen"]  # fmt: skip
EN_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

TA_ONES = ["பூஜ்ஜியம்", "ஒன்று", "இரண்டு", "மூன்று", "நான்கு", "ஐந்து", "ஆறு", "ஏழு",
           "எட்டு", "ஒன்பது", "பத்து", "பதினொன்று", "பன்னிரண்டு", "பதின்மூன்று",
           "பதினான்கு", "பதினைந்து", "பதினாறு", "பதினேழு", "பதினெட்டு", "பத்தொன்பது"]  # fmt: skip
TA_TENS = ["", "", "இருபது", "முப்பது", "நாற்பது", "ஐம்பது", "அறுபது", "எழுபது", "எண்பது",
           "தொண்ணூறு"]  # fmt: skip
# The form a ten takes when a unit follows: இருபது -> இருபத்து ஒன்று.
TA_TENS_JOIN = ["", "", "இருபத்து", "முப்பத்து", "நாற்பத்து", "ஐம்பத்து", "அறுபத்து",
                "எழுபத்து", "எண்பத்து", "தொண்ணூற்று"]  # fmt: skip
TA_HUNDREDS = ["", "நூறு", "இருநூறு", "முன்னூறு", "நானூறு", "ஐநூறு", "அறுநூறு", "எழுநூறு",
               "எண்ணூறு", "தொள்ளாயிரம்"]  # fmt: skip
TA_HUNDREDS_JOIN = ["", "நூற்று", "இருநூற்று", "முன்னூற்று", "நானூற்று", "ஐநூற்று",
                    "அறுநூற்று", "எழுநூற்று", "எண்ணூற்று", "தொள்ளாயிரத்து"]  # fmt: skip

# Hindi numbers below 100 are irregular, so all 100 are listed (index = value).
HI_UNDER_100 = [
    "शून्य", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ",
    "दस", "ग्यारह", "बारह", "तेरह", "चौदह", "पंद्रह", "सोलह", "सत्रह", "अठारह", "उन्नीस",
    "बीस", "इक्कीस", "बाईस", "तेईस", "चौबीस", "पच्चीस", "छब्बीस", "सत्ताईस", "अट्ठाईस", "उनतीस",
    "तीस", "इकतीस", "बत्तीस", "तैंतीस", "चौंतीस", "पैंतीस", "छत्तीस", "सैंतीस", "अड़तीस", "उनतालीस",
    "चालीस", "इकतालीस", "बयालीस", "तैंतालीस", "चौवालीस",
    "पैंतालीस", "छियालीस", "सैंतालीस", "अड़तालीस", "उनचास",
    "पचास", "इक्यावन", "बावन", "तिरपन", "चौवन", "पचपन", "छप्पन", "सत्तावन", "अट्ठावन", "उनसठ",
    "साठ", "इकसठ", "बासठ", "तिरसठ", "चौंसठ", "पैंसठ", "छियासठ", "सड़सठ", "अड़सठ", "उनहत्तर",
    "सत्तर", "इकहत्तर", "बहत्तर", "तिहत्तर", "चौहत्तर", "पचहत्तर", "छिहत्तर", "सतहत्तर", "अठहत्तर", "उन्यासी",
    "अस्सी", "इक्यासी", "बयासी", "तिरासी", "चौरासी", "पचासी", "छियासी", "सत्तासी", "अट्ठासी", "नवासी",
    "नब्बे", "इक्यानवे", "बानवे", "तिरानवे", "चौरानवे", "पंचानवे", "छियानवे", "सत्तानवे", "अट्ठानवे", "निन्यानवे",
]  # fmt: skip

# Scale words: (value, English, Tamil alone, Tamil when more follows, Hindi).
SCALES = [
    (10_000_000, "crore", "கோடி", "கோடியே", "करोड़"),
    (100_000, "lakh", "லட்சம்", "லட்சத்து", "लाख"),
    (1_000, "thousand", "ஆயிரம்", "ஆயிரத்து", "हज़ार"),
]
POINT = {"en": "point", "ta": "புள்ளி", "hi": "दशमलव"}
RUPEES = {"en": ("rupee", "rupees"), "ta": ("ரூபாய்", "ரூபாய்"), "hi": ("रुपया", "रुपये")}


def _en_under_1000(n: int) -> str:
    hundreds, rest = divmod(n, 100)
    words = [f"{EN_ONES[hundreds]} hundred"] if hundreds else []
    if rest >= 20:
        words.append(EN_TENS[rest // 10] + (f"-{EN_ONES[rest % 10]}" if rest % 10 else ""))
    elif rest or not words:
        words.append(EN_ONES[rest])
    return " ".join(words)


def _ta_under_100(n: int) -> str:
    if n < 20:
        return TA_ONES[n]
    tens, ones = divmod(n, 10)
    return f"{TA_TENS_JOIN[tens]} {TA_ONES[ones]}" if ones else TA_TENS[tens]


def _ta_under_1000(n: int) -> str:
    hundreds, rest = divmod(n, 100)
    if not hundreds:
        return _ta_under_100(rest)
    if not rest:
        return TA_HUNDREDS[hundreds]
    return f"{TA_HUNDREDS_JOIN[hundreds]} {_ta_under_100(rest)}"


def _hi_under_1000(n: int) -> str:
    hundreds, rest = divmod(n, 100)
    words = [f"{HI_UNDER_100[hundreds]} सौ"] if hundreds else []
    if rest or not words:
        words.append(HI_UNDER_100[rest])
    return " ".join(words)


def number_to_words(n: int, language: str) -> str:
    """Whole number in words, Indian grouping. language: "en", "ta" or "hi"."""
    if n < 0:
        raise ValueError("negative amounts are not spelled out")
    if n == 0:
        return {"en": EN_ONES[0], "ta": TA_ONES[0], "hi": HI_UNDER_100[0]}[language]
    parts = []
    rest = n
    for value, en, ta, ta_join, hi in SCALES:
        count, rest = divmod(rest, value)
        if not count:
            continue
        # Crores can exceed 99 (e.g. 150 crore), so the count is itself spelled out.
        if language == "en":
            parts.append(f"{number_to_words(count, 'en')} {en}")
        elif language == "hi":
            parts.append(f"{number_to_words(count, 'hi')} {hi}")
        else:
            scale = ta_join if rest else ta
            if count == 1:
                # "ஆயிரம்" on its own; "ஒரு லட்சம்", "ஒரு கோடி".
                parts.append(scale if value == 1_000 else f"ஒரு {scale}")
            else:
                parts.append(f"{number_to_words(count, 'ta')} {scale}")
    if rest:
        if language == "en":
            parts.append(_en_under_1000(rest))
        elif language == "hi":
            parts.append(_hi_under_1000(rest))
        else:
            parts.append(_ta_under_1000(rest))
    return " ".join(parts)


# ---------- words back to a number (the safety check) ----------


def _word_values() -> dict[str, tuple[int, bool]]:
    """word -> (value, is_scale). Built from the same tables, per language merged."""
    values: dict[str, tuple[int, bool]] = {}
    for n, word in enumerate(EN_ONES):
        values[word] = (n, False)
    for n, word in enumerate(HI_UNDER_100):
        values[word] = (n, False)
    for n, word in enumerate(TA_ONES):
        values[word] = (n, False)
    for tens in range(2, 10):
        values[EN_TENS[tens]] = (tens * 10, False)
        values[TA_TENS[tens]] = (tens * 10, False)
        values[TA_TENS_JOIN[tens]] = (tens * 10, False)
    for hundreds in range(1, 10):
        values[TA_HUNDREDS[hundreds]] = (hundreds * 100, False)
        values[TA_HUNDREDS_JOIN[hundreds]] = (hundreds * 100, False)
    values["ஒரு"] = (1, False)
    for value, en, ta, ta_join, hi in SCALES:
        for word in (en, ta, ta_join, hi):
            values[word] = (value, True)
    values["hundred"] = values["सौ"] = (100, True)
    return values


_VALUES = _word_values()


def words_to_number(text: str) -> int | None:
    """Inverse of number_to_words for its own output; None if a word is unknown."""
    total = current = 0
    largest_scale = 0
    for word in text.replace("-", " ").split():
        if word not in _VALUES:
            return None
        value, is_scale = _VALUES[word]
        if not is_scale:
            current += value
        elif value == 100:
            current = (current or 1) * 100
        elif total and value > largest_scale:
            # "five thousand two hundred crore": the crore multiplies everything before it.
            total = (total + current) * value
            current, largest_scale = 0, value
        else:
            total += (current or 1) * value
            current, largest_scale = 0, max(largest_scale, value)
    return total + current


# ---------- finding amounts in text ----------

# "ரூபாய் 1,000" and "रुपये 500" also occur, with the rupee word in front.
_CURRENCY = r"(?:Rs\.?|INR|₹|ரூபாய்|ரூ\.?|रुपये|रु\.?|रू\.?)"
_NUMBER = r"\d{1,3}(?:,\d{2,3})+(?!\d)|\d+"
_UNITS = {"lakh": 100_000, "lakhs": 100_000, "crore": 10_000_000, "crores": 10_000_000,
          "லட்சம்": 100_000, "கோடி": 10_000_000, "लाख": 100_000, "करोड़": 10_000_000}  # fmt: skip
_RUPEE_WORDS = r"(?:rupees|rupee|ரூபாய்|रुपये|रुपए|रुपया)"
_UNIT_WORDS = "|".join(sorted(map(re.escape, _UNITS), key=len, reverse=True))
# Letters and Indic combining marks: a unit or rupee word must not run on into a longer word.
_WORD_CHAR = r"[\w஀-௿ऀ-ॿ]"

AMOUNT = re.compile(
    rf"(?<![\w.,])(?P<currency>{_CURRENCY})?\s?(?P<number>(?:{_NUMBER})(?:\.\d+)?)(?![\d.,]\d|\d)"
    rf"(?:\s?(?P<unit>{_UNIT_WORDS})(?!{_WORD_CHAR}))?"
    rf"(?:\s?(?P<rupees>{_RUPEE_WORDS})(?!{_WORD_CHAR}))?"
    r"(?P<dash>/-)?",  # "Rs.1000/-": the "/-" is dropped so it is not read aloud
    re.IGNORECASE,
)


def _valid_grouping(number: str) -> bool:
    """1,000 / 1,20,000 (Indian) / 120,000 (Western) are fine; 1,0000 or 12,00 are not."""
    groups = number.split(",")
    if len(groups) == 1:
        return True
    if len(groups[-1]) != 3:
        return False
    middle = groups[1:-1]
    return all(len(g) == 2 for g in middle) or all(len(g) == 3 for g in middle)


def _spell_number(number: str, language: str) -> str | None:
    whole, _, fraction = number.replace(",", "").partition(".")
    words = number_to_words(int(whole), language)
    if words_to_number(words) != int(whole):
        return None
    if fraction:
        digits = " ".join(number_to_words(int(d), language) for d in fraction)
        words += f" {POINT[language]} {digits}"
    return words


def _spell_match(match: re.Match[str], language: str) -> str:
    original = match.group(0)
    number, unit = match.group("number"), match.group("unit")
    is_money = match.group("currency") or unit or match.group("rupees")
    if not is_money or not _valid_grouping(number.split(".")[0]):
        return original
    if "." in number and not unit:
        return original  # rupees and paise: leave as written
    spoken = _spell_number(number, language)
    if spoken is None:
        return original
    if unit:
        scale = _UNITS[unit.lower()]
        spoken += " " + next(
            {"en": en, "ta": ta, "hi": hi}[language] for v, en, ta, _, hi in SCALES if v == scale
        )
    if match.group("currency") or match.group("rupees"):
        one = Decimal(number.replace(",", "")) == 1 and not unit
        if one and language == "ta":
            spoken = "ஒரு"  # "ஒரு ரூபாய்", not "ஒன்று ரூபாய்"
        spoken += " " + RUPEES[language][0 if one else 1]
    return spoken


def amount_shape(amount: str) -> str:
    """ "Rs.1,20,000/-" -> "Rs.9,99,999/-": groups amounts by how they are written."""
    return re.sub(r"\d", "9", amount)


def find_amounts(text: str) -> list[str]:
    """Every money amount in `text`, as written (for checking the corpus)."""
    return [
        m.group(0)
        for m in AMOUNT.finditer(text)
        if m.group("currency") or m.group("unit") or m.group("rupees")
    ]


def spell_amounts(text: str, language_code: str) -> str:
    """Money amounts in `text` as words in the voice's language (ta-IN, hi-IN, en-IN)."""
    language = {"ta-IN": "ta", "hi-IN": "hi"}.get(language_code, "en")
    return AMOUNT.sub(lambda match: _spell_match(match, language), text)


_PHONE = re.compile(r"(?<![\d.,₹/])(\d[\d -]{3,}\d)(?![\d,.]?\d)")
_MONEY_BEFORE = re.compile(r"(rs\.?|₹|ரூ\.?|रु\.?|inr)\s*$", re.IGNORECASE)


def phone_numbers_as_digits(text: str) -> str:
    """Helplines are read one digit at a time ("1800 425 3993" -> "1 8 0 0, 4 2 5, 3 9 9 3"),
    as people dial them. Only runs of 5 or more digits that are not money (no Rs/₹ before
    them) are changed; years and amounts are left alone."""

    def spell(match: re.Match[str]) -> str:
        number = match.group(1)
        digits = re.sub(r"\D", "", number)
        if len(digits) < 5 or _MONEY_BEFORE.search(text[: match.start()]):
            return number
        groups = [g for g in re.split(r"[ -]+", number.strip()) if g]
        return ", ".join(" ".join(group) for group in groups)

    return _PHONE.sub(spell, text)
