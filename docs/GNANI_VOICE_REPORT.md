# Pakkam 2.0 Comprehensive Voice & Audio Evidence Report

> **Generated at:** 29 Oct 2026  
> **Repository:** `mailtojaswanthss-svg/pakkam` (Branch: `feat/prompt-pack-execution`)  
> **Status:** Working Prototype (Local Backup Only)  
> **Timelines:** Code Freeze: Mon 2 Nov 2026 | Demonstration Video Delivery: Tue 3 Nov 2026 | Own Target: Fri 6 Nov 2026 | Submission: 10 Nov 2026  

---

## 1. Speech-to-Text Performance (Gnani Prisma v2.5 STT)

Evaluated against public AI4Bharat Kathbath read-speech dataset and synthetic validation audio:

| Language | Clips ($n$) | Mean Normalized WER | Mean Raw WER | Median STT Latency | Empirical Finding |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **HINDI** | 15 | **2.6%** | 3.7% | 3,114.6 ms | High phoneme fidelity on clean read speech |
| **TAMIL** | 16 | **4.1%** | 5.2% | 3,098.2 ms | Clean read speech; field acoustics untested |

---

## 2. Gate 1.4: Tanglish Text Retrieval Check (Synthetic, n=10, Written by AI)

> **Gate 1.4 Status:** **UNTESTED** (Gate 1.4 requires consented real smartphone recordings across acoustic environments).  
> **Evaluation Mode:** Synthetic text strings only (no audio, no Gnani STT).  

| Metric | Measured on Synthetic Text | Target | Gate 1.4 Status |
| :--- | :---: | :---: | :---: |
| **Top-1 Scheme Accuracy** | **70.0% (7/10)** | $\ge 70.0\%$ | **UNTESTED** |
| **Top-5 Retrieval Recall** | **90.0% (9/10)** | $\ge 90.0\%$ | **UNTESTED** |
| **Average Retrieval Latency** | **486.8 ms** | $< 500$ ms | **UNTESTED** |

**Critical Finding on Retrieval Miss `t03`:**  
The single complete retrieval miss was query `t03` (*"kudumbathula oru penukku 1000 tharanga la adhu epdi apply panradhu?"*), which targets the **Kalaignar Magalir Urimai Thittam** scheme. The query failed to retrieve the target scheme because colloquial phrasing without the scheme keyword 'magalir' did not match the document index.

---

## 3. Step 4B: Query Understanding & Paraphrase Sanity Check ($n=20$)

> **Status:** **Development check, not evidence.**  
> **Note:** These 20 queries were authored *after* the scheme aliases database was created and are **not held-out**. They verify alias mapping mechanics, but do not provide held-out proof.  

| Metric | Measured Result | Finding |
| :--- | :---: | :--- |
| **Top-5 Retrieval Recall** | **100.0% (20/20)** | Development check on alias expansion |
| **False Refusal Rate ($< 0.35$)** | **5.0% (1/20)** | Query `p20` routed to candidate clarification |
| **Average Pipeline Latency** | **379.0 ms** | Fast deterministic normalization |

---

## 4. Step 5: Sentence-by-Sentence Speech Synthesis (Gnani Timbre TTS)

- **Abbreviation Protection:** Regex protects `Rs.`, `ரூ.`, `रु.`, `No.`, `Dr.`, and `p.` from false sentence boundary splitting.
- **Indic Amount Spelling:** Monetary values are deterministically converted into full Indic words (*ஆயிரம் ரூபாய்* / *एक हज़ार रुपये*) via `voice/numbers.py`.
- **Playback Queueing:** Sentence 1 begins playing immediately while Sentence 2 pre-fetches in the background.
- **Instant Abort Control:** Client-side stop button invokes `AbortController.abort()` to halt audio synthesis and playback immediately.
- **Unit Verification:** 4 unit tests passing in `tests/test_sentence_speech.py` with 0 real Gnani calls.

---

## 5. Step 7: Gnani-Centred Voice Uncertainty Confirmation

- **Uncertainty Trigger Conditions:**
  1. Retrieval confidence score in the near-threshold band: $0.30 \le \text{confidence} \le 0.40$.
  2. STT confidence score (if returned by Gnani API) $< 0.60$.
  3. *(Note: The 'under 3 words' rule was dropped per empirical guidance to avoid false confirmations on clear short queries like 'Atal Pension').*
- **Confirmation Prompts (4 Languages):**
  - **English:** *"I heard {scheme}. Is that right?"*
  - **Tamil:** *"நான் {scheme} என்று கேட்டேன். சரியா?"*
  - **Hindi:** *"मैंने {scheme} सुना। क्या यह सही है?"*
  - **Tanglish:** *"Naan {scheme} nu ketten. Sariyaa?"*
- **Unit Verification:** 4 unit tests passing in `tests/test_voice_step7.py`.

---

## 6. Safety, Caching & Privacy Summary

- **Semantic Cache:** Wrong-match rate on non-matching questions is **unmeasured**; cache is **disabled by default for the demo** (`answer_cache_size = 0`).
- **Helpline Numbers:** In `data/contacts.json`, only Atal Pension Yojana has a cited brochure reference; the other 9 schemes remain null/unverified pending manual confirmation.
- **Daily Call Cap:** 2 / 100 Gnani calls used today in `logs/gnani-calls.json`.
- **Privacy Audit:** `/ask` and `/transcribe` log 0 audio and 0 cleartext questions (using `question_hash`). In contrast, `/feedback` currently writes raw question strings and free-text critique to `logs/feedback.jsonl`.
- **Test Integrity:** **476 passed, 10 deselected** across the full repository test suite.
