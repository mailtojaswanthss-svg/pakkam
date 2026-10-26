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

    def record(
        self, request_id: str, answer: Answer, extra_timings_ms: dict[str, float] | None = None
    ) -> None:
        timings = {**answer.timings_ms, **(extra_timings_ms or {})}
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
            "timings_ms": {k: round(v, 1) for k, v in timings.items()},
        }
        self._write(entry)

    def record_speech(self, request_id: str, chars: int, language_code: str, tts_ms: float) -> None:
        """A spoken answer: numbers only, never the text or the audio."""
        self._write(
            {
                "time": datetime.now(UTC).isoformat(timespec="seconds"),
                "request_id": request_id,
                "kind": "speech",
                "chars": chars,
                "language_code": language_code,
                "timings_ms": {"tts": round(tts_ms, 1)},
            }
        )

    def record_transcript(self, request_id: str, language_code: str, stt_ms: float) -> None:
        """Speech to text on its own: numbers only, never the transcript or the audio."""
        self._write(
            {
                "time": datetime.now(UTC).isoformat(timespec="seconds"),
                "request_id": request_id,
                "kind": "transcript",
                "language_code": language_code,
                "timings_ms": {"stt": round(stt_ms, 1)},
            }
        )

    def _write(self, entry: dict[str, object]) -> None:
        line = json.dumps(entry, ensure_ascii=False)
        with self._lock, self._path.open("a", encoding="utf-8") as file:
            file.write(line + "\n")
