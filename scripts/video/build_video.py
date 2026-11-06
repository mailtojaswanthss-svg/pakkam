"""Builds the three Lakshmi-story cuts (full, 90 s, 60 s) from the recording, the art and the narration.

    python scripts/video/build_video.py WORK_DIR OUT_DIR [cut ...]

WORK_DIR holds main.webm + marks.json (record_demo.js), hook.webm / end.webm + *.lead.txt
(record_cards.js), the WAVs + durations.json (make_voice.py) and go/p1,p2,p3,p10.png (pages of
the real G.O.(Ms) No.15 from the site's /page endpoint). The illustrations are scripts/video/art.
Writes OUT_DIR/pakkam-{full,90s,60s}.mp4, with no subtitles."""

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
M = json.loads((WORK / "marks.json").read_text())
D = json.loads((WORK / "durations.json").read_text())
LEAD = {n: float((WORK / f"{n}.lead.txt").read_text()) for n in ("hook", "end")}
W, H, FPS = 1920, 1080, 30


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


def still(name: str, image: Path, seconds: float, zoom_in: bool = True) -> Path:
    """A slow Ken Burns move over one illustration."""
    out = TMP / f"{name}.mp4"
    frames = int(seconds * FPS)
    z = f"1+0.08*on/{frames}" if zoom_in else f"1.08-0.08*on/{frames}"
    vf = (
        f"scale=3840:-2,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
        "format=yuv420p"
    )
    ffmpeg(
        "-loop",
        "1",
        "-i",
        str(image),
        "-vf",
        vf,
        "-t",
        f"{seconds:.3f}",
        "-c:v",
        "libx264",
        "-crf",
        "18",
        str(out),
    )
    return out


def music(seconds: float) -> Path:
    """An original ambient bed (no samples): warm chords that swell in, lift, and resolve."""
    out = TMP / f"music_{int(seconds)}.wav"
    chords = [
        (110.0, 164.81, 220.0, 277.18),
        (98.0, 146.83, 196.0, 246.94),
        (87.31, 130.81, 174.61, 220.0),
        (82.41, 123.47, 164.81, 207.65),
    ]
    bar = 4.0
    parts = []
    for i, ch in enumerate(chords):
        tone = "+".join(f"0.06*sin(2*PI*{f}*t)+0.02*sin(2*PI*{2 * f}*t)" for f in ch)
        env = f"if(between(mod(t,{4 * bar}),{i * bar},{(i + 1) * bar}),sin(PI*(mod(t,{bar}))/{bar})^0.6,0)"
        parts.append(f"({tone})*{env}")
    expr = "+".join(parts)
    fade_out = max(0.0, seconds - 3)
    ffmpeg(
        "-f",
        "lavfi",
        "-i",
        f"aevalsrc='{expr}':s=48000:d={seconds:.2f}",
        "-af",
        f"aecho=0.8:0.7:60|120:0.3|0.2,lowpass=f=2400,afade=t=in:d=2.5,afade=t=out:st={fade_out:.2f}:d=3,"
        "aformat=channel_layouts=stereo,volume=0.9",
        str(out),
    )
    return out


def go_scroll(seconds: float) -> Path:
    """The real Government Order pages scrolling past, too long to read."""
    out = TMP / "go_scroll.mp4"
    pages = [WORK / "go" / f"p{n}.png" for n in (1, 2, 3, 10)]
    ins = sum((["-i", str(p)] for p in pages), [])
    stack = "".join(
        f"[{i}:v]scale=1100:-2,pad=1160:ih+40:30:20:color=0x0b1020[p{i}];"
        for i in range(len(pages))
    )
    stack += "".join(f"[p{i}]" for i in range(len(pages))) + f"vstack=inputs={len(pages)}[s];"
    vf = (
        stack + f"color=c=0x0b1020:s={W}x{H}:r={FPS}:d={seconds:.3f}[bg];"
        f"[bg][s]overlay=x=(W-w)/2:y='-(h-H)*t/{seconds:.3f}':shortest=0,format=yuv420p[v]"
    )
    ffmpeg(
        *ins,
        "-filter_complex",
        vf,
        "-map",
        "[v]",
        "-t",
        f"{seconds:.3f}",
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-crf",
        "18",
        str(out),
    )
    return out


