# Pakkam 2.0 - Technical Project Specification & Empirical Audit

## 1. Abstract

Public welfare schemes in India distribute billions of rupees in critical financial aid, educational stipends, and pensions. However, citizen access is severely hindered by complex bureaucratic documentation, scanned legacy PDF policy notes containing Tamil font encodings, and linguistic barriers across regional dialects and Romanized code-mixing (Tanglish). **Pakkam 2.0** is an independent student research prototype providing an auditable, multilingual, citation-grounded Retrieval-Augmented Generation (RAG) assistant for Tamil Nadu and Central Government welfare schemes in **Tamil, Hindi, English, and Tanglish**.

Pakkam 2.0 implements a hybrid crop OCR pipeline coupling Tesseract bounding-box detection with `krutrim-ai-labs/Chitrapathak-2` to eliminate Indic numeral transcription errors, a two-stage hybrid retrieval architecture with Reciprocal Rank Fusion and cross-encoder reranking, a sentence-level pipelined voice loop utilizing Gnani Prisma v2.5 STT and Timbre v3.0 TTS, and code-enforced daily LLM budget guards with strict refusal safety thresholds.

---

## 2. Core Contributions

1. **Hybrid Crop OCR Architecture**: Localized currency box detection via Tesseract coupled with targeted Chitrapathak-2 OCR inference, reducing per-page latency from ~95 s to ~12 s (~8× speedup) while resolving 100% of examined Indic numeral misreadings.
2. **Citation-Grounded Multilingual Retrieval**: Two-stage retrieval pairing dense and sparse representations (`BAAI/bge-m3`) with cross-encoder reranking (`BAAI/bge-reranker-v2-m3`), reaching 98.7% Recall@5 across 194 evaluation queries.
3. **Pipelined Voice Loop with Sentence Streaming**: Decoupled sentence-by-sentence text-to-speech synthesis achieving a perceived Time-to-First-Audio (TTFA) of ~2.8 s and perceived interactive start of ~8.4 s, compared to monolithic ~14.2 s loops.
4. **Resilient "Never Fail Visibly" Fallback**: Deterministic graceful degradation ensuring that even under LLM rate limits (HTTP 429) or network timeouts, citizens receive official document passages and verified helplines.
5. **Code-Enforced Budget Guarding & Reproducibility**: Architectural fail-closed LLM budget enforcement with IST midnight rollover and zero key exposure, backed by a 521-test automated test suite.

---

## 3. Measured vs. Unmeasured Metrics Table

To ensure scientific honesty and prevent ungrounded claims, all project figures are categorized below:

| Metric / Component | Status | Measured Value | Provenance / Evidence Script | Notes / Human Dependency |
|---|---|---|---|---|
| **Hybrid OCR Problem Pages** | **MEASURED** | **7 / 7 (100.0%)** | `scripts/ocr_compare.py` | Known scanned numeral test cases |
| **OCR Inference Speedup** | **MEASURED** | **~8× (95s -> 12s)** | `scripts/run_crop_ocr.py` | Crop mode vs full page inference |
| **OCR Amount Disagreements** | **MEASURED** | **263 pages flagged** | `docs/review/ocr_disagreements.csv` | 68 scanned pages unreviewed (`BLK-06`) |
| **Retrieval Recall@5 (Hybrid+Rerank)**| **MEASURED** | **98.7%** | `scripts/ablate_retrieval.py` | 194 draft queries, `pakkam_chitra` collection |
| **Keyword-Only Recall@5** | **MEASURED** | **67.5%** | `scripts/ablate_retrieval.py` | Baseline BM25 sparse search |
| **Refusal Curve Routing Accuracy** | **MEASURED** | **87.1%** | `scripts/evaluate_refusal_curve.py` | Threshold 0.35, 92.5% ungrounded refused |
| **Fast Sources Latency (`/ask/sources`)** | **MEASURED** | **421.8 ms mean** | `scripts/benchmark_instant_sources.py`| $n=10$, median: 352.9 ms, 0 LLM calls |
| **Voice Loop Perceived Start** | **MEASURED** | **8,417.9 ms** | `scripts/voice_loop_timing.py` | STT (1320ms) + Ret (452ms) + LLM (3850ms) + TTFA (2795ms) |
| **TTS Sentence 1 TTFA** | **MEASURED** | **2,795.1 ms** | `scripts/test_sentence_speech.py` | Timbre v3.0 `Shivani` |
| **Prisma v2.5 Raw JSON Payload** | **MEASURED** | **Confidence absent** | `scripts/capture_prisma_raw.py` | Live request captured in `prisma_raw_sample.json` |
| **Daily LLM Budget Execution** | **MEASURED** | **3 calls used / 17 spare**| `scripts/run_daily.py` | Tested on pinned `gemini-3.8-flash` |
| **Automated Test Suite** | **MEASURED** | **521 passed / 10 deselected**| `pytest -q` | Zero secrets found in history |
| **Teammate 50 Verified Questions** | *UNMEASURED* | **TODO (`BLK-02`)** | `data/eval/teammate_50_verified.jsonl`| Pending ingestion from teammate |
| **Held-Out Question Evaluation** | *UNMEASURED* | **TODO (`BLK-01`)** | Scheduled Mon 2 Nov | Gated strictly on `.freeze` marker |
| **Field Audio Real-World WER** | *UNMEASURED* | **TODO (`BLK-03`)** | `docs/voice/CLIP_PLAN.md` | Pending 30 physical recordings |
| **Official Helpline Phone Audit** | *UNMEASURED* | **TODO (`BLK-04`)** | `docs/review/helpline_check.csv` | Requires human telephone calls |
| **Full Answer Blind Hand-Grading** | *UNMEASURED* | **TODO (`BLK-05`)** | `docs/review/grading_sheet.csv` | 194 answers pending human hand-grading |
| **Telephony / SIP Trunk Latency** | *UNMEASURED* | **TODO (`BLK-08`)** | Live telecom line test | Deferred post-submission |

---

## 4. System Architecture & Model Card Provenance

### Models Deployed
1. **BAAI/bge-m3**: Multilingual Dense and Sparse Embedding (1024-dim dense, lexical weights, ColBERT vectors). License: `MIT`.
2. **BAAI/bge-reranker-v2-m3**: Cross-Encoder Relevance Reranker. License: `Apache-2.0`.
3. **krutrim-ai-labs/Chitrapathak-2**: Indic Vision-Language OCR Model. License: `Krutrim Community License` (Research Use Only). Visible attribution acknowledged in documentation and code headers.
4. **Google Gemini 3.8 Flash (`gemini-3.8-flash`)**: Pinned generative answer synthesis and verifier model.
5. **Gnani Prisma v2.5 & Timbre v3.0**: Speech-to-Text and Indic Text-to-Speech engines (`ta-IN`, `hi-IN`, `en-IN`).

---

## 5. Limitations & Future Work

1. **Physical Telephone Dialing**: Pakkam 2.0 operates as a web-based voice and text application. Real PSTN/telephony integration (via SIP trunks or Twilio/Exotel) is deferred post-submission.
2. **68 Unreviewed OCR Disagreements**: Scanned legacy PDF pages with differing numerical interpretations between Tesseract and Chitrapathak-2 require authoritative human verification.
3. **Local GPU Footprint**: Real-time local execution of BGE-M3 and Chitrapathak-2 requires $\ge 8$ GB VRAM; lower-spec client deployments rely on server-side pre-rendering and caching.
