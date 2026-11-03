"""Benchmark the deployed Pakkam (website -> tunnel -> laptop) on the evaluation questions.

Measures what a visitor gets, end to end:
- answerable questions: answered (not refused), and whether a cited page is a gold page
- questions the documents do not cover: refused (the honest answer)
- "busy" replies (model unavailable), and speed (p50 / p90) per language

Only the standard library is used, so it runs anywhere. It sleeps between questions to stay
under the free Gemini per-minute limit, and --per-group picks an even sample per language
(the daily LLM budget does not cover all 194 questions in one day).

    python scripts/live_benchmark.py --per-group 10
    python scripts/live_benchmark.py --url http://localhost:8000 --per-group 49

Writes data/eval/live_benchmark.json (raw replies) and docs/review/LIVE_BENCHMARK.md.
"""

import argparse
import json
import statistics
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "data" / "eval" / "questions.jsonl"
RAW_OUT = ROOT / "data" / "eval" / "live_benchmark.json"
REPORT_OUT = ROOT / "docs" / "review" / "LIVE_BENCHMARK.md"
GROUP_NAMES = {"en": "English", "ta": "Tamil", "hi": "Hindi", "ta-Latn": "Tanglish"}


def pick(questions: list[dict[str, Any]], per_group: int | None) -> list[dict[str, Any]]:
    """An even sample per language, keeping the answerable / not-covered mix of each group."""
    if per_group is None:
        return questions
    chosen: list[dict[str, Any]] = []
    for group in GROUP_NAMES:
        rows = [q for q in questions if q["group"] == group]
        covered = [q for q in rows if q["answerable"]]
        uncovered = [q for q in rows if not q["answerable"]]
        n_uncovered = max(1, round(per_group * len(uncovered) / max(len(rows), 1)))
        chosen += covered[: per_group - n_uncovered] + uncovered[:n_uncovered]
    return chosen


def ask(url: str, question: str, timeout: float) -> tuple[dict[str, Any] | None, float, str]:
    body = json.dumps({"question": question}).encode()
    request = urllib.request.Request(
        f"{url.rstrip('/')}/ask",
        body,
        # The debug header returns drafts the checks dropped, to explain each miss.
        {"Content-Type": "application/json", "X-Pakkam-Debug": "drafts"},
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
        return data, time.perf_counter() - started, ""
    except urllib.error.HTTPError as error:
        return None, time.perf_counter() - started, f"HTTP {error.code}"
    except (urllib.error.URLError, OSError) as error:  # timeouts, resets mid-reply
        return None, time.perf_counter() - started, str(error)[:80]


def gold_hit(question: dict[str, Any], data: dict[str, Any]) -> bool:
    gold = {(g["doc_id"], page) for g in question["gold"] for page in g["pages"]}
    cited = {
        (c["doc_id"], page)
        for c in data.get("citations", [])
        for page in range(c["page_start"], c["page_end"] + 1)
    }
    return bool(gold & cited)


def grade(question: dict[str, Any], data: dict[str, Any] | None, error: str) -> dict[str, Any]:
    if data is None:
        return {"outcome": "error", "detail": error}
    status = data.get("status")
    if status == "MODEL_UNAVAILABLE":
        return {"outcome": "busy"}
    answered = not data.get("refused") and bool(data.get("sentences"))
    discovery = data.get("path") == "discovery" or status == "needs_clarification"
    if not question["answerable"]:
        return {"outcome": "correct_refusal" if not answered else "answered_uncovered"}
    if discovery:
        return {"outcome": "clarified"}
    if not answered:
        reasons = ",".join(data.get("rejected_reasons") or [])
        return {"outcome": "missed", "reason": f"{data.get('refusal_reason')} {reasons}".strip()}
    return {"outcome": "answered", "cited_gold_page": gold_hit(question, data)}


def pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.0f}% ({part}/{whole})" if whole else "–"


def percentile(values: list[float], q: float) -> str:
    if not values:
        return "–"
    ordered = sorted(values)
    return f"{ordered[min(len(ordered) - 1, int(q * len(ordered)))]:.1f} s"


