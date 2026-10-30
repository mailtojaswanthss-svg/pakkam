# Pakkam 2.0 - Live Demonstration Runbook

This guide contains step-by-step instructions for conducting an interactive demonstration of Pakkam 2.0, covering pre-flight checks, vetted queries across all 4 languages, voice interaction, and contingency fallbacks.

---

## 1. Pre-Flight Verification (10 Minutes Prior to Demo)

1. **Start the Backend:**
   ```powershell
   $env:PYTHONPATH="src"
   $env:SCHEMEBOT_QDRANT_COLLECTION="pakkam_chitra"
   uv run python -m uvicorn schemebot.api.main:app --host 0.0.0.0 --port 8000
   ```
2. **Verify System Health Diagnostics (`GET /health`):**
   Open in browser or run:
   ```powershell
   curl http://localhost:8000/health
   ```
   **Expected Response:**
   ```json
   {
     "status": "ok",
     "models": {
       "llm_provider": "gemini",
       "llm_model": "gemini-3.8-flash",
       "embedding_model": "BAAI/bge-m3",
       "reranker_model": "BAAI/bge-reranker-v2-m3",
       "tts_model": "timbre-v3.0"
     },
     "retrieval_ready": true,
     "gnani_voice_ready": true,
     "preload_status": "ready",
     "quota": {
       "daily_limit": 20,
       "used_today": 3,
       "remaining_today": 17,
       "low_quota_warning": false
     }
   }
   ```
   *Verify that remaining LLM quota is $\ge 5$ calls and zero API keys are exposed.*
3. **Open the Web Interface:**
   - Citizen Web App: [http://localhost:8000/chat/](http://localhost:8000/chat/)
   - Confirm audio permissions are allowed in the browser.

---

## 2. Tested Demonstration Queries (4 Languages)

Use these synthetic, verified queries during live presentations:

### Scenario A: Tamil Native Text / Voice Query (Education Scheme)
- **Spoken / Typed Input:**
  `புதுமைப்பெண் திட்டத்தின் கீழ் மாணவிகளுக்கு மாதந்தோறும் எவ்வளவு உதவித்தொகை வழங்கப்படுகிறது?`
- **Expected Outcome:**
  - Status: `SUPPORTED`
  - Answer: *புதுமைப்பெண் திட்டத்தின் கீழ் அரசுப் பள்ளிகளில் பயின்று உயர்கல்வி சேரும் மாணவிகளுக்கு மாதந்தோறும் ரூ. 1,000 உதவித்தொகை வழங்கப்படுகிறது. [1]*
  - Citation: TN Higher Education Department Policy Note (p. 33)
  - Timings: Fast Sources pre-fetch in ~350 ms; voice playback starts at Sentence 1 in ~2.8s.

### Scenario B: Tanglish Code-Mixed Voice Query
- **Spoken / Typed Input:**
  `Pudhumai penn scheme la apply panna evlo monthly amount tharanga?`
- **Expected Outcome:**
  - Query Understanding cleans fillers and glosses Tanglish words.
  - Correctly routes to Pudhumai Penn scheme with 100% precision.
  - Answers: *மாதந்தோறும் ரூ. 1,000 வழங்கப்படுகிறது.*

### Scenario C: Hindi Agricultural Welfare Query
- **Spoken / Typed Input:**
  `पीएम किसान सम्मान निधि योजना के तहत किसानों को सालाना कितनी राशि मिलती है?`
- **Expected Outcome:**
  - Status: `SUPPORTED`
  - Answer: *पीएम किसान योजना के अंतर्गत पात्र किसानों को प्रति वर्ष ₹6,000 की वित्तीय सहायता ₹2,000 की तीन समान किस्तों में प्रदान की जाती है। [1]*
  - Citation: PM-KISAN Operational Guidelines (p. 3)

### Scenario D: English Pension Query
- **Spoken / Typed Input:**
  `What is the minimum monthly pension guaranteed under Atal Pension Yojana?`
- **Expected Outcome:**
  - Status: `SUPPORTED`
  - Answer: *Under Atal Pension Yojana, subscribers receive a minimum guaranteed monthly pension of ₹1,000 to ₹5,000 depending on contributions.*
  - Citation: APY Official Brochure (p. 1)

### Scenario E: Out-of-Domain Refusal & Safety Guardrail
- **Spoken / Typed Input:**
  `Can I get a driving license under the CMCHIS health insurance scheme?`
- **Expected Outcome:**
  - Status: `INSUFFICIENT_EVIDENCE`
  - Answer: *I cannot find information about driving licenses under CMCHIS in the official government documents.*
  - Contact Card: Official CMCHIS portal ([cmchistn.com](https://cmchistn.com)) and toll-free helpline.
  - Guardrail: Never hallucinates non-existent benefits.

---

## 3. Contingency Fallback Procedures

| Failure Mode | Immediate Behavior | Demonstration Talking Point |
|---|---|---|
| **LLM 429 Rate Limit / Timeout** | System executes Step 6 "Never Fail Visibly". Displays top 3 official citations and verified helpline. | *"Our architecture prioritizes citizen resilience: if the generative LLM experiences latency spikes, verified citations and helplines are served immediately from the local index."* |
| **Microphone / STT Network Drop** | Web UI displays speech error toast and automatically opens the text chat input. | *"Multimodal accessibility ensures users in low-bandwidth rural conditions can seamlessly switch to typing or voice notes."* |
| **Low Daily Quota Alert** | `/health` displays `low_quota_warning: true` when remaining $\le 5$. Fast Sources continue operating with 0 LLM calls. | *"The application includes a strict code-level budget guard that prevents unexpected cloud credit depletion."* |

---

## 4. Post-Demo Shutdown

1. Press `Ctrl + C` in the uvicorn terminal.
2. Inspect session metrics:
   ```powershell
   uv run python scripts/review_feedback.py
   ```
