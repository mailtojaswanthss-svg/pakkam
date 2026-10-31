"""Sign off fact cards after checking each one against its PDF page.

    uv run python scripts/sign_fact_cards.py --list
    uv run python scripts/sign_fact_cards.py --by "Jaswanth" kmut_income_en kmut_income_ta

Only signed cards are served (generate/fact_cards.py). Run scripts/make_card_audio.py afterwards
to pre-record their Gnani audio.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

CARDS = Path(__file__).resolve().parents[1] / "data" / "fact_cards.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sign off checked fact cards.")
    parser.add_argument("card_ids", nargs="*")
    parser.add_argument("--by", help="your name, as the person who checked the PDF page")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    cards = json.loads(CARDS.read_text(encoding="utf-8"))
    if args.list or not args.card_ids:
        for card in cards:
            mark = f"signed by {card['verified_by']}" if card.get("verified_by") else "NOT SIGNED"
            print(
                f"{card['card_id']:<22} {card['source_document']} p{card['source_page']:<4} {mark}"
            )
            print(f"    {card['answer_text']}")
        return 0
    if not args.by:
        print("Give your name with --by.")
        return 1
    known = {card["card_id"]: card for card in cards}
    unknown = [cid for cid in args.card_ids if cid not in known]
    if unknown:
        print("No such card: " + ", ".join(unknown))
        return 1
    for cid in args.card_ids:
        known[cid]["verified_by"] = args.by
        known[cid]["verified_on"] = date.today().isoformat()
    CARDS.write_text(json.dumps(cards, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Signed {len(args.card_ids)} card(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
