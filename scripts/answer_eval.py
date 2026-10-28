"""Answer-level evaluation script.

Runs Pakkam on verified questions and outputs docs/review/answer_eval.csv
with empty review columns for human grading:
- number_correct (y/n/na)
- citation_supports (y/n)
- unsupported_claim (y/n)
- notes

Does NOT grade anything automatically.
Supports --limit N, resumes where it left off, and stops cleanly on rate limits.
Saves raw responses to data/eval/answer_eval_raw/ for offline inspection.
"""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from schemebot.config import get_settings
from schemebot.generate.factory import build_answerer
from schemebot.generate.llm import LlmUnavailableError
from schemebot.retrieve.factory import build_retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("answer_eval")

DEFAULT_OUTPUT_CSV = PROJECT_ROOT / "docs" / "review" / "answer_eval.csv"
RAW_CACHE_DIR = PROJECT_ROOT / "data" / "eval" / "answer_eval_raw"

CSV_HEADERS = [
    "id",
    "question",
    "status",
    "answer",
    "claims",
    "citations",
    "cited_passage_text",
    "number_correct",
    "citation_supports",
    "unsupported_claim",
    "notes",
]


def load_input_questions(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"Input questions file not found: {path}")

    if path.suffix == ".csv":
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Only use verified=yes if the column exists
            return [
                row for row in reader
                if row.get("verified", "yes").strip().lower() in ("yes", "y", "true", "1")
            ]

    # JSONL fallback
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            # Filter if verified column exists
            if "verified" in item and item["verified"] not in (True, "yes", "y"):
                continue
            rows.append(item)
    return rows


def get_already_processed_ids(csv_path: Path) -> set[str]:
    if not csv_path.is_file():
        return set()
    processed = set()
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            qid = row.get("id")
            if qid:
                processed.add(qid)
    return processed


def main():
    parser = argparse.ArgumentParser(description="Pakkam answer-level evaluation harness.")
    parser.add_argument("--limit", type=int, default=3, help="Maximum questions to run in this batch.")
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "eval" / "questions.jsonl")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_CSV)
    args = parser.parse_args()

    questions = load_input_questions(args.input)
    logger.info("Loaded %d candidate questions from %s", len(questions), args.input)

    processed_ids = get_already_processed_ids(args.output)
    logger.info("Found %d already processed questions in %s", len(processed_ids), args.output)

    pending = [q for q in questions if q.get("id") not in processed_ids]
    logger.info("%d questions pending evaluation", len(pending))

    to_run = pending[:args.limit]
    if not to_run:
        logger.info("No questions to run. Exiting.")
        return

    logger.info("Running batch of %d questions (limit=%d)...", len(to_run), args.limit)

    RAW_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Initialize answerer
    settings = get_settings()
    retriever = build_retriever(settings, use_reranker=True)
    answerer = build_answerer(settings, retriever)

    write_header = not args.output.is_file()
    out_file = args.output.open("a", encoding="utf-8", newline="")
    writer = csv.DictWriter(out_file, fieldnames=CSV_HEADERS)
    if write_header:
        writer.writeheader()
        out_file.flush()

    rate_limited = False
    completed = 0

    for item in to_run:
        qid = item.get("id", "q")
        q_text = item.get("question", "")
        logger.info("Evaluating [%s]: %s", qid, q_text)

        raw_file = RAW_CACHE_DIR / f"{qid}.json"
        
        answer_data = None
        if raw_file.is_file():
            try:
                answer_data = json.loads(raw_file.read_text(encoding="utf-8"))
                logger.info("Loaded cached output for [%s]", qid)
            except Exception:
                answer_data = None

        if answer_data is None:
            try:
                ans = answerer.answer(q_text)
                answer_data = {
                    "question": ans.question,
                    "language": ans.language,
                    "text": ans.text,
                    "refused": ans.refused,
                    "refusal_reason": ans.refusal_reason,
                    "path": getattr(ans, "path", "rag"),
                    "citations": [
                        {
                            "number": c.number,
                            "doc_id": c.doc_id,
                            "scheme": c.scheme,
                            "page": c.page_start,
                            "text": c.text,
                        }
                        for c in ans.citations
                    ],
                    "passages": [p.chunk.text for p in getattr(ans, "passages", [])],
                }
                raw_file.write_text(json.dumps(answer_data, indent=2, ensure_ascii=False), encoding="utf-8")
            except LlmUnavailableError as err:
                logger.warning("Rate limit / quota exhausted while processing [%s]: %s", qid, err)
                rate_limited = True
                break
            except Exception as err:
                logger.error("Error processing [%s]: %s", qid, err)
                continue

        # Format row
        status_val = "MODEL_UNAVAILABLE" if answer_data.get("refusal_reason") == "service_unavailable" else ("INSUFFICIENT_EVIDENCE" if answer_data.get("refused") else "SUPPORTED")
        cites_summary = "; ".join(f"[{c['number']}] {c['doc_id']}:p{c['page']}" for c in answer_data.get("citations", []))
        cites_text = " --- ".join(c.get("text", "") for c in answer_data.get("citations", []))
        
        row = {
            "id": qid,
            "question": q_text,
            "status": status_val,
            "answer": answer_data.get("text", ""),
            "claims": "",  # To be extracted by claim-lite
            "citations": cites_summary,
            "cited_passage_text": cites_text,
            "number_correct": "",  # Empty for human reviewer
            "citation_supports": "",  # Empty for human reviewer
            "unsupported_claim": "",  # Empty for human reviewer
            "notes": "",
        }
        writer.writerow(row)
        out_file.flush()
        completed += 1

    out_file.close()
    logger.info("Batch finished: %d questions written to %s", completed, args.output)
    if rate_limited:
        logger.info("Paused cleanly due to quota limits. Re-run --limit N when quota resets to continue.")


if __name__ == "__main__":
    main()
