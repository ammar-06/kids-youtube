"""Animate the 2D cast with GSAP: one Stage collects characters, scenery and tweens, then writes a Hyperframes page.

Every move is a timeline tween at a fixed time, so any frame can be seeked (Hyperframes renders deterministically).
Characters sit in a wrapper <div id="c-NAME"> (whole-body moves: x/y/scale/rotation) holding their rigged SVG.
"""
import json
import math
import os
import random
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animals2d, family2d, mo2d, people2d  # noqa: E402

# name -> (svg maker, prefix, viewBox w, h, real height in "units", part pivots)
CAST = {
    "mo": (mo2d.mo_svg, "mo", 400, 640, 0.92, mo2d.PIVOTS),
    "zara": (people2d.zara, "zr", 400, 640, 0.95, people2d.PIVOTS["zara"]),
    "mom": (people2d.mom, "mm", 400, 900, 1.62, people2d.PIVOTS["mom"]),
    "dad": (people2d.dad, "dd", 400, 900, 1.72, people2d.PIVOTS["dad"]),
    "grandpa": (family2d.grandpa, "gp", 480, 900, 1.6, family2d.PIVOTS["grandpa"]),
    "biscuit": (family2d.biscuit, "bs", 420, 640, 0.78, family2d.PIVOTS["biscuit"]),
}
for _n, _h in (("cow", 0.95), ("pig", 0.72), ("duck", 0.55), ("sheep", 0.78), ("horse", 1.05), ("chicken", 0.55)):
    _p = animals2d.PREFIX[_n]
    CAST[_n] = (animals2d.ANIMALS[_n], _p, 400, 420, _h, {f"{_p}-head": animals2d.HEAD_PIVOT[_n]})

HUMAN = {"mo", "zara", "mom", "dad", "grandpa", "biscuit"}
NAMES = {"mo": "Mo", "zara": "Zara", "mom": "Mom", "dad": "Dad", "grandpa": "Grandpa", "biscuit": "Biscuit"}


