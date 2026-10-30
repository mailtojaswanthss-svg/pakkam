"""Claim-lite: deterministic claim-level evidence verification without LLM calls.

Each claim returned by the answering model is checked against official source chunks:
1. chunk_id was among the retrieved chunks.
2. quote appears in the chunk text after Unicode and whitespace normalisation.
3. Every number and date in the claim also appears in the quote.
4. If period is 'monthly', 'yearly', or 'one_time', source must support that periodicity.

Failing any check marks the claim INSUFFICIENT_EVIDENCE.
If an amount claim fails, the entire answer is refused to prevent financial harm.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

from schemebot.generate.guardrails import numbers_in
from schemebot.ingest.models import Chunk
from schemebot.text import normalize_for_search

ClaimType = Literal["amount", "date", "condition", "description"]
ClaimPeriod = Literal["monthly", "yearly", "one_time", "unknown"]

MONTHLY_KEYWORDS = (
    "month",
    "monthly",
    "மாதம்",
    "மாதாந்திர",
    "மாதந்தோறும்",
    "மாதம் தோறும்",
    "प्रति माह",
    "मासिक",
    "महीना",
    "माह",
)
YEARLY_KEYWORDS = (
    "year",
    "yearly",
    "annual",
    "annum",
    "ஆண்டு",
    "ஆண்டுக்கு",
    "ஆண்டிற்கு",
    "வருடம்",
    "வருடாந்திர",
    "வருடத்திற்கு",
    "प्रति वर्ष",
    "वार्षिक",
    "साल",
    "वर्ष",
)
ONE_TIME_KEYWORDS = (
    "one-time",
    "one time",
    "lump sum",
    "single installment",
    "ஒரே முறை",
    "ஒரு முறை",
    "ஒற்றை",
    "एकमुश्त",
    "एक बार",
)


class Claim(BaseModel):
    text: str = Field(description="The factual claim made.")
    type: ClaimType = Field(description="Category of claim.")
    period: ClaimPeriod = Field(default="unknown", description="Periodicity if applicable.")
    chunk_id: str = Field(description="ID of the source chunk cited.")
    quote: str = Field(description="Exact words quoted from the source chunk.")


class VerifiedClaim(Claim):
    status: Literal["SUPPORTED", "INSUFFICIENT_EVIDENCE"]
    failure_reason: str | None = None


def normalize_whitespace_and_text(s: str) -> str:
    cleaned = re.sub(r"\s+", " ", normalize_for_search(s))
    return cleaned.strip().casefold()


def verify_claim(claim: Claim, retrieved_chunks: dict[str, Chunk]) -> tuple[bool, str]:
    """Deterministically verifies a claim against retrieved source chunks."""
    # 1. chunk_id check
    if claim.chunk_id not in retrieved_chunks:
        return False, "chunk_id_not_retrieved"

    chunk = retrieved_chunks[claim.chunk_id]

    # 2. Quote containment check
    norm_chunk = normalize_whitespace_and_text(chunk.text)
    norm_quote = normalize_whitespace_and_text(claim.quote)
    if not norm_quote or norm_quote not in norm_chunk:
        return False, "quote_not_in_chunk"

    # 3. Numbers & dates containment check
    claim_numbers = numbers_in(claim.text)
    quote_numbers = numbers_in(claim.quote)
    missing_numbers = claim_numbers - quote_numbers
    if missing_numbers:
        return False, f"numbers_missing_from_quote:{missing_numbers}"

    # 4. Periodicity check
    if claim.period == "monthly":
        q_lower = norm_quote
        c_lower = norm_chunk
        if not any(k in q_lower or k in c_lower for k in MONTHLY_KEYWORDS):
            return False, "monthly_period_not_found_in_source"
    elif claim.period == "yearly":
        q_lower = norm_quote
        c_lower = norm_chunk
        if not any(k in q_lower or k in c_lower for k in YEARLY_KEYWORDS):
            return False, "yearly_period_not_found_in_source"
    elif claim.period == "one_time":
        q_lower = norm_quote
        c_lower = norm_chunk
        if not any(k in q_lower or k in c_lower for k in ONE_TIME_KEYWORDS):
            return False, "one_time_period_not_found_in_source"

    return True, "SUPPORTED"


def verify_all_claims(
    claims: list[Claim],
    retrieved_chunks: dict[str, Chunk],
) -> tuple[list[VerifiedClaim], bool]:
    """Verifies all claims.

    Returns:
    (verified_claims, should_refuse_whole_answer)
    If any 'amount' claim fails, should_refuse_whole_answer is True.
    """
    verified = []
    refuse_answer = False

    for c in claims:
        passed, reason = verify_claim(c, retrieved_chunks)
        if passed:
            verified.append(
                VerifiedClaim(
                    **c.model_dump(),
                    status="SUPPORTED",
                    failure_reason=None,
                )
            )
        else:
            verified.append(
                VerifiedClaim(
                    **c.model_dump(),
                    status="INSUFFICIENT_EVIDENCE",
                    failure_reason=reason,
                )
            )
            # Rule: If an amount claim fails, refuse the whole answer
            if c.type == "amount":
                refuse_answer = True

    return verified, refuse_answer
