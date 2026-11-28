"""Old MacDonald in 3D: Mo visits Grandpa's farm. Builds a Hyperframes project from the song timing.

    python cartoon3d/oldmac3d.py      # needs videos/oldmac/song.wav + words.json; writes videos/oldmac/anim3d/
    (then: cd videos/oldmac/anim3d && npx hyperframes@0.9.40 render)
"""
import json
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import make_video as mv  # noqa: E402

F = os.path.join(ROOT, "videos", "oldmac")
A = os.path.join(F, "anim3d")
ORDER = [("cow", "moo"), ("pig", "oink"), ("duck", "quack"), ("sheep", "baa"), ("horse", "neigh"), ("chicken", "cluck")]
LETTERS = [("E", "#ff5a5f"), ("I", "#ffb400"), ("E", "#3ec300"), ("I", "#1fa2ff"), ("O", "#a259ff")]
rnd = random.Random(4)
js = []


def J(o):
    return json.dumps(o)


def at(t):
    return f"{max(0.0, t):.3f}"


def to(sel, p, t):
    js.append(f"tl.to({J(sel)}, {J(p)}, {at(t)});")


def fromto(sel, a, b, t):
    js.append(f"tl.fromTo({J(sel)}, {J(a)}, {J(dict(b, immediateRender=False))}, {at(t)});")


def setp(sel, p, t):
    js.append(f"tl.set({J(sel)}, {J(p)}, {at(t)});")


