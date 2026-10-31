import pytest

from schemebot.generate.discovery import (
    SCHEME_AUDIENCES,
    discovery_text,
    is_discovery,
    suggest_schemes,
)


@pytest.mark.parametrize(
    "question",
    [
        "i need to find a scheme on social welfare",
        "Which schemes are there for farmers?",
        "Any scheme for college girls?",
        "pengalukku enna thittam irukku?",
        "பெண்களுக்கு என்ன திட்டங்கள் உள்ளன?",
        "किसानों के लिए कौन सी योजना है?",
    ],
)
def test_broad_questions_are_discovery(question: str) -> None:
    assert is_discovery(question, names_a_scheme=False)


@pytest.mark.parametrize(
    "question",
    [
        "How much does the scheme give per month?",
        "What documents are needed for the gas scheme?",
        "Who is the chief minister of Kerala?",
        "How do I apply?",
    ],
)
def test_specific_or_unrelated_questions_are_not(question: str) -> None:
    assert not is_discovery(question, names_a_scheme=False)


def test_a_named_scheme_is_never_discovery() -> None:
    assert not is_discovery("Which scheme is PM-KISAN?", names_a_scheme=True)


def test_suggestions_follow_who_is_asking() -> None:
    assert suggest_schemes("schemes for farmers") == ["PM-KISAN"]
    women = suggest_schemes("any scheme for women?")
    assert "Kalaignar Magalir Urimai Thittam" in women
    assert "PM-KISAN" not in women
    assert suggest_schemes("social welfare schemes") == list(SCHEME_AUDIENCES)


def test_intro_in_each_language() -> None:
    assert len({discovery_text(lang) for lang in ("en", "ta", "hi", "ta-Latn")}) == 4  # type: ignore[arg-type]
