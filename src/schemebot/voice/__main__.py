"""Voice tests that spend real Gnani credits. Each one shows how many calls it will make
and waits for you to type yes; every call counts in the daily cap.

Compare language codes on your clips (results in data/voice/runs/, gitignored;
folder layout in voice/compare.py):

    uv run python -m schemebot.voice compare data/voice/tanglish/
    uv run python -m schemebot.voice compare data/voice/tanglish/ --codes ta-IN en-IN

Listen to Timbre on short made-up sentences (WAVs in data/voice/tts-samples/, gitignored;
the cases are in voice/samples.py):

    uv run python -m schemebot.voice tts-samples --cases tamil --models timbre-v2.5 timbre-v3.0
    uv run python -m schemebot.voice tts-samples --cases digits tanglish --models timbre-v2.5

Voice evaluation (voice/evaluate.py): write the reading script, record the clips, then run.
Transcripts are cached next to the clips, so re-runs spend no Gnani credits. Retrieval-only
by default (free); --full also answers each spoken question with the paid LLM and asks first:

    uv run python -m schemebot.voice eval-script
    uv run python -m schemebot.voice eval data/voice/eval/
    uv run python -m schemebot.voice eval data/voice/eval/ --full

Check how money amounts in the corpus would be spoken (free, no calls; voice/numbers.py):

    uv run python -m schemebot.voice amounts
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import cast

from schemebot.config import PROJECT_ROOT, Settings, TimbreModel, get_settings
from schemebot.evaluation.dataset import EvalQuestion, load_questions
from schemebot.evaluation.report import git_revision, per_question_rows, run_stamp
from schemebot.evaluation.runner import evaluate
from schemebot.voice.compare import find_clips, run, write_csv
from schemebot.voice.evaluate import (
    SCRIPT_NAME,
    TRANSCRIPTS_NAME,
    Transcript,
    clip_question_id,
    find_eval_clips,
    load_transcripts,
    missing_clips,
    pick_questions,
    render_report,
    spoken_questions,
    transcribe_missing,
    write_script,
)
from schemebot.voice.numbers import amount_shape, find_amounts, spell_amounts
from schemebot.voice.samples import CASES, MODELS, make_samples
from schemebot.voice.stt import GNANI_LANGUAGE_CODES, build_budget, build_transcriber
from schemebot.voice.tts import BudgetedSpeaker, GnaniTts, Speaker, voices_for

DEFAULT_CODES = ["ta-IN", "en-IN"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Gnani language codes on your clips.")
    sub = parser.add_subparsers(dest="command", required=True)
    compare = sub.add_parser("compare", help="Send each clip once per language code.")
    compare.add_argument("folder", type=Path)
    compare.add_argument("--codes", nargs="+", default=DEFAULT_CODES)
    samples = sub.add_parser("tts-samples", help="Make Timbre WAVs of test sentences.")
    samples.add_argument("--cases", nargs="+", choices=list(CASES), default=["tamil"])
    samples.add_argument("--models", nargs="+", choices=list(MODELS), required=True)
    script = sub.add_parser("eval-script", help="Write the list of questions to record.")
    script.add_argument("--answerable", type=int, default=6, help="per language")
    script.add_argument("--unanswerable", type=int, default=2, help="per language")
    voice_eval = sub.add_parser("eval", help="Typed vs spoken evaluation over your clips.")
    voice_eval.add_argument("folder", type=Path)
    voice_eval.add_argument("--full", action="store_true", help="also answer (paid LLM calls)")
    voice_eval.add_argument("--tanglish-code", default="ta-IN", choices=["ta-IN", "en-IN"])
    sub.add_parser("amounts", help="Show how corpus money amounts would be spoken.")
    args = parser.parse_args()
    if args.command == "amounts":
        return amounts_command()
    if args.command == "compare":
        return compare_command(args.folder, args.codes)
    if args.command == "eval-script":
        return eval_script_command(args.answerable, args.unanswerable)
    if args.command == "eval":
        return eval_command(args.folder, args.full, args.tanglish_code)
    # argparse `choices` already limited --models to the Timbre model names.
    return tts_samples_command(args.cases, cast(list[TimbreModel], args.models))


def compare_command(folder: Path, codes: list[str]) -> int:
    settings = get_settings()
    stt = build_transcriber(settings)
    if stt is None:
        print("No Gnani key: set SCHEMEBOT_GNANI_API_KEY in .env first.", file=sys.stderr)
        return 1
    if not folder.is_dir():
        print(f"No such folder: {folder}", file=sys.stderr)
        return 1

    clips = find_clips(folder)
    calls = len(clips) * len(codes)
    left = stt.budget.remaining()
    for clip in clips:
        print(f"  {clip.path.name:30} {clip.clip_type}")
    print(f"\n{len(clips)} clips x {len(codes)} codes ({', '.join(codes)})")
    print(f"This will make {calls} Gnani calls. {left} calls left today under the daily cap.")
    if calls == 0:
        return 0
    if calls > left:
        print("Not enough calls left today. Raise the cap or use fewer clips.", file=sys.stderr)
        return 1
    if input("Type yes to spend these credits: ").strip().lower() != "yes":
        print("Cancelled. No calls made.")
        return 0

    rows = run(clips, codes, stt, settings.stt_max_bytes, settings.stt_max_seconds)
    out = settings.data_dir / "voice" / "runs" / f"compare-{datetime.now():%Y%m%d-%H%M}.csv"
    write_csv(rows, out)
    errors = sum(1 for row in rows if row["error"])
    print(f"Saved {len(rows)} rows ({errors} errors) to {out}")
    return 0


def tts_samples_command(cases: list[str], models: list[TimbreModel]) -> int:
    settings = get_settings()
    if settings.gnani_api_key is None:
        print("No Gnani key: set SCHEMEBOT_GNANI_API_KEY in .env first.", file=sys.stderr)
        return 1
    budget = build_budget(settings)
    speakers: dict[str, Speaker] = {}
    for model in models:
        voices = voices_for(settings, model)
        key = settings.gnani_api_key.get_secret_value()
        gnani = GnaniTts(key, settings.gnani_tts_url, model, voices)
        speakers[model] = BudgetedSpeaker(gnani, budget)
        for case in cases:
            code = CASES[case].language_code
            print(f"  {case:9} {model:12} voice {voices[code]} ({code})")

    calls = len(cases) * len(models)
    left = budget.remaining()
    print(f"\nThis will make {calls} Gnani calls. {left} calls left today under the daily cap.")
    if calls > left:
        print("Not enough calls left today.", file=sys.stderr)
        return 1
    if input("Type yes to spend these credits: ").strip().lower() != "yes":
        print("Cancelled. No calls made.")
        return 0

    folder = settings.data_dir / "voice" / "tts-samples"
    for path, outcome in make_samples(speakers, cases, folder):
        print(f"  {path.name}: {outcome}")
    print(f"Synthetic test audio in {folder}. Listen, then tell Claude what you heard.")
    return 0


def eval_script_command(answerable: int, unanswerable: int) -> int:
    settings = get_settings()
    picked = pick_questions(load_questions(settings.eval_questions_path), answerable, unanswerable)
    path = settings.data_dir / "voice" / "eval" / SCRIPT_NAME
    write_script(picked, path)
    print(f"{len(picked)} questions to record, listed in {path}.")
    print("Save each clip in that folder as <id>.wav (or <id>-noisy.wav for a noisy take).")
    return 0


def confirm(prompt: str) -> bool:
    return input(f"{prompt} Type yes to continue: ").strip().lower() == "yes"


def eval_command(folder: Path, full: bool, tanglish_code: str) -> int:
    settings = get_settings()
    if not folder.is_dir():
        print(f"No such folder: {folder}", file=sys.stderr)
        return 1
    questions = {q.id: q for q in load_questions(settings.eval_questions_path)}
    clips = [c for c in find_eval_clips(folder) if clip_question_id(c.name) in questions]
    if not clips:
        print("No clips named after a question id (e.g. q001.wav) in that folder.", file=sys.stderr)
        return 1
    codes = {qid: GNANI_LANGUAGE_CODES[q.group] for qid, q in questions.items()}
    codes.update({qid: tanglish_code for qid, q in questions.items() if q.group == "ta-Latn"})

    if not _transcribe_new_clips(settings, folder, clips, codes):
        return 1
    cached = load_transcripts(folder / TRANSCRIPTS_NAME)
    transcripts = [cached[(c.name, codes[clip_question_id(c.name)])] for c in clips]
    return _evaluate_and_report(settings, folder, questions, transcripts, full, tanglish_code)


def _transcribe_new_clips(
    settings: Settings, folder: Path, clips: list[Path], codes: dict[str, str]
) -> bool:
    """Speech to text for clips not in the cache yet. False if the run should stop."""
    cache = folder / TRANSCRIPTS_NAME
    todo = missing_clips(clips, codes, load_transcripts(cache))
    print(f"{len(clips)} clips, {len(clips) - len(todo)} already transcribed (cached).")
    if not todo:
        return True
    stt = build_transcriber(settings)
    if stt is None:
        print("No Gnani key: set SCHEMEBOT_GNANI_API_KEY in .env first.", file=sys.stderr)
        return False
    left = stt.budget.remaining()
    print(f"This will make {len(todo)} Gnani calls. {left} calls left today under the daily cap.")
    if len(todo) > left:
        print("Not enough calls left today.", file=sys.stderr)
        return False
    if not confirm("Speech to text for the new clips."):
        print("Cancelled. No calls made.")
        return False
    transcribe_missing(todo, codes, stt, cache, settings.stt_max_bytes, settings.stt_max_seconds)
    return True


def _evaluate_and_report(
    settings: Settings,
    folder: Path,
    questions: dict[str, EvalQuestion],
    transcripts: list[Transcript],
    full: bool,
    tanglish_code: str,
) -> int:
    from schemebot.retrieve.factory import IndexMissingError, build_retriever

    try:
        retriever = build_retriever(settings)
    except IndexMissingError as error:
        print(error, file=sys.stderr)
        return 1
    answerer = judge = None
    spoken = spoken_questions(questions, transcripts)
    if full:
        from schemebot.evaluation.judge import FaithfulnessJudge
        from schemebot.generate.factory import build_answerer, build_llm

        # Answer, verifier and judge: up to three LLM calls per spoken question.
        if not confirm(f"--full makes up to {3 * len(spoken)} paid LLM calls."):
            print("Cancelled. No LLM calls made.")
            return 0
        answerer = build_answerer(settings, retriever)
        judge = FaithfulnessJudge(build_llm(settings, "judge"))

    typed_ids = sorted({t.question_id for t in transcripts})
    typed = evaluate([questions[qid] for qid in typed_ids], retriever, settings.refusal_threshold)
    heard = evaluate(spoken, retriever, settings.refusal_threshold, answerer=answerer, judge=judge)
    run_info = {
        "Run": f"{run_stamp()}, commit {git_revision(PROJECT_ROOT)}",
        "Mode": "full pipeline on spoken questions" if full else "retrieval only (free)",
        "Speech to text": f"Gnani Prisma v2.5; Tanglish sent as {tanglish_code}",
        "Clips": folder.name,
    }
    report = render_report(typed, heard, transcripts, run_info, full)
    synthetic = "synthetic-" if any("synthetic" in t.clip.lower() for t in transcripts) else ""
    out = settings.data_dir / "voice" / "runs" / f"{synthetic}voice-eval-{run_stamp()}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".md").write_text(report, encoding="utf-8")
    rows = [json.dumps(row, ensure_ascii=False) for row in per_question_rows(heard)]
    out.with_suffix(".jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(report)
    print(f"Saved {out.with_suffix('.md')} (and per-clip details in .jsonl).")
    return 0


def amounts_command() -> int:
    """Every way the corpus writes money, each spoken in Tamil, Hindi and English."""
    from schemebot.ingest.models import Chunk

    settings = get_settings()
    texts = [q.reference for q in load_questions(settings.eval_questions_path)]
    chunks_path = settings.processed_dir / "chunks.jsonl"
    if chunks_path.exists():
        lines = chunks_path.read_text(encoding="utf-8").splitlines()
        texts += [Chunk.model_validate_json(line).text for line in lines if line.strip()]
    else:
        print(f"No {chunks_path}; checking the eval references only.", file=sys.stderr)

    by_shape: dict[str, list[str]] = {}
    for text in texts:
        for amount in find_amounts(text):
            by_shape.setdefault(amount_shape(amount), []).append(amount)

    rows = []
    for shape, amounts in sorted(by_shape.items(), key=lambda item: -len(item[1])):
        example = amounts[0]
        spoken = {code: spell_amounts(example, code) for code in ("ta-IN", "hi-IN", "en-IN")}
        unchanged = spoken["en-IN"] == example
        rows.append([shape, len(amounts), example, "KEPT AS WRITTEN" if unchanged else "spelled",
                     spoken["ta-IN"], spoken["hi-IN"], spoken["en-IN"]])  # fmt: skip
        print(f"{len(amounts):5}  {example:22} -> {spoken['ta-IN']} | {spoken['en-IN']}")

    out = settings.data_dir / "voice" / "runs" / f"amounts-{run_stamp()}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["shape", "count", "example", "result", "tamil", "hindi", "english"])
        writer.writerows(rows)
    kept = sum(1 for row in rows if row[3] != "spelled")
    print(f"\n{len(rows)} ways of writing amounts, {kept} kept as written. Saved {out}.")
    print("Tamil and Hindi wording needs a native speaker's check before the demo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
