"""Broad questions like "I need a scheme for women": suggest schemes instead of refusing.

A specific question ("How much does PM-KISAN pay?") goes to the documents. A broad one names
no scheme, so no single passage matches it and the honest answer used to be a refusal, a
dead end for someone who does not know the scheme names yet. These questions now get the
schemes Pakkam can read that fit who is asking, as buttons; tapping one asks about it.
No facts are stated here, only scheme names, so nothing can be wrong about amounts or rules.
"""

import re

from schemebot.ingest.langid import Language

# Who each scheme is for. Only names and audiences: amounts and rules come from documents.
SCHEME_AUDIENCES: dict[str, tuple[str, ...]] = {
    "Kalaignar Magalir Urimai Thittam": ("women", "family"),
    "Pudhumai Penn Scheme": ("women", "students"),
    "Chief Minister's Breakfast Scheme": ("children", "students"),
    "PM-KISAN": ("farmers",),
    "Atal Pension Yojana": ("elderly", "workers"),
    "Pradhan Mantri Ujjwala Yojana": ("women", "family"),
    "Chief Minister's Comprehensive Health Insurance Scheme": ("health", "family"),
    "Moovalur Ramamirtham Ammaiyar Ninaivu Marriage Assistance Scheme": ("women", "marriage"),
}

_AUDIENCE_WORDS: dict[str, str] = {
    "women": r"wom[ae]n|ladies|lady|girls?|mother|widow|magalir|pengal|ponnu|பெண்|மகளிர்|"
    r"महिला|औरत|लड़की",
    "students": r"student|college|school|study|studies|padi|maanav|மாணவ|கல்லூரி|पढ़|छात्र",
    "children": r"child|kids?|kuzhandhai|pasanga|குழந்தை|बच्च",
    "farmers": r"farm|agri|vivasay|விவசாய|किसान|खेती",
    "elderly": r"old age|elder|senior|pension|retire|muthiyor|வயதான|முதியோர்|ஓய்வூதிய|"
    r"बुज़ुर्ग|बुजुर्ग|पेंशन|वृद्ध",
    "workers": r"worker|labou?r|unorganised|unorganized|kooli|தொழிலாள|मज़दूर|मजदूर|श्रमिक",
    "family": r"famil|household|poor|gas|lpg|cooking|kudumbam|குடும்ப|எரிவாயு|परिवार|गैस",
    "health": r"health|hospital|medical|treatment|insurance|maruthuva|மருத்துவ|स्वास्थ्य|इलाज",
    "marriage": r"marriage|wedding|kalyanam|thirumanam|திருமண|शादी|विवाह",
}
_AUDIENCE_PATTERNS = {
    name: re.compile(words, re.IGNORECASE) for name, words in _AUDIENCE_WORDS.items()
}

# "find / suggest / which / any ... scheme", in the four ways people ask.
_LOOKING = re.compile(
    r"\b(find|search|suggest|recommend|list|show|which|what|any|all|available|eligible|"
    r"need|want|looking|enna|endha|edhu|ethu|irukka|irukku)\b|"
    r"என்ன|எந்த|ஏதாவது|உள்ளன|இருக்கிற|कौन|क्या|कोई|सभी|बताओ|बताइए",
    re.IGNORECASE,
)
_SCHEME_WORD = re.compile(
    r"\b(schemes?|yojanas?|yojnas?|thittam|thittangal|benefits?|welfare|programs?|"
    r"programmes?)\b|திட்ட|योजना",
    re.IGNORECASE,
)
_SPECIFIC = re.compile(
    r"\b(how much|amount|evlo|evvalavu|apply|documents?|eligib\w*|age limit|income limit)\b|"
    r"எவ்வளவு|விண்ணப்ப|ஆவண|कितना|आवेदन|दस्तावेज़",
    re.IGNORECASE,
)


def audiences_in(question: str) -> set[str]:
    return {name for name, pattern in _AUDIENCE_PATTERNS.items() if pattern.search(question)}


def is_discovery(question: str, names_a_scheme: bool) -> bool:
    """True for "which schemes are there for farmers?"-type questions that name no scheme
    and ask nothing specific (amount, documents, how to apply)."""
    if names_a_scheme or _SPECIFIC.search(question):
        return False
    return bool(_SCHEME_WORD.search(question)) and (
        bool(_LOOKING.search(question)) or bool(audiences_in(question))
    )


def suggest_schemes(question: str) -> list[str]:
    """Schemes for the audiences the question mentions; every scheme when it names none."""
    wanted = audiences_in(question)
    matches = [s for s, who in SCHEME_AUDIENCES.items() if wanted & set(who)]
    return matches or list(SCHEME_AUDIENCES)


_INTRO = {
    "en": "These are the schemes Pakkam can read that may fit you. Tap one to ask about it:",
    "ta": "உங்களுக்குப் பொருந்தக்கூடிய, பக்கம் படிக்கும் திட்டங்கள் இவை. ஒன்றைத் தொட்டுக் கேளுங்கள்:",
    "hi": "ये वे योजनाएँ हैं जिन्हें पक्कम पढ़ सकता है और जो आपके काम की हो सकती हैं। किसी एक को चुनकर पूछें:",
    "ta-Latn": "Ungalukku porundhakoodiya, Pakkam padikkira schemes idho. "
    "Onna touch panni kelunga:",
}


def discovery_text(language: Language) -> str:
    return _INTRO.get(language, _INTRO["en"])
