"""Second-stage scoring with a cross-encoder.

The first stage compares a query vector with passage vectors that were computed separately.
A cross-encoder reads the question and the passage together, which is much better at
judging whether the passage actually answers the question. It is too slow for the whole
corpus, so it only rescores the first stage's top candidates.
"""

from collections.abc import Sequence
from typing import Any, Protocol

MAX_PAIR_TOKENS = 1024
"""Query (<= 256 tokens) plus a chunk; Tamil OCR text is the most tokens per character."""
SCORE_BATCH = 16


class Reranker(Protocol):
    def score(self, query: str, passages: Sequence[str]) -> list[float]:
        """Relevance of each passage to the query, between 0 and 1."""
        ...


class BgeReranker:
    """bge-reranker-v2-m3 through transformers directly.

    FlagEmbedding's FlagReranker loads the weights in float32 and only halves them at the
    first call, which briefly needs ~2.3 GB of extra memory next to the embedding model and
    crashed runs on a 16 GB machine. Loading straight into float16 on the GPU avoids that.
    """

    def __init__(self, model_name: str) -> None:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self._torch: Any = torch
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self._device == "cuda" else torch.float32
        self._tokenizer: Any = AutoTokenizer.from_pretrained(model_name)
        self._model: Any = AutoModelForSequenceClassification.from_pretrained(
            model_name, dtype=dtype
        ).to(self._device)
        self._model.eval()

    def score(self, query: str, passages: Sequence[str]) -> list[float]:
        scores: list[float] = []
        torch = self._torch
        for start in range(0, len(passages), SCORE_BATCH):
            batch = passages[start : start + SCORE_BATCH]
            inputs = self._tokenizer(
                [[query, passage] for passage in batch],
                padding=True,
                truncation=True,
                max_length=MAX_PAIR_TOKENS,
                return_tensors="pt",
            ).to(self._device)
            with torch.no_grad():
                logits = self._model(**inputs).logits.view(-1).float()
            scores.extend(torch.sigmoid(logits).tolist())
        return scores
