"""Builds the three demo cuts (full, 90 s, 60 s) from the recording and the Timbre narration.

    python scripts/video/build_video.py WORK_DIR OUT_DIR

WORK_DIR holds main.webm + marks.json (record_demo.js), hook.webm / end.webm + *.lead.txt
(record_cards.js) and the WAVs + durations.json (make_voice.py, plus tamil_answer.wav).
Writes OUT_DIR/pakkam-{full,90s,60s}.mp4 and matching .srt files (English subtitles)."""
import json
import re
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


TAMIL_Q_EN = "(Tamil) “How much is the Magalir Urimai amount?”"
TAMIL_A_EN = "(Tamil) “Under Kalaignar Magalir Urimai Thittam, eligible women heads of families get Rs.1,000 a month (Rs.12,000 a year).”"


def scene(sid: str, clips: list, audio: list, subs: list | None = None, labels: list | None = None, tail: float = 0.7) -> dict:
    """clips: (source, start, end, speed); audio: (wav name, at seconds); subs: (text, at, length);
    labels: (text, at, length) shown top-left. Subtitles default to each narration line."""
    return {"id": sid, "clips": clips, "audio": audio, "subs": subs or [], "labels": labels or [], "tail": tail}


def vo_subs(text: str, at: float, length: float) -> list:
    """Split a narration line into sentence-sized subtitles timed by their share of the characters."""
    parts = [p.strip() for p in re.split(r"(?<=[.?!:])\s+", text) if p.strip()]
    merged: list[str] = []
    for p in parts:  # keep very short pieces with their neighbour
        if merged and (len(p) < 28 or len(merged[-1]) < 28) and len(merged[-1]) + len(p) < 95:
            merged[-1] += " " + p
        else:
            merged.append(p)
    total = sum(len(p) for p in merged)
    out, t = [], at
    for p in merged:
        d = length * len(p) / total
        out.append((p, t, d))
        t += d
    return out


def build_scenes() -> dict:
    s = {}
    hook0, end0 = LEAD["hook"], LEAD["end"]
    s["hook"] = scene("hook", [("hook", hook0, hook0 + 6.6, 1)], [("s01_hook", 0.5)])
    s["hook"]["subs"] = vo_subs(SCRIPT["s01_hook"]["sub"], 0.5, D["s01_hook"])

    a = M["s02"]
    v = M["s02_verdict"]
    s["shield"] = scene("shield", [("main", a, a + 5.6, 1), ("main", v - 0.6, v + 2.75, 0.7)], [("s02_shield", 0.4)])
    s["shield"]["subs"] = vo_subs(SCRIPT["s02_shield"]["sub"], 0.4, D["s02_shield"])
    s["shield_short"] = scene("shield_short", [("main", a + 0.9, a + 4.3, 1), ("main", v - 0.4, v + 2.75, 0.8)], [("s02_shield_short", 0.3)])
    s["shield_short"]["subs"] = vo_subs(SCRIPT["s02_shield"]["short_sub"], 0.3, D["s02_shield_short"])

    s["home"] = scene("home", [("main", M["s03"], M["s03_end"], 1)], [("s03_home", 0.4)])
    s["home"]["subs"] = vo_subs(SCRIPT["s03_home"]["sub"], 0.4, D["s03_home"])

    a = M["s04"]
    mic = M["s04_mic"]
    ans = M["s04_answer"]
    len1 = mic + 3.4 - a
    q_at = mic + 0.55 - a
    b_at = len1 + 1.2
    ta_at = b_at + D["s04_voice_b"] + 0.4
    full_tail = ta_at + wav_len("tamil_answer") + 0.8 - len1
    s["voice"] = scene("voice", [("main", a, mic + 3.4, 1), ("main", ans - 1.0, ans - 1.0 + full_tail, 1)],
                       [("s04_voice", 0.3), ("tamil_question", q_at), ("s04_voice_b", b_at), ("tamil_answer", ta_at)])
    s["voice"]["subs"] = (vo_subs(SCRIPT["s04_voice"]["sub"], 0.3, D["s04_voice"]) + [(TAMIL_Q_EN, q_at, 2.6)]
                          + vo_subs(SCRIPT["s04_voice"]["sub_b"], b_at, D["s04_voice_b"]) + [(TAMIL_A_EN, ta_at, wav_len("tamil_answer"))])
    s["voice_short"] = scene("voice_short", [("main", a, mic + 3.4, 1), ("main", ans - 1.0, ans - 1.0 + D["s04_voice_b"] + 2.4, 1)],
                             [("s04_voice", 0.3), ("tamil_question", q_at), ("s04_voice_b", b_at)])
    s["voice_short"]["subs"] = (vo_subs(SCRIPT["s04_voice"]["sub"], 0.3, D["s04_voice"]) + [(TAMIL_Q_EN, q_at, 2.6)]
                                + vo_subs(SCRIPT["s04_voice"]["sub_b"], b_at, D["s04_voice_b"]))

    s["proof"] = scene("proof", [("main", M["s05"], M["s05_end"] - 0.4, 1)], [("s05_proof", 0.6)])
    s["proof"]["subs"] = vo_subs(SCRIPT["s05_proof"]["sub"], 0.6, D["s05_proof"])

    clips, labels, t = [], [], 0.0
    prev = M["s06"]
    for key, label in (("tanglish", "Tanglish"), ("hindi", "Hindi · हिंदी"), ("english", "English")):
        typing = (prev, M[f"{key}_sent"] + 0.2, 2.0)
        answer = (M[f"{key}_answer"] - 0.5, M[f"{key}_answer"] + 2.6, 1.0)
        start = t
        for a0, b0, sp in (typing, answer):
            clips.append(("main", a0, b0, sp))
            t += (b0 - a0) / sp
        labels.append((label, start, t - start))
        prev = M[f"{key}_answer"] + 2.6
    s["langs"] = scene("langs", clips, [("s06_langs", 0.5)], labels=labels)
    s["langs"]["subs"] = vo_subs(SCRIPT["s06_langs"]["sub"], 0.5, D["s06_langs"])

    a = M["s07"]
    sent = M["refusal_sent"]
    ans = M["refusal_answer"]
    len1 = (sent + 0.2 - a) / 2
    s["refusal"] = scene("refusal", [("main", a, sent + 0.2, 2), ("main", ans - 0.5, M["s07_end"], 1)], [("s07_refusal", len1 + 0.9)])
    s["refusal"]["subs"] = vo_subs(SCRIPT["s07_refusal"]["sub"], len1 + 0.9, D["s07_refusal"])
    s["refusal_short"] = scene("refusal_short", [("main", a, sent + 0.2, 2), ("main", ans - 0.5, ans + D["s07_refusal_short"] + 1.4, 1)],
                               [("s07_refusal_short", len1 + 0.9)])
    s["refusal_short"]["subs"] = vo_subs(SCRIPT["s07_refusal"]["short_sub"], len1 + 0.9, D["s07_refusal_short"])

    s["how"] = scene("how", [("main", M["s08"], M["s08_end"], 1)], [("s08_how", 0.4)])
    s["how"]["subs"] = vo_subs(SCRIPT["s08_how"]["sub"], 0.4, D["s08_how"])
    s["numbers"] = scene("numbers", [("main", M["s09"], M["s09_end"], 1)], [("s09_numbers", 0.6)])
    s["numbers"]["subs"] = vo_subs(SCRIPT["s09_numbers"]["sub"], 0.6, D["s09_numbers"])

    s["end"] = scene("end", [("end", end0, end0 + 6.0, 1)], [("s10_end", 1.0)], tail=0.3)
    return s


