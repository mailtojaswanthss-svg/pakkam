from schemebot.index.store import build_index, open_client, point_id
from schemebot.ingest.models import Chunk
from tests.conftest import FakeEncoder

COLLECTION = "test"


def test_build_index_stores_every_chunk_with_its_payload(corpus: list[Chunk]) -> None:
    client = open_client(None)

    count = build_index(client, COLLECTION, corpus, FakeEncoder())

    assert count == client.count(COLLECTION).count == len(corpus)
    [point] = client.retrieve(COLLECTION, [point_id("apy-en-002")])
    assert point.payload is not None
    assert Chunk.model_validate(point.payload) == corpus[3]


def test_rebuilding_replaces_the_collection_instead_of_duplicating(corpus: list[Chunk]) -> None:
    client = open_client(None)

    build_index(client, COLLECTION, corpus, FakeEncoder())
    build_index(client, COLLECTION, corpus[:2], FakeEncoder())

    assert client.count(COLLECTION).count == 2


def test_passages_are_encoded_as_passages_not_queries(corpus: list[Chunk]) -> None:
    encoder = FakeEncoder()

    build_index(open_client(None), COLLECTION, corpus, encoder)

    assert encoder.calls and all(is_query is False for _, is_query in encoder.calls)


def test_point_ids_are_stable_and_unique() -> None:
    assert point_id("kmut-go15-2023-ta-p9-027") == point_id("kmut-go15-2023-ta-p9-027")
    assert point_id("a-p1-000") != point_id("a-p1-001")
