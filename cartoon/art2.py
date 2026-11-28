"""Cartoon characters, version 2: cute big-head proportions, soft shading, rigged for animation.

Every character is drawn in a 400x400 box (farmer 300x500), feet on the bottom, facing right, and built from
named parts the animator moves:
  .head .ear-l .ear-r .tail .wing .arm-l .arm-r .leg-a .leg-b (legs swing in two alternating sets)
  .lid (eyelids for blinking, start closed=hidden by the animator), .brows
  .m-shut .m-open .m-o (mouth shapes: smile, singing, round "ooo")
PIVOTS gives each part's rotation point in the character's own coordinates.
DEFS (gradients) must be put on the page once.
"""

INK = "#4a3428"


def S(fill, w=6):
    return f'fill="{fill}" stroke="{INK}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


GRADS = {   # id: (light, dark)
    "wh": ("#ffffff", "#dcdbe6"), "pk": ("#ffd9e2", "#f39ab2"), "pg": ("#ffd0dc", "#ef8faa"),
    "ye": ("#fff59a", "#ffbf1f"), "or": ("#ffc06e", "#ee7d10"), "wo": ("#ffffff", "#e6e1d6"),
    "sf": ("#7d6a62", "#3f312b"), "ho": ("#eab07a", "#b06b36"), "mn": ("#8f4c26", "#55290f"),
    "rd": ("#ff7a6c", "#d42f27"), "sk": ("#ffe3c8", "#f0b088"), "sh": ("#ff6f5f", "#cf3328"),
    "dn": ("#79a6f5", "#3a5fc0"), "ha": ("#ffe58a", "#dca52a"), "gy": ("#f4efe8", "#cfc7bb"),
    "cr": ("#fff6d6", "#e8d39a"), "bl": ("#ffe98a", "#e8b100"),
}
DEFS = ('<svg width="0" height="0" style="position:absolute"><defs>' + "".join(
    f'<radialGradient id="g{k}" cx="38%" cy="30%" r="80%"><stop offset="0" stop-color="{a}"/>'
    f'<stop offset="1" stop-color="{b}"/></radialGradient>' for k, (a, b) in GRADS.items()) + '</defs></svg>')


def g(k):
    return f"url(#g{k})"


def eye(cx, cy, r, lid):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * 1.18:.1f}" {S("#fff", 4)}/>'
            f'<ellipse cx="{cx + r * 0.12:.1f}" cy="{cy + r * 0.12:.1f}" rx="{r * 0.68:.1f}" ry="{r * 0.78:.1f}" fill="#3a2418"/>'
            f'<ellipse cx="{cx + r * 0.12:.1f}" cy="{cy + r * 0.22:.1f}" rx="{r * 0.36:.1f}" ry="{r * 0.42:.1f}" fill="#150b06"/>'
            f'<circle cx="{cx + r * 0.38:.1f}" cy="{cy - r * 0.25:.1f}" r="{r * 0.3:.1f}" fill="#fff"/>'
            f'<circle cx="{cx - r * 0.2:.1f}" cy="{cy + r * 0.4:.1f}" r="{r * 0.13:.1f}" fill="#fff"/>'
            f'<ellipse class="lid" cx="{cx}" cy="{cy}" rx="{r + 1.5:.1f}" ry="{r * 1.18 + 1.5:.1f}" {S(lid, 4)}/>')


def eyes(pts, r, lid):
    return "".join(eye(x, y, r, lid) for x, y in pts)


def brows(pts, r, col=INK):
    return '<g class="brows">' + "".join(
        f'<path d="M{x - r * 0.7:.0f} {y - r * 1.75:.0f} q{r * 0.7:.0f} {-r * 0.45:.0f} {r * 1.4:.0f} 0" fill="none" '
        f'stroke="{col}" stroke-width="6" stroke-linecap="round"/>' for x, y in pts) + '</g>'


