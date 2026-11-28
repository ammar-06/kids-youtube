"""The farm world for the cartoon: one long landscape with a place for each animal, in parallax layers.

Screen is 1920x1080. Station k (0..5) is seen when the camera is at x = k*1920. Layers scroll at different speeds:
  sky (fixed) > clouds 0.15 > far hills 0.4 > near hills 0.7 > ground + props 1.0 > front grass 1.3
Props are drawn at screen positions inside their station, so the animator knows where doors and ponds are.
"""
import math
import random

from art2 import INK, S, g

W = 1920
N = 6
SPEED = {"clouds": 0.15, "far": 0.4, "near": 0.7, "ground": 1.0, "front": 1.3}
EXTRA = {   # more gradients for the world, added to the page next to art2.DEFS
    "mud": ("#9a6a42", "#5e3a1e"), "water": ("#8fdcff", "#2f9ad8"), "wood": ("#c98a52", "#8a5a30"),
    "barn": ("#f0584a", "#b8322a"), "roof": ("#8b3a2c", "#5a2016"), "hay": ("#ffe27a", "#d9a92a"),
    "stone": ("#d8d3cc", "#9c958c"), "coop": ("#ffcf6b", "#d99a2a"), "leaf": ("#6fd15a", "#3c9a35"),
    "trunk": ("#a76a3a", "#6e4321"), "sky": ("#5fbdf7", "#cdeeff"),
}
DEFS = ('<svg width="0" height="0" style="position:absolute"><defs>' + "".join(
    f'<radialGradient id="g{k}" cx="38%" cy="30%" r="80%"><stop offset="0" stop-color="{a}"/>'
    f'<stop offset="1" stop-color="{b}"/></radialGradient>' for k, (a, b) in EXTRA.items())
    + '<linearGradient id="gskyl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5fbdf7"/>'
      '<stop offset="1" stop-color="#d6f2ff"/></linearGradient>'
      '<linearGradient id="ggrass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7fd65e"/>'
      '<stop offset="1" stop-color="#4fae3a"/></linearGradient>'
    + '</defs></svg>')

rnd = random.Random(5)


def layer_width(speed):
    return int(W + (N - 1) * W * speed) + 4


def hills(width, base, amp, period, color, outline=False, seed=1):
    r = random.Random(seed)
    pts, x = [], 0
    while x <= width + period:
        pts.append((x, base - amp * (0.6 + 0.4 * r.random())))
        x += period * (0.7 + 0.6 * r.random())
    d = f"M0 1080 L0 {pts[0][1]:.0f} "
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        mx = (x1 + x2) / 2
        d += f"Q{x1 + (x2 - x1) * 0.25:.0f} {y1 - amp * 0.5:.0f} {mx:.0f} {(y1 + y2) / 2:.0f} "
        d += f"T{x2:.0f} {y2:.0f} "
    d += f"L{width} 1080 Z"
    st = f'stroke="{INK}" stroke-width="5"' if outline else ""
    return f'<path d="{d}" fill="{color}" {st}/>'


def tree(x, y, s=1.0, apples=False):
    a = "".join(f'<circle cx="{x + dx * s:.0f}" cy="{y + dy * s:.0f}" r="{11 * s:.0f}" fill="#ff4d4d" stroke="{INK}" stroke-width="3"/>'
                for dx, dy in ((-40, -60), (30, -30), (-10, 10), (55, 15), (-60, 0))) if apples else ""
    return (f'<path d="M{x - 16 * s:.0f} {y + 40 * s:.0f} q4 {90 * s:.0f} -6 {150 * s:.0f} h{44 * s:.0f} q-10 {-60 * s:.0f} -6 {-150 * s:.0f}z" {S(g("trunk"), 5)}/>'
            f'<circle cx="{x}" cy="{y - 30 * s:.0f}" r="{95 * s:.0f}" {S(g("leaf"), 5)}/>'
            f'<circle cx="{x - 75 * s:.0f}" cy="{y + 20 * s:.0f}" r="{65 * s:.0f}" {S(g("leaf"), 5)}/>'
            f'<circle cx="{x + 75 * s:.0f}" cy="{y + 20 * s:.0f}" r="{70 * s:.0f}" {S(g("leaf"), 5)}/>'
            f'<circle cx="{x}" cy="{y + 25 * s:.0f}" r="{70 * s:.0f}" fill="{g("leaf")}"/>{a}')


