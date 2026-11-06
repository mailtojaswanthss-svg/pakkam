"""Narration for the demo video, spoken by Gnani Timbre through the live site's /speak.

    python scripts/video/make_voice.py OUT_DIR

Writes one WAV per scene (narration lowered in pitch so it differs from Pakkam's voice) (and a short version where the script has one), the Tamil question
used as the fake microphone input, and durations.json."""

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
SCRIPT = json.loads((HERE / "script.json").read_text(encoding="utf-8"))
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)


def speak(text: str, language: str, path: Path) -> None:
    if path.exists():
        return
    body = json.dumps({"text": text, "language": language}).encode()
    req = urllib.request.Request(
        SCRIPT["site"] + "/speak", data=body, headers={"Content-Type": "application/json"}
    )
    for attempt in range(4):
        try:
            path.write_bytes(urllib.request.urlopen(req, timeout=90).read())
            return
        except Exception as error:  # rate limit or a slow tunnel: wait and retry
            print("retry", path.name, error)
            time.sleep(8 * (attempt + 1))
    raise SystemExit(f"could not voice {path.name}")


def narrator(raw: Path, out: Path) -> None:
    """The narrator: the same Timbre voice, lowered and slowed slightly, so it is clearly not Pakkam."""
    if not out.exists():
        subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(raw),
                "-af",
                "rubberband=pitch=0.82:formant=preserved:tempo=0.97,equalizer=f=180:t=q:w=1:g=3",
                str(out),
            ],
            check=True,
        )


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(out.stdout.strip())


durations = {}
for scene in SCRIPT["scenes"]:
    for key, suffix in (("vo", ""), ("short_vo", "_short"), ("vo_b", "_b"), ("vo_c", "_c")):
        if key in scene:
            wav = OUT / f"{scene['id']}{suffix}.wav"
            raw = OUT / f"raw_{wav.name}"
            speak(scene[key], "en", raw)
            narrator(raw, wav)
            durations[wav.stem] = duration(wav)
            time.sleep(2)
for name in ("tamil_question", "tamil_answer"):  # Pakkam's own voice (the default Tamil voice)
    speak(SCRIPT[name], "ta", OUT / f"{name}.wav")
    durations[name] = duration(OUT / f"{name}.wav")
(OUT / "durations.json").write_text(json.dumps(durations, indent=2))
print(json.dumps(durations, indent=2))