def blush(x, y, r=16):
    return f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.62:.1f}" fill="#ff7f9a" opacity="0.5"/>'


def mouths(cx, cy, w=20, tongue="#ff7b8a"):
    shut = f'<path d="M{cx - w} {cy - 3} Q{cx} {cy + w * 0.8:.0f} {cx + w} {cy - 3}" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
    opn = (f'<path d="M{cx - w * 1.1:.0f} {cy - 6} Q{cx} {cy - 2} {cx + w * 1.1:.0f} {cy - 6} Q{cx + w} {cy + w * 1.5:.0f} {cx} {cy + w * 1.5:.0f} '
           f'Q{cx - w} {cy + w * 1.5:.0f} {cx - w * 1.1:.0f} {cy - 6}z" {S("#7a1f22", 5)}/>'
           f'<ellipse cx="{cx}" cy="{cy + w * 1.05:.0f}" rx="{w * 0.62:.0f}" ry="{w * 0.36:.0f}" fill="{tongue}"/>')
    o = (f'<ellipse cx="{cx}" cy="{cy + w * 0.4:.0f}" rx="{w * 0.62:.0f}" ry="{w * 0.8:.0f}" {S("#7a1f22", 5)}/>'
         f'<ellipse cx="{cx}" cy="{cy + w * 0.8:.0f}" rx="{w * 0.38:.0f}" ry="{w * 0.25:.0f}" fill="{tongue}"/>')
    return (f'<g class="m-shut">{shut}</g><g class="m-open" opacity="0">{opn}</g><g class="m-o" opacity="0">{o}</g>')


def leg(cls, x, top, bot, w, fill, hoof=None, hoof_h=20):
    h = (f'<rect x="{x - w / 2 - 3:.0f}" y="{bot - hoof_h}" width="{w + 6}" height="{hoof_h}" rx="8" {S(hoof, 5)}/>'
         if hoof else "")
    return (f'<g class="{cls}"><rect x="{x - w / 2:.0f}" y="{top}" width="{w}" height="{bot - top}" rx="{w / 2.2:.0f}" {S(fill)}/>'
            f'{h}</g>')


def shadow(cx=200, w=140):
    return f'<ellipse class="shadow" cx="{cx}" cy="388" rx="{w}" ry="13" fill="#244a14" opacity="0.2"/>'


def svg(body, vb="0 0 400 400"):
    return f'<svg viewBox="{vb}" xmlns="http://www.w3.org/2000/svg" overflow="visible">{body}</svg>'