def far_tree(x, y, s):
    return (f'<rect x="{x - 5 * s:.0f}" y="{y}" width="{10 * s:.0f}" height="{40 * s:.0f}" fill="#7aa858"/>'
            f'<circle cx="{x}" cy="{y - 10 * s:.0f}" r="{30 * s:.0f}" fill="#6cbf58"/>')


def svg(width, body, height=1080):
    return f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


def sky():
    return svg(W, f'<rect width="{W}" height="1080" fill="url(#gskyl)"/>')


def clouds():
    w = layer_width(SPEED["clouds"])
    body = ""
    for i in range(int(w / 420)):
        x, y, s = i * 420 + rnd.randint(0, 200), rnd.randint(40, 260), rnd.uniform(0.7, 1.2)
        body += (f'<g transform="translate({x} {y}) scale({s:.2f})" fill="#fff" opacity="0.95">'
                 '<circle cx="70" cy="75" r="42"/><circle cx="125" cy="55" r="52"/><circle cx="185" cy="72" r="40"/>'
                 '<rect x="40" y="70" width="180" height="46" rx="23"/></g>')
    return svg(w, body)


def far():
    w = layer_width(SPEED["far"])
    body = hills(w, 640, 90, 520, "#b5e6a0", seed=2)
    for x in range(80, w, 230):
        body += far_tree(x + rnd.randint(-40, 40), 600 + rnd.randint(-30, 30), rnd.uniform(0.7, 1.1))
    return svg(w, body)


def near():
    w = layer_width(SPEED["near"])
    body = hills(w, 720, 70, 700, "#94d870", seed=3)
    for x in range(300, w, 900):
        body += tree(x + rnd.randint(-100, 100), 600, 0.55)
    return svg(w, body)


# ------------------------------------------------------------------------------------------------ stations
def barn(x, y):   # 420 wide, door centre at (x+200, y+500)
    return (f'<g transform="translate({x} {y})">'
            f'<path d="M0 170 l200 -150 l200 150 v330 h-400z" {S(g("barn"))}/>'
            f'<path d="M-24 186 l224 -176 l224 176" fill="none" stroke="#fff4e0" stroke-width="24" stroke-linejoin="round"/>'
            f'<rect x="150" y="130" width="100" height="80" rx="8" {S("#7a2a22")}/>'
            f'<path d="M150 130 l100 80 M250 130 l-100 80" stroke="#fff4e0" stroke-width="8"/>'
            f'<rect x="90" y="280" width="220" height="220" {S("#9b3027")}/>'
            f'<path d="M90 280 l220 220 M310 280 l-220 220 M200 280 v220" stroke="#fff4e0" stroke-width="12"/>'
            f'<rect x="90" y="280" width="220" height="220" fill="none" stroke="#fff4e0" stroke-width="12"/></g>')


def hay(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><rect x="-80" y="-60" width="160" height="90" rx="22" {S(g("hay"))}/>'
            f'<path d="M-60 -40 h120 M-70 -15 h140 M-60 10 h120" stroke="#c99a20" stroke-width="5" stroke-linecap="round"/></g>')


def fence(x0, x1, y=700, col="#fff4e0"):
    posts = "".join(f'<rect x="{x}" y="{y}" width="22" height="112" rx="6" {S(col, 4)}/>' for x in range(x0, x1, 92))
    return (posts + f'<rect x="{x0 - 10}" y="{y + 25}" width="{x1 - x0}" height="18" rx="6" {S(col, 4)}/>'
            f'<rect x="{x0 - 10}" y="{y + 70}" width="{x1 - x0}" height="18" rx="6" {S(col, 4)}/>')


def _inside(x, y, ex):
    return any(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1 for cx, cy, rx, ry in ex)


def flowers(x0, x1, y0, y1, n, seed, ex=()):
    r = random.Random(seed)
    out = ""
    for _ in range(n):
        x, y = r.randint(x0, x1), r.randint(y0, y1)
        if _inside(x, y, ex):
            continue
        c = r.choice(["#ff6b8b", "#ffd23f", "#ffffff", "#b38bff", "#ff9f43"])
        out += f'<g transform="translate({x} {y})">' + "".join(
            f'<circle cx="{8 * math.cos(a * 1.2566):.1f}" cy="{8 * math.sin(a * 1.2566):.1f}" r="6" fill="{c}"/>' for a in range(5)) + \
            '<circle r="5" fill="#ffb300"/></g>'
    return out