def report(rows: list[dict[str, Any]], url: str) -> str:
    lines = [
        f"# Live benchmark ({date.today().isoformat()})",
        "",
        f"Questions sent to `{url}` one at a time, as a visitor would. Times are end to end",
        "(network, tunnel, search, answer writing, checks). Answers come from Gemini (free plan).",
        "",
        "| Language | Answered (covered questions) | Cited a correct page | "
        "Refused when not covered | Busy | Median | p90 |",
        "|---|---|---|---|---|---|---|",
    ]
    groups = [*GROUP_NAMES, "all"]
    for group in groups:
        sub = rows if group == "all" else [r for r in rows if r["group"] == group]
        if not sub:
            continue
        covered = [r for r in sub if r["answerable"]]
        answered = [r for r in covered if r["outcome"] == "answered"]
        hits = [r for r in answered if r.get("cited_gold_page")]
        uncovered = [r for r in sub if not r["answerable"]]
        refused = [r for r in uncovered if r["outcome"] == "correct_refusal"]
        busy = [r for r in sub if r["outcome"] == "busy"]
        times = [r["seconds"] for r in sub if r["outcome"] not in ("error", "busy")]
        name = "**All**" if group == "all" else GROUP_NAMES[group]
        lines.append(
            f"| {name} | {pct(len(answered), len(covered))} | {pct(len(hits), len(answered))} | "
            f"{pct(len(refused), len(uncovered))} | {len(busy)} | "
            f"{percentile(times, 0.5)} | {percentile(times, 0.9)} |"
        )
    misses = [r for r in rows if r["outcome"] in ("missed", "answered_uncovered", "error")]
    if misses:
        lines += ["", "## To look at", ""]
        for r in misses:
            extra = r.get("reason") or r.get("detail") or ""
            lines.append(
                f"- `{r['id']}` ({r['group']}) **{r['outcome']}** {extra}: {r['question']}"
            )
    lines += [
        "",
        "Raw replies: `data/eval/live_benchmark.json`. Questions: `data/eval/questions.jsonl`",
        "(the reference answers are drafts; correctness of wording is graded separately).",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--url", default="https://pakkam-alpha.vercel.app")
    parser.add_argument("--per-group", type=int, default=None, help="questions per language")
    parser.add_argument("--pause", type=float, default=7.0, help="seconds between questions")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="keep earlier results and ask only questions not yet answered (or busy / failed)",
    )
    args = parser.parse_args()

    questions = [json.loads(line) for line in QUESTIONS.read_text(encoding="utf-8").splitlines()]
    chosen = pick(questions, args.per_group)
    rows: list[dict[str, Any]] = []
    raw: dict[str, Any] = {}
    if args.resume and RAW_OUT.is_file():
        earlier = json.loads(RAW_OUT.read_text(encoding="utf-8"))
        rows = [r for r in earlier["rows"] if r["outcome"] not in ("busy", "error")]
        raw = {r["id"]: earlier["replies"].get(r["id"]) for r in rows}
        done = {r["id"] for r in rows}
        chosen = [q for q in chosen if q["id"] not in done]
        print(f"resuming: {len(done)} kept, {len(chosen)} to ask")
    failures_in_a_row = 0
    for n, question in enumerate(chosen, start=1):
        data, seconds, error = ask(args.url, question["question"], args.timeout)
        row = {
            "id": question["id"],
            "group": question["group"],
            "question": question["question"],
            "answerable": question["answerable"],
            "seconds": round(seconds, 2),
            **grade(question, data, error),
        }
        rows.append(row)
        raw[question["id"]] = data
        print(f"{n:3}/{len(chosen)} {row['group']:7} {row['outcome']:18} {seconds:5.1f}s")
        # Saved after every question, so a stop (budget, network) loses nothing.
        RAW_OUT.write_text(
            json.dumps({"url": args.url, "rows": rows, "replies": raw}, ensure_ascii=False),
            encoding="utf-8",
        )
        failures_in_a_row = failures_in_a_row + 1 if row["outcome"] in ("busy", "error") else 0
        if failures_in_a_row >= 4:
            print("4 busy/failed replies in a row (daily budget?): stopping; rerun with --resume")
            break
        if n < len(chosen):
            time.sleep(args.pause)

    by_outcome: dict[str, int] = defaultdict(int)
    for row in rows:
        by_outcome[row["outcome"]] += 1
    RAW_OUT.write_text(
        json.dumps({"url": args.url, "rows": rows, "replies": raw}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    REPORT_OUT.write_text(report(rows, args.url), encoding="utf-8")
    print(dict(by_outcome))
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")
    times = [r["seconds"] for r in rows if r["outcome"] not in ("error", "busy")]
    if times:
        print(f"median {statistics.median(times):.1f} s")


if __name__ == "__main__":
    main()
