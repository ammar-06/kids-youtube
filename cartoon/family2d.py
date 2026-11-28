"""The rest of the 2D family, drawn after the Gemini designs in the same soft-shaded style as mo2d.py.

Each character is a front-facing rigged SVG, feet on the bottom of its viewBox. Class names use the character's
prefix (gp = Grandpa ...). Parts:
  .{p}-head .{p}-arm-r .{p}-fore-r .{p}-arm-l .{p}-fore-l .{p}-leg-r .{p}-leg-l .{p}-body
  .{p}-lid (blink, scaleY 0->1 from the top) .{p}-pupils .{p}-brows
  .{p}-m-smile .{p}-m-open .{p}-m-o .{p}-m-wide (mouth shapes)
plus extras per character (Grandpa: .gp-hat, .gp-stache).
'r' / 'l' are the character's own sides (his right is on screen-left).
PIVOTS[character][part] = (x, y) in viewBox units, for GSAP svgOrigin.
"""
import math


def radial(pid, name, a, b, c, cx="40%", cy="32%", r="75%"):
    return (f'<radialGradient id="{pid}-{name}" cx="{cx}" cy="{cy}" r="{r}"><stop offset="0" stop-color="{a}"/>'
            f'<stop offset="0.55" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></radialGradient>')


def common_defs(pid):
    return (f'<radialGradient id="{pid}-blush" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#ff6f6f" stop-opacity="0.42"/>'
            f'<stop offset="1" stop-color="#ff6f6f" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="{pid}-shade" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#000" stop-opacity="0.28"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>')


def eye(pid, cx, cy, rx, ry, iris_r, side, skin_grad, iris=("#8a5530", "#5c341a", "#2c160a"), lid_line=True):
    clip = f"{pid}-eclip-{side}"
    out = (f'<g class="{pid}-eye">'
           f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{pid}-sclera)"/>'
           f'<clipPath id="{clip}"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath>'
           f'<g clip-path="url(#{clip})"><g class="{pid}-pupils">'
           f'<circle cx="{cx}" cy="{cy + iris_r * 0.12:.1f}" r="{iris_r}" fill="url(#{pid}-iris)"/>'
           f'<circle cx="{cx}" cy="{cy + iris_r * 0.16:.1f}" r="{iris_r * 0.5:.1f}" fill="#120906"/>'
           f'<ellipse cx="{cx + iris_r * 0.36:.1f}" cy="{cy - iris_r * 0.34:.1f}" rx="{iris_r * 0.34:.1f}" ry="{iris_r * 0.3:.1f}" fill="#fff"/>'
           f'<circle cx="{cx - iris_r * 0.34:.1f}" cy="{cy + iris_r * 0.48:.1f}" r="{iris_r * 0.14:.1f}" fill="#fff" opacity="0.9"/>'
           f'</g>'
           f'<ellipse cx="{cx}" cy="{cy - ry - 3}" rx="{rx + 3}" ry="{ry * 0.45:.1f}" fill="#000" opacity="0.12"/>'
           f'<rect class="{pid}-lid" x="{cx - rx - 2}" y="{cy - ry - 2}" width="{2 * rx + 4}" height="{2 * ry + 4}" fill="url(#{skin_grad})" transform="matrix(1 0 0 0.001 0 {(cy - ry - 2) * 0.999:.2f})"/>'
           f'</g>')
    if lid_line:
        out += (f'<path d="M{cx - rx + 2} {cy - ry * 0.5:.1f} Q{cx} {cy - ry - 6:.1f} {cx + rx - 2} {cy - ry * 0.5:.1f}" fill="none" '
                f'stroke="#2b1a14" stroke-width="3" stroke-linecap="round" opacity="0.85"/>')
    return out + '</g>'


