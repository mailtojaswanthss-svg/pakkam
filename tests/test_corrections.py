import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from schemebot.api.schemas import AskResponse
from schemebot.config import PROJECT_ROOT, Settings
from schemebot.generate.answer import Answer, Answerer
from schemebot.generate.guardrails import DraftSentence, check_answer
from schemebot.index.store import build_index, open_client
from schemebot.ingest.chunk import chunk_document
from schemebot.ingest.corrections import (
    CORRECTED,
    CorrectionError,
    OcrCorrection,
    apply_corrections,
    load_corrections,
)
from schemebot.ingest.extract import PageText
from schemebot.ingest.models import SourceDoc
from schemebot.ingest.pipeline import load_manifest, read_chunks, run_ingest
from schemebot.retrieve.hybrid import HybridRetriever
from schemebot.retrieve.retriever import Retriever
from tests.conftest import FakeEncoder, FakeReranker, make_chunk
from tests.test_answer import THRESHOLD, FakeLlm, passage_number, sentences
from tests.test_pipeline import data_dir, make_entry, write_manifest  # noqa: F401

PENN_PAGE = "புதுமைப்பெண் திட்டம்\nமாதந்தோறும் ரூ.4,000/- வங்கி கணக்கில் செலுத்தப்படுகிறது."


def correction(confirmed: bool = True, **changes: object) -> OcrCorrection:
    fields: dict[str, object] = {
        "doc_id": "penn-ta",
        "page": 2,
        "ocr_reads": "ரூ.4,000",
        "pdf_shows": "ரூ.1,000",
        "confirmed_by": "Jaswanth" if confirmed else None,
        "confirmed_on": date(2026, 10, 27) if confirmed else None,
    }
    return OcrCorrection.model_validate({**fields, **changes})


def pages() -> list[PageText]:
    return [PageText(1, "Introduction", "ocr"), PageText(2, PENN_PAGE, "ocr")]


# The real file


def test_project_corrections_file_is_valid_and_names_real_documents() -> None:
    corrections = load_corrections(PROJECT_ROOT / "data" / "corrections.json")
    doc_ids = {doc.doc_id for doc in load_manifest(PROJECT_ROOT / "data" / "sources.json")}

    assert corrections
    assert {c.doc_id for c in corrections} <= doc_ids


def test_no_correction_is_confirmed_until_a_person_checks_the_pdf() -> None:
    # Flip this test only together with an entry that a person has checked by eye.
    corrections = load_corrections(PROJECT_ROOT / "data" / "corrections.json")
    assert not any(c.confirmed for c in corrections)


def test_missing_file_means_no_corrections(tmp_path: Path) -> None:
    assert load_corrections(tmp_path / "corrections.json") == []


# The entry rules


def test_confirmed_entry_needs_page_and_date() -> None:
    with pytest.raises(ValidationError, match="page and date"):
        correction(page=None)
    with pytest.raises(ValidationError, match="page and date"):
        correction(confirmed_on=None)


def test_blank_name_does_not_count_as_confirmed() -> None:
    with pytest.raises(ValidationError, match="blank"):
        correction(confirmed_by="  ")


def test_unconfirmed_entry_may_leave_the_page_open() -> None:
    assert not correction(confirmed=False, page=None).confirmed


# Ingestion


def test_confirmed_fix_replaces_the_misreading_and_marks_the_page() -> None:
    fixed, applied = apply_corrections("penn-ta", pages(), [correction()])

    assert "ரூ.1,000/-" in fixed[1].text
    assert "4,000" not in fixed[1].text
    assert fixed[1].method == CORRECTED
    assert fixed[0] == pages()[0]  # other pages untouched
    assert applied == [correction()]


def test_unconfirmed_entry_leaves_the_text_alone() -> None:
    fixed, applied = apply_corrections("penn-ta", pages(), [correction(confirmed=False)])

    assert fixed == pages()
    assert applied == []


def test_entry_for_another_document_is_ignored() -> None:
    fixed, applied = apply_corrections("other-ta", pages(), [correction()])

    assert fixed == pages()
    assert applied == []


@pytest.mark.parametrize(
    "changes, message",
    [
        ({"ocr_reads": "ரூ.9,000"}, "found 0 times"),
        ({"ocr_reads": "ம"}, "times, expected exactly once"),
        ({"page": 7}, "page 7 does not exist"),
    ],
)
def test_fix_that_does_not_match_exactly_once_stops_ingestion(
    changes: dict[str, object], message: str
) -> None:
    with pytest.raises(CorrectionError, match=message):
        apply_corrections("penn-ta", pages(), [correction(**changes)])


def test_chunk_with_a_fixed_page_is_marked_even_next_to_plain_ocr() -> None:
    doc = SourceDoc(
        doc_id="penn-ta",
        scheme="Pudhumai Penn",
        file="penn.pdf",
        source_url="https://example.gov.in/penn.pdf",
        language="ta",
        accessed=date(2026, 10, 25),
    )
    fixed, _ = apply_corrections("penn-ta", pages(), [correction()])

    [chunk] = chunk_document(doc, fixed)

    assert chunk.extraction == CORRECTED


