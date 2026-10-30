# Streaming Architecture Design Note

**Status:** Design Proposal (No implementation in Step 2)  
**Target Step:** Step 4 ("Instant feel") & Step 5 ("Sentence-by-sentence speech")  
**Goal:** Deliver perceived sub-second response times for chat and voice pipelines by decoupling retrieval, sentence generation, claim verification, and text-to-speech synthesis into pipelined streams.

---

## 1. Problem Statement & Baseline Bottleneck

In the non-streaming baseline (Step 1):
1. User submits question.
2. Dense & lexical retrieval runs (~200–400 ms).
3. Cross-encoder reranker runs (~1,000–1,500 ms).
4. LLM processes entire prompt and outputs complete JSON response (~3,000–5,000 ms).
5. Deterministic claim verification runs on all sentences (~5 ms).
6. Entire text is sent to TTS synthesis (~800–1,500 ms).
7. First sound played to user after **8.4 to 9.2 seconds** (n=1 measured baseline).

The visitor waits through stages 2–6 before receiving any visual token or audible sound.

---

## 2. Pipelined Streaming Solution

Streaming reorganizes the pipeline into three overlapping asynchronous stages:

```
[ User Query ]
      │
      ▼
┌──────────────┐
│  Retrieval   │ ────► Emit Step 1: `event: sources` (immediate UI display)
└──────┬───────┘
       │ Chunks ready
       ▼
┌──────────────┐
│ LLM Stream   │ ────► Emit Step 2: `event: token` (live typing in chat)
└──────┬───────┘
       │ Sentences yielded incrementally
       ▼
┌──────────────┐
│ Claim Check  │ ────► Checks quote/numbers against retrieved chunks
└──────┬───────┘
       │ Valid sentence
       ▼
┌──────────────┐
│  Gnani TTS   │ ────► Synthesizes sentence 1 while LLM generates sentence 2
└──────────────┘
```

---

## 3. Core Technical Components

### A. Provider Streaming Protocol
Both Claude (`anthropic`) and Gemini (`google-genai`) SDKs support token-level streaming:
- **Claude:** `client.beta.messages.stream(...)` yielding `BetaRawMessageStreamEvent` / `text_delta`.
- **Gemini:** `client.models.generate_content_stream(...)` yielding `GenerateContentResponse` chunks.

Interface definition:
```python
class StreamingJsonLlm(Protocol):
    def stream_tokens(self, system: str, user: str, schema: dict[str, object]) -> Iterator[str]:
        """Yields raw JSON tokens incrementally as received from provider."""
        ...
```

### B. Incremental Sentence & Field Parser
Because models output structured JSON:
`{"answerable": true, "sentences": [{"text": "...", "citations": [...]}]}`

An incremental parser (e.g. tracking token buffer or standard JSON chunking):
1. Detects `"answerable": false` within first ~5 tokens; if false, aborts generation immediately to avoid token waste.
2. Collects character deltas inside `"text": "..."` values.
3. Detects sentence boundaries on punctuation (`.`, `!`, `?`, `\n`, or Indian punctuation `।`).
4. Yields individual complete sentences as soon as boundary is reached.

### C. Sentence-by-Sentence TTS Synthesis (Step 5)
1. **Sentence 1** is yielded by the streaming parser.
2. `verify_claims` checks whether numbers in Sentence 1 exist in retrieved chunks.
3. Sentence 1 is dispatched to Gnani Timbre API asynchronously.
4. Client begins playing audio for Sentence 1 while the LLM is midway through Sentence 2.
5. **Expected Target:** First-sound latency drops from ~8.5s to ~2.5–3.0s.

### D. Server-Sent Events (SSE) API Contract
Endpoint: `POST /ask/stream` and `POST /ask/voice/stream` (`Content-Type: text/event-stream`):

```http
event: step
data: {"step": "searching", "message": "Searching official documents..."}

event: sources
data: {"passages": [...], "document": "PM-KISAN Operational Guidelines", "page": 4, "url": "https://pmkisan.gov.in"}

event: token
data: {"delta": "Eligible"}

event: sentence
data: {"index": 0, "text": "Eligible farmers receive ₹6,000 annually in three equal instalments."}

event: audio_chunk
data: {"index": 0, "audio_base64": "...", "mime_type": "audio/wav"}

event: done
data: {"status": "ok", "timings_ms": {"retrieval": 220, "first_token": 650, "first_sentence": 1400, "first_audio": 2200, "total": 3100}}
```

---

## 4. Error Handling & Failover Guarantees

1. **Mid-stream 429 or Network Drop:**
   - If stream breaks before the first sentence finishes: catch `LlmUnavailableError`, fallback to static excerpt display: *"Model busy, here is what the official document states: [Excerpt]"*.
   - If secondary provider failover is enabled: abort broken stream, restart prompt on secondary provider.
2. **Quota Conservation:**
   - Client disconnect / abort signal immediately closes the provider HTTP stream, terminating generation to avoid billable/rate-limited token overconsumption.
