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
DEFAULT_CSV_1 = PROJECT_ROOT / "docs" / "review" / "grading_sheet.csv"
DEFAULT_CSV_2 = PROJECT_ROOT / "docs" / "review" / "answer_eval.csv"


def main():
    if len(sys.argv) > 1:
        csv_path = Path(sys.argv[1])
    elif DEFAULT_CSV_1.is_file():
        csv_path = DEFAULT_CSV_1
    else:
        csv_path = DEFAULT_CSV_2

    if not csv_path.is_file():
        print(f"Error: Neither {DEFAULT_CSV_1} nor {DEFAULT_CSV_2} exists.")
        print("Run scripts/make_grading_sheet.py to create one.")
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
        na_cnt = num_counts.get("na", 0)
        c_str = f"{num_y} y, {num_n} n, {na_cnt} n/a"
        print(f"Numeric Accuracy:         {num_acc:5.1f}%  (n={num_total}: {c_str})")
    else:
        print("Numeric Accuracy:         Awaiting human grades in 'number_correct' column")

    if cite_total > 0:
        c_str = f"{cite_y} y, {cite_n} n"
        print(f"Citation Precision:       {cite_prec:5.1f}%  (n={cite_total}: {c_str})")
    else:
        print("Citation Precision:       Awaiting human grades in 'citation_supports' column")

    if unsupp_total > 0:
        c_str = f"{unsupp_y} y, {unsupp_n} n"
        print(f"Unsupported-Claim Rate:   {unsupp_rate:5.1f}%  (n={unsupp_total}: {c_str})")
    else:
        print("Unsupported-Claim Rate:   Awaiting human grades in 'unsupported_claim' column")

    print("=" * 60)


if __name__ == "__main__":
    main()
