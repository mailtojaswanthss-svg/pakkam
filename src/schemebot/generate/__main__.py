"""Ask a question end to end: `uv run python -m schemebot.generate "your question"`."""

import argparse
import sys

from schemebot.config import get_settings
from schemebot.generate.factory import build_answerer
from schemebot.retrieve.factory import IndexMissingError


def main() -> int:
    parser = argparse.ArgumentParser(description="Answer a scheme question with citations.")
    parser.add_argument("question")
    args = parser.parse_args()

    try:
        answerer = build_answerer(get_settings())
    except IndexMissingError as error:
        print(error, file=sys.stderr)
        return 1

    answer = answerer.answer(args.question)
    print(answer.text)
    for citation in answer.citations:
        pages = f"p{citation.page_start}" + (
            f"-{citation.page_end}" if citation.page_end != citation.page_start else ""
        )
        print(f"  [{citation.number}] {citation.scheme}, {citation.doc_id} {pages}")
        print(f"      {citation.source_url}")
    print(f"\n({answer.disclaimer})")
    status = f"refused: {answer.refusal_reason}" if answer.refused else "answered"
    print(f"[{status} | confidence {answer.confidence:.2f} | {answer.timings_ms['total']:.0f} ms]")
    for rejected in answer.rejected:
        print(f"[removed by guardrail ({rejected.reason}): {rejected.sentence.text}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
