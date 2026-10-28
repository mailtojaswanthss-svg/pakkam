"""Answer-level evaluation summary calculator.

Reads docs/review/answer_eval.csv (filled by a human reviewer) and prints:
- Numeric Accuracy (number_correct: y vs n)
- Citation Precision (citation_supports: y vs n)
- Unsupported-claim rate (unsupported_claim: y vs n)
Each metric is printed with exact sample count n.
"""

import csv
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = PROJECT_ROOT / "docs" / "review" / "answer_eval.csv"


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    if not csv_path.is_file():
        print(f"Error: CSV file not found at {csv_path}")
        return

    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print(f"CSV {csv_path} is empty.")
        return

    total_rows = len(rows)

    num_counts = Counter(r.get("number_correct", "").strip().lower() for r in rows)
    cite_counts = Counter(r.get("citation_supports", "").strip().lower() for r in rows)
    unsupp_counts = Counter(r.get("unsupported_claim", "").strip().lower() for r in rows)

    # Numeric Accuracy: y / (y + n)
    num_y = num_counts.get("y", 0)
    num_n = num_counts.get("n", 0)
    num_total = num_y + num_n
    num_acc = (num_y / num_total * 100) if num_total > 0 else 0.0

    # Citation Precision: y / (y + n)
    cite_y = cite_counts.get("y", 0)
    cite_n = cite_counts.get("n", 0)
    cite_total = cite_y + cite_n
    cite_prec = (cite_y / cite_total * 100) if cite_total > 0 else 0.0

    # Unsupported-claim rate: y / total reviewed
    unsupp_y = unsupp_counts.get("y", 0)
    unsupp_n = unsupp_counts.get("n", 0)
    unsupp_total = unsupp_y + unsupp_n
    unsupp_rate = (unsupp_y / unsupp_total * 100) if unsupp_total > 0 else 0.0

    print("=" * 60)
    print("PAKKAM ANSWER-LEVEL HUMAN EVALUATION SUMMARY")
    print(f"Source CSV: {csv_path}")
    print(f"Total Rows: {total_rows}")
    print("-" * 60)

    if num_total > 0:
        print(f"Numeric Accuracy:         {num_acc:5.1f}%  (n={num_total}: {num_y} correct, {num_n} wrong, {num_counts.get('na', 0)} n/a)")
    else:
        print("Numeric Accuracy:         Awaiting human grades in 'number_correct' column")

    if cite_total > 0:
        print(f"Citation Precision:       {cite_prec:5.1f}%  (n={cite_total}: {cite_y} supported, {cite_n} unsupported)")
    else:
        print("Citation Precision:       Awaiting human grades in 'citation_supports' column")

    if unsupp_total > 0:
        print(f"Unsupported-Claim Rate:   {unsupp_rate:5.1f}%  (n={unsupp_total}: {unsupp_y} unsupported, {unsupp_n} supported)")
    else:
        print("Unsupported-Claim Rate:   Awaiting human grades in 'unsupported_claim' column")

    print("=" * 60)


if __name__ == "__main__":
    main()
