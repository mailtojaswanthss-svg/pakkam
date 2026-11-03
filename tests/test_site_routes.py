"""Every server path the web pages use must be forwarded by the start script's Vercel rewrites,
or the feature silently 404s on the live site."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def called_paths() -> set[str]:
    pages = (ROOT / "web/assets/chat.js").read_text(encoding="utf-8") + (
        ROOT / "web/dashboard/index.html"
    ).read_text(encoding="utf-8")
    called = set(re.findall(r"fetch\(\s*[`'\"](/[a-z\-/]+)", pages))
    called |= set(re.findall(r"(?:src|Path) = `(/[a-z\-/]+)\?", pages))  # the page image
    return called


def test_every_path_the_pages_call_is_routed_to_the_laptop() -> None:
    called = called_paths()
    script = (ROOT / "scripts/start_pakkam.ps1").read_text(encoding="utf-8")
    line = next(row for row in script.splitlines() if row.startswith("$paths ="))
    routed = set(re.findall(r'"(/[a-z\-/]+)"', line))
    assert "/page" in called
    assert called <= routed, f"not routed: {sorted(called - routed)}"


def test_every_path_falls_back_to_the_backup_server() -> None:
    backup = (ROOT / "web/assets/backup.js").read_text(encoding="utf-8")
    pattern = re.search(r"const API = /(.+)/;", backup)
    assert pattern
    api = re.compile(pattern.group(1).replace("\\/", "/"))
    missing = sorted(p for p in called_paths() if not api.match(p))
    assert not missing, f"no backup for: {missing}"
    for page in ("web/chat/index.html", "web/dashboard/index.html"):
        html = (ROOT / page).read_text(encoding="utf-8")
        assert html.index("backup.js") < html.index("<script", html.index("backup.js") + 1)