def mouths(pid, cx, cy, s=1.0, smile_col="#9b3b33"):
    def P(d):
        return d
    w = 26 * s
    smile = f'<path d="M{cx - w:.1f} {cy - 4 * s:.1f} Q{cx} {cy + 16 * s:.1f} {cx + w:.1f} {cy - 4 * s:.1f}" fill="none" stroke="{smile_col}" stroke-width="{4.5 * s:.1f}" stroke-linecap="round"/>'
    opn = (f'<path d="M{cx - 24 * s:.1f} {cy - 6 * s:.1f} Q{cx} {cy - s:.1f} {cx + 24 * s:.1f} {cy - 6 * s:.1f} Q{cx + 20 * s:.1f} {cy + 26 * s:.1f} {cx} {cy + 27 * s:.1f} '
           f'Q{cx - 20 * s:.1f} {cy + 26 * s:.1f} {cx - 24 * s:.1f} {cy - 6 * s:.1f}z" fill="#6e1d22"/>'
           f'<ellipse cx="{cx}" cy="{cy + 18 * s:.1f}" rx="{13 * s:.1f}" ry="{7 * s:.1f}" fill="#ff7d86"/>')
    o = (f'<ellipse cx="{cx}" cy="{cy + 6 * s:.1f}" rx="{12 * s:.1f}" ry="{16 * s:.1f}" fill="#6e1d22"/>'
         f'<ellipse cx="{cx}" cy="{cy + 14 * s:.1f}" rx="{8 * s:.1f}" ry="{5 * s:.1f}" fill="#ff7d86"/>')
    wide = (f'<path d="M{cx - 32 * s:.1f} {cy - 8 * s:.1f} Q{cx} {cy - 2 * s:.1f} {cx + 32 * s:.1f} {cy - 8 * s:.1f} Q{cx + 28 * s:.1f} {cy + 34 * s:.1f} {cx} {cy + 35 * s:.1f} '
            f'Q{cx - 28 * s:.1f} {cy + 34 * s:.1f} {cx - 32 * s:.1f} {cy - 8 * s:.1f}z" fill="#6e1d22"/>'
            f'<ellipse cx="{cx}" cy="{cy + 24 * s:.1f}" rx="{17 * s:.1f}" ry="{9 * s:.1f}" fill="#ff7d86"/>')
    return (f'<g class="{pid}-m-smile">{smile}</g><g class="{pid}-m-open" opacity="0">{opn}</g>'
            f'<g class="{pid}-m-o" opacity="0">{o}</g><g class="{pid}-m-wide" opacity="0">{wide}</g>')


def limb(x0, y0, x1, y1, w, col, dark, light, sg):
    return (f'<path d="M{x0} {y0} L{x1} {y1}" stroke="{dark}" stroke-width="{w + 3}" stroke-linecap="round"/>'
            f'<path d="M{x0} {y0} L{x1} {y1}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="M{x0 - sg * 4} {y0} L{x1 - sg * 4} {y1}" stroke="{light}" stroke-width="{w * 0.3:.0f}" stroke-linecap="round" opacity="0.5"/>')


def hand(hx, hy, sg, col, dark, s=1.0):
    return (f'<g transform="translate({hx} {hy}) rotate({-sg * 28}) scale({s})">'
            f'<path d="M-15 -4 Q-17 22 -6 30 Q4 36 13 28 Q19 16 16 -4 Q0 -12 -15 -4z" fill="{col}" stroke="{dark}" stroke-width="2"/>'
            f'<path d="M{-sg * 14} 0 Q{-sg * 26} 8 {-sg * 20} 18 Q{-sg * 14} 16 {-sg * 11} 10" fill="{col}" stroke="{dark}" stroke-width="2"/>'
            f'<path d="M-6 22 v6 M1 24 v7 M8 22 v6" stroke="{dark}" stroke-width="1.8" stroke-linecap="round" opacity="0.7"/>'
            f'</g>')


def fluff_path(cx, cy, rx, ry, a0, a1, n, bump):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        r = 1 + (bump if i % 2 else 0)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1, 2):
        d += f" Q{pts[i][0]:.1f} {pts[i][1]:.1f} {pts[i + 1][0]:.1f} {pts[i + 1][1]:.1f}"
    return d


# =============================================================================================== Grandpa
GP_SKIN, GP_SKIN_D, GP_SKIN_L = "#d7a07a", "#b27852", "#eec3a0"
GP_DENIM, GP_DENIM_D = "#46619e", "#33497e"


