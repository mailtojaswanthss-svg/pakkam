"""API Contract Verification Tests.

Validates that real server endpoints and every documented sample payload in
docs/API_CONTRACT.md conform strictly to the public Pydantic schemas:
- AskResponse (for SUPPORTED, needs_clarification, INSUFFICIENT_EVIDENCE, etc.)
- VoiceAskResponse (for /ask/voice)
- AskSourcesResponse (for /ask/sources)
- FeedbackResponse (for /feedback)
"""

import json
import re
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient

from schemebot.api.main import create_app
from schemebot.api.schemas import (
    AskResponse,
    AskSourcesResponse,
    FeedbackResponse,
    VoiceAskResponse,
)
from schemebot.generate.answer import Answerer
from schemebot.retrieve.retriever import RetrievalResult, RetrievedPassage
from tests.test_answer import FakeLlm


def extract_json_blocks_from_contract(contract_path: Path) -> list[dict[str, Any]]:
    text = contract_path.read_text(encoding="utf-8")
    blocks = re.findall(r"```json\s*\n(.*?)\n```", text, re.DOTALL)
    parsed = []
    for block in blocks:
        try:
            parsed.append(json.loads(block))
        except json.JSONDecodeError as err:
            pytest.fail(f"Invalid JSON block in API_CONTRACT.md: {err}\nBlock was:\n{block}")
    return parsed


def test_api_contract_markdown_sample_payloads() -> None:
    """Verifies that every JSON sample documented in docs/API_CONTRACT.md is syntactically

    valid and conforms directly to the authoritative Pydantic models.
    """
    contract_p = Path("docs/API_CONTRACT.md")
    assert contract_p.is_file(), "docs/API_CONTRACT.md must exist"

    blocks = extract_json_blocks_from_contract(contract_p)
    assert len(blocks) >= 8, f"Expected at least 8 contract payloads, found {len(blocks)}"

    # Block 0: Status 1: SUPPORTED
    supported_model = AskResponse.model_validate(blocks[0])
    assert supported_model.status == "SUPPORTED"
    assert len(supported_model.sentences) > 0
    assert "total" in supported_model.timings_ms
    assert supported_model.understood_query is not None

    # Block 1: Status 2: needs_clarification
    clarify_model = AskResponse.model_validate(blocks[1])
    assert clarify_model.status == "needs_clarification"
    assert len(clarify_model.candidate_schemes) > 0
    assert clarify_model.understood_query is not None

    # Block 2: Status 3: INSUFFICIENT_EVIDENCE
    refusal_model = AskResponse.model_validate(blocks[2])
    assert refusal_model.status == "INSUFFICIENT_EVIDENCE"
    assert refusal_model.refusal_reason == "low_confidence"
    assert refusal_model.understood_query is not None

    # Block 3: Status 4: MODEL_UNAVAILABLE
    unavailable_model = AskResponse.model_validate(blocks[3])
    assert unavailable_model.status == "MODEL_UNAVAILABLE"
    assert unavailable_model.refusal_reason == "service_unavailable"
    assert unavailable_model.passages is not None
    assert len(unavailable_model.passages) > 0

    # Block 4: Status 5: PII_DETECTED
    pii_model = AskResponse.model_validate(blocks[4])
    assert pii_model.status == "PII_DETECTED"
    assert pii_model.refusal_reason == "pii_detected"
    assert pii_model.path == "guardrail"
    assert pii_model.understood_query is not None

    # Block 5: Status 6: Spoken Voice Response
    voice_model = VoiceAskResponse.model_validate(blocks[5])
    assert voice_model.transcript is not None
    assert voice_model.stt_language_code == "ta-IN"
    assert "stt" in voice_model.timings_ms

    # Block 6: Status 7: Fast Sources-First
    sources_model = AskSourcesResponse.model_validate(blocks[6])
    assert len(sources_model.passages) > 0
    assert "total" in sources_model.timings_ms

    # Block 7: Status 8: Feedback
    feedback_model = FeedbackResponse.model_validate(blocks[7])
    assert feedback_model.recorded is True


