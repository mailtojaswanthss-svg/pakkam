"""Per-stage latency benchmark on 10 representative citizen queries.

Measures median and p95 latency for each stage:
- search (first stage retrieval)
- rerank (BGE reranker)
- llm_answer (generation)
- verifier (answer verification)
- total (end-to-end latency)

Outputs: docs/review/SPEED_REPORT.md
"""

import json
import logging
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from schemebot.config import get_settings
from schemebot.generate.factory import build_answerer
from schemebot.retrieve.factory import build_retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("speed_benchmark")

# 10 Representative questions covering all 4 languages and key schemes
BENCHMARK_QUESTIONS = [
    {"id": "q001", "lang": "ta", "q": "புதுமைப்பெண் திட்டத்தின் கீழ் மாணவிகளுக்கு மாதந்தோறும் எவ்வளவு உதவித்தொகை வழங்கப்படுகிறது?"},
    {"id": "q002", "lang": "ta", "q": "முதலமைச்சரின் விரிவான மருத்துவக் காப்பீட்டுத் திட்டத்தில் பயன்பெற குடும்ப ஆண்டு வருமான வரம்பு என்ன?"},
    {"id": "q003", "lang": "en", "q": "How much financial assistance is provided per year under PM-KISAN?"},
    {"id": "q004", "lang": "en", "q": "What is the minimum pension guaranteed under Atal Pension Yojana?"},
    {"id": "q005", "lang": "hi", "q": "पीएम किसान सम्मान निधि योजना के तहत किसानों को सालाना कितनी राशि मिलती है?"},
    {"id": "q006", "lang": "hi", "q": "अटल पेंशन योजना में शामिल होने के लिए न्यूनतम और अधिकतम आयु सीमा क्या है?"},
    {"id": "q007", "lang": "ta-Latn", "q": "Pudhumai penn scheme ku evlo monthly amount tharanga?"},
    {"id": "q008", "lang": "ta-Latn", "q": "CMCHIS scheme la apply panna annual family income limit evlo?"},
    {"id": "q009", "lang": "en", "q": "What is the security deposit for new LPG connection under PMUY?"},
    {"id": "q010", "lang": "ta", "q": "கலைஞர் மகளிர் உரிமைத் திட்டத்தின் கீழ் பயன்பெற தகுதிகள் என்ன?"},
]

OUT_REPORT = PROJECT_ROOT / "docs" / "review" / "SPEED_REPORT.md"


def get_git_info() -> tuple[str, bool]:
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT_ROOT, text=True).strip()
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=PROJECT_ROOT, text=True).strip()
        return commit, (len(status) == 0)
    except Exception:
        return "unknown", False


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_v = sorted(values)
    idx = int(0.95 * len(sorted_v))
    return sorted_v[min(idx, len(sorted_v) - 1)]


def main():
    settings = get_settings()
    logger.info("Initializing retriever and answerer for speed benchmark...")
    retriever = build_retriever(settings, use_reranker=True)
    answerer = build_answerer(settings, retriever)

    results = []
    stage_timings: dict[str, list[float]] = {
        "search": [],
        "rerank": [],
        "llm_answer": [],
        "verifier": [],
        "total": [],
    }

    logger.info("Starting latency evaluation across %d questions...", len(BENCHMARK_QUESTIONS))

    for idx, item in enumerate(BENCHMARK_QUESTIONS, start=1):
        q = item["q"]
        qid = item["id"]
        lang = item["lang"]
        logger.info("[%d/%d] Running %s (%s): %s...", idx, len(BENCHMARK_QUESTIONS), qid, lang, q[:40])

        t0 = time.perf_counter()
        ans = answerer.answer(q)
        wall_ms = (time.perf_counter() - t0) * 1000

        t_data = dict(ans.timings_ms)
        t_data["total"] = wall_ms

        for k in stage_timings:
            val = t_data.get(k, 0.0)
            if val > 0:
                stage_timings[k].append(val)

        results.append({
            "id": qid,
            "lang": lang,
            "question": q,
            "refused": ans.refused,
            "confidence": round(ans.confidence, 4),
            "timings_ms": {k: round(v, 1) for k, v in t_data.items()},
        })

    commit, is_clean = get_git_info()
    clean_flag = "clean ✅" if is_clean else "uncommitted changes ⚠️"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")

    report_lines = [
        "# Pakkam End-to-End Latency & Speed Benchmark Report",
        "",
        f"**Generated:** {now_str}  ",
        f"**Git Commit:** `{commit}` ({clean_flag})  ",
        f"**Qdrant Collection:** `{settings.qdrant_collection}`  ",
        f"**LLM Provider:** `{settings.llm_provider}` (`{settings.llm_model}`)  ",
        f"**Sample Count (n):** 10 prepared representative citizen questions  ",
        "",
        "---",
        "",
        "## 1. Per-Stage Latency Summary",
        "",
        "| Pipeline Stage | Sample Count (n) | Median Latency (ms) | p95 Latency (ms) | Min (ms) | Max (ms) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    stage_names = {
        "search": "1. First-Stage Dense+Sparse Search",
        "rerank": "2. BGE Reranker v2",
        "llm_answer": "3. Primary Answer LLM Generation",
        "verifier": "4. Grounding Verifier Guardrail",
        "total": "**5. Full End-to-End Pipeline**",
    }

    for k, label in stage_names.items():
        vals = stage_timings[k]
        if vals:
            med = statistics.median(vals)
            p_95 = p95(vals)
            min_v = min(vals)
            max_v = max(vals)
            report_lines.append(f"| {label} | {len(vals)} | {med:.1f} ms | {p_95:.1f} ms | {min_v:.1f} ms | {max_v:.1f} ms |")

    report_lines.extend([
        "",
        "---",
        "",
        "## 2. Per-Question Detailed Breakdown",
        "",
        "| ID | Lang | Question Excerpt | Refused? | Search (ms) | Rerank (ms) | LLM (ms) | Verifier (ms) | Total (ms) |",
        "| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])

    for r in results:
        t = r["timings_ms"]
        q_snippet = (r["question"][:45] + "...") if len(r["question"]) > 45 else r["question"]
        report_lines.append(
            f"| `{r['id']}` | `{r['lang']}` | {q_snippet} | {r['refused']} | "
            f"{t.get('search', 0.0):.1f} | {t.get('rerank', 0.0):.1f} | "
            f"{t.get('llm_answer', 0.0):.1f} | {t.get('verifier', 0.0):.1f} | {t.get('total', 0.0):.1f} |"
        )

    report_lines.extend([
        "",
        "---",
        "",
        "## 3. Not Claimed",
        "",
        "- Latencies measured on single local workstation under warm GPU cache.",
        "- Network variability from LLM APIs (Claude/Gemini) can cause outliers during peak server hours.",
    ])

    OUT_REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    logger.info("SUCCESS: Wrote speed report to %s", OUT_REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
