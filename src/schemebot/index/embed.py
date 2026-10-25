"""Text -> dense + sparse vectors.

bge-m3 produces both in one forward pass: a 1024-d dense vector for meaning (works across
languages, so a Tamil question can land near an English passage) and sparse lexical weights
per token, which act as a learned keyword index for scheme names and numbers.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol

QUERY_MAX_TOKENS = 256
PASSAGE_MAX_TOKENS = 1024
"""Chunks are at most 1000 characters; Tamil needs up to ~3 characters per token."""


@dataclass(frozen=True)
class Embedding:
    dense: list[float]
    sparse: dict[int, float]
    """Token id -> weight. Only tokens with a non-zero weight are present."""


class Encoder(Protocol):
    dimension: int

    def encode(self, texts: Sequence[str], *, is_query: bool) -> list[Embedding]: ...


class BgeM3Encoder:
    dimension = 1024

    def __init__(self, model_name: str, batch_size: int, use_fp16: bool = True) -> None:
        from FlagEmbedding import BGEM3FlagModel

        self._model: Any = BGEM3FlagModel(model_name, use_fp16=use_fp16)
        self._batch_size = batch_size

    def encode(self, texts: Sequence[str], *, is_query: bool) -> list[Embedding]:
        if not texts:
            return []
        output = self._model.encode(
            list(texts),
            batch_size=self._batch_size,
            max_length=QUERY_MAX_TOKENS if is_query else PASSAGE_MAX_TOKENS,
            return_dense=True,
            return_sparse=True,
            return_colbert_vecs=False,
        )
        return [
            Embedding(
                dense=[float(value) for value in dense],
                sparse={int(token): float(weight) for token, weight in weights.items()},
            )
            for dense, weights in zip(output["dense_vecs"], output["lexical_weights"], strict=True)
        ]
