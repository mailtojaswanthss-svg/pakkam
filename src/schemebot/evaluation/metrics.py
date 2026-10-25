"""Metric definitions, kept as small pure functions so each can be checked by hand."""

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

RECALL_KS = (1, 5)


@dataclass
class QuestionResult:
    id: str
    group: str
    answerable: bool
    status: str
    retrieved: list[str]
    """"doc_id:p<start>" of each passage, best first."""
    relevant: list[bool]
    confidence: float
    retrieval_ms: float
    refused: bool
    """By the answer pipeline, or by the confidence threshold in retrieval-only runs."""
    refusal_reason: str | None = None
    answer: str | None = None
    citations_relevant: list[bool] = field(default_factory=list)
    sentences_supported: list[bool] = field(default_factory=list)
    total_ms: float | None = None


def recall_at_k(relevant: Sequence[bool], k: int) -> bool:
    """At least one relevant passage among the first k."""
    return any(relevant[:k])


def reciprocal_rank(relevant: Sequence[bool]) -> float:
    for rank, hit in enumerate(relevant, start=1):
        if hit:
            return 1.0 / rank
    return 0.0


def percentile(values: Sequence[float], q: float) -> float:
    """Nearest-rank percentile; q in [0, 100]."""
    if not values:
        return math.nan
    ordered = sorted(values)
    rank = max(1, math.ceil(q / 100 * len(ordered)))
    return ordered[rank - 1]


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def rate(flags: Sequence[bool]) -> float:
    return mean([1.0 if flag else 0.0 for flag in flags])


@dataclass(frozen=True)
class Summary:
    answerable: int
    unanswerable: int
    recall: dict[int, float]
    mrr: float
    correct_refusal: float
    """Share of unanswerable questions that were refused."""
    false_refusal: float
    """Share of answerable questions that were refused."""
    faithfulness: float
    """Share of answer sentences the judge found supported by their citations."""
    citation_accuracy: float
    """Share of citations (on answerable questions) that point to a gold page."""
    retrieval_p50: float
    retrieval_p95: float
    total_p50: float
    total_p95: float


def summarize(results: Sequence[QuestionResult]) -> Summary:
    answerable = [r for r in results if r.answerable]
    unanswerable = [r for r in results if not r.answerable]
    totals = [r.total_ms for r in results if r.total_ms is not None]
    return Summary(
        answerable=len(answerable),
        unanswerable=len(unanswerable),
        recall={k: rate([recall_at_k(r.relevant, k) for r in answerable]) for k in RECALL_KS},
        mrr=mean([reciprocal_rank(r.relevant) for r in answerable]),
        correct_refusal=rate([r.refused for r in unanswerable]),
        false_refusal=rate([r.refused for r in answerable]),
        faithfulness=rate([s for r in results for s in r.sentences_supported]),
        citation_accuracy=rate([c for r in answerable for c in r.citations_relevant]),
        retrieval_p50=percentile([r.retrieval_ms for r in results], 50),
        retrieval_p95=percentile([r.retrieval_ms for r in results], 95),
        total_p50=percentile(totals, 50),
        total_p95=percentile(totals, 95),
    )
