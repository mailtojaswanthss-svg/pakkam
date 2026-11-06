"""Builds the three demo cuts (full, 90 s, 60 s) from the recording and the Timbre narration.

    python scripts/video/build_video.py WORK_DIR OUT_DIR

WORK_DIR holds main.webm + marks.json (record_demo.js), hook.webm / end.webm + *.lead.txt
(record_cards.js) and the WAVs + durations.json (make_voice.py, plus tamil_answer.wav).
Writes OUT_DIR/pakkam-{full,90s,60s}.mp4 (no subtitles; the narrator explains each scene)."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
TMP = WORK / "build"
TMP.mkdir(exist_ok=True)
SCRIPT = {s["id"]: s for s in json.loads((HERE / "script.json").read_text(encoding="utf-8"))["scenes"]}
M = json.loads((WORK / "marks.json").read_text())
D = json.loads((WORK / "durations.json").read_text())
LEAD = {n: float((WORK / f"{n}.lead.txt").read_text()) for n in ("hook", "end")}
SRC = {"main": WORK / "main.webm", "hook": WORK / "hook.webm", "end": WORK / "end.webm"}
W, H, FPS = 1920, 1080, 30


def wav_len(name: str) -> float:
    if name in D:
        return D[name]
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(WORK / f"{name}.wav")],
                         capture_output=True, text=True, check=True)
    D[name] = float(out.stdout)
    return D[name]


def scene(sid: str, clips: list, audio: list, tail: float = 0.7) -> dict:
    """clips: (source, start, end, speed); audio: (wav name, at seconds)."""
    return {"id": sid, "clips": clips, "audio": audio, "tail": tail}


def build_scenes() -> dict:
    s = {}
    hook0, end0 = LEAD["hook"], LEAD["end"]
    s["hook"] = scene("hook", [("hook", hook0, hook0 + 6.6, 1)], [("s01_hook", 0.4)])

    a, v, sg, e = M["s02"], M["s02_verdict"], M["s02_signs"], M["s02_end"]
    s["shield"] = scene("shield", [("main", a, a + 4.6, 1), ("main", v - 0.5, e, 1)], [("s02_shield", 0.3)])
    s["shield_short"] = scene("shield_short", [("main", a + 0.6, a + 3.8, 1), ("main", v - 0.4, v + 1.6, 1), ("main", sg, sg + 2.6, 1)],
                              [("s02_shield_short", 0.3)])

    s["home"] = scene("home", [("main", M["s03"], M["s03_end"], 1)], [("s03_home", 0.3)])

    a, mic, ans = M["s04"], M["s04_mic"], M["s04_answer"]
    len1 = mic + 3.6 - a
    q_at = mic + 0.55 - a
    b_at = len1 + 1.0
    ta_at = b_at + D["s04_voice_b"] + 0.3
    s["voice"] = scene("voice", [("main", a, mic + 3.6, 1), ("main", ans - 0.8, M["s04_end"], 1)],
                       [("s04_voice", 0.2), ("tamil_question", q_at), ("s04_voice_b", b_at), ("tamil_answer", ta_at)])
    s["voice_short"] = scene("voice_short", [("main", a, mic + 3.6, 1), ("main", ans - 0.8, ans + D["s04_voice_b"] + 1.6, 1)],
                             [("s04_voice", 0.2), ("tamil_question", q_at), ("s04_voice_b", b_at)])

    s["proof"] = scene("proof", [("main", M["s05"], M["s05_end"] - 0.3, 1)], [("s05_proof", 0.5)])
    s["schemes"] = scene("schemes", [("main", M["s06"], M["s06_end"], 1)], [("s06_schemes", 0.5)])

    a, sent, ans = M["s07"], M["refusal_sent"], M["refusal_answer"]
    len1 = (sent + 0.2 - a) / 2
    s["refusal"] = scene("refusal", [("main", a, sent + 0.2, 2), ("main", ans - 0.5, M["s07_end"], 1)], [("s07_refusal", len1 + 0.8)])
    s["refusal_short"] = scene("refusal_short", [("main", a, sent + 0.2, 2), ("main", ans - 0.5, ans + D["s07_refusal_short"] + 1.2, 1)],
                               [("s07_refusal_short", len1 + 0.8)])

    s["how"] = scene("how", [("main", M["s08"], M["s08_end"], 1)], [("s08_how", 0.4)])
    s["numbers"] = scene("numbers", [("main", M["s09"], M["s09_end"], 1)], [("s09_numbers", 0.5)])
    s["story"] = scene("story", [("main", M["s09b"], M["s09b_end"], 1)], [("s09b_story", 0.4)])
    s["end"] = scene("end", [("end", end0, end0 + 6.0, 1)], [("s10_end", 1.0)], tail=0.3)
    return s


CUTS = {
    "full": ["hook", "shield", "home", "voice", "proof", "schemes", "refusal", "how", "numbers", "story", "end"],
    "90s": ["hook", "shield_short", "home", "voice", "proof", "refusal_short", "numbers", "story", "end"],
    "60s": ["hook", "shield_short", "voice_short", "proof", "refusal_short", "end"],
}


def render_scene(sc: dict) -> tuple[Path, float]:
    """One scene as an MP4 with its own audio; returns the file and its length."""
    vlen = sum((b - a) / sp for _, a, b, sp in sc["clips"])
    aend = max(at + wav_len(n) for n, at in sc["audio"])
    length = max(vlen, aend + sc["tail"])
    out = TMP / f"{sc['id']}.mp4"
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    for src in sorted({c[0] for c in sc["clips"]}):
        cmd += ["-i", str(SRC[src])]
    order = sorted({c[0] for c in sc["clips"]})
    for n, _ in sc["audio"]:
        cmd += ["-i", str(WORK / f"{n}.wav")]
    parts, labels = [], []
    for i, (src, a, b, sp) in enumerate(sc["clips"]):
        k = order.index(src)
        parts.append(f"[{k}:v]trim=start={a:.3f}:end={b:.3f},setpts=(PTS-STARTPTS)/{sp},fps={FPS},scale={W}:{H}:flags=lanczos,setsar=1[v{i}]")
        labels.append(f"[v{i}]")
    vf = ";".join(parts) + f";{''.join(labels)}concat=n={len(labels)}:v=1:a=0[vc];[vc]tpad=stop_mode=clone:stop_duration={max(0, length - vlen) + 0.1:.3f},trim=duration={length:.3f}[v]"
    aparts, alabels = [], []
    for j, (n, at) in enumerate(sc["audio"]):
        idx = len(order) + j
        vol = 1.0 if n.startswith("s") else 0.95
        aparts.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={vol},adelay={int(at * 1000)}|{int(at * 1000)}[a{j}]")
        alabels.append(f"[a{j}]")
    af = ";".join(aparts) + f";{''.join(alabels)}amix=inputs={len(alabels)}:normalize=0,apad,atrim=duration={length:.3f}[a]"
    cmd += ["-filter_complex", vf + ";" + af, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)]
    subprocess.run(cmd, check=True)
    return out, length


def build_cut(name: str, scenes: dict) -> None:
    files, t = [], 0.0
    for sid in CUTS[name]:
        f, length = render_scene(scenes[sid])
        files.append(f)
        t += length
    lst = TMP / f"{name}.txt"
    lst.write_text("".join(f"file '{f}'\n" for f in files))
    joined = TMP / f"{name}_joined.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], check=True)
    final = OUT / f"pakkam-{name}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(joined), "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                    "-movflags", "+faststart", str(final)], check=True)
    print(name, f"{t:.1f}s", final)


if __name__ == "__main__":
    sc = build_scenes()
    for cut in (sys.argv[3:] or CUTS):
        build_cut(cut, sc)
