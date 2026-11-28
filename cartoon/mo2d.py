"""2D Mo drawn after the Gemini design (character/1-apose-images/mo-apose.jpg): soft shaded, no ink outlines.

Front-facing, viewBox 0 0 400 640, feet at y=630. Rigged parts (animate with GSAP, transform-origin from PIVOTS):
  .mo-head .mo-hair-tuft .mo-arm-l .mo-fore-l .mo-arm-r .mo-fore-r .mo-leg-l .mo-leg-r .mo-body
  .mo-lid (blink: scaleY 0 -> 1), .mo-pupils (look around: x/y), .mo-brows
  .mo-m-smile .mo-m-open .mo-m-o .mo-m-wide (mouth shapes for singing, opacity)
'right'/'left' = the character's own side (his left is on screen-right).
"""

SKIN, SKIN_D, SKIN_L = "#d9996b", "#b8754c", "#efbd94"
HAIR, HAIR_L = "#141118", "#3a3440"
SHIRT, SHIRT_D, SHIRT_L = "#4cb050", "#35903c", "#74cb72"
SHORTS, SHORTS_D = "#3d4f8f", "#2c3a70"
SHOE, SHOE_D = "#f28a3a", "#d0661c"

GRADS = {
    "skin": (SKIN_L, SKIN, SKIN_D), "shirt": (SHIRT_L, SHIRT, SHIRT_D), "shorts": ("#5466a8", SHORTS, SHORTS_D),
    "hair": (HAIR_L, HAIR, "#060508"), "shoe": ("#ffb070", SHOE, SHOE_D), "iris": ("#a8683a", "#7a4524", "#3e2010"),
    "sock": ("#ffffff", "#f2f0ee", "#d6d2cf"), "sclera": ("#ffffff", "#fbfaf9", "#e3dfdc"),
}


def defs():
    out = []
    for k, (a, b, c) in GRADS.items():
        out.append(f'<radialGradient id="mo-{k}" cx="40%" cy="32%" r="75%"><stop offset="0" stop-color="{a}"/>'
                   f'<stop offset="0.55" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></radialGradient>')
    out.append('<radialGradient id="mo-blush" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff6f6f" stop-opacity="0.45"/>'
               '<stop offset="1" stop-color="#ff6f6f" stop-opacity="0"/></radialGradient>')
    out.append('<radialGradient id="mo-shade" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#000" stop-opacity="0.28"/>'
               '<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>')
    out.append('<linearGradient id="mo-under" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/>'
               '<stop offset="1" stop-color="#000" stop-opacity="0.22"/></linearGradient>')
    return "".join(out)


def G(k):
    return f"url(#mo-{k})"


def fluff(cx, cy, rx, ry, a0, a1, n, bump, jitter=0.0):
    """closed blob outline with soft bumps between angles a0..a1 (degrees), for fluffy hair edges"""
    import math
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        r = 1 + (bump if i % 2 else 0) + jitter * math.sin(i * 2.3)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1, 2):
        d += f" Q{pts[i][0]:.1f} {pts[i][1]:.1f} {pts[i + 1][0]:.1f} {pts[i + 1][1]:.1f}"
    return d


def eye(cx, cy, side):
    rx, ry = 31, 34
    return (f'<g class="mo-eye mo-eye-{side}">'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{G("sclera")}"/>'
            f'<clipPath id="mo-eclip-{side}"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath>'
            f'<g clip-path="url(#mo-eclip-{side})"><g class="mo-pupils">'
            f'<circle cx="{cx}" cy="{cy + 3}" r="26" fill="{G("iris")}"/>'
            f'<circle cx="{cx}" cy="{cy + 3}" r="26" fill="none" stroke="#2a150a" stroke-width="2.5" opacity="0.7"/>'
            f'<circle cx="{cx}" cy="{cy + 4}" r="13" fill="#130a06"/>'
            f'<ellipse cx="{cx + 9}" cy="{cy - 9}" rx="9" ry="8" fill="#fff"/>'
            f'<circle cx="{cx - 9}" cy="{cy + 13}" r="3.6" fill="#fff" opacity="0.9"/>'
            f'</g>'
            # soft shadow of the upper lid on the eyeball
            f'<ellipse cx="{cx}" cy="{cy - ry - 4}" rx="{rx + 4}" ry="16" fill="#000" opacity="0.12"/>'
            f'<rect class="mo-lid" x="{cx - rx - 2}" y="{cy - ry - 2}" width="{2 * rx + 4}" height="{2 * ry + 4}" fill="{G("skin")}" '
            f'/>'
            f'</g>'
            f'<path d="M{cx - rx + 2} {cy - ry * 0.55:.1f} Q{cx} {cy - ry - 7} {cx + rx - 2} {cy - ry * 0.55:.1f}" fill="none" stroke="#2b1a14" stroke-width="3.2" stroke-linecap="round" opacity="0.85"/>'
            f'</g>')


