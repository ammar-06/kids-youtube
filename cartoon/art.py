"""Vector cartoon art for the kids videos: a farm background, a farmer and farm animals.

Every character is an SVG string (viewBox 0 0 400 400, feet on y=380, facing right) built from named parts the
animation moves: .eyes (blink), .mouth-shut / .mouth-open (sing, make the sound), .head (tilt), .tail, .arm.
No ids inside characters, so the same animal can be drawn many times at once.
"""

INK = "#4a3428"          # outline colour for everything
SW = 6                   # outline width


def _s(fill, w=SW):
    return f'fill="{fill}" stroke="{INK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def eye(cx, cy, r=15):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * 1.15:.1f}" {_s("#fff", w=4)}/>'
            f'<circle cx="{cx + r * 0.2:.1f}" cy="{cy + r * 0.15:.1f}" r="{r * 0.62:.1f}" fill="#2b1d16"/>'
            f'<circle cx="{cx + r * 0.42:.1f}" cy="{cy - r * 0.2:.1f}" r="{r * 0.24:.1f}" fill="#fff"/>')


def eyes(*pts, r=15):
    return '<g class="eyes">' + "".join(eye(x, y, r) for x, y in pts) + "</g>"


def cheek(cx, cy, r=12):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * 0.7:.1f}" fill="#ff8fa3" opacity="0.55"/>'


def mouths(shut, open_):
    return f'<g class="mouth-shut">{shut}</g><g class="mouth-open" opacity="0">{open_}</g>'


def open_mouth(cx, cy, w=26, h=22):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{w}" ry="{h}" {_s("#8c2a2a", w=5)}/>'
            f'<ellipse cx="{cx}" cy="{cy + h * 0.45:.1f}" rx="{w * 0.6:.1f}" ry="{h * 0.38:.1f}" fill="#ff7b8a"/>')


def smile(x1, y1, x2, y2, depth=14):
    mx = (x1 + x2) / 2
    return f'<path d="M{x1} {y1} Q{mx} {y1 + depth} {x2} {y2}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'


def leg(x, top, bottom, w, fill, hoof="#6b5444"):
    return (f'<rect x="{x - w / 2}" y="{top}" width="{w}" height="{bottom - top}" rx="{w / 2.4:.1f}" {_s(fill)}/>'
            f'<rect x="{x - w / 2 - 2}" y="{bottom - 22}" width="{w + 4}" height="24" rx="8" {_s(hoof)}/>')


def shadow(cx=200, w=150):
    return f'<ellipse cx="{cx}" cy="384" rx="{w}" ry="14" fill="#2f5d1e" opacity="0.22"/>'


def wrap(body):
    return f'<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" overflow="visible">{body}</svg>'


# ------------------------------------------------------------------------------------------------ animals
def cow():
    spots = (f'<path d="M150 200 q30 -20 55 0 q10 30 -20 40 q-35 5 -35 -40z" fill="#3a2c26"/>'
             f'<path d="M95 255 q20 -15 35 5 q0 25 -25 25 q-20 -5 -10 -30z" fill="#3a2c26"/>'
             f'<path d="M230 265 q25 -10 35 10 q-5 22 -30 18 q-15 -10 -5 -28z" fill="#3a2c26"/>')
    head = (f'<g class="head">'
            f'<ellipse cx="245" cy="118" rx="26" ry="14" transform="rotate(-30 245 118)" {_s("#e9c9b8")}/>'
            f'<ellipse cx="350" cy="118" rx="26" ry="14" transform="rotate(30 350 118)" {_s("#e9c9b8")}/>'
            f'<path d="M262 98 q-10 -28 6 -40 q6 18 12 34z" {_s("#fff3c4")}/>'
            f'<path d="M332 98 q10 -28 -6 -40 q-6 18 -12 34z" {_s("#fff3c4")}/>'
            f'<ellipse cx="298" cy="140" rx="66" ry="62" {_s("#ffffff")}/>'
            f'<path d="M262 104 q20 -14 40 0 q-6 22 -22 22 q-16 -4 -18 -22z" fill="#3a2c26"/>'
            f'{eyes((275, 138), (322, 138), r=13)}'
            f'<ellipse cx="300" cy="186" rx="52" ry="34" {_s("#f7b3c2")}/>'
            f'<ellipse cx="282" cy="180" rx="7" ry="9" fill="#8a4a55"/><ellipse cx="318" cy="180" rx="7" ry="9" fill="#8a4a55"/>'
            + mouths(smile(282, 200, 318, 200, 10), open_mouth(300, 204, 18, 13)) +
            f'</g>')
    return wrap(shadow(200, 160)
                + f'<path class="tail" d="M78 220 q-40 30 -30 90" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
                + f'<ellipse class="tail" cx="48" cy="318" rx="12" ry="16" fill="#3a2c26"/>'
                + leg(105, 270, 378, 40, "#fff") + leg(250, 270, 378, 40, "#fff")
                + f'<ellipse cx="185" cy="240" rx="125" ry="78" {_s("#ffffff")}/>' + spots
                + f'<ellipse cx="160" cy="312" rx="28" ry="16" {_s("#f7b3c2")}/>'
                + leg(150, 290, 380, 40, "#fff") + leg(290, 280, 380, 40, "#fff")
                + f'<path d="M262 205 l-6 24 h28 l-6 -24z" {_s("#f2c230")}/>'
                + head)


