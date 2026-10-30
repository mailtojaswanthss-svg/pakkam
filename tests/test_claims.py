import datetime

import pytest

from schemebot.generate.claims import Claim, verify_all_claims, verify_claim
from schemebot.ingest.models import Chunk


@pytest.fixture
def sample_chunk() -> Chunk:
    return Chunk(
        chunk_id="test_doc:p1:c0",
        doc_id="test_doc",
        scheme="Test Scheme",
        source_url="https://test.gov.in",
        page_start=1,
        page_end=1,
        section="Benefit",
        language="en",
        doc_date=datetime.date(2024, 1, 1),
        text="Under the scheme, beneficiaries receive Rs 6000 per year in three installments.",
        extraction="original",
    )


def test_claim_passes_when_supported(sample_chunk: Chunk):
    chunks = {sample_chunk.chunk_id: sample_chunk}
    claim = Claim(
        text="Beneficiaries receive Rs 6000 per year.",
        type="amount",
        period="yearly",
        chunk_id=sample_chunk.chunk_id,
        quote="beneficiaries receive Rs 6000 per year in three installments",
    )
    passed, reason = verify_claim(claim, chunks)
    assert passed is True
    assert reason == "SUPPORTED"


def test_claim_fails_on_wrong_chunk_id(sample_chunk: Chunk):
    chunks = {sample_chunk.chunk_id: sample_chunk}
    claim = Claim(
        text="Beneficiaries receive Rs 6000 per year.",
        type="amount",
        period="yearly",
        chunk_id="non_existent_chunk",
        quote="beneficiaries receive Rs 6000 per year",
    )
    passed, reason = verify_claim(claim, chunks)
    assert passed is False
    assert reason == "chunk_id_not_retrieved"


def test_claim_fails_when_quote_not_in_chunk(sample_chunk: Chunk):
    chunks = {sample_chunk.chunk_id: sample_chunk}
    claim = Claim(
        text="Beneficiaries receive Rs 10000 per month.",
        type="amount",
        period="monthly",
        chunk_id=sample_chunk.chunk_id,
        quote="beneficiaries receive Rs 10000 per month",  # Hallucinated quote
    )
    passed, reason = verify_claim(claim, chunks)
    assert passed is False
    assert reason == "quote_not_in_chunk"


def test_claim_fails_when_number_not_in_quote(sample_chunk: Chunk):
    chunks = {sample_chunk.chunk_id: sample_chunk}
    claim = Claim(
        text="Beneficiaries receive Rs 12000 per year.",  # Claim says 12,000, quote says 6,000
        type="amount",
        period="yearly",
        chunk_id=sample_chunk.chunk_id,
        quote="beneficiaries receive Rs 6000 per year",
    )
    passed, reason = verify_claim(claim, chunks)
    assert passed is False
    assert "numbers_missing_from_quote" in reason


def test_claim_periodicity_verification(sample_chunk: Chunk):
    chunks = {sample_chunk.chunk_id: sample_chunk}
    # Claim says monthly, but chunk says per year
    claim = Claim(
        text="Beneficiaries receive Rs 6000 monthly.",
        type="amount",
        period="monthly",
        chunk_id=sample_chunk.chunk_id,
        quote="beneficiaries receive Rs 6000 per year",
    )
    passed, reason = verify_claim(claim, chunks)
    assert passed is False
    assert reason == "monthly_period_not_found_in_source"


def test_verify_all_claims_refuses_when_amount_claim_fails(sample_chunk: Chunk):
    chunks = {sample_chunk.chunk_id: sample_chunk}
    claims = [
        Claim(
            text="Beneficiaries receive Rs 9000 per year.",
            type="amount",
            period="yearly",
            chunk_id=sample_chunk.chunk_id,
            quote="not in source",
        ),
        Claim(
            text="General scheme description.",
            type="description",
            period="unknown",
            chunk_id=sample_chunk.chunk_id,
            quote="under the scheme",
        ),
    ]
    verified, should_refuse = verify_all_claims(claims, chunks)
    assert should_refuse is True
    assert verified[0].status == "INSUFFICIENT_EVIDENCE"
    assert verified[1].status == "SUPPORTED"