def main():
    lyrics = open(os.path.join(F, "lyrics.txt"), encoding="utf-8").read()
    lines = mv.lyric_lines(lyrics)
    song = os.path.join(F, "song.wav")
    words = json.load(open(os.path.join(F, "words.json"), encoding="utf-8"))
    D = mv.probe_duration(song)
    timed = mv.time_lines(lines, words, D)
    bt = [x["time"] for x in json.load(open(os.path.join(F, "anim", "beats", "assets", "song.wav.json")))["beats"]]
    gaps = sorted(b - a for a, b in zip(bt, bt[1:]))
    beat, b0 = gaps[len(gaps) // 2], bt[0]
    last = timed[-1]["end"]

    os.makedirs(os.path.join(A, "assets", "fonts"), exist_ok=True)
    shutil.copy(song, os.path.join(A, "assets", "song.wav"))
    shutil.copy(os.path.join(F, "anim", "assets", "fonts", "rounded.ttf"), os.path.join(A, "assets", "fonts", "rounded.ttf"))
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(os.path.join(F, "anim", f), os.path.join(A, f))
    open(os.path.join(A, "meta.json"), "w").write('{"id":"oldmac3d","name":"oldmac3d","createdAt":"2026-11-28T19:00:00.000Z"}')
    for f in ("characters.js", "animals.js", "scene_oldmac.js"):
        shutil.copy(os.path.join(HERE, "lib", f), os.path.join(A, f))

    # ---------------- cues for the 3D scene
    verses = []
    for v, (name, snd) in enumerate(ORDER):
        L = timed[v * 5: v * 5 + 5]
        nw = next((w for w in L[1]["words"] if w["w"] in (name, name + "s")), None)
        sounds = [w for ln in (L[2], L[3]) for w in ln["words"] if mv.tokens(w["w"])[:1] == [snd]]
        cue = [w for ln in (L[2], L[3]) for w in ln["words"] if mv.tokens(w["w"])[:1] and mv.tokens(w["w"])[0] in ("here", "there", "everywhere")]
        pops, j = [], 0
        for w in cue:
            if j >= 8:
                break
            if mv.tokens(w["w"])[0] == "everywhere":
                pops += [w["s"] + 0.07 * k for k in range(8 - j)]
                j = 8
            else:
                pops.append(w["s"])
                j += 1
        verses.append({"L": [{"start": l["start"], "end": l["end"], "words": l["words"]} for l in L],
                       "name": nw["s"] if nw else L[1]["start"] + 1.6, "sounds": sounds, "pops": pops})
    cues = {"D": D, "beat": beat, "b0": b0, "last": last, "verses": verses}

    # ---------------- 2D overlays: title, captions, E-I-E-I-O, sound bubbles, name cards, bye, confetti
    html = []
    H = html.append
    H('<div class="abs" id="eieio">' + "".join(f'<div class="ltr" id="l{i}" style="background:{c}">{ch}</div>' for i, (ch, c) in enumerate(LETTERS)) + '</div>')
    for v, (name, snd) in enumerate(ORDER):
        H(f'<div class="abs bubble" id="bub{v}"><span>{snd.upper()}!</span></div>')
        H(f'<div class="abs namecard" id="name{v}">{name.upper()}</div>')
    H('<div class="abs" id="title"><div class="t1">' + "".join(f'<span class="tl">{c if c != " " else "&nbsp;"}</span>' for c in "Old MacDonald")
      + '</div><div class="t2">' + "".join(f'<span class="tl">{c if c != " " else "&nbsp;"}</span>' for c in "Had a Farm") + '</div></div>')
    H('<div class="abs" id="bye">Bye bye, friends!</div>')
    for i in range(40):
        c = ["#ff5a5f", "#ffb400", "#3ec300", "#1fa2ff", "#a259ff", "#ff7ac6"][i % 6]
        H(f'<div class="abs confetti" id="c{i}" style="background:{c};left:{rnd.randint(40, 1880)}px"></div>')
    for i, ln in enumerate(timed):
        ws = "".join(f'<span class="w" id="w{i}_{k}">{w}</span> ' for k, w in enumerate(ln["line"].split()))
        H(f'<div class="abs cap" id="cap{i}"><div class="pill">{ws}</div></div>')

    setp(".ltr, .bubble, .namecard, #bye", {"scale": 0}, 0)
    first = timed[0]["start"]
    fromto("#title .tl", {"y": -300, "opacity": 0}, {"y": 0, "opacity": 1, "duration": 0.6, "ease": "bounce.out", "stagger": 0.06}, 0.6)
    to("#title", {"scale": 0.2, "opacity": 0, "duration": 0.45, "ease": "back.in(1.6)"}, max(2.5, first - 0.7))
    for i, ln in enumerate(timed):
        s = ln["start"] - 0.25
        nxt = timed[i + 1]["start"] - 0.25 if i + 1 < len(timed) else ln["end"] + 1.5
        e = min(nxt, ln["end"] + 1.2)
        fromto(f"#cap{i}", {"opacity": 0, "y": 30}, {"opacity": 1, "y": 0, "duration": 0.2, "ease": "power2.out"}, s)
        to(f"#cap{i}", {"opacity": 0, "duration": 0.15}, e - 0.15)
        k = 0
        for j, w in enumerate(ln["line"].split()):
            tk = mv.tokens(w)
            if not tk:
                continue
            to(f"#w{i}_{j}", {"color": "#ff6a00", "duration": 0.08}, ln["words"][min(k, len(ln["words"]) - 1)]["s"])
            k += len(tk)
    for v, (name, snd) in enumerate(ORDER):
        V = verses[v]
        L = V["L"]
        for idx in (0, 1, 4):
            ws = L[idx]["words"][-5:]
            nx = timed[v * 5 + idx + 1]["start"] if v * 5 + idx + 1 < 30 else last + 2
            for i, w in enumerate(ws):
                fromto(f"#l{i}", {"scale": 0, "rotation": -30, "opacity": 1}, {"scale": 1, "rotation": 0, "duration": 0.35, "ease": "back.out(2.5)"}, w["s"])
            end = min(nx - 0.1, ws[-1]["e"] + 0.7)
            to("#eieio .ltr", {"scale": 0, "opacity": 0, "duration": 0.2, "ease": "back.in(2)", "stagger": 0.03}, end - 0.2)
        fromto(f"#name{v}", {"scale": 0, "opacity": 1}, {"scale": 1, "duration": 0.4, "ease": "back.out(2.2)"}, V["name"])
        to(f"#name{v}", {"scale": 0, "opacity": 0, "duration": 0.25, "ease": "back.in(2)"}, L[2]["start"] - 0.3)
        runs = []
        for w in V["sounds"]:
            if runs and w["s"] - runs[-1][-1]["e"] < 0.7:
                runs[-1].append(w)
            else:
                runs.append([w])
        for run in runs:
            s0, e0 = run[0]["s"], max(run[-1]["e"], run[-1]["s"] + 0.35) + 0.2
            fromto(f"#bub{v}", {"scale": 0, "opacity": 1, "rotation": -12}, {"scale": 1, "rotation": 0, "duration": 0.2, "ease": "back.out(3)"}, s0 - 0.05)
            for w in run[1:]:
                fromto(f"#bub{v}", {"scale": 1.18}, {"scale": 1, "duration": 0.2, "ease": "power2.out"}, w["s"])
            to(f"#bub{v}", {"scale": 0, "opacity": 0, "duration": 0.14}, e0)
    fromto("#bye", {"scale": 0, "opacity": 1}, {"scale": 1, "duration": 0.6, "ease": "back.out(2)"}, last + 0.8)
    for i in range(40):
        fromto(f"#c{i}", {"y": -60, "opacity": 1, "rotation": 0},
               {"y": 1200, "rotation": rnd.randint(200, 720), "x": rnd.randint(-120, 120), "duration": rnd.uniform(2.4, 3.6), "ease": "none"},
               last + 0.7 + rnd.uniform(0, 1.2))
    to("#fade", {"opacity": 1, "duration": 0.8}, D - 0.9)

    css = open(os.path.join(HERE, "oldmac3d.css"), encoding="utf-8").read()
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>Old MacDonald Had a Farm</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js"></script>
<style>
{css}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="1920" data-height="1080" data-fps="30">
<canvas id="c" width="1920" height="1080"></canvas>
{chr(10).join(html)}
<div class="abs" id="fade"></div>
<audio id="music" data-timeline-role="music" class="clip" data-start="0" data-duration="{D:.3f}" data-track-index="10" data-volume="1" src="assets/song.wav"></audio>
</div>
<script>window.CUES = {json.dumps(cues)};</script>
<script src="characters.js"></script>
<script src="animals.js"></script>
<script src="scene_oldmac.js"></script>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.to(Scene3D.clock, {{ t: {D:.3f}, duration: {D:.3f}, ease: "none" }}, 0);
{chr(10).join(js)}
tl.set({{}}, {{}}, {D:.3f});
window.__timelines["main"] = tl;
Scene3D.draw(0);
</script>
</body>
</html>'''
    open(os.path.join(A, "index.html"), "w", encoding="utf-8").write(page)
    print(f"built: {D:.1f} s, beat {beat:.3f}, overlay tweens {len(js)}")


if __name__ == "__main__":
    main()