CUTS = {
    "full": ["hook", "shield", "home", "voice", "proof", "langs", "refusal", "how", "numbers", "end"],
    "90s": ["hook", "shield_short", "home", "voice", "proof", "refusal_short", "numbers", "end"],
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


def ts(t: float, ass: bool = False) -> str:
    h, rem = divmod(max(t, 0), 3600)
    m, s = divmod(rem, 60)
    if ass:
        return f"{int(h)}:{int(m):02d}:{s:05.2f}"
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


ASS_HEAD = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter,44,&H00FFFFFF,&H00FFFFFF,&H9A120A07,&H9A120A07,1,0,0,0,100,100,0,0,3,14,0,2,220,220,54,1
Style: Label,Inter,36,&H00EBDD42,&H00EBDD42,&HB0120A07,&HB0120A07,1,0,0,0,100,100,1,0,3,12,0,7,70,70,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def build_cut(name: str, scenes: dict) -> None:
    files, srt, ass, t, n = [], [], [ASS_HEAD], 0.0, 1
    for sid in CUTS[name]:
        sc = scenes[sid]
        f, length = render_scene(sc)
        files.append(f)
        for text, at, d in sc["subs"]:
            a, b = t + at, t + at + d
            srt.append(f"{n}\n{ts(a)} --> {ts(b)}\n{text}\n")
            ass.append(f"Dialogue: 0,{ts(a, True)},{ts(b, True)},Sub,,0,0,0,,{text}\n")
            n += 1
        for text, at, d in sc["labels"]:
            ass.append(f"Dialogue: 1,{ts(t + at, True)},{ts(t + at + d, True)},Label,,0,0,0,,{text}\n")
        t += length
    lst = TMP / f"{name}.txt"
    lst.write_text("".join(f"file '{f}'\n" for f in files))
    joined = TMP / f"{name}_joined.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], check=True)
    (OUT / f"pakkam-{name}.srt").write_text("\n".join(srt), encoding="utf-8")
    ass_path = TMP / f"{name}.ass"
    ass_path.write_text("".join(ass), encoding="utf-8")
    final = OUT / f"pakkam-{name}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(joined), "-vf", f"ass={ass_path}",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", str(final)], check=True)
    print(name, f"{t:.1f}s", final)


if __name__ == "__main__":
    sc = build_scenes()
    for cut in (sys.argv[3:] or CUTS):
        build_cut(cut, sc)
