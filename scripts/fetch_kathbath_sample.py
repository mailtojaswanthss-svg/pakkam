"""Step 4: Fetch a small, targeted sample of Tamil and Hindi clips from AI4Bharat Kathbath.

Streams directly from remote Parquet files on Hugging Face using range requests (fsspec + pyarrow)
to download only the requested clips (~10-15 MB total) rather than the 174 GB full dataset.
Checks disk space (must be >= 5 GB free) and converts audio to standard 16 kHz mono WAV via ffmpeg.
Outputs:
- data/voice/kathbath/<lang>_<index>.wav
- data/voice/kathbath_clips.csv
"""

import csv
import io
import os
import shutil
import sys
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from schemebot.config import get_settings
from schemebot.voice.audio import convert_to_wav16k

TARGET_CLIPS_PER_LANG = 15
MAX_DURATION = 30.0

LANG_CONFIGS = [
    {
        "lang": "ta",
        "name": "tamil",
        "parquet_path": "tamil/valid-00000-of-00002.parquet",
    },
    {
        "lang": "hi",
        "name": "hindi",
        "parquet_path": "hindi/valid-00000-of-00002.parquet",
    },
]


def check_disk_space(target_path: Path, min_gb: float = 5.0) -> None:
    anchor = target_path.resolve().anchor
    usage = shutil.disk_usage(anchor)
    free_gb = usage.free / (1024 ** 3)
    if free_gb < min_gb:
        raise RuntimeError(
            f"Insufficient disk space on {anchor}: {free_gb:.1f} GB free, required >= {min_gb} GB"
        )
    print(f"[Disk Check] {anchor} has {free_gb:.1f} GB free (requirement: >= {min_gb} GB) - OK")


def get_hf_token() -> str:
    settings = get_settings()
    token = os.environ.get("HF_TOKEN")
    if not token and settings.model_config.get("env_file"):
        with open(settings.model_config["env_file"], "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("HF_TOKEN="):
                    token = line.strip().split("=", 1)[1]
                    break
    if not token:
        raise ValueError("HF_TOKEN not found in environment or .env file.")
    return token


def main():
    import fsspec
    import pyarrow.parquet as pq

    print("=" * 70)
    print(" KATHBATH SAMPLE FETCHER (Tamil & Hindi Only, Max 15 clips each)")
    print(" Gated Dataset: ai4bharat/Kathbath (Splits used: valid)")
    print("=" * 70)

    hf_token = get_hf_token()
    out_dir = Path("data/voice/kathbath")
    out_dir.mkdir(parents=True, exist_ok=True)
    check_disk_space(out_dir, min_gb=5.0)

    csv_path = Path("data/voice/kathbath_clips.csv")
    csv_rows = []

    headers = {"Authorization": f"Bearer {hf_token}"}
    fs = fsspec.filesystem("https", headers=headers)

    for cfg in LANG_CONFIGS:
        lang = cfg["lang"]
        name = cfg["name"]
        parquet_rel = cfg["parquet_path"]
        url = f"https://huggingface.co/datasets/ai4bharat/Kathbath/resolve/main/{parquet_rel}"

        print(f"\nStreaming remote Parquet for {name.capitalize()} ({parquet_rel})...")
        saved_count = 0

        with fs.open(url, "rb") as remote_file:
            pf = pq.ParquetFile(remote_file)
            for rg_idx in range(pf.num_row_groups):
                if saved_count >= TARGET_CLIPS_PER_LANG:
                    break
                table = pf.read_row_group(rg_idx)
                col_names = table.column_names

                # Find relevant columns
                text_col = "text" if "text" in col_names else "transcription"
                dur_col = "duration" if "duration" in col_names else None
                bytes_col = "audio_filepath" if "audio_filepath" in col_names else ("bytes" if "bytes" in col_names else "audio")

                for row_idx in range(table.num_rows):
                    if saved_count >= TARGET_CLIPS_PER_LANG:
                        break

                    ref_text = str(table[text_col][row_idx].as_py()).strip()
                    duration = float(table[dur_col][row_idx].as_py()) if dur_col else 0.0

                    if duration > MAX_DURATION:
                        continue

                    # Extract raw audio bytes
                    raw_val = table[bytes_col][row_idx].as_py()
                    if isinstance(raw_val, dict):
                        raw_bytes = raw_val.get("bytes")
                    else:
                        raw_bytes = raw_val

                    if not raw_bytes:
                        continue

                    # Convert to standard 16 kHz mono WAV via ffmpeg
                    try:
                        wav_16k = convert_to_wav16k(raw_bytes, f"raw_{name}.wav", max_seconds=MAX_DURATION)
                    except Exception as e:
                        continue

                    saved_count += 1
                    clip_filename = f"kathbath_{lang}_{saved_count:02d}.wav"
                    clip_path = out_dir / clip_filename
                    clip_path.write_bytes(wav_16k)

                    csv_rows.append({
                        "filename": clip_filename,
                        "language": lang,
                        "reference_text": ref_text,
                        "source": "Kathbath",
                        "synthetic_or_real": "real",
                    })
                    print(f"  [{name.upper()} {saved_count:02d}/{TARGET_CLIPS_PER_LANG}] Saved {clip_filename} ({len(wav_16k)} bytes, {duration:.1f}s)")

    # Write catalog CSV
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "language", "reference_text", "source", "synthetic_or_real"])
        writer.writeheader()
        writer.writerows(csv_rows)

    print("\n" + "=" * 70)
    print(f"SUCCESS: Fetched {len(csv_rows)} clips total to {out_dir.as_posix()}")
    print(f"Wrote metadata to {csv_path.as_posix()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