# ------------------------------------------------------------------------------------------------ animals
def cow():
    body = (f'<ellipse cx="170" cy="282" rx="112" ry="70" {S(g("wh"))}/>'
            f'<path d="M108 238 q26 -18 48 4 q6 28 -22 32 q-30 -6 -26 -36z" fill="#3b2d27"/>'
            f'<path d="M70 290 q18 -12 30 6 q-2 22 -22 20 q-14 -10 -8 -26z" fill="#3b2d27"/>'
            f'<path d="M180 300 q22 -12 34 6 q-4 22 -26 20 q-14 -10 -8 -26z" fill="#3b2d27"/>'
            f'<ellipse cx="150" cy="345" rx="24" ry="12" {S(g("pk"), 5)}/>')
    head = (f'<g class="head">'
            f'<g class="ear-l"><ellipse cx="200" cy="120" rx="34" ry="17" transform="rotate(-28 200 120)" {S(g("wh"))}/>'
            f'<ellipse cx="203" cy="121" rx="20" ry="8" transform="rotate(-28 203 121)" fill="#f7a9bd"/></g>'
            f'<g class="ear-r"><ellipse cx="372" cy="120" rx="34" ry="17" transform="rotate(28 372 120)" {S(g("wh"))}/>'
            f'<ellipse cx="369" cy="121" rx="20" ry="8" transform="rotate(28 369 121)" fill="#f7a9bd"/></g>'
            f'<path d="M244 86 q-14 -30 2 -46 q10 22 18 40z" {S(g("cr"), 5)}/>'
            f'<path d="M328 86 q14 -30 -2 -46 q-10 22 -18 40z" {S(g("cr"), 5)}/>'
            f'<ellipse cx="286" cy="150" rx="90" ry="82" {S(g("wh"))}/>'
            f'<path d="M318 92 q36 -6 50 26 q4 34 -26 42 q-34 -2 -34 -36 q0 -22 10 -32z" fill="#3b2d27"/>'
            f'<path d="M272 70 q14 -22 30 -2 q-10 -2 -14 10 q-6 -12 -16 -8z" {S("#3b2d27", 4)}/>'
            f'{eyes([(254, 140), (318, 140)], 22, "#ffffff")}{brows([(254, 140), (318, 140)], 22)}'
            f'<ellipse cx="288" cy="205" rx="72" ry="44" {S(g("pk"))}/>'
            f'<ellipse cx="262" cy="196" rx="9" ry="12" fill="#b25a6e"/><ellipse cx="314" cy="196" rx="9" ry="12" fill="#b25a6e"/>'
            f'{blush(222, 186)}{blush(354, 186)}{mouths(288, 224, 18)}</g>')
    bell = f'<path d="M232 252 q-4 -16 10 -20 q14 4 10 20z" {S(g("bl"), 4)}/><circle cx="242" cy="256" r="5" fill="{INK}"/>'
    tail = (f'<g class="tail"><path d="M62 262 q-30 20 -28 64" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M34 318 q-12 10 -2 26 q12 4 16 -10z" {S("#3b2d27", 4)}/></g>')
    return svg(shadow(185, 150) + tail
               + leg("leg-b", 128, 300, 386, 34, "#ece9f0", "#7a5f4c") + leg("leg-a", 248, 300, 386, 34, "#ece9f0", "#7a5f4c")
               + body
               + leg("leg-a", 98, 304, 388, 36, g("wh"), "#8a6c56") + leg("leg-b", 218, 304, 388, 36, g("wh"), "#8a6c56")
               + bell + f'<g transform="translate(-6 10)">{head}</g>')


def pig():
    head = (f'<g class="head">'
            f'<g class="ear-l"><path d="M214 96 q-16 -54 22 -62 q22 22 18 52z" {S(g("pg"))}/>'
            f'<path d="M222 88 q-6 -34 14 -40 q10 16 8 36z" fill="#ef8faa"/></g>'
            f'<g class="ear-r"><path d="M352 96 q16 -54 -22 -62 q-22 22 -18 52z" {S(g("pg"))}/>'
            f'<path d="M344 88 q6 -34 -14 -40 q-10 16 -8 36z" fill="#ef8faa"/></g>'
            f'<ellipse cx="283" cy="152" rx="88" ry="82" {S(g("pg"))}/>'
            f'<path d="M262 74 q10 -14 18 0 q8 -12 16 2" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>'
            f'{eyes([(248, 136), (318, 136)], 21, "#ffc6d4")}{brows([(248, 136), (318, 136)], 21)}'
            f'<ellipse cx="285" cy="190" rx="44" ry="32" {S(g("pk"))}/>'
            f'<ellipse cx="270" cy="190" rx="8" ry="13" fill="#a8455f"/><ellipse cx="300" cy="190" rx="8" ry="13" fill="#a8455f"/>'
            f'{blush(220, 186, 18)}{blush(350, 186, 18)}{mouths(285, 236, 17)}</g>')
    tail = f'<g class="tail"><path d="M66 262 q-34 -14 -30 12 q6 22 -16 20 q-14 -2 -12 -16" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/></g>'
    return svg(shadow(185, 145) + tail
               + leg("leg-b", 125, 310, 386, 34, "#f6b3c4", "#d77d96") + leg("leg-a", 240, 310, 386, 34, "#f6b3c4", "#d77d96")
               + f'<ellipse cx="172" cy="285" rx="112" ry="76" {S(g("pg"))}/>'
               + f'<ellipse cx="140" cy="250" rx="46" ry="18" fill="#fff" opacity="0.35"/>'
               + leg("leg-a", 96, 312, 388, 36, g("pg"), "#d77d96") + leg("leg-b", 212, 312, 388, 36, g("pg"), "#d77d96")
               + f'<g transform="translate(-18 30)">{head}</g>')


