"""Faithfulness judge for the evaluation.

Separate from the in-pipeline verifier on purpose: different model and prompt, and it
grades the final answer (after the guardrail), so the pipeline is not marking its own work
with the same check. It is still an LLM judge; a sample of its verdicts should be checked
by hand and reported alongside the numbers.
"""

from pydantic import BaseModel

from schemebot.generate.answer import Answer
from schemebot.generate.llm import JsonLlm, parse_reply

JUDGE_SYSTEM = """\
You are grading an assistant that answers questions about government schemes from \
official documents. For each numbered sentence of the answer, decide whether every fact in \
it (amounts, ages, limits, dates, names, conditions) is stated in the passages that \
sentence cites. A faithful translation counts as stated. Anything added, changed, \
calculated or generalised beyond the passages is not supported. Judge only support by the \
cited passages, not whether the sentence is true in the world."""

JUDGE_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sentence": {"type": "integer"},
                    "supported": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
                "required": ["sentence", "supported", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["verdicts"],
    "additionalProperties": False,
}


class JudgeVerdict(BaseModel):
    sentence: int
    supported: bool
    reason: str


class JudgeReply(BaseModel):
    verdicts: list[JudgeVerdict]


def judge_message(answer: Answer) -> str:
    passages = "\n\n".join(f"[{c.number}]\n{c.text}" for c in answer.citations)
    sentences = "\n".join(
        f"{index}. {s.text}  (cites {', '.join(map(str, s.citations))})"
        for index, s in enumerate(answer.sentences, start=1)
    )
    return (
        f"<question>\n{answer.question}\n</question>\n\n"
        f"<passages>\n{passages}\n</passages>\n\n"
        f"<answer_sentences>\n{sentences}\n</answer_sentences>"
    )


class FaithfulnessJudge:
    def __init__(self, llm: JsonLlm) -> None:
        self._llm = llm

    def supported(self, answer: Answer) -> list[bool]:
        """One verdict per answer sentence; a sentence the judge skips counts as unsupported."""
        if not answer.sentences:
            return []
        reply = parse_reply(
            JudgeReply, self._llm.complete_json(JUDGE_SYSTEM, judge_message(answer), JUDGE_SCHEMA)
        )
        verdicts = {v.sentence: v.supported for v in reply.verdicts}
        return [verdicts.get(index, False) for index in range(1, len(answer.sentences) + 1)]
