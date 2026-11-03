"""Publish Pakkam to a free Hugging Face Space (Docker, CPU).

    (put HF_TOKEN=<a "write" token> in .env, or run `hf auth login` once)
    uv run python deploy/hf-space/push.py --dry-run        # list what would be uploaded
    uv run python deploy/hf-space/push.py                  # create/update the Space

Settings come from this laptop's .env: every SCHEMEBOT_* line is copied to the Space, the API
keys as Space *secrets* (encrypted, never in the Space's files) and the rest as variables.
Nothing is printed except setting names. The Space builds the image itself (about 20-30
minutes the first time) and serves the site at https://<user>-<space>.hf.space.
"""

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

# (source, destination in the Space). Only what the image needs: no .env, logs or caches.
FILES = [
    (HERE / "README.md", "README.md"),
    (ROOT / "pyproject.toml", "pyproject.toml"),
    (ROOT / "uv.lock", "uv.lock"),
    (ROOT / "src", "src"),
    (ROOT / "web", "web"),
    (ROOT / "data" / "index", "data/index"),
    (ROOT / "data" / "sources.json", "data/sources.json"),
    (ROOT / "data" / "contacts.json", "data/contacts.json"),
    (ROOT / "data" / "corrections.json", "data/corrections.json"),
    (ROOT / "data" / "fact_cards.json", "data/fact_cards.json"),
    (ROOT / "data" / "scheme_aliases.json", "data/scheme_aliases.json"),
]
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".lock", "vercel.json")

SECRET_WORDS = ("KEY", "TOKEN", "SECRET", "PASSWORD")
# Laptop-only settings: Windows paths and tools the Space does not have.
SKIP = {
    "SCHEMEBOT_DATA_DIR",
    "SCHEMEBOT_LOG_DIR",
    "SCHEMEBOT_TESSERACT_CMD",
    "SCHEMEBOT_TESSDATA_DIR",
    "SCHEMEBOT_OCR_ENGINE",
}
# The free Space is a slower backup (2 CPU cores): rerank 10 search results instead of 20,
# which halves the reranker's time. Same models and refusal threshold as the laptop.
SPACE_OVERRIDES = {"SCHEMEBOT_RETRIEVAL_TOP_K": "10"}
# Baked into the image at build time (Dockerfile ARGs), as well as set at run time.
BUILD_ARGS = {
    "SCHEMEBOT_EMBEDDING_MODEL": "EMBEDDING_MODEL",
    "SCHEMEBOT_RERANKER_MODEL": "RERANKER_MODEL",
    "SCHEMEBOT_EMBEDDING_REVISION": "EMBEDDING_REVISION",
    "SCHEMEBOT_RERANKER_REVISION": "RERANKER_REVISION",
}


