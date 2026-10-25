"""First-stage retrieval: dense and sparse search fused with Reciprocal Rank Fusion.

Dense search finds passages with the same meaning in any language; sparse search finds
exact scheme names, numbers and rare words. RRF combines them by rank, so the two scores
never need to be put on the same scale.
"""

from dataclasses import dataclass
from typing import Literal

from qdrant_client import QdrantClient, models

from schemebot.index.embed import Encoder
from schemebot.index.store import DENSE_VECTOR, SPARSE_VECTOR, to_sparse
from schemebot.ingest.models import Chunk
from schemebot.text import normalize_for_search

SearchMode = Literal["hybrid", "dense", "sparse"]
"""dense / sparse alone exist for the ablation study in the evaluation."""


@dataclass(frozen=True)
class Candidate:
    chunk: Chunk
    score: float
    """RRF score for hybrid, cosine for dense, dot product for sparse. Only for ordering."""


class HybridRetriever:
    def __init__(
        self,
        client: QdrantClient,
        collection: str,
        encoder: Encoder,
        candidates_per_method: int,
    ) -> None:
        self._client = client
        self._collection = collection
        self._encoder = encoder
        self._candidates_per_method = candidates_per_method

    def search(self, query: str, limit: int, mode: SearchMode = "hybrid") -> list[Candidate]:
        [embedding] = self._encoder.encode([normalize_for_search(query)], is_query=True)
        dense_query = embedding.dense
        sparse_query = to_sparse(embedding.sparse)

        if mode == "dense":
            response = self._client.query_points(
                self._collection, query=dense_query, using=DENSE_VECTOR, limit=limit
            )
        elif mode == "sparse":
            response = self._client.query_points(
                self._collection, query=sparse_query, using=SPARSE_VECTOR, limit=limit
            )
        else:
            response = self._client.query_points(
                self._collection,
                prefetch=[
                    models.Prefetch(
                        query=dense_query, using=DENSE_VECTOR, limit=self._candidates_per_method
                    ),
                    models.Prefetch(
                        query=sparse_query, using=SPARSE_VECTOR, limit=self._candidates_per_method
                    ),
                ],
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=limit,
            )
        return [
            Candidate(Chunk.model_validate(point.payload), point.score) for point in response.points
        ]
