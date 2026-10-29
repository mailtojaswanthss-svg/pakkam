"""Audio conversion and validation using ffmpeg.

Converts any supported input format (WAV, MP3, M4A, OGG, WEBM, FLAC, AAC) into
standard 16 kHz mono 16-bit PCM WAV. Caps audio at 30 seconds and raises a clear
error if audio exceeds the time limit.
"""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

from schemebot.voice.stt import SttError

MAX_AUDIO_SECONDS = 30.0
TARGET_SAMPLE_RATE = 16000
TARGET_CHANNELS = 1


def get_audio_duration(wav_bytes: bytes) -> float:
    """Calculate the duration in seconds of a standard WAV buffer."""
    try:
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            if rate > 0:
                return frames / float(rate)
    except Exception:
        pass
    # Fallback based on 16 kHz 16-bit mono PCM (32,000 bytes/sec)
    pcm_bytes = max(len(wav_bytes) - 44, 0)
    return pcm_bytes / 32000.0


def convert_to_wav16k(
    audio_bytes: bytes,
    filename: str = "audio.wav",
    max_seconds: float = MAX_AUDIO_SECONDS,
) -> bytes:
    """Convert input audio (WAV, MP3, M4A, OGG, WEBM, FLAC, etc.) to 16 kHz mono WAV via ffmpeg.

    Uses a temporary file so ffmpeg writes seekable, standard RIFF WAVE chunk headers.
    Enforces a strict duration cap at `max_seconds`.
    """
    if not audio_bytes:
        raise SttError("The recording is empty.", 400)

    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        raise SttError("ffmpeg is not installed or available on PATH.", 500)

    # Determine input extension
    suffix = Path(filename).suffix.lower() if filename else ".wav"
    if not suffix:
        suffix = ".wav"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as in_f:
        in_f.write(audio_bytes)
        in_path = in_f.name

    out_path = in_path + "_converted.wav"

    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", in_path,
        "-ac", str(TARGET_CHANNELS),
        "-ar", str(TARGET_SAMPLE_RATE),
        "-f", "wav",
        out_path,
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            err_msg = proc.stderr.decode("utf-8", errors="replace")
            raise SttError(f"Unsupported or corrupted audio format: {err_msg[:200]}", 415)

        converted_wav = Path(out_path).read_bytes()
    finally:
        if os.path.exists(in_path):
            with contextlib.suppress(OSError):
                os.remove(in_path)
        if os.path.exists(out_path):
            with contextlib.suppress(OSError):
                os.remove(out_path)

    duration = get_audio_duration(converted_wav)
    if duration > max_seconds + 0.1:  # Allow 100ms jitter
        msg = (
            f"Recording is {duration:.1f}s long. "
            f"Please keep questions under {max_seconds:.0f} seconds."
        )
        raise SttError(msg, 400)

    return converted_wav
