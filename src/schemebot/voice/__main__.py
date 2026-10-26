"""Compare Gnani language codes on your clips (this spends real Gnani credits):

    uv run python -m schemebot.voice compare data/voice/tanglish/
    uv run python -m schemebot.voice compare data/voice/tanglish/ --codes ta-IN en-IN

It shows how many calls it will make and waits for you to type yes. Results go to
data/voice/runs/compare-<time>.csv (gitignored). See voice/compare.py for the folder layout.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from schemebot.config import get_settings
from schemebot.voice.compare import find_clips, run, write_csv
from schemebot.voice.stt import build_transcriber

DEFAULT_CODES = ["ta-IN", "en-IN"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Gnani language codes on your clips.")
    sub = parser.add_subparsers(dest="command", required=True)
    compare = sub.add_parser("compare", help="Send each clip once per language code.")
    compare.add_argument("folder", type=Path)
    compare.add_argument("--codes", nargs="+", default=DEFAULT_CODES)
    args = parser.parse_args()
    return compare_command(args.folder, args.codes)


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


if __name__ == "__main__":
    sys.exit(main())