def prepare() -> dict:
    art = HERE / "art"
    return {
        "main": WORK / "main.webm",
        "hook": WORK / "hook.webm",
        "end": WORK / "end.webm",
        "art1": still("art1", art / "lakshmi-1.png", 4.0),
        "art2": still("art2", art / "lakshmi-2.png", 3.5, zoom_in=False),
        "art3": still("art3", art / "lakshmi-3.png", 2.0),
        "art4": still("art4", art / "lakshmi-4.png", 3.0, zoom_in=False),
        "go": go_scroll(6.5),
    }


def scene(sid: str, clips: list, audio: list, tail: float = 0.6) -> dict:
    """clips: (source, start, end, speed); audio: (wav name, at seconds)."""
    return {"id": sid, "clips": clips, "audio": audio, "tail": tail}


def build_scenes() -> dict:
    s = {}
    h0, e0 = LEAD["hook"], LEAD["end"]
    s["hook"] = scene("hook", [("hook", h0 + 0.3, h0 + 4.0, 1)], [("l0_hook", 0.15)], tail=0.2)
    s["day"] = scene("day", [("art1", 0, 4.0, 1)], [("l1_day", 0.15)], tail=0.3)
    s["struggle"] = scene(
        "struggle", [("art2", 0, 3.5, 1), ("go", 0, 6.5, 1)], [("l2_struggle", 0.2)], tail=0.3
    )
    s["intro"] = scene(
        "intro",
        [("art3", 0, 2.0, 1), ("main", M["l3"], M["l3"] + 2.2, 1)],
        [("l3_intro", 0.2)],
        tail=0.3,
    )

    a, mic, ans, pr, e = M["l4"], M["l4_mic"], M["l4_answer"], M["l4_proof"], M["l4_end"]
    a = mic - 2.6
    len1 = mic + 3.4 - a
    len2 = pr - (ans - 0.6)
    s["ask"] = scene(
        "ask",
        [("main", a, mic + 3.4, 1), ("main", ans - 0.6, pr, 1), ("main", pr, e, 1)],
        [
            ("l4_ask", 0.1),
            ("tamil_question", mic + 0.55 - a),
            ("l4_ask_b", len1 + 0.3),
            ("tamil_answer", len1 + 0.5 + D["l4_ask_b"]),
            ("l4_ask_c", len1 + len2 + 0.3),
        ],
        tail=0.3,
    )

    a, sent, ans = M["l5"], M["refusal_sent"], M["refusal_answer"]
    len1 = (sent + 0.2 - a) / 2.5
    s["refusal"] = scene(
        "refusal",
        [
            ("main", a, sent + 0.2, 2.5),
            ("main", ans - 0.4, M["l5_end"], 1),
            ("main", M["l5b"], M["l5b_end"], 1),
        ],
        [("l5_refusal", 0.2)],
        tail=0.3,
    )
    s["refusal_short"] = scene(
        "refusal_short",
        [("main", a, sent + 0.2, 2.5), ("main", ans - 0.4, ans + D["l5_refusal_short"] + 0.8, 1)],
        [("l5_refusal_short", len1 + 0.3)],
        tail=0.3,
    )

    s["bigger"] = scene(
        "bigger",
        [
            ("main", M["l6_verdict"] - 0.3, M["l6_verdict"] + 2.6, 1),
            ("main", M["l6_schemes"] + 0.8, M["l6_schemes"] + 3.0, 1),
            ("main", M["l6_lang"] + 0.6, M["l6_lang"] + 3.0, 1),
        ],
        [("l6_bigger", 0.2)],
        tail=0.3,
    )
    s["end"] = scene(
        "end", [("art4", 0, 3.0, 1), ("end", e0, e0 + 3.6, 1)], [("l7_end", 0.4)], tail=0.6
    )
    s["end_short"] = scene("end_short", [("end", e0, e0 + 4.0, 1)], [("l7_end", 0.3)], tail=0.6)
    return s