def duck():
    head = (f'<g class="head">'
            f'<path d="M232 64 q-6 -30 16 -36 q-2 20 6 30 q4 -26 26 -24 q-12 16 -10 34z" {S(g("ye"), 5)}/>'
            f'<circle cx="248" cy="142" r="82" {S(g("ye"))}/>'
            f'{eyes([(218, 128), (282, 128)], 21, "#ffe46a")}{brows([(218, 128), (282, 128)], 21)}'
            f'{blush(196, 168, 16)}{blush(300, 168, 14)}'
            f'<g class="bill-bot"><path d="M268 186 q50 2 72 14 q-14 24 -64 16 q-14 -10 -8 -30z" {S(g("or"))}/></g>'
            f'<path d="M262 170 q60 -16 86 8 q-10 20 -80 18 q-14 -12 -6 -26z" {S(g("or"))}/>'
            f'<ellipse cx="300" cy="176" rx="5" ry="3" fill="#a3500a"/>'
            f'<g class="m-shut"></g><g class="m-open" opacity="0"></g><g class="m-o" opacity="0"></g></g>')
    feet = "".join(
        f'<g class="{c}"><rect x="{x - 6}" y="330" width="12" height="44" rx="5" {S(g("or"), 4)}/>'
        f'<path d="M{x - 30} 386 q4 -16 26 -14 q4 -2 8 0 q24 -2 26 14 q-30 6 -60 0z" {S(g("or"), 5)}/></g>'
        for c, x in (("leg-b", 205), ("leg-a", 160)))
    wing = (f'<g class="wing"><path d="M120 262 q50 -46 112 -8 q-14 40 -54 50 q-16 -12 -28 0 q-22 -6 -30 -42z" {S(g("ye"))}/>'
            f'<path d="M150 272 q30 -16 60 -4" fill="none" stroke="#e0a400" stroke-width="5" stroke-linecap="round"/></g>')
    return svg(shadow(185, 115) + feet
               + f'<g class="tail"><path d="M88 262 q-34 -28 -36 -62 q22 14 40 18 q-12 -24 -2 -42 q18 26 40 40z" {S(g("ye"))}/></g>'
               + f'<ellipse cx="180" cy="282" rx="104" ry="80" {S(g("ye"))}/>'
               + f'<ellipse cx="160" cy="320" rx="56" ry="26" fill="#fffbd0" opacity="0.6"/>'
               + wing + head)


