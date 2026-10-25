"""Try retrieval by hand: `uv run python -m schemebot.retrieve "your question"`."""

import argparse
import sys

from schemebot.config import get_settings
from schemebot.retrieve.factory import IndexMissingError, build_retriever

PREVIEW_CHARS = 200


def main() -> int:
    parser = argparse.ArgumentParser(description="Show the passages retrieved for a question.")
    parser.add_argument("query")
    parser.add_argument("--mode", choices=["hybrid", "dense", "sparse"], default="hybrid")
    parser.add_argument("--no-rerank", action="store_true")
    args = parser.parse_args()

    try:
        retriever = build_retriever(get_settings(), use_reranker=not args.no_rerank)
    except IndexMissingError as error:
        print(error, file=sys.stderr)
        return 1

    result = retriever.retrieve(args.query, mode=args.mode)
    print(f"confidence: {result.confidence:.3f}")
    for rank, passage in enumerate(result.passages, start=1):
        chunk = passage.chunk
        preview = chunk.text[:PREVIEW_CHARS].replace("\n", " ")
        source = f"{chunk.doc_id} p{chunk.page_start} [{chunk.language}]"
        print(f"\n#{rank} {passage.relevance:.3f}  {source}")
        print(f"   {preview}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
