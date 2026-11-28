"""Old MacDonald, version 2: rigged characters, a travelling camera across six farm places, parallax.

    python cartoon/oldmac2.py        # needs videos/oldmac/song.wav + words.json; writes videos/oldmac/anim2/index.html
"""
import json
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import art2  # noqa: E402
import world  # noqa: E402
import make_video as mv  # noqa: E402

F = os.path.join(ROOT, "videos", "oldmac")
A = os.path.join(F, "anim2")
ORDER = [("cow", "moo"), ("pig", "oink"), ("duck", "quack"), ("sheep", "baa"), ("horse", "neigh"), ("chicken", "cluck")]
LETTERS = [("E", "#ff5a5f"), ("I", "#ffb400"), ("E", "#3ec300"), ("I", "#1fa2ff"), ("O", "#a259ff")]
W = world.W
BIG = 480                    # featured animal size (px)
HOME = {0: (720, 915), 1: (700, 915), 2: (720, 960), 3: (720, 915), 4: (720, 915), 5: (720, 915)}  # feet per station
FARMER = (1470, 340, 567, 975)   # left, width, height, feet y
ROW_Y, ROW_S = 805, 0.36
rnd = random.Random(21)
js_lines = []


def J(o):
    return json.dumps(o)


def at(t):
    return f"{max(0.0, t):.3f}"


def T(s):
    js_lines.append(s)


def to(sel, props, t):
    T(f"tl.to({J(sel)}, {J(props)}, {at(t)});")


def fromto(sel, a, b, t):
    b = dict(b, immediateRender=False)
    T(f"tl.fromTo({J(sel)}, {J(a)}, {J(b)}, {at(t)});")


def setp(sel, props, t):
    T(f"tl.set({J(sel)}, {J(props)}, {at(t)});")