def mouths(cx, cy):
    lip = "#b0473f"
    smile = (f'<path d="M{cx - 26} {cy - 4} Q{cx} {cy + 16} {cx + 26} {cy - 4}" fill="none" stroke="#9b3b33" stroke-width="4.5" stroke-linecap="round"/>'
             f'<path d="M{cx - 18} {cy + 4} Q{cx} {cy + 14} {cx + 18} {cy + 4}" fill="none" stroke="#e98c80" stroke-width="3" stroke-linecap="round" opacity="0.6"/>')
    opn = (f'<path d="M{cx - 24} {cy - 6} Q{cx} {cy - 1} {cx + 24} {cy - 6} Q{cx + 20} {cy + 26} {cx} {cy + 27} Q{cx - 20} {cy + 26} {cx - 24} {cy - 6}z" fill="#6e1d22"/>'
           f'<path d="M{cx - 18} {cy - 4} Q{cx} {cy} {cx + 18} {cy - 4} l-2 5 Q{cx} {cy + 5} {cx - 16} {cy + 1}z" fill="#fff"/>'
           f'<ellipse cx="{cx}" cy="{cy + 18}" rx="13" ry="7" fill="#ff7d86"/>')
    o = (f'<ellipse cx="{cx}" cy="{cy + 6}" rx="12" ry="16" fill="#6e1d22"/>'
         f'<ellipse cx="{cx}" cy="{cy + 14}" rx="8" ry="5" fill="#ff7d86"/>')
    wide = (f'<path d="M{cx - 32} {cy - 8} Q{cx} {cy - 2} {cx + 32} {cy - 8} Q{cx + 28} {cy + 34} {cx} {cy + 35} Q{cx - 28} {cy + 34} {cx - 32} {cy - 8}z" fill="#6e1d22"/>'
            f'<path d="M{cx - 24} {cy - 6} Q{cx} {cy - 1} {cx + 24} {cy - 6} l-2 6 Q{cx} {cy + 5} {cx - 22} {cy}z" fill="#fff"/>'
            f'<ellipse cx="{cx}" cy="{cy + 24}" rx="17" ry="9" fill="#ff7d86"/>')
    return (f'<g class="mo-m-smile">{smile}</g><g class="mo-m-open" opacity="0">{opn}</g>'
            f'<g class="mo-m-o" opacity="0">{o}</g><g class="mo-m-wide" opacity="0">{wide}</g>')


