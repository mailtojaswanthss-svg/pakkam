import pytest

from schemebot.ingest.langid import detect_language, is_tanglish, script_counts


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Who is eligible for the PM-KISAN scheme?", "en"),
        ("மகளிர் உரிமைத் தொகை திட்டத்திற்கு யார் தகுதியானவர்?", "ta"),
        ("पीएम किसान योजना के लिए कौन पात्र है?", "hi"),
        ("Magalir urimai thogai ku yaar eligible?", "ta-Latn"),
        ("Enakku 1000 rubai kidaikuma?", "ta-Latn"),
        ("Pudhumai Penn scheme ku apply panna enna documents venum", "ta-Latn"),
    ],
)
def test_detects_each_language_group(text: str, expected: str) -> None:
    assert detect_language(text) == expected


def test_tamil_page_with_english_scheme_names_stays_tamil() -> None:
    text = "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) திட்டத்தின் கீழ் விவசாயிகளுக்கு நிதியுதவி"

    assert detect_language(text) == "ta"


def test_english_page_quoting_a_short_tamil_name_stays_english() -> None:
    text = (
        "The Kalaignar Magalir Urimai Thogai scheme (கலைஞர்) provides monthly assistance "
        "to eligible women heads of families in Tamil Nadu under the state government."
    )

    assert detect_language(text) == "en"


@pytest.mark.parametrize("text", ["", "   ", "12345 / 2024", "a1"])
def test_too_little_text_is_unknown(text: str) -> None:
    assert detect_language(text) == "unknown"


def test_one_lexicon_hit_in_a_long_english_sentence_is_not_tanglish() -> None:
    assert not is_tanglish("Applicants aged 21 to 60 can apply; the aa category is described below")


def test_script_counts_ignores_digits_and_punctuation() -> None:
    assert script_counts("ab 12, கா!") == {"tamil": 2, "devanagari": 0, "latin": 2}


@pytest.mark.parametrize(
    "query",
    [
        "husband govt job la irukaru, eligible ah",
        "ration card illa, apply panna mudiyuma",
        "thogai eppo varum",
        "PM kisan ku epdi apply panradhu",
    ],
)
def test_spoken_tanglish_queries(query: str) -> None:
    assert detect_language(query) == "ta-Latn"
