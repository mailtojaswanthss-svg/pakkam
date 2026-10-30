"""Run Chitrapathak-2 OCR on gated pages.

Designed to run either locally (with CUDA GPU) or in Google Colab (free T4 GPU).
Contains NO API keys and NO personal data.
Model revision is pinned for reproducible runs.

Usage:
    python scripts/colab_chitrapathak.py --csv docs/review/ocr_gate_pages.csv --pdf-dir data/raw --out-dir data/processed/chitrapathak_text
"""

import argparse
import csv
import os
import sys
from io import BytesIO
from pathlib import Path

# Default cache dir to F: drive if available to avoid C: drive out-of-space
if Path("F:/").exists():
    os.environ.setdefault("HF_HOME", "F:/hf_cache")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import pymupdf
import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

MODEL_ID = "krutrim-ai-labs/Chitrapathak-2"
MODEL_REVISION = "e21a8b2983fdf6fbf335c9e5ae6a3e52ba9e5e3b"
DPI = 150  # 150 DPI provides crisp text while keeping memory within GPU limits
MAX_PIXELS = 1280 * 28 * 28  # Cap vision tokens to avoid CUDA OOM on 8GB VRAM


def get_model_and_processor(device: str = "auto", cache_dir: str | None = None):
    device_str = ("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device

    effective_cache = cache_dir or os.environ.get("HF_HOME")
    print(
        f"Loading {MODEL_ID} (rev {MODEL_REVISION[:7]}) on {device_str} (cache: {effective_cache})..."
    )

    processor = AutoProcessor.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        cache_dir=effective_cache,
        max_pixels=MAX_PIXELS,
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        cache_dir=effective_cache,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map=device_str if device_str != "cpu" else None,
    )
    if device_str == "cpu":
        model = model.to("cpu")
    return model, processor


def render_page_image(pdf_path: Path, page_num_1based: int) -> Image.Image:
    with pymupdf.open(pdf_path) as doc:
        page = doc[page_num_1based - 1]
        pix = page.get_pixmap(dpi=DPI)
        return Image.open(BytesIO(pix.tobytes("png")))


def main():
    parser = argparse.ArgumentParser(description="Run Chitrapathak-2 OCR on specific PDF pages")
    parser.add_argument(
        "--csv", default="docs/review/ocr_gate_pages.csv", help="CSV with document, page columns"
    )
    parser.add_argument("--pdf-dir", default="data/raw", help="Directory containing PDF files")
    parser.add_argument(
        "--out-dir",
        default="data/processed/chitrapathak_text",
        help="Directory to save extracted texts",
    )
    parser.add_argument("--cache-dir", default=None, help="Custom HuggingFace cache directory")
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

    model, processor = get_model_and_processor(device=args.device, cache_dir=args.cache_dir)

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if args.limit > 0:
        rows = rows[: args.limit]

    print(f"Processing {len(rows)} pages from {csv_path}...")

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
            text_prompt = processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            inputs = processor(
                text=[text_prompt],
                images=[img],
                padding=True,
                return_tensors="pt",
            )
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

            with torch.no_grad():
                generated_ids = model.generate(**inputs, max_new_tokens=2048)
                generated_ids_trimmed = [
                    out_ids[len(in_ids) :]
                    for in_ids, out_ids in zip(inputs["input_ids"], generated_ids, strict=False)
                ]
                extracted_text = processor.batch_decode(
                    generated_ids_trimmed,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=False,
                )[0]

            out_file.write_text(extracted_text, encoding="utf-8")
            print(f"    Saved: {out_file.name} ({len(extracted_text)} chars)")
        except Exception as e:
            print(f"    Error processing {doc_id} p{page_num}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
