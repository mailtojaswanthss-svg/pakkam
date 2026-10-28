# Pakkam End-to-End Latency & Speed Benchmark Report

**Generated:** 2026-10-28 05:26:18 IST  
**Git Commit:** `72e4a98` (uncommitted changes ⚠️)  
**Qdrant Collection:** `pakkam_chitra`  
**LLM Provider:** `gemini` (`claude-opus-5-5`)  
**Sample Count (n):** 10 prepared representative citizen questions  

---

## 1. Per-Stage Latency Summary

| Pipeline Stage | Sample Count (n) | Median Latency (ms) | p95 Latency (ms) | Min (ms) | Max (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 1. First-Stage Dense+Sparse Search | 10 | 399.1 ms | 984.0 ms | 347.2 ms | 984.0 ms |
| 2. BGE Reranker v2 | 10 | 236.8 ms | 491.6 ms | 197.2 ms | 491.6 ms |
| 3. Primary Answer LLM Generation | 9 | 6300.7 ms | 13416.6 ms | 3776.5 ms | 13416.6 ms |
| 4. Grounding Verifier Guardrail | 9 | 1378.5 ms | 1430.7 ms | 1003.3 ms | 1430.7 ms |
| **5. Full End-to-End Pipeline** | 10 | 8246.5 ms | 16276.0 ms | 5631.4 ms | 16276.0 ms |

---

## 2. Per-Question Detailed Breakdown

| ID | Lang | Question Excerpt | Refused? | Search (ms) | Rerank (ms) | LLM (ms) | Verifier (ms) | Total (ms) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `q001` | `ta` | புதுமைப்பெண் திட்டத்தின் கீழ் மாணவிகளுக்கு மா... | False | 984.0 | 247.8 | 5299.9 | 1421.6 | 7959.5 |
| `q002` | `ta` | முதலமைச்சரின் விரிவான மருத்துவக் காப்பீட்டுத்... | False | 467.6 | 279.5 | 6313.2 | 1428.6 | 8490.5 |
| `q003` | `en` | How much financial assistance is provided per... | False | 347.2 | 218.4 | 3776.5 | 1288.4 | 5631.4 |
| `q004` | `en` | What is the minimum pension guaranteed under ... | False | 415.8 | 491.6 | 7564.3 | 1378.5 | 9851.7 |
| `q005` | `hi` | पीएम किसान सम्मान निधि योजना के तहत किसानों क... | False | 487.9 | 248.1 | 5853.6 | 1122.8 | 7713.1 |
| `q006` | `hi` | अटल पेंशन योजना में शामिल होने के लिए न्यूनतम... | False | 382.4 | 253.0 | 5931.6 | 1430.7 | 7998.7 |
| `q007` | `ta-Latn` | Pudhumai penn scheme ku evlo monthly amount t... | False | 364.7 | 217.0 | 6300.7 | 1119.2 | 8002.5 |
| `q008` | `ta-Latn` | CMCHIS scheme la apply panna annual family in... | False | 364.1 | 197.2 | 12399.0 | 1003.3 | 13964.5 |
| `q009` | `en` | What is the security deposit for new LPG conn... | True | 380.5 | 225.8 | 0.0 | 0.0 | 16276.0 |
| `q010` | `ta` | கலைஞர் மகளிர் உரிமைத் திட்டத்தின் கீழ் பயன்பெ... | False | 473.2 | 208.4 | 13416.6 | 1421.2 | 15520.7 |

---

## 3. Not Claimed

- Latencies measured on single local workstation under warm GPU cache.
- Network variability from LLM APIs (Claude/Gemini) can cause outliers during peak server hours.