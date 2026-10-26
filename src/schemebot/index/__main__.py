"""Build the search index: `uv run python -m schemebot.index`."""

import logging
import sys
import time

from schemebot.config import get_settings
from schemebot.index.embed import BgeM3Encoder, model_source
from schemebot.index.store import build_index, open_client
from schemebot.ingest.pipeline import CHUNKS_NAME, read_chunks


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    settings = get_settings()
    chunks_path = settings.processed_dir / CHUNKS_NAME
    if not chunks_path.is_file():
        print(
            f"No chunks at {chunks_path}. Run `python -m schemebot.ingest` first.", file=sys.stderr
        )
        return 1

    chunks = read_chunks(chunks_path)
    started = time.perf_counter()
    encoder = BgeM3Encoder(
        model_source(settings.embedding_model, settings.embedding_revision),
        settings.embed_batch_size,
    )
    count = build_index(
        open_client(settings.index_dir), settings.qdrant_collection, chunks, encoder
    )
    print(
        f"indexed {count} chunks into {settings.index_dir} in {time.perf_counter() - started:.0f}s"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
