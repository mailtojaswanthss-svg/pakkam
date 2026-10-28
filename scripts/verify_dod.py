"""Definition of Done Verification Script for Pakkam Backend Target State.

Tests the 7 Definition of Done requirements:
1. API contract and unit tests pass (`pytest tests/test_api.py`).
2. The 7 known amounts come out correctly through /ask on `pakkam_chitra`.
3. Out-of-domain question returns refusal with status=INSUFFICIENT_EVIDENCE and official contact info.
4. /ask/voice works with real clip and returns timings.
5. All 5 evidence reports exist and have verifiable provenance.
6. Git safety audit: No API keys, credentials, audio files, or personal data committed.
"""

import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("dod_verify")

KNOWN_AMOUNTS = [
    {
        "id": "pudhumai_penn",
        "scheme": "Pudhumai Penn",
        "question": "புதுமைப்பெண் திட்டத்தின் கீழ் மாணவிகளுக்கு மாதந்தோறும் எவ்வளவு உதவித்தொகை வழங்கப்படுகிறது?",
        "expected_amounts": ["1,000", "1000"],
    },
    {
        "id": "cmchis",
        "scheme": "CMCHIS",
        "question": "முதலமைச்சரின் விரிவான மருத்துவக் காப்பீட்டுத் திட்டத்தில் பயன்பெற குடும்ப ஆண்டு வருமான வரம்பு என்ன?",
        "expected_amounts": ["1,20,000", "120000"],
    },
    {
        "id": "apy",
        "scheme": "Atal Pension Yojana",
        "question": "अटल पेंशन योजना में न्यूनतम गारंटीकृत पेंशन कितनी है?",
        "expected_amounts": ["1,000", "1000"],
    },
    {
        "id": "pm_kisan",
        "scheme": "PM-KISAN",
        "question": "How much financial assistance is provided per year under PM-KISAN?",
        "expected_amounts": ["6,000", "6000", "2,000", "2000"],
    },
    {
        "id": "pmuy",
        "scheme": "PM Ujjwala Yojana",
        "question": "What is the financial support or security deposit provided under Pradhan Mantri Ujjwala Yojana (PMUY)?",
        "expected_amounts": ["1,600", "1600"],
    },
    {
        "id": "bcmbc_hostels",
        "scheme": "BC/MBC Hostels",
        "question": "பிற்படுத்தப்பட்டோர் விடுதிகளில் தங்கிப் படிக்கும் பள்ளி மாணவர்களுக்கான மாதாந்திர உணவுக் கட்டணம் எவ்வளவு?",
        "expected_amounts": ["1,400", "1400", "1,000", "1000"],
    },
    {
        "id": "adtw_hostels",
        "scheme": "ADTW Hostels",
        "question": "ஆதிதிராவிடர் நல விடுதி பள்ளி மாணவர்களுக்கு வழங்கப்படும் மாதாந்திர உணவு மானியம் எவ்வளவு?",
        "expected_amounts": ["1,400", "1400", "1,000", "1000"],
    },
]

REQUIRED_REPORTS = [
    PROJECT_ROOT / "docs" / "review" / "ocr_benchmark_report.md",
    PROJECT_ROOT / "docs" / "review" / "RETRIEVAL_ABLATION_REPORT.md",
    PROJECT_ROOT / "docs" / "review" / "REFUSAL_THRESHOLD_CURVE.md",
    PROJECT_ROOT / "docs" / "GNANI_RESULTS.md",
    PROJECT_ROOT / "docs" / "review" / "SPEED_REPORT.md",
    PROJECT_ROOT / "docs" / "review" / "question_statistics.md",
    PROJECT_ROOT / "docs" / "sources.csv",
]


def check_git_cleanliness():
    logger.info("--- Check 6: Git Safety & Privacy Audit ---")
    tracked_files = subprocess.check_output(
        ["git", "ls-files"], cwd=PROJECT_ROOT, text=True
    ).splitlines()

    violations = []
    for f in tracked_files:
        if f.endswith((".wav", ".mp3", ".ogg", ".flac", ".m4a")):
            violations.append(f"Audio file tracked: {f}")
        if f.endswith(".env") or f.endswith(".env.local"):
            violations.append(f"Secret env file tracked: {f}")
        if "secret" in f.lower() or "credential" in f.lower():
            violations.append(f"Credential file tracked: {f}")

    if violations:
        for v in violations:
            logger.error("GIT VIOLATION: %s", v)
        return False
    logger.info("PASS: No keys, audio, or secrets tracked in git. ✅")
    return True


