"""Check every Pakkam feature through the deployed website, end to end.

    python scripts/live_feature_check.py                       # the live site
    python scripts/live_feature_check.py --url http://localhost:8000

Each check prints PASS / FAIL with a short reason and the time taken. Standard library only.
It leaves one officer request marked "[TEST]" in the help-desk log (it says so).
"""

import argparse
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import wave
from collections.abc import Callable
from typing import Any

RESULTS: list[tuple[str, bool, str, float]] = []


def call(
    base: str,
    path: str,
    body: object | None = None,
    form: tuple[bytes, str] | None = None,
    timeout: float = 120,
) -> tuple[int, bytes, str]:
    url = base.rstrip("/") + path
    headers: dict[str, str] = {}
    data: bytes | None = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if form is not None:
        boundary = uuid.uuid4().hex
        audio, language = form
        parts = [
            f'--{boundary}\r\nContent-Disposition: form-data; name="language"\r\n\r\n{language}\r\n'.encode(),
            f'--{boundary}\r\nContent-Disposition: form-data; name="audio"; filename="q.wav"\r\n'
            "Content-Type: audio/wav\r\n\r\n".encode()
            + audio
            + b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
        data = b"".join(parts)
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read(), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as error:
        return error.code, error.read(), error.headers.get("Content-Type", "")


def clean_wav(raw: bytes) -> bytes:
    """Streamed WAV from Timbre carries placeholder sizes in its header: rebuild it from the
    format chunk and the bytes after "data", so the clip can be sent back as a file."""
    fmt = raw.index(b"fmt ") + 8
    channels = int.from_bytes(raw[fmt + 2 : fmt + 4], "little")
    rate = int.from_bytes(raw[fmt + 4 : fmt + 8], "little")
    width = int.from_bytes(raw[fmt + 14 : fmt + 16], "little") // 8
    frames = raw[raw.index(b"data") + 8 :]
    out = io.BytesIO()
    with wave.open(out, "wb") as clip:
        clip.setnchannels(channels)
        clip.setsampwidth(width)
        clip.setframerate(rate)
        clip.writeframes(frames[: len(frames) - len(frames) % (channels * width)])
    return out.getvalue()


def check(name: str, fn: Callable[[], str]) -> None:
    started = time.perf_counter()
    try:
        detail = fn()
        ok = True
    except AssertionError as error:
        detail, ok = str(error) or "assertion failed", False
    except Exception as error:  # noqa: BLE001 - report any failure, keep checking the rest
        detail, ok = f"{type(error).__name__}: {error}", False
    seconds = time.perf_counter() - started
    RESULTS.append((name, ok, detail, seconds))
    print(f"{'PASS' if ok else 'FAIL'}  {name:<34} {seconds:5.1f}s  {detail}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--url", default="https://pakkam-alpha.vercel.app")
    base = parser.parse_args().url
    state: dict[str, Any] = {}

    def ask(question: str) -> dict[str, Any]:
        status, raw, _ = call(base, "/ask", {"question": question})
        assert status == 200, f"/ask HTTP {status}"
        return json.loads(raw)

    def answer_with_page() -> str:
        data = ask("What is the income limit for Magalir Urimai Thogai?")
        assert not data["refused"], f"refused: {data.get('refusal_reason')}"
        c = data["citations"][0]
        state["citation"] = c
        signed = f", checked by {c['checked_by']}" if c.get("checked_by") else ""
        return f"{data['path']}: cites {c['document']} p.{c['page_start']}{signed}"

    def page_image() -> str:
        c = state["citation"]
        query = urllib.parse.urlencode(
            {"doc": c["doc_id"], "p": c["page_start"], "mark": c["excerpt"][:200]}
        )
        status, raw, kind = call(base, f"/page?{query}")
        assert status == 200 and raw.startswith(b"\x89PNG"), f"HTTP {status} {kind}"
        return f"PNG {len(raw) // 1024} KB"

    def tanglish() -> str:
        data = ask("magalir urimai ku income limit evlo")
        assert not data["refused"], (
            f"refused: {data.get('refusal_reason')} {data.get('rejected_reasons')}"
        )
        return data["sentences"][0]["text"][:70]

    def refusal() -> str:
        data = ask("What is the interest rate on Sukanya Samriddhi Yojana deposits?")
        assert data["refused"], "answered a question the documents do not cover"
        return f"refused ({data['refusal_reason']})"

    def what_can_i_get() -> str:
        data = ask("Which schemes are there for women?")
        assert data["path"] == "discovery", f"path {data['path']}"
        facts = [f for f in data.get("scheme_facts", []) if f.get("amount") or f.get("who")]
        total = sum(f.get("yearly_amount") or 0 for f in facts)
        assert facts, "no signed facts (are the cards signed?)"
        return f"{len(facts)} schemes with signed facts, up to Rs.{total:,} a year"

    def checklist() -> str:
        status, raw, _ = call(base, "/checklist?scheme=Pradhan%20Mantri%20Ujjwala%20Yojana&lang=en")
        assert status == 200, f"HTTP {status}"
        items = json.loads(raw)["items"]
        assert items, "no items"
        return f"{len(items)} item(s), first cites p.{items[0]['citation']['page_start']}"

    def rumour() -> str:
        message = "Magalir Urimai increased to Rs.2,000 a month! Register at bit.ly/kmut2000 today only and share OTP."
        status, raw, _ = call(base, "/check-forward", {"message": message}, timeout=180)
        assert status == 200, f"HTTP {status}"
        data = json.loads(raw)
        assert "otp" in data["scam_signs"] and "unofficial_link" in data["scam_signs"], data[
            "scam_signs"
        ]
        return f"overall={data['overall']}, verdicts={[c['verdict'] for c in data['claims']]}, signs={data['scam_signs']}"

    def officer() -> str:
        status, raw, _ = call(
            base,
            "/officer-request",
            {"question": "[TEST] live feature check, please ignore", "language": "en"},
        )
        assert status == 200, f"HTTP {status}"
        return json.loads(raw)["ticket"] + " (test ticket)"

    def dashboard() -> str:
        status, raw, _ = call(base, "/dashboard/stats")
        assert status == 200, f"HTTP {status}"
        s = json.loads(raw)
        return f"{s['questions']} questions, {s['forwards']['checked']} forwards, {s['officer_requests']['open']} open requests"

    def speak() -> str:
        status, raw, kind = call(
            base, "/speak", {"text": "மகளிர் உரிமைத் தொகை எவ்வளவு?", "language": "ta"}
        )
        assert status == 200 and raw[:4] == b"RIFF", f"HTTP {status} {kind}"
        state["audio"] = clean_wav(raw)
        with wave.open(io.BytesIO(state["audio"])) as clip:
            seconds = clip.getnframes() / clip.getframerate()
        return f"Timbre Tamil audio {seconds:.1f}s"

    def transcribe() -> str:
        status, raw, _ = call(base, "/transcribe", form=(state["audio"], "ta"))
        assert status == 200, f"HTTP {status}: {raw[:120]!r}"
        heard = json.loads(raw)["transcript"]
        assert "மகளிர்" in heard or "உரிமை" in heard, f"heard: {heard}"
        return f"Prisma heard: {heard}"

    check("Answer with an official page", answer_with_page)
    check("Proof card page image", page_image)
    check("Tanglish answer", tanglish)
    check("Honest refusal", refusal)
    check("What can I get (signed facts)", what_can_i_get)
    check("Visit checklist", checklist)
    check("Rumour shield + scam signs", rumour)
    check("Ask an officer", officer)
    check("Pakkam Desk dashboard", dashboard)
    check("Timbre speech (Tamil)", speak)
    if "audio" in state:
        check("Prisma v3 hears it back", transcribe)

    passed = sum(ok for _, ok, _, _ in RESULTS)
    print(f"\n{passed}/{len(RESULTS)} checks passed")


if __name__ == "__main__":
    main()
