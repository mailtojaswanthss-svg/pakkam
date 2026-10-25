import json
import math
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from schemebot.config import PROJECT_ROOT
from schemebot.evaluation.dataset import EvalQuestion, GoldPages, is_relevant, load_questions
from schemebot.evaluation.judge import FaithfulnessJudge
from schemebot.evaluation.metrics import (
    QuestionResult,
    percentile,
    recall_at_k,
    reciprocal_rank,
    summarize,
)
from schemebot.evaluation.report import render
from schemebot.evaluation.runner import evaluate
from schemebot.generate.answer import Answer, AnswerSentence, Citation
from schemebot.index.store import build_index, open_client
from schemebot.ingest.models import Chunk
from schemebot.retrieve.hybrid import HybridRetriever
from schemebot.retrieve.retriever import Retriever
from tests.conftest import FakeEncoder, FakeReranker, make_chunk

GOLD = [GoldPages(doc_id="apy-en", pages=[1, 2])]


def question(qid: str, text: str, answerable: bool = True, group: str = "en") -> EvalQuestion:
    return EvalQuestion.model_validate(
        {
            "id": qid,
            "group": group,
            "question": text,
            "answerable": answerable,
            "gold": [g.model_dump() for g in GOLD] if answerable else [],
            "reference": "-",
            "status": "draft",
        }
    )


def result(**overrides: Any) -> QuestionResult:
    base: dict[str, Any] = dict(
        id="q", group="en", answerable=True, status="draft", retrieved=[], relevant=[],
        confidence=0.9, retrieval_ms=100.0, refused=False,
    )  # fmt: skip
    return QuestionResult(**(base | overrides))


# --- metrics -----------------------------------------------------------------------------


def test_recall_at_k_and_reciprocal_rank() -> None:
    relevant = [False, False, True, False]

    assert not recall_at_k(relevant, 1)
    assert recall_at_k(relevant, 5)
    assert reciprocal_rank(relevant) == pytest.approx(1 / 3)
    assert reciprocal_rank([False, False]) == 0.0


def test_percentile_uses_nearest_rank() -> None:
    values = [10.0, 20.0, 30.0, 40.0]

    assert percentile(values, 50) == 20.0
    assert percentile(values, 95) == 40.0
    assert math.isnan(percentile([], 50))


def test_summary_splits_answerable_and_unanswerable() -> None:
    results = [
        result(relevant=[True], refused=False),
        result(relevant=[False, True], refused=True),
        result(answerable=False, refused=True),
        result(answerable=False, refused=False),
    ]

    summary = summarize(results)

    assert (summary.answerable, summary.unanswerable) == (2, 2)
    assert summary.recall[1] == 0.5
    assert summary.mrr == pytest.approx(0.75)
    assert summary.correct_refusal == 0.5
    assert summary.false_refusal == 0.5
    assert math.isnan(summary.faithfulness)  # no answers were judged


# --- dataset -----------------------------------------------------------------------------


def test_relevance_needs_same_document_and_overlapping_page() -> None:
    assert is_relevant(make_chunk("apy-en-001", "x", page=2), GOLD)
    assert not is_relevant(make_chunk("apy-en-001", "x", page=3), GOLD)
    assert not is_relevant(make_chunk("apy-hi-001", "x", page=1), GOLD)


def test_answerable_question_without_gold_is_rejected() -> None:
    with pytest.raises(ValidationError, match="gold pages"):
        EvalQuestion.model_validate(
            {
                "id": "q1",
                "group": "en",
                "question": "Who can join?",
                "answerable": True,
                "gold": [],
                "reference": "-",
                "status": "draft",
            }  # fmt: skip
        )


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    line = question("q1", "Who can join APY?").model_dump_json()
    path = tmp_path / "questions.jsonl"
    path.write_text(f"{line}\n{line}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate"):
        load_questions(path)


