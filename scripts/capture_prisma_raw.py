"""Make exactly 1 real request to Gnani Prisma STT on a public Kathbath clip.

Saves raw response JSON to data/voice/prisma_raw_sample.json (gitignored)
and inspects the response schema for presence/absence of confidence fields.
"""

# ruff: noqa: E402

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from schemebot.config import get_settings
from schemebot.voice.budget import CALLS_FILE_NAME, CallBudget

RAW_SAMPLE_PATH = PROJECT_ROOT / "data" / "voice" / "prisma_raw_sample.json"
SAMPLE_CLIP_PATH = PROJECT_ROOT / "data" / "voice" / "kathbath" / "kathbath_ta_01.wav"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("capture_prisma")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    settings = get_settings()
    if not settings.gnani_api_key:
        print("ERROR: SCHEMEBOT_GNANI_API_KEY is not set.")
        sys.exit(1)

    if not SAMPLE_CLIP_PATH.exists():
        print(f"ERROR: Sample clip {SAMPLE_CLIP_PATH} not found.")
        sys.exit(1)

    budget = CallBudget(
        PROJECT_ROOT / CALLS_FILE_NAME, max_per_day=settings.gnani_max_calls_per_day
    )
    logger.info("Gnani budget before call: %d / %d", budget.used_today(), budget.max_per_day)

    # Count 1 call before dispatch
    budget.take()

    audio_bytes = SAMPLE_CLIP_PATH.read_bytes()
    api_key = settings.gnani_api_key.get_secret_value()

    headers = {
        "X-API-Key-ID": api_key,
    }
    data = {
        "language_code": "ta-IN",
    }
    files = {
        "audio_file": (SAMPLE_CLIP_PATH.name, audio_bytes, "audio/wav"),
    }

    logger.info("Dispatching 1 real STT request to %s...", settings.gnani_stt_url)
    t0 = time.perf_counter()
    with httpx.Client(timeout=settings.stt_timeout_seconds) as client:
        resp = client.post(
            settings.gnani_stt_url,
            headers=headers,
            data=data,
            files=files,
        )
    latency_ms = (time.perf_counter() - t0) * 1000
    logger.info("Received HTTP %d in %.1f ms", resp.status_code, latency_ms)

    try:
        raw_json: dict[str, Any] = resp.json()
    except Exception as exc:
        print(f"Failed to parse JSON response: {exc}")
        print("Raw text:", resp.text)
        sys.exit(1)

    # Save to gitignored destination
    RAW_SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_SAMPLE_PATH.write_text(json.dumps(raw_json, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Saved raw JSON to %s", RAW_SAMPLE_PATH)

    # Inspect fields
    has_confidence = "confidence" in raw_json
    has_transcript = "transcript" in raw_json
    success = raw_json.get("success", False)
    all_keys = list(raw_json.keys())

    print("\n" + "=" * 60)
    print("GNANI PRISMA v2.5 RAW RESPONSE AUDIT")
    print("=" * 60)
    print(f"Status Code:        {resp.status_code}")
    print(f"Success Flag:       {success}")
    print(f"Latency:            {latency_ms:.1f} ms")
    print(f"Keys present:       {all_keys}")
    print(f"Has 'transcript':   {has_transcript} ({repr(raw_json.get('transcript'))[:50]})")
    print(f"Has 'confidence':   {has_confidence}")
    if has_confidence:
        print(f"Confidence value:   {raw_json.get('confidence')}")
    else:
        print("CONFIDENCE AUDIT:   CONFIRMED ABSENT. Prisma v2.5 returns NO confidence field.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
