"""Full retrieval: hybrid search for candidates, then rerank and keep the best few."""

import threading
from dataclasses import dataclass

from schemebot.ingest.langid import detect_language
from schemebot.ingest.models import Chunk
from schemebot.retrieve.hybrid import HybridRetriever, SearchMode
from schemebot.retrieve.rerank import Reranker
from schemebot.retrieve.tanglish import gloss_tanglish
from schemebot.text import normalize_for_search

ROMANISED = ("en", "ta-Latn")


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
        gloss_tanglish: bool = True,
    ) -> None:
        self._first_stage = first_stage
        self._reranker = reranker
        self._candidates = candidates
        self._keep = keep
        self._gloss_tanglish = gloss_tanglish
        # The models sit on one GPU: callers on several threads take turns.
        self._lock = threading.Lock()

    def retrieve(self, query: str, mode: SearchMode = "hybrid") -> RetrievalResult:
        with self._lock:
            return self._retrieve(query, mode)

    def _retrieve(self, query: str, mode: SearchMode) -> RetrievalResult:
        candidates = self._first_stage.search(query, limit=self._candidates, mode=mode)
        if self._reranker is None:
            passages = [RetrievedPassage(c.chunk, c.score) for c in candidates]
        else:
            scores = self._reranker.score(
                normalize_for_search(self.rerank_query(query)),
                [normalize_for_search(c.chunk.text) for c in candidates],
            )
            passages = sorted(
                (RetrievedPassage(c.chunk, s) for c, s in zip(candidates, scores, strict=True)),
                key=lambda passage: passage.relevance,
                reverse=True,
            )
        return RetrievalResult(query=query, passages=passages[: self._keep])

    def rerank_query(self, query: str) -> str:
        """The query the reranker reads. First-stage search always uses the original.

        Romanised questions get an English gloss of their Tanglish words appended. Gloss
        alone answered unanswerable questions in testing; original plus gloss did not.
        The gate is whether there is anything to gloss, not language detection, which
        missed 6 of 28 Tanglish questions; plain English has nothing to gloss.
        """
        if not self._gloss_tanglish or detect_language(query) not in ROMANISED:
            return query
        glossed = gloss_tanglish(query)
        return query if glossed == query else f"{query} ({glossed})"