class Stage:
    def __init__(self, duration, unit_px=430, ground_y=930):
        self.D = duration
        self.unit = unit_px          # screen px for 1 unit of character height
        self.ground = ground_y
        self.js = []
        self.html = []
        self.ui = []
        self.chars = {}
        self.rnd = random.Random(5)

    # ------------------------------------------------------------------ low level
    def tw(self, sel, props, t, kind="to"):
        if t < 0:
            t = 0
        self.js.append(f"tl.{kind}({json.dumps(sel)}, {json.dumps(props)}, {t:.3f});")

    def set(self, sel, props, t):
        self.tw(sel, props, t, "set")

    def part(self, name, part):
        return f"#c-{name} .{CAST[name][1]}-{part}"

    def rot(self, name, part, ang, t, dur, ease="sine.inOut"):
        p = CAST[name][1]
        key = f"{p}-{part}"
        piv = CAST[name][5].get(key)
        if piv is None:
            return
        self.tw(f"#c-{name} .{key}", {"rotation": ang, "svgOrigin": f"{piv[0]} {piv[1]}", "duration": dur, "ease": ease}, t)

    # ------------------------------------------------------------------ setup
    def add(self, name, x, scale=1.0, z=10, flip=False, hidden=False, y=0):
        """x = screen x of the character's centre; feet on the ground line."""
        mk, p, vw, vh, units, piv = CAST[name]
        h = units * self.unit * scale
        w = h * vw / vh
        style = (f"position:absolute;left:{x - w / 2:.0f}px;top:{self.ground - h + y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;z-index:{z};"
                 + ("opacity:0;" if hidden else ""))
        self.html.append(f'<div class="char" id="c-{name}" style="{style}">{mk()}</div>')
        self.chars[name] = dict(x=x, w=w, h=h)
        if flip:
            self.set(f"#c-{name}", {"scaleX": -1}, 0)
        return self

    def scenery(self, svg):
        self.html.insert(0, svg)

    def overlay(self, html, ui=False):
        (self.ui if ui else self.html).append(html)

    # ------------------------------------------------------------------ whole-body moves
    def enter(self, name, t, frm="left", dur=1.6, walk=True):
        c = self.chars[name]
        dx = -1300 if frm == "left" else 1300
        self.set(f"#c-{name}", {"opacity": 1, "x": dx}, max(0, t - 0.01))
        self.tw(f"#c-{name}", {"x": 0, "duration": dur, "ease": "power1.out"}, t)
        if walk:
            self.walk_legs(name, t, t + dur)

    def exit(self, name, t, to="right", dur=1.4):
        dx = 1400 if to == "right" else -1400
        self.tw(f"#c-{name}", {"x": dx, "duration": dur, "ease": "power1.in"}, t)
        self.walk_legs(name, t, t + dur)

    def pop_in(self, name, t):
        self.set(f"#c-{name}", {"opacity": 1, "scale": 0, "transformOrigin": "50% 100%"}, t)
        self.tw(f"#c-{name}", {"scale": 1, "duration": 0.45, "ease": "back.out(2.2)"}, t)

    def move_to(self, name, x, t, dur=1.0):
        self.tw(f"#c-{name}", {"x": x - self.chars[name]["x"], "duration": dur, "ease": "power1.inOut"}, t)
        self.walk_legs(name, t, t + dur)

    def bob(self, name, t0, t1, beat=0.55, amp=8):
        i = 0
        t = t0
        while t < t1 - 0.05:
            self.tw(f"#c-{name}", {"y": -amp if i % 2 == 0 else 0, "duration": beat, "ease": "sine.inOut"}, t)
            t += beat
            i += 1
        self.tw(f"#c-{name}", {"y": 0, "duration": 0.2}, t1)

    def walk_legs(self, name, t0, t1, step=0.28):
        p = CAST[name][1]
        if name in HUMAN:
            n = 0
            t = t0
            while t < t1 - 0.05:
                s = 1 if n % 2 == 0 else -1
                self.rot(name, "leg-r", 14 * s, t, step)
                self.rot(name, "leg-l", -14 * s, t, step)
                self.rot(name, "arm-r", -10 * s, t, step)
                self.rot(name, "arm-l", -10 * s, t, step)
                t += step
                n += 1
            for prt in ("leg-r", "leg-l", "arm-r", "arm-l"):
                self.rot(name, prt, 0, t1, 0.2)
        else:   # animals: alternate leg sets lift, body rocks
            n = 0
            t = t0
            while t < t1 - 0.05:
                a, b = ("leg-a", "leg-b") if n % 2 == 0 else ("leg-b", "leg-a")
                self.tw(f"#c-{name} .{p}-{a}", {"y": -16, "duration": step / 2, "ease": "sine.out"}, t)
                self.tw(f"#c-{name} .{p}-{a}", {"y": 0, "duration": step / 2, "ease": "sine.in"}, t + step / 2)
                self.tw(f"#c-{name} svg", {"rotation": 2.5 if n % 2 == 0 else -2.5, "transformOrigin": "50% 100%", "duration": step, "ease": "sine.inOut"}, t)
                t += step
                n += 1
            self.tw(f"#c-{name} svg", {"rotation": 0, "duration": 0.2}, t1)

    def jump(self, name, t, height=160, arms=True):
        sel = f"#c-{name} svg"
        self.tw(sel, {"scaleY": 0.88, "scaleX": 1.07, "transformOrigin": "50% 100%", "duration": 0.13}, t)
        self.tw(sel, {"scaleY": 1.06, "scaleX": 0.96, "y": -height, "duration": 0.33, "ease": "power2.out"}, t + 0.13)
        self.tw(sel, {"scaleY": 1, "scaleX": 1, "y": 0, "duration": 0.3, "ease": "power2.in"}, t + 0.46)
        self.tw(sel, {"scaleY": 0.9, "scaleX": 1.06, "duration": 0.08}, t + 0.76)
        self.tw(sel, {"scaleY": 1, "scaleX": 1, "duration": 0.22, "ease": "back.out(3)"}, t + 0.84)
        if arms and name in HUMAN:
            self.rot(name, "arm-r", 140, t + 0.13, 0.25)
            self.rot(name, "arm-l", -140, t + 0.13, 0.25)
            self.rot(name, "arm-r", 0, t + 0.6, 0.3)
            self.rot(name, "arm-l", 0, t + 0.6, 0.3)

    def hop(self, name, t, height=90, dur=0.48):
        sel = f"#c-{name} svg"
        q = dur / 4
        self.tw(sel, {"scaleY": 0.9, "scaleX": 1.05, "transformOrigin": "50% 100%", "duration": q * 0.6}, t)
        self.tw(sel, {"scaleY": 1.04, "scaleX": 0.97, "y": -height, "duration": q * 1.5, "ease": "power2.out"}, t + q * 0.6)
        self.tw(sel, {"scaleY": 1, "scaleX": 1, "y": 0, "duration": q * 1.4, "ease": "power2.in"}, t + q * 2.1)
        self.tw(sel, {"scaleY": 0.93, "scaleX": 1.04, "duration": q * 0.25}, t + q * 3.5)
        self.tw(sel, {"scaleY": 1, "scaleX": 1, "duration": q * 0.5, "ease": "back.out(3)"}, t + q * 3.75)

    def spin(self, name, t, dur=0.8):
        sel = f"#c-{name} svg"
        self.tw(sel, {"scaleX": -1, "duration": dur / 2, "ease": "sine.inOut"}, t)
        self.tw(sel, {"scaleX": 1, "duration": dur / 2, "ease": "sine.inOut"}, t + dur / 2)
        self.tw(sel, {"y": -24, "duration": dur / 2, "ease": "sine.out"}, t)
        self.tw(sel, {"y": 0, "duration": dur / 2, "ease": "sine.in"}, t + dur / 2)
        if name in HUMAN:
            self.rot(name, "arm-r", 80, t, dur / 2)
            self.rot(name, "arm-l", -80, t, dur / 2)
            self.rot(name, "arm-r", 0, t + dur / 2, dur / 2)
            self.rot(name, "arm-l", 0, t + dur / 2, dur / 2)

    def stomp(self, name, t, side="r"):
        """lift one leg, slam it down with a squash and a little dust"""
        sg = 1 if side == "r" else -1
        self.rot(name, f"leg-{side}", -22 * sg, t, 0.16, "power2.out")
        self.rot(name, f"leg-{side}", 0, t + 0.16, 0.1, "power3.in")
        self.tw(f"#c-{name} svg", {"scaleY": 0.95, "scaleX": 1.03, "transformOrigin": "50% 100%", "duration": 0.06}, t + 0.26)
        self.tw(f"#c-{name} svg", {"scaleY": 1, "scaleX": 1, "duration": 0.18, "ease": "back.out(3)"}, t + 0.32)

    def wave(self, name, t, dur=2.0, side="r"):
        sg = 1 if side == "r" else -1
        self.rot(name, f"arm-{side}", 98 * sg, t, 0.4, "back.out(1.6)")
        self.rot(name, f"fore-{side}", 50 * sg, t, 0.4)
        n = max(2, int((dur - 0.8) / 0.3))
        for i in range(n):
            self.rot(name, f"fore-{side}", (25 if i % 2 == 0 else 62) * sg, t + 0.4 + i * 0.3, 0.3)
        self.rot(name, f"arm-{side}", 0, t + dur - 0.4, 0.4, "power2.inOut")
        self.rot(name, f"fore-{side}", 0, t + dur - 0.4, 0.4)

    def clap(self, name, t, times):
        """arms come to the front; one clap per time in `times` (absolute)"""
        self.rot(name, "arm-r", -32, t, 0.3)
        self.rot(name, "fore-r", -78, t, 0.3)
        self.rot(name, "arm-l", 32, t, 0.3)
        self.rot(name, "fore-l", 78, t, 0.3)
        for c in times:
            self.rot(name, "fore-r", -62, c - 0.14, 0.12)
            self.rot(name, "fore-l", 62, c - 0.14, 0.12)
            self.rot(name, "fore-r", -84, c - 0.02, 0.08, "power3.in")
            self.rot(name, "fore-l", 84, c - 0.02, 0.08, "power3.in")
        end = (times[-1] if times else t) + 0.3
        for prt in ("arm-r", "fore-r", "arm-l", "fore-l"):
            self.rot(name, prt, 0, end, 0.3)
        return end

    def clap_high(self, name, c):
        """one clap above the head at time c"""
        self.rot(name, "arm-r", 150, c - 0.3, 0.2)
        self.rot(name, "arm-l", -150, c - 0.3, 0.2)
        self.rot(name, "fore-r", -20, c - 0.3, 0.2)
        self.rot(name, "fore-l", 20, c - 0.3, 0.2)

    def arms_rest(self, name, t, dur=0.3):
        for prt in ("arm-r", "fore-r", "arm-l", "fore-l"):
            self.rot(name, prt, 0, t, dur)

    def dance(self, name, t0, t1, beat=0.5):
        i = 0
        t = t0
        while t < t1 - 0.05:
            s = 1 if i % 2 == 0 else -1
            self.tw(f"#c-{name} svg", {"rotation": 4 * s, "x": 10 * s, "transformOrigin": "50% 100%", "duration": beat, "ease": "sine.inOut"}, t)
            if name in HUMAN:
                self.rot(name, "arm-r", 120 if s > 0 else 40, t, beat)
                self.rot(name, "arm-l", -40 if s > 0 else -120, t, beat)
                self.rot(name, "fore-r", 25 * s, t, beat)
                self.rot(name, "fore-l", 25 * s, t, beat)
                self.rot(name, "leg-r", -10 if s > 0 else 0, t, beat)
                self.rot(name, "leg-l", 0 if s > 0 else 10, t, beat)
            else:
                self.rot(name, "head", 8 * s, t, beat)
            t += beat
            i += 1
        self.tw(f"#c-{name} svg", {"rotation": 0, "x": 0, "duration": 0.25}, t1)
        if name in HUMAN:
            for prt in ("arm-r", "fore-r", "arm-l", "fore-l", "leg-r", "leg-l"):
                self.rot(name, prt, 0, t1, 0.25)

    def wag(self, name, t0, t1, speed=0.16):
        p = CAST[name][1]
        piv = CAST[name][5].get(f"{p}-tail", (60, 300))
        i = 0
        t = t0
        while t < t1:
            self.tw(f"#c-{name} .{p}-tail", {"rotation": 22 if i % 2 == 0 else -14, "svgOrigin": f"{piv[0]} {piv[1]}", "duration": speed, "ease": "sine.inOut"}, t)
            t += speed
            i += 1
        self.tw(f"#c-{name} .{p}-tail", {"rotation": 0, "svgOrigin": f"{piv[0]} {piv[1]}", "duration": 0.2}, t1)

    def wiggle(self, name, t0, t1, beat=0.25):
        i = 0
        t = t0
        while t < t1 - 0.02:
            self.tw(f"#c-{name} svg", {"rotation": 6 if i % 2 == 0 else -6, "transformOrigin": "50% 100%", "duration": beat, "ease": "sine.inOut"}, t)
            t += beat
            i += 1
        self.tw(f"#c-{name} svg", {"rotation": 0, "duration": 0.2}, t1)

    def tip_hat(self, name, t):
        p = CAST[name][1]
        piv = CAST[name][5].get(f"{p}-hat")
        if not piv:
            return
        self.tw(f"#c-{name} .{p}-hat", {"rotation": -14, "y": -40, "svgOrigin": f"{piv[0]} {piv[1]}", "duration": 0.35, "ease": "back.out(2)"}, t)
        self.tw(f"#c-{name} .{p}-hat", {"rotation": 0, "y": 0, "svgOrigin": f"{piv[0]} {piv[1]}", "duration": 0.4, "ease": "power2.inOut"}, t + 0.9)
        self.wave(name, t, 1.4, "l")

    def nod(self, name, t, ang=6, dur=0.5):
        self.rot(name, "head", ang, t, dur / 2)
        self.rot(name, "head", 0, t + dur / 2, dur / 2)

    def look(self, name, t, dx, dur=0.3):
        self.tw(f"#c-{name} .{CAST[name][1]}-pupils", {"x": dx, "duration": dur}, t)

    # ------------------------------------------------------------------ face
    def blinks(self, name, t0, t1):
        p = CAST[name][1]
        t = t0 + self.rnd.uniform(0.4, 2.0)
        while t < t1:
            self.tw(f"#c-{name} .{p}-lid", {"scaleY": 1, "transformOrigin": "50% 0%", "duration": 0.07}, t)
            self.tw(f"#c-{name} .{p}-lid", {"scaleY": 0.001, "transformOrigin": "50% 0%", "duration": 0.09}, t + 0.1)
            t += self.rnd.uniform(2.4, 4.6)

    def mouth(self, name, shape, t):
        p = CAST[name][1]
        for s in ("smile", "open", "o", "wide"):
            self.set(f"#c-{name} .{p}-m-{s}", {"opacity": 1 if s == shape else 0}, t)

    def sing(self, name, words):
        """mouth shapes from word timings [{'w','s','e'}]: open on each word, closed in the gaps"""
        last_e = None
        for w in words:
            txt = w["w"].lower()
            shape = "o" if any(v in txt for v in ("oo", "ou", "o!", "whee")) else ("wide" if txt.endswith("!") or len(txt) > 5 else "open")
            if last_e is not None and w["s"] - last_e > 0.12:
                self.mouth(name, "smile", last_e)
            self.mouth(name, shape, w["s"])
            mid = (w["s"] + w["e"]) / 2
            if w["e"] - w["s"] > 0.3:
                self.mouth(name, "open" if shape != "open" else "o", mid)
            last_e = w["e"]
        if last_e is not None:
            self.mouth(name, "smile", last_e + 0.05)

    # ------------------------------------------------------------------ output
    def write(self, out_dir, title, audio=None, extra_css="", fonts_from=None):
        os.makedirs(out_dir, exist_ok=True)
        here = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(here)
        for f in ("hyperframes.json", "package.json"):
            shutil.copy(os.path.join(root, "cartoon3d", "compare2d", f), os.path.join(out_dir, f))
        open(os.path.join(out_dir, "meta.json"), "w").write(json.dumps({"id": os.path.basename(out_dir), "name": os.path.basename(out_dir),
                                                                        "createdAt": "2026-11-29T01:00:00.000Z"}))
        aud = ""
        if audio:
            os.makedirs(os.path.join(out_dir, "assets"), exist_ok=True)
            shutil.copy(audio, os.path.join(out_dir, "assets", "song.wav"))
            aud = (f'<audio id="music" data-timeline-role="music" class="clip" data-start="0" data-duration="{self.D:.3f}" '
                   f'data-track-index="10" data-volume="1" src="assets/song.wav"></audio>')
        font = ""
        if fonts_from:
            os.makedirs(os.path.join(out_dir, "assets", "fonts"), exist_ok=True)
            shutil.copy(fonts_from, os.path.join(out_dir, "assets", "fonts", "rounded.ttf"))
            font = "@font-face{font-family:Rounded;src:url(assets/fonts/rounded.ttf)}"
        page = f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>{font}*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#9fd8ff}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:#9fd8ff}}.char svg{{width:100%;height:100%;overflow:visible}}
