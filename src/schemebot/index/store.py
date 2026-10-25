"""Qdrant collection holding every chunk with a dense and a sparse vector.

Qdrant runs in local mode (inside this process, persisted to data/index/), so there is no
server to start. Point ids are derived from chunk ids, so rebuilding gives the same ids.
"""

import logging
import uuid
from collections.abc import Sequence
from pathlib import Path

from qdrant_client import QdrantClient, models

from schemebot.index.embed import Encoder
from schemebot.ingest.models import Chunk
from schemebot.text import normalize_for_search

logger = logging.getLogger(__name__)

DENSE_VECTOR = "dense"
SPARSE_VECTOR = "sparse"
UPSERT_BATCH = 64


def point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def open_client(path: Path | None) -> QdrantClient:
    """Persistent local client at `path`, or an in-memory one when `path` is None."""
    if path is None:
        return QdrantClient(":memory:")
    path.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(path))


def to_sparse(weights: dict[int, float]) -> models.SparseVector:
    indices = sorted(weights)
    return models.SparseVector(indices=indices, values=[weights[i] for i in indices])


def build_index(
    client: QdrantClient, collection: str, chunks: Sequence[Chunk], encoder: Encoder
) -> int:
    """(Re)create `collection` and fill it with `chunks`. Returns the number indexed."""
    if client.collection_exists(collection):
        client.delete_collection(collection)
    client.create_collection(
        collection,
        vectors_config={
            DENSE_VECTOR: models.VectorParams(
                size=encoder.dimension, distance=models.Distance.COSINE
            )
        },
        sparse_vectors_config={SPARSE_VECTOR: models.SparseVectorParams()},
    )

    for start in range(0, len(chunks), UPSERT_BATCH):
        batch = chunks[start : start + UPSERT_BATCH]
        embeddings = encoder.encode([normalize_for_search(c.text) for c in batch], is_query=False)
        client.upsert(
            collection,
            points=[
                models.PointStruct(
                    id=point_id(chunk.chunk_id),
                    vector={
                        DENSE_VECTOR: embedding.dense,
                        SPARSE_VECTOR: to_sparse(embedding.sparse),
                    },
                    payload=chunk.model_dump(mode="json"),
                )
                for chunk, embedding in zip(batch, embeddings, strict=True)
            ],
        )
        logger.info("indexed %d/%d chunks", min(start + UPSERT_BATCH, len(chunks)), len(chunks))
    return len(chunks)
