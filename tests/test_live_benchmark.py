import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "live_benchmark", Path(__file__).resolve().parents[1] / "scripts" / "live_benchmark.py"
)
assert spec and spec.loader
live = importlib.util.module_from_spec(spec)
sys.modules["live_benchmark"] = live
spec.loader.exec_module(live)

COVERED = {"answerable": True, "gold": [{"doc_id": "apy", "pages": [1, 2]}]}
UNCOVERED = {"answerable": False, "gold": []}


def reply(**fields: object) -> dict[str, object]:
    base: dict[str, object] = {
        "status": "SUPPORTED",
        "refused": False,
        "sentences": [{"text": "x"}],
    }
    return {**base, "citations": [{"doc_id": "apy", "page_start": 2, "page_end": 2}], **fields}


def test_grading_outcomes() -> None:
    assert live.grade(COVERED, reply(), "") == {"outcome": "answered", "cited_gold_page": True}
    wrong_page = reply(citations=[{"doc_id": "apy", "page_start": 5, "page_end": 5}])
    assert live.grade(COVERED, wrong_page, "")["cited_gold_page"] is False
    refused = reply(refused=True, sentences=[], refusal_reason="low_confidence")
    assert live.grade(COVERED, refused, "")["outcome"] == "missed"
    assert live.grade(UNCOVERED, refused, "")["outcome"] == "correct_refusal"
    assert live.grade(UNCOVERED, reply(), "")["outcome"] == "answered_uncovered"
    assert live.grade(COVERED, reply(status="MODEL_UNAVAILABLE"), "")["outcome"] == "busy"
    assert live.grade(COVERED, None, "HTTP 502")["outcome"] == "error"


def test_sample_keeps_each_language_and_some_uncovered_questions() -> None:
    questions = [
        {"group": g, "answerable": i % 5 != 0, "id": f"{g}{i}"}
        for g in ("en", "ta", "hi", "ta-Latn")
        for i in range(20)
    ]
    chosen = live.pick(questions, 5)
    assert len(chosen) == 20
    assert all(
        sum(not q["answerable"] for q in chosen if q["group"] == g) >= 1 for g in live.GROUP_NAMES
    )