def main():
    lyrics = open(os.path.join(F, "lyrics.txt"), encoding="utf-8").read()
    lines = mv.lyric_lines(lyrics)
    song = os.path.join(F, "song.wav")
    words = json.load(open(os.path.join(F, "words.json"), encoding="utf-8"))
    D = mv.probe_duration(song)
    os.makedirs(os.path.join(A, "assets", "fonts"), exist_ok=True)
    shutil.copy(song, os.path.join(A, "assets", "song.wav"))
    for f in ("hyperframes.json", "package.json"):
        shutil.copy(os.path.join(F, "anim", f), os.path.join(A, f))
    shutil.copy(os.path.join(F, "anim", "assets", "fonts", "rounded.ttf"), os.path.join(A, "assets", "fonts", "rounded.ttf"))
    open(os.path.join(A, "meta.json"), "w").write('{"id":"oldmac2","name":"oldmac2","createdAt":"2026-11-28T17:00:00.000Z"}')
    timed = mv.time_lines(lines, words, D)
    assert len(timed) == 30
    bt = [x["time"] for x in json.load(open(os.path.join(F, "anim", "beats", "assets", "song.wav.json")))["beats"]]
    gaps = sorted(b - a for a, b in zip(bt, bt[1:]))
    beat, b0 = gaps[len(gaps) // 2], bt[0]
    first, last = timed[0]["start"], timed[-1]["end"]
    html = []
    H = html.append

    def on_beat(t):
        k = -(-(t - b0) // beat)
        return b0 + k * beat

    # ------------------------------------------------------------------ world layers
    ground_svg, spots = world.ground()
    H('<div id="world">')
    H(f'<div class="abs" id="L-sky">{world.sky()}</div>')
    for name, fn in (("clouds", world.clouds), ("far", world.far), ("near", world.near)):
        H(f'<div class="abs layer" id="L-{name}">{fn()}</div>')
    H(f'<div class="abs layer" id="L-ground">{ground_svg}</div>')
    H('<div class="abs" id="chars">')

    def char(cid, svg, w, h, feet_x, feet_y, z, hidden=True, foot=0.97):
        left, top = feet_x - w / 2, feet_y - h * foot
        H(f'<div class="abs pos" id="{cid}" style="left:{left:.0f}px;top:{top:.0f}px;width:{w}px;height:{h}px;z-index:{z};'
          f'{"opacity:0;" if hidden else ""}"><div class="bob"><div class="sq">{svg}</div></div></div>')

    fl, fw, fh, ffeet = FARMER
    char("farmer", art2.farmer(), fw, fh, fl + fw / 2, ffeet, 40, hidden=False, foot=0.99)
    for v, (name, snd) in enumerate(ORDER):
        hx, hy = HOME[v]
        char(f"a{v}", getattr(art2, name)(), BIG, BIG, hx, hy, 30 - v)
        for m in range(8):
            char(f"m{v}_{m}", getattr(art2, name)(), 200, 200, 100, 300, 26)
    # chicken's egg and chick
    H('<div class="abs fx" id="egg" style="left:560px;top:860px;width:70px;height:86px;z-index:31;opacity:0">'
      '<svg viewBox="0 0 70 86"><ellipse cx="35" cy="46" rx="30" ry="38" fill="#fff7ea" stroke="#4a3428" stroke-width="5"/></svg></div>')
    H('<div class="abs fx" id="chick" style="left:545px;top:850px;width:100px;height:100px;z-index:32;opacity:0">'
      '<svg viewBox="0 0 100 100"><circle cx="50" cy="58" r="36" fill="url(#gye)" stroke="#4a3428" stroke-width="5"/>'
      '<circle cx="38" cy="50" r="6" fill="#2a1a10"/><circle cx="62" cy="50" r="6" fill="#2a1a10"/>'
      '<path d="M44 62 l6 8 l6 -8z" fill="#ff9a2e" stroke="#4a3428" stroke-width="3"/>'
      '<path d="M50 22 q-4 -12 6 -14 q-2 8 2 12" fill="#ffd83d" stroke="#4a3428" stroke-width="3"/></svg></div>')
    H('</div>')   # chars
    # particles
    H('<div class="abs" id="fx">')
    for i in range(14):
        H(f'<div class="abs note" id="n{i}">{"♪" if i % 2 else "♫"}</div>')
    for v in range(6):
        for i in range(10):
            H(f'<div class="abs star" id="st{v}_{i}"></div>')
    for i in range(14):
        H(f'<div class="abs drop" id="d{i}"></div>')
    for i in range(5):
        H(f'<div class="abs ripple" id="r{i}"></div>')
    wl = HOME[2][1] - 106          # duck's waterline
    pcx, pcy = spots[2]["pond"]
    H(f'<div class="abs" id="waterfront"><svg viewBox="0 0 1920 1080" width="1920" height="1080">'
      f'<defs><clipPath id="wcut"><rect x="0" y="{wl}" width="1920" height="400"/></clipPath>'
      f'<clipPath id="wpond"><ellipse cx="{pcx}" cy="{pcy}" rx="556" ry="121"/></clipPath></defs>'
      f'<g clip-path="url(#wcut)"><ellipse cx="{pcx}" cy="{pcy}" rx="560" ry="125" fill="url(#gwater)" stroke="#4a3428" stroke-width="6"/></g>'
      f'<g clip-path="url(#wpond)"><path d="M{pcx - 600} {wl} ' + " ".join(f"q20 -12 40 0" for _ in range(30)) +
      f'" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.9"/></g></svg></div>')
    ml = HOME[1][1] - 26           # mud line on the pig's legs
    mcx, mcy = spots[1]["mud"]
    H(f'<div class="abs" id="mudfront"><svg viewBox="0 0 1920 1080" width="1920" height="1080">'
      f'<defs><clipPath id="mcut"><rect x="0" y="{ml}" width="1920" height="400"/></clipPath></defs>'
      f'<g clip-path="url(#mcut)"><ellipse cx="{mcx}" cy="{mcy}" rx="340" ry="70" fill="url(#gmud)" stroke="#4a3428" stroke-width="6"/>'
      f'<ellipse cx="{mcx - 90}" cy="{mcy - 14}" rx="90" ry="16" fill="#b78457" opacity="0.7"/></g></svg></div>')
    for i in range(40):
        c = ["#ff5a5f", "#ffb400", "#3ec300", "#1fa2ff", "#a259ff", "#ff7ac6"][i % 6]
        H(f'<div class="abs confetti" id="c{i}" style="background:{c};left:{rnd.randint(40, 1880)}px"></div>')
    H('</div>')
    H(f'<div class="abs layer" id="L-front">{world.front()}</div>')
    H('</div>')   # world

    # overlays
    H('<div class="abs" id="eieio">' + "".join(f'<div class="ltr" id="l{i}" style="background:{c}">{ch}</div>'
                                            for i, (ch, c) in enumerate(LETTERS)) + '</div>')
    for v, (name, snd) in enumerate(ORDER):
        H(f'<div class="abs bubble" id="bub{v}"><span>{snd.upper()}!</span></div>')
        H(f'<div class="abs namecard" id="name{v}">{name.upper()}</div>')
    H('<div class="abs" id="title"><div class="t1">' + "".join(f'<span class="tl">{c if c != " " else "&nbsp;"}</span>' for c in "Old MacDonald")
      + '</div><div class="t2">' + "".join(f'<span class="tl">{c if c != " " else "&nbsp;"}</span>' for c in "Had a Farm") + '</div></div>')
    H('<div class="abs" id="bye">Bye bye, friends!</div>')
    for i, ln in enumerate(timed):
        ws = "".join(f'<span class="w" id="w{i}_{k}">{w}</span> ' for k, w in enumerate(ln["line"].split()))
        H(f'<div class="abs cap" id="cap{i}"><div class="pill">{ws}</div></div>')

    # ------------------------------------------------------------------ helpers
    def legs_walk(sel, t0, dur, step=None, amp=22):
        step = step or beat / 2
        n = max(1, int(dur / step))
        fromto(f"{sel} .leg-a", {"rotation": -amp, "transformOrigin": "50% 0%"},
               {"rotation": amp, "duration": step, "yoyo": True, "repeat": n - 1, "ease": "sine.inOut"}, t0)
        fromto(f"{sel} .leg-b", {"rotation": amp, "transformOrigin": "50% 0%"},
               {"rotation": -amp, "duration": step, "yoyo": True, "repeat": n - 1, "ease": "sine.inOut"}, t0)
        to(f"{sel} .leg-a, {sel} .leg-b", {"rotation": 0, "duration": 0.12}, t0 + n * step)
        fromto(f"{sel} > .bob", {"y": 0}, {"y": -12, "duration": step / 2, "yoyo": True, "repeat": n * 2 - 1, "ease": "sine.out"}, t0)

    def bob(sel, t0, t1, amp=12):
        t0 = on_beat(t0)
        n = int((t1 - t0) / beat)
        if n >= 1:
            fromto(f"{sel} > .bob", {"y": 0}, {"y": -amp, "duration": beat / 2, "yoyo": True, "repeat": n * 2 - 1, "ease": "sine.inOut"}, t0)

    def blink(sel, t0, t1):
        t = t0 + rnd.uniform(0.3, 1.5)
        while t < t1 - 0.3:
            setp(f"{sel} .lid", {"opacity": 1}, t)
            setp(f"{sel} .lid", {"opacity": 0}, t + 0.11)
            t += rnd.uniform(2.4, 4.6)

    def mouth(sel, s, e, shape="m-open", bill=False):
        e = max(e, s + 0.16)
        if bill:
            px, py = art2.PIVOTS[bill]["bill-bot"]
            fromto(f"{sel} .bill-bot", {"rotation": 0}, {"rotation": 24, "svgOrigin": f"{px} {py}", "duration": 0.07}, s)
            to(f"{sel} .bill-bot", {"rotation": 0, "duration": 0.1}, e)
            return
        setp(f"{sel} .{shape}", {"opacity": 1}, s)
        setp(f"{sel} .m-shut", {"opacity": 0}, s)
        setp(f"{sel} .{shape}", {"opacity": 0}, e)
        setp(f"{sel} .m-shut", {"opacity": 1}, e)

    def part_rot(sel, who, part, deg, dur, reps, t, ease="sine.inOut"):
        px, py = art2.PIVOTS[who][part]
        fromto(f"{sel} .{part}", {"rotation": 0}, {"rotation": deg, "svgOrigin": f"{px} {py}", "duration": dur, "yoyo": True,
                                                    "repeat": reps, "ease": ease}, t)

    def move(sel, x, y, scale, dur, t, ease="power1.inOut"):
        to(sel, {"x": x, "y": y, "scale": scale, "duration": dur, "ease": ease}, t)

    BILL = {"duck", "chicken"}

    def bill_fix():   # bill pivots: rotate around the beak hinge
        pass

    # ------------------------------------------------------------------ static setup
    setp(".lid", {"opacity": 0}, 0)
    setp(".ltr, .bubble, .namecard, #bye", {"scale": 0}, 0)
    setp(".pos", {"transformOrigin": "50% 97%"}, 0)
    for k in ("clouds", "far", "near"):
        pass
    to("#L-clouds", {"x": -260, "duration": D, "ease": "none"}, 0)

    # farmer: walks in during the intro, blinks, sings
    fromto("#farmer", {"x": 600}, {"x": 0, "duration": 3.0, "ease": "power1.out"}, 0.3)
    legs_walk("#farmer", 0.3, 3.0)
    blink("#farmer", 0, D)
    part_rot("#farmer", "farmer", "arm-r", -150, 0.01, 0, 3.4)
    to("#farmer .arm-r", {"rotation": -125, "duration": 0.3, "yoyo": True, "repeat": 5, "ease": "sine.inOut"}, 3.5)
    to("#farmer .arm-r", {"rotation": 0, "duration": 0.4}, 5.4)

    # title
    fromto("#title .tl", {"y": -300, "opacity": 0}, {"y": 0, "opacity": 1, "duration": 0.6, "ease": "bounce.out", "stagger": 0.06}, 0.3)
    to("#title", {"scale": 0.2, "opacity": 0, "duration": 0.45, "ease": "back.in(1.6)"}, max(2.0, first - 0.6))

    # captions (karaoke)
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
            wt = ln["words"][min(k, len(ln["words"]) - 1)]
            to(f"#w{i}_{j}", {"color": "#ff6a00", "duration": 0.08}, wt["s"])
            k += len(tk)

    note_i = [0]

    def notes(ln):   # music notes float up from the farmer while he sings
        for w in ln["words"][::3]:
            i = note_i[0] % 14
            note_i[0] += 1
            x0 = fl + 120 + rnd.randint(-60, 60)
            setp(f"#n{i}", {"left": x0, "top": 470, "opacity": 0, "x": 0, "y": 0, "rotation": 0}, w["s"] - 0.01)
            to(f"#n{i}", {"opacity": 1, "duration": 0.2}, w["s"])
            to(f"#n{i}", {"y": -220, "x": rnd.randint(-80, 40), "rotation": rnd.randint(-30, 30), "duration": 1.6, "ease": "sine.out"}, w["s"])
            to(f"#n{i}", {"opacity": 0, "duration": 0.4}, w["s"] + 1.2)

    def stars(v, x, y, t):
        for i in range(10):
            ang = i / 10 * 6.283
            import math
            setp(f"#st{v}_{i}", {"left": x, "top": y, "opacity": 1, "x": 0, "y": 0, "scale": 0.4}, t)
            to(f"#st{v}_{i}", {"x": 260 * math.cos(ang), "y": 170 * math.sin(ang), "scale": 1, "rotation": 180, "duration": 0.7, "ease": "power2.out"}, t)
            to(f"#st{v}_{i}", {"opacity": 0, "duration": 0.3}, t + 0.5)

    drop_i = [0]

    def splash(x, y, t, n=7, col="#7a4a26"):
        import math
        for k in range(n):
            i = drop_i[0] % 14
            drop_i[0] += 1
            ang = 3.14 + (k + 0.5) / n * 3.14
            setp(f"#d{i}", {"left": x, "top": y, "opacity": 1, "x": 0, "y": 0, "scale": 1, "backgroundColor": col}, t)
            to(f"#d{i}", {"x": 190 * math.cos(ang), "y": 130 * math.sin(ang), "duration": 0.35, "ease": "power2.out"}, t)
            to(f"#d{i}", {"y": 40, "opacity": 0, "duration": 0.35, "ease": "power2.in"}, t + 0.35)

    def eieio(ln, nxt_start, chorus):
        ws = ln["words"][-5:]
        for i, w in enumerate(ws):
            fromto(f"#l{i}", {"scale": 0, "rotation": -30, "opacity": 1}, {"scale": 1, "rotation": 0, "duration": 0.35, "ease": "back.out(2.5)"}, w["s"])
            for sel in chorus:
                mouth(sel, w["s"], w["e"] - 0.03)
        end = min(nxt_start - 0.1, ws[-1]["e"] + 0.7)
        to("#eieio .ltr", {"y": -14, "duration": 0.12, "yoyo": True, "repeat": 1, "stagger": 0.05}, ws[-1]["e"])
        to("#eieio .ltr", {"scale": 0, "opacity": 0, "duration": 0.2, "ease": "back.in(2)", "stagger": 0.03}, end - 0.2)
        # farmer: both arms up and a little dance
        part_rot("#farmer", "farmer", "arm-l", 130, 0.25, 1, ws[0]["s"] - 0.1)
        part_rot("#farmer", "farmer", "arm-r", -130, 0.25, 1, ws[0]["s"] - 0.1)
        to("#farmer > .bob > .sq", {"rotation": 5, "transformOrigin": "50% 100%", "duration": beat / 2, "yoyo": True, "repeat": 3,
                                    "ease": "sine.inOut"}, ws[0]["s"])

    minis_pos = [(300, 820, 1.0), (1150, 800, 1.0), (110, 880, 0.9), (1270, 660, 0.8),
                 (520, 300, 0.75), (900, 230, 0.75), (1270, 350, 0.7), (180, 400, 0.7)]

    in_row = []        # animals already in the back row
    row_free_from = {}  # animal -> time it joined
    pans = []
    for v, (name, snd) in enumerate(ORDER):
        L = timed[v * 5: v * 5 + 5]
        a = f"#a{v}"
        hx, hy = HOME[v]
        bill = name if name in BILL else None
        # ---------------- travel to this animal's place during line 0
        if v > 0:
            p0 = L[0]["start"] - 0.2
            P = max(2.6, min(4.6, L[0]["end"] - p0 - 0.2))
            pans.append((p0 - 0.6, p0 + P + 0.9))
            move("#farmer", -260, 0, 1, 0.6, p0 - 0.6)
            legs_walk("#farmer", p0 - 0.6, P + 0.6)
            for i, u in enumerate(in_row):
                ux, uy = HOME[u]
                mx, my = 1210 - 190 * (len(in_row) - i), 975
                move(f"#a{u}", mx - ux, my - uy, 0.46, 0.6, p0 - 0.6)
                legs_walk(f"#a{u}", p0 - 0.6, P + 0.6, amp=26)
            for k, sp in world.SPEED.items():
                if k != "clouds":
                    to(f"#L-{k}", {"x": -v * W * sp, "duration": P, "ease": "power1.inOut"}, p0)
            ret = p0 + P + 0.05
            move("#farmer", 0, 0, 1, 0.7, ret)
            legs_walk("#farmer", ret, 0.7)
            for i, u in enumerate(in_row):
                ux, uy = HOME[u]
                sx, sy = 975 + u * 86, ROW_Y
                move(f"#a{u}", sx - ux, sy - uy, ROW_S, 0.8, ret + 0.05 * i)
                legs_walk(f"#a{u}", ret + 0.05 * i, 0.8, amp=26)
        sing_t = [L[0], L[4]]
        for ln in sing_t:
            for w in ln["words"]:
                mouth("#farmer", w["s"], w["e"] - 0.04)
            notes(ln)
        part_rot("#farmer", "farmer", "arm-r", -135, beat, 3, L[4]["start"])
        chorus = [f"#a{u}" for u in in_row]
        for idx in (0, 1, 4):
            ln = L[idx]
            nx = timed[v * 5 + idx + 1]["start"] if v * 5 + idx + 1 < 30 else last + 2
            eieio(ln, nx, chorus if idx != 1 else chorus)

        # ---------------- the animal arrives (line 1), each in its own way
        name_w = next((w for w in L[1]["words"] if w["w"] in (name, name + "s")), None)
        t_land = name_w["s"] if name_w else L[1]["start"] + 1.6
        t_in = max(L[1]["start"] - 0.8, (pans[-1][1] if pans else 0) - 0.2)
        dur = max(1.0, t_land - t_in)
        if name == "cow":           # out of the barn
            dx, dy = 262 - hx, 878 - hy
            setp(a, {"opacity": 1, "x": dx, "y": dy, "scale": 0.35}, t_in)
            move(a, 0, 0, 1, dur, t_in)
            legs_walk(a, t_in, dur)
        elif name == "pig":         # runs in and jumps into the mud
            setp(a, {"opacity": 1, "x": -900, "y": 0, "scale": 1}, t_in)
            to(a, {"x": -260, "duration": dur * 0.7, "ease": "none"}, t_in)
            legs_walk(a, t_in, dur * 0.7, step=0.16, amp=30)
            to(a, {"x": 0, "duration": dur * 0.3, "ease": "power1.out"}, t_in + dur * 0.7)
            to(f"{a} > .bob", {"y": -160, "duration": dur * 0.15, "yoyo": True, "repeat": 1, "ease": "power2.out"}, t_in + dur * 0.7)
            splash(hx, hy - 40, t_land, 9)
            setp("#mudfront", {"opacity": 1}, t_land - 0.05)
            setp("#mudfront", {"opacity": 0}, L[4]["start"] + 0.3)
        elif name == "duck":        # swims in across the pond
            setp(a, {"opacity": 1, "x": -1000, "y": 0, "scale": 1}, t_in)
            to(a, {"x": 0, "duration": dur, "ease": "power2.out"}, t_in)
            part_rot(a, "duck", "wing", -25, 0.18, int(dur / 0.18) // 2 * 2 + 1, t_in)
            to(f"{a} > .bob", {"y": -8, "duration": 0.5, "yoyo": True, "repeat": int((L[4]["start"] - t_in) / 0.5), "ease": "sine.inOut"}, t_in)
        elif name == "sheep":       # bounces down from the hilltop
            hx0, hy0 = spots[3]["hilltop"]
            setp(a, {"opacity": 1, "x": hx0 - hx, "y": hy0 - hy, "scale": 0.45}, t_in)
            to(a, {"x": 0, "scale": 1, "duration": dur, "ease": "power1.inOut"}, t_in)
            to(a, {"y": 0, "duration": dur, "ease": "power1.in"}, t_in)
            hops = max(2, int(dur / 0.45))
            fromto(f"{a} > .bob", {"y": 0}, {"y": -90, "duration": dur / hops / 2, "yoyo": True, "repeat": hops * 2 - 1, "ease": "power1.out"}, t_in)
        elif name == "horse":       # gallops in and rears up
            setp(a, {"opacity": 1, "x": -1100, "y": 0, "scale": 1}, t_in)
            to(a, {"x": 0, "duration": dur, "ease": "power2.out"}, t_in)
            legs_walk(a, t_in, dur, step=0.13, amp=34)
            fromto(f"{a} > .bob > .sq", {"rotation": 0}, {"rotation": -14, "transformOrigin": "25% 100%", "duration": 0.3, "yoyo": True,
                                                          "repeat": 1, "ease": "power2.out"}, t_land)
            part_rot(a, "horse", "mane", -10, 0.2, 5, t_in)
        elif name == "chicken":     # walks down the coop ramp
            rx, ry = spots[5]["ramp"]
            setp(a, {"opacity": 1, "x": 230 - hx, "y": 650 - hy, "scale": 0.4}, t_in)
            to(a, {"x": rx - hx, "y": ry - hy, "scale": 0.6, "duration": dur * 0.5, "ease": "none"}, t_in)
            to(a, {"x": 0, "y": 0, "scale": 1, "duration": dur * 0.5, "ease": "power1.out"}, t_in + dur * 0.5)
            legs_walk(a, t_in, dur, step=0.16, amp=26)
        fromto(f"{a} .sq", {"scaleY": 0.82, "scaleX": 1.14, "transformOrigin": "50% 100%"},
               {"scaleY": 1, "scaleX": 1, "duration": 0.5, "ease": "elastic.out(1.2, 0.4)"}, t_land)
        fromto(f"#name{v}", {"scale": 0, "opacity": 1}, {"scale": 1, "duration": 0.4, "ease": "back.out(2.2)"}, t_land)
        stars(v, hx, 380, t_land)
        to(f"#name{v}", {"scale": 0, "opacity": 0, "duration": 0.25, "ease": "back.in(2)"}, L[2]["start"] - 0.3)
        if name == "duck":
            setp("#waterfront", {"opacity": 1}, t_in)
            setp("#waterfront", {"opacity": 0}, L[4]["start"] + 1.4)
            for i in range(5):
                setp(f"#r{i}", {"left": hx - 120, "top": hy - 135}, t_land - 0.5)
                fromto(f"#r{i}", {"scale": 0.3, "opacity": 0.9},
                       {"scale": 1.6, "opacity": 0, "duration": 1.6, "ease": "power1.out", "repeat": int((L[4]["start"] - t_land) / 2),
                        "repeatDelay": 0.4}, t_land + i * 0.4)
        # idle life: blink, tail wag, ear twitch
        stay = L[4]["start"]
        blink(a, t_land, D)
        if "tail" in art2.PIVOTS[name]:
            part_rot(a, name, "tail", 16, beat / 2, int((stay - t_land) / (beat / 2)), t_land)
        if name != "duck":
            bob(a, t_land + 0.6, L[2]["start"], 8)

        # ---------------- the sound (lines 2-3): here, there, everywhere
        to("#world", {"scale": 1.07, "transformOrigin": f"{hx}px {hy - 220}px", "duration": 0.8, "ease": "power2.inOut"}, L[2]["start"] - 0.4)
        to("#world", {"scale": 1, "duration": 0.8, "ease": "power2.inOut"}, L[4]["start"] - 0.4)
        sounds = [w for ln in (L[2], L[3]) for w in ln["words"] if mv.tokens(w["w"])[:1] == [snd]]
        runs = []
        for w in sounds:
            if runs and w["s"] - runs[-1][-1]["e"] < 0.7:
                runs[-1].append(w)
            else:
                runs.append([w])
        shape = "m-o" if snd in ("moo", "oink") else "m-open"
        for w in sounds:
            mouth(a, w["s"], w["e"], shape, bill)
            if "head" in art2.PIVOTS[name]:
                part_rot(a, name, "head", -9, 0.12, 1, w["s"])
            if "wing" in art2.PIVOTS[name]:
                part_rot(a, name, "wing", -35, 0.1, 3, w["s"])
            if name == "sheep":
                fromto(f"{a} > .bob", {"y": 0}, {"y": -50, "duration": 0.16, "yoyo": True, "repeat": 1, "ease": "power2.out"}, w["s"])
            if name == "pig":
                splash(hx, hy - 30, w["s"], 4)
            if "ear-l" in art2.PIVOTS[name]:
                part_rot(a, name, "ear-l", -14, 0.1, 1, w["s"])
                part_rot(a, name, "ear-r", 14, 0.1, 1, w["s"])
        for run in runs:
            s0, e0 = run[0]["s"], max(run[-1]["e"], run[-1]["s"] + 0.35) + 0.2
            fromto(f"#bub{v}", {"scale": 0, "opacity": 1, "rotation": -12}, {"scale": 1, "rotation": 0, "duration": 0.2, "ease": "back.out(3)"}, s0 - 0.05)
            for w in run[1:]:
                fromto(f"#bub{v}", {"scale": 1.18}, {"scale": 1, "duration": 0.2, "ease": "power2.out"}, w["s"])
            to(f"#bub{v}", {"scale": 0, "opacity": 0, "duration": 0.14}, e0)
            if name == "horse":
                fromto(f"{a} > .bob > .sq", {"rotation": 0}, {"rotation": -10, "transformOrigin": "25% 100%", "duration": 0.25,
                                                              "yoyo": True, "repeat": 1}, s0)
        cue = [w for ln in (L[2], L[3]) for w in ln["words"] if mv.tokens(w["w"])[:1] and mv.tokens(w["w"])[0] in ("here", "there", "everywhere")]
        shown = 0
        for w in cue:
            if shown >= 8:
                break
            group = [shown] if w["w"].lower().strip(",.") != "everywhere" else list(range(shown, 8))
            for m in group:
                x, y, sc = minis_pos[m]
                sel = f"#m{v}_{m}"
                setp(sel, {"left": x - 100, "top": y - 194, "opacity": 1}, w["s"])
                fromto(f"{sel} > .bob", {"scale": 0}, {"scale": sc, "transformOrigin": "50% 97%", "duration": 0.35, "ease": "back.out(2.4)"},
                       w["s"] + 0.06 * (m - group[0]))
                n = max(1, int((L[4]["start"] - w["s"]) / beat))
                fromto(f"{sel} > .bob > .sq", {"y": 0}, {"y": -18, "duration": beat / 2, "yoyo": True, "repeat": n * 2 - 1, "ease": "sine.inOut"}, w["s"] + 0.35)
                for s2 in sounds:
                    if s2["s"] > w["s"]:
                        mouth(sel, s2["s"], s2["e"], shape, bill)
            shown = group[-1] + 1
        for m in range(8):
            to(f"#m{v}_{m} > .bob", {"scale": 0, "duration": 0.25, "ease": "back.in(2)"}, L[4]["start"] + 0.05 * m)
            setp(f"#m{v}_{m}", {"opacity": 0}, L[4]["start"] + 0.7)
        if name == "chicken":       # she lays an egg, and a chick hatches
            te = L[3]["end"] - 0.2
            fromto("#egg", {"opacity": 1, "scale": 0, "y": -40}, {"opacity": 1, "scale": 1, "y": 0, "duration": 0.4, "ease": "bounce.out"}, te)
            to("#egg", {"rotation": 12, "duration": 0.1, "yoyo": True, "repeat": 5}, te + 0.6)
            setp("#egg", {"opacity": 0}, te + 1.3)
            fromto("#chick", {"opacity": 1, "scale": 0}, {"opacity": 1, "scale": 1, "duration": 0.45, "ease": "back.out(3)"}, te + 1.3)
            stars(v, 595, 880, te + 1.3)
            fromto("#chick", {"y": 0}, {"y": -20, "duration": beat / 2, "yoyo": True, "repeat": int((D - te) / beat) * 2, "ease": "sine.inOut"}, te + 1.8)

        # ---------------- line 4: the animal joins the back row
        sx, sy = 975 + v * 86, ROW_Y
        t_go = L[4]["start"] + 0.2
        move(a, sx - hx, sy - hy, ROW_S, 1.3, t_go, "power2.inOut")
        legs_walk(a, t_go, 1.3, amp=26)
        in_row.append(v)
        row_free_from[v] = t_go + 1.4

    # beat bounce for back-row animals between their walks
    busy = pans + [(last + 0.5, D)]
    for v in range(6):
        t = row_free_from[v]
        for p0, p1 in sorted(busy):
            if p1 <= t:
                continue
            if p0 > t:
                bob(f"#a{v}", t, p0 - 0.1, 8)
            t = max(t, p1)
        if t < last + 0.4:
            bob(f"#a{v}", t, last + 0.4, 8)

    # ------------------------------------------------------------------ finale
    to(".pos:not(.mini) > .bob", {"y": -60, "duration": 0.26, "yoyo": True, "repeat": 9, "ease": "power1.out", "stagger": 0.07}, last + 0.6)
    fromto("#bye", {"scale": 0, "opacity": 1}, {"scale": 1, "duration": 0.6, "ease": "back.out(2)"}, last + 0.8)
    part_rot("#farmer", "farmer", "arm-r", -140, 0.3, 11, last + 0.5)
    part_rot("#farmer", "farmer", "arm-l", 140, 0.3, 11, last + 0.5)
    for i in range(40):
        fromto(f"#c{i}", {"y": -60, "opacity": 1, "rotation": 0},
               {"y": 1200, "rotation": rnd.randint(200, 720), "x": rnd.randint(-120, 120), "duration": rnd.uniform(2.4, 3.6), "ease": "none"},
               last + 0.7 + rnd.uniform(0, 1.2))
    to("#world, #bye", {"opacity": 0, "duration": 0.8}, D - 0.9)

    css = open(os.path.join(HERE, "oldmac2.css"), encoding="utf-8").read()
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>Old MacDonald Had a Farm</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
{css}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="1920" data-height="1080" data-fps="30">
{art2.DEFS}{world.DEFS}
{chr(10).join(html)}
<audio id="music" data-timeline-role="music" class="clip" data-start="0" data-duration="{D:.3f}" data-track-index="10" data-volume="1" src="assets/song.wav"></audio>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js_lines)}
tl.set({{}}, {{}}, {D:.3f});
window.__timelines["main"] = tl;
</script>
</body>
</html>'''
    open(os.path.join(A, "index.html"), "w", encoding="utf-8").write(page)
    print(f"built: {D:.1f} s, beat {beat:.3f} s, tweens={len(js_lines)}")


if __name__ == "__main__":
    main()
