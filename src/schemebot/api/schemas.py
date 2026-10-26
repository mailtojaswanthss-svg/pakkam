"""Public request and response shapes of the HTTP API."""

from collections.abc import Mapping
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from schemebot.generate.answer import Answer
from schemebot.generate.messages import RefusalReason
from schemebot.ingest.langid import Language

MIN_QUESTION_CHARS = 3
MAX_QUESTION_CHARS = 500
"""Long enough for a detailed eligibility question; short enough to bound cost and latency."""

Question = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=MIN_QUESTION_CHARS, max_length=MAX_QUESTION_CHARS
    ),
]


class AskRequest(BaseModel):
    question: Question = Field(examples=["PM Kisan ku evlo panam kidaikum?"])


class CitationOut(BaseModel):
    number: int
    scheme: str
    doc_id: str
    document: str = Field(description="Readable document title, e.g. 'G.O.(Ms) No.15'.")
    page_start: int
    page_end: int
    source_url: str
    excerpt: str = Field(description="The cited passage, as extracted from the document.")
    language: Language


class SentenceOut(BaseModel):
    text: str
    citations: list[int] = Field(description="Numbers into `citations`.")


class AskResponse(BaseModel):
    answer: str = Field(description="Full answer with [n] markers, or the refusal message.")
    language: Language
    refused: bool
    refusal_reason: RefusalReason | None
    sentences: list[SentenceOut]
    citations: list[CitationOut]
    confidence: float = Field(description="Relevance of the best retrieved passage, 0-1.")
    disclaimer: str
    latency_ms: float

    @classmethod
    def from_answer(cls, answer: Answer, titles: Mapping[str, str] | None = None) -> "AskResponse":
        titles = titles or {}
        return cls(
            answer=answer.text,
            language=answer.language,
            refused=answer.refused,
            refusal_reason=answer.refusal_reason,
            sentences=[SentenceOut(text=s.text, citations=s.citations) for s in answer.sentences],
            citations=[
                CitationOut(
                    number=c.number,
                    scheme=c.scheme,
                    doc_id=c.doc_id,
                    document=titles.get(c.doc_id, c.doc_id),
                    page_start=c.page_start,
                    page_end=c.page_end,
                    source_url=c.source_url,
                    excerpt=c.text,
                    language=c.language,
                )
                for c in answer.citations
            ],
            confidence=round(answer.confidence, 4),
            disclaimer=answer.disclaimer,
            latency_ms=round(answer.timings_ms.get("total", 0.0), 1),
        )


class VoiceAskResponse(AskResponse):
    transcript: str = Field(description="What Gnani speech to text heard; this was the question.")
    stt_language_code: str = Field(description="Language code sent to Gnani, e.g. 'ta-IN'.")
    stt_ms: float = Field(description="Time spent on speech to text, in milliseconds.")


class SpeakRequest(BaseModel):
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] = Field(
        description="Answer text to read aloud; [n] citation markers are removed first."
    )
    language: Language = Field(description="The answer's language, from the /ask response.")


class HealthResponse(BaseModel):
    status: Literal["ok"]


class SourceOut(BaseModel):
    doc_id: str
    scheme: str
    title: str
    language: Language
    source_url: str
    doc_date: str | None
