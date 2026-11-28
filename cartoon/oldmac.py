"""Builds the Old MacDonald cartoon (a Hyperframes project) timed to the sung words.

    python cartoon/oldmac.py            # uses videos/oldmac/song.wav + words.json if they exist, else a guessed timing

Writes videos/oldmac/anim/index.html; render it with hyperframes.
"""
import json
import os
import random
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import art  # noqa: E402
import make_video as mv  # noqa: E402

F = os.path.join(ROOT, "videos", "oldmac")
A = os.path.join(F, "anim")
ORDER = [("cow", "moo"), ("pig", "oink"), ("duck", "quack"), ("sheep", "baa"), ("horse", "neigh"), ("chicken", "cluck")]
LETTERS = [("E", "#ff5a5f"), ("I", "#ffb400"), ("E", "#3ec300"), ("I", "#1fa2ff"), ("O", "#a259ff")]

CX, FEET = 700, 935           # where the verse's animal stands (centre x, feet y)
BIG = 470                     # its size in px
DOOR = (262, 878)             # barn door: animals come out of here
rnd = random.Random(11)


def fake_words(lines, start=5.0, per_line=4.3, gap_every=5, gap=2.2):
    """Even timing for building before the song exists."""
    words, t = [], start
    for i, ln in enumerate(lines):
        toks = mv.tokens(ln)
        step = per_line * 0.92 / len(toks)
        for k, w in enumerate(toks):
            words.append({"w": w, "s": round(t + k * step, 2), "e": round(t + (k + 0.9) * step, 2)})
        t += per_line + (gap if (i + 1) % gap_every == 0 else 0)
    return words, t + 4