def grass(x0, x1, y0, y1, n, seed, ex=()):
    r = random.Random(seed)
    pts = [(r.randint(x0, x1), r.randint(y0, y1)) for _ in range(n)]
    return "".join(f'<path d="M{x} {y} q4 -18 8 0 q4 -22 8 0" fill="none" stroke="#3f9a2e" stroke-width="4" stroke-linecap="round"/>'
                   for x, y in pts if not _inside(x, y, ex))


def mud(cx, cy):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="340" ry="70" {S(g("mud"))}/>'
            f'<ellipse cx="{cx - 90}" cy="{cy - 14}" rx="90" ry="16" fill="#b78457" opacity="0.7"/>'
            f'<ellipse cx="{cx + 120}" cy="{cy + 12}" rx="60" ry="12" fill="#b78457" opacity="0.6"/>')


def pond(cx, cy):
    pads = "".join(f'<path d="M{cx + dx} {cy + dy} m-34 0 a34 18 0 1 0 68 0 l-34 -2z" {S("#59c24a", 4)}/>'
                   for dx, dy in ((-380, -20), (330, 10), (-250, 50)))
    reeds = "".join(f'<path d="M{x} {cy - 40} q-6 -80 4 -150" fill="none" stroke="#3c8a2e" stroke-width="7" stroke-linecap="round"/>'
                    f'<rect x="{x - 7}" y="{cy - 210}" width="16" height="50" rx="8" {S("#8a5a30", 4)}/>'
                    for x in (cx - 560, cx - 530, cx + 540, cx + 575))
    return (reeds + f'<ellipse cx="{cx}" cy="{cy}" rx="560" ry="125" {S(g("water"))}/>'
            f'<ellipse cx="{cx - 150}" cy="{cy - 40}" rx="200" ry="22" fill="#fff" opacity="0.35"/>'
            f'<ellipse cx="{cx + 200}" cy="{cy + 40}" rx="120" ry="14" fill="#fff" opacity="0.25"/>' + pads)


def stable(x, y):   # door centre (x+190, y+440)
    return (f'<g transform="translate({x} {y})">'
            f'<rect x="0" y="120" width="380" height="320" {S(g("wood"))}/>'
            f'<path d="M-30 130 l220 -120 l220 120z" {S(g("roof"))}/>'
            + "".join(f'<path d="M{i} 130 v310" stroke="#8a5a30" stroke-width="5"/>' for i in range(40, 380, 48)) +
            f'<path d="M110 440 v-170 q80 -60 160 0 v170z" {S("#5a3518")}/>'
            f'<path d="M110 330 h160" stroke="#c98a52" stroke-width="10"/>'
            f'<path d="M168 70 a22 22 0 1 0 44 0" fill="none" stroke="#c0c0c8" stroke-width="10" stroke-linecap="round"/></g>')


def coop(x, y):   # ramp foot at (x+330, y+440)
    return (f'<g transform="translate({x} {y})">'
            f'<rect x="30" y="230" width="18" height="210" {S(g("wood"), 4)}/><rect x="270" y="230" width="18" height="210" {S(g("wood"), 4)}/>'
            f'<rect x="0" y="110" width="320" height="140" rx="10" {S(g("coop"))}/>'
            f'<path d="M-24 120 l184 -100 l184 100z" {S(g("barn"))}/>'
            f'<path d="M100 250 v-90 q60 -50 120 0 v90z" {S("#6b3d18")}/>'
            f'<path d="M160 250 l190 190 h-40 l-170 -170z" {S(g("wood"), 5)}/>'
            + "".join(f'<path d="M{200 + i * 26} {286 + i * 26} l18 -18" stroke="#8a5a30" stroke-width="5"/>' for i in range(5)) +
            f'</g>')


def nest(cx, cy):
    eggs = "".join(f'<ellipse cx="{cx + dx}" cy="{cy - 20}" rx="17" ry="22" {S("#fff7ea", 4)}/>' for dx in (-28, 0, 28))
    return eggs + (f'<ellipse cx="{cx}" cy="{cy}" rx="80" ry="30" {S(g("hay"))}/>'
                   f'<path d="M{cx - 64} {cy - 6} q30 12 60 0 q30 12 60 0" fill="none" stroke="#c99a20" stroke-width="5"/>')