def test_ingest_applies_confirmed_fixes_and_reports_them(data_dir: Path) -> None:  # noqa: F811
    write_manifest(data_dir, [make_entry("test-guidelines-en", "guidelines.pdf")])
    fix = correction(doc_id="test-guidelines-en", page=1, ocr_reads="2.5", pdf_shows="3.5")
    (data_dir / "corrections.json").write_text(
        json.dumps([fix.model_dump(mode="json")]), encoding="utf-8"
    )

    report = run_ingest(Settings(_env_file=None, data_dir=data_dir), ocr_factory=None)

    chunks = read_chunks(data_dir / "processed" / "chunks.jsonl")
    eligibility = next(c for c in chunks if c.section == "Eligibility")
    assert "3.5 lakh" in eligibility.text
    assert eligibility.extraction == CORRECTED
    assert report.corrections_applied == ["test-guidelines-en p1: 2.5 -> 3.5"]


def test_ingest_refuses_corrections_for_unknown_documents(data_dir: Path) -> None:  # noqa: F811
    write_manifest(data_dir, [make_entry("test-guidelines-en", "guidelines.pdf")])
    (data_dir / "corrections.json").write_text(
        json.dumps([correction(doc_id="no-such-doc").model_dump(mode="json")]), encoding="utf-8"
    )

    with pytest.raises(CorrectionError, match="no-such-doc"):
        run_ingest(Settings(_env_file=None, data_dir=data_dir), ocr_factory=None)


# Answer time


def test_guardrail_removes_a_sentence_using_a_known_misread_number() -> None:
    passages = ["Pudhumai Penn pays Rs.4,000 a month to girl students in college."]
    draft = DraftSentence("Pudhumai Penn pays Rs.4,000 a month.", [1])

    result = check_answer([draft], passages, misread_numbers=[{"4000"}])

    assert result.kept == []
    assert [r.reason for r in result.rejected] == ["known_ocr_error"]


def test_guardrail_keeps_other_numbers_from_the_same_passage() -> None:
    passages = ["Pudhumai Penn pays Rs.4,000 a month to students of class 6 to 12."]
    draft = DraftSentence("Students of class 6 to 12 can apply.", [1])

    result = check_answer([draft], passages, misread_numbers=[{"4000"}])

    assert result.kept == [draft]


def answer_from(
    corpus_texts: dict[str, str], llm: FakeLlm, corrections: list[OcrCorrection]
) -> Answer:
    client = open_client(None)
    encoder = FakeEncoder()
    build_index(client, "test", [make_chunk(i, t) for i, t in corpus_texts.items()], encoder)
    retriever = Retriever(
        HybridRetriever(client, "test", encoder, 10), FakeReranker(), candidates=5, keep=3
    )
    answerer = Answerer(retriever, llm, None, THRESHOLD, corrections=corrections)
    return answerer.answer("How much does Pudhumai Penn pay per month?")


UNCONFIRMED_PENN = [correction(confirmed=False, ocr_reads="Rs 4000", pdf_shows="Rs 1000")]
PENN_CORPUS = {
    "penn-ta-001": "Pudhumai Penn pays Rs 4000 per month to girl students.",
    "penn-en-001": "Pudhumai Penn pays Rs 1000 per month to girl students.",
}


def test_unconfirmed_misreading_cannot_reach_an_answer() -> None:
    llm = FakeLlm(
        lambda prompt: sentences(
            ("Pudhumai Penn pays Rs 4000 per month.", [passage_number(prompt, "Rs 4000")])
        )
    )

    answer = answer_from(PENN_CORPUS, llm, UNCONFIRMED_PENN)

    assert answer.refused
    assert [r.reason for r in answer.rejected] == ["known_ocr_error"]


def test_right_amount_from_the_same_document_is_still_answered() -> None:
    corpus = {"penn-ta-001": "Pudhumai Penn pays Rs 4000 per month; apply by 30 June."}
    llm = FakeLlm(sentences(("Apply by 30 June.", [1])))

    answer = answer_from(corpus, llm, UNCONFIRMED_PENN)

    assert not answer.refused


def test_corrected_passage_is_flagged_in_the_api_response() -> None:
    chunk = make_chunk("penn-ta-001", "Pudhumai Penn pays Rs 1000 per month to girl students.")
    corrected = chunk.model_copy(update={"extraction": CORRECTED})
    client = open_client(None)
    encoder = FakeEncoder()
    build_index(client, "test", [corrected], encoder)
    retriever = Retriever(
        HybridRetriever(client, "test", encoder, 10), FakeReranker(), candidates=5, keep=3
    )
    llm = FakeLlm(sentences(("Pudhumai Penn pays Rs 1000 per month.", [1])))

    answer = Answerer(retriever, llm, None, THRESHOLD).answer(
        "How much does Pudhumai Penn pay per month?"
    )
    body = AskResponse.from_answer(answer).model_dump()

    assert [c["ocr_corrected"] for c in body["citations"]] == [True]
