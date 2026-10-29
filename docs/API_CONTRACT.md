# Pakkam API Response Contract Specification (Finalized)

**Status:** Authoritative API Contract  
**Last Updated:** 2026-10-29  
**Scope:** Defines public endpoint contracts, supported statuses, payload schemas, and mock response samples for backend and frontend integration.

---

## 1. Endpoints Overview

| Method | Endpoint | Description | Primary Payload Keys |
| :--- | :--- | :--- | :--- |
| `POST` | `/ask` | Text inquiry answering (RAG, fact card, or fallback) | `answer`, `status`, `citations`, `timings_ms` |
| `POST` | `/ask/sources` | Instant sources pre-fetch (<400ms) | `sources [{doc_id, title, page, snippet}]` |
| `POST` | `/ask/voice` | End-to-end voice question answering | Inherits `/ask` + `transcript`, `stt_ms`, `confirmation_text` |
| `POST` | `/transcribe` | Single-stage speech-to-text (Gnani Prisma) | `transcript`, `stt_language_code`, `stt_ms` |
| `POST` | `/speak` | Spoken sentence synthesis (Gnani Timbre WAV) | Binary `audio/wav` response |
| `POST` | `/feedback` | Citizen feedback & rating | `recorded: true` (privacy-safe, text opt-in only) |
| `GET` | `/health` | Health & subsystem readiness check | `status: "ok"`, subsystem details |

---

## 2. Response Statuses and Payload Samples

### Status 1: `SUPPORTED` (Grounded Answer with Citations)
Returned when retrieval confidence is high ($\ge 0.35$) and the LLM produces a grounded, verified answer.

```json
{
  "answer": "Under the PM-KISAN scheme, eligible landholding farmer families receive Rs 6,000 per year in three equal installments of Rs 2,000 each. [1]",
  "language": "en",
  "refused": false,
  "status": "SUPPORTED",
  "path": "rag",
  "needs_confirmation": false,
  "refusal_reason": null,
  "sentences": [
    {
      "text": "Under the PM-KISAN scheme, eligible landholding farmer families receive Rs 6,000 per year in three equal installments of Rs 2,000 each.",
      "citations": [1]
    }
  ],
  "citations": [
    {
      "number": 1,
      "scheme": "PM-KISAN",
      "doc_id": "pmkisan-guidelines-2020-en",
      "document": "PM-KISAN Operational Guidelines",
      "page": 2,
      "page_start": 2,
      "page_end": 2,
      "source_url": "https://pmkisan.gov.in/",
      "excerpt": "Under the scheme, financial assistance of Rs. 6000/- per annum is provided to all eligible landholding farmer families...",
      "snippet": "Under the scheme, financial assistance of Rs. 6000/- per annum is provided...",
      "document_date": "2020-02-01",
      "language": "en",
      "ocr_corrected": false
    }
  ],
  "confidence": 0.9698,
  "disclaimer": "Informational only; not an official government service. Verify with official sources.",
  "latency_ms": 7357.4,
  "timings_ms": {
    "search": 208.5,
    "rerank": 145.0,
    "llm_answer": 5299.9,
    "verifier": 1421.6,
    "total": 7357.4
  },
  "contact": null
}
```

---

### Status 2: `needs_clarification` (Near-Threshold Ambiguity)
Returned when top retrieval score falls in the near-threshold band $[0.30, 0.35)$. Prompts the citizen with candidate schemes rather than flat refusal.

```json
{
  "answer": "Did you mean one of these schemes?\n1. Pudhumai Penn Scheme\n2. Kalaignar Magalir Urimai Thittam\n\nPlease reply with the scheme name.",
  "language": "en",
  "refused": false,
  "status": "needs_clarification",
  "path": "rag",
  "needs_confirmation": false,
  "refusal_reason": null,
  "candidate_schemes": [
    "Pudhumai Penn Scheme",
    "Kalaignar Magalir Urimai Thittam"
  ],
  "understood_query": "monthly college aid for women",
  "sentences": [],
  "citations": [],
  "confidence": 0.3240,
  "disclaimer": "Informational only; not an official government service. Verify with official sources.",
  "latency_ms": 382.1,
  "timings_ms": {
    "search": 210.0,
    "rerank": 150.0,
    "total": 382.1
  },
  "contact": null
}
```

---

### Status 3: `INSUFFICIENT_EVIDENCE` (Safe Grounded Refusal)
Returned when retrieval confidence is below 0.30, or the question is unanswerable from ingested government gazettes.

```json
{
  "answer": "I couldn't find this in the official scheme documents I have, so I can't answer it reliably. Please check the scheme's official website or ask at your nearest government service centre.",
  "language": "en",
  "refused": true,
  "status": "INSUFFICIENT_EVIDENCE",
  "path": "rag",
  "needs_confirmation": false,
  "refusal_reason": "low_confidence",
  "sentences": [],
  "citations": [],
  "confidence": 0.1250,
  "disclaimer": "Informational only; not an official government service. Verify with official sources.",
  "latency_ms": 412.3,
  "timings_ms": {
    "search": 235.1,
    "rerank": 160.2,
    "total": 412.3
  },
  "contact": null
}
```

