"""Find money amounts the OCR may have misread, so wrong numbers are fixed before users hear them.

    uv run python scripts/check_amounts.py            # free checks only
    uv run python scripts/check_amounts.py --vision   # also let Claude read the risky pages

Three independent checks on every money amount in data/processed/chunks.jsonl:
1. Common sense: an income limit above Rs.10 lakh or a monthly benefit above Rs.50,000 in a
   welfare document is almost certainly a misread (Rs.2.5 lakh read as 25 lakh).
2. Tamil vs English: in the policy notes published in both languages, an amount on a Tamil
   OCR page that never appears in the English version is suspicious.
3. A third reader (--vision): Claude reads the printed page image and lists its amounts. An
   amount the image does not show is flagged. Asks before spending (about 1-2 US cents a page).

Writes docs/review/amount_check.csv: one row per suspicious amount with the reasons, and what
the page image shows. Check the 'check' rows against the PDF, then add each confirmed fix to
data/corrections.json (Claude can do that from the CSV).
"""

import argparse
import base64
import csv
import json
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from schemebot.generate.guardrails import numbers_in  # noqa: E402

OUT = PROJECT_ROOT / "docs" / "review" / "amount_check.csv"
LAKH = 100_000
INCOME_LIMIT_MAX = 10 * LAKH
MONTHLY_MAX = 50_000

# A money amount: a currency mark before it, or a lakh/crore/rupee word after it.
_MONEY = re.compile(
    r"(?:(?:rs\.?|₹|ரூ\.?|ரூபாய்|रु\.?|रुपये)\s*\d[\d,.]*(?:\s*(?:lakhs?|lacs?|crores?|இ?லட்ச\w*|கோடி|लाख|करोड़))?)"
    r"|(?:\d[\d,.]*\s*(?:lakhs?|lacs?|crores?|இ?லட்ச\w*|கோடி|लाख|करोड़|rupees|ரூபாய்|रुपये))",
    re.IGNORECASE,
)
_INCOME = re.compile(r"income|வருமான|आय", re.IGNORECASE)
_MONTHLY = re.compile(r"per month|monthly|a month|மாத|मासिक|प्रति माह", re.IGNORECASE)


def amount_value(phrase: str) -> int | None:
    """The amount in rupees, using the same reading as the answer guardrail."""
    values = []
    for number in numbers_in(phrase):
        try:
            values.append(int(Decimal(number)))
        except (InvalidOperation, ValueError):
            continue
    return max(values) if values else None


def amounts_in(text: str) -> list[tuple[str, int, str]]:
    """(phrase, rupees, context) for each money amount in a passage."""
    found = []
    for match in _MONEY.finditer(text):
        value = amount_value(match.group(0))
        if value is None or value < 100:
            continue
        context = text[max(0, match.start() - 80) : match.end() + 40].replace("\n", " ")
        found.append((match.group(0).strip(), value, context))
    return found


def common_sense_flags(value: int, context: str) -> list[str]:
    flags = []
    if _INCOME.search(context) and value > INCOME_LIMIT_MAX:
        flags.append(f"income limit above Rs.{INCOME_LIMIT_MAX:,}")
    if _MONTHLY.search(context) and value > MONTHLY_MAX:
        flags.append(f"monthly amount above Rs.{MONTHLY_MAX:,}")
    return flags


