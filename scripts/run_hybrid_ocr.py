"""Overnight Runner: Step 3 (GPU OCR), Step 4 (Disagreements CSV), Step 5 (Qdrant Index).

Executes Option C:
- Processes the 352 critical scheme pages containing currency amounts in priority order.
- Full resume support: instantly skips already extracted pages.
- VRAM protection: clears CUDA cache between pages and handles OOM gracefully without crashing.
- Compares numbers against Tesseract baseline and outputs docs/review/ocr_disagreements.csv.
- Builds the new Qdrant collection 'pakkam_chitra' leaving 'schemes' untouched.
"""

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

# Priority order for Option C
DOC_PRIORITY = {
    # Demo priority 1: Short national & pension schemes
    "apy-brochure-hi": 1,
    "pmkisan-ekyc-note-2023-hi": 2,
    "pmuy-sop-2023-en": 3,
    # Demo priority 2: Tamil G.O.s
    "kmut-go15-2023-ta": 4,
    "cmbfs-go43-2022-ta": 5,
    # Demo priority 3: Pudhumai Penn / Higher Ed / Women Welfare
    "tn-hedu-policy-note-2024-ta": 6,
    "tn-swwe-policy-note-2024-ta": 7,
    # Demo priority 4: Hostels (BC/MBC & ADTW)
    "tn-bcmbc-policy-note-2024-ta": 8,
    "tn-bcmbc-policy-note-2024-en": 9,
    "tn-adtw-policy-note-2024-ta": 10,
    "tn-adtw-policy-note-2024-en": 11,
}


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
    settings = get_settings()
    manifest_file = settings.data_dir / "sources.json"
    sources_by_id = {s["doc_id"]: s for s in json.loads(manifest_file.read_text(encoding="utf-8"))}

    flagged_csv = Path("docs/review/ocr_flagged_pages.csv")
    if not flagged_csv.exists():
        logger.error("Flagged pages CSV not found at %s", flagged_csv)
        return 1

    with flagged_csv.open("r", encoding="utf-8") as f:
        all_flagged = list(csv.DictReader(f))

    # Filter for Option C: Target docs and currency markers only
    target_tasks = []
    for r in all_flagged:
        doc_id = r["document"]
        if doc_id in DOC_PRIORITY and "currency:" in r["reason"]:
            target_tasks.append({
                "document": doc_id,
                "page": int(r["page"]),
                "reason": r["reason"],
                "priority": DOC_PRIORITY[doc_id],
            })

    target_tasks.sort(key=lambda t: (t["priority"], t["page"]))
    logger.info("Found %d target pages for Option C overnight processing", len(target_tasks))

    out_dir = Path("data/processed/chitrapathak_text")
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_root = settings.processed_dir / "ocr_cache"

    # Check already completed pages
    pending_tasks = [
        t for t in target_tasks
        if not (out_dir / f"{t['document']}_p{t['page']}.txt").is_file()
        or (out_dir / f"{t['document']}_p{t['page']}.txt").stat().st_size < 20
    ]
    logger.info("%d pages already completed; %d pages pending to extract", len(target_tasks) - len(pending_tasks), len(pending_tasks))

    # Initialize model if tasks pending
    if pending_tasks:
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
                if chitra_p.is_file():
                    text = chitra_p.read_text(encoding="utf-8")
                    method = "ocr-chitrapathak"
                else:
                    text = load_tesseract_page(cache_root, pdf_path, s["language"], i)
                    method = "ocr-tesseract" if text else "text"
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
