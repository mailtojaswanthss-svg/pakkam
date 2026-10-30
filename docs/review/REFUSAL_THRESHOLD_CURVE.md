# Refusal-Threshold Curve Sweep & Safety Calibration

**Generated:** 2026-10-28 05:17:20 IST  
**Git Commit:** `72e4a98` (uncommitted changes ⚠️)  
**Default Refusal Threshold:** `0.35` (active)  
**Qdrant Collection:** `pakkam_chitra`  
**Total Questions:** 194  

---

## 1. Refusal Operating Characteristic Curve

| Threshold | Operating Role | Correct Refusals (Unanswerable) | False Refusals (Answerable) | Overall Routing Accuracy |
| :---: | :--- | :---: | :---: | :---: |
| `0.20` | Permissive (risk of hallucination) | 31/40 (77.5%) | 15/154 (9.7%) | **87.6%** |
| `0.25` | Permissive (risk of hallucination) | 33/40 (82.5%) | 16/154 (10.4%) | **88.1%** |
| `0.30` | Permissive (risk of hallucination) | 34/40 (85.0%) | 21/154 (13.6%) | **86.1%** |
| `0.35` **[ACTIVE DEFAULT]** | Balanced Safety Default | 37/40 (92.5%) | 22/154 (14.3%) | **87.1%** |
| `0.40` | Aggressive refusal | 37/40 (92.5%) | 27/154 (17.5%) | **84.5%** |
| `0.45` | Aggressive refusal | 38/40 (95.0%) | 31/154 (20.1%) | **83.0%** |
| `0.50` | Aggressive refusal | 38/40 (95.0%) | 34/154 (22.1%) | **81.4%** |

---

## 2. Analysis & Recommendations

1. **Safety Grounding:** The active threshold of **`0.35`** sits at the inflection point between minimizing false refusals and intercepting queries about ungrounded schemes.
2. **Zero Modification Policy:** Per system instructions, the default threshold remains strictly at `0.35` pending human stakeholder review.

---

## 3. Not Claimed

- Unanswerable test queries represent out-of-domain scheme inquiries, not adversarial jailbreak attempts.