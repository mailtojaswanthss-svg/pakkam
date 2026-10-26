"""Question -> cited answer, or an honest refusal.

Order of decisions:
1. Retrieve. If the best passage is not relevant enough, refuse without calling the LLM.
2. Ask the LLM to answer from the passages only, as cited sentences.
3. Run the guardrail; drop any sentence the passages do not back. Refuse if none remain.
"""

import logging
import time
from dataclasses import dataclass, field

from schemebot.generate.contacts import Contact
from schemebot.generate.guardrails import (
    DraftSentence,
    RejectedSentence,
    check_answer,
    numbers_in,
)
from schemebot.generate.llm import JsonLlm, LlmDeclinedError, LlmUnavailableError, parse_reply
from schemebot.generate.messages import RefusalReason, contact_text, disclaimer, refusal_text
from schemebot.generate.prompt import (
    ANSWER_SCHEMA,
    SYSTEM_PROMPT,
    AnswerReply,
    build_user_message,
)
from schemebot.ingest.corrections import CORRECTED, OcrCorrection
from schemebot.ingest.langid import Language, detect_language
from schemebot.ingest.models import Chunk
from schemebot.retrieve.retriever import RetrievedPassage, Retriever

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Citation:
    number: int
    doc_id: str
    scheme: str
    page_start: int
    page_end: int
    source_url: str
    text: str
    """The cited passage itself, for showing the source and for faithfulness checks."""
    language: Language = "unknown"
    """Language of the passage, so the UI can tag and render it correctly."""
    ocr_corrected: bool = False
    """The passage holds a misreading fixed by hand from the printed page."""


@dataclass(frozen=True)
class AnswerSentence:
    text: str
    citations: list[int]
    """Numbers into Answer.citations."""


@dataclass(frozen=True)
class Answer:
    question: str
    language: Language
    text: str
    sentences: list[AnswerSentence]
    citations: list[Citation]
    refused: bool
    refusal_reason: RefusalReason | None
    confidence: float
    disclaimer: str
    rejected: list[RejectedSentence] = field(default_factory=list)
    timings_ms: dict[str, float] = field(default_factory=dict)
    """Milliseconds per stage: retrieval (= search + rerank), llm_answer, verifier,
    generation (= llm_answer + verifier) and total. A stage that did not run is absent."""


def _citation(number: int, passage: RetrievedPassage) -> Citation:
    chunk = passage.chunk
    return Citation(
        number=number,
        doc_id=chunk.doc_id,
        scheme=chunk.scheme,
        page_start=chunk.page_start,
        page_end=chunk.page_end,
        source_url=str(chunk.source_url),
        text=chunk.text,
        language=chunk.language,
        ocr_corrected=chunk.extraction == CORRECTED,
    )


def misread_numbers_by_page(corrections: list[OcrCorrection]) -> dict[tuple[str, int], set[str]]:
    """(doc_id, page) -> numbers OCR is known to have misread there ('4000' for Rs.1,000).
    An entry whose page is not known yet blocks nothing."""
    found: dict[tuple[str, int], set[str]] = {}
    for correction in corrections:
        if correction.page is None:
            continue
        wrong = numbers_in(correction.ocr_reads) - numbers_in(correction.pdf_shows)
        found.setdefault((correction.doc_id, correction.page), set()).update(wrong)
    return found


def _misread_in(chunk: Chunk, misread: dict[tuple[str, int], set[str]]) -> set[str]:
    """Known-wrong numbers on the pages this passage covers that its text really contains."""
    pages = range(chunk.page_start, chunk.page_end + 1)
    wrong = set().union(*(misread.get((chunk.doc_id, page), set()) for page in pages))
    return wrong & numbers_in(chunk.text)


