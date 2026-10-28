"""Public request and response shapes of the HTTP API."""

from collections.abc import Mapping
import re
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


def rounded_timings(timings: Mapping[str, float]) -> dict[str, float]:
    return {stage: round(ms, 1) for stage, ms in timings.items()}


class CitationOut(BaseModel):
    number: int
    scheme: str
    doc_id: str
    document: str = Field(description="Readable document title, e.g. 'G.O.(Ms) No.15'.")
    page_start: int
    page_end: int
    page: int = Field(default=0, description="1-based starting page.")
    source_url: str
    excerpt: str = Field(description="The cited passage, as extracted from the document.")
    snippet: str = Field(default="", description="Alias for excerpt snippet.")
    document_date: str | None = Field(default=None, description="Official publication date of source document.")
    language: Language
    ocr_corrected: bool = Field(
        default=False,
        description="The excerpt holds an OCR misreading corrected by hand from the printed "
        "page; the UI should say so.",
    )


class SentenceOut(BaseModel):
    text: str
    citations: list[int] = Field(description="Numbers into `citations`.")


class ContactOut(BaseModel):
    scheme: str
    website: str
    helpline: str | None


class FallbackPassage(BaseModel):
    scheme: str
    doc_id: str
    document: str = Field(description="Readable document title, e.g. 'G.O.(Ms) No.15'.")
    page: int = Field(description="1-based starting page.")
    text: str = Field(description="Passage text from the retrieved chunk.")
    source_url: str


class AskResponse(BaseModel):
    answer: str = Field(description="Full answer with [n] markers, or the refusal message.")
    language: Language
    refused: bool
    status: Literal["SUPPORTED", "INSUFFICIENT_EVIDENCE", "MODEL_UNAVAILABLE"] = Field(
        default="SUPPORTED",
        description="SUPPORTED when verified by citations, INSUFFICIENT_EVIDENCE on refusal, MODEL_UNAVAILABLE on LLM failure.",
    )
    path: Literal["rag", "fact_card", "fallback"] = Field(
        default="rag",
        description="Path taken to answer: 'rag', 'fact_card', or 'fallback'.",
    )
    passages: list[FallbackPassage] | None = Field(
        default=None,
        description="Top retrieved passages provided on fallback when model is unavailable.",
    )
    needs_confirmation: bool = Field(
        default=False,
        description="True when query/transcript contains numbers or a scheme name requiring confirmation.",
    )
    refusal_reason: RefusalReason | None
    sentences: list[SentenceOut]
    citations: list[CitationOut]
    confidence: float = Field(description="Relevance of the best retrieved passage, 0-1.")
    disclaimer: str
    latency_ms: float
    timings_ms: dict[str, float] = Field(
        description="Milliseconds per stage, e.g. search, rerank, llm_answer, verifier, total "
        "(plus stt for voice questions). A stage that did not run is absent."
    )
    contact: ContactOut | None = Field(
        default=None, description="On a refusal about a known scheme: its official contact."
    )

    @classmethod
    def from_answer(
        cls,
        answer: Answer,
        titles: Mapping[str, str] | None = None,
        doc_dates: Mapping[str, str | None] | None = None,
    ) -> "AskResponse":
        titles = titles or {}
        doc_dates = doc_dates or {}
        has_digits = bool(re.search(r"[\d\u0BE6-\u0BEF\u0966-\u096F]", answer.question))
        q_lower = answer.question.lower()
        has_scheme = any(
            s in q_lower
            for s in (
                "pudhumai penn", "புதுமைப்பெண்", "cmchis", "முதலமைச்சர்", "maruthuva",
                "apy", "atal pension", "pm kisan", "pmkisan", "pmuy", "ujjwala",
                "kmut", "magalir urimai", "மகளிர் உரிமை", "moovalur", "muthulakshmi", "hostel", "விடுதி"
            )
        )
        needs_confirm = has_digits or has_scheme
        if answer.refusal_reason == "service_unavailable":
            status_val: Literal["SUPPORTED", "INSUFFICIENT_EVIDENCE", "MODEL_UNAVAILABLE"] = (
                "MODEL_UNAVAILABLE"
            )
            path_val: Literal["rag", "fact_card", "fallback"] = "fallback"
            fallback_passages = [
                FallbackPassage(
                    scheme=p.chunk.scheme,
                    doc_id=p.chunk.doc_id,
                    document=titles.get(p.chunk.doc_id, p.chunk.doc_id),
                    page=p.chunk.page_start,
                    text=p.chunk.text,
                    source_url=str(p.chunk.source_url),
                )
                for p in getattr(answer, "passages", [])
            ]
        elif answer.refused:
            status_val = "INSUFFICIENT_EVIDENCE"
            path_val = getattr(answer, "path", "rag")
            fallback_passages = None
        else:
            status_val = "SUPPORTED"
            path_val = getattr(answer, "path", "rag")
            fallback_passages = None

        return cls(
            answer=answer.text,
            language=answer.language,
            refused=answer.refused,
            status=status_val,
            path=path_val,
            passages=fallback_passages,
            needs_confirmation=needs_confirm,
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
                    page=c.page_start,
                    source_url=c.source_url,
                    excerpt=c.text,
                    snippet=c.text,
                    document_date=doc_dates.get(c.doc_id),
                    language=c.language,
                    ocr_corrected=c.ocr_corrected,
                )
                for c in answer.citations
            ],
            confidence=round(answer.confidence, 4),
            disclaimer=answer.disclaimer,
            latency_ms=round(answer.timings_ms.get("total", 0.0), 1),
            timings_ms=rounded_timings(answer.timings_ms),
            contact=(
                ContactOut(
                    scheme=answer.contact.scheme,
                    website=str(answer.contact.website),
                    helpline=answer.contact.helpline,
                )
                if answer.contact
                else None
            ),
        )


class VoiceAskResponse(AskResponse):
    transcript: str = Field(description="What Gnani speech to text heard; this was the question.")
    stt_language_code: str = Field(description="Language code sent to Gnani, e.g. 'ta-IN'.")
    stt_ms: float = Field(description="Time spent on speech to text, in milliseconds.")


class TranscribeResponse(BaseModel):
    transcript: str = Field(description="What Gnani speech to text heard.")
    stt_language_code: str = Field(description="Language code sent to Gnani, e.g. 'ta-IN'.")
    stt_ms: float = Field(description="Time spent on speech to text, in milliseconds.")


class SpeakRequest(BaseModel):
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] = Field(
        description="Answer text to read aloud; [n] citation markers are removed first."
    )
    language: Language = Field(description="The answer's language, from the /ask response.")


class AskSourcesResponse(BaseModel):
    passages: list[FallbackPassage]
    timings_ms: dict[str, float]


class HealthResponse(BaseModel):
    status: Literal["ok"]


class SourceOut(BaseModel):
    doc_id: str
    scheme: str
    title: str
    language: Language
    source_url: str
    doc_date: str | None
