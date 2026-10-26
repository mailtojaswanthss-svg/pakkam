"""Compare Gnani language codes on your own clips, e.g. Tanglish sent as ta-IN vs en-IN.

Folder layout (data/voice/ is gitignored, so recordings never reach git):

    data/voice/tanglish/
        tanglish-01.wav       clip type from the filename prefix:
        tamil-01.wav          tanglish, tamil, english or noisy
        noisy-01.m4a
        said.txt              optional, one line per clip:
                              filename | what you said
                              filename | type | what you said   (type overrides the prefix)

The word match is the share of the words you said that appear in the transcript. It is only
computed when both texts are in the same script (a Tamil-script transcript cannot be matched
word for word against Tanglish you typed in Latin letters); otherwise it is "n/a".
"""

import csv
import re
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from schemebot.voice.stt import AUDIO_EXTENSIONS, SttError, Transcriber, check_audio, wav_seconds

CLIP_TYPES = ("tanglish", "tamil", "english", "hindi", "noisy")
SAID_FILE_NAME = "said.txt"
NOT_APPLICABLE = "n/a"

SCRIPT_RANGES = {"Tamil": (0x0B80, 0x0BFF), "Devanagari": (0x0900, 0x097F)}
MIN_SCRIPT_SHARE = 0.8
"""A text counts as one script when at least this share of its letters are in it."""

_WORD = re.compile(r"\w+")

CSV_COLUMNS = [
    "clip",
    "clip_type",
    "duration_s",
    "language_code",
    "transcript",
    "error",
    "call_s",
    "transcript_script",
    "said",
    "said_script",
    "said_words_found",
]


@dataclass
class Clip:
    path: Path
    clip_type: str
    said: str


# ---------- reading the folder ----------


def find_clips(folder: Path) -> list[Clip]:
    said_lines = read_said_file(folder / SAID_FILE_NAME)
    clips = []
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        clip_type, said = said_lines.get(path.name, ("", ""))
        clips.append(Clip(path, clip_type or type_from_name(path.name), said))
    return clips


def read_said_file(path: Path) -> dict[str, tuple[str, str]]:
    """filename -> (type or "", what was said)."""
    if not path.exists():
        return {}
    entries = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = [part.strip() for part in line.split("|")]
        if len(parts) == 2:
            entries[parts[0]] = ("", parts[1])
        elif len(parts) == 3 and parts[1].lower() in CLIP_TYPES:
            entries[parts[0]] = (parts[1].lower(), parts[2])
    return entries


def type_from_name(filename: str) -> str:
    prefix = filename.lower().split("-")[0].split("_")[0]
    return prefix if prefix in CLIP_TYPES else "unknown"


# ---------- comparing texts ----------


def script_of(text: str) -> str:
    """Tamil, Devanagari, Latin, mixed, or none (no letters)."""
    # Tamil and Hindi vowel signs are marks, not letters, so count every char in a script range.
    chars = [char for char in text if char.isalpha() or _script_name(char)]
    if not chars:
        return "none"
    for name in (*SCRIPT_RANGES, "Latin"):
        share = sum(1 for char in chars if _script_name(char) == name) / len(chars)
        if share >= MIN_SCRIPT_SHARE:
            return name
    return "mixed"


def _script_name(char: str) -> str:
    for name, (low, high) in SCRIPT_RANGES.items():
        if low <= ord(char) <= high:
            return name
    return "Latin" if char.isascii() and char.isalpha() else ""


def words(text: str) -> list[str]:
    return [word.lower() for word in _WORD.findall(text)]


def said_words_found(said: str, transcript: str) -> str:
    """Share of said words present in the transcript, as "0.75", or "n/a"."""
    said_script = script_of(said)
    if said_script in ("none", "mixed") or said_script != script_of(transcript):
        return NOT_APPLICABLE
    said_words = words(said)
    heard = set(words(transcript))
    found = sum(1 for word in said_words if word in heard)
    return f"{found / len(said_words):.2f}"


# ---------- running ----------


def run(
    clips: Iterable[Clip],
    language_codes: list[str],
    stt: Transcriber,
    max_bytes: int,
    max_seconds: float,
) -> list[dict[str, str]]:
    rows = []
    for clip in clips:
        audio = clip.path.read_bytes()
        for code in language_codes:
            rows.append(compare_one(clip, audio, code, stt, max_bytes, max_seconds))
    return rows


def compare_one(
    clip: Clip, audio: bytes, code: str, stt: Transcriber, max_bytes: int, max_seconds: float
) -> dict[str, str]:
    duration = wav_seconds(audio)
    row = {
        "clip": clip.path.name,
        "clip_type": clip.clip_type,
        "duration_s": f"{duration:.1f}" if duration is not None else NOT_APPLICABLE,
        "language_code": code,
        "transcript": "",
        "error": "",
        "call_s": "",
        "transcript_script": "",
        "said": clip.said,
        "said_script": script_of(clip.said) if clip.said else "",
        "said_words_found": "",
    }
    started = time.perf_counter()
    try:
        check_audio(audio, clip.path.name, max_bytes, max_seconds)
        transcript = stt.transcribe(audio, clip.path.name, code)
    except SttError as error:
        row["error"] = error.message
        return row
    row["call_s"] = f"{time.perf_counter() - started:.2f}"
    row["transcript"] = transcript
    row["transcript_script"] = script_of(transcript)
    if clip.said:
        row["said_words_found"] = said_words_found(clip.said, transcript)
    return row


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig so Excel shows Tamil and Hindi correctly.
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
