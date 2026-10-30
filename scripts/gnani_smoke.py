"""Step 2: Real Smoke Test for Gnani STT and Timbre TTS.

Executes:
1. One real TTS call to generate a short synthetic clip ("வணக்கம், இது ஒரு சோதனை ஒலி.") in Tamil.
2. One real STT call sending that synthetic clip to Gnani Prisma STT (ta-IN).
3. Respects CallBudget daily cap and logs latency, status, language, and credits without leaking keys.
"""

import sys
import time
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from schemebot.config import get_settings
from schemebot.voice.budget import BudgetExhausted
from schemebot.voice.stt import GnaniStt, build_budget
from schemebot.voice.tts import DEFAULT_VOICES, GnaniTts


def main() -> int:
    settings = get_settings()
    if not settings.gnani_api_key or not settings.gnani_api_key.get_secret_value().strip():
        print("ERROR: SCHEMEBOT_GNANI_API_KEY is not set in .env", file=sys.stderr)
        return 1

    api_key = settings.gnani_api_key.get_secret_value()
    budget = build_budget(settings)

    print("=" * 65)
    print(" GNANI VOICE: REAL SMOKE TEST (STT & TTS)")
    print("=" * 65)
    print(f"Daily Cap: {budget.max_per_day} | Calls used today before test: {budget.used_today()}")

    out_dir = Path("data/voice")
    out_dir.mkdir(parents=True, exist_ok=True)
    synth_wav_path = out_dir / "synthetic_smoke_ta.wav"

    # --- 1. Real TTS Call ---
    model = settings.tts_model or "timbre-v3.0"
    voices = DEFAULT_VOICES.get(model, {"ta-IN": "Shivani"})
    tts_client = GnaniTts(
        api_key=api_key,
        url=settings.gnani_tts_url,
        model=model,
        voices=voices,
    )

    test_phrase = "வணக்கம், இது ஒரு சோதனை ஒலி."
    print(
        f"\n[1/2] Testing TTS (Timbre Model: {model}, Voice: {voices.get('ta-IN', 'default')}, Lang: ta-IN)..."
    )
    tts_start = time.perf_counter()

    try:
        budget.take()
        audio_bytes = tts_client.speak(test_phrase, "ta-IN")
        tts_dur = time.perf_counter() - tts_start
        synth_wav_path.write_bytes(audio_bytes)
        print(f"  -> TTS SUCCESS: {len(audio_bytes)} bytes received in {tts_dur:.2f}s")
        print(f"  -> Saved synthetic clip to {synth_wav_path.as_posix()} (labelled: synthetic)")
    except BudgetExhausted as e:
        print(f"  -> TTS BLOCKED by Credit Guard: {e}")
        return 1
    except Exception as e:
        print(f"  -> TTS FAILED: {type(e).__name__}: {e}")
        return 1

    # --- 2. Real STT Call ---
    stt_client = GnaniStt(
        api_key=api_key,
        url=settings.gnani_stt_url,
    )

    print("\n[2/2] Testing STT (Prisma v2.5, Lang: ta-IN)...")
    stt_start = time.perf_counter()

    try:
        budget.take()
        transcript = stt_client.transcribe(audio_bytes, synth_wav_path.name, "ta-IN")
        stt_dur = time.perf_counter() - stt_start
        print(f"  -> STT SUCCESS: Completed in {stt_dur:.2f}s")
        print(f"  -> Original text:   '{test_phrase}'")
        print(f"  -> STT Transcript:  '{transcript}'")
    except BudgetExhausted as e:
        print(f"  -> STT BLOCKED by Credit Guard: {e}")
        return 1
    except Exception as e:
        print(f"  -> STT FAILED: {type(e).__name__}: {e}")
        return 1

    print("-" * 65)
    print(f"Calls used today after test: {budget.used_today()} / {budget.max_per_day}")
    print("REAL SMOKE TEST RESULT: ALL PASSED ✅")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
