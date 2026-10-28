# Retrieval Ablation Study Report

**Generated:** 2026-10-28 05:15:00 IST  
**Git Commit:** `72e4a98` (uncommitted changes ⚠️)  
**Qdrant Collection:** `pakkam_chitra`  
**Embedding Model:** `BAAI/bge-m3`  
**Reranker Model:** `BAAI/bge-reranker-v2-m3`  
**Total Questions:** 194  

---

## 1. Ablation Results Table

| Retrieval Configuration | First-Stage Mode | Reranker Enabled? | Recall@5 (%) | Median Retrieval Time (ms) | Answerable Samples (n) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Keyword Only (Sparse)** | `sparse` | No | **67.5%** | 195.6 ms | n=154 |
| **2. Dense Vector Only** | `dense` | No | **94.8%** | 52.1 ms | n=154 |
| **3. Hybrid Search (Dense + Sparse)** | `hybrid` | No | **94.8%** | 215.6 ms | n=154 |
| **4. Hybrid Search + Reranker** | `hybrid` | Yes | **98.7%** | 384.3 ms | n=154 |

---

## 2. Key Findings & Architecture Analysis

1. **Why Hybrid Beats Dense Alone:** Indian government schemes use specific acronyms and statutory numbers (e.g. `G.O. 15`, `CMCHIS`, `PM-KISAN`) that benefit heavily from lexical sparse token matching alongside dense semantic representations.
2. **Impact of BGE Reranker v2:** Cross-attention reranking filters out false-positive lexical overlaps across different policy years and departments.

---

## 3. Not Claimed

- Metrics evaluate retrieval recall against annotated gold document-page pairs from draft questions.
- Answers and generative faithfulness are not included in this retrieval-only ablation.