"""Prompt and output schema for grounded answering.

The model sees numbered passages [1]..[k] and must return JSON: a flag saying whether the
passages answer the question, and the answer as a list of sentences, each with the numbers
of the passages that support it. Keeping citations per sentence (instead of free text with
inline markers) is what lets the guardrail check every claim.
"""

from pydantic import BaseModel

from schemebot.ingest.langid import Language
from schemebot.retrieve.retriever import RetrievedPassage

ANSWER_LANGUAGE: dict[Language, str] = {
    "en": "English",
    "ta": "Tamil, written in Tamil script",
    "hi": "Hindi, written in Devanagari script",
    "ta-Latn": "Tamil written in English letters (Tanglish), the way the user wrote it",
    "unknown": "the same language and script as the question",
}

VOICE_SYSTEM_PROMPT = """\
You answer questions about Indian government welfare schemes for citizens over voice.

You are given numbered passages from official government documents. Answer using only \
what those passages say.

Rules for Voice:
- Exactly 1 or 2 short, concise sentences that are easy to understand when read aloud.
- Focus strictly on the primary answer: the exact amount, key eligibility rule, or main requirement.
- Copy amounts and numbers exactly from the passages. Do not calculate or convert them.
- If the passages do not answer the question, set "answerable" to false and return no sentences.
- Write each sentence without citation markers; the passage numbers go in "sources".
- Give each sentence a "section": "amount" (money or benefit), "eligibility" (who can \
get it, age or income limits), "documents" (papers needed), "apply" (how, where or when \
to apply), or "other".
"""


SYSTEM_PROMPT = """\
You answer questions about Indian government welfare schemes for citizens.

You are given numbered passages from official government documents. Answer using only \
what those passages say. People act on these answers to claim benefits, so a wrong \
amount, age limit or eligibility rule causes real harm; an honest "the documents don't \
say" is much better than a guess.

Rules:
- Use only facts stated in the passages. Do not add facts from your own knowledge, even \
if you are confident they are true.
- Every sentence must list the passage numbers that support it. Only cite a passage if it \
states the sentence's facts directly.
- Copy amounts, ages, dates and income limits exactly as the passage gives them. Do not \
convert or calculate them (for example, do not turn a yearly amount into a monthly one).
- If the passages do not answer the question, set "answerable" to false and return no \
sentences. Do this also when they only partly answer it in a way that would mislead.
- Passages may be in a different language from the question; translate their facts \
faithfully into the answer language.
- Keep the answer short and practical: who is eligible, how much, what documents, how to \
apply - whatever the question asks. Two to five sentences is usually enough.
- Write each sentence without citation markers; the passage numbers go in "sources".
- Give each sentence a "section": "amount" (money or benefit), "eligibility" (who can \
get it, age or income limits), "documents" (papers needed), "apply" (how, where or when \
to apply), or "other".
"""

SECTIONS = ("amount", "eligibility", "documents", "apply", "other")
"""How an answer is grouped on screen: how much, who can get it, documents, how to apply."""

ANSWER_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "answerable": {
            "type": "boolean",
            "description": "True only if the passages contain the answer.",
        },
        "sentences": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "sources": {"type": "array", "items": {"type": "integer"}},
                    "section": {
                        "type": "string",
                        "enum": list(SECTIONS),
                        "description": "What the sentence is about, for grouping on screen.",
                    },
                },
                "required": ["text", "sources", "section"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["answerable", "sentences"],
    "additionalProperties": False,
}


class ReplySentence(BaseModel):
    text: str
    sources: list[int]
    section: str = "other"


class AnswerReply(BaseModel):
    """The reply ANSWER_SCHEMA describes, validated before use."""

    answerable: bool
    sentences: list[ReplySentence]


def format_passages(passages: list[RetrievedPassage]) -> str:
    blocks = []
    for number, passage in enumerate(passages, start=1):
        chunk = passage.chunk
        header = f"[{number}] {chunk.scheme} | {chunk.doc_id} | page {chunk.page_start}"
        blocks.append(f"{header}\n{chunk.text}")
    return "\n\n".join(blocks)


def build_user_message(
    question: str,
    language: Language,
    passages: list[RetrievedPassage],
    earlier_question: str | None = None,
) -> str:
    """`earlier_question`: the user's previous question, when this one follows up on it
    ("and how do I apply?"). It only helps read the new question; facts still come from the
    passages."""
    earlier = (
        f"<earlier_question>\n{earlier_question}\n</earlier_question>\n"
        "The question below may follow up on this earlier question; read it in that light.\n\n"
        if earlier_question
        else ""
    )
    return (
        f"<passages>\n{format_passages(passages)}\n</passages>\n\n"
        f"{earlier}"
        f"<question>\n{question}\n</question>\n\n"
        f"Answer in {ANSWER_LANGUAGE[language]}."
    )
