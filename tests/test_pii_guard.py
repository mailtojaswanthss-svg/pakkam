import pytest

from schemebot.generate.messages import contains_pii
from schemebot.ingest.models import Chunk
from tests.test_answer import FakeLlm, answer_with


@pytest.mark.parametrize(
    "text",
    [
        "What is the eligibility for 12,000 scheme?",
        "ரூ. 2,50,000 வருமான வரம்பு உள்ளதா?",
        "Income limit is 60000 per year for scholarship",
        "G.O. dated 2024-05-12 notification details",
        "Scheme launched on 15/08/2023 by government",
        "Gazette notification 12-05-2024",
        "Call toll free 1800110069 for national helpline",
        "Call helpline 1800 425 3993 for assistance",
        "Dial 14417 for education department query",
        "CM Helpline number is 1100",
        "Health department helpline is 104",
        "Women helpline is 181",
    ],
)
def test_pii_guard_false_positives(text: str) -> None:
    """Verifies that amounts, dates, and helplines are never falsely flagged as PII."""
    assert not contains_pii(text), f"False positive detected for: {text}"


@pytest.mark.parametrize(
    "text",
    [
        "My Aadhaar is 2345 6789 0123 please verify",
        "Aadhaar: 2345-6789-0123",
        "Card number 234567890123",
        "My phone number is 9876543210",
        "Call me at +91 9876543210",
        "Mobile: +91-9876543210",
        "Contact 09876543210 for details",
        "Phone 98765 43210",
        "என் ஆதார் எண் ௨௩௪௫ ௬௭௮௯ ௦௧௨௩",
        "என் தொலைபேசி ௯௮௭௬௫௪௩௨௧௦",
        "मेरा आधार २३४५ ६७८९ ०१२३ है",
        "मोबाइल नंबर ९८७६५४३२१० पर कॉल करें",
    ],
)
def test_pii_guard_true_positives(text: str) -> None:
    """Verifies that spaced/dashed/continuous Aadhaar, mobiles, and Indic numerals are caught."""
    assert contains_pii(text), f"True positive missed for: {text}"


def test_pii_guard_voice_transcript_flow(corpus: list[Chunk]) -> None:
    """Verifies that voice transcripts containing PII intercept LLM calls with zero leakage."""
    voice_transcript_tamil = "என் மொபைல் நம்பர் ௯௮௭௬௫௪௩௨௧௦ உதவித்தொகை எப்போது வரும்?"
    llm = FakeLlm({"answerable": True, "sentences": [{"text": "Leaked"}]})
    ans = answer_with(llm, corpus, voice_transcript_tamil)
    assert ans.refused
    assert ans.refusal_reason == "pii_detected"
    assert ans.status == "PII_DETECTED"
    assert ans.path == "guardrail"
    assert "பாதுகாப்பிற்காக" in ans.text
    assert len(llm.user_messages) == 0
