"""Unit tests for Step 7: Gnani-centred voice uncertainty confirmation."""

import datetime
from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from schemebot.api.main import create_app
from schemebot.generate.answer import Answer, AnswerSentence, Citation
from schemebot.generate.contacts import Contact
from schemebot.ingest.models import Chunk
from schemebot.retrieve.retriever import RetrievedPassage
from tests.test_stt import make_wav


def _short_wav() -> bytes:
    return make_wav(1.0)


def _make_mock_service(confidence: float, scheme: str = "Pudhumai Penn") -> MagicMock:
    chunk = Chunk(
        chunk_id=f"{scheme.lower().replace(' ', '-')}:p1:c0",
        doc_id="pudhumai-penn-go",
        scheme=scheme,
        source_url="https://tnsocialwelfare.tn.gov.in",
        page_start=1,
        page_end=1,
        section="Assistance",
        language="ta",
        text="Sample scheme details.",
        extraction="original",
        doc_date=datetime.date(2024, 1, 1),
    )
    passage = RetrievedPassage(chunk=chunk, relevance=confidence)
    ans = Answer(
        question="general question",
        language="ta",
        text="மாதம் ₹1,000 உதவித்தொகை வழங்கப்படுகிறது. [1]",
        sentences=[AnswerSentence("மாதம் ₹1,000 உதவித்தொகை வழங்கப்படுகிறது.", [1])],
        citations=[
            Citation(
                1,
                "pudhumai-penn-go",
                scheme,
                1,
                1,
                "https://tnsocialwelfare.tn.gov.in",
                "மாதம் ₹1,000 உதவித்தொகை வழங்கப்படுகிறது.",
            )
        ],
        refused=False,
        refusal_reason=None,
        confidence=confidence,
        disclaimer="தகவலுக்காக மட்டுமே.",
        contact=Contact(
            scheme=scheme,
            helpline="181",
            helpline_source="tn-social-welfare",
            website="https://tnsocialwelfare.tn.gov.in",
        ),
        candidate_schemes=[scheme],
        passages=[passage],
        timings_ms={"retrieval": 40.0, "generation": 900.0, "total": 940.0},
    )
    svc = MagicMock()
    svc.answer.return_value = ans
    return svc


class FakeStep7Stt:
    def __init__(self, transcript: str, confidence: float | None = None) -> None:
        self.transcript = transcript
        self.last_confidence = confidence

    def transcribe(self, audio: bytes, filename: str, language_code: str) -> str:
        return self.transcript


def test_voice_uncertain_retrieval_score_triggers_confirmation(tmp_path: Path) -> None:
    """When retrieval confidence is in [0.30, 0.40], trigger uncertainty confirmation."""
    svc = _make_mock_service(confidence=0.35, scheme="Pudhumai Penn")
    stt = FakeStep7Stt("pudhumai penn", confidence=0.90)

    app = create_app(lambda: svc, build_stt=lambda: stt, log_dir=tmp_path)
    with TestClient(app) as client:
        resp = client.post(
            "/ask/voice",
            files={"audio": ("q.wav", _short_wav(), "audio/wav")},
            data={"language": "ta"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_confirmation"] is True
        assert data["confirmation_text"] == "நான் Pudhumai Penn என்று கேட்டேன். சரியா?"
        assert data["stt_confidence"] == 0.90


def test_voice_low_stt_confidence_triggers_confirmation(tmp_path: Path) -> None:
    """When STT confidence is < 0.60, trigger uncertainty confirmation even if score > 0.40."""
    svc = _make_mock_service(confidence=0.75, scheme="CMCHIS")
    stt = FakeStep7Stt("maruthuva kaapeedu", confidence=0.52)

    app = create_app(lambda: svc, build_stt=lambda: stt, log_dir=tmp_path)
    with TestClient(app) as client:
        resp = client.post(
            "/ask/voice",
            files={"audio": ("q.wav", _short_wav(), "audio/wav")},
            data={"language": "ta"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_confirmation"] is True
        assert data["confirmation_text"] == "நான் CMCHIS என்று கேட்டேன். சரியா?"
        assert data["stt_confidence"] == 0.52


def test_voice_high_confidence_no_confirmation(tmp_path: Path) -> None:
    """When both retrieval score (> 0.40) and STT confidence (>= 0.60) are high, no prompt."""
    svc = _make_mock_service(confidence=0.88, scheme="CMCHIS")
    stt = FakeStep7Stt("general question", confidence=0.95)

    app = create_app(lambda: svc, build_stt=lambda: stt, log_dir=tmp_path)
    with TestClient(app) as client:
        resp = client.post(
            "/ask/voice",
            files={"audio": ("q.wav", _short_wav(), "audio/wav")},
            data={"language": "ta"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["confirmation_text"] is None
        assert data["stt_confidence"] == 0.95


def test_voice_under_3_words_rule_dropped(tmp_path: Path) -> None:
    """Under 3 words does NOT trigger confirmation when scores are high."""
    # 2-word query: "pudhumai penn"
    svc = _make_mock_service(confidence=0.85, scheme="Pudhumai Penn")
    stt = FakeStep7Stt("general question", confidence=0.92)

    app = create_app(lambda: svc, build_stt=lambda: stt, log_dir=tmp_path)
    with TestClient(app) as client:
        resp = client.post(
            "/ask/voice",
            files={"audio": ("q.wav", _short_wav(), "audio/wav")},
            data={"language": "ta"},
        )
        assert resp.status_code == 200
        data = resp.json()
        # Confirmation text should NOT be set because scores are confident
        assert data["confirmation_text"] is None
