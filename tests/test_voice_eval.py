import csv
import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import SecretStr

from schemebot.config import Settings, get_settings
from schemebot.evaluation.dataset import load_questions
from schemebot.evaluation.runner import evaluate
from schemebot.retrieve.retriever import Retriever
from schemebot.voice import __main__ as cli
from schemebot.voice.budget import CallBudget
from schemebot.voice.evaluate import (
    TRANSCRIPTS_NAME,
    Transcript,
    find_eval_clips,
    load_transcripts,
    missing_clips,
    parse_clip_name,
    pick_questions,
    render_report,
    spoken_questions,
    transcribe_missing,
    write_script,
)
from schemebot.voice.stt import BudgetedTranscriber, SttError
from tests.test_evaluation import question, retriever  # noqa: F401  (pytest fixture)
from tests.test_stt import make_wav


class FakeStt:
    """Hears the question back for good clips; fails for clips named *-bad*."""

    def __init__(self, heard: dict[str, str]) -> None:
        self.heard = heard
        self.calls: list[tuple[str, str]] = []

    def transcribe(self, audio: bytes, filename: str, language_code: str) -> str:
        self.calls.append((filename, language_code))
        if "-bad" in filename:
            raise SttError("The speech service could not read this recording.")
        return self.heard[filename]


def test_pick_is_deterministic_and_balanced() -> None:
    questions = load_questions(get_settings().eval_questions_path)

    picked = pick_questions(questions)

    assert len(picked) == 32
    assert picked == pick_questions(list(reversed(questions)))
    for group in ("en", "ta", "hi", "ta-Latn"):
        in_group = [q for q in picked if q.group == group]
        assert sum(q.answerable for q in in_group) == 6
        assert sum(not q.answerable for q in in_group) == 2


def test_script_lists_file_names_and_text(tmp_path: Path) -> None:
    path = tmp_path / "script.csv"
    write_script([question("q007", "Who can join APY?")], path)

    with path.open(encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))
    assert rows == [
        {
            "save_as": "q007.wav",
            "language": "English",
            "answerable": "True",
            "read_this_aloud": "Who can join APY?",
        }
    ]


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("q001.wav", ("q001", "")),
        ("Q012-noisy.m4a", ("q012", "noisy")),
        ("q003-synthetic-take2.wav", ("q003", "synthetic-take2")),
        ("notes.wav", None),
    ],
)
def test_parse_clip_name(name: str, expected: tuple[str, str] | None) -> None:
    assert parse_clip_name(name) == expected


def make_clips(folder: Path, names: list[str]) -> list[Path]:
    folder.mkdir(exist_ok=True)
    for name in names:
        (folder / name).write_bytes(make_wav(1))
    (folder / "script.csv").write_text("not audio")
    return find_eval_clips(folder)


def test_transcripts_are_cached_and_failures_retried(tmp_path: Path) -> None:
    clips = make_clips(tmp_path / "clips", ["q1.wav", "q2-bad.wav"])
    codes = {"q1": "ta-IN", "q2": "en-IN"}
    cache = tmp_path / "clips" / TRANSCRIPTS_NAME
    stt = FakeStt({"q1.wav": "heard one"})

    transcribe_missing(clips, codes, stt, cache, 5_000_000, 30)

    cached = load_transcripts(cache)
    assert cached[("q1.wav", "ta-IN")].transcript == "heard one"
    assert cached[("q2-bad.wav", "en-IN")].error
    assert [c.name for c in missing_clips(clips, codes, cached)] == ["q2-bad.wav"]
    # A different language code for the same clip is a new transcript.
    assert len(missing_clips(clips, {"q1": "en-IN", "q2": "en-IN"}, cached)) == 2


def test_spoken_questions_keep_gold_and_use_the_transcript() -> None:
    original = question("q1", "Who can join Atal Pension Yojana?")
    transcripts = [
        Transcript("q1.wav", "q1", "en-IN", "who can join atal pension", 300.0),
        Transcript("q1-noisy.wav", "q1", "en-IN", "", 280.0, "could not read"),
        Transcript("q1-quiet.wav", "q1", "en-IN", "a", 250.0),
    ]

    [spoken] = spoken_questions({"q1": original}, transcripts)

    assert spoken.id == "q1.wav"
    assert spoken.question == "who can join atal pension"
    assert spoken.gold == original.gold


def test_report_compares_typed_and_spoken_with_n(retriever: Retriever) -> None:  # noqa: F811
    questions = {
        "q1": question("q1", "Who can join Atal Pension Yojana aged 18 to 40?"),
        "q2": question("q2", "Quel temps fait-il?", answerable=False),
    }
    transcripts = [
        Transcript("q1.wav", "q1", "en-IN", "who can join atal pension yojana", 410.0),
        Transcript("q1-noisy.wav", "q1", "en-IN", "blah blah blah", 520.0),
        Transcript("q2.wav", "q2", "en-IN", "", 300.0, "could not read"),
    ]
    typed = evaluate(list(questions.values()), retriever, 0.3)
    spoken = evaluate(spoken_questions(questions, transcripts), retriever, 0.3)

    report = render_report(typed, spoken, transcripts, {"Run": "test"}, full=False)

    assert "Draft questions, not yet native-speaker verified." in report
    assert "SYNTHETIC" not in report
    english = next(line for line in report.splitlines() if line.startswith("| English"))
    cells = [cell.strip() for cell in english.strip("|").split("|")]
    # Clips, STT failed, recall, correct refusal, false refusal. The garbled noisy take is
    # refused, so the spoken false-refusal rate rises; q2's failed clip has no spoken result.
    assert cells[1:6] == [
        "3",
        "1",
        "100% (n=1) → 100% (n=2)",
        "100% (n=1) → –",
        "0% (n=1) → 50% (n=2)",
    ]
    assert "| Noisy clips | 1 |" in report


