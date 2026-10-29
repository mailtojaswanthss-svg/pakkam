# ruff: noqa: E501
"""Step 8: Review citizen feedback logs (logs/feedback.jsonl).

Summarizes thumbs up vs thumbs down, breakdown by status, and lists
reported wrong-answer reasons for dataset triage.
"""

from collections import Counter
import json
from pathlib import Path
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def review_feedback() -> None:
    fb_path = PROJECT_ROOT / "logs" / "feedback.jsonl"
    if not fb_path.is_file():
        print("No feedback logged yet. Log path:", fb_path)
        return

    entries = []
    with open(fb_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    total = len(entries)
    print("=" * 60)
    print(f"PAKKAM FEEDBACK AUDIT: {total} total user ratings")
    print("=" * 60)

    thumbs_counts = Counter(e.get("thumbs") for e in entries)
    print(f"Thumbs Up:   {thumbs_counts.get('up', 0)} ({thumbs_counts.get('up', 0)/total*100:.1f}%)")
    print(f"Thumbs Down: {thumbs_counts.get('down', 0)} ({thumbs_counts.get('down', 0)/total*100:.1f}%)")

    status_counts = Counter(e.get("status") for e in entries)
    print("\nBreakdown by Response Status:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

    down_reasons = [e for e in entries if e.get("thumbs") == "down" and e.get("reason")]
    if down_reasons:
        print(f"\nUser Reported Issues ({len(down_reasons)} items):")
        for idx, item in enumerate(down_reasons, 1):
            ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get("timestamp", 0)))
            print(f"  [{idx}] {ts} - Q: \"{item.get('question')}\"")
            print(f"      Reason: {item.get('reason')}")
    else:
        print("\nNo detailed wrong-answer reasons logged.")


if __name__ == "__main__":
    review_feedback()
