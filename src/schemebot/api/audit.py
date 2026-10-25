"""Request log for audit and evaluation, without personal data.

Questions can contain names, Aadhaar numbers or family details, so the log never stores
the question text: only a hash (to spot repeats), its length and language, and what the
system did with it - which passages it cited, whether it refused, and how long it took.
"""

import hashlib
import json
import threading
from datetime import UTC, datetime
from pathlib import Path

from schemebot.generate.answer import Answer

QUESTION_HASH_CHARS = 16


def question_hash(question: str) -> str:
    return hashlib.sha256(question.encode("utf-8")).hexdigest()[:QUESTION_HASH_CHARS]


class AuditLog:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, request_id: str, answer: Answer) -> None:
        entry = {
            "time": datetime.now(UTC).isoformat(timespec="seconds"),
            "request_id": request_id,
            "question_hash": question_hash(answer.question),
            "question_chars": len(answer.question),
            "language": answer.language,
            "refused": answer.refused,
            "refusal_reason": answer.refusal_reason,
            "confidence": round(answer.confidence, 4),
            "cited": [f"{c.doc_id}:p{c.page_start}" for c in answer.citations],
            "sentences": len(answer.sentences),
            "removed_by_guardrail": [r.reason for r in answer.rejected],
            "timings_ms": {k: round(v, 1) for k, v in answer.timings_ms.items()},
        }
        line = json.dumps(entry, ensure_ascii=False)
        with self._lock, self._path.open("a", encoding="utf-8") as file:
            file.write(line + "\n")
