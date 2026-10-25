"""Run the evaluation: `uv run python -m schemebot.evaluation [--retrieval-only] [--mode ...]`.

Writes the table to docs/results.md and every question's details to data/eval/runs/.
"""

import argparse
import json
import logging
import sys

from schemebot.config import PROJECT_ROOT, get_settings
from schemebot.evaluation.dataset import load_questions
from schemebot.evaluation.report import git_revision, per_question_rows, render, run_stamp
from schemebot.evaluation.runner import evaluate
from schemebot.ingest.pipeline import CHUNKS_NAME, read_chunks
from schemebot.retrieve.factory import IndexMissingError, build_retriever


def main() -> int:
    parser = argparse.ArgumentParser(description="Per-language evaluation.")
    parser.add_argument("--retrieval-only", action="store_true", help="skip the LLM (no API key)")
    parser.add_argument("--mode", choices=["hybrid", "dense", "sparse"], default="hybrid")
    parser.add_argument("--no-rerank", action="store_true")
    parser.add_argument("--no-judge", action="store_true", help="skip the faithfulness judge")
    parser.add_argument("--report", default=str(PROJECT_ROOT / "docs" / "results.md"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    settings = get_settings()
    full = not args.retrieval_only
    if full and args.mode != "hybrid":
        print("--mode only applies to retrieval-only runs (answers use hybrid search).",
              file=sys.stderr)  # fmt: skip
        return 2

    questions = load_questions(settings.eval_questions_path)
    try:
        retriever = build_retriever(settings, use_reranker=not args.no_rerank)
    except IndexMissingError as error:
        print(error, file=sys.stderr)
        return 1

    answerer = judge = None
    if full:
        from schemebot.evaluation.judge import FaithfulnessJudge
        from schemebot.generate.factory import build_answerer
        from schemebot.generate.llm import ClaudeJsonLlm

        api_key = (
            settings.anthropic_api_key.get_secret_value() if settings.anthropic_api_key else None
        )
        judge_llm = ClaudeJsonLlm(settings.judge_model, api_key, effort="medium")
        if not judge_llm.configured:
            print("No Claude API key configured. Set SCHEMEBOT_ANTHROPIC_API_KEY in .env, or "
                  "run with --retrieval-only.", file=sys.stderr)  # fmt: skip
            return 1
        answerer = build_answerer(settings, retriever)
        judge = None if args.no_judge else FaithfulnessJudge(judge_llm)

    results = evaluate(questions, retriever, settings.refusal_threshold, args.mode, answerer, judge)

    chunks = read_chunks(settings.processed_dir / CHUNKS_NAME)
    run_info = {
        "Run": f"{run_stamp()}, commit {git_revision(PROJECT_ROOT)}",
        "Mode": ("full pipeline" if full else "retrieval only")
        + f", {args.mode} search, reranker {'off' if args.no_rerank else 'on'}",
        "Models": f"{settings.embedding_model}, {settings.reranker_model}"
        + (f", answers {settings.llm_model}, judge {settings.judge_model}" if full else ""),
        "Refusal threshold": f"{settings.refusal_threshold}",
        "Corpus": f"{len({c.doc_id for c in chunks})} documents, {len(chunks)} chunks",
        "Questions": f"{len(questions)} ({sum(q.status == 'verified' for q in questions)} "
        "verified)",
    }
    report = render(results, run_info, full)
    with open(args.report, "w", encoding="utf-8") as file:
        file.write(report)

    runs_dir = settings.data_dir / "eval" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    detail_path = runs_dir / f"{run_stamp()}-{'full' if full else args.mode}.jsonl"
    with detail_path.open("w", encoding="utf-8") as file:
        for row in per_question_rows(results):
            file.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(report)
    print(f"per-question details: {detail_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
