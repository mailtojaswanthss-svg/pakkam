"""'Is this forward real?' (POST /check-forward) with fake models: no network."""

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from schemebot.api.main import create_app
from schemebot.generate.answer import Answer, AnswerSentence
from schemebot.generate.forward import ForwardChecker


def official(question: str, text: str | None) -> Answer:
    return Answer(
        question=question,
        language="en",
        text=text or "Not in the documents.",
        sentences=[AnswerSentence(text, [])] if text else [],
        citations=[],
        refused=text is None,
        refusal_reason=None if text else "low_confidence",
        confidence=0.9 if text else 0.1,
        disclaimer="Informational only.",
    )


class Service:
    answers = {
        "How much does Magalir Urimai pay?": "Rs.1,000 a month to women heads of families.",
        "Is there a Rs.5,000 gold coin?": None,
    }

    def answer(self, question: str, voice_mode: bool = False) -> Answer:
        return official(question, self.answers.get(question))


class Llm:
    """Splits the forward into two claims, then judges by the official amount."""

    def complete_json(self, system: str, user: str, schema: dict[str, object]) -> dict[str, Any]:
        if "forwarded on WhatsApp" in system:
            return {
                "claims": [
                    {
                        "claim": "Rs.4,000 every month for women",
                        "question": "How much does Magalir Urimai pay?",
                    },
                    {
                        "claim": "free Rs.5,000 gold coin",
                        "question": "Is there a Rs.5,000 gold coin?",
                    },
                ]
            }
        return {"verdict": "contradicted", "explanation": "The order says Rs.1,000 a month."}


def test_forward_with_a_wrong_amount_and_an_invented_claim() -> None:
    result = ForwardChecker(Service(), Llm()).check(
        "Rs.4,000 every month for women! Free gold coin!"
    )
    assert result.overall == "wrong"
    assert [c.verdict for c in result.claims] == ["contradicted", "not_in_documents"]
    assert "Rs.1,000" in result.claims[0].explanation


def test_check_forward_endpoint(tmp_path: Path) -> None:
    app = create_app(
        lambda: Service(),
        build_stt=lambda: None,
        build_tts=lambda: None,
        log_dir=tmp_path,
        build_forward_llm=Llm,
    )
    with TestClient(app) as client:
        response = client.post(
            "/check-forward", json={"message": "Rs.4,000 every month for women!"}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["overall"] == "wrong"
    assert data["claims"][0]["answer"]["sentences"][0]["text"].startswith("Rs.1,000")
