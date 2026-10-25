"""Checks with the real bge-m3 and bge-reranker-v2-m3 models.

Skipped by default (see pyproject addopts). Run with `uv run pytest -m models`.
These verify the claim the whole project rests on: a question in one language finds the
right passage written in another.
"""

import pytest

from schemebot.index.store import build_index, open_client
from schemebot.ingest.models import Chunk
from schemebot.retrieve.hybrid import HybridRetriever
from schemebot.retrieve.retriever import Retriever
from tests.conftest import make_chunk

pytestmark = pytest.mark.models

COLLECTION = "models-test"

# Only English passages: every non-English question must cross languages to succeed.
ENGLISH_CORPUS = [
    make_chunk("pmkisan-en-001", "Under PM-KISAN, landholding farmer families receive Rs 6000 "
               "per year in three equal instalments paid directly into their bank accounts."),
    make_chunk("apy-en-001", "Any citizen of India aged between 18 and 40 years who is not an "
               "income tax payer can join the Atal Pension Yojana."),
    make_chunk("pmuy-en-001", "Under Ujjwala, adult women from poor households get a free LPG "
               "connection. A KYC form and proof of address are required."),
    make_chunk("kmut-en-001", "Women heads of families with annual family income below Rs 2.5 "
               "lakh are eligible for Rs 1000 per month under Kalaignar Magalir Urimai Thittam."),
    make_chunk("breakfast-en-001", "The Chief Minister's Breakfast Scheme serves free breakfast "
               "to students of classes 1 to 5 in government schools."),
]  # fmt: skip

CROSS_LINGUAL_QUESTIONS = [
    ("ta", "விவசாயிகளுக்கு ஆண்டுக்கு எவ்வளவு பணம் கிடைக்கும்?", "pmkisan-en-001"),
    ("ta", "மகளிர் உரிமைத் தொகைக்கு வருமான வரம்பு என்ன?", "kmut-en-001"),
    ("ta", "அரசுப் பள்ளி மாணவர்களுக்கு காலை உணவு திட்டம் உள்ளதா?", "breakfast-en-001"),
    ("hi", "अटल पेंशन योजना में कौन शामिल हो सकता है?", "apy-en-001"),
    ("hi", "मुफ्त गैस कनेक्शन के लिए कौन से दस्तावेज़ चाहिए?", "pmuy-en-001"),
    ("ta-Latn", "magalir urimai thogai ku income limit enna", "kmut-en-001"),
    ("ta-Latn", "pension scheme la join panna age evlo", "apy-en-001"),
]


@pytest.fixture(scope="module")
def retriever() -> Retriever:
    from schemebot.config import Settings
    from schemebot.index.embed import BgeM3Encoder
    from schemebot.retrieve.rerank import BgeReranker

    settings = Settings(_env_file=None)
    encoder = BgeM3Encoder(settings.embedding_model, batch_size=8)
    client = open_client(None)
    build_index(client, COLLECTION, ENGLISH_CORPUS, encoder)
    return Retriever(
        HybridRetriever(client, COLLECTION, encoder, candidates_per_method=5),
        BgeReranker(settings.reranker_model),
        candidates=5,
        keep=3,
    )


@pytest.mark.parametrize(("language", "question", "expected"), CROSS_LINGUAL_QUESTIONS)
def test_question_retrieves_english_passage(
    retriever: Retriever, language: str, question: str, expected: str
) -> None:
    result = retriever.retrieve(question)

    assert result.passages[0].chunk.chunk_id == expected, f"[{language}] {question}"


def test_unrelated_question_gets_low_confidence(retriever: Retriever) -> None:
    result = retriever.retrieve("What is the capital of France?")

    assert result.confidence < 0.1


def test_answerable_question_gets_high_confidence(retriever: Retriever) -> None:
    result = retriever.retrieve("How much money do farmers get per year under PM-KISAN?")

    assert result.confidence > 0.5


def test_corpus_chunks_are_valid(retriever: Retriever) -> None:
    assert all(isinstance(chunk, Chunk) for chunk in ENGLISH_CORPUS)
