"""Publish Pakkam to a free Hugging Face Space (Docker, CPU).

    uv run hf auth login                                   # once, with a "write" token
    uv run python deploy/hf-space/push.py --dry-run        # list what would be uploaded
    uv run python deploy/hf-space/push.py                  # create/update the Space

Then add the API key as a secret in the Space's settings (never uploaded from here). The
Space builds the image itself (about 20 minutes the first time) and serves the site at
https://<user>-<space>.hf.space.
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

# (source, destination in the Space). Only what the image needs: no .env, raw PDFs or logs.
FILES = [
    (HERE / "Dockerfile", "Dockerfile"),
    (HERE / "README.md", "README.md"),
    (ROOT / "pyproject.toml", "pyproject.toml"),
    (ROOT / "uv.lock", "uv.lock"),
    (ROOT / "src", "src"),
    (ROOT / "web", "web"),
    (ROOT / "data" / "index", "data/index"),
    (ROOT / "data" / "sources.json", "data/sources.json"),
    (ROOT / "data" / "contacts.json", "data/contacts.json"),
]
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".lock")


def assemble(target: Path) -> list[tuple[str, int]]:
    for source, dest in FILES:
        if not source.exists():
            sys.exit(f"Missing {source}. Build the index first (uv run python -m schemebot.index).")
        out = target / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, out, ignore=IGNORE)
        else:
            shutil.copy2(source, out)
    return sorted(
        (str(p.relative_to(target)).replace("\\", "/"), p.stat().st_size)
        for p in target.rglob("*")
        if p.is_file()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish Pakkam to a Hugging Face Space.")
    parser.add_argument("--space", default="pakkam", help="Space name (default: pakkam)")
    parser.add_argument("--provider", default="gemini", choices=["gemini", "claude"])
    parser.add_argument("--dry-run", action="store_true", help="only list the files")
    # The free Gemini tier: these answered when Flash was overloaded or out of daily quota.
    parser.add_argument("--gemini-model", default="gemini-3.5-flash-lite")
    parser.add_argument("--gemini-verifier", default="gemini-3.1-flash-lite")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        files = assemble(Path(tmp))
        total = sum(size for _, size in files)
        print(f"{len(files)} files, {total / 1e6:.1f} MB")
        if args.dry_run:
            for name, size in files:
                if not name.startswith(("src/", "web/")):
                    print(f"  {name} ({size:,} bytes)")
            print("  plus src/ and web/")
            return 0

        from huggingface_hub import HfApi

        api = HfApi()
        user = api.whoami()["name"]
        repo_id = f"{user}/{args.space}"
        api.create_repo(repo_id, repo_type="space", space_sdk="docker", exist_ok=True)
        api.add_space_variable(repo_id, "SCHEMEBOT_LLM_PROVIDER", args.provider)
        if args.provider == "gemini":
            api.add_space_variable(repo_id, "SCHEMEBOT_GEMINI_MODEL", args.gemini_model)
            api.add_space_variable(repo_id, "SCHEMEBOT_GEMINI_VERIFIER_MODEL", args.gemini_verifier)
        api.upload_folder(
            repo_id=repo_id,
            repo_type="space",
            folder_path=tmp,
            commit_message="Deploy Pakkam",
            delete_patterns=["src/**", "web/**", "data/**"],
        )

    key = "SCHEMEBOT_GEMINI_API_KEY" if args.provider == "gemini" else "SCHEMEBOT_ANTHROPIC_API_KEY"
    host = f"{user}-{args.space}".lower().replace("_", "-")
    print(f"\nUploaded: https://huggingface.co/spaces/{repo_id}")
    print(f"Next: add the secret {key} in Settings -> Variables and secrets.")
    print(f"Site (once built): https://{host}.hf.space  (chat: /chat/)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
