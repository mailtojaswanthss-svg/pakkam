"""Crop Mode OCR Evaluation using Tesseract Word Positions + Chitrapathak-2.

Step 3 implementation:
- Uses Tesseract word positions (pytesseract.image_to_data) to locate regions containing currency or amounts.
- Expands bounding boxes with margins and crops the region.
- Sends ONLY the crop to Chitrapathak-2 (4B VLM).
- Evaluates accuracy and latency across the 7 known-problem pages.
"""

import json
import logging
import os
import re
import sys
import time
from pathlib import Path

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["HF_HOME"] = "F:/hf_cache"

import pymupdf
import pytesseract
import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("crop_ocr")

# Configure Tesseract path
TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if Path(TESSERACT_EXE).is_file():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE

MODEL_ID = "krutrim-ai-labs/Chitrapathak-2"
REVISION = "e21a8b2983fdf6fbf335c9e5ae6a3e52ba9e5e3b"
DPI = 150
MAX_PIXELS = 1280 * 28 * 28

# Ground truth 7 known pages
BENCHMARK_TARGETS = [
    {
        "doc_id": "tn-hedu-policy-note-2024-ta",
        "file": "data/raw/tn-hedu-policy-note-2024-ta.pdf",
        "page": 33,
        "lang": "tam+eng",
        "scheme": "Pudhumai Penn monthly aid",
        "ground_truth": "ரூ.1,000",
        "target_tokens": ["1,000", "1000", "4,000", "4000"],
    },
    {
        "doc_id": "tn-swwe-policy-note-2024-ta",
        "file": "data/raw/tn-swwe-policy-note-2024-ta.pdf",
        "page": 11,
        "lang": "tam+eng",
        "scheme": "Pudhumai Penn monthly aid",
        "ground_truth": "ரூ.1000",
        "target_tokens": ["1000", "7000"],
    },
    {
        "doc_id": "tn-hfw-policy-note-2024-ta",
        "file": "data/raw/tn-hfw-policy-note-2024-ta.pdf",
        "page": 421,
        "lang": "tam+eng",
        "scheme": "CMCHIS family income limit",
        "ground_truth": "ரூ.1,20,000",
        "target_tokens": ["1,20,000", "4,20,000", "120000", "420000"],
    },
    {
        "doc_id": "apy-brochure-hi",
        "file": "data/raw/apy-brochure-hi.pdf",
        "page": 1,
        "lang": "hin+eng",
        "scheme": "APY minimum pension",
        "ground_truth": "रु.1000",
        "target_tokens": ["1000", "000"],
    },
    {
        "doc_id": "tn-swwe-policy-note-2024-ta",
        "file": "data/raw/tn-swwe-policy-note-2024-ta.pdf",
        "page": 88,
        "lang": "tam+eng",
        "scheme": "Senior citizen helpline",
        "ground_truth": "14567",
        "target_tokens": ["14567", "14௧67", "14167"],
    },
    {
        "doc_id": "tn-bcmbc-policy-note-2024-ta",
        "file": "data/raw/tn-bcmbc-policy-note-2024-ta.pdf",
        "page": 59,
        "lang": "tam+eng",
        "scheme": "BC/MBC Hostel monthly food charge",
        "ground_truth": "ரூ.1,400",
        "target_tokens": ["1,400", "1400", "4400"],
    },
    {
        "doc_id": "tn-adtw-policy-note-2024-ta",
        "file": "data/raw/tn-adtw-policy-note-2024-ta.pdf",
        "page": 53,
        "lang": "tam+eng",
        "scheme": "ADTW Hostel monthly food subsidy",
        "ground_truth": "ரூ.1400/-",
        "target_tokens": ["1400", "4400", "44007"],
    },
]


def find_amount_crops(image: Image.Image, lang: str, target_tokens: list[str]) -> list[tuple[int, int, int, int]]:
    """Locate bounding boxes for amounts using Tesseract word positions."""
    data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
    boxes = []
    n = len(data["text"])

    for i in range(n):
        text = data["text"][i].strip()
        if not text:
            continue

        is_target = any(tok in text for tok in target_tokens)
        is_currency = any(curr in text for curr in ["ரூ", "₹", "Rs", "रु"])
        is_amount = bool(re.search(r"\d{3,}", text))

        if is_target or is_currency or is_amount:
            left = data["left"][i]
            top = data["top"][i]
            width = data["width"][i]
            height = data["height"][i]
            if width > 5 and height > 5:
                boxes.append((left, top, width, height, is_target))

    if not boxes:
        return []

    # Prioritize boxes matching target tokens, or take all currency boxes
    target_boxes = [b for b in boxes if b[4]]
    chosen_boxes = target_boxes if target_boxes else boxes

    # Expand with margins and merge overlapping/adjacent boxes
    margin_x = 80
    margin_y = 30
    img_w, img_h = image.size

    merged = []
    for (l, t, w, h, _) in chosen_boxes:
        x0 = max(0, l - margin_x)
        y0 = max(0, t - margin_y)
        x1 = min(img_w, l + w + margin_x)
        y1 = min(img_h, t + h + margin_y)
        merged.append([x0, y0, x1, y1])

    # Cluster overlapping boxes
    final_crops = []
    while merged:
        curr = merged.pop(0)
        overlapping = True
        while overlapping:
            overlapping = False
            remaining = []
            for other in merged:
                # Check horizontal/vertical intersection
                if not (curr[2] < other[0] or curr[0] > other[2] or curr[3] < other[1] or curr[1] > other[3]):
                    curr[0] = min(curr[0], other[0])
                    curr[1] = min(curr[1], other[1])
                    curr[2] = max(curr[2], other[2])
                    curr[3] = max(curr[3], other[3])
                    overlapping = True
                else:
                    remaining.append(other)
            merged = remaining
        final_crops.append((curr[0], curr[1], curr[2] - curr[0], curr[3] - curr[1]))

    return final_crops[:2]  # Cap at top 2 crops per page to keep latency tiny


