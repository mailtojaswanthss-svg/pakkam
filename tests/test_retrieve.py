import pytest

from schemebot.index.store import build_index, open_client
from schemebot.ingest.models import Chunk
from schemebot.retrieve.hybrid import HybridRetriever, SearchMode
from schemebot.retrieve.retriever import Retriever
from tests.conftest import FakeEncoder, FakeReranker

COLLECTION = "test"


@pytest.fixture
def first_stage(corpus: list[Chunk]) -> HybridRetriever:
    client = open_client(None)
    encoder = FakeEncoder()
    build_index(client, COLLECTION, corpus, encoder)
    return HybridRetriever(client, COLLECTION, encoder, candidates_per_method=10)


@pytest.mark.parametrize("mode", ["hybrid", "dense", "sparse"])
def test_each_search_mode_finds_the_matching_chunk(
    first_stage: HybridRetriever, mode: SearchMode
) -> None:
    results = first_stage.search("pension after 60 Atal", limit=3, mode=mode)

    assert results[0].chunk.chunk_id == "apy-en-001"


def test_limit_is_respected(first_stage: HybridRetriever) -> None:
    assert len(first_stage.search("scheme", limit=2)) == 2


def test_reranker_reorders_and_keeps_only_the_best(first_stage: HybridRetriever) -> None:
    retriever = Retriever(first_stage, FakeReranker(), candidates=5, keep=2)

    result = retriever.retrieve("who can join APY between 18 and 40 years of age")

    assert len(result.passages) == 2
    assert result.passages[0].chunk.chunk_id == "apy-en-002"
    assert result.passages[0].relevance >= result.passages[1].relevance
    assert result.confidence == result.passages[0].relevance


def test_without_reranker_first_stage_order_is_kept(first_stage: HybridRetriever) -> None:
    retriever = Retriever(first_stage, None, candidates=5, keep=3)

    result = retriever.retrieve("income tax payers excluded")

    assert result.passages[0].chunk.chunk_id == "pmkisan-en-002"


def test_confidence_is_zero_when_nothing_is_retrieved() -> None:
    client = open_client(None)
    encoder = FakeEncoder()
    build_index(client, COLLECTION, [], encoder)
    retriever = Retriever(HybridRetriever(client, COLLECTION, encoder, 10), None, 5, 3)

    result = retriever.retrieve("anything")

    assert result.passages == []
    assert result.confidence == 0.0


def test_indic_digits_in_query_match_ascii_digits_in_passage(
    first_stage: HybridRetriever,
) -> None:
    tamil_two_point_five = chr(0x0BE8) + "." + chr(0x0BEB)  # ௨.௫

    results = first_stage.search(f"income below {tamil_two_point_five} lakh", limit=1)

    assert results[0].chunk.chunk_id == "kmut-en-001"
