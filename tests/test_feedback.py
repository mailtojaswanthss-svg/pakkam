"""Unit tests for citizen feedback loop (POST /feedback)."""

import json
from pathlib import Path
from typing import Iterator
from fastapi.testclient import TestClient
import pytest

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


def test_post_feedback(client: TestClient, tmp_path: Path) -> None:
    payload = {
        "question": "Pudhumai Penn amount evalo?",
        "status": "SUPPORTED",
        "thumbs": "up",
        "reason": None,
        "timings_ms": {"total": 420.5},
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recorded"] is True

    fb_path = Path("logs/feedback.jsonl")
    assert fb_path.is_file()
    lines = fb_path.read_text(encoding="utf-8").strip().split("\n")
    last_entry = json.loads(lines[-1])
    assert last_entry["question"] == "Pudhumai Penn amount evalo?"
    assert last_entry["thumbs"] == "up"


def test_post_feedback_with_reason(client: TestClient) -> None:
    payload = {
        "question": "CMCHIS annual income limit?",
        "status": "INSUFFICIENT_EVIDENCE",
        "thumbs": "down",
        "reason": "Official document says 1.2 lakh, answer was refused.",
        "timings_ms": {"total": 350.0},
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["recorded"] is True