def test_real_server_output_conforms_to_api_contract(tmp_path: Path) -> None:
    """Verifies that live responses returned by the FastAPI server match the API contract."""
    from tests.conftest import make_chunk
    chunk = make_chunk("apy-2020-001", "Citizens aged 18 to 40 can join the scheme.")

    class RealTestRetriever:
        def retrieve(self, q: str, top_k: int = 5) -> RetrievalResult:
            passage = RetrievedPassage(chunk=chunk, relevance=0.92)
            return RetrievalResult(
                query=q,
                passages=[passage],
                timings_ms={"search": 10.0, "rerank": 5.0},
            )

    llm_reply = {
        "answerable": True,
        "sentences": [{"text": "Citizens aged 18 to 40 can join.", "sources": [1]}],
    }
    answerer = Answerer(
        retriever=cast(Any, RealTestRetriever()),
        llm=FakeLlm(llm_reply),
        verifier=None,
        refusal_threshold=0.35,
    )

    app = create_app(lambda: answerer, log_dir=tmp_path)

    with TestClient(app) as client:
        # 1. Real Supported answer through live pipeline
        res_supported = client.post("/ask", json={"question": "What is APY eligibility?"})
        assert res_supported.status_code == 200
        data_sup = res_supported.json()
        validated_sup = AskResponse.model_validate(data_sup)
        assert validated_sup.status == "SUPPORTED"
        assert len(validated_sup.sentences) > 0
        assert "total" in validated_sup.timings_ms
        assert validated_sup.understood_query is not None
        assert validated_sup.path == "rag"
        assert validated_sup.refused is False

        # 2. Real PII Intercepted answer through live pipeline
        res_pii = client.post(
            "/ask", json={"question": "My aadhaar is 2345 6789 0123 can I apply?"}
        )
        assert res_pii.status_code == 200
        data_pii = res_pii.json()
        validated_pii = AskResponse.model_validate(data_pii)
        assert validated_pii.status == "PII_DETECTED"
        assert validated_pii.refusal_reason == "pii_detected"
        assert validated_pii.path == "guardrail"
        assert validated_pii.refused is True
        assert len(validated_pii.sentences) == 0
        assert "total" in validated_pii.timings_ms

        # 3. Fast sources prefetch
        res_sources = client.post("/ask/sources", json={"question": "What is APY?"})
        assert res_sources.status_code == 200
        data_src = res_sources.json()
        validated_src = AskSourcesResponse.model_validate(data_src)
        assert len(validated_src.passages) == 1
        assert "total" in validated_src.timings_ms

        # 4. Feedback endpoint
        res_fb = client.post(
            "/feedback", json={"status": "SUPPORTED", "thumbs": "up", "language": "ta"}
        )
        assert res_fb.status_code == 200
        data_fb = res_fb.json()
        validated_fb = FeedbackResponse.model_validate(data_fb)
        assert validated_fb.recorded is True


def test_real_ask_voice_endpoint_conforms_to_contract(tmp_path: Path) -> None:
    """Verifies that live /ask/voice endpoint output conforms strictly to VoiceAskResponse

    and has no Prisma confidence field.
    """
    from tests.conftest import make_chunk
    from tests.test_api import FakeStt, FakeTts, short_wav

    chunk = make_chunk("apy-2020-001", "Citizens aged 18 to 40 can join the scheme.")

    class RealTestRetriever:
        def retrieve(self, q: str, top_k: int = 5) -> RetrievalResult:
            passage = RetrievedPassage(chunk=chunk, relevance=0.92)
            return RetrievalResult(
                query=q,
                passages=[passage],
                timings_ms={"search": 10.0, "rerank": 5.0},
            )

    llm_reply = {
        "answerable": True,
        "sentences": [{"text": "Citizens aged 18 to 40 can join.", "sources": [1]}],
    }
    answerer = Answerer(
        retriever=cast(Any, RealTestRetriever()),
        llm=FakeLlm(llm_reply),
        verifier=None,
        refusal_threshold=0.35,
    )

    app = create_app(
        lambda: answerer,
        build_stt=lambda: FakeStt("What is APY eligibility?"),
        build_tts=lambda: FakeTts(),
        log_dir=tmp_path,
    )

    with TestClient(app) as client:
        res = client.post(
            "/ask/voice",
            files={"audio": ("q.wav", short_wav(), "audio/wav")},
            data={"language": "en"},
        )
        assert res.status_code == 200
        data = res.json()
        validated = VoiceAskResponse.model_validate(data)
        assert validated.transcript == "What is APY eligibility?"
        assert validated.stt_language_code == "en-IN"
        assert validated.status == "SUPPORTED"
        assert validated.stt_confidence is None  # Prisma returns no confidence
        assert "stt" in validated.timings_ms
        assert len(validated.sentences) > 0
