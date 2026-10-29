"""Audit script to verify that any non-null helpline has human verification and source URL.

Release gate rule:
If any helpline is published / non-null without a valid source URL and a human verified_by
entry, this script exits with non-zero status to fail the release build.
"""

import sys
from pathlib import Path

from schemebot.generate.contacts import verify_helplines

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "docs" / "review" / "helpline_check.csv"


def main() -> None:
    errors = verify_helplines(CSV_PATH)
    if errors:
        print("FAIL: Helpline release check failed with unverified numbers:")
        for err in errors:
            print(f"  - {err}")
        print("\nAction required: verify the number, record URL and verified_by in")
        print("docs/review/helpline_check.csv, or set helpline to null.")
        sys.exit(1)
    else:
        print("OK: All helpline entries conform to the verification protocol.")
        sys.exit(0)


if __name__ == "__main__":
    main()