def pig():
    head = (f'<g class="head">'
            f'<path d="M248 92 l-6 -44 l40 26z" {_s("#f6a5b5")}/>'
            f'<path d="M340 92 l14 -42 l-44 22z" {_s("#f6a5b5")}/>'
            f'<circle cx="295" cy="140" r="66" {_s("#f9bccb")}/>'
            f'{eyes((268, 126), (320, 126), r=12)}'
            f'{cheek(254, 165)}{cheek(338, 165)}'
            f'<ellipse cx="296" cy="168" rx="36" ry="25" {_s("#f6a0b2")}/>'
            f'<ellipse cx="284" cy="168" rx="6" ry="9" fill="#a8546a"/><ellipse cx="308" cy="168" rx="6" ry="9" fill="#a8546a"/>'
            + mouths(smile(278, 200, 314, 200, 9), open_mouth(296, 205, 17, 12)) +
            f'</g>')
    return wrap(shadow(200, 150)
                + f'<path class="tail" d="M70 225 q-30 -12 -26 12 q6 22 -20 18" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
                + leg(110, 280, 378, 38, "#f9bccb", "#d27f93") + leg(250, 280, 378, 38, "#f9bccb", "#d27f93")
                + f'<ellipse cx="180" cy="250" rx="125" ry="88" {_s("#f9bccb")}/>'
                + f'<ellipse cx="150" cy="225" rx="50" ry="22" fill="#fff" opacity="0.35"/>'
                + leg(150, 300, 380, 38, "#f9bccb", "#d27f93") + leg(285, 290, 380, 38, "#f9bccb", "#d27f93")
                + head)


def duck():
    head = (f'<g class="head">'
            f'<circle cx="250" cy="150" r="62" {_s("#ffd83d")}/>'
            f'{eyes((236, 136), (278, 138), r=12)}'
            f'{cheek(222, 170, 10)}'
            + mouths(f'<path d="M282 162 q52 -8 66 10 q-10 22 -66 16z" {_s("#ff9a2e")}/>',
                     f'<path d="M282 154 q55 -22 70 -6 q-14 18 -70 16z" {_s("#ff9a2e")}/>'
                     f'<path d="M282 174 q50 6 62 24 q-20 14 -62 -6z" {_s("#ff9a2e")}/>') +
            f'</g>')
    feet = (f'<path d="M150 360 l-24 20 h52z" {_s("#ff9a2e")}/><path d="M215 360 l-24 20 h52z" {_s("#ff9a2e")}/>'
            f'<rect x="146" y="320" width="10" height="44" fill="#ff9a2e" stroke="{INK}" stroke-width="4"/>'
            f'<rect x="211" y="320" width="10" height="44" fill="#ff9a2e" stroke="{INK}" stroke-width="4"/>')
    return wrap(shadow(190, 120) + feet
                + f'<path class="tail" d="M88 240 l-40 -30 l20 50z" {_s("#ffd83d")}/>'
                + f'<ellipse cx="180" cy="262" rx="105" ry="74" {_s("#ffd83d")}/>'
                + f'<path class="arm" d="M120 250 q60 -30 110 10 q-50 40 -110 -10z" {_s("#ffc21a")}/>'
                + head)


