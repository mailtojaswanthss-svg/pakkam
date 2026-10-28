# Pakkam API Response Contract Specification

**Status:** Agreed Target State (Read-Only Specification)  
**Date:** 2026-10-28  
**Scope:** Defines current field mappings, proposed additions, and backwards-compatibility guardrails.

---

## 1. Current Live Responses (`POST /ask` and `POST /ask/voice`)

### Example: Live `/ask` Response
```json
{
  "answer": "Under the PM-KISAN scheme, eligible farmers receive Rs 6,000 per year in three equal installments of Rs 2,000 each. [1]",
  "language": "en",
  "refused": false,
  "status": "SUPPORTED",
  "needs_confirmation": true,
  "refusal_reason": null,
  "sentences": [
    {
      "text": "Under the PM-KISAN scheme, eligible farmers receive Rs 6,000 per year in three equal installments of Rs 2,000 each.",
      "citations": [1]
    }
  ],
  "citations": [
    {
      "number": 1,
      "scheme": "PM-KISAN",
      "doc_id": "pmkisan-guidelines-2020-en",
      "document": "Pradhan Mantri Kisan Samman Nidhi Guidelines",
      "page_start": 2,
      "page_end": 2,
      "page": 2,
      "source_url": "https://pmkisan.gov.in/",
      "excerpt": "Under the scheme, financial assistance of Rs. 6000/- per annum is provided...",
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
    "search": 399.1,
    "rerank": 236.8,
    "llm_answer": 5299.9,
    "verifier": 1421.6,
    "total": 7357.4
  },
  "contact": null
}
```

### Example: Live `/ask/voice` Response
Inherits all fields from `/ask`, plus voice metadata:
```json
{
  "transcript": "PM Kisan ku evlo panam kidaikum?",
  "stt_language_code": "ta-IN",
  "stt_ms": 1320.4,
  "answer": "PM-KISAN திட்டத்தின் கீழ் விவசாயிகளுக்கு ஆண்டுக்கு ரூ. 6,000 வழங்கப்படுகிறது. [1]",
  "language": "ta",
  "refused": false,
  "status": "SUPPORTED",
  "needs_confirmation": true,
  "citations": [ ... ],
  "timings_ms": {
    "stt": 1320.4,
    "search": 208.5,
    "rerank": 277.4,
    "total": 6850.2
  }
}
```

---

## 2. Proposed Contract vs. Current Implementation

| Proposed Field | Current Implementation Status | Action Plan |
| :--- | :--- | :--- |
| `status` (`ok`, `needs_confirmation`, `insufficient_evidence`, `model_unavailable`) | Exists as `"SUPPORTED"` \| `"INSUFFICIENT_EVIDENCE"` | Keep existing enum values for backwards compatibility; extend with `"MODEL_UNAVAILABLE"` in Prompt 5. |
| `path` (`fact_card`, `rag`, `fallback`) | **Missing** | Add to `AskResponse` with default `"rag"`. Non-breaking additive field. |
| `language` | **Already Exists** (`"en"`, `"ta"`, `"hi"`, `"ta-Latn"`) | Keep unchanged. |
| `transcript` | **Already Exists** on `/ask/voice` | Keep unchanged. |
| `needs_confirmation` (boolean vs object) | Exists as `bool` (triggers on digits or scheme names) | Keep `needs_confirmation: bool` for UI compatibility; add `confirmation_detail: {value, reason}` as optional. |
| `answer_text` | Exists as `answer` | **DO NOT RENAME:** Renaming `answer` to `answer_text` would break `web/chat/app.js`. Maintain `answer` and alias `answer_text`. |
| `sentences [{text, audio}]` | Exists as `sentences [{text, citations}]` | Keep `citations`; add optional `audio_url` or `audio` string. |
| `citations [{scheme, document, page, document_date, url}]` | Exists with `number, scheme, doc_id, document, page, excerpt, snippet, source_url, document_date` | Keep existing fields; `url` is aliased by `source_url`. |
| `passages` (fallback) | **Missing** | Add as `passages: list[FallbackPassage] | None` on model down. |
| `timings_ms` | Exists with `{search, rerank, llm_answer, verifier, total, stt}` | Keep unchanged. |

---

## 3. UI Protection Guarantee (Fields that must NOT be renamed)
The web chat application (`web/chat/`) directly depends on:
1. `answer` (string used for chat bubble rendering).
2. `citations` (array iterated for pill links: `number`, `document`, `page`, `source_url`).
3. `refused` (boolean checked to style disclaimer and warnings).
4. `status` (`"SUPPORTED"` or `"INSUFFICIENT_EVIDENCE"`).
5. `needs_confirmation` (boolean to highlight uncertainty).
6. `timings_ms` (rendered in the performance drawer).

All future changes (Prompt 5 onward) must add new fields additively without mutating or renaming these keys.
