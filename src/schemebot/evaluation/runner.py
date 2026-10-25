"""Runs the question set through retrieval and, when available, the full answer pipeline."""

import logging
import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor

from schemebot.evaluation.dataset import EvalQuestion, is_relevant, pages_overlap
from schemebot.evaluation.judge import FaithfulnessJudge
from schemebot.evaluation.metrics import QuestionResult
from schemebot.generate.answer import Answerer
from schemebot.generate.llm import LlmDeclinedError, LlmUnavailableError
from schemebot.retrieve.hybrid import SearchMode
from schemebot.retrieve.retriever import Retriever

logger = logging.getLogger(__name__)


def evaluate(
    questions: Sequence[EvalQuestion],
    retriever: Retriever,
    refusal_threshold: float,
    mode: SearchMode = "hybrid",
    answerer: Answerer | None = None,
    judge: FaithfulnessJudge | None = None,
    workers: int = 1,
) -> list[QuestionResult]:
    """Retrieval metrics always; answer metrics only when an `answerer` is given.

    Without an answerer, "refused" means the retrieval confidence was below the threshold,
    which is the first refusal check the full pipeline makes.
    """

    def run_one(question: EvalQuestion) -> QuestionResult:
        started = time.perf_counter()
        retrieval = retriever.retrieve(question.question, mode=mode)
        retrieval_ms = (time.perf_counter() - started) * 1000
        result = QuestionResult(
            id=question.id,
            group=question.group,
            answerable=question.answerable,
            status=question.status,
            retrieved=[f"{p.chunk.doc_id}:p{p.chunk.page_start}" for p in retrieval.passages],
            relevant=[is_relevant(p.chunk, question.gold) for p in retrieval.passages],
            confidence=retrieval.confidence,
            retrieval_ms=retrieval_ms,
            refused=retrieval.confidence < refusal_threshold,
        )

        if answerer is not None:
            answer = answerer.answer(question.question)
            result.refused = answer.refused
            result.refusal_reason = answer.refusal_reason
            result.answer = answer.text
            result.total_ms = answer.timings_ms.get("total")
            if question.answerable:
                result.citations_relevant = [
                    pages_overlap(c.doc_id, c.page_start, c.page_end, question.gold)
                    for c in answer.citations
                ]
            if judge is not None and not answer.refused:
                try:
                    result.sentences_supported = judge.supported(answer)
                except (LlmUnavailableError, LlmDeclinedError) as error:
                    # One failed grading call should not throw away the whole run.
                    logger.warning("judge failed on %s: %s", question.id, error)
                    result.judge_failed = True

        logger.info("%s done", question.id)
        return result

    # Several workers overlap the LLM calls; retrieval still takes turns on the GPU, so
    # retrieval latency in a parallel run includes waiting and is not representative.
    if workers <= 1:
        return [run_one(q) for q in questions]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(run_one, questions))
