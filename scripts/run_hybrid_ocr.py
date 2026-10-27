"""Overnight Runner: Step 3 (GPU OCR), Step 4 (Disagreements CSV), Step 5 (Qdrant Index).

Executes Option C:
- Processes the 352 critical scheme pages containing currency amounts in priority order.
- Full resume support: instantly skips already extracted pages.
- VRAM protection: clears CUDA cache between pages and handles OOM gracefully without crashing.
- Compares numbers against Tesseract baseline and outputs docs/review/ocr_disagreements.csv.
- Builds the new Qdrant collection 'pakkam_chitra' leaving 'schemes' untouched.
"""

import argparse
import csv
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pymupdf
import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

from schemebot.config import get_settings
from schemebot.index.embed import BgeM3Encoder, model_source
from schemebot.index.store import build_index, open_client
from schemebot.ingest.chunk import chunk_document
from schemebot.ingest.extract import OCR_DPI, OCR_LANGUAGES, PageText
from schemebot.ingest.models import SourceDoc
from schemebot.ingest.ocr_cache import HASH_PREFIX, file_sha256

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("hybrid_ocr")

MODEL_ID = "krutrim-ai-labs/Chitrapathak-2"
REVISION = "e21a8b2983fdf6fbf335c9e5ae6a3e52ba9e5e3b"
DPI = 150
MAX_PIXELS = 1280 * 28 * 28

NUM_PATTERN = re.compile(r"\b[\d\u0BE6-\u0BEF]+(?:[,\.][\d\u0BE6-\u0BEF]+)*\b")
TAMIL_DIGITS = str.maketrans("௦௧௨௩௪௫௬௭௮௯", "0123456789")

def get_page_priority(doc_id: str, page_num: int) -> int:
    """Demo priority order:
    1. Pudhumai Penn (tn-hedu, tn-swwe)
    2. CMCHIS page 421 and nearby (tn-hfw pages 410-430)
    3. BC/MBC and ADTW hostels (tn-bcmbc, tn-adtw)
    4. National schemes (apy, pmkisan, pmuy)
    5. Tamil G.O.s (kmut, cmbfs)
    6. Other documents
    """
    if doc_id in ("tn-hedu-policy-note-2024-ta", "tn-swwe-policy-note-2024-ta"):
        return 1
    if doc_id == "tn-hfw-policy-note-2024-ta" and 410 <= page_num <= 430:
        return 2
    if doc_id in (
        "tn-bcmbc-policy-note-2024-ta",
        "tn-bcmbc-policy-note-2024-en",
        "tn-adtw-policy-note-2024-ta",
        "tn-adtw-policy-note-2024-en",
    ):
        return 3
    if doc_id in ("apy-brochure-hi", "pmkisan-ekyc-note-2023-hi", "pmuy-sop-2023-en"):
        return 4
    if doc_id in ("kmut-go15-2023-ta", "cmbfs-go43-2022-ta"):
        return 5
    return 6


def normalize_num(token: str) -> str:
    cleaned = token.translate(TAMIL_DIGITS).replace(",", "").strip(".")
    return cleaned


def extract_numbers(text: str) -> set[str]:
    raw = NUM_PATTERN.findall(text)
    return {normalize_num(n) for n in raw if normalize_num(n)}


def load_tesseract_page(cache_root: Path, pdf_path: Path, language: str, page_num: int) -> str:
    lang_code = OCR_LANGUAGES.get(language, "tam+eng")
    key = f"{file_sha256(pdf_path)[:HASH_PREFIX]}-{lang_code}-{OCR_DPI}dpi"
    txt_file = cache_root / key / f"p{page_num}.txt"
    if txt_file.is_file():
        return txt_file.read_text(encoding="utf-8")
    return ""


