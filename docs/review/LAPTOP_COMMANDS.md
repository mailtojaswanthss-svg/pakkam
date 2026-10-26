# Laptop commands (updated 26 Oct 2026, 13:30 UTC)

Run these in the Pakkam folder. They make no paid calls: no LLM key and no Gnani.

## 0. Merge PR #8 first

PR #8 contains the results script, the OCR block list, the cache and the model pinning. Merge it
on GitHub once CI is green.

## 1. Get main, clean

```
git status                      # must say "nothing to commit"; if not: git stash
git checkout main
git pull origin main
git log --oneline -1            # this commit must be on GitHub
```

## 2. Install and test (same lockfile as CI)

```
uv sync --frozen --extra ingest --extra index --extra store --extra generate --extra gemini --extra api --extra eval
uv run --frozen ruff check .
uv run --frozen mypy src
uv run --frozen pytest -q       # expect about 405 passed
```

If `uv sync --frozen` says the lockfile is out of date, stop and tell me. Do not run `uv lock`.

## 3. Pin the versions your index was built with (one time)

```
ls ~/.cache/huggingface/hub/models--BAAI--bge-m3/snapshots/
ls ~/.cache/huggingface/hub/models--BAAI--bge-reranker-v2-m3/snapshots/
```

On Windows the folder is `%USERPROFILE%\.cache\huggingface\hub\...`. Each command prints one
40-character folder name, which is the commit hash. Put them in your `.env`:

```
SCHEMEBOT_EMBEDDING_REVISION=<bge-m3 hash>
SCHEMEBOT_RERANKER_REVISION=<reranker hash>
```

If a folder lists more than one hash, send me both names and don't guess. For the Docker base
image, if Docker is installed: `docker buildx imagetools inspect python:3.12-slim-trixie` and
send me the "Digest:" line.

## 4. Clean retrieval-only run plus the summary

```
git status --porcelain --untracked-files=no                 # must print nothing
uv run --frozen python -m schemebot.evaluation --retrieval-only
uv run --frozen python -m schemebot.evaluation.summary --split held-out
uv run --frozen python -m schemebot.evaluation.summary --split dev --failures > dev-failures.txt
```

The summary prints the following:
- the run's commit (it must not say "uncommitted changes");
- per language, n (answerable/unanswerable), Recall@1 and @5, and false and correct refusals;
- for full runs, "model-judged faithfulness" with the number of sentences judged.

## 4b. Find the hostel and helpline pages (prints document and page only)

```
uv run --frozen python -m schemebot.ingest.find 14167 4400 "4,20,000"
```

Send me the output. I'll add those pages to `data/corrections.json`, still unconfirmed, so the
wrong numbers are blocked on exactly those pages.

## 5. Commit the result

```
git checkout -b results-rerun-26oct
git add docs/results.md
git commit -m "docs: retrieval-only results from a clean pushed commit"
git push -u origin results-rerun-26oct
```

Send me `dev-failures.txt` (upload it in the thread) and tell me the branch name.

# The improvement loop ("run it again until it's good")

Each round is free and takes one retrieval-only run on your laptop.

1. **You:** steps 1, 4 and 5 above, then send `dev-failures.txt`.
2. **Me:** I group the misses by cause:
   - a wrong gold label;
   - a Tanglish word the gloss doesn't know;
   - an OCR-damaged page;
   - a chunk split in the wrong place;
   - the threshold.
   I fix the causes in code or data, with tests, and push a PR.
3. **You:** merge the PR, then run steps 1 and 4 again. We compare the dev numbers with the
   last round.

Rules that keep the numbers honest:
- Changes are judged **only on dev (q001-q110)**.
- Held-out (q111-q194) is printed for the report, but never used to choose a change.
- If a change helps dev but lowers held-out, we say so in the report and don't hide it.
- The refusal threshold changes only if dev shows a clear gain.
- No LLM or Gnani calls in the loop. A full run (answers and faithfulness) happens only when you
  say yes, because it costs credit.
- Stop after 3 rounds, or when a round fixes fewer than 3 dev questions. Then we write up what
  changed.
