"""Evaluates Gnani Prisma STT accuracy and downstream retrieval on field clips.

Computes:
- Word Error Rate (WER) per clip and aggregated by language.
- Downstream retrieval scheme hit rate (Recall@1, Recall@3).
- STT latency (ms).

Reads:
- docs/voice/field_clips_metadata.csv
- Audio files from data/voice/field_clips/*.wav
Outputs:
- Console summary table
- data/voice/field_clips_results.json
"""

import csv
import json
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from schemebot.config import get_settings  # noqa: E402
from schemebot.retrieve.factory import build_retriever  # noqa: E402
from schemebot.voice.audio import convert_to_wav16k  # noqa: E402
from schemebot.voice.stt import GNANI_LANGUAGE_CODES, build_transcriber  # noqa: E402

logger = logging.getLogger(__name__)


def compute_wer(reference: str, hypothesis: str) -> float:
    """Standard Levenshtein word error rate."""
    ref_words = reference.strip().lower().split()
    hyp_words = hypothesis.strip().lower().split()
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
                d[i][j] = min(
                    d[i - 1][j] + 1,      # deletion
                    d[i][j - 1] + 1,      # insertion
                    d[i - 1][j - 1] + 1,  # substitution
                )
    return d[len(ref_words)][len(hyp_words)] / len(ref_words)


def main() -> None:
    metadata_csv = PROJECT_ROOT / "docs" / "voice" / "field_clips_metadata.csv"
    clips_dir = PROJECT_ROOT / "data" / "voice" / "field_clips"

    if not metadata_csv.exists():
        print(f"Error: metadata CSV not found at {metadata_csv}")
        sys.exit(1)

    with metadata_csv.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    available_clips = []
    for r in rows:
        clip_id = r["clip_id"]
        # Match clip_id*.wav
        matches = list(clips_dir.glob(f"{clip_id}*.wav")) if clips_dir.exists() else []
        if matches:
            available_clips.append((r, matches[0]))

    if not available_clips:
        print(f"No recorded audio clips found in {clips_dir}.")
        print("Status: BLOCKED on human audio collection (see docs/review/BLOCKED.md).")
        print(f"Plan is ready in docs/voice/CLIP_PLAN.md with {len(rows)} defined prompts.")
        sys.exit(0)

    settings = get_settings()
    transcriber = build_transcriber(settings)
    if transcriber is None or not getattr(transcriber, "configured", False):
        print("Gnani STT not configured in .env. Cannot run live field evaluation.")
        sys.exit(1)

    retriever = build_retriever(settings)

    results = []
    lang_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"wers": [], "retrieval_hits": 0, "total": 0, "stt_latencies": []}
    )

    for r, clip_path in available_clips:
        lang = r["language"]
        ref_text = r["reference_text"]
        target_scheme = r["target_scheme"].strip().lower()

        audio_bytes = clip_path.read_bytes()
        converted = convert_to_wav16k(audio_bytes, clip_path.name, settings.stt_max_seconds)

        st_start = time.perf_counter()
        lang_code = GNANI_LANGUAGE_CODES.get(lang, "ta-IN")
        try:
            transcript = transcriber.transcribe(converted, clip_path.name, lang_code)
        except Exception as exc:
            logger.error("STT failed for %s: %s", clip_path.name, exc)
            transcript = ""
        stt_ms = (time.perf_counter() - st_start) * 1000

        wer = compute_wer(ref_text, transcript)

        # Retrieval check
        retrieval_hit = False
        if transcript.strip():
            ret = retriever.retrieve(transcript)
            top_schemes = [p.chunk.scheme.lower() for p in ret.passages[:3]]
            retrieval_hit = any(target_scheme in s for s in top_schemes)

        lang_stats[lang]["wers"].append(wer)
        lang_stats[lang]["stt_latencies"].append(stt_ms)
        lang_stats[lang]["total"] += 1
        if retrieval_hit:
            lang_stats[lang]["retrieval_hits"] += 1

        results.append({
            "clip_id": r["clip_id"],
            "language": lang,
            "reference": ref_text,
            "transcript": transcript,
            "wer": round(wer, 4),
            "stt_ms": round(stt_ms, 1),
            "retrieval_hit_top3": retrieval_hit,
        })

    # Save results
    out_file = PROJECT_ROOT / "data" / "voice" / "field_clips_results.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # Print summary table
    print("\n" + "=" * 65)
    print("PAKKAM FIELD CLIPS EVALUATION RESULTS")
    print("=" * 65)
    hdr = (
        f"{'Language':<10} | {'Count':<5} | {'Mean WER':<9} | "
        f"{'Top-3 Hit%':<10} | {'Avg STT ms':<10}"
    )
    print(hdr)
    print("-" * 65)
    for lang, s in sorted(lang_stats.items()):
        mean_wer = sum(s["wers"]) / len(s["wers"]) if s["wers"] else 0.0
        hit_rate = (s["retrieval_hits"] / s["total"] * 100) if s["total"] else 0.0
        avg_lat = sum(s["stt_latencies"]) / len(s["stt_latencies"]) if s["stt_latencies"] else 0.0
        row_str = (
            f"{lang:<10} | {s['total']:<5} | {mean_wer*100:>7.1f}% | "
            f"{hit_rate:>9.1f}% | {avg_lat:>8.1f} ms"
        )
        print(row_str)
    print("=" * 65)


if __name__ == "__main__":
    main()
