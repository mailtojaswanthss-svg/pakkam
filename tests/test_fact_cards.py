from pathlib import Path

import pytest

from schemebot.generate.fact_cards import FactCard, FactCardMatcher, load_verified_cards


class MockEmbedding:
    def __init__(self, dense: list[float]):
        self.dense = dense


class MockEncoder:
    def __init__(self):
        # Maps phrase -> deterministic embedding vector
        self.map = {
            "KMUT amount?": [1.0, 0.0, 0.0],
            "How much under KMUT?": [0.95, 0.05, 0.0],
            "Unrelated query about KMUT": [0.1, 0.9, 0.0],
            "Random text": [0.0, 0.0, 1.0],
        }

    def encode(self, texts, *, is_query: bool):
        results = []
        for t in texts:
            vec = self.map.get(t, [0.0, 1.0, 0.0])
            results.append(MockEmbedding(vec))
        return results


@pytest.fixture
def sample_cards() -> list[FactCard]:
    return [
        FactCard(
            card_id="test_kmut",
            scheme="Kalaignar Magalir Urimai Thittam",
            field="amount",
            language="ta",
            question_examples=["KMUT amount?"],
            answer_text="Monthly amount is ₹1,000.",
            source_document="kmut-go15-2023-ta",
            source_page=2,
            document_date="2023-07-10",
            verified_by="Verifier Name",
            verified_on="2026-10-28",
        ),
        FactCard(
            card_id="unverified_card",
            scheme="PM-KISAN",
            field="amount",
            language="en",
            question_examples=["PM Kisan amount?"],
            answer_text="₹6,000 per year.",
            source_document="pmkisan-guidelines",
            source_page=4,
            document_date="2020-03-29",
            verified_by=None,  # Not verified
            verified_on=None,
        ),
    ]


def test_load_verified_cards_filters_unverified(
    tmp_path: Path, sample_cards: list[FactCard]
) -> None:
    p = tmp_path / "cards.json"
    p.write_text(
        f"""[
            {sample_cards[0].model_dump_json()},
            {sample_cards[1].model_dump_json()}
        ]""",
        encoding="utf-8",
    )
    loaded = load_verified_cards(p)
    assert len(loaded) == 1
    assert loaded[0].card_id == "test_kmut"


def test_fact_card_matcher_matches_high_similarity(sample_cards: list[FactCard]) -> None:
    verified_cards = [sample_cards[0]]
    matcher = FactCardMatcher(verified_cards, encoder=MockEncoder(), threshold=0.85)

    # Question with KMUT alias and high similarity
    card, score = matcher.match("How much under KMUT?")
    assert card is not None
    assert card.card_id == "test_kmut"
    assert score >= 0.85


def test_fact_card_matcher_rejects_unrelated_or_unmatched_scheme(
    sample_cards: list[FactCard],
) -> None:
    verified_cards = [sample_cards[0]]
    matcher = FactCardMatcher(verified_cards, encoder=MockEncoder(), threshold=0.85)

    # Low similarity
    card, score = matcher.match("Unrelated query about KMUT")
    assert card is None

    # High similarity vector but no scheme keyword in query
    card, score = matcher.match("KMUT amount?")  # Has KMUT keyword -> matches
    assert card is not None

    card, score = matcher.match("Random text")  # No scheme keyword
    assert card is None