def head():
    cx, cy = 200, 196
    hair_back = f'<path d="{fluff(cx, cy - 18, 136, 128, 160, 380, 26, 0.045)} Z" fill="{G("hair")}"/>'
    ears = "".join(
        f'<ellipse cx="{x}" cy="232" rx="27" ry="34" fill="{G("skin")}"/>'
        f'<ellipse cx="{x + (5 if x < 200 else -5)}" cy="234" rx="13" ry="19" fill="{SKIN_D}" opacity="0.55"/>' for x in (72, 328))
    face = (f'<ellipse cx="{cx}" cy="{cy + 18}" rx="128" ry="124" fill="{G("skin")}"/>'
            '')
    cheeks = (f'<ellipse cx="118" cy="262" rx="34" ry="24" fill="url(#mo-blush)"/>'
              f'<ellipse cx="282" cy="262" rx="34" ry="24" fill="url(#mo-blush)"/>')
    nose = (f'<ellipse cx="{cx}" cy="250" rx="17" ry="14" fill="{SKIN_D}" opacity="0.45"/>'
            f'<ellipse cx="{cx - 3}" cy="246" rx="11" ry="8" fill="{SKIN_L}" opacity="0.8"/>')
    brows = ('<g class="mo-brows">'
             '<path d="M118 160 Q146 146 172 156" fill="none" stroke="#5b3a2a" stroke-width="6" stroke-linecap="round"/>'
             '<path d="M228 156 Q254 146 282 160" fill="none" stroke="#5b3a2a" stroke-width="6" stroke-linecap="round"/></g>')
    # front hair: fluffy cap, fringe sweeping to his left (screen right), small soft tuft on top
    cap = (f'<path d="M66 214 Q58 120 112 76 Q160 40 214 46 Q290 52 326 110 Q344 150 336 214 '
           f'Q326 170 300 150 Q288 176 262 132 Q236 150 214 142 Q196 152 158 128 Q128 150 110 138 Q86 160 66 214z" fill="{G("hair")}"/>')
    fringe = (f'<path d="M150 70 Q208 40 262 74 Q232 72 222 100 Q236 128 216 150 Q206 118 180 108 Q170 96 150 70z" fill="{HAIR_L}" opacity="0.25"/>'
              + "".join(f'<path d="M{x} {y} q{dx} {dy} {dx * 2} {dy * 2.4}" fill="none" stroke="#2c2733" stroke-width="3" stroke-linecap="round" opacity="0.7"/>'
                        for x, y, dx, dy in ((126, 104, 6, 12), (160, 84, 8, 12), (240, 80, 8, 12), (282, 104, 6, 12), (204, 70, 6, 14))))
    tuft = (f'<g class="mo-hair-tuft"><path d="M180 64 Q182 26 214 8 Q206 34 222 44 Q232 18 262 12 Q244 40 250 70 Q216 54 180 64z" fill="{G("hair")}"/>'
            '</g>')
    shine = ('<path d="M120 102 Q154 70 196 64" fill="none" stroke="#6a6276" stroke-width="7" stroke-linecap="round" opacity="0.28"/>')
    edge = (f'<path d="{fluff(cx, cy - 22, 134, 126, 196, 344, 30, 0.035)}" fill="none" stroke="{HAIR}" stroke-width="10" stroke-linecap="round" opacity="0.9"/>')
    return (f'<g class="mo-head">{hair_back}{ears}{face}{cheeks}{nose}'
            f'{eye(152, 212, "r")}{eye(248, 212, "l")}{brows}'
            f'<g class="mo-mouth">{mouths(200, 286)}</g>{edge}{cap}{fringe}{tuft}{shine}</g>')


def rocket(x, y, s, ang):
    return (f'<g transform="translate({x} {y}) rotate({ang}) scale({s})" fill="#fafafa">'
            f'<path d="M0 -34 Q14 -18 12 10 L-12 10 Q-14 -18 0 -34z"/>'
            f'<path d="M-12 -2 L-24 16 L-12 12z M12 -2 L24 16 L12 12z"/>'
            f'<path d="M-6 13 Q0 30 6 13z"/>'
            f'<circle cx="0" cy="-10" r="5.5" fill="{SHIRT}"/></g>')


def arm(side):
    # shoulder pivot, upper arm + sleeve, forearm + hand (separate group so the elbow can bend)
    sg = -1 if side == "r" else 1           # his right arm is on screen-left
    sx, sy = 200 + sg * 88, 362
    ex, ey = 200 + sg * 124, 432
    hx, hy = 200 + sg * 150, 486
    def limb(x0, y0, x1, y1, w):
        return (f'<path d="M{x0} {y0} L{x1} {y1}" stroke="{SKIN_D}" stroke-width="{w + 3}" stroke-linecap="round"/>'
                f'<path d="M{x0} {y0} L{x1} {y1}" stroke="{SKIN}" stroke-width="{w}" stroke-linecap="round"/>'
                f'<path d="M{x0 - sg * 4} {y0} L{x1 - sg * 4} {y1}" stroke="{SKIN_L}" stroke-width="{w * 0.3:.0f}" stroke-linecap="round" opacity="0.55"/>')
    hand = (f'<g transform="translate({hx} {hy}) rotate({-sg * 28})">'
            f'<path d="M-15 -4 Q-17 22 -6 30 Q4 36 13 28 Q19 16 16 -4 Q0 -12 -15 -4z" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2"/>'
            f'<path d="M{-sg * 14} 0 Q{-sg * 26} 8 {-sg * 20} 18 Q{-sg * 14} 16 {-sg * 11} 10" fill="{SKIN}" stroke="{SKIN_D}" stroke-width="2"/>'
            f'<path d="M-6 22 v6 M1 24 v7 M8 22 v6" stroke="{SKIN_D}" stroke-width="1.8" stroke-linecap="round" opacity="0.7"/>'
            f'</g>')
    fore = f'<g class="mo-fore-{side}">{limb(ex, ey, hx, hy, 25)}{hand}</g>'
    sleeve = (f'<path d="M{sx - sg * 30} {sy - 22} Q{sx + sg * 26} {sy - 30} {sx + sg * 42} {sy + 30} Q{sx + sg * 26} {sy + 46} {sx + sg * 4} {sy + 52} Q{sx - sg * 22} {sy + 30} {sx - sg * 30} {sy - 22}z" fill="{SHIRT}"/>'
              f'<path d="M{sx + sg * 42} {sy + 30} Q{sx + sg * 26} {sy + 46} {sx + sg * 4} {sy + 52}" fill="none" stroke="{SHIRT_D}" stroke-width="6" stroke-linecap="round"/>')
    return f'<g class="mo-arm-{side}">{fore}{limb(sx, sy, ex, ey, 27)}{sleeve}</g>'