def grandpa():
    """Grandpa (Old MacDonald). viewBox 0 0 480 900, boots on y=893."""
    p = "gp"
    defs = (radial(p, "skin", GP_SKIN_L, GP_SKIN, GP_SKIN_D) + radial(p, "sclera", "#ffffff", "#fbfaf9", "#e3dfdc")
            + radial(p, "iris", "#7a4a2a", "#4e2c16", "#24120a") + radial(p, "beard", "#ffffff", "#f3f1ee", "#cfcac4")
            + radial(p, "nose", "#ff8f86", "#e8574f", "#b83a34") + radial(p, "hat", "#f2d79a", "#dcb46a", "#b48a44")
            + radial(p, "denim", "#5c79b8", GP_DENIM, GP_DENIM_D) + radial(p, "boot", "#a8714a", "#7c4a2b", "#4e2c17")
            + common_defs(p)
            + f'<pattern id="{p}-ging" width="22" height="22" patternUnits="userSpaceOnUse">'
              f'<rect width="22" height="22" fill="#fff4f2"/><rect width="22" height="11" fill="#e8443f" opacity="0.55"/>'
              f'<rect width="11" height="22" fill="#e8443f" opacity="0.55"/></pattern>'
            + radial(p, "gshade", "#ffffff", "#ffffff", "#000000"))
    sh = f'<ellipse cx="240" cy="893" rx="150" ry="16" fill="url(#{p}-shade)"/>'

    def leg(side):
        sg = -1 if side == "r" else 1
        x = 240 + sg * 54
        return (f'<g class="{p}-leg-{side}">'
                f'<rect x="{x - 52}" y="700" width="104" height="112" rx="30" fill="url(#{p}-denim)"/>'
                f'<path d="M{x - 52 + sg * 4} 893 Q{x - 54 + sg * 4} 790 {x + sg * 2} 784 Q{x + 54 + sg * 4} 790 {x + 52 + sg * 4} 893z" fill="url(#{p}-boot)"/>'
                f'<rect x="{x - 54 + sg * 4}" y="882" width="108" height="12" rx="6" fill="#3a2214"/>'
                f'<path d="M{x - 44 + sg * 4} 800 Q{x + sg * 4} 790 {x + 44 + sg * 4} 800" fill="none" stroke="#a8714a" stroke-width="5" stroke-linecap="round" opacity="0.7"/>'
                f'</g>')

    def arm(side):
        sg = -1 if side == "r" else 1
        sx, sy = 240 + sg * 118, 462
        ex, ey = 240 + sg * 156, 560
        hx, hy = 240 + sg * 178, 650
        fore = (f'<g class="{p}-fore-{side}">{limb(ex, ey, hx, hy, 34, GP_SKIN, GP_SKIN_D, GP_SKIN_L, sg)}'
                f'{hand(hx, hy, sg, GP_SKIN, GP_SKIN_D, 1.35)}'
                # rolled cuff
                f'<path d="M{ex - 24} {ey - 4} L{ex + 24} {ey - 4} L{ex + 26} {ey + 18} L{ex - 26} {ey + 18}z" fill="url(#{p}-ging)" transform="rotate({-sg * 20} {ex} {ey})"/>'
                f'</g>')
        upper = (f'<path d="M{sx} {sy} L{ex} {ey}" stroke="#c23a35" stroke-width="47" stroke-linecap="round"/>'
                 f'<path d="M{sx} {sy} L{ex} {ey}" stroke="url(#{p}-ging)" stroke-width="44" stroke-linecap="round"/>')
        return f'<g class="{p}-arm-{side}">{fore}{upper}</g>'

    shirt = (f'<path d="M140 450 Q240 430 340 450 Q372 462 378 500 L362 690 Q240 712 118 690 L102 500 Q108 462 140 450z" fill="url(#{p}-ging)"/>'
             f'<path d="M140 450 Q240 430 340 450 Q372 462 378 500 L362 690 Q240 712 118 690 L102 500 Q108 462 140 450z" fill="#000" opacity="0.06"/>'
             f'<path d="M206 440 L240 476 L274 440" fill="#fff4f2" stroke="#c23a35" stroke-width="3"/>')
    overalls = (f'<path d="M150 500 L330 500 L338 600 Q350 640 350 770 L244 770 L240 742 L236 770 L130 770 Q130 640 142 600z" fill="url(#{p}-denim)"/>'
                f'<path d="M150 500 L188 452 M330 500 L292 452" stroke="{GP_DENIM_D}" stroke-width="30" stroke-linecap="round"/>'
                f'<path d="M150 500 L188 452 M330 500 L292 452" stroke="{GP_DENIM}" stroke-width="24" stroke-linecap="round"/>'
                f'<circle cx="168" cy="512" r="12" fill="#ffd23a" stroke="#c9a114" stroke-width="3"/>'
                f'<circle cx="312" cy="512" r="12" fill="#ffd23a" stroke="#c9a114" stroke-width="3"/>'
                f'<rect x="196" y="540" width="88" height="66" rx="12" fill="{GP_DENIM}" stroke="#8aa3d6" stroke-width="2.5" stroke-dasharray="6 5"/>'
                f'<path d="M150 600 Q240 612 330 600" fill="none" stroke="#8aa3d6" stroke-width="2.5" stroke-dasharray="6 5" opacity="0.8"/>'
                f'<path d="M240 660 L240 742" stroke="{GP_DENIM_D}" stroke-width="4"/>')
    body = f'<g class="{p}-body">{shirt}{overalls}</g>'

    cx = 240
    ears = "".join(f'<ellipse cx="{x}" cy="250" rx="24" ry="34" fill="url(#{p}-skin)"/>'
                   f'<ellipse cx="{x + (5 if x < cx else -5)}" cy="252" rx="11" ry="18" fill="{GP_SKIN_D}" opacity="0.5"/>' for x in (100, 380))
    face = f'<ellipse cx="{cx}" cy="262" rx="140" ry="132" fill="url(#{p}-skin)"/>'
    side_hair = "".join(f'<path d="M{x} 200 q{-s * 22} 40 {-s * 8} 96 q{s * 14} -10 {s * 20} -40 q{-s * 2} -30 {-s * 12} -56z" fill="url(#{p}-beard)"/>' for x, s in ((116, 1), (364, -1)))
    cheeks = f'<ellipse cx="146" cy="262" rx="30" ry="22" fill="url(#{p}-blush)"/><ellipse cx="334" cy="262" rx="30" ry="22" fill="url(#{p}-blush)"/>'
    eyes = eye(p, 190, 222, 19, 21, 17, "r", f"{p}-skin") + eye(p, 290, 222, 19, 21, 17, "l", f"{p}-skin")
    brows = (f'<g class="{p}-brows">'
             f'<path d="{fluff_path(186, 186, 40, 17, 180, 360, 10, 0.18)} Q206 196 186 196 Q160 198 146 186z" fill="url(#{p}-beard)"/>'
             f'<path d="{fluff_path(294, 186, 40, 17, 180, 360, 10, 0.18)} Q316 198 294 196 Q272 196 254 186z" fill="url(#{p}-beard)"/></g>')
    beard = (f'<path d="M104 250 Q102 360 160 410 Q200 446 240 448 Q280 446 320 410 Q378 360 376 250 '
             f'Q350 300 300 302 Q240 296 180 302 Q130 300 104 250z" fill="url(#{p}-beard)"/>'
             + "".join(f'<path d="M{x} {y} q{dx} 14 0 28" fill="none" stroke="#d8d3cc" stroke-width="3" stroke-linecap="round"/>'
                       for x, y, dx in ((150, 340, -6), (190, 380, -5), (240, 400, 0), (290, 380, 5), (330, 340, 6), (214, 350, -4), (266, 350, 4))))
    mouth = f'<g class="{p}-mouth">{mouths(p, cx, 318, 0.75)}</g>'
    stache = (f'<g class="{p}-stache"><g transform="translate(240 300) scale(1.35) translate(-240 -300)"><path d="M240 290 Q206 272 176 286 Q150 300 160 322 Q190 314 214 318 Q232 316 240 306 '
              f'Q248 316 266 318 Q290 314 320 322 Q330 300 304 286 Q274 272 240 290z" fill="url(#{p}-beard)"/>'
              f'<path d="M188 300 q20 -6 40 2 M252 302 q20 -8 40 -2" fill="none" stroke="#d8d3cc" stroke-width="3" stroke-linecap="round"/></g></g>')
    nose = (f'<circle cx="{cx}" cy="266" r="30" fill="url(#{p}-nose)"/>'
            f'<ellipse cx="{cx - 9}" cy="256" rx="10" ry="7" fill="#fff" opacity="0.4"/>')
    crown = "M144 128 Q142 14 240 2 Q338 14 336 128 Q240 150 144 128z"
    hat = (f'<g class="{p}-hat"><g transform="translate(0 -16)">'
           f'<ellipse cx="{cx}" cy="134" rx="212" ry="48" fill="url(#{p}-hat)"/>'
           f'<path d="M28 138 Q240 196 452 138" fill="none" stroke="#b48a44" stroke-width="4" opacity="0.5"/>'
           f'<clipPath id="{p}-crown"><path d="{crown}"/></clipPath>'
           f'<path d="{crown}" fill="url(#{p}-hat)"/>'
           f'<g clip-path="url(#{p}-crown)">'
           + "".join(f'<path d="M{x} 0 Q{x + (x - cx) * 0.12:.0f} 70 {x + (x - cx) * 0.08:.0f} 140" fill="none" stroke="#c99f55" stroke-width="2" opacity="0.5"/>' for x in range(168, 320, 22))
           + f'<path d="M140 94 Q240 116 340 94 L340 118 Q240 140 140 118z" fill="#d8322c"/></g>'
           f'</g></g>')
    head = f'<g class="{p}-head">{ears}{face}{side_hair}{cheeks}{eyes}{brows}{beard}{mouth}{stache}{nose}{hat}</g>'
    body_all = sh + leg("r") + leg("l") + body + arm("r") + arm("l") + head
    return (f'<svg class="grandpa2d" viewBox="0 0 480 900" xmlns="http://www.w3.org/2000/svg" overflow="visible">'
            f'<defs>{defs}</defs>{body_all}</svg>')