def sheep():
    puffs = [(110, 220), (150, 195), (200, 190), (245, 205), (270, 245), (250, 290), (200, 305), (145, 300),
             (100, 275), (175, 250), (220, 250)]
    wool = "".join(f'<circle cx="{x}" cy="{y}" r="42" {_s("#fffdf6")}/>' for x, y in puffs[:-2])
    wool += "".join(f'<circle cx="{x}" cy="{y}" r="44" fill="#fffdf6"/>' for x, y in puffs[-2:])
    head = (f'<g class="head">'
            f'<ellipse cx="262" cy="140" rx="24" ry="13" transform="rotate(-25 262 140)" {_s("#4b3b35")}/>'
            f'<ellipse cx="352" cy="140" rx="24" ry="13" transform="rotate(25 352 140)" {_s("#4b3b35")}/>'
            f'<ellipse cx="306" cy="160" rx="50" ry="58" {_s("#5a4740")}/>'
            f'<circle cx="290" cy="104" r="22" {_s("#fffdf6")}/><circle cx="320" cy="100" r="22" {_s("#fffdf6")}/>'
            f'<circle cx="305" cy="92" r="20" fill="#fffdf6"/>'
            f'{eyes((288, 150), (325, 150), r=12)}'
            f'{cheek(280, 182, 9)}{cheek(334, 182, 9)}'
            + mouths(smile(294, 196, 318, 196, 8), open_mouth(306, 200, 14, 11)) +
            f'</g>')
    return wrap(shadow(200, 140)
                + leg(125, 290, 378, 26, "#5a4740", "#3a2c26") + leg(240, 290, 378, 26, "#5a4740", "#3a2c26")
                + wool
                + leg(160, 310, 380, 26, "#5a4740", "#3a2c26") + leg(270, 305, 380, 26, "#5a4740", "#3a2c26")
                + head)


def horse():
    mane = "".join(f'<path d="M{238 + i * 14} {58 + i * 22} q-30 6 -36 30 q20 -2 40 -12z" {_s("#7a3f1d")}/>' for i in range(5))
    head = (f'<g class="head">'
            f'<path d="M250 150 q10 -90 70 -96 q40 4 50 70 l10 70 q0 30 -40 30 h-30 q-40 -10 -60 -74z" {_s("#c98a4b")}/>'
            f'<path d="M282 62 l-8 -38 l30 26z" {_s("#c98a4b")}/>'
            f'<ellipse cx="345" cy="205" rx="40" ry="28" {_s("#e8b98a")}/>'
            f'<ellipse cx="335" cy="203" rx="5" ry="8" fill="#7a4a2a"/><ellipse cx="358" cy="203" rx="5" ry="8" fill="#7a4a2a"/>'
            f'{eyes((300, 118), (340, 122), r=12)}'
            f'<path d="M300 50 q20 -18 38 6 q-14 16 -30 18z" {_s("#7a3f1d")}/>'
            + mouths(smile(328, 224, 360, 222, 7), open_mouth(345, 228, 16, 10)) +
            f'</g>')
    return wrap(shadow(200, 160)
                + f'<path class="tail" d="M70 210 q-46 30 -34 110 q20 -30 30 -60 q10 -30 24 -40z" {_s("#7a3f1d")}/>'
                + leg(100, 260, 378, 32, "#c98a4b", "#5a3a26") + leg(240, 260, 378, 32, "#c98a4b", "#5a3a26")
                + f'<ellipse cx="170" cy="235" rx="115" ry="68" {_s("#c98a4b")}/>'
                + f'<path d="M230 205 q10 -60 40 -90 l40 40 q-20 40 -30 90z" {_s("#c98a4b")}/>'
                + mane
                + leg(140, 275, 380, 32, "#c98a4b", "#5a3a26") + leg(270, 270, 380, 32, "#c98a4b", "#5a3a26")
                + head)


