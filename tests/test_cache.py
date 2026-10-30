"""Unit tests for SemanticCache sub-50ms verified answer retrieval."""

from pathlib import Path

from schemebot.generate.cache import CacheEntry, SemanticCache, cosine_similarity


def test_cosine_similarity() -> None:
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert cosine_similarity(v1, v2) == 1.0
    assert cosine_similarity(v1, v3) == 0.0
    assert cosine_similarity([], []) == 0.0


def test_semantic_cache_hit_and_miss(tmp_path: Path) -> None:
    entry = CacheEntry(
        question="Pudhumai Penn thittam amount?",
        embedding=[0.9, 0.1, 0.0],
        answer_text="Under Pudhumai Penn, eligible girl students receive Rs. 1,000 per month.",
        scheme="Pudhumai Penn Scheme",
        language="en",
        doc_id="pudhumai-penn-go",
        page=2,
        source_url="https://www.tn.gov.in",
        disclaimer="Official Government Scheme",
    )
    cache = SemanticCache([entry], threshold=0.95)

    # Identical or near-identical vector hit
    hit = cache.lookup([0.89, 0.11, 0.0])
    assert hit is not None
    assert hit.similarity >= 0.95
    assert hit.entry.scheme == "Pudhumai Penn Scheme"
    assert hit.duration_ms >= 0.0

    # Convert to Answer
    ans = cache.to_answer(hit, "What is Pudhumai Penn amount?")
    assert ans.status == "SUPPORTED"
    assert ans.path == "semantic_cache"
    assert len(ans.citations) == 1
    assert "Rs. 1,000" in ans.text

    # Completely different vector miss
    miss = cache.lookup([0.0, 0.0, 1.0])
    assert miss is None


def test_semantic_cache_persistence(tmp_path: Path) -> None:
    p = tmp_path / "cache.json"
    entry = CacheEntry(
        question="PM Kisan annual amount",
        embedding=[0.5, 0.5, 0.0],
        answer_text="PM-KISAN provides Rs. 6,000 per year in 3 installments.",
        scheme="PM-KISAN",
        language="en",
        doc_id="pmkisan-doc",
        page=1,
        source_url="https://pmkisan.gov.in",
        disclaimer="Official Scheme",
    )
    cache = SemanticCache([entry])
    cache.save(p)

    loaded = SemanticCache.load(p)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].scheme == "PM-KISAN"