def test_synthetic_clips_mark_the_report(retriever: Retriever) -> None:  # noqa: F811
    questions = {"q1": question("q1", "Who can join Atal Pension Yojana aged 18 to 40?")}
    transcripts = [Transcript("q1-synthetic.wav", "q1", "en-IN", "who can join apy", 400.0)]
    typed = evaluate(list(questions.values()), retriever, 0.3)

    report = render_report(typed, [], transcripts, {}, full=False)

    assert "SYNTHETIC CLIPS" in report


# ---------- the command: credits are only spent after yes ----------


@pytest.fixture
def eval_setup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    retriever: Retriever,  # noqa: F811
) -> tuple[Path, FakeStt, CallBudget]:
    eval_dir = tmp_path / "data" / "eval"
    eval_dir.mkdir(parents=True)
    rows = [
        question("q1", "Who can join Atal Pension Yojana aged 18 to 40?"),
        question("q2", "Quel temps fait-il?", answerable=False, group="ta-Latn"),
    ]
    (eval_dir / "questions.jsonl").write_text("\n".join(q.model_dump_json() for q in rows))
    settings = Settings(_env_file=None, data_dir=tmp_path / "data", gnani_api_key=SecretStr("k"))
    stt = FakeStt({"q1.wav": "who can join atal pension", "q2.wav": "quel temps"})
    budget = CallBudget(tmp_path / "calls.json", 100, lambda: date(2026, 10, 26))
    monkeypatch.setattr(cli, "get_settings", lambda: settings)
    monkeypatch.setattr(cli, "build_transcriber", lambda s: BudgetedTranscriber(stt, budget))
    monkeypatch.setattr("schemebot.retrieve.factory.build_retriever", lambda s: retriever)
    folder = tmp_path / "data" / "voice" / "eval"
    folder.mkdir(parents=True)
    make_clips(folder, ["q1.wav", "q2.wav"])
    return folder, stt, budget


def test_eval_asks_before_spending_and_then_caches(
    eval_setup: tuple[Path, FakeStt, CallBudget], monkeypatch: pytest.MonkeyPatch
) -> None:
    folder, stt, budget = eval_setup
    monkeypatch.setattr("builtins.input", lambda prompt: "no")
    assert cli.eval_command(folder, full=False, tanglish_code="en-IN") == 1
    assert stt.calls == []

    monkeypatch.setattr("builtins.input", lambda prompt: "yes")
    assert cli.eval_command(folder, full=False, tanglish_code="en-IN") == 0
    assert stt.calls == [("q1.wav", "en-IN"), ("q2.wav", "en-IN")]  # Tanglish sent as en-IN
    assert budget.used_today() == 2

    # Re-run: everything cached, so no prompt and no calls.
    monkeypatch.setattr("builtins.input", lambda prompt: pytest.fail("should not ask"))
    assert cli.eval_command(folder, full=False, tanglish_code="en-IN") == 0
    assert len(stt.calls) == 2
    reports = sorted((folder.parent / "runs").glob("voice-eval-*.md"))
    assert reports and "retrieval only (free)" in reports[-1].read_text()
    details = sorted((folder.parent / "runs").glob("voice-eval-*.jsonl"))
    assert [json.loads(line)["id"] for line in details[-1].read_text().splitlines()] == [
        "q1.wav",
        "q2.wav",
    ]


def test_eval_script_writes_32_rows(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    settings = Settings(_env_file=None, data_dir=tmp_path / "data")
    real = get_settings().eval_questions_path
    monkeypatch.setattr(cli, "get_settings", lambda: settings)
    monkeypatch.setattr(Settings, "eval_questions_path", property(lambda self: real))

    assert cli.eval_script_command(6, 2) == 0

    script = tmp_path / "data" / "voice" / "eval" / "script.csv"
    with script.open(encoding="utf-8-sig") as file:
        assert len(list(csv.DictReader(file))) == 32


def test_amounts_command_lists_formats_without_calls(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    settings = Settings(_env_file=None, data_dir=tmp_path / "data")
    real = get_settings().eval_questions_path
    monkeypatch.setattr(cli, "get_settings", lambda: settings)
    monkeypatch.setattr(Settings, "eval_questions_path", property(lambda self: real))
    monkeypatch.setattr(cli, "build_transcriber", lambda s: pytest.fail("no Gnani calls"))

    assert cli.amounts_command() == 0

    assert "kept as written" in capsys.readouterr().out
    assert list((tmp_path / "data" / "voice" / "runs").glob("amounts-*.csv"))