def test_project_question_set_is_valid_and_points_at_real_documents() -> None:
    questions = load_questions(PROJECT_ROOT / "data" / "eval" / "questions.jsonl")
    sources = json.loads((PROJECT_ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    doc_ids = {source["doc_id"] for source in sources}

    assert {q.group for q in questions} == {"en", "ta", "hi", "ta-Latn"}
    assert all(g.doc_id in doc_ids for q in questions for g in q.gold)
    assert any(not q.answerable for q in questions)


# --- runner ------------------------------------------------------------------------------


@pytest.fixture
def retriever() -> Retriever:
    chunks = [
        make_chunk("apy-en-001", "Citizens aged 18 to 40 can join Atal Pension Yojana.", page=1),
        make_chunk("pmk-en-001", "PM-KISAN pays Rs 6000 per year to farmers.", page=4),
    ]
    client = open_client(None)
    encoder = FakeEncoder()
    build_index(client, "eval", chunks, encoder)
    return Retriever(HybridRetriever(client, "eval", encoder, 10), FakeReranker(), 5, 3)


def test_retrieval_only_run_scores_gold_pages_and_threshold_refusals(
    retriever: Retriever,
) -> None:
    questions = [
        question("q1", "Who can join Atal Pension Yojana aged 18 to 40?"),
        question("q2", "Quel temps fait-il?", answerable=False),
    ]

    results = evaluate(questions, retriever, refusal_threshold=0.3)

    assert results[0].relevant[0] is True
    assert results[0].retrieved[0] == "apy-en:p1"
    assert results[0].refused is False
    assert results[1].refused is True
    assert results[0].answer is None


class FakeAnswerer:
    def answer(self, question: str) -> Answer:
        citation = Citation(1, "apy-en", "APY", 1, 1, "https://pfrda.org.in", "Aged 18 to 40.")
        return Answer(
            question=question, language="en", text="Ages 18 to 40. [1]",
            sentences=[AnswerSentence("Ages 18 to 40.", [1])], citations=[citation],
            refused=False, refusal_reason=None, confidence=0.9, disclaimer="-",
            timings_ms={"total": 1200.0},
        )  # fmt: skip


class FakeJudgeLlm:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def complete_json(self, system: str, user: str, schema: dict[str, object]) -> dict[str, Any]:
        self.messages.append(user)
        return {"verdicts": [{"sentence": 1, "supported": True, "reason": "stated"}]}


def test_full_run_records_citations_and_judged_sentences(retriever: Retriever) -> None:
    judge_llm = FakeJudgeLlm()

    [res] = evaluate(
        [question("q1", "Who can join Atal Pension Yojana aged 18 to 40?")],
        retriever,
        refusal_threshold=0.3,
        answerer=FakeAnswerer(),  # type: ignore[arg-type]
        judge=FaithfulnessJudge(judge_llm),
    )

    assert res.citations_relevant == [True]
    assert res.sentences_supported == [True]
    assert res.total_ms == 1200.0
    assert "Aged 18 to 40." in judge_llm.messages[0]  # the judge sees the cited passage


def test_judge_counts_skipped_sentences_as_unsupported() -> None:
    answer = FakeAnswerer().answer("q")
    answer.sentences.append(AnswerSentence("Second claim.", [1]))

    verdicts = FaithfulnessJudge(FakeJudgeLlm()).supported(answer)

    assert verdicts == [True, False]


# --- report ------------------------------------------------------------------------------


def test_report_warns_about_drafts_and_shows_each_group() -> None:
    results = [result(group="en", relevant=[True]), result(group="ta", relevant=[False])]

    report = render(results, {"Mode": "retrieval only"}, full=False)

    assert "unverified drafts" in report
    assert "| English |" in report and "| Tamil |" in report
    assert "Faithfulness" not in report


def test_chunk_fixture_type() -> None:
    assert isinstance(make_chunk("a-001", "x"), Chunk)
