"""Full retrieval: hybrid search for candidates, then rerank and keep the best few."""

from dataclasses import dataclass

from schemebot.ingest.models import Chunk
from schemebot.retrieve.hybrid import HybridRetriever, SearchMode
from schemebot.retrieve.rerank import Reranker
from schemebot.text import normalize_for_search


@dataclass(frozen=True)
class RetrievedPassage:
    chunk: Chunk
    relevance: float
    """Reranker probability (0-1) that the passage answers the query; the first-stage score
    when no reranker is used."""


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    passages: list[RetrievedPassage]

    @property
    def confidence(self) -> float:
        """Relevance of the best passage. Phase 4 refuses to answer when this is too low."""
        return self.passages[0].relevance if self.passages else 0.0


class Retriever:
    def __init__(
        self,
        first_stage: HybridRetriever,
        reranker: Reranker | None,
        candidates: int,
        keep: int,
    ) -> None:
        self._first_stage = first_stage
        self._reranker = reranker
        self._candidates = candidates
        self._keep = keep

    def retrieve(self, query: str, mode: SearchMode = "hybrid") -> RetrievalResult:
        candidates = self._first_stage.search(query, limit=self._candidates, mode=mode)
        if self._reranker is None:
            passages = [RetrievedPassage(c.chunk, c.score) for c in candidates]
        else:
            scores = self._reranker.score(
                normalize_for_search(query),
                [normalize_for_search(c.chunk.text) for c in candidates],
            )
            passages = sorted(
                (RetrievedPassage(c.chunk, s) for c, s in zip(candidates, scores, strict=True)),
                key=lambda passage: passage.relevance,
                reverse=True,
            )
        return RetrievalResult(query=query, passages=passages[: self._keep])
