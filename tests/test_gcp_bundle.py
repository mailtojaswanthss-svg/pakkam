"""deploy/gcp/bundle.py: the zip carries the settings and Unix-format server scripts."""

import importlib.util
import json
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bundle", ROOT / "deploy" / "gcp" / "bundle.py")
assert spec and spec.loader
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


def test_env_file_writes_values_unquoted_and_sorted() -> None:
    text = bundle.env_file({"SCHEMEBOT_B": "two words", "SCHEMEBOT_A": "1"})
    assert text == "SCHEMEBOT_A=1\nSCHEMEBOT_B=two words\n"


def test_bundle_has_settings_and_unix_scripts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A fake project: index, PDFs and data files, with Windows line endings in the scripts.
    root = tmp_path / "project"
    for name in ["sources.json", "contacts.json", "corrections.json", "fact_cards.json"]:
        (root / "data").mkdir(parents=True, exist_ok=True)
        (root / "data" / name).write_text("[]", encoding="utf-8")
    (root / "data" / "scheme_aliases.json").write_text("{}", encoding="utf-8")
    sources = [{"file": "a.pdf"}]
    (root / "data" / "sources.json").write_text(json.dumps(sources), encoding="utf-8")
    (root / "data" / "raw").mkdir()
    (root / "data" / "raw" / "a.pdf").write_bytes(b"%PDF")
    (root / "data" / "index").mkdir()
    (root / "data" / "index" / "meta.json").write_text("{}", encoding="utf-8")
    for name in ["pyproject.toml", "uv.lock"]:
        (root / name).write_text("x", encoding="utf-8")
    for name in ["src", "web"]:
        (root / name).mkdir()
        (root / name / "f.txt").write_text("x", encoding="utf-8")
    here = tmp_path / "gcp"
    here.mkdir()
    for name in bundle.SERVER_FILES:
        (here / name).write_bytes(b"line one\r\nline two\r\n")
    monkeypatch.setattr(bundle.push, "ROOT", root)
    monkeypatch.setattr(
        bundle.push,
        "FILES",
        [(root / d, d) for d in ["src", "web"]] + [(root / "data" / "index", "data/index")],
    )
    monkeypatch.setattr(bundle, "HERE", here)

    env = tmp_path / ".env"
    env.write_text(
        "SCHEMEBOT_GEMINI_API_KEY=k\nHF_TOKEN=hf_x\nSCHEMEBOT_TESSDATA_DIR=C:\\t\n",
        encoding="utf-8",
    )
    out = tmp_path / "pakkam-gcp.zip"
    size, names = bundle.build(env, out)

    assert size > 0 and names == ["SCHEMEBOT_GEMINI_API_KEY"]
    with zipfile.ZipFile(out) as z:
        files = set(z.namelist())
        assert {"pakkam/pakkam.env", "pakkam/Dockerfile", "pakkam/README.md"} <= files
        assert "pakkam/data/raw/a.pdf" in files
        assert z.read("pakkam/pakkam.env") == b"SCHEMEBOT_GEMINI_API_KEY=k\n"
        for name in bundle.SERVER_FILES + ["Dockerfile"]:
            assert b"\r\n" not in z.read(f"pakkam/{name}"), name
