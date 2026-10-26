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
    parser.add_argument("--no-gloss", action="store_true", help="rerank Tanglish as typed")
    parser.add_argument("--no-judge", action="store_true", help="skip the faithfulness judge")
    parser.add_argument("--workers", type=int, default=1, help="questions answered in parallel")
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
        retriever = build_retriever(
            settings,
            use_reranker=not args.no_rerank,
            gloss_tanglish=False if args.no_gloss else None,
        )
    except IndexMissingError as error:
        print(error, file=sys.stderr)
        return 1

    answerer = judge = None
    if full:
        from schemebot.evaluation.judge import FaithfulnessJudge
        from schemebot.generate.factory import build_answerer, build_llm

        judge_llm = build_llm(settings, "judge")
        if not judge_llm.configured:
            provider = "GEMINI" if settings.llm_provider == "gemini" else "ANTHROPIC"
            key_name = f"SCHEMEBOT_{provider}_API_KEY"
            print(f"No {settings.llm_provider} API key configured. Set {key_name} in .env, or "
                  "run with --retrieval-only.", file=sys.stderr)  # fmt: skip
            return 1
        answerer = build_answerer(settings, retriever)
        judge = None if args.no_judge else FaithfulnessJudge(judge_llm)

    results = evaluate(
        questions, retriever, settings.refusal_threshold, args.mode, answerer, judge, args.workers
    )

    chunks = read_chunks(settings.processed_dir / CHUNKS_NAME)
    llm_models = ""
    if full:
        from schemebot.generate.factory import model_for

        verifier = model_for(settings, "verifier") if settings.verify_answers else "off"
        llm_models = (
            f"; {settings.llm_provider}: answers {model_for(settings, 'answer')}, "
            f"verifier {verifier}, judge {model_for(settings, 'judge')}"
        )
    run_info = {
        "Run": f"{run_stamp()}, commit {git_revision(PROJECT_ROOT)}",
        "Mode": ("full pipeline" if full else "retrieval only")
        + f", {args.mode} search, reranker {'off' if args.no_rerank else 'on'}"
        + ("" if args.no_rerank else f", Tanglish gloss {'off' if args.no_gloss else 'on'}"),
        "Models": f"{settings.embedding_model}@{settings.embedding_revision or 'latest'}, "
        f"{settings.reranker_model}@{settings.reranker_revision or 'latest'}"
        + (llm_models if full else ""),
        "Refusal threshold": f"{settings.refusal_threshold}",
        "Corpus": f"{len({c.doc_id for c in chunks})} documents, {len(chunks)} chunks",
        "Questions": f"{len(questions)} ({sum(q.status == 'verified' for q in questions)} "
        "verified)",
    }
    if full:
        # Calls that failed are refusals or missing verdicts, not wrong answers: show them.
        unavailable = sum(r.refusal_reason == "service_unavailable" for r in results)
        run_info["LLM failures"] = (
            f"{unavailable} answers refused as service_unavailable, "
            f"{sum(r.judge_failed for r in results)} answers the judge could not grade"
        )
    report = render(results, run_info, full)
    with open(args.report, "w", encoding="utf-8") as file:
        file.write(report)

    runs_dir = settings.data_dir / "eval" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    variant = ("full" if full else args.mode) + ("-norerank" if args.no_rerank else "")
    variant += "-nogloss" if args.no_gloss else ""
    detail_path = runs_dir / f"{run_stamp()}-{variant}.jsonl"
    with detail_path.open("w", encoding="utf-8") as file:
        for row in per_question_rows(results):
            file.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(report)
    print(f"per-question details: {detail_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
