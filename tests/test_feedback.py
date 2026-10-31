"""Unit tests for citizen feedback loop (POST /feedback)."""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from schemebot.api.main import create_app
from schemebot.generate.answer import Answer


class FakeService:
    def answer(self, question: str, voice_mode: bool = False) -> Answer:
        raise NotImplementedError


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    app = create_app(lambda: FakeService(), log_dir=tmp_path)
    with TestClient(app) as test_client:
        yield test_client


def test_post_feedback_default_stores_no_text(client: TestClient, tmp_path: Path) -> None:
    # By default, include_text is False; question and reason must NOT be stored
    payload = {
        "question": "Pudhumai Penn amount evalo?",
        "status": "SUPPORTED",
        "thumbs": "up",
        "reason": "Great answer",
        "timings_ms": {"total": 420.5},
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recorded"] is True

    fb_path = tmp_path / "feedback.jsonl"
    assert fb_path.is_file()
    lines = fb_path.read_text(encoding="utf-8").strip().split("\n")
    last_entry = json.loads(lines[-1])
    # Verify no text is logged
    assert "question" not in last_entry
    assert "reason" not in last_entry
    assert last_entry["include_text"] is False
    assert last_entry["status"] == "SUPPORTED"
    assert last_entry["thumbs"] == "up"
    assert last_entry["language"] == "ta"


def test_post_feedback_opt_in_stores_text(client: TestClient, tmp_path: Path) -> None:
    payload = {
        "question": "CMCHIS annual income limit?",
        "status": "INSUFFICIENT_EVIDENCE",
        "thumbs": "down",
        "reason": "Official document says 1.2 lakh, answer was refused.",
        "timings_ms": {"total": 350.0},
        "include_text": True,
        "language": "en",
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["recorded"] is True

    fb_path = tmp_path / "feedback.jsonl"
    lines = fb_path.read_text(encoding="utf-8").strip().split("\n")
    last_entry = json.loads(lines[-1])
    assert last_entry["include_text"] is True
    assert last_entry["question"] == "CMCHIS annual income limit?"
    assert last_entry["reason"] == "Official document says 1.2 lakh, answer was refused."
    assert last_entry["language"] == "en"
