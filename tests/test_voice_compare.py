import csv
from datetime import date
from pathlib import Path

import pytest

from schemebot.config import Settings
from schemebot.voice import __main__ as cli
from schemebot.voice.budget import CallBudget
from schemebot.voice.compare import (
    Clip,
    find_clips,
    run,
    said_words_found,
    script_of,
    type_from_name,
    write_csv,
)
from schemebot.voice.stt import BudgetedTranscriber, SttError
from tests.test_stt import make_wav


class FakeStt:
    """Tamil script for ta-IN, Latin letters for en-IN; fails for clips named *bad*."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def transcribe(self, audio: bytes, filename: str, language_code: str) -> str:
        self.calls.append((filename, language_code))
        if "bad" in filename:
            raise SttError("The speech service could not read this recording.")
        return "பிஎம் கிசான் எவ்வளவு" if language_code == "ta-IN" else "pm kisan evlo"


def make_folder(tmp_path: Path) -> Path:
    folder = tmp_path / "clips"
    folder.mkdir()
    for name in ["tanglish-01.wav", "tamil-01.wav", "english-01.wav", "noisy-01.wav", "x.wav"]:
        (folder / name).write_bytes(make_wav(1))
    (folder / "notes.md").write_text("not audio")
    (folder / "said.txt").write_text(
        "tanglish-01.wav | pm kisan evlo panam\nx.wav | tamil | பிஎம் கிசான்\n", encoding="utf-8"
    )
    return folder


def test_find_clips_reads_types_and_said_text(tmp_path: Path) -> None:
    clips = {clip.path.name: clip for clip in find_clips(make_folder(tmp_path))}

    assert sorted(clips) == [
        "english-01.wav",
        "noisy-01.wav",
        "tamil-01.wav",
        "tanglish-01.wav",
        "x.wav",
    ]
    assert clips["tanglish-01.wav"].clip_type == "tanglish"
    assert clips["tanglish-01.wav"].said == "pm kisan evlo panam"
    assert clips["noisy-01.wav"].clip_type == "noisy"
    assert clips["x.wav"].clip_type == "tamil"  # from said.txt, not the name


@pytest.mark.parametrize(
    ("name", "expected"),
    [("Tanglish-02.m4a", "tanglish"), ("noisy_bus.wav", "noisy"), ("clip1.wav", "unknown")],
)
def test_type_from_name(name: str, expected: str) -> None:
    assert type_from_name(name) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("பிஎம் கிசான் எவ்வளவு", "Tamil"),
        ("पीएम किसान", "Devanagari"),
        ("pm kisan evlo", "Latin"),
        ("PM Kisan திட்டம் எவ்வளவு பணம்", "mixed"),
        ("123 ?", "none"),
    ],
)
def test_script_of(text: str, expected: str) -> None:
    assert script_of(text) == expected


def test_word_match_only_within_one_script() -> None:
    assert said_words_found("pm kisan evlo panam", "PM Kisan evlo") == "0.75"
    assert said_words_found("pm kisan evlo panam", "பிஎம் கிசான் எவ்வளவு") == "n/a"
    assert said_words_found("", "anything") == "n/a"


def test_run_sends_each_clip_once_per_code(tmp_path: Path) -> None:
    clip = Clip(tmp_path / "tanglish-01.wav", "tanglish", "pm kisan evlo panam")
    clip.path.write_bytes(make_wav(2))
    stt = FakeStt()

    rows = run([clip], ["ta-IN", "en-IN"], stt, max_bytes=5_000_000, max_seconds=30)

    assert stt.calls == [("tanglish-01.wav", "ta-IN"), ("tanglish-01.wav", "en-IN")]
    tamil, english = rows
    assert tamil["duration_s"] == "2.0"
    assert tamil["transcript_script"] == "Tamil"
    assert tamil["said_words_found"] == "n/a"
    assert english["said_words_found"] == "0.75"
    assert english["call_s"] != ""


def test_run_records_errors_and_skips_bad_files(tmp_path: Path) -> None:
    bad = Clip(tmp_path / "bad.wav", "unknown", "")
    bad.path.write_bytes(make_wav(1))
    long = Clip(tmp_path / "long.wav", "unknown", "")
    long.path.write_bytes(make_wav(31, rate=8000))
    stt = FakeStt()

    rows = run([bad, long], ["ta-IN"], stt, max_bytes=5_000_000, max_seconds=30)

    assert rows[0]["error"] == "The speech service could not read this recording."
    assert "30 seconds" in rows[1]["error"]
    assert stt.calls == [("bad.wav", "ta-IN")]  # the long clip never reached Gnani


def test_write_csv_round_trips_tamil(tmp_path: Path) -> None:
    clip = Clip(tmp_path / "tamil-01.wav", "tamil", "")
    clip.path.write_bytes(make_wav(1))
    rows = run([clip], ["ta-IN"], FakeStt(), max_bytes=5_000_000, max_seconds=30)
    out = tmp_path / "runs" / "out.csv"

    write_csv(rows, out)

    with out.open(encoding="utf-8-sig") as file:
        assert list(csv.DictReader(file))[0]["transcript"] == "பிஎம் கிசான் எவ்வளவு"


# ---------- the command: confirmation and the daily cap ----------


def use_fake_gnani(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, max_calls: int
) -> tuple[FakeStt, CallBudget]:
    stt = FakeStt()
    budget = CallBudget(tmp_path / "calls.json", max_calls, lambda: date(2026, 10, 26))
    settings = Settings(_env_file=None, data_dir=tmp_path / "data")
    monkeypatch.setattr(cli, "get_settings", lambda: settings)
    monkeypatch.setattr(cli, "build_transcriber", lambda s: BudgetedTranscriber(stt, budget))
    return stt, budget


def test_nothing_is_sent_without_yes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    stt, budget = use_fake_gnani(monkeypatch, tmp_path, 100)
    monkeypatch.setattr("builtins.input", lambda prompt: "y")

    assert cli.compare_command(make_folder(tmp_path), ["ta-IN", "en-IN"]) == 0

    assert "This will make 10 Gnani calls" in capsys.readouterr().out
    assert stt.calls == []
    assert budget.used_today() == 0


def test_yes_runs_counts_and_saves(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    stt, budget = use_fake_gnani(monkeypatch, tmp_path, 100)
    monkeypatch.setattr("builtins.input", lambda prompt: "yes")

    assert cli.compare_command(make_folder(tmp_path), ["ta-IN", "en-IN"]) == 0

    assert len(stt.calls) == 10
    assert budget.used_today() == 10
    assert len(list((tmp_path / "data" / "voice" / "runs").glob("compare-*.csv"))) == 1


def test_refuses_to_start_over_the_daily_cap(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    stt, _ = use_fake_gnani(monkeypatch, tmp_path, 9)
    monkeypatch.setattr("builtins.input", lambda prompt: pytest.fail("should not ask"))

    assert cli.compare_command(make_folder(tmp_path), ["ta-IN", "en-IN"]) == 1
    assert stt.calls == []