def read_chunks(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def pair_of(doc_id: str) -> str | None:
    """The other-language version: tn-swwe-policy-note-2024-ta <-> ...-en."""
    for a, b in (("-ta", "-en"), ("-en", "-ta")):
        if doc_id.endswith(a):
            return doc_id[: -len(a)] + b
    return None


def find_suspects(chunks: list[dict[str, object]]) -> list[dict[str, object]]:
    by_doc: dict[str, set[int]] = defaultdict(set)
    rows: list[dict[str, object]] = []
    for chunk in chunks:
        for _, value, _ in amounts_in(str(chunk["text"])):
            by_doc[str(chunk["doc_id"])].add(value)
    for chunk in chunks:
        doc_id, page = str(chunk["doc_id"]), int(chunk["page_start"])  # type: ignore[call-overload]
        is_ocr = str(chunk.get("extraction", "")).startswith("ocr")
        other = pair_of(doc_id)
        for phrase, value, context in amounts_in(str(chunk["text"])):
            flags = common_sense_flags(value, context)
            if is_ocr and other in by_doc and value not in by_doc[other]:
                flags.append(f"not found in {other}")
            if flags:
                rows.append(
                    {
                        "doc_id": doc_id,
                        "page": page,
                        "ocr_reads": phrase,
                        "rupees": value,
                        "reasons": "; ".join(flags),
                        "context": context,
                        "image_shows": "",
                        "verdict": "check",
                    }
                )
    return rows


def vision_read(pdf: Path, page: int, client: object, model: str) -> list[str]:
    """Amounts printed on one page, read from the page image by Claude."""
    import pymupdf  # ingest extra

    with pymupdf.open(pdf) as document:
        png = document[page - 1].get_pixmap(dpi=200).tobytes("png")
    schema = {
        "type": "object",
        "properties": {"amounts": {"type": "array", "items": {"type": "string"}}},
        "required": ["amounts"],
        "additionalProperties": False,
    }
    response = client.messages.create(  # type: ignore[attr-defined]
        model=model,
        max_tokens=4000,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64.standard_b64encode(png).decode(),
                        },
                    },
                    {
                        "type": "text",
                        "text": "List every money amount printed on this page exactly as "
                        "printed, with its unit (for example 'ரூ.2.5 இலட்சம்', 'Rs.1,000', '₹6000'). "
                        "Copy digits and decimal points exactly; do not convert or guess.",
                    },
                ],
            }
        ],
    )
    text = next((b.text for b in response.content if b.type == "text"), '{"amounts": []}')
    return list(json.loads(text).get("amounts", []))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--vision", action="store_true", help="let Claude read flagged pages")
    parser.add_argument("--model", default="claude-opus-5-5")
    args = parser.parse_args()

    chunks_path = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"
    if not chunks_path.is_file():
        print(f"Missing {chunks_path}. Run this on the machine that built the index.")
        return 1
    rows = find_suspects(read_chunks(chunks_path))
    pages = sorted({(str(r["doc_id"]), int(r["page"])) for r in rows})  # type: ignore[call-overload]
    print(f"{len(rows)} suspicious amounts on {len(pages)} pages.")

    if args.vision and pages:
        sources = json.loads((PROJECT_ROOT / "data" / "sources.json").read_text("utf-8"))
        files = {s["doc_id"]: PROJECT_ROOT / "data" / "raw" / s["file"] for s in sources}
        if (
            input(
                f"Claude will read {len(pages)} page images (about US$0.01-0.02 each). Type yes: "
            )
            != "yes"
        ):
            print("Skipped the vision check.")
        else:
            import anthropic

            client = anthropic.Anthropic()
            seen: dict[tuple[str, int], list[str]] = {}
            for doc_id, page in pages:
                try:
                    seen[(doc_id, page)] = vision_read(files[doc_id], page, client, args.model)
                except Exception as error:  # one bad page must not stop the run
                    print(f"  {doc_id} p{page}: could not read ({error})")
            for row in rows:
                printed = seen.get((str(row["doc_id"]), int(row["page"])))  # type: ignore[call-overload]
                if printed is None:
                    continue
                row["image_shows"] = " | ".join(printed)
                image_values = {amount_value(p) for p in printed}
                row["verdict"] = "image agrees" if row["rupees"] in image_values else "check"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "verdict",
        "doc_id",
        "page",
        "ocr_reads",
        "rupees",
        "reasons",
        "image_shows",
        "context",
    ]
    with OUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(
            sorted(rows, key=lambda r: (r["verdict"] != "check", r["doc_id"], r["page"]))
        )
    to_check = sum(r["verdict"] == "check" for r in rows)
    print(f"Wrote {OUT}: {to_check} rows to check against the PDF.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
