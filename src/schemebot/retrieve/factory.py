"""Builds a ready-to-use Retriever from settings (loads both models, opens the index)."""

from schemebot.config import Settings
from schemebot.index.embed import BgeM3Encoder
from schemebot.index.store import open_client
from schemebot.retrieve.hybrid import HybridRetriever
from schemebot.retrieve.rerank import BgeReranker
from schemebot.retrieve.retriever import Retriever


class IndexMissingError(RuntimeError):
    pass


def build_retriever(
    settings: Settings, use_reranker: bool = True, gloss_tanglish: bool | None = None
) -> Retriever:
    """`gloss_tanglish=None` follows the setting; the evaluation can force it off."""
    client = open_client(settings.index_dir)
    if not client.collection_exists(settings.qdrant_collection):
        raise IndexMissingError(
            f"No index at {settings.index_dir}. Run `python -m schemebot.index` first."
        )
    encoder = BgeM3Encoder(settings.embedding_model, settings.embed_batch_size)
    return Retriever(
        HybridRetriever(
            client,
            settings.qdrant_collection,
            encoder,
            candidates_per_method=settings.retrieval_top_k,
        ),
        BgeReranker(settings.reranker_model) if use_reranker else None,
        candidates=settings.retrieval_top_k,
        keep=settings.rerank_top_k,
        gloss_tanglish=settings.gloss_tanglish if gloss_tanglish is None else gloss_tanglish,
    )