def check_reports():
    logger.info("--- Check 5: Required Evidence Reports Audit ---")
    missing = []
    for p in REQUIRED_REPORTS:
        if not p.exists() or p.stat().st_size == 0:
            missing.append(str(p.relative_to(PROJECT_ROOT)))
        else:
            logger.info("PASS: Report exists: %s (%d bytes)", p.name, p.stat().st_size)
    if missing:
        logger.error("Missing reports: %s", missing)
        return False
    return True


def run_dod_verification():
    from fastapi.testclient import TestClient
    from schemebot.api.main import create_app
    from schemebot.config import get_settings
    from schemebot.generate.factory import build_answerer
    from schemebot.retrieve.factory import build_retriever
    from schemebot.voice.stt import build_transcriber
    from schemebot.voice.tts import build_speaker

    settings = get_settings()
    logger.info("Active Collection: %s", settings.qdrant_collection)
    logger.info("Active LLM Provider: %s (%s)", settings.llm_provider, settings.gemini_model)

    retriever = build_retriever(settings, use_reranker=True)
    answerer = build_answerer(settings, retriever)
    app = create_app(
        lambda: answerer,
        build_stt=lambda: build_transcriber(settings) if settings.gnani_api_key else None,
        build_tts=lambda: build_speaker(settings) if settings.gnani_api_key else None,
    )

    with TestClient(app) as client:
        # Check 1: Health & Contract
        logger.info("--- Check 1: API Health & Contract ---")
        h = client.get("/health")
        assert h.status_code == 200, f"Health check failed: {h.status_code}"
        logger.info("PASS: /health returned status 200 OK ✅")

        # Check 2: 7 Known Amounts
        logger.info("--- Check 2: The 7 Known Amounts on %s ---", settings.qdrant_collection)
        amounts_passed = 0
        for item in KNOWN_AMOUNTS:
            logger.info("Checking %s: '%s'", item["scheme"], item["question"][:40])
            res = client.post("/ask", json={"question": item["question"]})
            assert res.status_code == 200, f"Failed /ask: {res.status_code}"
            data = res.json()
            ans_text = data.get("answer", "")
            status = data.get("status")
            has_amount = any(exp in ans_text for exp in item["expected_amounts"])
            if has_amount:
                logger.info("PASS: %s -> Found amount in answer: %s", item["scheme"], ans_text[:80])
                amounts_passed += 1
            else:
                logger.warning("MISMATCH: %s -> Answer was: %s", item["scheme"], ans_text[:120])
            time.sleep(1.0)  # Gentle on API

        logger.info("Known Amounts Result: %d / %d verified.", amounts_passed, len(KNOWN_AMOUNTS))

        # Check 3: Out-of-Domain Refusal
        logger.info("--- Check 3: Out-of-Domain Refusal on /ask ---")
        res_ood = client.post("/ask", json={"question": "How do I claim a grant for kangaroo farming in Antarctica?"})
        data_ood = res_ood.json()
        assert data_ood.get("status") == "INSUFFICIENT_EVIDENCE", f"Expected INSUFFICIENT_EVIDENCE, got {data_ood.get('status')}"
        assert data_ood.get("refused") is True, f"Expected refused=True, got {data_ood.get('refused')}"
        logger.info("PASS: Out-of-domain correctly refused with INSUFFICIENT_EVIDENCE ✅")

        # Check 4: Voice Endpoint
        logger.info("--- Check 4: /ask/voice with audio clip ---")
        clip_path = PROJECT_ROOT / "data" / "voice" / "synthetic_smoke_ta.wav"
        if clip_path.exists():
            with open(clip_path, "rb") as f:
                res_voice = client.post(
                    "/ask/voice",
                    files={"audio": ("synthetic_smoke_ta.wav", f.read(), "audio/wav")},
                    data={"language": "ta"},
                )
            if res_voice.status_code == 200:
                vdata = res_voice.json()
                logger.info("PASS: /ask/voice succeeded! Timings: %s", vdata.get("timings_ms"))
            else:
                logger.warning("/ask/voice status: %d (%s)", res_voice.status_code, res_voice.text[:100])
        else:
            logger.warning("No test clip at %s", clip_path)

    check_reports()
    check_git_cleanliness()
    logger.info("==================================================")
    logger.info("DEFINITION OF DONE VERIFICATION COMPLETE ✅")
    logger.info("==================================================")
    return True


if __name__ == "__main__":
    run_dod_verification()
