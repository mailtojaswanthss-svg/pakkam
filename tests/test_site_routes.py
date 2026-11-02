"""Every server path the web pages use must be forwarded by the start script's Vercel rewrites,
or the feature silently 404s on the live site."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_every_path_the_pages_call_is_routed_to_the_laptop() -> None:
    pages = (ROOT / "web/assets/chat.js").read_text(encoding="utf-8") + (
        ROOT / "web/dashboard/index.html"
    ).read_text(encoding="utf-8")
    called = set(re.findall(r"fetch\(\s*[`'\"](/[a-z\-/]+)", pages))
    called |= set(re.findall(r"src = `(/[a-z\-/]+)\?", pages))  # the page image
    script = (ROOT / "scripts/start_pakkam.ps1").read_text(encoding="utf-8")
    line = next(row for row in script.splitlines() if row.startswith("$paths ="))
    routed = set(re.findall(r'"(/[a-z\-/]+)"', line))
    assert "/page" in called
    assert called <= routed, f"not routed: {sorted(called - routed)}"
