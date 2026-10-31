"""Question -> cited answer, or an honest refusal.

Order of decisions:
1. Retrieve. If the best passage is not relevant enough, refuse without calling the LLM.
2. Ask the LLM to answer from the passages only, as cited sentences.
3. Run the guardrail; drop any sentence the passages do not back. Refuse if none remain.
"""

import logging
import re
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Literal

from schemebot.generate.contacts import Contact
from schemebot.generate.guardrails import (
    DraftSentence,
    RejectedSentence,
    check_answer,
    numbers_in,
)
from schemebot.generate.llm import JsonLlm, LlmDeclinedError, LlmUnavailableError, parse_reply
from schemebot.generate.messages import (
    RefusalReason,
    clarification_text,
    contact_text,
    contains_pii,
    disclaimer,
    refusal_text,
)
from schemebot.generate.prompt import (
    ANSWER_SCHEMA,
    SYSTEM_PROMPT,
    VOICE_SYSTEM_PROMPT,
    AnswerReply,
    build_user_message,
)
from schemebot.ingest.corrections import CORRECTED, OcrCorrection
from schemebot.ingest.langid import Language, detect_language
from schemebot.ingest.models import Chunk
from schemebot.retrieve.retriever import RetrievalResult, RetrievedPassage, Retriever
from schemebot.text import clean_query

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
class FollowUp:
    """What the page remembers from the previous turn, so "and how do I apply?" works.

    Nothing here is stored on the server; the page sends it with the next question."""

    question: str | None = None
    scheme: str | None = None


_NAMES_A_SCHEME = re.compile(r"\b(scheme|thittam|yojana|yojna)\b|திட்ட|योजना", re.IGNORECASE)

