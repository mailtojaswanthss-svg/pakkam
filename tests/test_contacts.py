import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from schemebot.config import PROJECT_ROOT
from schemebot.generate.answer import Answerer
from schemebot.generate.contacts import Contact, load_contacts
from schemebot.index.store import build_index, open_client
from schemebot.ingest.models import Chunk
from schemebot.retrieve.hybrid import HybridRetriever
from schemebot.retrieve.retriever import Retriever
from tests.conftest import FakeEncoder, FakeReranker
from tests.test_answer import THRESHOLD, FakeLlm

CONTACTS = {
    "Test Scheme": Contact(
        scheme="Test Scheme",
        helpline="1800 000 000",
        helpline_source="test-doc p1",
        website="https://example.gov.in",
    )
}


def answerer(corpus: list[Chunk], llm: FakeLlm) -> Answerer:
    client = open_client(None)
    encoder = FakeEncoder()
    build_index(client, "test", corpus, encoder)
    retriever = Retriever(HybridRetriever(client, "test", encoder, 10), FakeReranker(), 5, 3)
    return Answerer(retriever, llm, None, THRESHOLD, CONTACTS)


def test_on_topic_refusal_names_the_scheme_contact(corpus: list[Chunk]) -> None:
    llm = FakeLlm({"answerable": False, "sentences": []})

    answer = answerer(corpus, llm).answer("How much does PM-KISAN pay per year to farmers?")

    assert answer.refusal_reason == "not_in_documents"
    assert "1800 000 000" in answer.text
    assert "https://example.gov.in" in answer.text
    assert answer.contact == CONTACTS["Test Scheme"]


def test_off_topic_refusal_does_not_guess_a_scheme(corpus: list[Chunk]) -> None:
    # No word in common with the test passages, so the fake reranker scores it 0.
    answer = answerer(corpus, FakeLlm({})).answer("Quel temps fait-il aujourd'hui à Paris?")

    assert answer.refusal_reason == "low_confidence"
    assert "1800" not in answer.text
    assert answer.contact is None


def test_contact_text_is_in_the_question_language(corpus: list[Chunk]) -> None:
    llm = FakeLlm({"answerable": False, "sentences": []})

    answer = answerer(corpus, llm).answer("PM-KISAN farmers pay per year ku evlo panam kidaikum")

    assert answer.language == "ta-Latn"
    assert "call pannunga" in answer.text


def test_helpline_without_source_is_rejected() -> None:
    with pytest.raises(ValidationError, match="no source document"):
        Contact(scheme="X", helpline="1800 1", helpline_source=None, website="https://x.gov.in")


def test_missing_contacts_file_means_no_contacts(tmp_path: Path) -> None:
    assert load_contacts(tmp_path / "contacts.json") == {}


def test_project_contacts_match_schemes_in_the_source_list() -> None:
    contacts = load_contacts(PROJECT_ROOT / "data" / "contacts.json")
    sources = json.loads((PROJECT_ROOT / "data" / "sources.json").read_text(encoding="utf-8"))

    schemes = {source["scheme"] for source in sources}

    assert contacts, "data/contacts.json is empty"
    assert set(contacts) <= schemes


def test_helpline_release_check_fails_on_unverified_non_null(tmp_path: Path) -> None:
    from schemebot.generate.contacts import verify_helplines

    csv_file = tmp_path / "check.csv"
    csv_file.write_text(
        "scheme,helpline,source_url,verified_by,verification_date,notes\n"
        "Scheme A,1800-111-222,https://gov.in,,,unverified\n"
        "Scheme B,,https://gov.in,,,null is safe\n"
        "Scheme C,1800-333-444,https://gov.in,Verified Person,2026-10-30,verified\n",
        encoding="utf-8",
    )
    errors = verify_helplines(csv_file)
    assert len(errors) == 1
    assert "Scheme A" in errors[0]
    assert "verified_by" in errors[0]
