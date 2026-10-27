# Gnani Voice Integration & Benchmark Report

**Project:** indic-scheme-rag (Pakkam)  
**Date:** 2026-10-27 22:33:20 IST  
**Git Commit:** `10d74f4d`  
**STT Engine:** Gnani Prisma v2.5 (`POST /stt/v3`)  
**TTS Engine:** Gnani Timbre v3.0 (`Shivani` voice)  
**Credit Guard Status:** 31 calls used in run | 33 / 100 daily calls used  

---

## 1. Executive Summary

This report documents the live integration, smoke testing, and speech-to-text benchmark of Gnani Voice services on Windows workstation for public scheme assistance.

- **Smoke Test:** Passed 100% end-to-end. Generated Tamil TTS audio via Timbre v3.0 in 2.22s and transcribed back via Prisma v2.5 STT in 0.71s with 0% error on the spoken test sentence.
- **Kathbath Tamil Benchmark (n=15):** Achieved **94.8% word accuracy (5.2% Mean WER)** with a **0.95s median latency**.
- **Kathbath Hindi Benchmark (n=15):** Achieved **96.3% word accuracy (3.7% Mean WER)** with a **0.92s median latency**.
- **Credit Guard:** All live calls strictly tracked and verified by `schemebot.voice.budget.CallBudget`.

---

## 2. Speech-to-Text Benchmark Results

Evaluated using `scripts/gnani_stt_eval.py` on real human speech samples from the AI4Bharat Kathbath dataset and synthetic plumbing controls:

| Source Dataset | Data Type | Language | Sample Count (n) | Median Latency | p95 Latency | Mean WER (Word Error Rate) | Accuracy (1 - WER) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Kathbath** | real | TA | 15 | 0.95s | 3.88s | **5.2%** | **94.8%** |
| **Kathbath** | real | HI | 15 | 0.92s | 5.87s | **3.7%** | **96.3%** |
| **Synthetic-Plumbing** | synthetic | TA | 1 | 0.62s | 0.62s | **0.0%** | **100.0%** |

---

## 3. Smoke Test Metrics (Live End-to-End Loop)

| Stage | Operation | Engine / Model | Test Input | Output Status | Latency |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TTS (Speech Out)** | Text-to-Speech | Timbre v3.0 (`Shivani`) | *"வணக்கம், இது ஒரு சோதனை ஒலி."* | 126,764 bytes (24 kHz WAV) | **2.22s** |
| **STT (Speech In)** | Speech-to-Text | Prisma v2.5 (`ta-IN`) | Converted 16 kHz WAV | *"வணக்கம் இது ஒரு சோதனை ஒலி"* | **0.71s** |
| **End-to-End Total** | Audio Roundtrip | Timbre + Prisma | Roundtrip loop | Complete match (0% WER) | **2.93s** |

---

## 4. Audio Pipeline & Safety Constraints

1. **Format Normalization (`schemebot.voice.audio`):**
   - Automatically converts incoming user audio (WAV, MP3, M4A, OGG, WEBM, FLAC) into 16 kHz mono 16-bit PCM WAV via `ffmpeg`.
   - Generates fully compliant, seekable RIFF headers preventing chunk corruption on upstream API gateways.
2. **Duration Cap:**
   - Enforces a hard 30.0-second limit. Clips exceeding 30s raise HTTP 400 with a clear error prompt (*"Please keep questions under 30 seconds"*).
3. **Credit Guard:**
   - Limits total STT + TTS calls to a maximum daily budget (`SCHEMEBOT_GNANI_MAX_CALLS_PER_DAY=100`) via thread-safe atomic lockfile (`logs/gnani-calls.json`).

---

## 5. What is NOT Claimed

1. **Tanglish Speech:** Gnani does not document a native Tanglish (`ta-Latn`) model. Tanglish queries route to `ta-IN`; performance on mixed English-Tamil voice input remains unverified until native speaker recordings are evaluated.
2. **General Speech vs Scheme Terminology:** The AI4Bharat Kathbath dataset consists of read news sentences, not spontaneous citizen queries about government schemes. Real field queries with background noise will exhibit higher error rates.
3. **Synthetic Audio:** Synthetic audio tests verify programmatic API plumbing and audio formatting only; they do not represent real-world acoustic diversity.
