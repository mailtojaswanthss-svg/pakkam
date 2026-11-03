"""Pack Pakkam for a Google Cloud server into one zip file (run on the laptop).

    uv run --extra ingest --extra index --extra generate --extra gemini --extra api \\
        python deploy/gcp/bundle.py

Writes pakkam-gcp.zip in the project folder: the code, the web pages, the search index, the
official PDFs, the fact cards, the Docker files, and pakkam.env with this laptop's SCHEMEBOT_*
settings, API keys included. The zip holds your keys: upload it only to your own Google Cloud
Shell, never share or commit it (it is in .gitignore). The Hugging Face token is left out.
Then follow deploy/gcp/README.md.
"""

import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "pakkam-gcp.zip"

spec = importlib.util.spec_from_file_location("push", ROOT / "deploy" / "hf-space" / "push.py")
assert spec and spec.loader
push = importlib.util.module_from_spec(spec)
spec.loader.exec_module(push)

SERVER_FILES = ["compose.yaml", "Caddyfile", "vm-setup.sh", "deploy.sh"]


def env_file(settings: dict[str, str]) -> str:
    """Docker env-file lines. Values are written as is (Docker does not unquote them)."""
    bad = [k for k, v in settings.items() if "\n" in v]
    if bad:
        sys.exit(f"Settings with line breaks cannot go in an env file: {', '.join(bad)}")
    return "".join(f"{k}={v}\n" for k, v in sorted(settings.items()))


def build(env_path: Path, out: Path) -> tuple[int, list[str]]:
    settings = push.read_env(env_path)
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp) / "pakkam"
        folder.mkdir()
        push.assemble(folder, settings)
        # The Space card is replaced; the image build still needs a README (pyproject's readme).
        (folder / "README.md").write_text("# Pakkam (Google Cloud server)\n", encoding="utf-8")
        for name in SERVER_FILES + ["Dockerfile"]:
            # Unix line endings: a Windows checkout may have \r\n, which breaks bash on Linux.
            source = folder / name if name == "Dockerfile" else HERE / name
            text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
            (folder / name).write_text(text, encoding="utf-8", newline="\n")
        (folder / "pakkam.env").write_text(env_file(settings), encoding="utf-8", newline="\n")
        archive = shutil.make_archive(str(out.with_suffix("")), "zip", tmp, "pakkam")
    return Path(archive).stat().st_size, sorted(settings)


def main() -> int:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        sys.exit("No .env in the project folder.")
    size, names = build(env_path, OUT)
    keys = [n for n in names if any(w in n for w in push.SECRET_WORDS)]
    print(f"Wrote {OUT.name} ({size / 1e6:.0f} MB) with {len(names)} settings.")
    print(f"Keys inside (values not shown): {', '.join(keys) or 'none'}")
    if not any("GEMINI_API_KEY" in k or "ANTHROPIC_API_KEY" in k for k in keys):
        print("Warning: no LLM API key in .env; the server will refuse every LLM question.")
    print("Keep this file private. Next: upload it in Google Cloud Shell (deploy/gcp/README.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
