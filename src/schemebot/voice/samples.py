"""Short made-up sentences for listening tests of Gnani Timbre (spends real credits).

Every file is named "synthetic-test-..." and goes to data/voice/tts-samples/ (gitignored).
The sentences are written for the test; they are not answers from the scheme documents
and must not be quoted as facts.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import get_args

from schemebot.config import TimbreModel
from schemebot.voice.tts import Speaker, TtsError

MODELS: tuple[TimbreModel, ...] = get_args(TimbreModel)


@dataclass(frozen=True)
class SampleCase:
    text: str
    language_code: str
    listen_for: str


CASES = {
    "tamil": SampleCase(
        "வணக்கம். இது பக்கம் உதவியாளரின் சோதனைக் குரல். உங்களுக்கு எந்தத் திட்டம் பற்றித் தெரிய வேண்டும்?",
        "ta-IN",
        "Is it clear, natural Tamil? Pace, tone, any word said wrongly.",
    ),
    "digits": SampleCase(
        "சோதனைக்காக மூன்று தொகைகள்: Rs. 1,000, Rs. 6,000, Rs. 12,000.",
        "ta-IN",
        "Is each amount read as the right number (one thousand, six thousand, twelve "
        "thousand)? Is 'Rs.' read as rupees or as letters? Is the comma a pause or a word?",
    ),
    "tanglish": SampleCase(
        "Vanakkam, idhu Pakkam assistant oda test voice. Ungalukku endha scheme pathi theriyanum?",
        "ta-IN",
        "Does the Tamil voice say these Latin-letter words as Tamil, as English, or garbled?",
    ),
}


def sample_path(folder: Path, case: str, model: str) -> Path:
    return folder / f"synthetic-test-{case}-{model}.wav"


def make_samples(
    speakers: dict[str, Speaker], cases: list[str], folder: Path
) -> list[tuple[Path, str]]:
    """One call per (case, model). Returns each output file, or the error, in order."""
    folder.mkdir(parents=True, exist_ok=True)
    results = []
    for case in cases:
        sample = CASES[case]
        write_notes(case, folder)
        for model, speaker in speakers.items():
            path = sample_path(folder, case, model)
            try:
                path.write_bytes(speaker.speak(sample.text, sample.language_code))
                results.append((path, "saved"))
            except TtsError as error:
                results.append((path, f"error: {error.message}"))
    return results


def write_notes(case: str, folder: Path) -> None:
    sample = CASES[case]
    lines = [
        "SYNTHETIC TEST AUDIO. A made-up sentence, not a scheme fact. Do not cite.",
        f"Language code: {sample.language_code}",
        f"Text: {sample.text}",
        f"Listen for: {sample.listen_for}",
    ]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"synthetic-test-{case}-notes.txt").write_text("\n".join(lines), encoding="utf-8")
