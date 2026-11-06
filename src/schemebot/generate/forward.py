"""'Is this forward real?': check a forwarded message against the official documents.

A forward ("Rs.1,000 every month for women. Apply fast!") is split into a few checkable claims.
Each claim is asked as a question through the normal answer pipeline (search, cited answer,
number guardrail), and a small model compares the claim with that cited answer:
supported, contradicted, or not in the documents. The verdict never adds facts of its own:
it can only point at what the cited answer says.
"""

import contextlib
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Literal, Protocol
from urllib.parse import urlsplit

from pydantic import BaseModel, ValidationError

from schemebot.config import PROJECT_ROOT
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


# Scam signs in a forward, found by fixed rules (no model): a link that is not a government
# site, a request for an OTP, money or ID numbers, and "today only" pressure. Fake scheme
# messages (PM-KISAN "bonus" SMS, fake registration links) use exactly these.
ScamSign = Literal[
    "unofficial_link",
    "official_link",
    "insecure_link",
    "otp",
    "payment",
    "personal_data",
    "urgency",
]
_LINK = re.compile(
    r"(https?://|www\.)\S+|\b[\w-]+\.(?:com|in|org|net|xyz|online|site|info|ly|me|apk)\b\S*",
    re.I,
)
OFFICIAL_DOMAINS_FILE = PROJECT_ROOT / "data" / "official_domains.json"


@lru_cache(maxsize=1)
def _official_rules() -> tuple[tuple[str, ...], dict[str, bool]]:
    """(suffix domains, {exact host: subdomains allowed}) from data/official_domains.json."""
    data = json.loads(OFFICIAL_DOMAINS_FILE.read_text(encoding="utf-8"))
    suffixes = tuple(entry["domain"].lower() for entry in data.get("suffix", []))
    exact = {e["host"].lower(): bool(e.get("subdomains")) for e in data.get("exact", [])}
    return suffixes, exact


def link_host(link: str) -> tuple[str, str]:
    """(scheme, normalised host) of a link found in a message. Bare 'bit.ly/x' counts as https."""
    text = link.strip().rstrip(".,;:!?)\"'")
    parts = urlsplit(text if re.match(r"^[a-z][a-z0-9+.-]*://", text, re.I) else f"https://{text}")
    host = (parts.hostname or "").rstrip(".").lower()
    with contextlib.suppress(UnicodeError):
        host = host.encode("idna").decode("ascii")
    if host.startswith("www."):
        host = host[4:]
    return parts.scheme.lower(), host


def is_official_host(host: str) -> bool:
    """True only for an approved government host: a suffix rule at a dot boundary, or an exact
    approved host. Never substring matching (gov.in.fakewebsite.com is not official)."""
    suffixes, exact = _official_rules()
    if any(host == s or host.endswith("." + s) for s in suffixes):
        return True
    for approved, subdomains in exact.items():
        if host == approved or (subdomains and host.endswith("." + approved)):
            return True
    return False


_SIGNS: dict[ScamSign, re.Pattern[str]] = {
    "otp": re.compile(r"\botp\b|ஓடிபி|ओटीपी|one.?time.?password|verification code", re.I),
    "payment": re.compile(
        r"\b(pay|fee|fees|charges?|deposit|processing|registration amount|upi|gpay|phonepe|"
        r"paytm|kattanam|panam kattu)\b|கட்டணம்|செலுத்த|शुल्क|फीस|भुगतान|जमा करें",
        re.I,
    ),
    "personal_data": re.compile(
        r"\b(aadhaar|aadhar|pan|bank account|account number|atm|card number|cvv|pin)\b|ஆதார்|"
        r"வங்கி கணக்கு|आधार|बैंक खाता",
        re.I,
    ),
    "urgency": re.compile(
        r"\b(today only|last date today|hurry|urgent|immediately|before midnight|limited|"
        r"inniku mattum|udane)\b|இன்று மட்டும்|உடனே|அவசர|आज ही|तुरंत|जल्दी",
        re.I,
    ),
}


def scam_signs(message: str) -> list[ScamSign]:
    """Warning signs in a forwarded message, in a fixed order."""
    found: list[ScamSign] = []
    for match in _LINK.finditer(message):
        scheme, host = link_host(match.group(0))
        signs: list[ScamSign] = ["official_link"] if is_official_host(host) else ["unofficial_link"]
        if signs == ["official_link"] and scheme == "http":
            signs.append("insecure_link")  # a recognised site, but not over a secure link
        for sign in signs:
            if sign not in found:
                found.append(sign)
    found += [name for name, pattern in _SIGNS.items() if pattern.search(message)]
    return found


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
    scam_signs: list[ScamSign] = field(default_factory=list)


class ForwardChecker:
    def __init__(self, service: AnswerService, llm: JsonLlm) -> None:
        self._service = service
        self._llm = llm

    def check(self, message: str) -> ForwardCheck:
        signs = scam_signs(message)
        try:
            raw = self._llm.complete_json(CLAIMS_SYSTEM, message, CLAIMS_SCHEMA)
            claims = _Claims.model_validate(raw).claims[:MAX_CLAIMS]
        except (ValidationError, LlmDeclinedError) as error:
            logger.info("forward: no claims extracted (%s)", error)
            claims = []
        if not claims:
            return ForwardCheck("no_claims", [], signs)
        # Claims are independent: check them at the same time (search takes turns on the GPU).
        with ThreadPoolExecutor(max_workers=len(claims)) as pool:
            checked = list(pool.map(self._check_claim, claims))
        return ForwardCheck(_overall([c.verdict for c in checked]), checked, signs)

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
