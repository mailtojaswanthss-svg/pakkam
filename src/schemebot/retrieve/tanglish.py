"""English gloss of a Tanglish query, for the reranker.

The cross-encoder reads English, Tamil and Hindi well but romanised Tamil poorly: on the
development set, answerable Tanglish questions scored far below the same questions asked in
English, so most of them were refused. Before reranking, common Tanglish words are replaced
with English ones ("evlo" -> "how much"). Scheme names and English words pass through
unchanged, so "magalir urimai thogai" still matches the Tamil documents.
"""

import re

# Question words, verbs, pronouns, particles and the everyday nouns people use when asking
# about schemes, with the spelling variants people type. Scheme-name words ("magalir",
# "thogai", "pudhumai") are left out on purpose.
# fmt: off
GLOSS: dict[str, str] = {
    # question words
    "enna": "what", "yenna": "what", "epdi": "how", "eppadi": "how", "yeppadi": "how",
    "evlo": "how much", "evvalavu": "how much", "yevlo": "how much",
    "ethana": "how many", "ethanai": "how many", "evvalo": "how much",
    "yaar": "who", "yaaru": "who", "yaarukku": "for whom", "yarukku": "for whom",
    "eppo": "when", "eppodhu": "when", "eppothu": "when",
    "edhu": "which", "ethu": "which", "endha": "which", "entha": "which", "yendha": "which",
    # verbs and states
    "irukku": "is", "iruku": "is", "irukka": "is there", "irukkum": "will be",
    "irukkuma": "is there", "illa": "not", "illai": "not", "illaya": "is it not",
    "venum": "needed", "vendum": "needed", "venuma": "is it needed", "vendama": "is it not needed",
    "theriyuma": "do you know", "theriyum": "know",
    "panna": "do", "pannanum": "must do", "pannalam": "can do", "pannuvathu": "doing",
    "panradhu": "doing", "panrathu": "doing", "pannradhu": "doing", "pannurathu": "doing",
    "seyya": "do", "seyyanum": "must do",
    "kudukkanum": "must give", "kodukkanum": "must give", "kudukkum": "gives",
    "kodukkum": "gives", "kudupanga": "they give", "kodupanga": "they give",
    "tharuvanga": "they give", "tharuvaanga": "they give", "tharum": "gives",
    "kidaikkum": "will get", "kidaikum": "will get", "kedaikum": "will get",
    "kedaikkum": "will get", "kidaikuma": "can get", "kidaikkuma": "can get",
    "kedaikuma": "can get", "vaangalam": "can get", "vaanganum": "must get",
    "varum": "will come", "varuma": "will it come", "varala": "did not come",
    "varudhu": "is coming", "sollunga": "tell", "solunga": "tell", "sollu": "tell",
    "mudiyuma": "is it possible", "mudiyum": "possible", "aagum": "will be", "aaguma": "will it be",
    "poganum": "must go", "pogalam": "can go", "seralam": "can join", "sera": "join",
    "seranum": "must join", "edukkanum": "must take", "edukkalam": "can take",
    "padikka": "study", "padikkira": "studying", "padikkura": "studying",
    "padikiravanga": "students", "irukavanga": "people who are",
    "irukkuravanga": "people who are", "irukuravanga": "people who are",
    "irukaru": "is", "irukkaru": "is", "irukanga": "are", "irukkanga": "are",
    "irukanum": "must be", "irukkanum": "must be",
    "padicha": "studied", "padichu": "studied", "padikra": "studying", "padikira": "studying",
    "pona": "goes to", "ponaa": "goes to", "pogum": "goes to",
    "kudupaanga": "they give", "koduppaanga": "they give", "kuduppanga": "they give",
    "tharaanga": "they give", "tharanga": "they give",
    "tharaangala": "do they give", "tharangala": "do they give",
    # pronouns
    "naan": "I", "naa": "I", "enakku": "for me", "enaku": "for me", "ungalukku": "for you",
    "nanga": "we", "naanga": "we", "avanga": "they", "ivanga": "they",
    "indha": "this", "andha": "that",
    # particles: case endings standing alone, emphasis and question markers
    "ku": "for", "kku": "for", "la": "in", "le": "in", "oda": "of", "kitta": "from",
    "ah": "", "aa": "", "dhaan": "", "thaan": "",
    "kooda": "also", "mattum": "only", "ellam": "all", "romba": "very", "konjam": "a little",
    # everyday nouns
    "panam": "money", "kaasu": "money", "varusham": "year", "varushathu": "year",
    "varudam": "year", "maasam": "month", "masam": "month", "maasathu": "month",
    "masathu": "month", "naal": "day", "vayasu": "age", "vayadhu": "age",
    "pasanga": "children", "pasangal": "children", "pillainga": "children",
    "kuzhandhai": "child", "kozhandhai": "child", "kuzhandhaigal": "children",
    "ponnu": "girl", "ponnunga": "girls", "pengal": "women", "paiyan": "boy",
    "amma": "mother", "appa": "father", "veedu": "house", "veetu": "house",
    "kudumbam": "family", "vela": "job", "velai": "job", "padippu": "education",
    "palli": "school", "kalluri": "college", "maanavargal": "students",
    "vivasayi": "farmer", "vivasayigal": "farmers", "kadan": "loan",
    "udhavi": "help", "udavi": "help", "maruthuvamanai": "hospital",
    "maruthuvam": "medical", "sigichai": "treatment", "sikichai": "treatment",
    "marundhu": "medicine", "marunthu": "medicine", "saandridhal": "certificate",
    "jaathi": "caste", "jathi": "caste", "puthu": "new", "pudhu": "new",
}

# Word pairs whose word-by-word gloss reads badly ("age how much"). Applied first.
PHRASES: dict[str, str] = {
    "join panna": "to join", "join pannanum": "must join",
    "apply panna": "to apply", "apply pannanum": "must apply",
    "age evlo": "what age", "vayasu evlo": "what age",
}

# Case endings joined to a word ("varushathu-ku", "pasangal-ukku"). Longest first.
SUFFIXES: tuple[tuple[str, str], ...] = (
    ("ukku", "for"), ("kku", "for"), ("ku", "for"),
    ("oda", "of"), ("la", "in"), ("le", "in"), ("ah", ""), ("aa", ""),
)
# fmt: on

MIN_STEM = 3
_TOKEN_RE = re.compile(r"[A-Za-z]+|[^A-Za-z]+")
_SPACES_RE = re.compile(r"\s+")


def _gloss_word(word: str) -> str:
    lower = word.lower()
    if lower in GLOSS:
        return GLOSS[lower]
    for suffix, meaning in SUFFIXES:
        stem = lower[: -len(suffix)]
        if lower.endswith(suffix) and len(stem) >= MIN_STEM and stem in GLOSS:
            return f"{meaning} {GLOSS[stem]}".strip()
    return word


_PHRASE_RE = re.compile(
    r"\b(" + "|".join(re.escape(p) for p in sorted(PHRASES, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


def gloss_tanglish(text: str) -> str:
    """Replace known Tanglish words with English; everything else is kept as typed."""
    # Phrases first; the word pass only sees the text between them.
    pieces = _PHRASE_RE.split(text)
    parts: list[str] = []
    for index, piece in enumerate(pieces):
        if index % 2:  # odd pieces are the matched phrases
            parts.append(PHRASES[piece.lower()])
        else:
            parts += [_gloss_word(t) if t[0].isalpha() else t for t in _TOKEN_RE.findall(piece)]
    return _SPACES_RE.sub(" ", "".join(parts)).strip()