.abs{{position:absolute}}{extra_css}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{self.D:.3f}" data-width="1920" data-height="1080" data-fps="30">
<div class="abs" id="cam" style="inset:0;transform-origin:960px 700px">
{chr(10).join(self.html)}
</div>
{chr(10).join(self.ui)}
<div class="abs" id="fade" style="inset:0;background:#fff;opacity:0;z-index:99"></div>
{aud}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(self.js)}
tl.set({{}}, {{}}, {self.D:.3f});
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>'''
        open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(page)
        return len(self.js)


# ---------------------------------------------------------------------------------------------- scenery
def backyard(seed=3):
    """sunny garden: sky, sun, clouds, hills, the family house, fence, trees, flowers, grass"""
    r = random.Random(seed)
    clouds = "".join(
        f'<g class="cloud" id="cl{i}" transform="translate({x} {y}) scale({s})">'
        f'<ellipse cx="0" cy="0" rx="90" ry="40" fill="#fff"/><ellipse cx="-60" cy="12" rx="60" ry="30" fill="#fff"/>'
        f'<ellipse cx="62" cy="10" rx="64" ry="32" fill="#fff"/><ellipse cx="10" cy="-28" rx="56" ry="38" fill="#fff"/></g>'
        for i, (x, y, s) in enumerate(((260, 150, 1.0), (980, 100, 0.8), (1600, 170, 1.1), (1340, 60, 0.6))))
    flowers = ""
    for i in range(46):
        x = r.uniform(20, 1900)
        y = r.uniform(960, 1070)
        c = ["#ff6f91", "#ffd23a", "#ffffff", "#b38cff", "#ff9a3a"][i % 5]
        flowers += (f'<g transform="translate({x:.0f} {y:.0f}) scale({0.6 + (y - 960) / 160:.2f})">'
                    + "".join(f'<circle cx="{8 * math.cos(a):.1f}" cy="{8 * math.sin(a):.1f}" r="7" fill="{c}"/>' for a in (0, 1.26, 2.51, 3.77, 5.03))
                    + '<circle r="5" fill="#ffb400"/></g>')
    tufts = "".join(f'<path d="M{x:.0f} {y:.0f} q4 -18 8 0 q4 -14 8 0" fill="none" stroke="#4fa83a" stroke-width="4" stroke-linecap="round"/>'
                    for x, y in ((r.uniform(0, 1920), r.uniform(940, 1075)) for _ in range(70)))
    tree = lambda x, s: (f'<g transform="translate({x} 860) scale({s})"><rect x="-18" y="-40" width="36" height="140" rx="12" fill="#9a6a44"/>'
                         f'<circle cx="0" cy="-120" r="110" fill="#5fbf4a"/><circle cx="-70" cy="-70" r="70" fill="#56b443"/>'
                         f'<circle cx="74" cy="-74" r="74" fill="#6acb54"/><circle cx="-20" cy="-170" r="60" fill="#78d562"/>'
                         f'<circle cx="40" cy="-140" r="16" fill="#ff5a5f"/><circle cx="-50" cy="-100" r="14" fill="#ff5a5f"/><circle cx="60" cy="-60" r="14" fill="#ff5a5f"/></g>')
    house = ('<g transform="translate(1420 520)">'
             '<rect x="0" y="120" width="380" height="280" rx="10" fill="#ffe6b8"/><rect x="0" y="120" width="380" height="280" rx="10" fill="url(#hshade)"/>'
             '<path d="M-30 130 L190 -20 L410 130z" fill="#e8574f"/><path d="M-30 130 L190 -20 L410 130" fill="none" stroke="#c23a35" stroke-width="10" stroke-linejoin="round"/>'
             '<rect x="150" y="250" width="80" height="150" rx="40" fill="#a0603a"/><circle cx="212" cy="330" r="6" fill="#ffd23a"/>'
             '<rect x="40" y="180" width="80" height="80" rx="10" fill="#bfe6ff" stroke="#fff" stroke-width="8"/><path d="M80 180 v80 M40 220 h80" stroke="#fff" stroke-width="6"/>'
             '<rect x="260" y="180" width="80" height="80" rx="10" fill="#bfe6ff" stroke="#fff" stroke-width="8"/><path d="M300 180 v80 M260 220 h80" stroke="#fff" stroke-width="6"/>'
             '<rect x="280" y="20" width="40" height="70" fill="#c23a35"/></g>')
    fence = "".join(f'<path d="M{x} 900 v-90 l14 -18 l14 18 v90z" fill="#fff7ec" stroke="#e6d6bf" stroke-width="3"/>' for x in range(0, 1400, 46))
    fence += '<rect x="0" y="828" width="1400" height="14" fill="#fff7ec"/><rect x="0" y="868" width="1400" height="14" fill="#fff7ec"/>'
    return (f'<svg class="abs" id="scene" style="inset:0;z-index:0" viewBox="0 0 1920 1080" width="1920" height="1080">'
            f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7cc8ff"/><stop offset="1" stop-color="#d8f1ff"/></linearGradient>'
            f'<linearGradient id="grass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fdc5e"/><stop offset="1" stop-color="#5fb63e"/></linearGradient>'
            f'<linearGradient id="hshade" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.1"/></linearGradient>'
            f'<radialGradient id="sun"><stop offset="0" stop-color="#fff6a8"/><stop offset="0.6" stop-color="#ffd23a"/><stop offset="1" stop-color="#ffb400"/></radialGradient></defs>'
            f'<rect width="1920" height="1080" fill="url(#sky)"/>'
            f'<g id="sunrays" transform="translate(1720 150)">' + "".join(f'<rect x="-6" y="-140" width="12" height="50" rx="6" fill="#ffe36a" transform="rotate({a})"/>' for a in range(0, 360, 30)) + '</g>'
            f'<circle cx="1720" cy="150" r="80" fill="url(#sun)"/>{clouds}'
            f'<path d="M0 700 Q300 560 700 680 Q1100 560 1500 660 Q1760 600 1920 650 L1920 1080 L0 1080z" fill="#a6e07a"/>'
            f'<path d="M0 780 Q420 700 900 770 Q1400 690 1920 760 L1920 1080 L0 1080z" fill="#97d86a"/>'
            f'{house}{tree(150, 1.0)}{tree(1270, 0.8)}{fence}'
            f'<rect x="0" y="880" width="1920" height="200" fill="url(#grass)"/>{tufts}{flowers}</svg>')
