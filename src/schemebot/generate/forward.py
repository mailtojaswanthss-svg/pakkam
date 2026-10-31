"""'Is this forward real?': check a forwarded message against the official documents.

A forward ("Rs.1,000 every month for women. Apply fast!") is split into a few checkable claims.
Each claim is asked as a question through the normal answer pipeline (search, cited answer,
number guardrail), and a small model compares the claim with that cited answer:
supported, contradicted, or not in the documents. The verdict never adds facts of its own:
it can only point at what the cited answer says.
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ValidationError

from schemebot.generate.answer import Answer
from schemebot.generate.llm import JsonLlm, LlmDeclinedError, LlmUnavailableError

logger = logging.getLogger(__name__)

MAX_CLAIMS = 3
Verdict = Literal["supported", "contradicted", "not_in_documents"]

CLAIMS_SYSTEM = """\
You read a message forwarded on WhatsApp about an Indian government welfare scheme. List the \
checkable claims in it (amounts, who can get it, dates, documents, how to apply), at most 3, \
most important first. Write each as a short question someone could ask about the official \
rules, in the same language and script as the message. Ignore urgency, links and opinions. \
If the message has no checkable claim about a scheme, return an empty list."""

CLAIMS_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"claim": {"type": "string"}, "question": {"type": "string"}},
                "required": ["claim", "question"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["claims"],
    "additionalProperties": False,
}

VERDICT_SYSTEM = """\
Compare a claim from a forwarded message with an answer taken from official documents. \
"supported" if the official answer states the same facts; "contradicted" if it states \
different facts (a different amount, age, group or date); "not_in_documents" if the official \
answer does not cover the claim. Judge only from the official answer. Explain in one short \
sentence in the claim's language, quoting the official amount or rule when there is one."""

VERDICT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["supported", "contradicted", "not_in_documents"]},
        "explanation": {"type": "string"},
    },
    "required": ["verdict", "explanation"],
    "additionalProperties": False,
}


class AnswerService(Protocol):
    def answer(self, question: str, voice_mode: bool = False) -> Answer: ...


class _Claim(BaseModel):
    claim: str
    question: str


class _Claims(BaseModel):
    claims: list[_Claim]


class _Verdict(BaseModel):
    verdict: Verdict
    explanation: str


@dataclass(frozen=True)
class CheckedClaim:
    claim: str
    question: str
    verdict: Verdict
    explanation: str
    answer: Answer


@dataclass(frozen=True)
class ForwardCheck:
    overall: Literal["looks_right", "partly_wrong", "wrong", "not_in_documents", "no_claims"]
    claims: list[CheckedClaim]


class ForwardChecker:
    def __init__(self, service: AnswerService, llm: JsonLlm) -> None:
        self._service = service
        self._llm = llm

    def check(self, message: str) -> ForwardCheck:
        try:
            raw = self._llm.complete_json(CLAIMS_SYSTEM, message, CLAIMS_SCHEMA)
            claims = _Claims.model_validate(raw).claims[:MAX_CLAIMS]
        except (ValidationError, LlmDeclinedError) as error:
            logger.info("forward: no claims extracted (%s)", error)
            claims = []
        if not claims:
            return ForwardCheck("no_claims", [])
        # Claims are independent: check them at the same time (search takes turns on the GPU).
        with ThreadPoolExecutor(max_workers=len(claims)) as pool:
            checked = list(pool.map(self._check_claim, claims))
        return ForwardCheck(_overall([c.verdict for c in checked]), checked)

    def _check_claim(self, claim: _Claim) -> CheckedClaim:
        answer = self._service.answer(claim.question)
        if answer.refused or not answer.sentences:
            return CheckedClaim(
                claim.claim, claim.question, "not_in_documents", answer.text, answer
            )
        official = " ".join(s.text for s in answer.sentences)
        try:
            raw = self._llm.complete_json(
                VERDICT_SYSTEM,
                f"<claim>\n{claim.claim}\n</claim>\n<official_answer>\n{official}\n</official_answer>",
                VERDICT_SCHEMA,
            )
            verdict = _Verdict.model_validate(raw)
        except (ValidationError, LlmDeclinedError, LlmUnavailableError) as error:
            logger.info("forward: verdict failed (%s)", error)
            return CheckedClaim(claim.claim, claim.question, "not_in_documents", official, answer)
        return CheckedClaim(
            claim.claim, claim.question, verdict.verdict, verdict.explanation, answer
        )


def _overall(
    verdicts: list[Verdict],
) -> Literal["looks_right", "partly_wrong", "wrong", "not_in_documents", "no_claims"]:
    if all(v == "not_in_documents" for v in verdicts):
        return "not_in_documents"
    if "contradicted" in verdicts:
        return "wrong" if "supported" not in verdicts else "partly_wrong"
    return "looks_right" if all(v == "supported" for v in verdicts) else "partly_wrong"
