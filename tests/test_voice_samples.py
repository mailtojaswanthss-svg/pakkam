from datetime import date
from pathlib import Path

import pytest
from pydantic import SecretStr

from schemebot.config import Settings
from schemebot.voice import __main__ as cli
from schemebot.voice.budget import CallBudget
from schemebot.voice.samples import CASES, make_samples
from schemebot.voice.tts import TtsError


class FakeTimbre:
    """Stands in for GnaniTts; records every call made through any instance."""

    calls: list[tuple[str, str, str]] = []

    def __init__(self, api_key: str, url: str, model: str, voices: dict[str, str]) -> None:
        self.model = model

    def speak(self, text: str, language_code: str) -> bytes:
        FakeTimbre.calls.append((self.model, text, language_code))
        if "Rs." in text:
            raise TtsError("The speech service could not read this answer aloud.")
        return b"RIFF-fake"


@pytest.fixture
def fake_gnani(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> CallBudget:
    FakeTimbre.calls = []
    budget = CallBudget(tmp_path / "calls.json", 100, lambda: date(2026, 10, 26))
    settings = Settings(_env_file=None, data_dir=tmp_path / "data", gnani_api_key=SecretStr("k"))
    monkeypatch.setattr(cli, "get_settings", lambda: settings)
    monkeypatch.setattr(cli, "build_budget", lambda s: budget)
    monkeypatch.setattr(cli, "GnaniTts", FakeTimbre)
    return budget


def test_samples_are_labelled_synthetic(tmp_path: Path) -> None:
    speaker = FakeTimbre("k", "url", "timbre-v2.5", {})

    results = make_samples({"timbre-v2.5": speaker}, ["tamil", "digits"], tmp_path)

    assert [(path.name, outcome) for path, outcome in results] == [
        ("synthetic-test-tamil-timbre-v2.5.wav", "saved"),
        ("synthetic-test-digits-timbre-v2.5.wav", "error: The speech service could not read "
         "this answer aloud."),
    ]  # fmt: skip
    notes = (tmp_path / "synthetic-test-digits-notes.txt").read_text(encoding="utf-8")
    assert notes.startswith("SYNTHETIC TEST AUDIO")
    assert "Rs. 1,000, Rs. 6,000, Rs. 12,000" in notes


def test_every_case_is_spoken_with_a_tamil_voice() -> None:
    assert {case.language_code for case in CASES.values()} == {"ta-IN"}


def test_nothing_is_sent_without_yes(
    fake_gnani: CallBudget, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt: "no")

    assert cli.tts_samples_command(["tamil"], ["timbre-v2.5", "timbre-v3.0"]) == 0

    out = capsys.readouterr().out
    assert "This will make 2 Gnani calls" in out
    assert "Asmita" in out and "Shivani" in out
    assert FakeTimbre.calls == []
    assert fake_gnani.used_today() == 0


def test_yes_makes_one_call_per_case_and_model(
    fake_gnani: CallBudget, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt: "yes")

    assert cli.tts_samples_command(["tamil"], ["timbre-v2.5", "timbre-v3.0"]) == 0

    assert [call[0] for call in FakeTimbre.calls] == ["timbre-v2.5", "timbre-v3.0"]
    assert fake_gnani.used_today() == 2
    folder = tmp_path / "data" / "voice" / "tts-samples"
    assert (folder / "synthetic-test-tamil-timbre-v3.0.wav").read_bytes() == b"RIFF-fake"


def test_failed_calls_still_count(fake_gnani: CallBudget, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt: "yes")

    cli.tts_samples_command(["digits", "tanglish"], ["timbre-v2.5"])

    assert fake_gnani.used_today() == 2
