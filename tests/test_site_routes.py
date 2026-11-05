"""Every server path the web page calls must exist in the backend and be forwarded by the
start script's Vercel rewrites, or the feature silently fails on the live site."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def called_paths() -> set[str]:
    app = (ROOT / "web/js/app.js").read_text(encoding="utf-8")
    called = set(re.findall(r"\b(?:api|postJson)\(\s*['`](/[a-z\-/]+)", app))  # api('/ask', ...)
    called |= set(re.findall(r"`\$\{API_BASE\}(/[a-z\-/]+)", app))  # `${API_BASE}/page...`
    called |= set(re.findall(r"`(/[a-z\-/]+)\?", app))  # `/page?doc=...`
    return called


def backend_routes() -> set[str]:
    main = (ROOT / "src/schemebot/api/main.py").read_text(encoding="utf-8")
    return set(re.findall(r'@app\.(?:get|post)\("(/[^"]*)"', main))


def test_the_page_calls_the_real_backend() -> None:
    called = called_paths()
    expected = {"/ask", "/ask/sources", "/transcribe", "/speak", "/page", "/sources"}
    expected |= {"/check-forward", "/checklist", "/feedback", "/officer-request", "/scheme-facts"}
    assert expected <= called, f"not called: {sorted(expected - called)}"
    missing = sorted(called - backend_routes())
    assert not missing, f"the page calls paths the backend does not have: {missing}"


def test_every_path_the_page_calls_is_routed_to_the_laptop() -> None:
    script = (ROOT / "scripts/start_pakkam.ps1").read_text(encoding="utf-8")
    line = next(row for row in script.splitlines() if row.startswith("$paths ="))
    routed = set(re.findall(r'"(/[a-z\-/]+)"', line))
    called = called_paths()
    assert called <= routed, f"not routed: {sorted(called - routed)}"


def test_the_recorder_loads_before_the_app() -> None:
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    assert html.index("js/recorder.js") < html.index("js/app.js")


def test_small_talk_module_is_imported() -> None:
    app = (ROOT / "web/js/app.js").read_text(encoding="utf-8")
    assert "from './talk.js'" in app
