"""Step 5: STT Evaluation on Kathbath and synthetic/user clips.

Computes Word Error Rate (WER) with explicit punctuation/whitespace normalization.
Tracks credit guard calls strictly and caps each evaluation run at max 40 calls.
Outputs:
- data/voice/stt_eval_results.json
- Console evaluation report
"""

import csv
import io
import json
import re
import statistics
import sys
import time
import wave
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from schemebot.config import get_settings
from schemebot.voice.budget import BudgetExhausted
from schemebot.voice.stt import GNANI_LANGUAGE_CODES, GnaniStt, build_budget

MAX_CALLS_THIS_RUN = 40


def normalize_tokens(text: str) -> list[str]:
    """WER Token Normalization:
    1. Strip punctuation marks (.,!?:;"'()[]-`~ and Indic danda)
    2. Lowercase all characters
    3. Collapse multiple whitespace into single tokens
    """
    cleaned = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return [w.strip().lower() for w in cleaned.split() if w.strip()]


def calculate_wer(reference: str, hypothesis: str, normalize: bool = True) -> float:
    """Levenshtein word error rate. If normalize=True, strips punctuation and collapses whitespace."""
    if normalize:
        ref_words = normalize_tokens(reference)
        hyp_words = normalize_tokens(hypothesis)
    else:
        ref_words = reference.strip().split()
        hyp_words = hypothesis.strip().split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j

    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = 1 + min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1])

    return d[len(ref_words)][len(hyp_words)] / len(ref_words)


def get_clip_duration(clip_path: Path) -> float:
    try:
        with wave.open(str(clip_path), "rb") as wf:
            nframes = wf.getnframes()
            framerate = wf.getframerate()
            nchannels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            # Handle unfinalized stream headers where nframes is 0x7FFFFFFF
            if nframes >= 2147483640 or (nframes / framerate > 3600):
                file_size = clip_path.stat().st_size
                data_size = max(0, file_size - 44)
                bytes_per_sec = framerate * nchannels * sampwidth
                return data_size / float(bytes_per_sec) if bytes_per_sec else 0.0
            return nframes / float(framerate)
    except Exception:
        return 0.0


def main():
    settings = get_settings()
    if not settings.gnani_api_key or not settings.gnani_api_key.get_secret_value().strip():
        print("ERROR: SCHEMEBOT_GNANI_API_KEY is not set in .env", file=sys.stderr)
        return 1

    budget = build_budget(settings)
    api_key = settings.gnani_api_key.get_secret_value()
    stt_client = GnaniStt(api_key=api_key, url=settings.gnani_stt_url)

    credits_before = budget.used_today()
    print("=" * 80)
    print(" GNANI STT EVALUATION: KATHBATH & SYNTHETIC BENCHMARK")
    print("=" * 80)
    print(f"Our Daily Cap Guard: {budget.max_per_day} | Used today before run: {credits_before} | Run cap: {MAX_CALLS_THIS_RUN}")

    # Load Kathbath CSV
    kathbath_csv = Path("data/voice/kathbath_clips.csv")
    clips = []
    if kathbath_csv.exists():
        with kathbath_csv.open("r", encoding="utf-8") as f:
            clips.extend(list(csv.DictReader(f)))

    # Load optional user clips CSV
    my_clips_csv = Path("data/voice/my_clips.csv")
    if my_clips_csv.exists():
        with my_clips_csv.open("r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("consent", "").lower() in ("yes", "true", "1"):
                    clips.append(r)

    # Add synthetic smoke clip as baseline synthetic test
    synth_path = Path("data/voice/synthetic_smoke_ta.wav")
    if synth_path.exists():
        clips.append({
            "filename": synth_path.name,
            "language": "ta",
            "reference_text": "வணக்கம், இது ஒரு சோதனை ஒலி.",
            "source": "Synthetic-Plumbing",
            "synthetic_or_real": "synthetic",
        })

    if not clips:
        print("No clips found to evaluate.", file=sys.stderr)
        return 1

    calls_made = 0
    results = []

    print(f"\nEvaluating {len(clips)} clips (Max calls this run: {MAX_CALLS_THIS_RUN}):\n")

    for idx, c in enumerate(clips, 1):
        if calls_made >= MAX_CALLS_THIS_RUN:
            print(f"\n[Cap Reached] Run cap of {MAX_CALLS_THIS_RUN} calls hit. Stopping.")
            break

        fname = c["filename"]
        lang = c["language"]
        ref_text = c["reference_text"]
        source = c.get("source", "Unknown")
        kind = c.get("synthetic_or_real", "real")

        # Resolve file location
        if (Path("data/voice/kathbath") / fname).exists():
            clip_path = Path("data/voice/kathbath") / fname
        elif (Path("data/voice") / fname).exists():
            clip_path = Path("data/voice") / fname
        else:
            print(f"[{idx:02d}] Missing file {fname}, skipping.")
            continue

        gnani_lang = GNANI_LANGUAGE_CODES.get(lang, "ta-IN")
        audio_bytes = clip_path.read_bytes()
        clip_duration = get_clip_duration(clip_path)

        start_time = time.perf_counter()
        try:
            budget.take()
            calls_made += 1
            transcript = stt_client.transcribe(audio_bytes, fname, gnani_lang)
            dur = time.perf_counter() - start_time
            norm_wer = calculate_wer(ref_text, transcript, normalize=True)
            raw_wer = calculate_wer(ref_text, transcript, normalize=False)

            results.append({
                "filename": fname,
                "language": lang,
                "source": source,
                "kind": kind,
                "reference": ref_text,
                "transcript": transcript,
                "clip_duration_s": round(clip_duration, 2),
                "latency_s": round(dur, 2),
                "wer_normalized": round(norm_wer, 4),
                "wer_raw": round(raw_wer, 4),
                "success": True,
            })
            print(f"[{idx:02d}/{len(clips)}] {source:<12} ({lang}): Latency={dur:.2f}s | Norm WER={norm_wer*100:.1f}% | Raw WER={raw_wer*100:.1f}%")
        except BudgetExhausted as e:
            print(f"\n[Budget Exceeded]: {e}")
            break
        except Exception as e:
            results.append({
                "filename": fname,
                "language": lang,
                "source": source,
                "kind": kind,
                "reference": ref_text,
                "clip_duration_s": round(clip_duration, 2),
                "error": str(e),
                "success": False,
            })
            print(f"[{idx:02d}/{len(clips)}] {source:<12} ({lang}): FAILED - {e}")

    credits_after = budget.used_today()

    # Save detailed JSON output
    out_json = Path("data/voice/stt_eval_results.json")
    out_json.write_text(json.dumps({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S IST"),
        "credits_before": credits_before,
        "credits_after": credits_after,
        "calls_made": calls_made,
        "credits_cost_per_call": "unknown (undocumented by Gnani API)",
        "daily_cap_note": f"The {budget.max_per_day} calls/day limit is our own application-level safety guard",
        "results": results,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 80)
    print(" STT EVALUATION SUMMARY REPORT")
    print("=" * 80)
    print(f"Calls Made This Run: {calls_made} | Today's Guard: {credits_after} / {budget.max_per_day} calls used")
    print(f"Results saved to {out_json.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
