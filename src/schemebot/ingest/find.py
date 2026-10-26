"""Find which pages of the extracted text contain a number or phrase.

    uv run python -m schemebot.ingest.find 14167 4400 "4,20,000"

Searches data/processed/chunks.jsonl (what OCR actually produced), so the page numbers can
go straight into data/corrections.json. Commas are ignored: "4,20,000" also finds "420000".
Prints document and pages only.
"""

import argparse
import sys
from collections.abc import Sequence

from schemebot.config import get_settings
from schemebot.ingest.models import Chunk
from schemebot.ingest.pipeline import CHUNKS_NAME, read_chunks
from schemebot.text import normalize_for_search


def _plain(text: str) -> str:
    return normalize_for_search(text).replace(",", "")


def find_pages(chunks: Sequence[Chunk], needle: str) -> list[tuple[str, int, int]]:
    """(doc_id, first page, last page) of each chunk containing `needle`, without repeats."""
    wanted = _plain(needle)
    found = {(c.doc_id, c.page_start, c.page_end) for c in chunks if wanted in _plain(c.text)}
    return sorted(found)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("texts", nargs="+", help="numbers or phrases to look for")
    args = parser.parse_args(argv)
    path = get_settings().processed_dir / CHUNKS_NAME
    if not path.is_file():
        print(f"No chunks at {path}. Run `python -m schemebot.ingest` first.", file=sys.stderr)
        return 1
    chunks = read_chunks(path)
    for text in args.texts:
        hits = find_pages(chunks, text)
        pages = [f"{doc} p{a}" if a == b else f"{doc} p{a}-{b}" for doc, a, b in hits]
        print(f"{text}: {', '.join(pages) if pages else 'not found'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