def chicken():
    head = (f'<g class="head">'
            f'<path d="M232 102 q8 -30 26 -14 q10 -26 28 -6 q16 -18 24 8 q-30 12 -78 12z" {_s("#ef3b36")}/>'
            f'<circle cx="262" cy="148" r="50" {_s("#ffffff")}/>'
            f'{eyes((250, 138), (284, 140), r=11)}'
            f'{cheek(240, 166, 9)}'
            f'<path d="M296 180 q8 18 -4 30 q-14 -8 -10 -26z" {_s("#ef3b36")}/>'
            + mouths(f'<path d="M300 148 l34 12 l-34 12z" {_s("#ffb21f")}/>',
                     f'<path d="M300 142 l36 4 l-34 12z" {_s("#ffb21f")}/><path d="M300 164 l34 10 l-34 6z" {_s("#ffb21f")}/>') +
            f'</g>')
    feet = (f'<path d="M160 330 v44 M150 378 l10 -6 l10 6 M160 372 v8" fill="none" stroke="#ff9a1f" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M215 330 v44 M205 378 l10 -6 l10 6 M215 372 v8" fill="none" stroke="#ff9a1f" stroke-width="8" stroke-linecap="round"/>')
    return wrap(shadow(190, 110) + feet
                + f'<path class="tail" d="M95 230 q-40 -50 -10 -80 q10 30 30 40 q-10 -40 20 -50 q0 40 10 60z" {_s("#ffffff")}/>'
                + f'<ellipse cx="185" cy="265" rx="95" ry="80" {_s("#ffffff")}/>'
                + f'<path class="arm" d="M130 250 q50 -30 95 10 q-40 45 -95 -10z" {_s("#f1ece4")}/>'
                + head)