def main():
    lyrics = open(os.path.join(F, "lyrics.txt"), encoding="utf-8").read()
    lines = mv.lyric_lines(lyrics)
    song = os.path.join(F, "song.wav")
    wpath = os.path.join(F, "words.json")
    os.makedirs(os.path.join(A, "assets"), exist_ok=True)
    if os.path.exists(song) and os.path.exists(wpath):
        D = mv.probe_duration(song)
        words = json.load(open(wpath, encoding="utf-8"))
        shutil.copy(song, os.path.join(A, "assets", "song.wav"))
        have_song = True
    else:
        words, D = fake_words(lines)
        have_song = False
    timed = mv.time_lines(lines, words, D)
    assert len(timed) == 30, len(timed)
    bpm = 112
    info = os.path.join(F, "ace15_info.json")
    if os.path.exists(info):
        try:
            b = json.load(open(info))["takes"][0].get("bpm")
            bpm = float(b) if b else bpm
        except Exception:  # noqa: BLE001
            pass
    beat, b0 = 60.0 / bpm, 0.0
    bfile = os.path.join(A, "beats", "assets", "song.wav.json")
    if have_song and os.path.exists(bfile):   # the real beat, from `hyperframes beats`
        bt = [x["time"] for x in json.load(open(bfile))["beats"]]
        gaps = sorted(b - a for a, b in zip(bt, bt[1:]))
        beat, b0 = gaps[len(gaps) // 2], bt[0]
        bpm = round(60 / beat, 1)
    first, last = timed[0]["start"], timed[-1]["end"]

    html, js = [], []
    T = js.append

    def at(t):
        return f"{max(0.0, t):.3f}"

    # ------------------------------------------------------------- background world
    html.append(f'<div id="world">')
    html.append(f'<div class="abs" id="farm">{art.farm()}</div>')
    html.append(f'<div class="abs" id="sun" style="left:1520px;top:10px;width:320px;height:320px">{art.sun()}</div>')
    for i, (x, y, w) in enumerate([(120, 70, 280), (760, 150, 220), (1180, 60, 250)]):
        html.append(f'<div class="abs cloud" id="cloud{i}" style="left:{x}px;top:{y}px;width:{w}px">{art.cloud(w)}</div>')
        T(f'tl.to("#cloud{i}", {{x: {260 if i % 2 == 0 else -220}, duration: {D:.2f}, ease: "none"}}, 0);')
    T(f'tl.to("#sun .rays", {{rotation: 90, svgOrigin: "0 0", duration: {D:.2f}, ease: "none"}}, 0);')
    T(f'tl.to("#sun", {{y: 10, duration: {beat * 2:.3f}, yoyo: true, repeat: {int(D / beat / 2)}, ease: "sine.inOut"}}, 0);')

    # characters: .pos (placement) > .bob (beat bounce) > .sq (squash) > svg
    def char(cid, svg, w, h, left, top, z, cls="", hidden=True):
        op = "opacity:0;" if hidden else ""
        html.append(f'<div class="abs pos {cls}" id="{cid}" style="left:{left}px;top:{top}px;width:{w}px;height:{h}px;z-index:{z};{op}">'
                    f'<div class="bob"><div class="sq">{svg}</div></div></div>')

    def bob(sel, t0, t1, amp=14, period=None):
        period = period or beat
        k = -(-(t0 - b0) // period)            # start on a beat, so everyone bounces with the music
        t0 = b0 + k * period
        n = max(1, int((t1 - t0) / period))
        T(f'tl.to("{sel} > .bob", {{y: -{amp}, duration: {period / 2:.3f}, yoyo: true, repeat: {n * 2 - 1}, ease: "sine.inOut"}}, {at(t0)});')

    def blink(sel, t0, t1):
        t = t0 + rnd.uniform(0.5, 2.0)
        while t < t1 - 0.3:
            T(f'tl.to("{sel} .eyes", {{scaleY: 0.1, transformOrigin: "50% 50%", duration: 0.07, yoyo: true, repeat: 1}}, {at(t)});')
            t += rnd.uniform(2.6, 4.4)

    def mouth(sel, s, e):
        e = max(e, s + 0.16)
        T(f'tl.set("{sel} .mouth-open", {{opacity: 1}}, {at(s)}); tl.set("{sel} .mouth-shut", {{opacity: 0}}, {at(s)});')
        T(f'tl.set("{sel} .mouth-open", {{opacity: 0}}, {at(e)}); tl.set("{sel} .mouth-shut", {{opacity: 1}}, {at(e)});')

    # farmer: always there, sings the "Old MacDonald" lines
    char("farmer", art.farmer(), 330, 550, 1455, 455, 30, hidden=False)
    bob("#farmer", 0, D, 10, beat)
    blink("#farmer", 0, D)

    feats, slots = [], []
    for v, (name, snd) in enumerate(ORDER):
        svg = getattr(art, name)()
        char(f"a{v}", svg, BIG, BIG, CX - BIG // 2, FEET - int(BIG * 0.95), 20 - v)
        feats.append(svg)
        slots.append((975 + v * 86, 800))
        for m in range(8):
            char(f"m{v}_{m}", svg, 200, 200, 0, 0, 25, "mini")
    html.append('</div>')   # world

    # ------------------------------------------------------------- overlays
    html.append('<div class="abs" id="eieio">' + "".join(
        f'<div class="ltr" id="l{i}" style="background:{c}">{ch}</div>' for i, (ch, c) in enumerate(LETTERS)) + '</div>')
    for v, (name, snd) in enumerate(ORDER):
        html.append(f'<div class="abs bubble" id="bub{v}"><span>{snd.upper()}!</span></div>')
        html.append(f'<div class="abs namecard" id="name{v}">{name.upper()}</div>')
    html.append('<div class="abs" id="title"><div class="t1">' + "".join(
        f'<span class="tl">{c if c != " " else "&nbsp;"}</span>' for c in "Old MacDonald") +
        '</div><div class="t2">' + "".join(f'<span class="tl">{c if c != " " else "&nbsp;"}</span>' for c in "Had a Farm") + '</div></div>')
    html.append('<div class="abs" id="bye">Bye bye, friends!</div>')
    for i, ln in enumerate(timed):
        ws = "".join(f'<span class="w" id="w{i}_{k}">{w}</span> ' for k, w in enumerate(ln["line"].split()))
        html.append(f'<div class="abs cap" id="cap{i}"><div class="pill">{ws}</div></div>')

    # ------------------------------------------------------------- intro title
    T('tl.fromTo("#title .tl", {y: -260, opacity: 0}, {y: 0, opacity: 1, duration: 0.55, ease: "bounce.out", stagger: 0.06}, 0.2);')
    T(f'tl.to("#title .tl", {{y: -16, duration: {beat / 2:.3f}, yoyo: true, repeat: {max(1, int((first - 2.0) / beat) * 2 - 1)}, ease: "sine.inOut", stagger: 0.04}}, 1.6);')
    T(f'tl.to("#title", {{scale: 0.2, opacity: 0, duration: 0.45, ease: "back.in(1.6)"}}, {at(max(1.8, first - 0.5))});')
    T('tl.to("#farmer .arm", {rotation: -18, svgOrigin: "210 248", duration: 0.28, yoyo: true, repeat: 7, ease: "sine.inOut"}, 0.6);')

    # ------------------------------------------------------------- captions (karaoke)
    for i, ln in enumerate(timed):
        s = ln["start"] - 0.25
        nxt = timed[i + 1]["start"] - 0.25 if i + 1 < len(timed) else ln["end"] + 1.5
        e = min(nxt, ln["end"] + 1.2)
        T(f'tl.fromTo("#cap{i}", {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: 0.2, ease: "power2.out"}}, {at(s)});')
        T(f'tl.to("#cap{i}", {{opacity: 0, duration: 0.15}}, {at(e - 0.15)});')
        shown = ln["line"].split()
        toks = [mv.tokens(w) for w in shown]
        k = 0
        for j, tk in enumerate(toks):
            if not tk:
                continue
            wt = ln["words"][min(k, len(ln["words"]) - 1)]
            T(f'tl.to("#w{i}_{j}", {{color: "#ff6a00", scale: 1.07, duration: 0.08}}, {at(wt["s"])});')
            T(f'tl.to("#w{i}_{j}", {{scale: 1, duration: 0.15}}, {at(wt["s"] + 0.1)});')
            k += len(tk)

    # ------------------------------------------------------------- E-I-E-I-O letters
    def eieio(ln, nxt_start):
        ws = ln["words"][-5:]
        for i, w in enumerate(ws):
            T(f'tl.fromTo("#l{i}", {{scale: 0, rotation: -30, opacity: 1}}, {{scale: 1, rotation: 0, duration: 0.35, ease: "back.out(2.5)"}}, {at(w["s"])});')
        end = min(nxt_start - 0.1, ws[-1]["e"] + 0.7)
        T(f'tl.to("#eieio .ltr", {{y: -14, duration: 0.12, yoyo: true, repeat: 1, stagger: 0.05}}, {at(ws[-1]["e"])});')
        T(f'tl.to("#eieio .ltr", {{scale: 0, opacity: 0, duration: 0.2, ease: "back.in(2)", stagger: 0.03}}, {at(end - 0.2)});')
        # the farmer dances on E-I-E-I-O
        T(f'tl.to("#farmer > .bob > .sq", {{rotation: 6, transformOrigin: "50% 100%", duration: {beat / 2:.3f}, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {at(ws[0]["s"])});')

    def sing(sel, ln):
        for w in ln["words"]:
            mouth(sel, w["s"], w["e"] - 0.04)

    minis_pos = [(300, 800, 1.0), (1090, 790, 1.0), (90, 860, 0.9), (1210, 650, 0.8),
                 (520, 270, 0.75), (900, 210, 0.75), (1270, 330, 0.7), (180, 380, 0.7)]

    for v, (name, snd) in enumerate(ORDER):
        L = timed[v * 5: v * 5 + 5]
        nxt = timed[v * 5 + 5]["start"] if v < 5 else last + 3
        a = f"#a{v}"
        # line 0: Old MacDonald had a farm (farmer sings, waves)
        sing("#farmer", L[0])
        sing("#farmer", L[4])
        T(f'tl.to("#farmer .arm", {{rotation: -22, svgOrigin: "210 248", duration: {beat:.3f}, yoyo: true, repeat: 3, ease: "sine.inOut"}}, {at(L[0]["start"])});')
        for ln in (L[0], L[1], L[4]):
            eieio(ln, timed[timed.index(ln) + 1]["start"] if timed.index(ln) + 1 < len(timed) else last + 2)
        # line 1: the animal comes out of the barn and hops to the middle, landing on its name
        animal_w = next((w for w in L[1]["words"] if w["w"] in (name, name + "s")), L[1]["words"][7])
        t_in, t_land = L[1]["start"] - 0.6, animal_w["s"]
        dx, dy = DOOR[0] - CX, DOOR[1] - FEET
        T(f'tl.set("{a}", {{opacity: 1, x: {dx}, y: {dy}, scale: 0.35, transformOrigin: "50% 95%"}}, {at(t_in)});')
        T(f'tl.to("{a}", {{x: 0, y: 0, scale: 1, duration: {max(0.8, t_land - t_in):.3f}, ease: "power1.inOut"}}, {at(t_in)});')
        hops = max(2, int((t_land - t_in) / 0.42))
        T(f'tl.to("{a} > .bob", {{y: -60, duration: {(t_land - t_in) / hops / 2:.3f}, yoyo: true, repeat: {hops * 2 - 1}, ease: "power1.out"}}, {at(t_in)});')
        T(f'tl.fromTo("{a} .sq", {{scaleY: 0.8, scaleX: 1.15, transformOrigin: "50% 100%"}}, {{scaleY: 1, scaleX: 1, duration: 0.45, ease: "elastic.out(1.2, 0.4)"}}, {at(t_land)});')
        T(f'tl.fromTo("#name{v}", {{scale: 0, opacity: 1}}, {{scale: 1, duration: 0.4, ease: "back.out(2.2)"}}, {at(t_land)});')
        T(f'tl.to("#name{v}", {{scale: 0, opacity: 0, duration: 0.25, ease: "back.in(2)"}}, {at(L[2]["start"] - 0.3)});')
        bob(a, t_land + 0.5, L[4]["start"], 12)
        blink(a, t_land, L[4]["start"] + 1.5)
        # lines 2-3: the sound, here, there, everywhere
        T(f'tl.to("#world", {{scale: 1.07, transformOrigin: "{CX}px {FEET - 200}px", duration: 0.8, ease: "power2.inOut"}}, {at(L[2]["start"] - 0.4)});')
        T(f'tl.to("#world", {{scale: 1, duration: 0.8, ease: "power2.inOut"}}, {at(L[4]["start"] - 0.4)});')
        sounds = [w for ln in (L[2], L[3]) for w in ln["words"] if w["w"] == snd]
        runs = []   # sounds close together ("moo moo") share one bubble, which pulses on each
        for w in sounds:
            if runs and w["s"] - runs[-1][-1]["e"] < 0.7:
                runs[-1].append(w)
            else:
                runs.append([w])
        for w in sounds:
            mouth(a, w["s"], w["e"])
            T(f'tl.to("{a} .head", {{rotation: -8, svgOrigin: "300 200", duration: 0.12, yoyo: true, repeat: 1}}, {at(w["s"])});')
        for run in runs:
            s0, e0 = run[0]["s"], max(run[-1]["e"], run[-1]["s"] + 0.35) + 0.2
            T(f'tl.fromTo("#bub{v}", {{scale: 0, opacity: 1, rotation: -12}}, {{scale: 1, rotation: 0, duration: 0.2, ease: "back.out(3)", immediateRender: false}}, {at(s0 - 0.05)});')
            for w in run[1:]:
                T(f'tl.fromTo("#bub{v}", {{scale: 1.18}}, {{scale: 1, duration: 0.2, ease: "power2.out", immediateRender: false}}, {at(w["s"])});')
            T(f'tl.to("#bub{v}", {{scale: 0, opacity: 0, duration: 0.14}}, {at(e0)});')
        cue = [w for ln in (L[2], L[3]) for w in ln["words"] if w["w"] in ("here", "there", "everywhere")]
        shown = 0
        for w in cue:
            group = [shown] if w["w"] != "everywhere" else list(range(shown, 8))
            for m in group:
                x, y, sc = minis_pos[m]
                sel = f"#m{v}_{m}"
                T(f'tl.set("{sel}", {{left: {x}, top: {y - 190}, opacity: 1}}, {at(w["s"])});')
                T(f'tl.fromTo("{sel} > .bob", {{scale: 0}}, {{scale: {sc}, transformOrigin: "50% 95%", duration: 0.35, ease: "back.out(2.4)"}}, {at(w["s"] + 0.06 * (m - group[0]))});')
                T(f'tl.to("{sel} > .bob > .sq", {{y: -18, duration: {beat / 2:.3f}, yoyo: true, repeat: {max(1, int((L[4]["start"] - w["s"]) / beat) * 2 - 1)}, ease: "sine.inOut"}}, {at(w["s"] + 0.35)});')
                for s2 in sounds:
                    if s2["s"] > w["s"]:
                        mouth(sel, s2["s"], s2["e"])
            shown = group[-1] + 1
        for m in range(8):
            T(f'tl.to("#m{v}_{m} > .bob", {{scale: 0, duration: 0.25, ease: "back.in(2)"}}, {at(L[4]["start"] + 0.05 * m)});')
            T(f'tl.set("#m{v}_{m}", {{opacity: 0}}, {at(L[4]["start"] + 0.7)});')
        # line 4: the animal joins the others along the fence
        sx, sy = slots[v]
        T(f'tl.to("{a}", {{x: {sx - CX}, y: {sy - FEET}, scale: 0.36, duration: 1.3, ease: "power2.inOut"}}, {at(L[4]["start"] + 0.2)});')
        T(f'tl.to("{a} > .bob", {{y: -40, duration: 0.217, yoyo: true, repeat: 5, ease: "power1.out"}}, {at(L[4]["start"] + 0.2)});')
        bob(a, L[4]["start"] + 1.6, last + 0.5, 8, beat)

    # ------------------------------------------------------------- finale
    T(f'tl.to(".pos:not(.mini) > .bob", {{y: -50, duration: 0.25, yoyo: true, repeat: 7, ease: "power1.out", stagger: 0.08}}, {at(last + 0.6)});')
    T(f'tl.fromTo("#bye", {{scale: 0, opacity: 1}}, {{scale: 1, duration: 0.6, ease: "back.out(2)"}}, {at(last + 0.8)});')
    T(f'tl.to("#farmer .arm", {{rotation: -24, svgOrigin: "210 248", duration: 0.3, yoyo: true, repeat: 11, ease: "sine.inOut"}}, {at(last + 0.5)});')
    T(f'tl.to("#world, #bye", {{opacity: 0, duration: 0.8}}, {at(D - 0.9)});')

    audio = (f'<audio id="music" data-timeline-role="music" class="clip" data-start="0" data-duration="{D:.3f}" data-track-index="10" data-volume="1" '
             f'src="assets/song.wav"></audio>') if have_song else ""
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>Old MacDonald Had a Farm</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
@font-face {{ font-family: "Round"; src: url("assets/fonts/rounded.ttf"); font-weight: 700; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #6fc8ff; }}
#root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #6fc8ff; font-family: "Round", sans-serif; }}
.abs {{ position: absolute; }}
#world, #farm {{ position: absolute; inset: 0; }}
.pos svg {{ width: 100%; height: 100%; display: block; overflow: visible; }}
.bob, .sq {{ width: 100%; height: 100%; }}
#eieio {{ left: 0; right: 0; top: 40px; display: flex; justify-content: center; gap: 26px; z-index: 60; }}
.ltr {{ width: 132px; height: 132px; border-radius: 50%; color: #fff; font-size: 92px; font-weight: 700; display: flex;
        align-items: center; justify-content: center; border: 7px solid #fff; box-shadow: 0 8px 0 rgba(74,52,40,0.25);
        transform: scale(0); text-shadow: 0 4px 0 rgba(74,52,40,0.35); }}
.bubble {{ left: 820px; top: 330px; height: 170px; padding: 0 54px; white-space: nowrap; z-index: 55; background: #fff; border: 7px solid #4a3428;
           border-radius: 90px; display: flex; align-items: center; justify-content: center; transform: scale(0); transform-origin: 10% 100%; }}
.bubble::after {{ content: ""; position: absolute; left: 40px; bottom: -38px; border: 22px solid transparent; border-top: 30px solid #4a3428; }}
.bubble span {{ font-size: 96px; font-weight: 700; color: #e8410c; letter-spacing: 2px; }}
.namecard {{ left: {CX - 260}px; top: 300px; width: 520px; height: 150px; z-index: 55; background: #ffd23f; border: 8px solid #4a3428;
             border-radius: 40px; font-size: 110px; font-weight: 700; color: #4a3428; display: flex; align-items: center;
             justify-content: center; letter-spacing: 8px; transform: scale(0); box-shadow: 0 10px 0 rgba(74,52,40,0.25); }}
#title {{ left: 0; right: 0; top: 150px; text-align: center; z-index: 70; color: #fff; font-weight: 700; }}
#title .t1 {{ font-size: 170px; line-height: 1.05; }}
#title .t2 {{ font-size: 140px; line-height: 1.05; color: #ffd23f; }}
#title .tl {{ display: inline-block; -webkit-text-stroke: 10px #4a3428; paint-order: stroke fill; text-shadow: 0 10px 0 rgba(74,52,40,0.3); }}
#bye {{ left: 0; right: 0; top: 200px; text-align: center; z-index: 70; font-size: 150px; font-weight: 700; color: #ffd23f;
        -webkit-text-stroke: 10px #4a3428; paint-order: stroke fill; transform: scale(0); }}
.cap {{ left: 0; right: 0; bottom: 34px; display: flex; justify-content: center; z-index: 80; opacity: 0; }}
.pill {{ background: rgba(255,255,255,0.94); border: 6px solid #4a3428; border-radius: 60px; padding: 14px 44px;
         font-size: 60px; font-weight: 700; color: #4a3428; white-space: nowrap; }}
.w {{ display: inline-block; margin: 0 2px; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="1920" data-height="1080" data-fps="30">
{chr(10).join(html)}
{audio}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
tl.set({{}}, {{}}, {D:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>'''
    open(os.path.join(A, "index.html"), "w", encoding="utf-8").write(page)
    print(f"built: {D:.1f} s, song={'yes' if have_song else 'guessed timing'}, bpm={bpm}, tweens={len(js)}")


if __name__ == "__main__":
    main()
