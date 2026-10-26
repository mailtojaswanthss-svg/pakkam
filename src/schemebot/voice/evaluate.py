"""Voice evaluation: the same questions typed and spoken, side by side, per language.

1. `pick_questions` chooses which eval questions to record and `write_script` saves a
   reading script (data/voice/eval/script.csv).
2. Record one clip per row, named after the question id: q001.wav, or q001-noisy.wav for a
   noisy take. Files whose name contains "synthetic" mark the whole report as synthetic.
3. `transcribe_missing` sends each clip to Gnani once and caches the transcript in
   transcripts.jsonl next to the clips, so re-running the report costs no credits.
4. The spoken questions (transcripts) go through the normal evaluation runner, next to the
   typed originals, and `render_report` writes one table per language.

Everything lives under data/voice/ (gitignored): recordings and transcripts never reach git.
"""

import csv
import json
import math
import re
import time
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from schemebot.evaluation.dataset import GROUPS, EvalQuestion
from schemebot.evaluation.metrics import QuestionResult, percentile, rate, recall_at_k
from schemebot.evaluation.report import GROUP_NAMES
from schemebot.voice.stt import AUDIO_EXTENSIONS, SttError, Transcriber, check_audio

TRANSCRIPTS_NAME = "transcripts.jsonl"
SCRIPT_NAME = "script.csv"
RECALL_K = 5
_CLIP_NAME = re.compile(r"^(q\d+)(?:-([a-z0-9-]+))?$", re.IGNORECASE)


# ---------- choosing and recording ----------


def pick_questions(
    questions: Sequence[EvalQuestion], answerable: int = 6, unanswerable: int = 2
) -> list[EvalQuestion]:
    """The first n answerable and unanswerable questions of each language, by id order.

    Deterministic, so the same list comes back every time and nobody hand-picks easy ones.
    """
    picked = []
    for group in GROUPS:
        in_group = sorted((q for q in questions if q.group == group), key=lambda q: q.id)
        picked += [q for q in in_group if q.answerable][:answerable]
        picked += [q for q in in_group if not q.answerable][:unanswerable]
    return picked


def write_script(questions: Sequence[EvalQuestion], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["save_as", "language", "answerable", "read_this_aloud"])
        for q in questions:
            writer.writerow([f"{q.id}.wav", GROUP_NAMES[q.group], q.answerable, q.question])


def parse_clip_name(filename: str) -> tuple[str, str] | None:
    """ "q001-noisy.wav" -> ("q001", "noisy"); "q001.wav" -> ("q001", ""); else None."""
    match = _CLIP_NAME.match(Path(filename).stem)
    if not match:
        return None
    return match.group(1).lower(), (match.group(2) or "").lower()


def clip_question_id(filename: str) -> str:
    """The question id a clip is named after, or "" if the name does not follow the pattern."""
    parsed = parse_clip_name(filename)
    return parsed[0] if parsed else ""


def find_eval_clips(folder: Path) -> list[Path]:
    return sorted(
        path
        for path in folder.iterdir()
        if path.suffix.lower() in AUDIO_EXTENSIONS and parse_clip_name(path.name)
    )


# ---------- speech to text, cached ----------


@dataclass
class Transcript:
    clip: str
    question_id: str
    language_code: str
    transcript: str
    stt_ms: float
    error: str = ""


def load_transcripts(path: Path) -> dict[tuple[str, str], Transcript]:
    """(clip, language code) -> transcript from earlier runs."""
    if not path.exists():
        return {}
    cached = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = Transcript(**json.loads(line))
            cached[(item.clip, item.language_code)] = item
    return cached


def missing_clips(
    clips: Sequence[Path], codes: dict[str, str], cached: dict[tuple[str, str], Transcript]
) -> list[Path]:
    """Clips with no successful cached transcript for their language code.

    `codes` maps question id -> Gnani language code.
    """
    missing = []
    for clip in clips:
        done = cached.get((clip.name, codes[clip_question_id(clip.name)]))
        if done is None or done.error:
            missing.append(clip)
    return missing


def transcribe_missing(
    clips: Sequence[Path],
    codes: dict[str, str],
    stt: Transcriber,
    cache_path: Path,
    max_bytes: int,
    max_seconds: float,
) -> list[Transcript]:
    """Send each clip once and append the result to the cache straight away."""
    new = []
    for clip in clips:
        question_id = clip_question_id(clip.name)
        code = codes[question_id]
        audio = clip.read_bytes()
        started = time.perf_counter()
        try:
            check_audio(audio, clip.name, max_bytes, max_seconds)
            text, error = stt.transcribe(audio, clip.name, code), ""
        except SttError as failure:
            text, error = "", failure.message
        item = Transcript(
            clip.name, question_id, code, text, (time.perf_counter() - started) * 1000, error
        )
        with cache_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")
        new.append(item)
    return new


