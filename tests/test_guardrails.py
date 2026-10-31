from typing import Any

import pytest

from schemebot.generate.guardrails import DraftSentence, check_answer, numbers_in

PASSAGES = [
    "PM-KISAN pays Rs.6,000 per year in three instalments of Rs 2000.",
    "Applicants must be aged between 18 and 40 years.",
]


class FakeVerifier:
    def __init__(self, supported: set[int]) -> None:
        self.supported = supported
        self.calls = 0

    def complete_json(self, system: str, user: str, schema: dict[str, object]) -> dict[str, Any]:
        self.calls += 1
        return {"verdicts": [{"sentence": n, "supported": True} for n in self.supported]}


def test_numbers_ignore_thousands_separators_and_indic_digits() -> None:
    tamil_six_thousand = chr(0x0BEC) + chr(0x0BE6) * 3  # ௬௦௦௦

    assert numbers_in("Rs.6,000 per year") == {"6000"}
    assert numbers_in(f"ரூ.{tamil_six_thousand}") == {"6000"}
    assert numbers_in("income below 2.5 lakh") == {"250000"}


@pytest.mark.parametrize(
    ("sentence", "passage"),
    [
        ("Income must be below 2.5 lakh.", "Annual family income should not exceed Rs.2,50,000."),
        ("Income must be below Rs.2,50,000.", "Income should not exceed Rs. 2.5 lakhs."),
        ("ஆண்டு வருமானம் 2.5 லட்சத்திற்குள் இருக்க வேண்டும்.", "ஆண்டு வருமானம் ரூ.2,50,000/-க்குள்"),
        ("वार्षिक आय 2.5 लाख से कम होनी चाहिए।", "Annual income below Rs.2,50,000."),
        ("Cover of Rs.5 lakh per family.", "Cover of Rs.5,00,000 per family per year."),
        ("The budget is Rs.1 crore.", "An amount of Rs.1,00,00,000 is sanctioned."),
        ("The scheme started in 2023-24.", "Launched in the financial year 2023-2024."),
    ],
)
def test_same_amount_written_differently_is_kept(sentence: str, passage: str) -> None:
    result = check_answer([DraftSentence(sentence, [1])], [passage])

    assert result.rejected == []


@pytest.mark.parametrize(
    ("sentence", "passage"),
    [
        ("Income must be below 2.5 lakh.", "Income should not exceed Rs.25,000."),
        ("Income must be below 2 lakh.", "Income should not exceed Rs.2,50,000."),
        ("Income must be below 2.5 lakh.", "Income should not exceed Rs.2.5 crore."),
        ("The scheme started in 2023-24.", "Launched in 2023-2025."),
    ],
)
def test_different_amount_is_still_rejected(sentence: str, passage: str) -> None:
    result = check_answer([DraftSentence(sentence, [1])], [passage])

    assert [r.reason for r in result.rejected] == ["number_not_in_source"]


def test_age_ranges_and_plain_numbers_are_not_read_as_years() -> None:
    assert numbers_in("Age: 18-60 years") == {"18", "60"}
    assert numbers_in("in the year 2019-20") == {"2019", "2020"}
    assert numbers_in("2019-21") == {"2019", "21"}


def test_sentence_with_numbers_from_its_cited_passage_is_kept() -> None:
    sentence = DraftSentence("Farmers get Rs 6000 a year, paid as Rs 2000 instalments.", [1])

    result = check_answer([sentence], PASSAGES)

    assert result.kept == [sentence]
    assert result.rejected == []


def test_number_missing_from_cited_passage_is_rejected() -> None:
    # Right number, wrong passage: 6000 is in passage 1, not passage 2.
    wrong_source = DraftSentence("Farmers get Rs 6000 a year.", [2])
    # A calculated number the passage never states.
    calculated = DraftSentence("That is Rs 500 per month.", [1])

    result = check_answer([wrong_source, calculated], PASSAGES)

    assert result.kept == []
    assert [r.reason for r in result.rejected] == ["number_not_in_source"] * 2


def test_sentence_without_a_valid_citation_is_rejected() -> None:
    no_source = DraftSentence("You can apply online.", [])
    out_of_range = DraftSentence("You can apply online.", [7])

    result = check_answer([no_source, out_of_range], PASSAGES)

    assert [r.reason for r in result.rejected] == ["no_valid_citation"] * 2


def test_out_of_range_citations_are_dropped_but_valid_ones_kept() -> None:
    result = check_answer([DraftSentence("Ages 18 to 40 can join.", [2, 9])], PASSAGES)

    assert result.kept == [DraftSentence("Ages 18 to 40 can join.", [2])]


def test_verifier_removes_unsupported_sentences() -> None:
    sentences = [
        DraftSentence("Farmers get Rs 6000 a year.", [1]),
        DraftSentence("Only landless labourers can apply.", [1]),
    ]
    verifier = FakeVerifier(supported={1})

    result = check_answer(sentences, PASSAGES, verifier)

    assert result.kept == [sentences[0]]
    assert [(r.sentence, r.reason) for r in result.rejected] == [(sentences[1], "not_supported")]


def test_verifier_is_not_called_when_nothing_survives_the_cheap_checks() -> None:
    verifier = FakeVerifier(supported={1})

    check_answer([DraftSentence("Rs 999 per month.", [1])], PASSAGES, verifier)

    assert verifier.calls == 0


@pytest.mark.parametrize("missing", [set(), {2}])
def test_sentences_the_verifier_skips_count_as_unsupported(missing: set[int]) -> None:
    sentences = [DraftSentence("Farmers get Rs 6000 a year.", [1])]

    result = check_answer(sentences, PASSAGES, FakeVerifier(supported=missing))

    assert result.kept == []


def test_tamil_ilatcham_spelling_counts_as_lakh() -> None:
    from schemebot.generate.guardrails import numbers_in

    assert "250000" in numbers_in("ஆண்டு வருமானம் ரூ.2.5 இலட்சத்திற்குக் கீழ்")
    assert "250000" in numbers_in("Rs.2,50,000")


def test_monthly_claim_from_a_yearly_source_is_rejected() -> None:
    from schemebot.generate.guardrails import DraftSentence, check_answer

    passages = ["PM-KISAN gives Rs.6,000 per year to farmer families."]
    wrong = check_answer([DraftSentence("Farmers get Rs.6,000 a month.", [1])], passages)
    right = check_answer([DraftSentence("Farmers get Rs.6,000 a year.", [1])], passages)
    tamil = check_answer([DraftSentence("விவசாயிகளுக்கு ஆண்டுக்கு ரூ.6,000 கிடைக்கும்.", [1])], passages)
    assert [r.reason for r in wrong.rejected] == ["period_not_in_source"]
    assert len(right.kept) == 1
    assert len(tamil.kept) == 1


def test_source_without_a_period_is_left_to_the_verifier() -> None:
    from schemebot.generate.guardrails import DraftSentence, check_answer

    result = check_answer(
        [DraftSentence("The deposit is Rs.1,600 a year.", [1])], ["Security deposit Rs.1,600."]
    )
    assert len(result.kept) == 1