class Answerer:
    def __init__(
        self,
        retriever: Retriever,
        llm: JsonLlm,
        verifier: JsonLlm | None,
        refusal_threshold: float,
        contacts: dict[str, Contact] | None = None,
        corrections: list[OcrCorrection] | None = None,
    ) -> None:
        self._retriever = retriever
        self._llm = llm
        self._verifier = verifier
        self._refusal_threshold = refusal_threshold
        self._contacts = contacts or {}
        # Confirmed fixes are applied at ingestion, but stay here too: until the index is
        # rebuilt the passage still holds the misreading.
        self._misread = misread_numbers_by_page(corrections or [])

    def answer(self, question: str) -> Answer:
        timings: dict[str, float] = {}
        started = time.perf_counter()
        language = detect_language(question)

        retrieval = self._retriever.retrieve(question)
        timings["retrieval"] = (time.perf_counter() - started) * 1000
        timings.update(retrieval.timings_ms)  # "search" and "rerank" inside "retrieval"
        confidence = retrieval.confidence

        def refuse(reason: RefusalReason, rejected: list[RejectedSentence] | None = None) -> Answer:
            timings["total"] = (time.perf_counter() - started) * 1000
            logger.info("refused (%s), confidence %.3f", reason, confidence)
            text = refusal_text(reason, language)
            # Past the confidence check the question is about a scheme we hold documents
            # for, so point to that scheme's official contact. Below it we don't know which
            # scheme (if any) the question is about, so the generic advice stays.
            if reason != "low_confidence" and retrieval.passages:
                contact = self._contacts.get(retrieval.passages[0].chunk.scheme)
                if contact:
                    text += " " + contact_text(
                        contact.scheme, contact.helpline, str(contact.website), language
                    )
            return Answer(
                question=question,
                language=language,
                text=text,
                sentences=[],
                citations=[],
                refused=True,
                refusal_reason=reason,
                confidence=confidence,
                disclaimer=disclaimer(language),
                rejected=rejected or [],
                timings_ms=timings,
            )

        if confidence < self._refusal_threshold:
            return refuse("low_confidence")

        passages = retrieval.passages
        passage_texts = [passage.chunk.text for passage in passages]
        misread = [_misread_in(passage.chunk, self._misread) for passage in passages]
        generation_started = time.perf_counter()
        try:
            reply = parse_reply(
                AnswerReply,
                self._llm.complete_json(
                    SYSTEM_PROMPT, build_user_message(question, language, passages), ANSWER_SCHEMA
                ),
            )
            timings["llm_answer"] = (time.perf_counter() - generation_started) * 1000
            drafts = [DraftSentence(s.text.strip(), s.sources) for s in reply.sentences]
            if not reply.answerable or not drafts:
                return refuse("not_in_documents")
            verify_started = time.perf_counter()
            checked = check_answer(drafts, passage_texts, self._verifier, misread)
            # Guardrail checks plus the verifier call (when one is configured).
            timings["verifier"] = (time.perf_counter() - verify_started) * 1000
        except LlmDeclinedError:
            return refuse("model_declined")
        except LlmUnavailableError as error:
            logger.error("LLM unavailable: %s", error)
            return refuse("service_unavailable")
        finally:
            timings["generation"] = (time.perf_counter() - generation_started) * 1000

        if not checked.kept:
            return refuse("unsupported", checked.rejected)

        # Renumber citations so the user sees [1], [2], ... in order of first use.
        cited_order: list[int] = []
        for sentence in checked.kept:
            for source in sentence.sources:
                if source not in cited_order:
                    cited_order.append(source)
        renumber = {source: new for new, source in enumerate(cited_order, start=1)}
        citations = [_citation(renumber[s], passages[s - 1]) for s in cited_order]
        sentences = [
            AnswerSentence(s.text, sorted(renumber[source] for source in s.sources))
            for s in checked.kept
        ]
        text = " ".join(f"{s.text} {''.join(f'[{n}]' for n in s.citations)}" for s in sentences)
        timings["total"] = (time.perf_counter() - started) * 1000
        return Answer(
            question=question,
            language=language,
            text=text,
            sentences=sentences,
            citations=citations,
            refused=False,
            refusal_reason=None,
            confidence=confidence,
            disclaimer=disclaimer(language),
            rejected=checked.rejected,
            timings_ms=timings,
        )
