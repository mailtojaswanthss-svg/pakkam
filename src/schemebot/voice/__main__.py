"""Voice tests that spend real Gnani credits. Each one shows how many calls it will make
and waits for you to type yes; every call counts in the daily cap.

Compare language codes on your clips (results in data/voice/runs/, gitignored;
folder layout in voice/compare.py):

    uv run python -m schemebot.voice compare data/voice/tanglish/
    uv run python -m schemebot.voice compare data/voice/tanglish/ --codes ta-IN en-IN

Listen to Timbre on short made-up sentences (WAVs in data/voice/tts-samples/, gitignored;
the cases are in voice/samples.py):

    uv run python -m schemebot.voice tts-samples --cases tamil --models timbre-v2.5 timbre-v3.0
    uv run python -m schemebot.voice tts-samples --cases digits tanglish --models timbre-v2.5
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import cast

from schemebot.config import TimbreModel, get_settings
from schemebot.voice.compare import find_clips, run, write_csv
from schemebot.voice.samples import CASES, MODELS, make_samples
from schemebot.voice.stt import build_budget, build_transcriber
from schemebot.voice.tts import BudgetedSpeaker, GnaniTts, Speaker, voices_for

DEFAULT_CODES = ["ta-IN", "en-IN"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Gnani language codes on your clips.")
    sub = parser.add_subparsers(dest="command", required=True)
    compare = sub.add_parser("compare", help="Send each clip once per language code.")
    compare.add_argument("folder", type=Path)
    compare.add_argument("--codes", nargs="+", default=DEFAULT_CODES)
    samples = sub.add_parser("tts-samples", help="Make Timbre WAVs of test sentences.")
    samples.add_argument("--cases", nargs="+", choices=list(CASES), default=["tamil"])
    samples.add_argument("--models", nargs="+", choices=list(MODELS), required=True)
    args = parser.parse_args()
    if args.command == "compare":
        return compare_command(args.folder, args.codes)
    # argparse `choices` already limited --models to the Timbre model names.
    return tts_samples_command(args.cases, cast(list[TimbreModel], args.models))


def compare_command(folder: Path, codes: list[str]) -> int:
    settings = get_settings()
    stt = build_transcriber(settings)
    if stt is None:
        print("No Gnani key: set SCHEMEBOT_GNANI_API_KEY in .env first.", file=sys.stderr)
        return 1
    if not folder.is_dir():
        print(f"No such folder: {folder}", file=sys.stderr)
        return 1

    clips = find_clips(folder)
    calls = len(clips) * len(codes)
    left = stt.budget.remaining()
    for clip in clips:
        print(f"  {clip.path.name:30} {clip.clip_type}")
    print(f"\n{len(clips)} clips x {len(codes)} codes ({', '.join(codes)})")
    print(f"This will make {calls} Gnani calls. {left} calls left today under the daily cap.")
    if calls == 0:
        return 0
    if calls > left:
        print("Not enough calls left today. Raise the cap or use fewer clips.", file=sys.stderr)
        return 1
    if input("Type yes to spend these credits: ").strip().lower() != "yes":
        print("Cancelled. No calls made.")
        return 0

    rows = run(clips, codes, stt, settings.stt_max_bytes, settings.stt_max_seconds)
    out = settings.data_dir / "voice" / "runs" / f"compare-{datetime.now():%Y%m%d-%H%M}.csv"
    write_csv(rows, out)
    errors = sum(1 for row in rows if row["error"])
    print(f"Saved {len(rows)} rows ({errors} errors) to {out}")
    return 0


def tts_samples_command(cases: list[str], models: list[TimbreModel]) -> int:
    settings = get_settings()
    if settings.gnani_api_key is None:
        print("No Gnani key: set SCHEMEBOT_GNANI_API_KEY in .env first.", file=sys.stderr)
        return 1
    budget = build_budget(settings)
    speakers: dict[str, Speaker] = {}
    for model in models:
        voices = voices_for(settings, model)
        key = settings.gnani_api_key.get_secret_value()
        gnani = GnaniTts(key, settings.gnani_tts_url, model, voices)
        speakers[model] = BudgetedSpeaker(gnani, budget)
        for case in cases:
            code = CASES[case].language_code
            print(f"  {case:9} {model:12} voice {voices[code]} ({code})")

    calls = len(cases) * len(models)
    left = budget.remaining()
    print(f"\nThis will make {calls} Gnani calls. {left} calls left today under the daily cap.")
    if calls > left:
        print("Not enough calls left today.", file=sys.stderr)
        return 1
    if input("Type yes to spend these credits: ").strip().lower() != "yes":
        print("Cancelled. No calls made.")
        return 0

    folder = settings.data_dir / "voice" / "tts-samples"
    for path, outcome in make_samples(speakers, cases, folder):
        print(f"  {path.name}: {outcome}")
    print(f"Synthetic test audio in {folder}. Listen, then tell Claude what you heard.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