# =============================================================================================== Biscuit
BS_FUR, BS_FUR_D, BS_FUR_L, BS_WHITE = "#d9a15a", "#b07535", "#f2c784", "#fbf0de"


def biscuit():
    """Biscuit the puppy, standing upright. viewBox 0 0 420 640, feet on y=630."""
    p = "bs"
    defs = (radial(p, "fur", BS_FUR_L, BS_FUR, BS_FUR_D) + radial(p, "white", "#ffffff", BS_WHITE, "#e4d3bb")
            + radial(p, "sclera", "#ffffff", "#fbfaf9", "#e3dfdc") + radial(p, "iris", "#e39a44", "#b56a22", "#5e300c")
            + radial(p, "nose", "#6a4a40", "#3e2620", "#1e100c") + radial(p, "collar", "#ff6a5e", "#d8322c", "#9e1d18")
            + radial(p, "bone", "#fff3a0", "#ffd23a", "#d9a10e") + radial(p, "pad", "#9a7466", "#7a5446", "#55362a")
            + common_defs(p))
    F = f"url(#{p}-fur)"
    sh = f'<ellipse cx="210" cy="630" rx="120" ry="13" fill="url(#{p}-shade)"/>'
    tail = (f'<g class="{p}-tail"><path d="M118 500 Q70 490 62 440 Q58 400 82 388 Q92 420 100 446 Q110 474 132 478z" fill="{F}"/></g>')

    def leg(side):
        sg = -1 if side == "r" else 1
        x = 210 + sg * 46
        return (f'<g class="{p}-leg-{side}">'
                f'<rect x="{x - 33}" y="496" width="66" height="116" rx="28" fill="{F}"/>'
                f'<ellipse cx="{x + sg * 4}" cy="612" rx="44" ry="22" fill="{F}"/>'
                f'<path d="M{x - 14 + sg * 4} 600 v18 M{x + 14 + sg * 4} 600 v18" stroke="{BS_FUR_D}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>'
                f'</g>')

    def arm(side):
        sg = -1 if side == "r" else 1
        sx, sy = 210 + sg * 72, 328
        ex, ey = 210 + sg * 112, 386
        hx, hy = 210 + sg * 138, 432
        paw = (f'<g transform="translate({hx} {hy})">'
               f'<ellipse cx="0" cy="6" rx="30" ry="28" fill="{F}"/>'
               f'<ellipse cx="{sg * 2}" cy="12" rx="13" ry="11" fill="url(#{p}-pad)"/>'
               + "".join(f'<circle cx="{dx}" cy="{dy}" r="5.5" fill="url(#{p}-pad)"/>' for dx, dy in ((-14, -6), (-4, -12), (8, -11), (17, -3)))
               + '</g>')
        fore = f'<g class="{p}-fore-{side}">{limb(ex, ey, hx, hy, 40, BS_FUR, BS_FUR_D, BS_FUR_L, sg)}{paw}</g>'
        return f'<g class="{p}-arm-{side}">{fore}{limb(sx, sy, ex, ey, 44, BS_FUR, BS_FUR_D, BS_FUR_L, sg)}</g>'

    torso = (f'<ellipse cx="210" cy="290" rx="86" ry="44" fill="{F}"/>'
             f'<path d="M134 296 Q210 280 286 296 Q306 380 300 460 Q294 530 210 540 Q126 530 120 460 Q114 380 134 296z" fill="{F}"/>'
             f'<ellipse cx="210" cy="430" rx="56" ry="78" fill="{BS_FUR_L}" opacity="0.45"/>')
    collar = (f'<path d="M128 282 Q210 310 292 282 L294 304 Q210 334 126 304z" fill="url(#{p}-collar)"/>'
              f'<path d="M210 318 v16" stroke="#c9a114" stroke-width="3"/>'
              f'<g transform="translate(210 344)"><path d="M-22 -6 a7 7 0 1 1 6 -6 h32 a7 7 0 1 1 6 6 a7 7 0 1 1 -6 6 h-32 a7 7 0 1 1 -6 -6z" fill="url(#{p}-bone)"/></g>')
    body = f'<g class="{p}-body">{torso}{collar}</g>'

    cx, cy = 210, 160
    ears = (f'<g class="{p}-ear-r"><path d="M112 70 Q50 70 30 140 Q16 200 50 228 Q84 236 100 200 Q112 150 132 110z" fill="{F}"/>'
            f'<path d="M100 96 Q60 110 50 160 Q44 200 62 212 Q84 212 92 180 Q100 140 112 110z" fill="url(#{p}-white)"/></g>'
            f'<g class="{p}-ear-l"><path d="M308 70 Q370 70 390 140 Q404 200 370 228 Q336 236 320 200 Q308 150 288 110z" fill="{F}"/></g>')
    face = (f'<path d="{fluff_path(cx, cy, 116, 112, 0, 360, 36, 0.035)}z" fill="{F}"/>'
            f'<ellipse cx="270" cy="118" rx="58" ry="66" fill="url(#{p}-white)" transform="rotate(-18 270 118)"/>'
            f'<ellipse cx="{cx}" cy="212" rx="62" ry="44" fill="{BS_FUR_L}" opacity="0.7"/>')
    cheeks = f'<ellipse cx="132" cy="206" rx="24" ry="16" fill="url(#{p}-blush)"/><ellipse cx="288" cy="206" rx="24" ry="16" fill="url(#{p}-blush)"/>'
    eyes = eye(p, 152, 140, 29, 31, 26, "r", f"{p}-fur", lid_line=True) + eye(p, 266, 140, 29, 31, 26, "l", f"{p}-white", lid_line=True)
    brows = (f'<g class="{p}-brows"><path d="M128 98 Q148 86 170 94" fill="none" stroke="{BS_FUR_D}" stroke-width="5" stroke-linecap="round"/>'
             f'<path d="M246 94 Q268 86 290 98" fill="none" stroke="#c9a77a" stroke-width="5" stroke-linecap="round"/></g>')
    nose = (f'<ellipse cx="{cx}" cy="192" rx="27" ry="20" fill="url(#{p}-nose)"/>'
            f'<ellipse cx="{cx - 8}" cy="184" rx="9" ry="5" fill="#fff" opacity="0.35"/>'
            f'<path d="M{cx} 210 v10" stroke="#5a3a30" stroke-width="3.5" stroke-linecap="round"/>')
    mouth = f'<g class="{p}-mouth">{mouths(p, cx, 230, 0.8)}</g>'
    head = f'<g class="{p}-head">{ears}{face}{cheeks}{eyes}{brows}{mouth}{nose}</g>'
    allp = sh + tail + leg("r") + leg("l") + body + arm("r") + arm("l") + head
    return (f'<svg class="biscuit2d" viewBox="0 0 420 640" xmlns="http://www.w3.org/2000/svg" overflow="visible">'
            f'<defs>{defs}</defs>{allp}</svg>')


PIVOTS = {
    "grandpa": {"gp-head": (240, 440), "gp-hat": (240, 170), "gp-body": (240, 700),
                "gp-arm-r": (122, 462), "gp-fore-r": (84, 560), "gp-arm-l": (358, 462), "gp-fore-l": (396, 560),
                "gp-leg-r": (186, 708), "gp-leg-l": (294, 708), "gp-stache": (240, 300)},
    "biscuit": {"bs-head": (210, 290), "bs-body": (210, 540), "bs-tail": (124, 488),
                "bs-arm-r": (138, 328), "bs-fore-r": (98, 386), "bs-arm-l": (282, 328), "bs-fore-l": (322, 386),
                "bs-leg-r": (164, 506), "bs-leg-l": (256, 506), "bs-ear-r": (116, 90), "bs-ear-l": (304, 90)},
}

CHARS = {"grandpa": grandpa, "biscuit": biscuit}

if __name__ == "__main__":
    import sys
    n = sys.argv[1] if len(sys.argv) > 1 else "grandpa"
    open(n + "2d.svg", "w").write(CHARS[n]())