def sunflower(x, y, h=200):
    petals = "".join(f'<ellipse cx="{x + 34 * math.cos(a * 0.5236):.0f}" cy="{y - h + 34 * math.sin(a * 0.5236):.0f}" rx="18" ry="10" '
                     f'transform="rotate({a * 30} {x + 34 * math.cos(a * 0.5236):.0f} {y - h + 34 * math.sin(a * 0.5236):.0f})" {S("#ffd23f", 3)}/>'
                     for a in range(12))
    return (f'<path d="M{x} {y} v{-h}" stroke="#3c8a2e" stroke-width="10"/>'
            f'<path d="M{x} {y - h * 0.4:.0f} q30 -30 50 -10 q-30 20 -50 10z" {S("#59c24a", 3)}/>'
            + petals + f'<circle cx="{x}" cy="{y - h}" r="24" {S("#8a5a30", 4)}/>')


def stone_wall(x0, x1, y):
    out = ""
    for i, x in enumerate(range(x0, x1, 70)):
        out += f'<ellipse cx="{x}" cy="{y}" rx="38" ry="24" {S(g("stone"), 4)}/>'
        out += f'<ellipse cx="{x + 35}" cy="{y - 36}" rx="34" ry="22" {S(g("stone"), 4)}/>'
    return out


def ground():
    """All six places on one long strip. Returns the SVG and the screen spots the animator needs."""
    w = layer_width(SPEED["ground"])
    b = [f'<path d="M0 805 Q{w / 4:.0f} 780 {w / 2:.0f} 805 T{w} 805 V1080 H0z" fill="url(#ggrass)"/>']
    spots = {}
    for k in range(N):
        o = k * W
        ex = []
        if k == 0:     # barnyard: the cow
            b.append(fence(o + 520, o + 1920))
            b.append(barn(o + 60, o + 378))
            b.append(hay(o + 1150, o + 830, 0.8))
            spots[k] = {"door": (262, 878)}
        elif k == 1:   # pig pen with mud
            b.append(fence(o, o + 1920, 700, "#d9a46a"))
            b.append(mud(o + 700, 905))
            b.append(f'<rect x="{o + 150}" y="840" width="220" height="60" rx="10" {S(g("wood"))}/>')
            spots[k] = {"mud": (700, 905)}
            ex = [(o + 700, 905, 380, 95)]
        elif k == 2:   # pond
            b.append(fence(o, o + 300, 700))
            b.append(fence(o + 1500, o + 1920, 700))
            b.append(pond(o + 720, 890))
            spots[k] = {"pond": (720, 890)}
            ex = [(o + 720, 890, 600, 150)]
        elif k == 3:   # sheep hills
            b.append(f'<path d="M{o + 120} 820 Q{o + 700} 520 {o + 1300} 820z" {S("#8fd86a", 5)}/>')
            b.append(stone_wall(o + 1250, o + 1920, 790))
            b.append(flowers(o + 250, o + 1150, 700, 800, 22, 31))
            b.append(tree(o + 260, 560, 0.7, apples=True))
            spots[k] = {"hilltop": (700, 640)}
        elif k == 4:   # stable
            b.append(fence(o + 450, o + 1920, 700, "#d9a46a"))
            b.append(stable(o + 30, 400))
            b.append(hay(o + 1120, 840, 0.75))
            b.append(hay(o + 1250, 860, 0.6))
            spots[k] = {"door": (220, 840)}
        elif k == 5:   # chicken coop
            b.append(fence(o + 520, o + 1920))
            b.append(coop(o + 40, 400))
            b.append(nest(o + 1130, 880))
            b.append(sunflower(o + 1300, 800, 230) + sunflower(o + 1360, 790, 190))
            spots[k] = {"ramp": (370, 840), "nest": (1130, 880)}
        b.append(flowers(o, o + 1920, 870, 1070, 34, 100 + k, ex))
        b.append(grass(o, o + 1920, 830, 1075, 60, 200 + k, ex))
    return svg(w, "".join(b)), spots


def front():
    w = layer_width(SPEED["front"])
    out = ""
    r = random.Random(9)
    for x in range(200, w, 760):
        x += r.randint(-150, 150)
        out += "".join(f'<path d="M{x + i * 14} 1085 q{r.randint(-20, 20)} -70 {r.randint(-10, 10)} -{r.randint(70, 120)}" '
                       f'fill="none" stroke="#3c9a2e" stroke-width="12" stroke-linecap="round"/>' for i in range(5))
        out += f'<circle cx="{x + 30}" cy="1000" r="16" fill="#ff6b8b" stroke="{INK}" stroke-width="4"/>'
    return svg(w, out)