---

### Status 4: `MODEL_UNAVAILABLE` (Never Fail Visibly Fallback)
Returned on LLM 429 rate limit, timeout, or external API disruption. Surfaces top retrieved passages and official helpline without hallucination.

```json
{
  "answer": "The answering model is currently busy. Here is what the official document states:\n\n1. Under the PM-KISAN scheme, landholding farmer families receive financial assistance of Rs. 6000 per year...",
  "language": "en",
  "refused": true,
  "status": "MODEL_UNAVAILABLE",
  "path": "fallback",
  "needs_confirmation": false,
  "refusal_reason": "service_unavailable",
  "passages": [
    {
      "text": "Under the PM-KISAN scheme, landholding farmer families receive financial assistance of Rs. 6000 per year in three equal installments.",
      "scheme": "PM-KISAN",
      "document": "PM-KISAN Operational Guidelines",
      "page": 2,
      "source_url": "https://pmkisan.gov.in/"
    }
  ],
  "contact": {
    "scheme": "PM-KISAN",
    "helpline": null,
    "helpline_source": null,
    "website": "https://pmkisan.gov.in"
  },
  "citations": [],
  "confidence": 0.9450,
  "disclaimer": "Informational only; not an official government service. Verify with official sources.",
  "latency_ms": 1150.2,
  "timings_ms": {
    "search": 205.0,
    "rerank": 140.0,
    "total": 1150.2
  }
}
```

---

### Status 5: Spoken Voice Response (`POST /ask/voice`)
Evaluates audio through Gnani Prisma STT, answers in short voice mode, and includes spoken confirmation prompts if retrieval score is ambiguous $[0.30, 0.40]$.

```json
{
  "transcript": "கலைஞர் மகளிர் உரிமைத் திட்டத்தில் எவ்வளவு பணம் கிடைக்கும்?",
  "stt_language_code": "ta-IN",
  "stt_ms": 1450.2,
  "stt_confidence": null,
  "answer": "கலைஞர் மகளிர் உரிமைத் திட்டத்தின் கீழ் குடும்பத் தலைவிகளுக்கு மாதம் ரூ. 1,000 வழங்கப்படுகிறது. [1]",
  "language": "ta",
  "refused": false,
  "status": "SUPPORTED",
  "path": "rag",
  "needs_confirmation": false,
  "confirmation_text": null,
  "sentences": [
    {
      "text": "கலைஞர் மகளிர் உரிமைத் திட்டத்தின் கீழ் குடும்பத் தலைவிகளுக்கு மாதம் ஆயிரம் ரூபாய் வழங்கப்படுகிறது.",
      "citations": [1]
    }
  ],
  "citations": [ ... ],
  "timings_ms": {
    "stt": 1450.2,
    "search": 210.1,
    "rerank": 145.0,
    "llm_answer": 4562.5,
    "verifier": 0.0,
    "total": 6367.8
  }
}
```

When retrieval score is in $[0.30, 0.40]$ band:
- `needs_confirmation: true`
- `confirmation_text: "நான் Kalaignar Magalir Urimai Thittam என்று கேட்டேன். சரியா?"`

---

### Status 6: Fast Sources-First Pre-Fetch (`POST /ask/sources`)
Fired in parallel from client submit; returns top official citations in <400ms before LLM generation finishes.

```json
{
  "question": "PM Kisan eligibility and amount",
  "sources": [
    {
      "doc_id": "pmkisan-guidelines-2020-en",
      "scheme": "PM-KISAN",
      "title": "PM-KISAN Operational Guidelines",
      "page": 2,
      "page_start": 2,
      "page_end": 2,
      "source_url": "https://pmkisan.gov.in/",
      "snippet": "Under the scheme, financial assistance of Rs. 6000/- per annum is provided...",
      "relevance": 0.965,
      "document_date": "2020-02-01",
      "language": "en"
    }
  ],
  "latency_ms": 352.9,
  "timings_ms": {
    "search": 205.6,
    "rerank": 145.0,
    "total": 352.9
  }
}
```

---

### Status 7: Privacy-Safe Citizen Feedback (`POST /feedback`)
Opt-in design. By default, records only performance and thumbs rating.

**Request:**
```json
{
  "status": "SUPPORTED",
  "thumbs": "up",
  "language": "ta",
  "timings_ms": {"total": 420.5},
  "include_text": false,
  "question": null,
  "reason": null
}
```

**Response:**
```json
{
  "recorded": true,
  "message": "Feedback recorded. Thank you for improving Pakkam."
}
```
