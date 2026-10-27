"""Build a narrated slideshow demo video (offline): PIL slides + espeak-ng voice + ffmpeg.

Usage: python3 scripts/make_demo_video.py  -> build/demo/redloop_demo.mp4
Runs the offline showcase pipeline fresh and puts its real outputs on the slides.
Muse Spark numbers are quoted from results/ (recorded live runs), not regenerated.
"""
import pathlib, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUN = ROOT / "build" / "video_run"
OUT = ROOT / "build" / "demo"
W, H = 1280, 720
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PY = sys.executable


def sh(*args, ok=(0,)):
    r = subprocess.run([PY, "-m", "redloop", *args], cwd=ROOT, capture_output=True, text=True)
    if r.returncode not in ok:
        raise SystemExit(f"{args} exit {r.returncode}: {r.stderr[-500:]}")
    return r.stdout + r.stderr


def run_pipeline():
    RUN.mkdir(parents=True, exist_ok=True)
    a = str(RUN / "attack.jsonl")
    pathlib.Path(a).unlink(missing_ok=True)
    sh("attack", "--all", "--agents", "naive,guarded", "--results", a)
    sh("report", "--results", a, "--out", str(RUN / "ASR.md"))
    sh("export-suite", "--results", a, "--out", str(RUN / "suite.json"))
    g = sh("check-suite", "--suite", str(RUN / "suite.json"), "--agent", "guarded")
    n = sh("check-suite", "--suite", str(RUN / "suite.json"), "--agent", "naive", ok=(1,))
    return (RUN / "ASR.md").read_text(), g, n


def asr_table(md):
    rows = [[c.strip().strip("*") for c in l.strip("|").split("|")] for l in md.splitlines()
            if l.startswith("|") and "---" not in l and "Scenario" not in l and len(l.split("|")) == 5]
    out = ["scenario                        guarded         naive"]
    out += [f"{r[0][:30]:31} {r[1]:15} {r[2]}" for r in rows]
    return out


def slide(path, title, body, mono=True):
    img = Image.new("RGB", (W, H), (12, 16, 28))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 8], fill=(230, 60, 70))
    d.text((48, 32), title, font=ImageFont.truetype(SANS, 40), fill=(255, 255, 255))
    f = ImageFont.truetype(MONO if mono else SANS, 17 if mono else 28)
    y = 112
    for line in body:
        col = (255, 110, 110) if line.startswith("RED") or "65/65" in line else (120, 230, 150) if line.startswith("GREEN") or "0/65" in line else (210, 220, 235)
        d.text((48, y), line, font=f, fill=col)
        y += 25 if mono else 44
    d.text((48, H - 40), "RedLoop  |  Meta Global AI Developer Hackathon  |  sandboxed, synthetic data", font=ImageFont.truetype(MONO, 16), fill=(120, 130, 150))
    img.save(path)


def main():
    md, g, n = run_pipeline()
    OUT.mkdir(parents=True, exist_ok=True)
    tbl = asr_table(md)
    nred = [l for l in n.splitlines() if l.startswith("RED")][:12] + [n.strip().splitlines()[-1]]
    ggreen = [l for l in g.splitlines() if l.startswith("GREEN")][:12] + [g.strip().splitlines()[-1]]
    slides = [
        ("RedLoop", ["A unit test for prompt injection.", "It attacks tool-using AI agents with hidden instructions,", "judges every outbound action,", "and fails CI when a fixed hole reopens."], False,
         "Agents read untrusted email, tickets and screenshots. One hidden instruction can leak a secret. RedLoop is a unit test for that: it attacks tool using agents, judges every outbound action, and fails C I when a fixed hole reopens."),
        ("13 sandboxed scenarios", ["email, Slack, GitHub, X, calendar,", "docs, CRM, and a screenshot-OCR support ticket.", "Fresh sandbox per trial. No real accounts touched.", "An evolutionary attacker mutates payloads", "and keeps the strongest."], False,
         "RedLoop drops an agent into thirteen sandboxed scenarios across email, Slack, GitHub, X, calendar, docs, C R M, and a screenshot of a support ticket. An evolutionary attacker mutates injected payloads and keeps the strongest ones."),
        ("Attack search: naive vs guarded", tbl, True,
         "Here is a fresh offline attack search. The naive agent is breached in about ninety one percent of attempts. The guarded agent is breached in zero."),
        ("Frozen suite: naive agent goes RED", nred, True,
         "Successful attacks are frozen into a sixty five case regression suite. Replayed against the naive agent, all sixty five still succeed, so the check exits non zero and C I fails."),
        ("Guarded agent stays GREEN", ggreen, True,
         "The guarded agent passes all sixty five. In our ablation, spotlighting alone and a tool allowlist alone each also block all sixty five, so one regression does not reopen the hole."),
        ("Live on Muse Spark (Meta Model API)", ["Frozen 65-case suite, Muse Spark as target agent:", "  unguarded: 0/56 breaches   guarded: 0/55 breaches", "  about $1.16 per 65-run sweep, 8-10 s mean latency", "Live evolutionary search: 0/128 and 0/127 over 255 episodes", "", "The live runs exposed a real bug: the agent looped", "guessing document IDs. A docs.list_docs tool fixed it;", "docs scenarios now finish in 2 tool actions."], True,
         "Live on Muse Spark through the Meta Model A P I, the frozen suite found zero breaches for both variants, at about one dollar sixteen per sweep. The live runs also exposed a real reliability bug, an agent looping on document I Ds, and a new list docs tool fixed it."),
        ("Find the hole. Keep it closed.", ["pip install, one command, one GitHub Action.", "Infra errors are UNKNOWN, never counted as safe.", "github.com/arthi-arumugam-git/redloop"], False,
         "RedLoop. Find the hole, and keep it closed."),
    ]
    parts = []
    for i, (title, body, mono, voice) in enumerate(slides):
        png, wav, mp4 = OUT / f"s{i}.png", OUT / f"s{i}.wav", OUT / f"s{i}.mp4"
        slide(png, title, body, mono)
        subprocess.run(["espeak-ng", "-v", "en-us", "-s", "155", "-w", str(wav), voice], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(png), "-i", str(wav), "-c:v", "libx264", "-tune", "stillimage",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-af", "apad=pad_dur=0.8", "-shortest", str(mp4)], check=True)
        parts.append(mp4)
    lst = OUT / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    final = OUT / "redloop_demo.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(final)], check=True)
    for p in OUT.glob("s*.*"):
        p.unlink()
    lst.unlink()
    print(final)


if __name__ == "__main__":
    main()