def sheep():
    puffs = [(95, 245), (130, 210), (180, 200), (228, 214), (258, 250), (250, 300), (206, 322), (150, 324), (102, 300), (72, 272)]
    wool = "".join(f'<circle cx="{x}" cy="{y}" r="44" {S(g("wo"))}/>' for x, y in puffs)
    wool += f'<ellipse cx="168" cy="264" rx="100" ry="66" fill="{g("wo")}"/>'
    wool += "".join(f'<path d="M{x - 18} {y} q18 -14 36 0" fill="none" stroke="#e2dccf" stroke-width="5" stroke-linecap="round"/>'
                    for x, y in ((130, 250), (190, 240), (160, 290), (220, 285)))
    head = (f'<g class="head">'
            f'<g class="ear-l"><ellipse cx="212" cy="150" rx="34" ry="16" transform="rotate(-20 212 150)" {S(g("sf"))}/>'
            f'<ellipse cx="214" cy="150" rx="20" ry="7" transform="rotate(-20 214 150)" fill="#f2a7b8"/></g>'
            f'<g class="ear-r"><ellipse cx="360" cy="150" rx="34" ry="16" transform="rotate(20 360 150)" {S(g("sf"))}/>'
            f'<ellipse cx="358" cy="150" rx="20" ry="7" transform="rotate(20 358 150)" fill="#f2a7b8"/></g>'
            f'<ellipse cx="286" cy="166" rx="70" ry="78" {S(g("sf"))}/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" {S(g("wo"), 5)}/>' for x, y, r in
                      ((246, 104, 28), (276, 88, 30), (310, 92, 28), (330, 112, 22), (230, 126, 18)))
            + f'{eyes([(260, 156), (314, 156)], 19, "#5a4740")}'
            f'<ellipse cx="287" cy="210" rx="38" ry="24" fill="#8a766d"/>'
            f'<ellipse cx="275" cy="200" rx="5" ry="7" fill="#2a1d18"/><ellipse cx="299" cy="200" rx="5" ry="7" fill="#2a1d18"/>'
            f'{blush(238, 196, 13)}{blush(338, 196, 13)}{mouths(287, 222, 14, "#ff8fa0")}</g>')
    return svg(shadow(180, 140)
               + leg("leg-b", 128, 318, 386, 22, g("sf"), "#2a1d18") + leg("leg-a", 228, 318, 386, 22, g("sf"), "#2a1d18")
               + wool
               + leg("leg-a", 104, 322, 388, 24, g("sf"), "#2a1d18") + leg("leg-b", 204, 322, 388, 24, g("sf"), "#2a1d18")
               + f'<g transform="translate(-8 22)">{head}</g>')


def horse():
    mane = "".join(f'<path d="M{226 + i * 4} {66 + i * 34} q-34 4 -42 32 q22 2 46 -10z" {S(g("mn"), 5)}/>' for i in range(5))
    head = (f'<g class="head">'
            f'<g class="ear-l"><path d="M246 70 l-10 -44 l34 30z" {S(g("ho"))}/></g>'
            f'<g class="ear-r"><path d="M318 64 l16 -42 l12 44z" {S(g("ho"))}/></g>'
            f'<path d="M216 140 q4 -86 82 -88 q66 4 64 88 l2 60 q-6 50 -70 50 q-72 -6 -78 -110z" {S(g("ho"))}/>'
            f'<path d="M262 56 q20 -20 44 -4 q-6 22 -26 30 q2 -16 -18 -26z" {S(g("mn"), 5)}/>'
            f'{eyes([(258, 132), (322, 132)], 20, "#d99a62")}{brows([(258, 132), (322, 132)], 20)}'
            f'<ellipse cx="294" cy="210" rx="62" ry="42" {S(g("cr"))}/>'
            f'<ellipse cx="272" cy="204" rx="7" ry="11" fill="#8a5a36"/><ellipse cx="316" cy="204" rx="7" ry="11" fill="#8a5a36"/>'
            f'{blush(226, 176, 14)}{blush(358, 176, 14)}{mouths(294, 228, 17)}</g>')
    tail = f'<g class="tail"><path d="M66 236 q-50 24 -40 110 q20 -30 28 -54 q8 -34 30 -46z" {S(g("mn"))}/></g>'
    return svg(shadow(185, 150) + tail
               + leg("leg-b", 122, 286, 386, 30, "#c98a52", "#4a3022", 24) + leg("leg-a", 238, 286, 386, 30, "#c98a52", "#4a3022", 24)
               + f'<ellipse cx="168" cy="262" rx="110" ry="62" {S(g("ho"))}/>'
               + f'<path d="M206 236 q4 -70 30 -100 l60 40 q-24 40 -30 84z" {S(g("ho"))}/>'
               + f'<g class="mane">{mane}</g>'
               + leg("leg-a", 94, 290, 388, 32, g("ho"), "#4a3022", 24) + leg("leg-b", 214, 290, 388, 32, g("ho"), "#4a3022", 24)
               + f'<g transform="translate(-14 26)">{head}</g>')


