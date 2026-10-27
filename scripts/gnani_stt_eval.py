"""Step 5: STT Evaluation on Kathbath and synthetic/user clips.

Computes Word Error Rate (WER), character accuracy, and latency.
Tracks credit guard calls strictly and caps each evaluation run at max 40 calls.
Outputs:
- data/voice/stt_eval_results.json
- Console evaluation report
"""

import csv
import json
import statistics
import sys
import time
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from schemebot.config import get_settings
from schemebot.voice.budget import BudgetExhausted
from schemebot.voice.stt import GNANI_LANGUAGE_CODES, GnaniStt, build_budget

MAX_CALLS_THIS_RUN = 40


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Levenshtein word error rate."""
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
            if ref_words[i - 1].lower() == hyp_words[j - 1].lower():
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = 1 + min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1])

    return d[len(ref_words)][len(hyp_words)] / len(ref_words)


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
    print(f"Daily Cap: {budget.max_per_day} | Used today before run: {credits_before} | Run cap: {MAX_CALLS_THIS_RUN}")

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
            "reference_text": "வணக்கம் இது ஒரு சோதனை ஒலி",
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

        start_time = time.perf_counter()
        try:
            budget.take()
            calls_made += 1
            transcript = stt_client.transcribe(audio_bytes, fname, gnani_lang)
            dur = time.perf_counter() - start_time
            wer = calculate_wer(ref_text, transcript)

            results.append({
                "filename": fname,
                "language": lang,
                "source": source,
                "kind": kind,
                "reference": ref_text,
                "transcript": transcript,
                "latency_s": dur,
                "wer": wer,
                "success": True,
            })
            print(f"[{idx:02d}/{len(clips)}] {source:<12} ({lang}): Latency={dur:.2f}s | WER={wer*100:.1f}%")
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
        "results": results,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # Generate summary metrics
    print("\n" + "=" * 80)
    print(" STT EVALUATION SUMMARY REPORT")
    print("=" * 80)
    print(f"Credits Used: {calls_made} calls (Remaining today: {budget.remaining()} / {budget.max_per_day})")

    # Group by (source, kind, language)
    groups = {}
    for r in results:
        if not r.get("success"):
            continue
        key = (r["source"], r["kind"], r["language"])
        groups.setdefault(key, []).append(r)

    print(f"\n{'Source':<20} {'Kind':<12} {'Lang':<6} {'Count':<6} {'Median Latency':<16} {'Mean WER'}")
    print("-" * 75)
    for (src, kind, lang), items in groups.items():
        wers = [it["wer"] for it in items]
        lats = [it["latency_s"] for it in items]
        mean_wer = sum(wers) / len(wers) if wers else 0.0
        med_lat = statistics.median(lats) if lats else 0.0
        print(f"{src:<20} {kind:<12} {lang:<6} {len(items):<6} {med_lat:>5.2f}s          {mean_wer*100:>6.1f}%")

    print("=" * 80)
    print(f"Results saved to {out_json.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
