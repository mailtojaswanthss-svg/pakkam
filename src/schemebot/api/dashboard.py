"""What a scheme department would see: where citizens get stuck, without personal data.

Built only from the audit log (question hashes, never text) and the officer requests people
chose to send. It answers: which schemes people ask about, in which language; what the
official documents do not answer (refusals per scheme: the gaps to publish); which rumours
were checked and how they came out; and which questions are waiting for an officer.
"""

import json
import secrets
import threading
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

OFFICER_REQUESTS_NAME = "officer_requests.jsonl"
_lock = threading.Lock()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def add_officer_request(
    log_dir: Path, question: str, scheme: str | None, language: str, contact: str | None
) -> str:
    """Store a question the documents could not answer, for an officer to call back about.
    The person chose to send it, so the text is kept; the contact is never shown publicly."""
    ticket = f"PKM-{datetime.now(UTC):%y%m%d}-{secrets.token_hex(3).upper()}"
    entry = {
        "ticket": ticket,
        "time": datetime.now(UTC).isoformat(timespec="seconds"),
        "question": question,
        "scheme": scheme,
        "language": language,
        "contact": contact,
        "status": "open",
    }
    log_dir.mkdir(parents=True, exist_ok=True)
    with _lock, (log_dir / OFFICER_REQUESTS_NAME).open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return ticket


def dashboard_stats(audit_path: Path, log_dir: Path, recent: int = 10) -> dict[str, Any]:
    rows = _read_jsonl(audit_path)
    answers = [r for r in rows if "kind" not in r]
    forwards = [r for r in rows if r.get("kind") == "forward"]
    voice = [r for r in rows if r.get("kind") == "transcript"]
    answered = [r for r in answers if not r.get("refused") and r.get("status") == "SUPPORTED"]
    refused = [r for r in answers if r.get("refused")]
    gaps = Counter(
        r.get("scheme") or "Unknown scheme"
        for r in refused
        if r.get("refusal_reason") in ("low_confidence", "not_in_documents", "unsupported")
    )
    requests = _read_jsonl(log_dir / OFFICER_REQUESTS_NAME)
    return {
        "updated": datetime.now(UTC).isoformat(timespec="seconds"),
        "questions": len(answers),
        "answered": len(answered),
        "refused": len(refused),
        "instant_signed_answers": sum(1 for r in answers if r.get("path") == "fact_card"),
        "voice_questions": len(voice),
        "by_language": dict(Counter(r.get("language", "unknown") for r in answers).most_common()),
        "top_schemes": dict(
            Counter(r["scheme"] for r in answers if r.get("scheme")).most_common(8)
        ),
        "gaps": dict(gaps.most_common(8)),
        "forwards": {
            "checked": len(forwards),
            "overall": dict(Counter(r.get("overall") for r in forwards).most_common()),
            "claims": dict(
                Counter(v for r in forwards for v in r.get("verdicts", [])).most_common()
            ),
            "scam_signs": dict(
                Counter(s for r in forwards for s in r.get("scam_signs", [])).most_common()
            ),
        },
        "officer_requests": {
            "open": sum(1 for r in requests if r.get("status") == "open"),
            # Recent questions without the contact detail.
            "recent": [
                {k: r.get(k) for k in ("ticket", "time", "question", "scheme", "language")}
                for r in requests[-recent:][::-1]
            ],
        },
    }
