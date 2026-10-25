"""Shared test doubles: a word-overlap encoder and reranker that need no ML models."""

import hashlib
import math
import re
from collections import Counter
from collections.abc import Sequence
from datetime import date

import pytest

from schemebot.index.embed import Embedding
from schemebot.ingest.langid import Language
from schemebot.ingest.models import Chunk

FAKE_DIMENSION = 64
_WORD = re.compile(r"\w+")


def _token_id(word: str) -> int:
    return int(hashlib.md5(word.encode()).hexdigest()[:6], 16)


class FakeEncoder:
    """Bag-of-words vectors: texts sharing words are close. Deterministic across runs."""

    dimension = FAKE_DIMENSION

    def __init__(self) -> None:
        self.calls: list[tuple[int, bool]] = []

    def encode(self, texts: Sequence[str], *, is_query: bool) -> list[Embedding]:
        self.calls.append((len(texts), is_query))
        return [self._embed(text) for text in texts]

    def _embed(self, text: str) -> Embedding:
        counts = Counter(word.lower() for word in _WORD.findall(text))
        dense = [0.0] * FAKE_DIMENSION
        for word, count in counts.items():
            dense[_token_id(word) % FAKE_DIMENSION] += count
        norm = math.sqrt(sum(value * value for value in dense)) or 1.0
        return Embedding(
            dense=[value / norm for value in dense],
            sparse={_token_id(word): float(count) for word, count in counts.items()},
        )


class FakeReranker:
    """Share of query words found in the passage."""

    def score(self, query: str, passages: Sequence[str]) -> list[float]:
        query_words = {word.lower() for word in _WORD.findall(query)}
        return [
            len(query_words & {word.lower() for word in _WORD.findall(passage)})
            / max(len(query_words), 1)
            for passage in passages
        ]


def make_chunk(chunk_id: str, text: str, language: Language = "en", page: int = 1) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id=chunk_id.rsplit("-", 1)[0],
        scheme="Test Scheme",
        source_url="https://example.gov.in/doc.pdf",
        page_start=page,
        page_end=page,
        section=None,
        language=language,
        doc_date=date(2024, 1, 1),
        text=text,
        extraction="text",
    )


@pytest.fixture
def corpus() -> list[Chunk]:
    return [
        make_chunk("pmkisan-en-001", "PM-KISAN pays Rs 6000 per year to landholding farmers."),
        make_chunk("pmkisan-en-002", "Income tax payers are excluded from PM-KISAN benefits."),
        make_chunk(
            "apy-en-001", "Atal Pension Yojana gives a pension of Rs 1000 to 5000 after 60."
        ),
        make_chunk(
            "apy-en-002", "Subscribers between 18 and 40 years of age can join the APY scheme."
        ),
        make_chunk("kmut-en-001", "Women heads of family with income below 2.5 lakh are eligible."),
    ]
