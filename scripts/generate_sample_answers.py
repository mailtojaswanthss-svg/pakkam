"""Generate docs/review/sample_answers.md for Prompt 3.

Evaluates 10 questions across specified categories:
- 3 amounts
- 2 eligibility
- 2 documents needed
- 1 Hindi
- 1 Tamil
- 1 unanswerable
"""

import logging
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from schemebot.config import get_settings
from schemebot.generate.factory import build_answerer
from schemebot.retrieve.factory import build_retriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sample_answers")

SAMPLE_QUESTIONS = [
    # 3 amounts
    {"id": "q004", "lang": "en", "cat": "Amount", "q": "How much money does a farmer get every year under PM-KISAN?"},
    {"id": "q049", "lang": "en", "cat": "Amount", "q": "How much health cover does a family get under the Chief Minister's Comprehensive Health Insurance Scheme?"},
    {"id": "q126", "lang": "en", "cat": "Amount", "q": "How much are the monthly food charges for BC and MBC school hostel students?"},
    # 2 eligibility
    {"id": "q001", "lang": "en", "cat": "Eligibility", "q": "Who can apply for Kalaignar Magalir Urimai Thittam?"},
    {"id": "q053", "lang": "en", "cat": "Eligibility", "q": "Who can get the Pudhumai Penn monthly assistance?"},
    # 2 documents needed
    {"id": "q008", "lang": "en", "cat": "Documents Needed", "q": "Which documents are needed for a new Ujjwala LPG connection?"},
    {"id": "q116", "lang": "en", "cat": "Documents Needed", "q": "Can a migrant family get an Ujjwala connection without address proof?"},
    # 1 Hindi
    {"id": "q025", "lang": "hi", "cat": "Hindi", "q": "पीएम किसान योजना में किसानों को साल में कितना पैसा मिलता है?"},
    # 1 Tamil
    {"id": "q013", "lang": "ta", "cat": "Tamil", "q": "கலைஞர் மகளிர் உரிமைத் திட்டத்தில் யார் விண்ணப்பிக்கலாம்?"},
    # 1 unanswerable
    {"id": "q010", "lang": "en", "cat": "Unanswerable", "q": "What is the interest rate on Sukanya Samriddhi Yojana deposits?"},
]

OUT_FILE = PROJECT_ROOT / "docs" / "review" / "sample_answers.md"


def main():
    settings = get_settings()
    logger.info("Initializing Answerer on collection: %s (Provider: %s)", settings.qdrant_collection, settings.llm_provider)
    retriever = build_retriever(settings, use_reranker=True)
    answerer = build_answerer(settings, retriever)

    out_lines = [
        "# Sample Real Answers Benchmark (10 Queries)",
        "",
        f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S IST')}  ",
        f"**Qdrant Collection:** `{settings.qdrant_collection}`  ",
        f"**LLM Model:** `{settings.gemini_model}` (Verifier: `{settings.gemini_verifier_model}`)  ",
        "",
        "> [!IMPORTANT]",
        "> **Non-Representative Sample Notice:** These 10 questions were deliberately chosen to inspect qualitative model behavior across specific query categories (amounts, eligibility rules, document prerequisites, Hindi cross-lingual retrieval, native Tamil, and out-of-domain unanswerable queries). They do not constitute a statistically representative sample of overall citizen distribution.",
        "",
        "---",
        "",
    ]

    for idx, item in enumerate(SAMPLE_QUESTIONS, start=1):
        qid = item["id"]
        q = item["q"]
        cat = item["cat"]
        lang = item["lang"]
        logger.info("[%d/%d] Processing %s (%s): %s...", idx, len(SAMPLE_QUESTIONS), qid, cat, q[:40])

        try:
            ans = answerer.answer(q)
            status_label = "INSUFFICIENT_EVIDENCE" if ans.refused else "SUPPORTED"
            refusal_reason = f" (Reason: `{ans.refusal_reason}`)" if ans.refused else ""

            out_lines.append(f"## {idx}. [{qid}] {q}")
            out_lines.append("")
            out_lines.append(f"- **Category:** `{cat}` | **Language:** `{lang}`")
            out_lines.append(f"- **Status:** `{status_label}`{refusal_reason} | **Retrieval Confidence:** `{ans.confidence:.4f}`")
            out_lines.append(f"- **Answer Text:** {ans.text}")
            out_lines.append("")

            if ans.citations:
                out_lines.append("### Citations & Supporting Passages")
                out_lines.append("")
                out_lines.append("| # | Document ID | Page | Excerpt / Supporting Passage |")
                out_lines.append("| :---: | :--- | :---: | :--- |")
                for c in ans.citations:
                    snippet_clean = c.text.replace("\n", " ").replace("|", "\\|")
                    page_str = str(c.page_start) if c.page_start == c.page_end else f"{c.page_start}-{c.page_end}"
                    out_lines.append(f"| {c.number} | `{c.doc_id}` ({c.scheme}) | {page_str} | {snippet_clean[:250]}... |")
                out_lines.append("")
            else:
                out_lines.append("- **Citations:** None (safely refused without citing ungrounded passages)")
                if ans.contact:
                    out_lines.append(f"- **Official Contact:** `{ans.contact.scheme}` ({ans.contact.website or ans.contact.helpline})")
                out_lines.append("")

            out_lines.append("---")
            out_lines.append("")

        except Exception as e:
            logger.error("Failed on %s: %s", qid, e)
            out_lines.append(f"## {idx}. [{qid}] {q} - ERROR")
            out_lines.append(f"Error during answering: {e}")
            out_lines.append("---")
            out_lines.append("")

        time.sleep(1.5)

    OUT_FILE.write_text("\n".join(out_lines), encoding="utf-8")
    logger.info("SUCCESS: Wrote sample answers to %s", OUT_FILE)


if __name__ == "__main__":
    main()