def parse_env(path: Path) -> dict[str, str]:
    """Every NAME=value line of a .env file (quotes and comments allowed; empty values dropped)."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip().removeprefix("export ").strip()
        value = value.strip()
        if value[:1] in "\"'" and value[-1:] == value[:1] and len(value) >= 2:
            value = value[1:-1]
        else:
            value = value.split(" #", 1)[0].strip()
        if value:
            values[name] = value
    return values


def is_hf_token(name: str) -> bool:
    """The Hugging Face token that uploads the Space. It is never copied into the Space."""
    upper = name.upper()
    return ("HF" in upper or "HUGGING" in upper) and any(w in upper for w in ("TOKEN", "KEY"))


def read_env(path: Path) -> dict[str, str]:
    """SCHEMEBOT_* settings for the Space, without laptop-only ones or the HF token."""
    return {
        k: v
        for k, v in parse_env(path).items()
        if k.startswith("SCHEMEBOT_") and k not in SKIP and not is_hf_token(k)
    }


def hf_token(path: Path) -> str | None:
    """The Hugging Face token from .env (HF_TOKEN or similar), else None (use `hf auth login`)."""
    found = [v for k, v in parse_env(path).items() if is_hf_token(k)]
    return found[0] if found else None


def split_settings(env: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    """(secrets, variables): anything named like a key or token is a secret."""
    secrets = {k: v for k, v in env.items() if any(w in k for w in SECRET_WORDS)}
    variables = {k: v for k, v in env.items() if k not in secrets} | SPACE_OVERRIDES
    return secrets, variables


def dockerfile(env: dict[str, str]) -> str:
    """The Space Dockerfile with the model names and revisions from .env as ARG defaults."""
    text = (HERE / "Dockerfile").read_text(encoding="utf-8")
    for setting, arg in BUILD_ARGS.items():
        if setting in env:
            text = re.sub(rf"^ARG {arg}=.*$", f"ARG {arg}={env[setting]}", text, flags=re.M)
    return text


def pdf_files() -> list[tuple[Path, str]]:
    """The official PDFs the proof card renders pages from (one per entry in sources.json)."""
    sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    return [(ROOT / "data" / "raw" / s["file"], f"data/raw/{s['file']}") for s in sources]


def assemble(target: Path, env: dict[str, str]) -> list[tuple[str, int]]:
    missing = [str(s) for s, _ in FILES + pdf_files() if not s.exists()]
    if missing:
        listing = "\n  ".join(missing)
        sys.exit(f"Missing (build the index and download the PDFs first):\n  {listing}")
    for source, dest in FILES + pdf_files():
        out = target / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, out, ignore=IGNORE)
        else:
            shutil.copy2(source, out)
    (target / "Dockerfile").write_text(dockerfile(env), encoding="utf-8")
    return sorted(
        (str(p.relative_to(target)).replace("\\", "/"), p.stat().st_size)
        for p in target.rglob("*")
        if p.is_file()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish Pakkam to a Hugging Face Space.")
    parser.add_argument("--space", default="pakkam", help="Space name (default: pakkam)")
    parser.add_argument("--env", type=Path, default=ROOT / ".env", help="settings file")
    parser.add_argument("--dry-run", action="store_true", help="only list files and settings")
    parser.add_argument("--code-only", action="store_true", help="skip changing settings")
    args = parser.parse_args()

    env = read_env(args.env)
    secrets, variables = split_settings(env)
    if not any("GEMINI_API_KEY" in k or "ANTHROPIC_API_KEY" in k for k in secrets):
        print("Warning: no LLM API key in .env; the Space will refuse every LLM question.")

    with tempfile.TemporaryDirectory() as tmp:
        files = assemble(Path(tmp), env)
        total = sum(size for _, size in files)
        print(f"{len(files)} files, {total / 1e6:.1f} MB")
        print(f"secrets ({len(secrets)}): {', '.join(sorted(secrets)) or 'none'}")
        print(f"variables ({len(variables)}): {', '.join(sorted(variables)) or 'none'}")
        source = "found in .env" if hf_token(args.env) else "not in .env: run `hf auth login`"
        print(f"Hugging Face token: {source} (used to upload, never copied to the Space)")
        if args.dry_run:
            for name, size in files:
                if not name.startswith(("src/", "web/")):
                    print(f"  {name} ({size:,} bytes)")
            print("  plus src/ and web/")
            return 0

        from huggingface_hub import HfApi

        token = hf_token(args.env)
        api = HfApi(token=token)  # None: the token saved by `hf auth login`
        user = api.whoami()["name"]
        repo_id = f"{user}/{args.space}"
        api.create_repo(repo_id, repo_type="space", space_sdk="docker", exist_ok=True)
        if not args.code_only:
            for name, value in secrets.items():
                api.add_space_secret(repo_id, name, value)
            for name, value in variables.items():
                api.add_space_variable(repo_id, name, value)
        api.upload_folder(
            repo_id=repo_id,
            repo_type="space",
            folder_path=tmp,
            commit_message="Deploy Pakkam",
            delete_patterns=["src/**", "web/**", "data/**"],
        )

    host = f"{user}-{args.space}".lower().replace("_", "-").replace(".", "-")
    print(f"\nUploaded: https://huggingface.co/spaces/{repo_id}")
    print("The Space is building now (watch the Logs tab; about 20-30 minutes the first time).")
    print(f"Site (once built): https://{host}.hf.space  (chat: /chat/)")
    print("Tell Claude when it shows 'Running'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