CUTS = {
    "full": ["hook", "day", "struggle", "intro", "ask", "refusal", "bigger", "end"],
    "90s": ["hook", "day", "struggle", "intro", "ask", "refusal_short", "bigger", "end"],
    "60s": ["hook", "day", "intro", "ask", "refusal_short", "end_short"],
}


def wav_len(name: str) -> float:
    if name not in D:
        out = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(WORK / f"{name}.wav"),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        D[name] = float(out.stdout)
    return D[name]


def render_scene(sc: dict, src: dict) -> tuple[Path, float]:
    """One scene as an MP4 with its own audio; returns the file and its length."""
    vlen = sum((b - a) / sp for _, a, b, sp in sc["clips"])
    length = max(vlen, max(at + wav_len(n) for n, at in sc["audio"]) + sc["tail"])
    out = TMP / f"{sc['id']}.mp4"
    order = sorted({c[0] for c in sc["clips"]})
    cmd = []
    for name in order:
        cmd += ["-i", str(src[name])]
    for n, _ in sc["audio"]:
        cmd += ["-i", str(WORK / f"{n}.wav")]
    parts, labels = [], []
    for i, (name, a, b, sp) in enumerate(sc["clips"]):
        parts.append(
            f"[{order.index(name)}:v]trim=start={a:.3f}:end={b:.3f},setpts=(PTS-STARTPTS)/{sp},fps={FPS},"
            f"scale={W}:{H}:flags=lanczos,setsar=1,format=yuv420p[v{i}]"
        )
        labels.append(f"[v{i}]")
    pad = max(0, length - vlen) + 0.1
    vf = (
        ";".join(parts) + f";{''.join(labels)}concat=n={len(labels)}:v=1:a=0[vc];"
        f"[vc]tpad=stop_mode=clone:stop_duration={pad:.3f},trim=duration={length:.3f}[v]"
    )
    aparts, alabels = [], []
    for j, (_n, at) in enumerate(sc["audio"]):
        ms = int(at * 1000)
        aparts.append(
            f"[{len(order) + j}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[a{j}]"
        )
        alabels.append(f"[a{j}]")
    af = (
        ";".join(aparts)
        + f";{''.join(alabels)}amix=inputs={len(alabels)}:normalize=0,apad,atrim=duration={length:.3f}[a]"
    )
    ffmpeg(
        *cmd,
        "-filter_complex",
        vf + ";" + af,
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        str(out),
    )
    return out, length


def build_cut(name: str, scenes: dict, src: dict) -> None:
    files, t = [], 0.0
    for sid in CUTS[name]:
        f, length = render_scene(scenes[sid], src)
        files.append(f)
        t += length
    lst = TMP / f"{name}.txt"
    lst.write_text("".join(f"file '{f}'\n" for f in files))
    joined = TMP / f"{name}_joined.mp4"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined))
    final = OUT / f"pakkam-{name}.mp4"
    bed = music(t + 1)
    mix = (
        "[1:a]volume=0.5[m];[0:a]asplit[v][key];"
        "[m][key]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=600[duck];"
        "[v][duck]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
    )
    ffmpeg(
        "-i",
        str(joined),
        "-i",
        str(bed),
        "-filter_complex",
        mix,
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        str(final),
    )
    print(name, f"{t:.1f}s", final)


if __name__ == "__main__":
    sources = prepare()
    sc = build_scenes()
    for cut in sys.argv[3:] or CUTS:
        build_cut(cut, sc, sources)
