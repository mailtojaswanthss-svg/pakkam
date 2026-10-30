"""Verified fact cards: fast, deterministic, human-verified answers without LLM inference.

A fact card is served only when:
1. It is explicitly verified by a human (`verified_by` is set).
2. The user's question identifies the target scheme (via scheme name or recognized keywords).
3. Local bge-m3 embedding cosine similarity to the card's question examples exceeds `threshold`.

Responses served from fact cards have path="fact_card" and carry exact source page and date.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, TypeAdapter

logger = logging.getLogger(__name__)

CardField = Literal["amount", "who_qualifies", "documents", "how_to_apply"]

SCHEME_ALIASES: dict[str, list[str]] = {
    "Kalaignar Magalir Urimai Thittam": [
        "kmut",
        "magalir urimai",
        "மகளிர் உரிமை",
        "urimai thogai",
        "உரிமைத் தொகை",
        "kalaignar",
        "கலைஞர் மகளிர்",
    ],
    "PM-KISAN": ["pm kisan", "pmkisan", "pm-kisan", "kisan samman", "किसान सम्मान", "விவசாயி"],
    "Pradhan Mantri Ujjwala Yojana": ["pmuy", "ujjwala", "உஜ்வாலா", "उज्ज्वला", "gas connection", "lpg"],
    "Atal Pension Yojana": ["atal pension", "apy", "அடல் பென்ஷன்", "अटल पेंशन"],
    "Chief Minister's Comprehensive Health Insurance Scheme": [
        "cmchis",
        "மருத்துவக் காப்பீடு",
        "maruthuva",
        "காப்பீட்டு",
    ],
    "Pudhumai Penn": ["pudhumai penn", "புதுமைப்பெண்", "pudhumai pen", "moovalur ramamirtham"],
}


class FactCard(BaseModel):
    card_id: str
    scheme: str
    field: CardField
    language: str
    question_examples: list[str]
    answer_text: str
    source_document: str
    source_page: int
    document_date: str = "unknown"
    verified_by: str | None = None
    verified_on: str | None = None


def load_verified_cards(path: Path) -> list[FactCard]:
    """Read cards from JSON. Cards without a verified_by name are strictly filtered out."""
    if not path.is_file():
        return []
    raw = TypeAdapter(list[FactCard]).validate_json(path.read_bytes())
    # Rule: Cards without verified_by are never served
    verified = [c for c in raw if c.verified_by and c.verified_by.strip()]
    logger.info("Loaded %d fact cards (%d verified and eligible to serve)", len(raw), len(verified))
    return verified


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2, strict=False))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def scheme_matches(scheme: str, text: str) -> bool:
    t_lower = text.lower()
    if scheme.lower() in t_lower:
        return True
    aliases = SCHEME_ALIASES.get(scheme, [])
    return any(alias.lower() in t_lower for alias in aliases)


class FactCardMatcher:
    def __init__(
        self,
        cards: list[FactCard],
        encoder: Any | None = None,
        threshold: float = 0.85,
    ) -> None:
        self.cards = cards
        self._encoder = encoder
        self.threshold = threshold
        self._card_embeddings: list[tuple[FactCard, list[list[float]]]] = []
        if self._encoder and self.cards:
            self._precompute_embeddings()

    def set_encoder(self, encoder: Any) -> None:
        self._encoder = encoder
        if self.cards:
            self._precompute_embeddings()

    def _precompute_embeddings(self) -> None:
        if self._encoder is None:
            return
        self._card_embeddings = []
        for card in self.cards:
            if not card.question_examples:
                continue
            embs = self._encoder.encode(card.question_examples, is_query=True)
            self._card_embeddings.append((card, [e.dense for e in embs]))

    def match(self, question: str) -> tuple[FactCard | None, float]:
        """Returns the best matching verified card and cosine score
        if score >= threshold and scheme matches.
        """
        if not self.cards or self._encoder is None or not self._card_embeddings:
            return None, 0.0

        # Encode user question
        q_emb = self._encoder.encode([question], is_query=True)[0].dense

        best_card: FactCard | None = None
        best_score = 0.0

        for card, example_embs in self._card_embeddings:
            # Scheme must be identified in question text
            if not scheme_matches(card.scheme, question):
                continue

            for emb in example_embs:
                score = cosine_similarity(q_emb, emb)
                if score > best_score:
                    best_score = score
                    best_card = card

        if best_card is not None and best_score >= self.threshold:
            return best_card, best_score

        return None, best_score
