"""Run Chitrapathak-2 OCR on gated pages.

Designed to run either locally (with CUDA GPU) or in Google Colab (free T4 GPU).
Contains NO API keys and NO personal data.
Model revision is pinned for reproducible runs.

Usage:
    python scripts/colab_chitrapathak.py --csv docs/review/ocr_gate_pages.csv --pdf-dir data/raw --out-dir data/processed/chitrapathak_text
"""

import argparse
import csv
from io import BytesIO
from pathlib import Path
import sys

import pymupdf
from PIL import Image
import torch
from transformers import pipeline

MODEL_ID = "krutrim-ai-labs/Chitrapathak-2"
MODEL_REVISION = "e21a8b2983fdf6fbf335c9e5ae6a3e52ba9e5e3b"
DPI = 300


def get_pipeline(device: str = "auto"):
    if device == "auto":
        device_str = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device_str = device

    print(f"Loading {MODEL_ID} (rev {MODEL_REVISION[:7]}) on {device_str}...")
    pipe = pipeline(
        "image-text-to-text",
        model=MODEL_ID,
        revision=MODEL_REVISION,
        device=device_str,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
    )
    return pipe


def render_page_image(pdf_path: Path, page_num_1based: int) -> Image.Image:
    with pymupdf.open(pdf_path) as doc:
        page = doc[page_num_1based - 1]
        pix = page.get_pixmap(dpi=DPI)
        return Image.open(BytesIO(pix.tobytes("png")))


def main():
    parser = argparse.ArgumentParser(description="Run Chitrapathak-2 OCR on specific PDF pages")
    parser.add_argument("--csv", default="docs/review/ocr_gate_pages.csv", help="CSV with document, page columns")
    parser.add_argument("--pdf-dir", default="data/raw", help="Directory containing PDF files")
    parser.add_argument("--out-dir", default="data/processed/chitrapathak_text", help="Directory to save extracted texts")
    parser.add_argument("--device", default="auto", help="'cuda', 'cpu', or 'auto'")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit for test runs")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    pdf_dir = Path(args.pdf_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        print(f"Error: CSV not found at {csv_path}", file=sys.stderr)
        sys.exit(1)

    pipe = get_pipeline(device=args.device)

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if args.limit > 0:
        rows = rows[:args.limit]

    print(f"Processing {len(rows)} pages from {csv_path}...")

    # Cache open PDFs or resolve paths
    pdf_map = {p.stem: p for p in pdf_dir.glob("*.pdf")}

    for idx, row in enumerate(rows, 1):
        doc_id = row["document"].strip()
        page_num = int(row["page"].strip())
        out_file = out_dir / f"{doc_id}_p{page_num}.txt"

        if out_file.exists():
            print(f"[{idx}/{len(rows)}] Skipping {out_file.name} (already exists)")
            continue

        pdf_path = pdf_map.get(doc_id)
        if not pdf_path:
            alt_path = pdf_dir / f"{doc_id}.pdf"
            if alt_path.exists():
                pdf_path = alt_path
            else:
                print(f"[{idx}/{len(rows)}] Warning: PDF not found for {doc_id}", file=sys.stderr)
                continue

        print(f"[{idx}/{len(rows)}] Processing {doc_id} page {page_num}...")
        img = render_page_image(pdf_path, page_num)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": img},
                    {"type": "text", "text": "Extract all the text from this image accurately."},
                ],
            }
        ]

        try:
            output = pipe(text=messages, max_new_tokens=2048)
            extracted_text = ""
            if output and isinstance(output, list):
                first_item = output[0]
                if isinstance(first_item, dict):
                    extracted_text = first_item.get("generated_text", "")
                    # Strip leading message repeat if pipeline echoes prompt
                    if isinstance(extracted_text, list):
                        extracted_text = str(extracted_text)
                else:
                    extracted_text = str(first_item)
            out_file.write_text(extracted_text, encoding="utf-8")
            print(f"    Saved: {out_file.name} ({len(extracted_text)} chars)")
        except Exception as e:
            print(f"    Error processing {doc_id} p{page_num}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
