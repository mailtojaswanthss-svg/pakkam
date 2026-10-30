"""Fair timing and quality comparison across LLM providers and reasoning modes.

Compares:
- Gemini with thinking=MEDIUM (normal RAG prompt)
- Gemini with thinking=LOW (normal RAG prompt)
- Gemini with thinking=LOW (short voice prompt)
- Claude (if configured in .env and requested)

Metrics recorded per question (n=3 to 5):
- Retrieval time (ms)
- LLM response time (ms)
- Total answer time (ms)
- Output character length and sentence count
- Citation & claim check pass/fail (using deterministic quote and number checks)

All figures carry question ID, n, and source script attribution.
"""

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from schemebot.config import Settings
from schemebot.generate.factory import _build_provider_llm
from schemebot.generate.guardrails import DraftSentence, check_answer
from schemebot.generate.prompt import (
    ANSWER_SCHEMA,
    SYSTEM_PROMPT,
    VOICE_SYSTEM_PROMPT,
    build_user_message,
)
from schemebot.ingest.langid import detect_language
from schemebot.retrieve.factory import build_retriever
from schemebot.retrieve.retriever import Retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_QUESTION_IDS = ["q001", "q004", "q002"]


@dataclass
class RunMeasurement:
    question_id: str
    question_text: str
    provider: str
    model: str
    mode: str  # "normal" or "voice"
    thinking: str  # "medium", "low", etc.
    retrieval_ms: float
    llm_ms: float
    total_ms: float
    output_chars: int
    sentence_count: int
    claims_passed: bool
    answerable: bool
    answer_text: str


