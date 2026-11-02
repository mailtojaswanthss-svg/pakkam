"""Department dashboard and officer requests: counts only, contacts never shown."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from schemebot.api.dashboard import dashboard_stats
from schemebot.api.main import create_app


class NoService:
    def answer(self, question: str, voice_mode: bool = False) -> object:
        raise AssertionError("not used")


def client(tmp_path: Path) -> TestClient:
    return TestClient(
        create_app(
            lambda: NoService(), build_stt=lambda: None, build_tts=lambda: None, log_dir=tmp_path
        )
    )


def test_officer_request_is_stored_and_shown_without_the_contact(tmp_path: Path) -> None:
    with client(tmp_path) as c:
        response = c.post(
            "/officer-request",
            json={
                "question": "Can a widow apply twice?",
                "scheme": "KMUT",
                "contact": "98400 00000",
            },
        )
        assert response.status_code == 200
        assert response.json()["ticket"].startswith("PKM-")
        stats = c.get("/dashboard/stats").json()
    assert stats["officer_requests"]["open"] == 1
    [recent] = stats["officer_requests"]["recent"]
    assert recent["question"] == "Can a widow apply twice?"
    assert "contact" not in recent and "98400" not in json.dumps(stats)


def test_officer_request_refuses_id_numbers(tmp_path: Path) -> None:
    with client(tmp_path) as c:
        response = c.post(
            "/officer-request", json={"question": "My Aadhaar is 2345 6789 0123, am I eligible?"}
        )
    assert response.status_code == 422


def test_stats_count_answers_gaps_and_forwards(tmp_path: Path) -> None:
    audit = tmp_path / "requests.jsonl"
    rows = [
        {
            "language": "ta",
            "refused": False,
            "status": "SUPPORTED",
            "scheme": "PM-KISAN",
            "path": "fact_card",
        },
        {
            "language": "en",
            "refused": True,
            "refusal_reason": "not_in_documents",
            "scheme": "PM-KISAN",
        },
        {
            "kind": "forward",
            "overall": "wrong",
            "verdicts": ["contradicted"],
            "scam_signs": ["otp"],
        },
        {"kind": "transcript", "language_code": "ta-IN"},
    ]
    audit.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    stats = dashboard_stats(audit, tmp_path)

    assert stats["questions"] == 2 and stats["answered"] == 1 and stats["refused"] == 1
    assert stats["instant_signed_answers"] == 1 and stats["voice_questions"] == 1
    assert stats["gaps"] == {"PM-KISAN": 1}
    assert stats["forwards"]["scam_signs"] == {"otp": 1}
