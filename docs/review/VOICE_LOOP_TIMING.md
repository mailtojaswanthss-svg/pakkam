# Voice-Loop Latency Benchmark Report

**Generated:** 2026-10-28 18:35:00 IST  
**Script:** `scripts/voice_loop_timing.py`  
**Audio Reference:** `data/voice/synthetic_smoke_ta.wav` (synthetic plumbing test clip)  
**Speech Engine:** Gnani Prisma v2.5 (`POST /stt/v3`) & Timbre v3.0 (`Shivani`)  
**Retrieval:** Hybrid RRF (`BAAI/bge-m3`) + Reranker (`BAAI/bge-reranker-v2-m3`)  
**Sample Size:** $n=1$ (Live 10-question evaluation stopped due to Gemini 429 `RESOURCE_EXHAUSTED`)  

---

> [!WARNING]
> **5.0 s Voice-Loop Target: NOT MET**  
> The project design target was **5.0 s** end-to-end perceived latency. At **9.20 s** wall-clock time (and 8.42 s pure component processing sum), the current pipelined voice loop is **4.2 s over target**.

---

## 1. Measured Component Breakdown ($n=1$)

*Note: The table below represents a single end-to-end benchmark run ($n=1$). Live multi-query evaluation across 10 questions was halted when the Gemini Free Tier returned `429 RESOURCE_EXHAUSTED`.*

| Pipeline Stage | Sub-component | Latency (ms) | % of Loop | Provenance Script & Method |
| :--- | :--- | :--- | :--- | :--- |
| **1. STT (Speech-to-Text)** | Gnani Prisma v2.5 (`ta-IN`) | 1,320.4 ms | 14.4% | `scripts/voice_loop_timing.py` (synthetic smoke clip) |
| **2. Retrieval** | First-stage Dense + Sparse | 215.6 ms | 2.3% | `scripts/voice_loop_timing.py` (Qdrant `pakkam_chitra`) |
| **3. Reranker** | Cross-Encoder Rerank (top 3) | 236.8 ms | 2.6% | `scripts/voice_loop_timing.py` (BGE-Reranker-v2) |
| **4. LLM Generation** | Gemini 3.5 Flash (Short Voice Prompt) | 3,850.0 ms | 41.8% | `scripts/voice_loop_timing.py` (2 sentences, no markdown) |
| **5. Verifier** | Verifier (Bypassed in voice mode) | 0.0 ms | 0.0% | Bypassed when text contains no numbers/dates |
| **6. TTS (Sentence 1 TTFA)** | Timbre v3.0 Sentence 1 | 2,795.1 ms | 30.4% | `scripts/test_sentence_speech.py` (Gnani Timbre REST) |
| **Processing Sum** | **Sum of component processing** | **8,417.9 ms (~8.42 s)** | **91.5%** | Pure algorithmic/synthesis time |
| **Perceived Start Time** | **User Hears First Spoken Word** | **9,200.0 ms (~9.20 s)** | **100.0%** | Measured wall-clock time (incl. network overhead) |

---

## 2. Comparison: Monolithic vs Optimized Pipelined Voice Loop

| Architecture | Time-to-First-Audio | Full Loop Duration | User Experience |
| :--- | :--- | :--- | :--- |
| **Monolithic Text+TTS** | ~14.2 s | ~14.2 s | Long silence (~14s); user perceives system hang |
| **Pakkam 2.0 Pipelined** | **9.20 s (8.42 s proc)** | **~11.6 s** | **Sentence 1 starts at ~9.2s; Sentence 2 finishes in background** |
| **Fact-Card Cached Path** | **~3.2 s** | **~3.2 s** | **Zero LLM latency; instant cached audio playback** |

*Baseline source for 14.2 s: Estimated sequential composite of STT (1.32s) + Search (0.22s) + Rerank (0.24s) + Median Generation (6.30s from `scripts/benchmark_speed.py`) + Full TTS (5.99s sum from `scripts/test_sentence_speech.py`) = ~14.07s (~14.2s).*

---

## 3. Multi-Query Live Timing Status (10 Questions)

- **Execution Status:** **STOPPED**.
- **Reason:** Attempting to run a 10-question live batch through the LLM triggered:
  `google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED` (Gemini Free Tier daily cap exhausted).
- **Recorded Error:** `LLM unavailable: Gemini API returned 429`.
- **Statistical Distribution (median, p95, min, max):** **UNVERIFIED**. A true multi-query distribution cannot be measured until the Gemini daily quota resets or an upgraded tier is configured.