def chicken():
    head = (f'<g class="head">'
            f'<path d="M206 102 q-2 -34 24 -30 q4 -30 32 -18 q16 -24 36 4 q20 -4 18 22 q-50 8 -110 22z" {S(g("rd"))}/>'
            f'<circle cx="250" cy="160" r="72" {S(g("wh"))}/>'
            f'{eyes([(222, 146), (278, 146)], 19, "#ffffff")}{brows([(222, 146), (278, 146)], 19)}'
            f'{blush(204, 184, 14)}{blush(296, 182, 12)}'
            f'<path d="M292 200 q14 18 0 36 q-18 -6 -14 -30z" {S(g("rd"), 5)}/>'
            f'<g class="bill-bot"><path d="M296 186 l40 4 l-38 16z" {S(g("or"), 5)}/></g>'
            f'<path d="M294 168 q30 4 48 18 l-46 6z" {S(g("or"), 5)}/>'
            f'<g class="m-shut"></g><g class="m-open" opacity="0"></g><g class="m-o" opacity="0"></g></g>')
    feet = "".join(
        f'<g class="{c}"><path d="M{x} 330 v50 M{x - 18} 388 l18 -10 l18 10 M{x} 378 v10" fill="none" stroke="{INK}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="M{x} 330 v50 M{x - 18} 388 l18 -10 l18 10 M{x} 378 v10" fill="none" stroke="#ffa223" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g>'
        for c, x in (("leg-b", 205), ("leg-a", 160)))
    wing = (f'<g class="wing"><path d="M118 266 q46 -44 110 -6 q-12 44 -58 50 q-12 -10 -24 0 q-22 -6 -28 -44z" {S(g("gy"))}/>'
            f'<path d="M146 278 q30 -14 58 -2" fill="none" stroke="#c9c0b3" stroke-width="5" stroke-linecap="round"/></g>')
    tail = (f'<g class="tail"><path d="M96 252 q-50 -40 -24 -96 q16 30 34 40 q-8 -40 22 -60 q4 40 20 66z" {S(g("wh"))}/>'
            f'<path d="M86 200 q-4 -18 8 -30" fill="none" stroke="#d9d2c7" stroke-width="5" stroke-linecap="round"/></g>')
    return svg(shadow(185, 110) + feet + tail
               + f'<ellipse cx="182" cy="276" rx="98" ry="84" {S(g("wh"))}/>'
               + wing + head)