def spoken_questions(
    questions: dict[str, EvalQuestion], transcripts: Sequence[Transcript]
) -> list[EvalQuestion]:
    """Each heard clip as an eval question: same gold pages, the transcript as the text.

    The id becomes the clip name so two takes of one question stay separate.
    """
    spoken = []
    for item in transcripts:
        if item.error or len(item.transcript.strip()) < 3:
            continue
        original = questions[item.question_id]
        spoken.append(original.model_copy(update={"id": item.clip, "question": item.transcript}))
    return spoken


# ---------- report ----------


def _pct(flags: Sequence[bool]) -> str:
    if not flags:
        return "–"
    return f"{rate(flags) * 100:.0f}% (n={len(flags)})"


def _ms(values: Sequence[float]) -> str:
    if not values:
        return "–"
    p50, p95 = percentile(values, 50), percentile(values, 95)
    return "–" if math.isnan(p50) else f"{p50:,.0f} / {p95:,.0f}"


def _row(
    name: str,
    typed: Sequence[QuestionResult],
    spoken: Sequence[QuestionResult],
    transcripts: Sequence[Transcript],
    full: bool,
) -> str:
    def recall(results: Sequence[QuestionResult]) -> list[bool]:
        return [recall_at_k(r.relevant, RECALL_K) for r in results if r.answerable]

    def refusals(results: Sequence[QuestionResult], answerable: bool) -> list[bool]:
        return [r.refused for r in results if r.answerable == answerable]

    cells = [
        name,
        str(len(transcripts)),
        str(sum(1 for t in transcripts if t.error or len(t.transcript.strip()) < 3)),
        f"{_pct(recall(typed))} → {_pct(recall(spoken))}",
        f"{_pct(refusals(typed, False))} → {_pct(refusals(spoken, False))}",
        f"{_pct(refusals(typed, True))} → {_pct(refusals(spoken, True))}",
        _ms([t.stt_ms for t in transcripts if not t.error]),
    ]
    if full:
        supported = [s for r in spoken for s in r.sentences_supported]
        citations = [c for r in spoken if r.answerable for c in r.citations_relevant]
        totals = [r.total_ms for r in spoken if r.total_ms is not None]
        cells += [_pct(supported), _pct(citations), _ms(totals)]
    return "| " + " | ".join(cells) + " |"


def render_report(
    typed: Sequence[QuestionResult],
    spoken: Sequence[QuestionResult],
    transcripts: Sequence[Transcript],
    run_info: dict[str, str],
    full: bool,
) -> str:
    header = ["Language", "Clips", "STT failed", f"Recall@{RECALL_K} typed → spoken",
              "Correct refusal typed → spoken", "False refusal typed → spoken",
              "STT ms p50 / p95"]  # fmt: skip
    if full:
        header += ["Faithfulness (spoken, model-judged)", "Citation acc. (spoken)",
                   "Answer ms p50 / p95 (after STT)"]  # fmt: skip

    lines = ["# Voice evaluation", ""]
    if any("synthetic" in t.clip.lower() for t in transcripts):
        lines += ["> **SYNTHETIC CLIPS.** A plumbing test only. Not evidence for any claim.", ""]
    if any(r.status == "draft" for r in typed):
        lines += ["> Draft questions, not yet native-speaker verified.", ""]
    lines += [f"- **{key}:** {value}" for key, value in run_info.items()]
    lines += ["", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]

    groups = {r.id: r.group for r in typed}
    for group in GROUPS:
        rows = _subset(typed, spoken, transcripts, _in_group(groups, group))
        if rows[2]:
            lines.append(_row(GROUP_NAMES[group], *rows, full))
    noisy = _subset(typed, spoken, transcripts, lambda t: "noisy" in t.clip.lower())
    if noisy[2]:
        lines.append(_row("Noisy clips", *noisy, full))
    lines.append(_row("**All**", typed, spoken, transcripts, full))
    lines += [
        "",
        "Typed: the original question text. Spoken: what Gnani speech to text heard from the "
        "clip, sent through the same pipeline. n is the number of questions or clips behind "
        "each percentage. A clip whose speech to text failed counts under STT failed and is "
        "left out of the spoken columns.",
    ]
    return "\n".join(lines) + "\n"


def _in_group(groups: dict[str, str], group: str) -> Callable[[Transcript], bool]:
    return lambda item: groups.get(item.question_id) == group


def _subset(
    typed: Sequence[QuestionResult],
    spoken: Sequence[QuestionResult],
    transcripts: Sequence[Transcript],
    keep: Callable[[Transcript], bool],
) -> tuple[list[QuestionResult], list[QuestionResult], list[Transcript]]:
    chosen = [t for t in transcripts if keep(t)]
    ids = {t.question_id for t in chosen}
    clips = {t.clip for t in chosen}
    return [r for r in typed if r.id in ids], [r for r in spoken if r.id in clips], chosen