RETRIEVAL_REUSE_S = 120.0
"""How long a search result is kept so /ask can reuse the one /ask/sources just ran."""
RETRIEVAL_REUSE_MAX = 64


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
    contact: Contact | None = None
    """On a refusal about a scheme we hold documents for: its official contact."""
    passages: list[RetrievedPassage] = field(default_factory=list)
    """Retrieved passages, populated on fallback when model is unavailable."""
    path: Literal["rag", "fact_card", "fallback", "semantic_cache", "guardrail"] = "rag"
    """The pipeline path that produced this answer."""
    status: Literal[
        "SUPPORTED",
        "INSUFFICIENT_EVIDENCE",
        "MODEL_UNAVAILABLE",
        "needs_clarification",
        "PII_DETECTED",
        "UNSUPPORTED_LANGUAGE",
    ] = "SUPPORTED"
    """Status: SUPPORTED, INSUFFICIENT_EVIDENCE, MODEL_UNAVAILABLE, or needs_clarification."""
    understood_query: str | None = None
    """The cleaned, normalized query understood by the system."""
    candidate_schemes: list[str] = field(default_factory=list)
    """Candidate schemes when query is near-threshold or ambiguous."""


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
    def preload(self) -> None:
        """Preloads and warms up retrieval models to eliminate cold-start latency."""
        if hasattr(self._retriever, "retrieve"):
            try:
                self._retriever.retrieve("warmup")
                logger.info("Retriever models preloaded and warmed up successfully.")
            except Exception as exc:
                logger.debug("Preload retrieve skipped or failed: %s", exc)

    def __init__(
        self,
        retriever: Retriever,
        llm: JsonLlm,
        verifier: JsonLlm | None,
        refusal_threshold: float,
        contacts: dict[str, Contact] | None = None,
        corrections: list[OcrCorrection] | None = None,
        fact_cards: Any | None = None,
        alias_matcher: Any | None = None,
    ) -> None:
        self._retriever = retriever
        self._llm = llm
        self._verifier = verifier
        self._refusal_threshold = refusal_threshold
        self._contacts = contacts or {}
        # Confirmed fixes are applied at ingestion, but stay here too: until the index is
        # rebuilt the passage still holds the misreading.
        self._misread = misread_numbers_by_page(corrections or [])
        self._fact_cards = fact_cards
        self._alias_matcher = alias_matcher
        self._recent: OrderedDict[str, tuple[float, RetrievalResult]] = OrderedDict()
        self._recent_lock = threading.Lock()

    @property
    def retriever(self) -> Retriever:
        return self._retriever

    def search_query(self, question: str, follow_up: FollowUp | None = None) -> str:
        """The text actually searched: cleaned, with a known scheme alias spelled out, and,
        for a follow-up that names no scheme, the scheme of the previous answer."""
        search_q = clean_query(question)
        if self._alias_matcher is not None:
            search_q = self._alias_matcher.expand_query(search_q)
        scheme = follow_up.scheme if follow_up else None
        # A question that names a scheme of its own ("breakfast scheme enna") is a new
        # question, not a follow-up, even if that scheme is not in the alias table.
        names_scheme = bool(_NAMES_A_SCHEME.search(search_q)) or (
            self._alias_matcher is not None and self._alias_matcher.match(search_q) is not None
        )
        if scheme and not names_scheme and scheme.casefold() not in search_q.casefold():
            search_q = f"{search_q} {scheme}"
        return search_q

    def sources(self, question: str, follow_up: FollowUp | None = None) -> RetrievalResult:
        """Search only (no LLM): what /ask/sources shows while the answer is written. The
        result is kept briefly, so the /ask that follows does not search again."""
        return self._retrieve(self.search_query(question, follow_up))

    def _retrieve(self, search_q: str) -> RetrievalResult:
        now = time.monotonic()
        with self._recent_lock:
            hit = self._recent.get(search_q)
            if hit is not None and now - hit[0] <= RETRIEVAL_REUSE_S:
                self._recent.move_to_end(search_q)
                return RetrievalResult(hit[1].query, hit[1].passages, {"reused": 0.0})
        result = self._retriever.retrieve(search_q)
        with self._recent_lock:
            self._recent[search_q] = (now, result)
            self._recent.move_to_end(search_q)
            while len(self._recent) > RETRIEVAL_REUSE_MAX:
                self._recent.popitem(last=False)
        return result

    def answer(
        self, question: str, voice_mode: bool = False, follow_up: FollowUp | None = None
    ) -> Answer:
        timings: dict[str, float] = {}
        started = time.perf_counter()
        language = detect_language(question)

        # Privacy guardrail: intercept Aadhaar or mobile phone numbers before retrieval or LLM
        if contains_pii(question):
            timings["total"] = (time.perf_counter() - started) * 1000
            return Answer(
                question=question,
                language=language,
                text=refusal_text("pii_detected", language),
                sentences=[],
                citations=[],
                refused=True,
                refusal_reason="pii_detected",
                confidence=0.0,
                disclaimer=disclaimer(language),
                timings_ms=timings,
                status="PII_DETECTED",
                path="guardrail",
                understood_query=clean_query(question),
            )

        if language == "unknown":
            has_supported = any(
                0x0B80 <= ord(c) <= 0x0BFF
                or 0x0900 <= ord(c) <= 0x097F
                or ("a" <= c.lower() <= "z")
                for c in question
            )
            if not has_supported:
                timings["total"] = (time.perf_counter() - started) * 1000
                return Answer(
                    question=question,
                    language="en",
                    text=refusal_text("unsupported_language", "en"),
                    sentences=[],
                    citations=[],
                    refused=True,
                    refusal_reason="unsupported_language",
                    confidence=0.0,
                    disclaimer=disclaimer("en"),
                    timings_ms=timings,
                    status="UNSUPPORTED_LANGUAGE",
                    path="guardrail",
                    understood_query=clean_query(question),
                )

        # Step 4B: Deterministic cleanup & alias expansion (plus the previous scheme for a
        # follow-up that names none)
        cleaned_q = clean_query(question)
        search_q = self.search_query(question, follow_up)

        if self._fact_cards is not None:
            card_started = time.perf_counter()
            card, card_score = self._fact_cards.match(cleaned_q)
            card_ms = (time.perf_counter() - card_started) * 1000
            timings["fact_card_match"] = card_ms
            if card is not None:
                timings["total"] = (time.perf_counter() - started) * 1000
                contact = self._contacts.get(card.scheme)
                citation = Citation(
                    number=1,
                    doc_id=card.source_document,
                    scheme=card.scheme,
                    page_start=card.source_page,
                    page_end=card.source_page,
                    source_url=str(contact.website) if contact else "https://www.tn.gov.in",
                    text=card.answer_text,
                    language=card.language,
                    ocr_corrected=False,
                )
                sentence = AnswerSentence(text=card.answer_text, citations=[1])
                return Answer(
                    question=question,
                    language=language,
                    text=f"{card.answer_text} [1]",
                    sentences=[sentence],
                    citations=[citation],
                    refused=False,
                    refusal_reason=None,
                    confidence=card_score,
                    disclaimer=disclaimer(language),
                    timings_ms=timings,
                    contact=contact,
                    path="fact_card",
                    status="SUPPORTED",
                    understood_query=cleaned_q,
                )

        retrieval = self._retrieve(search_q)
        timings["retrieval"] = (time.perf_counter() - started) * 1000
        timings.update(retrieval.timings_ms)  # "search" and "rerank" inside "retrieval"
        confidence = retrieval.confidence

        def refuse(reason: RefusalReason, rejected: list[RejectedSentence] | None = None) -> Answer:
            timings["total"] = (time.perf_counter() - started) * 1000
            logger.info("refused (%s), confidence %.3f", reason, confidence)
            text = refusal_text(reason, language)
            contact: Contact | None = None
            if reason != "low_confidence" and retrieval.passages:
                contact = self._contacts.get(retrieval.passages[0].chunk.scheme)
                if contact:
                    text += " " + contact_text(
                        contact.scheme, contact.helpline, str(contact.website), language
                    )
            if reason == "service_unavailable":
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
                    contact=contact,
                    # Only passages that match the question well enough to answer it
                    # (at least the best one), so a garbled or off-topic page is not shown.
                    passages=[
                        p
                        for i, p in enumerate(retrieval.passages[:3])
                        if i == 0 or p.relevance >= self._refusal_threshold
                    ],
                    status="MODEL_UNAVAILABLE",
                    path="fallback",
                    understood_query=cleaned_q,
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
                contact=contact,
                passages=[],
                status="INSUFFICIENT_EVIDENCE",
                path="rag",
                understood_query=cleaned_q,
            )

        if confidence < self._refusal_threshold:
            # Step 4B: Near-threshold clarification band [0.30, 0.35)
            if confidence >= 0.30 and retrieval.passages:
                candidates = list(
                    dict.fromkeys(p.chunk.scheme for p in retrieval.passages if p.chunk.scheme)
                )[:2]
                if candidates:
                    timings["total"] = (time.perf_counter() - started) * 1000
                    contact = self._contacts.get(candidates[0])
                    return Answer(
                        question=question,
                        language=language,
                        text=clarification_text(candidates, language),
                        sentences=[],
                        citations=[],
                        refused=False,
                        refusal_reason=None,
                        confidence=confidence,
                        disclaimer=disclaimer(language),
                        timings_ms=timings,
                        contact=contact,
                        passages=retrieval.passages[:2],
                        path="rag",
                        status="needs_clarification",
                        understood_query=cleaned_q,
                        candidate_schemes=candidates,
                    )
            return refuse("low_confidence")

        prompt_to_use = VOICE_SYSTEM_PROMPT if voice_mode else SYSTEM_PROMPT
        passages = retrieval.passages[:3] if voice_mode else retrieval.passages
        passage_texts = [passage.chunk.text for passage in passages]
        misread = [_misread_in(passage.chunk, self._misread) for passage in passages]
        generation_started = time.perf_counter()
        try:
            reply = parse_reply(
                AnswerReply,
                self._llm.complete_json(
                    prompt_to_use,
                    build_user_message(
                        question,
                        language,
                        passages,
                        follow_up.question if follow_up else None,
                    ),
                    ANSWER_SCHEMA,
                ),
            )
            timings["llm_answer"] = (time.perf_counter() - generation_started) * 1000
            drafts = [DraftSentence(s.text.strip(), s.sources) for s in reply.sentences]
            if not reply.answerable or not drafts:
                return refuse("not_in_documents")

            # Voice optimization: skip LLM verifier if answer text has no numbers or dates
            has_numbers = any(bool(numbers_in(s.text)) for s in drafts)
            verifier_to_use = None if (voice_mode and not has_numbers) else self._verifier

            verify_started = time.perf_counter()
            checked = check_answer(drafts, passage_texts, verifier_to_use, misread)
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
        for kept_s in checked.kept:
            for source in kept_s.sources:
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
            status="SUPPORTED",
            understood_query=cleaned_q,
        )