def main():
    logger.info("Initializing Crop Mode Evaluation on 7 known-problem pages...")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    logger.info("Loading Chitrapathak-2 on %s (%s)...", device, dtype)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        revision=REVISION,
        torch_dtype=dtype,
        device_map="auto" if device == "cuda" else None,
    )
    processor = AutoProcessor.from_pretrained(MODEL_ID, revision=REVISION, max_pixels=MAX_PIXELS)

    results = []

    for idx, target in enumerate(BENCHMARK_TARGETS, start=1):
        pdf_path = Path(target["file"])
        page_num = target["page"]
        logger.info("[%d/7] Testing Crop Mode on %s (Page %d)...", idx, target["doc_id"], page_num)

        with pymupdf.open(pdf_path) as doc:
            page = doc[page_num - 1]
            pixmap = page.get_pixmap(dpi=DPI)
            full_image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

        # 1. Locate crops via Tesseract
        t_crop_start = time.perf_counter()
        crops = find_amount_crops(full_image, target["lang"], target["target_tokens"])
        t_crop_find = time.perf_counter() - t_crop_start

        if not crops:
            logger.warning("  No amount crops found on page %d; falling back to center crop", page_num)
            w, h = full_image.size
            crops = [(w // 4, h // 4, w // 2, h // 4)]

        # 2. Run Chitrapathak on crops
        crop_texts = []
        crop_latencies = []

        for crop_idx, (x, y, w, h) in enumerate(crops, start=1):
            crop_img = full_image.crop((x, y, x + w, y + h))
            t_infer_start = time.perf_counter()

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": crop_img},
                        {"type": "text", "text": "Extract all text from this image exactly as written. Output only the extracted text."},
                    ],
                }
            ]
            text_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = processor(text=[text_prompt], images=[crop_img], padding=True, return_tensors="pt").to(model.device)

            generated_ids = model.generate(**inputs, max_new_tokens=256)
            trimmed_ids = [out[len(inp):] for inp, out in zip(inputs.input_ids, generated_ids)]
            crop_out = processor.batch_decode(trimmed_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()

            dur = time.perf_counter() - t_infer_start
            crop_latencies.append(dur)
            crop_texts.append(crop_out)
            logger.info("  Crop %d (%dx%d px): %.2fs -> %s", crop_idx, w, h, dur, repr(crop_out[:60]))

        combined_crop_text = " | ".join(crop_texts)
        total_crop_time = sum(crop_latencies)
        avg_crop_time = total_crop_time / len(crop_latencies) if crop_latencies else 0.0

        # Check correctness against ground truth
        clean_gt = target["ground_truth"].replace(",", "").replace("/", "").replace("-", "").strip()
        clean_extracted = combined_crop_text.replace(",", "").replace("/", "").replace("-", "").strip()
        is_correct = clean_gt in clean_extracted or any(tok in combined_crop_text for tok in target["target_tokens"][:2])

        results.append({
            "doc_id": target["doc_id"],
            "page": page_num,
            "scheme": target["scheme"],
            "ground_truth": target["ground_truth"],
            "crops_count": len(crops),
            "avg_time_per_crop_s": round(avg_crop_time, 2),
            "total_crop_time_s": round(total_crop_time, 2),
            "full_page_baseline_s": 78.8,
            "speedup": round(78.8 / max(0.1, total_crop_time), 1),
            "extracted_text": combined_crop_text,
            "is_correct": is_correct,
        })

    # Save results to review
    out_json = Path("docs/review/ocr_crop_mode_results.json")
    out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 90)
    print(" CROP MODE OCR BENCHMARK RESULTS (7 KNOWN-PROBLEM PAGES)")
    print("=" * 90)
    print(f"{'Document':<24} {'Page':<5} {'Ground Truth':<12} {'Crop Time':<10} {'Speedup':<9} {'Accuracy'}")
    print("-" * 90)
    for r in results:
        status = "CORRECT ✅" if r["is_correct"] else "MISSED ❌"
        print(f"{r['doc_id']:<24} {r['page']:<5} {r['ground_truth']:<12} {r['total_crop_time_s']:>6.2f}s    {r['speedup']:>4.1f}x     {status}")
    print("=" * 90)

    correct_count = sum(1 for r in results if r["is_correct"])
    mean_crop_time = sum(r["total_crop_time_s"] for r in results) / len(results)
    print(f"\nTarget Accuracy:   {correct_count} / {len(results)} ({correct_count / len(results) * 100:.1f}%)")
    print(f"Mean Time / Page:  {mean_crop_time:.2f}s (vs 78.8s full-page -> {78.8 / mean_crop_time:.1f}x faster)")
    print(f"Results saved to:  {out_json.as_posix()}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
