"""Step 1 Preflight: Check environment, keys, tools, and budget guard."""

import os
import shutil
import socket
import sys
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from schemebot.config import get_settings


def check_port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def main() -> int:
    settings = get_settings()
    env_file = settings.model_config.get("env_file")
    failures = 0

    print("=" * 60)
    print(" GNANI VOICE INTEGRATION: PREFLIGHT DOCTOR")
    print("=" * 60)

    # 1. Check .env file
    if env_file and Path(env_file).is_file():
        print(f"[PASS] .env file located at {env_file}")
    else:
        print("[FAIL] .env file not found. Create it by copying .env.example.")
        failures += 1

    # 2. Check Gnani API Key (Never print value)
    if settings.gnani_api_key and settings.gnani_api_key.get_secret_value().strip():
        print("[PASS] SCHEMEBOT_GNANI_API_KEY is configured (masked)")
    else:
        print("[FAIL] SCHEMEBOT_GNANI_API_KEY is missing or empty in .env.")
        print("       Fix: Add your Gnani API key from app.gnani.ai/voice to .env")
        failures += 1

    # 3. Check TTS Model
    if settings.tts_model:
        print(f"[PASS] SCHEMEBOT_TTS_MODEL is set ({settings.tts_model})")
    else:
        print("[FAIL] SCHEMEBOT_TTS_MODEL is not set in .env.")
        print("       Fix: Set SCHEMEBOT_TTS_MODEL=timbre-v2.5 or timbre-v3.0 in .env")
        failures += 1

    # 4. Check HF_TOKEN (Never print value)
    hf_token = os.environ.get("HF_TOKEN", "")
    if not hf_token and env_file and Path(env_file).is_file():
        for line in Path(env_file).read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("HF_TOKEN="):
                hf_token = line.split("=", 1)[1].strip()
                break
    if hf_token:
        print("[PASS] HF_TOKEN is configured (masked)")
    else:
        print("[FAIL] HF_TOKEN is missing or empty in .env.")
        print("       Fix: Generate a token at huggingface.co/settings/tokens and add HF_TOKEN=... to .env")
        failures += 1

    # 5. Check ffmpeg
    ffmpeg_bin = shutil.which("ffmpeg")
    if ffmpeg_bin:
        print(f"[PASS] ffmpeg detected on PATH ({ffmpeg_bin})")
    else:
        print("[FAIL] ffmpeg is not found on system PATH.")
        print("       Fix: Run 'winget install Gyan.FFmpeg' in PowerShell, then restart terminal.")
        failures += 1

    # 6. Check Python environment & libraries
    try:
        import httpx
        import pydantic
        import pymupdf
        print("[PASS] Python environment has required packages (httpx, pydantic, pymupdf)")
    except ImportError as e:
        print(f"[FAIL] Missing Python dependencies: {e}")
        print("       Fix: Run 'uv sync --extra ingest --extra index --extra generate --extra api'")
        failures += 1

    # 7. Check Port 8000
    if check_port_free(8000):
        print("[PASS] Port 8000 is free for FastAPI service")
    else:
        print("[WARN] Port 8000 is currently occupied (a server may already be running).")

    # 8. Check Credit Guard
    if settings.gnani_max_calls_per_day > 0:
        print(f"[PASS] Credit Guard is active (limit: {settings.gnani_max_calls_per_day} calls/day)")
    else:
        print("[WARN] Credit Guard is disabled (SCHEMEBOT_GNANI_MAX_CALLS_PER_DAY=0).")

    print("-" * 60)
    if failures == 0:
        print("PREFLIGHT RESULT: ALL CHECKS PASSED ✅")
        print("=" * 60)
        return 0
    else:
        print(f"PREFLIGHT RESULT: {failures} CHECK(S) FAILED ❌")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
