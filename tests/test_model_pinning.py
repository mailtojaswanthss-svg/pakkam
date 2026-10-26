import sys
import types

import pytest
from pydantic import ValidationError

from schemebot.config import Settings
from schemebot.index.embed import UNUSED_MODEL_FILES, model_source

COMMIT = "5617a9f61b028005a4858fdac845db406aefb181"


def test_unpinned_model_loads_by_name() -> None:
    assert model_source("BAAI/bge-m3", None) == "BAAI/bge-m3"


def test_pinned_model_loads_exactly_that_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str, list[str]]] = []

    def snapshot_download(name: str, revision: str, ignore_patterns: list[str]) -> str:
        calls.append((name, revision, ignore_patterns))
        return f"/cache/{name}/snapshots/{revision}"

    fake = types.ModuleType("huggingface_hub")
    fake.snapshot_download = snapshot_download  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "huggingface_hub", fake)

    path = model_source("BAAI/bge-m3", COMMIT)

    assert path == f"/cache/BAAI/bge-m3/snapshots/{COMMIT}"
    assert calls == [("BAAI/bge-m3", COMMIT, UNUSED_MODEL_FILES)]


def test_revision_must_be_a_full_commit_hash() -> None:
    assert Settings(_env_file=None, embedding_revision=COMMIT).embedding_revision == COMMIT
    with pytest.raises(ValidationError):
        Settings(_env_file=None, embedding_revision="main")  # a branch moves; not a pin
    with pytest.raises(ValidationError):
        Settings(_env_file=None, reranker_revision=COMMIT[:7])


def test_empty_revision_means_latest() -> None:
    assert Settings(_env_file=None, reranker_revision="").reranker_revision is None
