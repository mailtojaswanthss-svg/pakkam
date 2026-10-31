"""Checks that every sentence of an answer is backed by the passages it cites.

Three layers, cheapest first:
1. Citation check: the sentence cites at least one passage that was actually shown.
2. Number check: every number in the sentence (amount, age, income limit, date) appears in
   a cited passage. Numbers are where a wrong answer hurts most, and this check works the
   same in every language once digits are normalised. A number that is in the passage but
   known to be an OCR misreading (data/corrections.json) does not count.
3. Support check (optional): a second model reads each sentence with its cited passages
   and says whether they state it. Catches wrong claims that contain no number.
A sentence that fails any check is removed; if nothing is left the answer is refused.
"""

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Literal

from pydantic import BaseModel

from schemebot.generate.llm import JsonLlm, parse_reply
from schemebot.text import normalize_for_search

_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")

# "2.5 lakh" and "Rs.2,50,000" are the same amount; so are "2023-24" and "2023-2024".
# Tamil and Hindi words are matched by their stem, so inflected forms such as
# "லட்சத்திற்குள்" (within ... lakh) count too.
_LAKH, _CRORE = Decimal(100_000), Decimal(10_000_000)
_UNITS = re.compile(
    r"(?P<number>\d+(?:[.,]\d+)*)\s*"
    r"(?:(?P<lakh>lakhs?\b|lacs?\b|இ?லட்ச|लाख)|(?P<crore>crores?\b|கோடி|करोड))",
    re.IGNORECASE,
)
_FINANCIAL_YEAR = re.compile(r"\b(?P<start>\d{4})\s*[-–/]\s*(?P<end>\d{2})\b")

FailureReason = Literal[
    "no_valid_citation",
    "number_not_in_source",
    "period_not_in_source",
    "known_ocr_error",
    "not_supported",
]

# "Rs.6,000 a month" and "Rs.6,000 a year" share a number but not a meaning. A sentence that
# states a period must find that period in a cited passage (any language, including Tanglish).
_PERIODS = {
    "monthly": re.compile(
        r"\bmonth|\bp\.m\.|per mensem|மாத|maas|\bmasa|मासिक|माह|महीन|महिन",
        re.IGNORECASE,
    ),
    "yearly": re.compile(
        r"\byear|\bannual|\bannum|\bp\.a\.|ஆண்டு|ஆண்டி|வருட|varus|varud|\bvarsh|"
        r"वार्षिक|वर्ष|साल",
        re.IGNORECASE,
    ),
}


def periods_in(text: str) -> set[str]:
    return {name for name, pattern in _PERIODS.items() if pattern.search(text)}


@dataclass(frozen=True)
class DraftSentence:
    text: str
    sources: list[int]
    """1-based passage numbers, as the model returned them."""


@dataclass(frozen=True)
class RejectedSentence:
    sentence: DraftSentence
    reason: FailureReason


@dataclass(frozen=True)
class GuardrailResult:
    kept: list[DraftSentence]
    rejected: list[RejectedSentence]


def _in_full(match: re.Match[str]) -> str:
    """'2.5 lakh' -> '250000', '1 crore' -> '10000000'; unchanged if not a plain number."""
    try:
        value = Decimal(match["number"].replace(",", ""))
    except InvalidOperation:
        return match[0]
    full = value * (_LAKH if match["lakh"] else _CRORE)
    return str(full.to_integral_value()) if full == full.to_integral_value() else match[0]


def _full_year(match: re.Match[str]) -> str:
    """'2023-24' -> '2023-2024', only when the second part is the following year."""
    start, end = int(match["start"]), int(match["end"])
    if (start + 1) % 100 != end:
        return match[0]
    return f"{start}-{start + 1}"


def numbers_in(text: str) -> set[str]:
    """Numbers in one comparable form: 'Rs.6,000' and '6000' both give '6000', '2.5 lakh'
    and '2,50,000' both give '250000', and '2023-24' gives '2023' and '2024'."""
    text = _UNITS.sub(_in_full, normalize_for_search(text))
    text = _FINANCIAL_YEAR.sub(_full_year, text)
    found = set()
    for match in _NUMBER.findall(text):
        number = match.replace(",", "").rstrip(".")
        found.add(number.removesuffix(".00").removesuffix(".0"))
    return found


VERIFIER_SYSTEM = """\
You check answers written for citizens about government schemes. For each numbered \
sentence, decide whether the passages it cites state what the sentence says. A sentence \
is supported only if a reader of those passages would reach the same facts; translation \
into another language is fine, added or changed facts are not. Be strict."""

VERIFIER_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sentence": {"type": "integer"},
                    "supported": {"type": "boolean"},
                },
                "required": ["sentence", "supported"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["verdicts"],
    "additionalProperties": False,
}


class Verdict(BaseModel):
    sentence: int
    supported: bool


class VerifierReply(BaseModel):
    verdicts: list[Verdict]


def _verifier_message(sentences: list[DraftSentence], passages: list[str]) -> str:
    blocks = [f"[{number}]\n{text}" for number, text in enumerate(passages, start=1)]
    claims = [
        f"{index}. {sentence.text}  (cites {', '.join(map(str, sentence.sources))})"
        for index, sentence in enumerate(sentences, start=1)
    ]
    return (
        "<passages>\n" + "\n\n".join(blocks) + "\n</passages>\n\n"
        "<sentences>\n" + "\n".join(claims) + "\n</sentences>"
    )


def check_answer(
    sentences: list[DraftSentence],
    passages: list[str],
    verifier: JsonLlm | None = None,
    misread_numbers: list[set[str]] | None = None,
) -> GuardrailResult:
    """`misread_numbers[i]`: numbers in passage i+1 known to be OCR misreadings."""
    misread = misread_numbers or [set() for _ in passages]
    kept: list[DraftSentence] = []
    rejected: list[RejectedSentence] = []

    for sentence in sentences:
        valid = [n for n in sentence.sources if 1 <= n <= len(passages)]
        if not valid:
            rejected.append(RejectedSentence(sentence, "no_valid_citation"))
            continue
        cited_numbers = set().union(*(numbers_in(passages[n - 1]) for n in valid))
        sentence_numbers = numbers_in(sentence.text)
        if not sentence_numbers <= cited_numbers:
            rejected.append(RejectedSentence(sentence, "number_not_in_source"))
            continue
        stated = periods_in(sentence.text) if sentence_numbers else set()
        cited_periods = set().union(*(periods_in(passages[n - 1]) for n in valid))
        # Only a clash counts: the sentence says "a month" and the source names "a year" but
        # never a month (or the reverse). A source that names no period is left to the verifier.
        if len(stated) == 1 and cited_periods and not stated <= cited_periods:
            rejected.append(RejectedSentence(sentence, "period_not_in_source"))
            continue
        if any(sentence_numbers & misread[n - 1] for n in valid):
            rejected.append(RejectedSentence(sentence, "known_ocr_error"))
            continue
        kept.append(DraftSentence(sentence.text, valid))

    if verifier is None or not kept:
        return GuardrailResult(kept, rejected)

    reply = parse_reply(
        VerifierReply,
        verifier.complete_json(VERIFIER_SYSTEM, _verifier_message(kept, passages), VERIFIER_SCHEMA),
    )
    # A sentence the verifier skipped counts as unsupported: fail closed.
    supported = {v.sentence for v in reply.verdicts if v.supported}
    final: list[DraftSentence] = []
    for index, sentence in enumerate(kept, start=1):
        if index in supported:
            final.append(sentence)
        else:
            rejected.append(RejectedSentence(sentence, "not_supported"))
    return GuardrailResult(final, rejected)
