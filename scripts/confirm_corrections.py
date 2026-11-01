"""Confirm OCR corrections after comparing each one with the printed PDF page.

    uv run python scripts/confirm_corrections.py --list
    uv run python scripts/confirm_corrections.py --by "Jaswanth" kmut-go15-2023-ta:10 kmut-go15-2023-ta:11

An unconfirmed entry only stops answers from using the misread number. A confirmed one also
replaces the misreading with what the page shows, at the next `python -m schemebot.ingest`
(then rebuild the index with `python -m schemebot.index`). Entries are named doc_id:page;
`doc_id:page#2` picks the second entry for the same page.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CORRECTIONS = Path(__file__).resolve().parents[1] / "data" / "corrections.json"


def names(entries: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    named: dict[str, dict[str, object]] = {}
    for entry in entries:
        base = f"{entry['doc_id']}:{entry['page']}"
        name, n = base, 1
        while name in named:
            n += 1
            name = f"{base}#{n}"
        named[name] = entry
    return named


def main() -> int:
    parser = argparse.ArgumentParser(description="Confirm checked OCR corrections.")
    parser.add_argument("entries", nargs="*", help="doc_id:page")
    parser.add_argument("--by", help="your name, as the person who checked the PDF page")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    entries = json.loads(CORRECTIONS.read_text(encoding="utf-8"))
    named = names(entries)
    if args.list or not args.entries:
        for name, entry in named.items():
            mark = (
                f"confirmed by {entry['confirmed_by']}"
                if entry.get("confirmed_by")
                else "NOT CONFIRMED"
            )
            print(f"{name:<36} {mark}")
            print(f"    OCR reads: {entry['ocr_reads']}")
            print(f"    page shows: {entry['pdf_shows']}")
        return 0
    if not args.by or not args.by.strip():
        print("Give your name with --by.")
        return 1
    unknown = [name for name in args.entries if name not in named]
    if unknown:
        print("No such entry: " + ", ".join(unknown) + " (see --list)")
        return 1
    for name in args.entries:
        named[name]["confirmed_by"] = args.by.strip()
        named[name]["confirmed_on"] = date.today().isoformat()
    CORRECTIONS.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Confirmed {len(args.entries)} correction(s). Now run: python -m schemebot.ingest, "
        "then python -m schemebot.index"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
