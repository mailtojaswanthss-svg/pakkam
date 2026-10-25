"""Language identification for the four language groups the project supports.

Tamil and Hindi have their own Unicode scripts, so counting characters per script is more
reliable than a statistical detector on short text. The hard case is Tanglish (Tamil written
in Latin letters), which looks like English to every off-the-shelf detector; we catch it with
a small lexicon of common romanised Tamil words.
"""

import re
from typing import Literal

Language = Literal["en", "ta", "hi", "ta-Latn", "unknown"]

TAMIL_RANGE = (0x0B80, 0x0BFF)
DEVANAGARI_RANGE = (0x0900, 0x097F)

MIN_LETTERS = 3
"""Below this many letters there is not enough signal to decide."""

DOMINANT_SCRIPT_SHARE = 0.3
"""A native script wins if it makes up at least this share of letters.

Government documents mix in English scheme names and acronyms, so a Tamil page is often
only 50-70% Tamil characters. 0.3 keeps those pages Tamil without misreading an English
page that quotes one Tamil phrase.
"""

TANGLISH_MIN_HITS = 2
TANGLISH_MIN_SHARE = 0.15

# Romanised Tamil question words, pronouns, verb forms and particles, with the spelling
# variants people actually type. Only grammar words: nouns such as "magalir" or "thogai"
# appear inside scheme names in English documents and would cause false hits. Words that
# are also English (e.g. "la", "pa") are left out for the same reason.
# fmt: off
TANGLISH_WORDS = frozenset(
    {
        "enna", "yenna", "epdi", "eppadi", "yeppadi", "evlo", "evvalavu", "yevlo",
        "enga", "engey", "yaaru", "yaar", "yaarukku", "eppo", "eppodhu", "edhu", "ethu",
        "irukku", "iruku", "irukka", "irukkum", "illa", "illai", "illaya",
        "venum", "vendum", "venuma", "theriyuma", "theriyum", "therla", "teriyala",
        "panna", "pannanum", "pannalam", "pannuvathu", "kudukkanum", "kodukkanum",
        "kidaikkum", "kidaikuma", "kedaikuma", "kedaikum", "vaanga", "vanga",
        "sollunga", "solunga", "sollu", "naan", "naa", "enakku", "enaku", "ungalukku",
        "nanga", "naanga", "avanga", "ivanga", "ku", "kku", "ah", "aa", "dhaan", "thaan",
        "kooda", "mattum", "ellam", "romba", "konjam", "mudiyuma", "mudiyum",
        "eligible-aa", "apply-panna", "apply-pannanum",
        "irukaru", "irukkaru", "irukanga", "irukkanga", "panradhu", "panrathu",
        "poganum", "varum", "varala", "varudhu", "aagum", "aaguma",
    }
)
# fmt: on

_WORD_RE = re.compile(r"[a-z]+(?:-[a-z]+)?")


def _in_range(char: str, block: tuple[int, int]) -> bool:
    return block[0] <= ord(char) <= block[1]


def script_counts(text: str) -> dict[str, int]:
    """Count letters per script. Digits, punctuation and whitespace are ignored."""
    counts = {"tamil": 0, "devanagari": 0, "latin": 0}
    for char in text:
        if _in_range(char, TAMIL_RANGE):
            counts["tamil"] += 1
        elif _in_range(char, DEVANAGARI_RANGE):
            counts["devanagari"] += 1
        elif char.isascii() and char.isalpha():
            counts["latin"] += 1
    return counts


def is_tanglish(text: str) -> bool:
    words = _WORD_RE.findall(text.lower())
    if not words:
        return False
    hits = sum(word in TANGLISH_WORDS for word in words)
    return hits >= TANGLISH_MIN_HITS or (hits > 0 and hits / len(words) >= TANGLISH_MIN_SHARE)


def detect_language(text: str) -> Language:
    counts = script_counts(text)
    total = sum(counts.values())
    if total < MIN_LETTERS:
        return "unknown"

    # Compare the two native scripts first: a bilingual Tamil/English page is still Tamil.
    native, native_count = max(
        (("ta", counts["tamil"]), ("hi", counts["devanagari"])), key=lambda pair: pair[1]
    )
    if native_count / total >= DOMINANT_SCRIPT_SHARE:
        return native  # type: ignore[return-value]

    if counts["latin"] == 0:
        return "unknown"
    return "ta-Latn" if is_tanglish(text) else "en"