def farmer():
    """Old MacDonald: viewBox 0 0 300 500, feet on y=490. The right arm (.arm) waves around the shoulder."""
    face = (f'<g class="head">'
            f'<circle cx="150" cy="150" r="62" {_s("#f6cba4")}/>'
            f'<ellipse cx="88" cy="156" rx="12" ry="18" {_s("#f6cba4")}/><ellipse cx="212" cy="156" rx="12" ry="18" {_s("#f6cba4")}/>'
            f'<path d="M92 170 q58 100 116 0 q-10 70 -58 74 q-48 -4 -58 -74z" {_s("#f4f1ea")}/>'
            f'{eyes((128, 140), (172, 140), r=11)}'
            f'<path d="M112 118 q14 -10 28 -2 M160 116 q14 -8 28 2" fill="none" stroke="#e8e2d6" stroke-width="9" stroke-linecap="round"/>'
            f'<ellipse cx="150" cy="164" rx="15" ry="12" {_s("#f0a07c")}/>'
            f'{cheek(116, 170, 11)}{cheek(184, 170, 11)}'
            + mouths(smile(134, 192, 166, 192, 8), open_mouth(150, 196, 14, 12)) +
            f'<path d="M50 112 q100 -30 200 0 q-10 14 -100 14 q-90 0 -100 -14z" {_s("#f2c34e")}/>'
            f'<path d="M92 108 q4 -70 58 -72 q54 2 58 72z" {_s("#f2c34e")}/>'
            f'<path d="M94 96 q56 12 112 0 v14 q-56 12 -112 0z" fill="#e0453a" stroke="{INK}" stroke-width="4"/>'
            f'</g>')
    body = (f'<rect x="102" y="400" width="40" height="76" rx="12" {_s("#3b5fb8")}/>'
            f'<rect x="158" y="400" width="40" height="76" rx="12" {_s("#3b5fb8")}/>'
            f'<path d="M92 478 h56 v14 h-62z" {_s("#6b4128")}/><path d="M152 478 h62 v14 h-56z" {_s("#6b4128")}/>'
            f'<path d="M86 236 q64 -26 128 0 l10 120 q-74 26 -148 0z" {_s("#e14b3d")}/>'
            f'<path d="M100 248 v24 M128 238 v30 M172 238 v30 M200 248 v24" stroke="#b8352b" stroke-width="5"/>'
            f'<path d="M96 300 h108 l8 110 h-124z" {_s("#4a74d6")}/>'
            f'<path d="M108 300 l-6 -62 M192 300 l6 -62" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M108 300 l-6 -62 M192 300 l6 -62" stroke="#4a74d6" stroke-width="5" stroke-linecap="round"/>'
            f'<rect x="128" y="318" width="44" height="34" rx="6" {_s("#3d64c2", w=4)}/>'
            f'<circle cx="112" cy="306" r="6" fill="#f2c34e"/><circle cx="188" cy="306" r="6" fill="#f2c34e"/>'
            f'<path d="M92 244 q-36 50 -26 110" fill="none" stroke="{INK}" stroke-width="34" stroke-linecap="round"/>'
            f'<path d="M92 244 q-36 50 -26 110" fill="none" stroke="#e14b3d" stroke-width="24" stroke-linecap="round"/>'
            f'<circle cx="66" cy="360" r="17" {_s("#f6cba4")}/>')
    arm = (f'<g class="arm">'
           f'<path d="M210 248 q46 -30 56 -100" fill="none" stroke="{INK}" stroke-width="34" stroke-linecap="round"/>'
           f'<path d="M210 248 q46 -30 56 -100" fill="none" stroke="#e14b3d" stroke-width="24" stroke-linecap="round"/>'
           f'<circle cx="266" cy="138" r="19" {_s("#f6cba4")}/>'
           f'</g>')
    return (f'<svg viewBox="0 0 300 500" xmlns="http://www.w3.org/2000/svg" overflow="visible">'
            f'<ellipse cx="150" cy="492" rx="110" ry="14" fill="#2f5d1e" opacity="0.22"/>'
            f'{body}{arm}{face}</svg>')


ANIMALS = {"cow": cow, "pig": pig, "duck": duck, "sheep": sheep, "horse": horse, "chicken": chicken}


# ------------------------------------------------------------------------------------------------ farm
def cloud(w=260):
    return (f'<svg viewBox="0 0 260 120" width="{w}" xmlns="http://www.w3.org/2000/svg">'
            '<g fill="#ffffff"><circle cx="70" cy="75" r="42"/><circle cx="125" cy="55" r="52"/>'
            '<circle cx="185" cy="72" r="40"/><rect x="40" y="70" width="180" height="46" rx="23"/></g></svg>')


