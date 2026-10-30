# Gnani Voice Integration Runbook (Windows)

This runbook provides the exact steps to verify, run, and test voice capabilities (STT and TTS) in **Pakkam** on a Windows workstation.

---

## 1. Environment Setup

### 1.1 Configure `.env`
Ensure your `.env` file has the required keys:
```bash
# Gnani API Credentials
SCHEMEBOT_GNANI_API_KEY=your_key_here
SCHEMEBOT_GNANI_MAX_CALLS_PER_DAY=100
SCHEMEBOT_TTS_MODEL=timbre-v3.0

# Hugging Face Access (for Kathbath benchmark dataset)
HF_TOKEN=hf_your_token_here
```

### 1.2 Verify Environment Health (Preflight Doctor)
Run the diagnostic script:
```powershell
python scripts/gnani_doctor.py
```
Expected output:
```
PREFLIGHT RESULT: ALL CHECKS PASSED ✅
```

---

## 2. Live Smoke Testing & Synthetic Plumbing

Test both Timbre TTS and Prisma STT with one live call each:
```powershell
python scripts/gnani_smoke.py
```
This tests:
1. Generating a spoken Tamil audio file with Timbre v3.0 (`Shivani` voice) saved to `data/voice/synthetic_smoke_ta.wav`.
2. Transcribing that audio back with Prisma v2.5 STT (`ta-IN`).
3. Checks that the daily call counter increments correctly in `logs/gnani-calls.json`.

---

## 3. Benchmark Dataset & STT Evaluation

### 3.1 Fetch Targeted Kathbath Sample (Tamil & Hindi Only)
Streams 15 Tamil and 15 Hindi clips (≤ 30s) directly from Hugging Face into `data/voice/kathbath/`:
```powershell
uv run python scripts/fetch_kathbath_sample.py
```

### 3.2 Run STT Evaluation
Computes Word Error Rate (WER) and latency against reference transcripts under the 40-call run cap:
```powershell
uv run python scripts/gnani_stt_eval.py
```
Results are saved to `data/voice/stt_eval_results.json`.

---

## 4. End-to-End Live Voice Chat in Browser

### 4.1 Start the Server
Start the FastAPI server:
```powershell
uv run fastapi run
```
The site runs at `http://localhost:8000`.

### 4.2 Interactive Voice Workflow
1. Open Chrome or Edge to: `http://localhost:8000/chat/`
2. Select your spoken language in the dropdown (e.g. **Tamil** or **Hindi**).
3. Click the **Mic** button.
4. When prompted by the browser, allow microphone access (`Allow`).
5. Speak your question (e.g., *"புதுமைப் பெண் திட்டத்தில் எவ்வளவு பணம் கிடைக்கும்?"*).
6. Click **Stop** (or wait for the automatic 30-second cap).
7. The transcribed text will appear in the chat input, followed by the grounded answer.
8. Click the **Listen (கேளுங்கள்)** button next to the answer to hear it spoken aloud via Timbre TTS.

---

## 5. Troubleshooting Table

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| **Microphone not working** | Browser permission denied | Click the camera/mic icon on the left of the browser URL bar and set Microphone to **Allow**. |
| **Mic disabled on remote IP** | Browsers block mic on plain HTTP | Access via `http://localhost:8000` or `http://127.0.0.1:8000` (which browsers treat as secure context). For remote access, use HTTPS or a Cloudflare tunnel. |
| **"Recording too long" error** | Audio exceeded 30 seconds | Keep voice questions concise (under 30s). The client auto-stops recording at 30 seconds. |
| **HTTP 503 "Voice input reached today's limit"** | Daily budget cap reached | The cap protects your credits. Check `logs/gnani-calls.json`. Cap resets at midnight IST or adjust `SCHEMEBOT_GNANI_MAX_CALLS_PER_DAY` in `.env`. |
| **HTTP 502 / Invalid Key** | Incorrect API key | Verify key at `app.gnani.ai/voice` and ensure no leading/trailing whitespace in `.env`. |
| **TTS Button Disabled / No Speech** | `SCHEMEBOT_TTS_MODEL` unset | Set `SCHEMEBOT_TTS_MODEL=timbre-v3.0` (or `timbre-v2.5`) in `.env`. |
| **Unsupported Audio Format (415)** | Non-standard container | The built-in converter (`schemebot.voice.audio`) uses `ffmpeg` to normalize to 16 kHz mono WAV. Ensure `ffmpeg -version` works in terminal. |
