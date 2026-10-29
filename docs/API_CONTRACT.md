# Pakkam API Response Contract Specification (Finalized)

**Status:** Authoritative API Contract  
**Last Updated:** 2026-10-30  
**Scope:** Defines public endpoint contracts, supported statuses, payload schemas, and mock response samples for backend and frontend integration.

---

## 1. Endpoints Overview

| Method | Endpoint | Description | Primary Payload Keys | Origin / Real Output Status |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/ask` | Text inquiry answering (RAG, fact card, or fallback) | `answer`, `status`, `sentences`, `citations`, `timings_ms`, `understood_query` | **Real Server Output** |
| `POST` | `/ask/sources` | Instant sources pre-fetch (<400ms) | `passages [{scheme, doc_id, document, page, text, source_url}]`, `timings_ms` | **Real Server Output** |
| `POST` | `/ask/voice` | End-to-end voice question answering | Inherits `/ask` + `transcript`, `stt_ms`, `confirmation_text` | **Hand-Written Mock** |
| `POST` | `/transcribe` | Single-stage speech-to-text (Gnani Prisma) | `transcript`, `stt_language_code`, `stt_ms` | **Hand-Written Mock** |
| `POST` | `/speak` | Spoken sentence synthesis (Gnani Timbre WAV) | Binary `audio/wav` response | **Real Server Output** |
| `POST` | `/feedback` | Citizen feedback & rating | `recorded: true` (privacy-safe, text opt-in only) | **Real Server Output** |
| `GET` | `/health` | Health & subsystem readiness check | `status: "ok"` | **Real Server Output** |

---

## 2. Response Statuses and Payload Samples

### Status 1: `SUPPORTED` (Grounded Answer with Citations)
*Returned when retrieval confidence is high ($\ge 0.35$) and the LLM produces a grounded, verified answer.*  
*Payload Origin:* **Real Server Output** (captured from live pipeline execution on PM-KISAN inquiry).

```json
{
  "answer": "Under the PM-KISAN scheme, eligible landholding farmer families receive Rs 6,000 per year in three equal installments of Rs 2,000 each. [1]",
  "language": "en",
  "refused": false,
  "status": "SUPPORTED",
  "path": "rag",
  "needs_confirmation": false,
  "refusal_reason": null,
  "understood_query": "PM Kisan ku evlo panam kidaikum?",
  "candidate_schemes": [],
  "passages": null,
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
*Returned when top retrieval score falls in the near-threshold band $[0.30, 0.35)$. Prompts the citizen with candidate schemes rather than flat refusal.*  
*Payload Origin:* **Hand-Written Mock Payload for Client Prototyping** (illustrates near-threshold disambiguation prompt shape).

```json
{
  "answer": "Did you mean one of these schemes?\n1. Pudhumai Penn Scheme\n2. Kalaignar Magalir Urimai Thittam\n\nPlease reply with the scheme name.",
  "language": "en",
  "refused": false,
  "status": "needs_clarification",
  "path": "rag",
  "needs_confirmation": false,
  "refusal_reason": null,
  "understood_query": "monthly college aid for women",
  "candidate_schemes": [
    "Pudhumai Penn Scheme",
    "Kalaignar Magalir Urimai Thittam"
  ],
  "passages": null,
  "sentences": [],
  "citations": [],
  "confidence": 0.324,
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
*Returned when retrieval confidence is below 0.30, or the question is unanswerable from ingested government gazettes.*  
*Payload Origin:* **Real Server Output** (captured from out-of-domain query execution).

```json
{
  "answer": "I couldn't find this in the official scheme documents I have, so I can't answer it reliably. Please check the scheme's official website or ask at your nearest government service centre.",
  "language": "en",
  "refused": true,
  "status": "INSUFFICIENT_EVIDENCE",
  "path": "rag",
  "needs_confirmation": false,
  "refusal_reason": "low_confidence",
  "understood_query": "how to apply for driving license renewal online",
  "candidate_schemes": [],
  "passages": null,
  "sentences": [],
  "citations": [],
  "confidence": 0.125,
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
*Returned on LLM 429 rate limit, timeout, or external API disruption. Surfaces top retrieved passages and official helpline without hallucination.*  
*Payload Origin:* **Real Server Output** (captured during simulated model unavailable / timeout failover).

```json
{
  "answer": "The answering model is currently busy. Here is what the official document states:\n\n1. Under the PM-KISAN scheme, landholding farmer families receive financial assistance of Rs. 6000 per year...",
  "language": "en",
  "refused": true,
  "status": "MODEL_UNAVAILABLE",
  "path": "fallback",
  "needs_confirmation": false,
  "refusal_reason": "service_unavailable",
  "understood_query": "PM Kisan pension payment amount",
  "candidate_schemes": [],
  "passages": [
    {
      "text": "Under the PM-KISAN scheme, landholding farmer families receive financial assistance of Rs. 6000 per year in three equal installments.",
      "scheme": "PM-KISAN",
      "doc_id": "pmkisan-guidelines-2020-en",
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
  "sentences": [],
  "citations": [],
  "confidence": 0.945,
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

### Status 5: `PII_DETECTED` (Privacy Guardrail Interception)
*Returned immediately before retrieval or LLM execution if the query contains personal identifying numbers (Aadhaar or 10-digit Indian mobile numbers in ASCII or Indic Tamil/Devanagari numerals).*  
*Payload Origin:* **Real Server Output** (captured from live query with Aadhaar number).

```json
{
  "answer": "For your privacy and security, please do not share personal numbers such as Aadhaar or phone numbers. Pakkam only provides general scheme eligibility information.",
  "language": "en",
  "refused": true,
  "status": "PII_DETECTED",
  "path": "guardrail",
  "needs_confirmation": false,
  "refusal_reason": "pii_detected",
  "understood_query": "my aadhaar is [intercepted] can i apply",
  "candidate_schemes": [],
  "passages": null,
  "sentences": [],
  "citations": [],
  "confidence": 0.0,
  "disclaimer": "Informational only; not an official government service. Verify with official sources.",
  "latency_ms": 1.2,
  "timings_ms": {
    "total": 1.2
  },
  "contact": null
}
```

> **Note on Spoken Digit Words:** The PII guard detects digit sequences (ASCII digits, spaced, hyphenated, and Indic Tamil `\u0be6-\u0bef` / Devanagari `\u0966-\u096f` numerals). Spoken number words (e.g. "nine eight seven..." or "ஒன்பது எட்டு ஏழு...") are not converted to digits before regex matching and are currently unintercepted; speech transcripts with spelled-out number words rather than digits require an STT text-to-numeral normalizer before the PII filter.

---

### Status 6: Spoken Voice Response (`POST /ask/voice`)
*Evaluates audio through Gnani Prisma STT, answers in short voice mode, and includes spoken confirmation prompts if retrieval score is ambiguous $[0.30, 0.40]$.*  
*Payload Origin:* **Hand-Written Mock Payload for Client Prototyping** (shows end-to-end voice envelope for teammate frontend integration while physical mic is offline).

```json
{
  "transcript": "கலைஞர் மகளிர் உரிமைத் திட்டத்தில் எவ்வளவு பணம் கிடைக்கும்?",
  "stt_language_code": "ta-IN",
  "stt_ms": 1450.2,
  "stt_confidence": null,
  "confirmation_text": null,
  "answer": "கலைஞர் மகளிர் உரிமைத் திட்டத்தின் கீழ் குடும்பத் தலைவிகளுக்கு மாதம் ரூ. 1,000 வழங்கப்படுகிறது. [1]",
  "language": "ta",
  "refused": false,
  "status": "SUPPORTED",
  "path": "rag",
  "needs_confirmation": false,
  "refusal_reason": null,
  "understood_query": "கலைஞர் மகளிர் உரிமைத் திட்டத்தில் எவ்வளவு பணம் கிடைக்கும்?",
  "candidate_schemes": [],
  "passages": null,
  "sentences": [
    {
      "text": "கலைஞர் மகளிர் உரிமைத் திட்டத்தின் கீழ் குடும்பத் தலைவிகளுக்கு மாதம் ஆயிரம் ரூபாய் வழங்கப்படுகிறது.",
      "citations": [1]
    }
  ],
  "citations": [
    {
      "number": 1,
      "scheme": "Kalaignar Magalir Urimai Thittam",
      "doc_id": "kmut-guidelines-2023-ta",
      "document": "KMUT Implementation Guidelines",
      "page": 1,
      "page_start": 1,
      "page_end": 1,
      "source_url": "https://kmut.tn.gov.in/",
      "excerpt": "குடும்பத் தலைவிகளுக்கு மாதம் ரூ. 1,000 உரிமைத் தொகை...",
      "snippet": "குடும்பத் தலைவிகளுக்கு மாதம் ரூ. 1,000...",
      "document_date": "2023-08-01",
      "language": "ta",
      "ocr_corrected": false
    }
  ],
  "confidence": 0.952,
  "disclaimer": "Informational only; not an official government service. Verify with official sources.",
  "latency_ms": 6367.8,
  "timings_ms": {
    "stt": 1450.2,
    "search": 210.1,
    "rerank": 145.0,
    "llm_answer": 4562.5,
    "verifier": 0.0,
    "total": 6367.8
  },
  "contact": null
}
```

When retrieval score is in $[0.30, 0.40]$ band:
- `needs_confirmation: true`
- `confirmation_text: "நான் Kalaignar Magalir Urimai Thittam என்று கேட்டேன். சரியா?"`

---

### Status 7: Fast Sources-First Pre-Fetch (`POST /ask/sources`)
*Fired in parallel from client submit; returns top official citations in <400ms before LLM generation finishes.*  
*Payload Origin:* **Real Server Output** (captured from live Qdrant hybrid retrieval execution).

```json
{
  "passages": [
    {
      "scheme": "PM-KISAN",
      "doc_id": "pmkisan-guidelines-2020-en",
      "document": "PM-KISAN Operational Guidelines",
      "page": 2,
      "text": "Under the scheme, financial assistance of Rs. 6000/- per annum is provided...",
      "source_url": "https://pmkisan.gov.in/"
    }
  ],
  "timings_ms": {
    "search": 205.6,
    "rerank": 145.0,
    "total": 352.9
  }
}
```

---

### Status 8: Privacy-Safe Citizen Feedback (`POST /feedback`)
*Opt-in design. By default, records only performance and thumbs rating.*  
*Payload Origin:* **Real Server Output** (captured from default submission).

```json
{
  "recorded": true,
  "retained_fields": [
    "status",
    "thumbs",
    "language",
    "timings_ms"
  ],
  "message": "Feedback recorded anonymously without personal data."
}
```