def leg(side):
    sg = -1 if side == "r" else 1
    x = 200 + sg * 40
    return (f'<g class="mo-leg-{side}">'
            f'<rect x="{x - 19}" y="540" width="38" height="64" rx="16" fill="{SKIN}"/>'
            f'<rect x="{x - 19 + 6}" y="550" width="8" height="40" rx="4" fill="{SKIN_L}" opacity="0.5"/>'
            f'<rect x="{x - 21}" y="584" width="42" height="24" rx="9" fill="{G("sock")}"/>'
            f'<path d="M{x - 34 + sg * 4} 632 Q{x - 36 + sg * 4} 600 {x + sg * 4} 598 Q{x + 36 + sg * 4} 600 {x + 34 + sg * 4} 632z" fill="{G("shoe")}"/>'
            f'<rect x="{x - 36 + sg * 4}" y="625" width="72" height="9" rx="4.5" fill="#fafafa"/>'
            f'<path d="M{x - 10 + sg * 4} 607 l20 0 M{x - 12 + sg * 4} 615 l24 0" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>'
            f'</g>')


def body():
    torso = (f'<path d="M150 342 Q200 334 250 342 Q290 352 296 384 L290 512 Q200 530 110 512 L104 384 Q110 352 150 342z" fill="{G("shirt")}"/>'
             f'<path d="M110 504 Q200 522 290 504 L290 512 Q200 530 110 512z" fill="{SHIRT_D}" opacity="0.7"/>'
             f'<path d="M172 340 Q200 354 228 340" fill="none" stroke="{SHIRT_D}" stroke-width="7" stroke-linecap="round"/>'
             f'{rocket(206, 432, 1.35, 35)}')
    shorts = (f'<path d="M114 500 L286 500 L292 562 Q252 570 210 562 L200 540 L190 562 Q148 570 108 562z" fill="{G("shorts")}"/>'
              f'<path d="M200 540 L200 512" stroke="{SHORTS_D}" stroke-width="3" opacity="0.6"/>')
    neck = f'<rect x="180" y="300" width="40" height="46" rx="14" fill="{SKIN_D}"/>'
    return f'<g class="mo-body">{neck}{shorts}{torso}</g>'


def mo_svg(extra_defs=True):
    shadow = '<ellipse cx="200" cy="630" rx="120" ry="14" fill="url(#mo-shade)"/>'
    parts = shadow + leg("r") + leg("l") + body() + arm("r") + arm("l") + head()
    # arms behind the torso, so draw body after arms; head last
    return (f'<svg class="mo2d" viewBox="0 0 400 640" xmlns="http://www.w3.org/2000/svg" overflow="visible">'
            f'<defs>{defs() if extra_defs else ""}</defs>{parts}</svg>')


PIVOTS = {  # transform-origin in viewBox px
    "mo-head": (200, 318), "mo-hair-tuft": (216, 60), "mo-body": (200, 520),
    "mo-arm-r": (112, 362), "mo-fore-r": (76, 432), "mo-arm-l": (288, 362), "mo-fore-l": (324, 432),
    "mo-leg-r": (160, 548), "mo-leg-l": (240, 548),
}

if __name__ == "__main__":
    import sys
    open(sys.argv[1] if len(sys.argv) > 1 else "mo2d.svg", "w").write(mo_svg())
