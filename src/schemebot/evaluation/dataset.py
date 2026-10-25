"""The labelled question set (data/eval/questions.jsonl).

Gold answers are recorded as pages of documents, not chunk ids, so the labels stay valid
when the chunker changes. A retrieved passage is relevant when it comes from a gold
document and its page range overlaps a gold page.
"""

from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from schemebot.ingest.models import Chunk

Group = Literal["en", "ta", "hi", "ta-Latn"]
GROUPS: tuple[Group, ...] = ("en", "ta", "hi", "ta-Latn")


class GoldPages(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    doc_id: str
    pages: list[int] = Field(min_length=1)


class EvalQuestion(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    group: Group
    question: str = Field(min_length=3)
    answerable: bool
    gold: list[GoldPages]
    reference: str
    fact: str | None = None
    status: Literal["draft", "verified"]

    @model_validator(mode="after")
    def _gold_matches_answerable(self) -> "EvalQuestion":
        if self.answerable != bool(self.gold):
            raise ValueError(f"{self.id}: answerable questions need gold pages, others none")
        return self


def load_questions(path: Path) -> list[EvalQuestion]:
    with path.open(encoding="utf-8") as file:
        questions = [EvalQuestion.model_validate_json(line) for line in file if line.strip()]
    duplicates = [qid for qid, n in Counter(q.id for q in questions).items() if n > 1]
    if duplicates:
        raise ValueError(f"duplicate question ids: {', '.join(duplicates)}")
    return questions


def pages_overlap(doc_id: str, page_start: int, page_end: int, gold: list[GoldPages]) -> bool:
    return any(
        g.doc_id == doc_id and any(page_start <= page <= page_end for page in g.pages) for g in gold
    )


def is_relevant(chunk: Chunk, gold: list[GoldPages]) -> bool:
    return pages_overlap(chunk.doc_id, chunk.page_start, chunk.page_end, gold)
