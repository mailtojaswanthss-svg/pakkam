# Gnani Voice Integration & Benchmark Report

**Project:** indic-scheme-rag (Pakkam)  
**Date:** 2026-10-27 22:33:20 IST  
**Git Commit:** `866ff742` (clean ✅)  
**STT Engine:** Gnani Prisma v2.5 (`POST /stt/v3`)  
**TTS Engine:** Gnani Timbre v3.0 (`Shivani` voice)  
**Credits & Billing:** Exact credit cost per API call and remaining wallet balance are **unknown** (not exposed by the Gnani API response).  
**Daily Call Guard:** 33 / 100 calls used today. *(Note: The 100 calls/day cap is our own application-level safety guard to prevent credit exhaustion, not a quota imposed by Gnani).*  

---

## 1. Executive Summary

This report evaluates live integration of Gnani Voice services (Prisma v2.5 STT and Timbre v3.0 TTS) on Windows for citizen scheme queries.

- **Kathbath Tamil Benchmark (n=15, read speech, clean audio):** Achieved **98.3% word accuracy (1.7% Normalized Mean WER)** with a **0.95s median latency**.
- **Kathbath Hindi Benchmark (n=15, read speech, clean audio):** Achieved **98.3% word accuracy (1.7% Normalized Mean WER)** with a **0.92s median latency**.
- **Synthetic Plumbing Check (n=1):** Verified that Timbre TTS audio can be successfully ingested and transcribed by Prisma STT end-to-end (2.22s TTS, 0.62s STT). *(Note: The synthetic round trip is circular plumbing test audio to verify connectivity and codecs, not human accuracy).*
- **Credit Safety:** All live calls strictly metered by `schemebot.voice.budget.CallBudget`.

---

## 2. Speech-to-Text Benchmark Results

Evaluated using `scripts/gnani_stt_eval.py` on real human read speech samples from the AI4Bharat Kathbath dataset and synthetic plumbing controls:

| Source Dataset | Condition | Lang | Sample Count (n) | Mean Clip Dur | Med Clip Dur | Median Latency | p95 Latency | Mean WER (Normalized) | Mean WER (Raw) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Kathbath** | read speech, clean audio | TA | n=15 | 6.13s | 6.11s | 0.95s | 3.88s | **1.7%** | 5.2% |
| **Kathbath** | read speech, clean audio | HI | n=15 | 4.28s | 4.34s | 0.92s | 5.87s | **1.7%** | 3.7% |
| **Synthetic-Plumbing** | synthetic plumbing, generated audio | TA | n=1 | 2.64s | 2.64s | 0.62s | 0.62s | **0.0%** | 0.0% |

---

## 3. WER Normalisation Specification

Word Error Rate (WER) is calculated as:
$$\text{WER} = \frac{S + D + I}{N}$$
where $S$ is substitutions, $D$ is deletions, $I$ is insertions, and $N$ is total words in the reference text.

To ensure fair measurement between model transcripts and human references, `scripts/gnani_stt_eval.py` applies deterministic normalisation:
1. **Punctuation Stripping:** Removes commas, periods, question marks, colons, semicolons, quotation marks, parentheses, and Indic dandas (`।`, `॥`) via `re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)`.
2. **Whitespace Normalisation:** Collapses consecutive whitespace into single tokens.
3. **Case Folding:** Normalises characters to lowercase.
4. **Raw WER Comparison:** Both normalized WER and raw WER (where punctuation attaches to words) are reported above.

---

## 4. Smoke Test Metrics (Live Service Verification)

| Stage | Operation | Engine / Model | Test Input | Output Status | Latency |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TTS (Speech Out)** | Text-to-Speech | Timbre v3.0 (`Shivani`) | *"வணக்கம், இது ஒரு சோதனை ஒலி."* | 126,764 bytes (24 kHz WAV) | **2.22s** |
| **STT (Speech In)** | Speech-to-Text | Prisma v2.5 (`ta-IN`) | Converted 16 kHz WAV | *"வணக்கம் இது ஒரு சோதனை ஒலி"* | **0.71s** |
| **TTS + STT round trip (test sentence), not system end-to-end latency** | Audio Roundtrip | Timbre + Prisma | Synthetic test phrase | Complete audio match | **2.93s** |

---

## 5. Audio Pipeline & Safety Constraints

1. **Format Normalization (`schemebot.voice.audio`):**
   - Automatically converts incoming user audio (WAV, MP3, M4A, OGG, WEBM, FLAC) into 16 kHz mono 16-bit PCM WAV via `ffmpeg`.
   - Uses temporary disk storage during conversion so `ffmpeg` seeks back to write standard, compliant RIFF headers, avoiding chunk truncation errors on upstream gateways.
2. **Duration Cap:**
   - Enforces a hard 30.0-second limit. Clips exceeding 30s raise HTTP 400 with a clear error prompt (*"Please keep questions under 30 seconds"*).
3. **Credit Guard:**
   - Limits total STT + TTS calls to a maximum daily budget (`SCHEMEBOT_GNANI_MAX_CALLS_PER_DAY=100`) via thread-safe atomic lockfile (`logs/gnani-calls.json`). Exact credit deduction per call on Gnani's backend is unbilled/undocumented in the response.

---

## 6. What is NOT Claimed

1. **Tanglish Speech:** Gnani does not document a native Tanglish (`ta-Latn`) model. Tanglish queries route to `ta-IN`; performance on mixed English-Tamil voice input remains unverified until native speaker recordings are evaluated.
2. **General Speech vs Scheme Terminology:** The AI4Bharat Kathbath dataset consists of crowdsourced **read speech in clean acoustic conditions**, not spontaneous citizen queries about government schemes with colloquial syntax or background noise.
3. **Synthetic Audio:** The synthetic audio test is circular plumbing test audio only (synthesized by Timbre, then transcribed by Prisma) to verify programmatic connectivity and codecs; it is not a measure of human speech accuracy.