def load_selected_questions(questions_file: Path, target_ids: list[str]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    with questions_file.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            item = json.loads(line)
            qid = item.get("id")
            if qid in target_ids:
                selected[qid] = item
    return [selected[qid] for qid in target_ids if qid in selected]


def run_single_comparison(
    question: dict[str, Any],
    retriever: Retriever,
    settings: Settings,
    provider: str,
    mode: str,
    thinking: str,
) -> RunMeasurement:
    qid = question["id"]
    q_text = question["question"]
    lang = detect_language(q_text)

    # 1. Retrieve passages (local, 0 API calls)
    t0 = time.perf_counter()
    retrieval = retriever.retrieve(q_text)
    retrieval_ms = (time.perf_counter() - t0) * 1000.0

    # In voice mode, top 3 passages are used; in normal mode, all retrieved passages
    passages = retrieval.passages[:3] if mode == "voice" else retrieval.passages

    # 2. Select prompt mode
    system_prompt = VOICE_SYSTEM_PROMPT if mode == "voice" else SYSTEM_PROMPT
    user_prompt = build_user_message(q_text, lang, passages)

    # 3. Build specific LLM instance
    provider_settings = settings.model_copy(
        update={
            "llm_provider": provider,
            "llm_effort": thinking,
        }
    )
    llm = _build_provider_llm(provider_settings, "answer", provider)  # type: ignore[arg-type]

    # 4. Query LLM and record timing
    t_llm0 = time.perf_counter()
    reply: dict[str, Any] = {}
    for attempt in range(3):
        try:
            reply = llm.complete_json(system_prompt, user_prompt, ANSWER_SCHEMA)
            break
        except Exception as err:
            if "503" in str(err) and attempt < 2:
                logger.warning(
                    "Gemini 503 transient spike on attempt %d; sleeping 5s...", attempt + 1
                )
                time.sleep(5.0)
            else:
                raise
    llm_ms = (time.perf_counter() - t_llm0) * 1000.0
    total_ms = retrieval_ms + llm_ms

    answerable = bool(reply.get("answerable", False))
    raw_sentences = reply.get("sentences", [])
    sentences = [s.get("text", "") for s in raw_sentences if isinstance(s, dict)]
    full_text = " ".join(sentences)

    # 5. Deterministic claim verification (guardrails check on citations & numbers)
    drafts = [
        DraftSentence(s.get("text", "").strip(), s.get("sources", []))
        for s in raw_sentences
        if isinstance(s, dict)
    ]
    passage_texts = [p.chunk.text for p in passages]
    check_result = check_answer(drafts, passage_texts)
    claims_passed = len(check_result.rejected) == 0

    model_name = settings.gemini_model if provider == "gemini" else settings.llm_model

    return RunMeasurement(
        question_id=qid,
        question_text=q_text,
        provider=provider,
        model=model_name,
        mode=mode,
        thinking=thinking,
        retrieval_ms=round(retrieval_ms, 1),
        llm_ms=round(llm_ms, 1),
        total_ms=round(total_ms, 1),
        output_chars=len(full_text),
        sentence_count=len(sentences),
        claims_passed=claims_passed,
        answerable=answerable,
        answer_text=full_text,
    )


def format_markdown_report(runs: list[RunMeasurement], n_questions: int) -> str:
    lines = [
        "# LLM Provider & Mode Comparison Report",
        "",
        "**Source script:** `scripts/compare_llm_providers.py`  ",
        f"**Sample size:** n={n_questions} questions  ",
        f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  ",
        "",
        "## Summary Results",
        "",
        "| Provider | Model | Mode | Thinking | LLM (ms) | Total (ms) | Chars | Claims |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    from collections import defaultdict

    groups: dict[tuple[str, str, str, str], list[RunMeasurement]] = defaultdict(list)
    for r in runs:
        groups[(r.provider, r.model, r.mode, r.thinking)].append(r)

    for (prov, model, mode, thinking), group in groups.items():
        avg_llm = sum(g.llm_ms for g in group) / len(group)
        avg_total = sum(g.total_ms for g in group) / len(group)
        avg_chars = sum(g.output_chars for g in group) / len(group)
        pass_rate = sum(1 for g in group if g.claims_passed) / len(group) * 100.0
        lines.append(
            f"| `{prov}` | `{model}` | {mode} | {thinking} | "
            f"{avg_llm:.1f} | {avg_total:.1f} | {avg_chars:.0f} | {pass_rate:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Per-Question Details",
            "",
            "| QID | Provider | Mode | Thinking | Retrieve | LLM (ms) | Total | Claims | Excerpt |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
    )

    for r in runs:
        safe_text = r.answer_text.replace("|", "/")
        if len(safe_text) > 60:
            safe_text = safe_text[:57] + "..."
        pass_str = "PASS" if r.claims_passed else "FAIL"
        lines.append(
            f"| {r.question_id} | `{r.provider}` | {r.mode} | {r.thinking} | "
            f"{r.retrieval_ms} | {r.llm_ms} | {r.total_ms} | {pass_str} | {safe_text} |"
        )

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            "- Default recommendation is determined strictly by measured latency and claim accuracy.",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fair timing comparison across LLM providers")
    parser.add_argument(
        "--questions",
        nargs="+",
        default=DEFAULT_QUESTION_IDS,
        help="Question IDs to benchmark (default: 3 draft questions)",
    )
    parser.add_argument(
        "--include-claude",
        action="store_true",
        help="Include Claude API calls in benchmark if key is configured",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm execution of live LLM calls",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/review/LLM_PROVIDER_COMPARISON.md"),
        help="Path to write the markdown report",
    )
    args = parser.parse_args()

    settings = Settings()
    questions_file = settings.data_dir / "eval" / "questions.jsonl"
    questions = load_selected_questions(questions_file, args.questions)
    n = len(questions)

    configs = [
        ("gemini", "normal", "medium"),
        ("gemini", "normal", "low"),
        ("gemini", "voice", "low"),
    ]
    if args.include_claude and settings.anthropic_api_key:
        configs.append(("claude", "normal", "medium"))
        configs.append(("claude", "voice", "low"))

    gemini_calls = n * 3
    claude_calls = n * 2 if args.include_claude else 0
    total_calls = gemini_calls + claude_calls

    print("\n================ LLM COMPARISON PLAN ================")
    print(f"Questions ({n}): {[q['id'] for q in questions]}")
    print(f"Configurations ({len(configs)}): {configs}")
    print("Total API Calls Required:")
    print(f"  - Gemini API Calls: {gemini_calls}")
    print(f"  - Claude API Calls: {claude_calls}")
    print("  - Gnani TTS/STT Calls: 0 (No voice calls in Step 3)")
    print(f"  - Total LLM Calls: {total_calls}")
    print("======================================================\n")

    if not args.yes:
        print("Dry run complete. To execute real calls, user approval is required first.")
        return

    logger.info("Building retriever once for all runs...")
    retriever = build_retriever(settings)

    runs: list[RunMeasurement] = []
    for q in questions:
        for prov, mode, thinking in configs:
            logger.info("Benchmarking %s with %s (%s, %s)...", q["id"], prov, mode, thinking)
            measurement = run_single_comparison(q, retriever, settings, prov, mode, thinking)
            runs.append(measurement)
            time.sleep(2.0)

    report_md = format_markdown_report(runs, n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report_md, encoding="utf-8")
    logger.info("Report written to %s", args.output)


if __name__ == "__main__":
    main()