def farmer():
    """Old MacDonald, 300x500, feet at y=495. Arms swing at the shoulders, legs at the hips."""
    legs = "".join(
        f'<g class="{c}"><rect x="{x}" y="390" width="44" height="88" rx="14" {S(g("dn"))}/>'
        f'<path d="M{x - 6} 470 h56 q10 0 12 16 v10 h-70z" {S("#6b4128")}/></g>'
        for c, x in (("leg-b", 160), ("leg-a", 98)))
    torso = (f'<path d="M84 270 q66 -30 132 0 l12 118 q-78 26 -156 0z" {S(g("sh"))}/>'
             f'<path d="M96 300 h108 l10 104 q-64 18 -128 0z" {S(g("dn"))}/>'
             f'<path d="M108 300 l-6 -42 M192 300 l6 -42" stroke="{INK}" stroke-width="12" stroke-linecap="round"/>'
             f'<path d="M108 300 l-6 -42 M192 300 l6 -42" stroke="#4a74d6" stroke-width="6" stroke-linecap="round"/>'
             f'<rect x="126" y="318" width="48" height="36" rx="8" {S("#3d64c2", 4)}/>'
             f'<circle cx="112" cy="306" r="7" {S(g("bl"), 3)}/><circle cx="188" cy="306" r="7" {S(g("bl"), 3)}/>')

    def arm(cls, sx, sy, hx, hy):
        return (f'<g class="{cls}"><path d="M{sx} {sy} Q{(sx + hx) / 2 + (8 if hx > sx else -8):.0f} {(sy + hy) / 2:.0f} {hx} {hy}" fill="none" stroke="{INK}" stroke-width="36" stroke-linecap="round"/>'
                f'<path d="M{sx} {sy} Q{(sx + hx) / 2 + (8 if hx > sx else -8):.0f} {(sy + hy) / 2:.0f} {hx} {hy}" fill="none" stroke="#e8483b" stroke-width="25" stroke-linecap="round"/>'
                f'<circle cx="{hx}" cy="{hy + 8}" r="20" {S(g("sk"))}/></g>')
    head = (f'<g class="head">'
            f'<ellipse cx="66" cy="168" rx="16" ry="22" {S(g("sk"))}/><ellipse cx="234" cy="168" rx="16" ry="22" {S(g("sk"))}/>'
            f'<circle cx="150" cy="160" r="84" {S(g("sk"))}/>'
            f'<path d="M72 180 q78 120 156 0 q-6 92 -78 96 q-72 -4 -78 -96z" {S(g("wo"))}/>'
            f'{eyes([(120, 152), (180, 152)], 17, "#f6c7a2")}'
            f'<path d="M98 122 q22 -14 42 -2 M160 120 q20 -12 42 2" fill="none" stroke="#e9e3d8" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M98 122 q22 -14 42 -2 M160 120 q20 -12 42 2" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" opacity="0.4"/>'
            f'<ellipse cx="150" cy="182" rx="20" ry="16" {S("#f29a78", 5)}/>'
            f'<path d="M110 200 q20 14 38 0 q18 14 40 0" fill="#f4f1ea" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            f'{blush(100, 186, 15)}{blush(200, 186, 15)}{mouths(150, 214, 15)}'
            f'<path d="M30 112 q120 -38 240 0 q-12 18 -120 18 q-108 0 -120 -18z" {S(g("ha"))}/>'
            f'<path d="M80 108 q4 -84 70 -86 q66 2 70 86z" {S(g("ha"))}/>'
            f'<path d="M82 92 q68 14 136 0 v16 q-68 14 -136 0z" fill="#e0453a" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M100 60 q20 -20 50 -22" fill="none" stroke="#fff2b8" stroke-width="7" stroke-linecap="round"/></g>')
    return svg(f'<ellipse class="shadow" cx="150" cy="497" rx="105" ry="14" fill="#244a14" opacity="0.2"/>'
               + legs + arm("arm-l", 92, 282, 58, 378) + torso + arm("arm-r", 208, 282, 244, 378) + head,
               "0 0 300 500")


ANIMALS = {"cow": cow, "pig": pig, "duck": duck, "sheep": sheep, "horse": horse, "chicken": chicken}

PIVOTS = {   # part -> (x, y) rotation point, per character
    "cow": {"head": (244, 250), "tail": (62, 262), "ear-l": (219, 138), "ear-r": (342, 138)},
    "pig": {"head": (232, 270), "tail": (66, 262), "ear-l": (218, 122), "ear-r": (312, 122)},
    "duck": {"head": (230, 220), "tail": (95, 262), "wing": (210, 258), "bill-bot": (272, 192)},
    "sheep": {"head": (242, 262), "ear-l": (228, 176), "ear-r": (328, 176)},
    "horse": {"head": (226, 266), "tail": (66, 236), "ear-l": (236, 92), "ear-r": (312, 88), "mane": (230, 100)},
    "chicken": {"head": (230, 230), "tail": (100, 252), "wing": (212, 262), "bill-bot": (298, 190)},
    "farmer": {"head": (150, 250), "arm-l": (92, 282), "arm-r": (208, 282)},
}
