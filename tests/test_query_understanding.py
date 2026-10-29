"""Unit tests for query understanding, deterministic cleanup, and scheme aliases."""

from pathlib import Path

import pytest

from schemebot.retrieve.aliases import AliasMatcher
from schemebot.text import clean_query, normalize_tanglish, strip_fillers


def test_strip_fillers() -> None:
    assert strip_fillers("can you tell me pudhumai penn amount") == "pudhumai penn amount"
    assert strip_fillers("CMCHIS details sollu please") == "CMCHIS please"
    assert strip_fillers("atal pension yojana ke baare mein batao") == "atal pension yojana"
    # When query is only filler, return original query stripped
    assert strip_fillers("kya hai") == "kya hai"


def test_normalize_tanglish() -> None:
    norm = normalize_tanglish("ponnungalukku 1000 thittam kedaikkuma")
    assert "பெண்கள்" in norm
    assert "திட்டம்" in norm
    assert "கிடைக்குமா" in norm


def test_clean_query_combined() -> None:
    cleaned = clean_query("Please tell me pudhumai penn details sollu")
    assert "pudhumai penn" in cleaned
    assert "tell me" not in cleaned


@pytest.fixture
def alias_matcher() -> AliasMatcher:
    path = Path("data/scheme_aliases.json")
    return AliasMatcher.load(path)


def test_alias_matcher_exact(alias_matcher: AliasMatcher) -> None:
    res = alias_matcher.match("Tell me about Pudhumai Penn Scheme")
    assert res is not None
    assert res.canonical == "Pudhumai Penn Scheme"
    assert res.match_type == "exact"


def test_alias_matcher_tamil_alias(alias_matcher: AliasMatcher) -> None:
    res = alias_matcher.match("கலைஞர் மகளிர் உரிமைத் திட்டம் தகுதி என்ன?")
    assert res is not None
    assert res.canonical == "Kalaignar Magalir Urimai Thittam"
    assert res.match_type == "alias"


def test_alias_matcher_transliteration(alias_matcher: AliasMatcher) -> None:
    res = alias_matcher.match("who is eligible for magalir 1000?")
    assert res is not None
    assert res.canonical == "Kalaignar Magalir Urimai Thittam"
    assert res.match_type == "transliteration"


def test_alias_matcher_stt_slip(alias_matcher: AliasMatcher) -> None:
    # STT slip "pm kishan" -> PM-KISAN
    res = alias_matcher.match("apply for pm kishan samman")
    assert res is not None
    assert res.canonical == "PM-KISAN"
    assert res.match_type == "stt_slip"

    # STT slip "adult pension" -> Atal Pension Yojana
    res2 = alias_matcher.match("how to open adult pension account")
    assert res2 is not None
    assert res2.canonical == "Atal Pension Yojana"
    assert res2.match_type == "stt_slip"


def test_alias_matcher_query_expansion(alias_matcher: AliasMatcher) -> None:
    expanded = alias_matcher.expand_query("how much under apy scheme?")
    assert "Atal Pension Yojana" in expanded


def test_alias_matcher_suggest_candidates(alias_matcher: AliasMatcher) -> None:
    candidates = alias_matcher.suggest_candidates("pension and marriage assistance", top_k=2)
    assert len(candidates) > 0
    assert any("Pension" in c or "Marriage" in c for c in candidates)


def test_near_threshold_clarification() -> None:
    import datetime
    from typing import Any, cast

    from schemebot.generate.answer import Answerer
    from schemebot.generate.contacts import Contact
    from schemebot.ingest.models import Chunk
    from schemebot.retrieve.retriever import RetrievalResult, RetrievedPassage, Retriever
    chunk1 = Chunk(
        chunk_id="c1",
        doc_id="doc1",
        scheme="Pudhumai Penn Scheme",
        section="main",
        doc_date=datetime.date(2026, 1, 1),
        page_start=1,
        page_end=1,
        text="Sample text about higher education aid.",
        extraction="text",
        source_url="https://example.com/1",
        language="en",
    )
    chunk2 = Chunk(
        chunk_id="c2",
        doc_id="doc2",
        scheme="Kalaignar Magalir Urimai Thittam",
        section="main",
        doc_date=datetime.date(2026, 1, 1),
        page_start=1,
        page_end=1,
        text="Sample text about monthly basic income.",
        extraction="text",
        source_url="https://example.com/2",
        language="en",
    )

    class MockRetriever:
        def __init__(self, score: float) -> None:
            self.score = score

        def retrieve(self, query: str) -> RetrievalResult:
            p1 = RetrievedPassage(chunk=chunk1, relevance=self.score)
            p2 = RetrievedPassage(chunk=chunk2, relevance=self.score * 0.95)
            return RetrievalResult(
                query=query, passages=[p1, p2], timings_ms={"retrieval": 10.0}
            )


    class MockLlm:
        def complete_json(self, *args: object, **kwargs: object) -> object:
            raise RuntimeError("Should not be called for clarification")

    contacts = {
        "Pudhumai Penn Scheme": Contact(
            scheme="Pudhumai Penn Scheme",
            helpline="14417",
            helpline_source="Pudhumai Penn Helpline 14417",
            website="https://pudhumai.tn.gov.in",
        )
    }

    # Case 1: score = 0.32 in near-threshold band [0.30, 0.35)
    near_answerer = Answerer(
        retriever=cast(Retriever, MockRetriever(0.32)),
        llm=cast(Any, MockLlm()),
        verifier=None,
        refusal_threshold=0.35,
        contacts=contacts,
    )
    ans = near_answerer.answer("tell me about monthly college money for girls")
    assert ans.status == "needs_clarification"
    assert not ans.refused
    assert "Did you mean" in ans.text
    assert ans.candidate_schemes == ["Pudhumai Penn Scheme", "Kalaignar Magalir Urimai Thittam"]
    assert ans.understood_query is not None
    assert len(ans.passages) == 2

    # Case 2: score = 0.22 below 0.30 refusal bound
    far_answerer = Answerer(
        retriever=cast(Retriever, MockRetriever(0.22)),
        llm=cast(Any, MockLlm()),
        verifier=None,
        refusal_threshold=0.35,
        contacts=contacts,
    )
    ans_far = far_answerer.answer("totally random unrelated inquiry")
    assert ans_far.refused
    assert ans_far.refusal_reason == "low_confidence"
    assert ans_far.status == "INSUFFICIENT_EVIDENCE"