def farm():
    """The whole 1920x1080 backdrop as one SVG (the sun and clouds are separate so they can move)."""
    flowers = ""
    import random
    rnd = random.Random(3)
    for _ in range(46):
        x, y = rnd.randint(20, 1900), rnd.randint(860, 1070)
        c = rnd.choice(["#ff6b8b", "#ffd23f", "#ffffff", "#b38bff", "#ff9f43"])
        flowers += (f'<g transform="translate({x} {y})">' + "".join(
            f'<circle cx="{8 * __import__("math").cos(a * 1.2566):.1f}" cy="{8 * __import__("math").sin(a * 1.2566):.1f}" r="6" fill="{c}"/>'
            for a in range(5)) + '<circle r="5" fill="#ffb300"/></g>')
    grass = "".join(f'<path d="M{x} {y} q4 -18 8 0 q4 -22 8 0" fill="none" stroke="#4fa83a" stroke-width="4" stroke-linecap="round"/>'
                    for x, y in ((rnd.randint(0, 1900), rnd.randint(820, 1075)) for _ in range(70)))
    fence = "".join(f'<rect x="{x}" y="700" width="22" height="110" rx="6" {_s("#fff4e0", w=4)}/>'
                    for x in range(540, 1920, 92))
    fence += (f'<rect x="530" y="725" width="1400" height="18" rx="6" {_s("#fff4e0", w=4)}/>'
              f'<rect x="530" y="770" width="1400" height="18" rx="6" {_s("#fff4e0", w=4)}/>')
    barn = (f'<g transform="translate(60 380)">'
            f'<path d="M0 170 l200 -150 l200 150 v330 h-400z" {_s("#e0473c")}/>'
            f'<path d="M-24 186 l224 -176 l224 176" fill="none" stroke="#fff4e0" stroke-width="22" stroke-linejoin="round"/>'
            f'<path d="M-24 186 l224 -176 l224 176" fill="none" stroke="{INK}" stroke-width="4" stroke-linejoin="round" transform="translate(0 -12)"/>'
            f'<rect x="150" y="130" width="100" height="80" rx="8" {_s("#7a2a22")}/>'
            f'<path d="M150 130 l100 80 M250 130 l-100 80" stroke="#fff4e0" stroke-width="8"/>'
            f'<rect x="90" y="280" width="220" height="220" {_s("#9b3027")}/>'
            f'<path d="M90 280 l220 220 M310 280 l-220 220 M200 280 v220" stroke="#fff4e0" stroke-width="12"/>'
            f'<rect x="90" y="280" width="220" height="220" fill="none" stroke="#fff4e0" stroke-width="12"/>'
            f'</g>')
    tree = (f'<g transform="translate(1640 330)">'
            f'<path d="M60 200 q10 160 -10 330 h70 q-20 -170 -10 -330z" {_s("#9a6236")}/>'
            f'<circle cx="80" cy="150" r="120" {_s("#4fb04a")}/><circle cx="0" cy="220" r="85" {_s("#4fb04a")}/>'
            f'<circle cx="170" cy="215" r="90" {_s("#4fb04a")}/><circle cx="80" cy="230" r="90" fill="#4fb04a"/>'
            f'<circle cx="40" cy="120" r="12" fill="#ff4d4d"/><circle cx="130" cy="180" r="12" fill="#ff4d4d"/>'
            f'<circle cx="0" cy="230" r="12" fill="#ff4d4d"/><circle cx="170" cy="250" r="12" fill="#ff4d4d"/>'
            f'<circle cx="90" cy="90" r="12" fill="#ff4d4d"/></g>')
    return (f'<svg viewBox="0 0 1920 1080" width="1920" height="1080" xmlns="http://www.w3.org/2000/svg">'
            f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6fc8ff"/>'
            f'<stop offset="1" stop-color="#d9f3ff"/></linearGradient></defs>'
            f'<rect width="1920" height="1080" fill="url(#sky)"/>'
            f'<path d="M0 640 q300 -150 640 -40 q380 -170 760 -20 q300 -90 520 -10 v470 h-1920z" fill="#9fdc77"/>'
            f'<path d="M0 720 q480 -110 980 -10 q520 -90 940 10 v360 h-1920z" fill="#7fcd5a"/>'
            f'{barn}{tree}{fence}'
            f'<path d="M0 820 q960 -60 1920 0 v260 h-1920z" fill="#6cc24a"/>'
            f'{grass}{flowers}</svg>')


def sun():
    rays = "".join(f'<rect x="-9" y="-150" width="18" height="44" rx="9" fill="#ffd23f" transform="rotate({a})"/>'
                   for a in range(0, 360, 30))
    return (f'<svg viewBox="-160 -160 320 320" width="320" height="320" xmlns="http://www.w3.org/2000/svg" overflow="visible">'
            f'<g class="rays">{rays}</g>'
            f'<circle r="92" fill="#ffd23f" stroke="#f2a20c" stroke-width="6"/>'
            f'<circle cx="-30" cy="-12" r="9" fill="{INK}"/><circle cx="30" cy="-12" r="9" fill="{INK}"/>'
            f'<path d="M-34 22 q34 30 68 0" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
            f'<ellipse cx="-52" cy="16" rx="13" ry="8" fill="#ff8f6b" opacity="0.6"/>'
            f'<ellipse cx="52" cy="16" rx="13" ry="8" fill="#ff8f6b" opacity="0.6"/></svg>')
