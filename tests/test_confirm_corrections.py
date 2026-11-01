import importlib.util
from pathlib import Path

from schemebot.ingest.corrections import load_corrections

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "confirm", ROOT / "scripts" / "confirm_corrections.py"
)
assert spec and spec.loader
confirm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(confirm)


def test_entries_for_the_same_page_get_distinct_names() -> None:
    entries = [{"doc_id": "d", "page": 11}, {"doc_id": "d", "page": 11}, {"doc_id": "d", "page": 3}]
    assert list(confirm.names(entries)) == ["d:11", "d:11#2", "d:3"]


def test_committed_corrections_file_is_valid() -> None:
    """A bad entry would stop ingestion."""
    assert load_corrections(ROOT / "data" / "corrections.json")