def main():
    parser = argparse.ArgumentParser(description="Hybrid OCR Runner and Finalizer (Option C)")
    parser.add_argument(
        "--finalize",
        action="store_true",
        help="Build ocr_disagreements.csv and pakkam_chitra index immediately from whatever pages are currently completed, without running further GPU extraction.",
    )
    args = parser.parse_args()

    settings = get_settings()
    manifest_file = settings.data_dir / "sources.json"
    sources_by_id = {s["doc_id"]: s for s in json.loads(manifest_file.read_text(encoding="utf-8"))}

    flagged_csv = Path("docs/review/ocr_flagged_pages.csv")
    if not flagged_csv.exists():
        logger.error("Flagged pages CSV not found at %s", flagged_csv)
        return 1

    with flagged_csv.open("r", encoding="utf-8") as f:
        all_flagged = list(csv.DictReader(f))

    # Filter for Option C: Currency markers across all documents, ordered by demo priority
    target_tasks = []
    for r in all_flagged:
        doc_id = r["document"]
        page_num = int(r["page"])
        if "currency:" in r["reason"]:
            prio = get_page_priority(doc_id, page_num)
            target_tasks.append({
                "document": doc_id,
                "page": page_num,
                "reason": r["reason"],
                "priority": prio,
            })

    target_tasks.sort(key=lambda t: (t["priority"], t["document"], t["page"]))
    logger.info("Found %d target pages for Option C processing", len(target_tasks))

    out_dir = Path("data/processed/chitrapathak_text")
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_root = settings.processed_dir / "ocr_cache"

    # Completed tasks vs pending tasks
    completed_tasks = [
        t for t in target_tasks
        if (out_dir / f"{t['document']}_p{t['page']}.txt").is_file()
        and (out_dir / f"{t['document']}_p{t['page']}.txt").stat().st_size >= 20
    ]
    pending_tasks = [
        t for t in target_tasks
        if not (out_dir / f"{t['document']}_p{t['page']}.txt").is_file()
        or (out_dir / f"{t['document']}_p{t['page']}.txt").stat().st_size < 20
    ]

    # Load recorded page timings
    timing_file = out_dir / "page_timings.json"
    timings: dict[str, float] = {}
    if timing_file.is_file():
        try:
            timings = json.loads(timing_file.read_text(encoding="utf-8"))
        except Exception:
            timings = {}

    avg_s = sum(timings.values()) / len(timings) if timings else 78.8
    done_count = len(completed_tasks)
    left_count = len(pending_tasks)
    est_sec_left = left_count * avg_s
    est_hours_left = est_sec_left / 3600

    print("\n" + "=" * 78)
    print(" OPTION C HYBRID OCR: PROGRESS SUMMARY")
    print("=" * 78)
    pct = (done_count / len(target_tasks) * 100) if target_tasks else 0.0
    print(f" Target Pages (Flagged with Currency): {len(target_tasks)}")
    print(f" Pages Completed (Chitrapathak):      {done_count} ({pct:.1f}%)")
    print(f" Pages Remaining:                     {left_count}")
    print(f" Average Time per Page:               {avg_s:.1f}s")
    print(f" Estimated Time Remaining:            {est_hours_left:.2f} hours ({int(est_sec_left)}s)")
    print("=" * 78 + "\n")

    if args.finalize:
        logger.info("--finalize flag passed: Skipping GPU extraction and building outputs directly from %d completed pages.", done_count)

    # Initialize model if tasks pending and not finalizing
    if not args.finalize and pending_tasks:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        logger.info("Loading Chitrapathak-2 on %s (%s)...", device, dtype)

        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            MODEL_ID,
            revision=REVISION,
            torch_dtype=dtype,
            device_map="auto" if device == "cuda" else None,
        )
        if device != "cuda":
            model = model.to("cpu")

        processor = AutoProcessor.from_pretrained(
            MODEL_ID,
            revision=REVISION,
            max_pixels=MAX_PIXELS,
        )

        for idx, task in enumerate(pending_tasks, 1):
            doc_id = task["document"]
            page_num = task["page"]
            target_txt = out_dir / f"{doc_id}_p{page_num}.txt"
            source = sources_by_id[doc_id]
            pdf_path = settings.raw_dir / source["file"]

            t0 = time.perf_counter()
            logger.info("[%d/%d] Extracting %s (Page %d)...", idx, len(pending_tasks), doc_id, page_num)

            try:
                with pymupdf.open(pdf_path) as doc:
                    page = doc[page_num - 1]
                    pixmap = page.get_pixmap(dpi=DPI)
                    image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": image},
                            {"type": "text", "text": "Extract all text from this image exactly as written. Output only the extracted text."},
                        ],
                    }
                ]
                text_prompt = processor.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                inputs = processor(
                    text=[text_prompt],
                    images=[image],
                    padding=True,
                    return_tensors="pt",
                ).to(model.device)

                generated_ids = model.generate(**inputs, max_new_tokens=2048)
                generated_ids_trimmed = [
                    out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                ]
                output_text = processor.batch_decode(
                    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                )[0].strip()

                target_txt.write_text(output_text, encoding="utf-8")
                elapsed = time.perf_counter() - t0
                timings[f"{doc_id}_p{page_num}"] = round(elapsed, 1)
                try:
                    timing_file.write_text(json.dumps(timings, indent=2), encoding="utf-8")
                except Exception:
                    pass
                logger.info("  -> Saved %s (%d chars) in %.1fs", target_txt.name, len(output_text), elapsed)

            except torch.cuda.OutOfMemoryError:
                logger.error("CUDA OOM on %s page %d! Clearing cache and pausing 5s...", doc_id, page_num)
                torch.cuda.empty_cache()
                time.sleep(5)
                continue
            except Exception as e:
                logger.error("Error on %s page %d: %s", doc_id, page_num, e)
                continue
            finally:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

    # Step 4: Disagreements comparison
    logger.info("Generating Step 4: docs/review/ocr_disagreements.csv...")
    disagreements = []

    for task in target_tasks:
        doc_id = task["document"]
        page_num = task["page"]
        chitra_txt_path = out_dir / f"{doc_id}_p{page_num}.txt"
        if not chitra_txt_path.is_file():
            continue

        chitra_text = chitra_txt_path.read_text(encoding="utf-8")
        source = sources_by_id[doc_id]
        pdf_path = settings.raw_dir / source["file"]
        tess_text = load_tesseract_page(cache_root, pdf_path, source["language"], page_num)

        tess_nums = extract_numbers(tess_text)
        chitra_nums = extract_numbers(chitra_text)

        tess_only = sorted(tess_nums - chitra_nums)
        chitra_only = sorted(chitra_nums - tess_nums)

        if tess_only or chitra_only:
            disagreements.append({
                "document": doc_id,
                "page": page_num,
                "tesseract_only_numbers": "; ".join(tess_only[:8]),
                "chitrapathak_only_numbers": "; ".join(chitra_only[:8]),
                "notes": task["reason"],
            })

    disagree_csv = Path("docs/review/ocr_disagreements.csv")
    with disagree_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["document", "page", "tesseract_only_numbers", "chitrapathak_only_numbers", "notes"])
        writer.writeheader()
        writer.writerows(disagreements)
    logger.info("Wrote %d number disagreements to %s", len(disagreements), disagree_csv.as_posix())

    # Step 5: Build 'pakkam_chitra' collection
    logger.info("Step 5: Building Qdrant collection 'pakkam_chitra'...")
    all_chunks = []

    for s in json.loads(manifest_file.read_text(encoding="utf-8")):
        doc_id = s["doc_id"]
        pdf_path = settings.raw_dir / s["file"]
        if not pdf_path.is_file():
            continue

        doc_pages = []
        with pymupdf.open(pdf_path) as pdf:
            for i, p in enumerate(pdf, start=1):
                chitra_p = out_dir / f"{doc_id}_p{i}.txt"
                if chitra_p.is_file() and chitra_p.stat().st_size >= 20:
                    text = chitra_p.read_text(encoding="utf-8")
                    method = "ocr-chitrapathak"
                else:
                    text = load_tesseract_page(cache_root, pdf_path, s["language"], i)
                    if text:
                        method = "ocr-tesseract"
                    else:
                        text = p.get_text("text").strip()
                        method = "text"
                doc_pages.append(PageText(page=i, text=text, method=method))

        source_doc = SourceDoc.model_validate(s)
        chunks = chunk_document(source_doc, doc_pages)
        all_chunks.extend(chunks)

    logger.info("Total hybrid chunks generated: %d. Indexing into 'pakkam_chitra'...", len(all_chunks))
    encoder = BgeM3Encoder(
        model_source(settings.embedding_model, settings.embedding_revision),
        settings.embed_batch_size,
    )
    client = open_client(settings.index_dir)
    indexed_count = build_index(client, "pakkam_chitra", all_chunks, encoder)
    logger.info("SUCCESS: Indexed %d chunks into Qdrant collection 'pakkam_chitra'!", indexed_count)
    print("\nOVERNIGHT RUN COMPLETED SUCCESSFULLY! ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
