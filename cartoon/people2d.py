"""Zara, Mom and Dad in the soft 2D family style (after character/1-apose-images/*.jpg).

One builder, person(), draws a front-facing rigged human from a settings dict. Parts (prefix p):
  .{p}-head .{p}-arm-r .{p}-fore-r .{p}-arm-l .{p}-fore-l .{p}-leg-r .{p}-leg-l .{p}-body
  .{p}-lid .{p}-pupils .{p}-brows .{p}-m-smile/-open/-o/-wide
PIVOTS[name][part] = (x, y) for GSAP svgOrigin. 'r'/'l' = the character's own side.
"""
from family2d import radial, common_defs, eye, mouths, limb, hand

PIVOTS = {}


def person(name, p, c):
    W, H = 400, c["H"]
    cx = 200
    skin, skin_d, skin_l = c["skin"]
    defs = (radial(p, "skin", skin_l, skin, skin_d) + radial(p, "sclera", "#ffffff", "#fbfaf9", "#e3dfdc")
            + radial(p, "iris", "#9a5e34", "#6a3a1c", "#2c160a") + radial(p, "hair", "#3a3440", "#141118", "#060508")
            + common_defs(p) + c.get("defs", ""))
    S = f"url(#{p}-skin)"
    hx, hy, hrx, hry = c["head"]
    sh = f'<ellipse cx="{cx}" cy="{H - 8}" rx="{c.get("shadow", 120)}" ry="14" fill="url(#{p}-shade)"/>'
    piv = {}

    # legs
    def leg(side):
        sg = -1 if side == "r" else 1
        x = cx + sg * c["hip_dx"]
        y0, y1, w = c["leg_top"], c["leg_bottom"], c["leg_w"]
        out = f'<g class="{p}-leg-{side}">'
        out += f'<rect x="{x - w / 2}" y="{y0}" width="{w}" height="{y1 - y0}" rx="{w * 0.4:.0f}" fill="{c.get("leg_fill", S)}"/>'
        out += c["foot"](x, sg, H)
        piv[f"{p}-leg-{side}"] = (x, y0 + 8)
        return out + '</g>'

    def arm(side):
        sg = -1 if side == "r" else 1
        (sdx, sy), (edx, ey), (hdx, hy2) = c["shoulder"], c["elbow"], c["hand"]
        sx, ex, hx2 = cx + sg * sdx, cx + sg * edx, cx + sg * hdx
        aw = c["arm_w"]
        fore = f'<g class="{p}-fore-{side}">{limb(ex, ey, hx2, hy2, aw - 2, skin, skin_d, skin_l, sg)}{hand(hx2, hy2, sg, skin, skin_d, c.get("hand_s", 1.0))}</g>'
        sleeve = c["sleeve"](sx, sy, ex, ey, sg)
        piv[f"{p}-arm-{side}"] = (sx, sy)
        piv[f"{p}-fore-{side}"] = (ex, ey)
        return f'<g class="{p}-arm-{side}">{fore}{limb(sx, sy, ex, ey, aw, skin, skin_d, skin_l, sg)}{sleeve}</g>'

    neck_y0, neck_y1, neck_w = c["neck"]
    body = (f'<g class="{p}-body"><rect x="{cx - neck_w / 2}" y="{neck_y0}" width="{neck_w}" height="{neck_y1 - neck_y0}" rx="12" fill="{skin_d}"/>'
            f'{c["torso"]}</g>')
    piv[f"{p}-body"] = (cx, c["leg_top"])
    ex_, ey_, erx, ery, ir = c["eyes"]
    eyes = eye(p, cx - ex_, ey_, erx, ery, ir, "r", f"{p}-skin") + eye(p, cx + ex_, ey_, erx, ery, ir, "l", f"{p}-skin")
    by, bc, bw = c["brows"]
    brows = (f'<g class="{p}-brows"><path d="M{cx - ex_ - erx * 0.95:.0f} {by + 4} Q{cx - ex_:.0f} {by - 9} {cx - ex_ + erx * 0.95:.0f} {by}" fill="none" stroke="{bc}" stroke-width="{bw}" stroke-linecap="round"/>'
             f'<path d="M{cx + ex_ - erx * 0.95:.0f} {by} Q{cx + ex_:.0f} {by - 9} {cx + ex_ + erx * 0.95:.0f} {by + 4}" fill="none" stroke="{bc}" stroke-width="{bw}" stroke-linecap="round"/></g>')
    ny = c["nose_y"]
    nose = (f'<ellipse cx="{cx}" cy="{ny}" rx="{c.get("nose_r", 14)}" ry="{c.get("nose_r", 14) * 0.78:.0f}" fill="{skin_d}" opacity="0.4"/>'
            f'<ellipse cx="{cx - 3}" cy="{ny - 4}" rx="{c.get("nose_r", 14) * 0.6:.0f}" ry="{c.get("nose_r", 14) * 0.42:.0f}" fill="{skin_l}" opacity="0.7"/>')
    ears = "".join(f'<ellipse cx="{x}" cy="{c["ear_y"]}" rx="{c.get("ear_rx", 22)}" ry="{c.get("ear_ry", 30)}" fill="{S}"/>'
                   f'<ellipse cx="{x + (5 if x < cx else -5)}" cy="{c["ear_y"] + 2}" rx="{c.get("ear_rx", 22) * 0.45:.0f}" ry="{c.get("ear_ry", 30) * 0.55:.0f}" fill="{skin_d}" opacity="0.5"/>'
                   for x in (hx - hrx + 4, hx + hrx - 4))
    cheeks = "".join(f'<ellipse cx="{cx + s * (ex_ + 16)}" cy="{ey_ + ery + 26}" rx="{hrx * 0.24:.0f}" ry="{hrx * 0.16:.0f}" fill="url(#{p}-blush)"/>' for s in (-1, 1))
    mouth = f'<g class="{p}-mouth">{mouths(p, cx, c["mouth_y"], c.get("mouth_s", 0.85))}</g>'
    face = f'<ellipse cx="{hx}" cy="{hy}" rx="{hrx}" ry="{hry}" fill="{S}"/>'
    head = (f'<g class="{p}-head">{c.get("hair_back", "")}{ears}{face}{cheeks}{eyes}{brows}{nose}{c.get("face_extra", "")}{mouth}'
            f'{c.get("hair_front", "")}{c.get("head_extra", "")}</g>')
    piv[f"{p}-head"] = (cx, neck_y1 - 10)
    PIVOTS[name] = piv
    parts = sh + c.get("behind", "") + leg("r") + leg("l") + body + arm("r") + arm("l") + head + c.get("front", "")
    return (f'<svg class="{name}2d" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" overflow="visible">'
            f'<defs>{defs}</defs>{parts}</svg>')


def short_sleeve(fill, dark):
    def f(sx, sy, ex, ey, sg):
        return (f'<path d="M{sx - sg * 28} {sy - 22} Q{sx + sg * 24} {sy - 30} {sx + sg * 40} {sy + 28} Q{sx + sg * 24} {sy + 44} {sx + sg * 4} {sy + 50} '
                f'Q{sx - sg * 20} {sy + 28} {sx - sg * 28} {sy - 22}z" fill="{fill}"/>'
                f'<path d="M{sx + sg * 40} {sy + 28} Q{sx + sg * 24} {sy + 44} {sx + sg * 4} {sy + 50}" fill="none" stroke="{dark}" stroke-width="5" stroke-linecap="round"/>')
    return f


# ------------------------------------------------------------------------------------------------ Zara
def zara():
    p = "zr"
    dots = (f'<pattern id="{p}-dots" width="30" height="30" patternUnits="userSpaceOnUse"><rect width="30" height="30" fill="#9b6ad0"/>'
            f'<circle cx="7" cy="7" r="4.2" fill="#f4eefc"/><circle cx="22" cy="22" r="4.2" fill="#f4eefc"/></pattern>')
    dress = (f'<path d="M150 344 Q200 334 250 344 Q284 354 290 384 L284 440 Q316 520 322 556 Q200 584 78 556 Q84 520 116 440 L110 384 Q116 354 150 344z" fill="url(#{p}-dots)"/>'
             f'<path d="M150 344 Q200 334 250 344 Q284 354 290 384 L284 440 Q316 520 322 556 Q200 584 78 556 Q84 520 116 440 L110 384 Q116 354 150 344z" fill="url(#{p}-shadeg)"/>'
             f'<path d="M116 446 Q200 458 284 446" fill="none" stroke="#7a4cb0" stroke-width="3" opacity="0.6"/>'
             f'<path d="M176 340 Q200 352 224 340" fill="none" stroke="#7a4cb0" stroke-width="5" stroke-linecap="round"/>')

    def foot(x, sg, H):
        return (f'<rect x="{x - 20}" y="586" width="40" height="22" rx="8" fill="#fbfaf8"/>'
                f'<path d="M{x - 30 + sg * 4} 632 Q{x - 32 + sg * 4} 604 {x + sg * 3} 602 Q{x + 32 + sg * 4} 604 {x + 30 + sg * 4} 632z" fill="#f2a3c2"/>'
                f'<path d="M{x - 18 + sg * 3} 608 L{x + 20 + sg * 3} 608" stroke="#d97ea4" stroke-width="5" stroke-linecap="round"/>'
                f'<rect x="{x - 31 + sg * 4}" y="627" width="62" height="7" rx="3.5" fill="#c9688f"/>')
    hair_back = '<path d="M68 210 Q64 92 200 74 Q336 92 332 210 L338 318 Q300 330 280 312 L280 230 L120 230 L120 312 Q100 330 62 318z" fill="url(#zr-hair)"/>'
    hair_front = ('<path d="M74 200 Q80 92 200 80 Q320 92 326 200 Q300 160 262 150 Q214 140 178 118 Q150 150 112 160 Q88 172 74 200z" fill="url(#zr-hair)"/>'
                  '<path d="M190 84 Q208 110 250 120" fill="none" stroke="#4a4452" stroke-width="5" stroke-linecap="round" opacity="0.5"/>'
                  '<path d="M110 120 Q140 96 180 90" fill="none" stroke="#4a4452" stroke-width="4" stroke-linecap="round" opacity="0.35"/>')
    flower = ('<g transform="translate(96 120)">' + "".join(
        f'<ellipse cx="0" cy="-17" rx="12" ry="19" fill="#a374d6" transform="rotate({a})"/>' for a in range(0, 360, 60))
        + '<circle r="10" fill="#7c4cb8"/><circle r="5" fill="#c9a6ee"/></g>')
    return person("zara", p, dict(
        H=640, skin=("#cf9168", "#ad6e47", "#e8b48c"), head=(200, 204, 124, 122),
        eyes=(48, 214, 30, 33, 25), brows=(166, "#2a1c18", 6), nose_y=252, nose_r=12, mouth_y=284, mouth_s=0.75,
        ear_y=236, neck=(306, 350, 40), hip_dx=36, leg_top=540, leg_bottom=600, leg_w=38,
        shoulder=(84, 362), elbow=(120, 430), hand=(146, 484), arm_w=27,
        torso=dress, foot=foot, sleeve=short_sleeve("url(#zr-dots)", "#7a4cb0"),
        hair_back=hair_back, hair_front=hair_front, head_extra=flower,
        defs=dots + '<linearGradient id="zr-shadeg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity="0.15"/>'
                    '<stop offset="0.5" stop-color="#fff" stop-opacity="0.08"/><stop offset="1" stop-color="#000" stop-opacity="0.18"/></linearGradient>'))


# ------------------------------------------------------------------------------------------------ Mom
def mom():
    p = "mm"
    teal, teal_d = "#3f9a96", "#2c7a76"
    kurta = (f'<path d="M140 300 Q200 290 260 300 Q290 310 294 340 L288 420 Q300 520 304 620 Q200 636 96 620 Q100 520 112 420 L106 340 Q110 310 140 300z" fill="url(#mm-teal)"/>'
             f'<path d="M180 296 L200 326 L220 296" fill="none" stroke="{teal_d}" stroke-width="4"/>'
             + "".join(f'<g transform="translate({x} {y})">' + "".join(f'<circle cx="{4 * __import__("math").cos(a)}" cy="{4 * __import__("math").sin(a)}" r="3" fill="#fbf6e8"/>' for a in (0, 1.26, 2.51, 3.77, 5.03)) + '<circle r="2" fill="#f2c23a"/></g>'
                       for x, y in ((168, 306), (232, 306), (200, 334)))
             + f'<path d="M106 600 L108 624 M294 600 L292 624" stroke="{teal_d}" stroke-width="3"/>')

    def foot(x, sg, H):
        return (f'<path d="M{x - 26 + sg * 4} {H - 10} Q{x - 28 + sg * 4} {H - 34} {x + sg * 3} {H - 36} Q{x + 28 + sg * 4} {H - 34} {x + 26 + sg * 4} {H - 10}z" fill="#f2cf5a"/>'
                f'<rect x="{x - 27 + sg * 4}" y="{H - 14}" width="54" height="6" rx="3" fill="#c9a12e"/>')
    hair_back = ('<path d="M104 160 Q100 40 200 34 Q300 40 296 160 L298 300 Q270 310 262 290 L262 170 L138 170 L138 290 Q130 310 102 300z" fill="url(#mm-hair)"/>')
    braid = ('<g class="mm-braid">' + "".join(f'<ellipse cx="{276 - i * 2}" cy="{290 + i * 34}" rx="20" ry="22" fill="url(#mm-hair)"/>' for i in range(6))
             + '<rect x="250" y="476" width="34" height="9" rx="4" fill="#f2c23a"/>'
             + '<path d="M262 488 Q266 520 258 530 Q272 520 276 488z" fill="#141118"/></g>')
    hair_front = ('<path d="M108 150 Q110 44 200 40 Q290 44 292 150 Q276 96 232 84 Q206 80 196 60 Q170 92 130 106 Q112 120 108 150z" fill="url(#mm-hair)"/>'
                  '<path d="M196 50 Q228 70 262 100" fill="none" stroke="#4a4452" stroke-width="4" stroke-linecap="round" opacity="0.5"/>')
    return person("mom", p, dict(
        H=900, skin=("#d49a70", "#b0744c", "#ecbd96"), head=(200, 150, 92, 104),
        eyes=(36, 158, 22, 24, 18), brows=(124, "#2a1c18", 5), nose_y=192, nose_r=11, mouth_y=218, mouth_s=0.6,
        ear_y=168, ear_rx=17, ear_ry=24, neck=(240, 300, 36), hip_dx=34, leg_top=600, leg_bottom=870, leg_w=56,
        leg_fill="url(#mm-white)", shoulder=(84, 318), elbow=(118, 450), hand=(146, 556), arm_w=26, hand_s=1.05,
        torso=kurta, foot=foot, sleeve=short_sleeve("url(#mm-teal)", teal_d), shadow=110,
        hair_back=hair_back, hair_front=hair_front, front=braid,
        defs=radial(p, "teal", "#5fbab4", teal, teal_d) + radial(p, "white", "#ffffff", "#f3f1ee", "#d6d2cc")))


# ------------------------------------------------------------------------------------------------ Dad
def dad():
    p = "dd"
    orng, orng_d = "#e8875a", "#c46a40"
    polo = (f'<path d="M136 302 Q200 292 264 302 Q296 312 300 344 L294 600 Q200 616 106 600 L100 344 Q104 312 136 302z" fill="url(#dd-polo)"/>'
            f'<path d="M168 296 L200 322 L232 296 L236 312 L200 338 L164 312z" fill="#f4efe6"/>'
            f'<rect x="192" y="322" width="16" height="44" rx="4" fill="#f4efe6"/>')
    jeans_legs = "url(#dd-jeans)"

    def foot(x, sg, H):
        return (f'<rect x="{x - 30}" y="{H - 62}" width="60" height="20" rx="6" fill="#a9c2e2"/>'
                f'<path d="M{x - 34 + sg * 4} {H - 8} Q{x - 36 + sg * 4} {H - 40} {x + sg * 3} {H - 42} Q{x + 36 + sg * 4} {H - 40} {x + 34 + sg * 4} {H - 8}z" fill="#fbfaf8"/>'
                f'<path d="M{x - 12 + sg * 4} {H - 34} l18 -6 M{x - 8 + sg * 4} {H - 26} l18 -6" stroke="#3f7ad6" stroke-width="4" stroke-linecap="round"/>'
                f'<rect x="{x - 35 + sg * 4}" y="{H - 13}" width="70" height="7" rx="3.5" fill="#d6d2cc"/>')
    hair = ('<path d="M110 150 Q104 50 196 40 Q280 36 294 110 Q296 140 290 160 Q282 118 254 104 Q220 96 180 98 Q140 104 118 140z" fill="url(#dd-hair)"/>'
            '<path d="M140 70 Q190 48 250 62" fill="none" stroke="#4a4452" stroke-width="5" stroke-linecap="round" opacity="0.45"/>')
    beard = ('<path d="M110 170 Q112 250 160 272 Q200 290 240 272 Q288 250 290 170 Q282 208 262 222 Q240 206 200 208 Q160 206 138 222 Q118 208 110 170z" fill="url(#dd-hair)"/>'
             '<path d="M164 214 Q200 200 236 214 Q226 222 200 220 Q174 222 164 214z" fill="#141118"/>')
    return person("dad", p, dict(
        H=900, skin=("#cc9068", "#a86c46", "#e6b28c"), head=(200, 160, 94, 108),
        eyes=(36, 160, 21, 23, 17), brows=(126, "#141118", 7), nose_y=196, nose_r=12, mouth_y=232, mouth_s=0.55,
        ear_y=172, ear_rx=18, ear_ry=25, neck=(250, 306, 42), hip_dx=40, leg_top=596, leg_bottom=860, leg_w=64,
        leg_fill=jeans_legs, shoulder=(88, 324), elbow=(124, 456), hand=(152, 566), arm_w=30, hand_s=1.15,
        torso=polo, foot=foot, sleeve=short_sleeve("url(#dd-polo)", orng_d), shadow=120,
        hair_front=hair, face_extra=beard,
        defs=radial(p, "polo", "#f4a47a", orng, orng_d) + radial(p, "jeans", "#bcd2ee", "#9fbbe0", "#7a98c4"),
        behind='<rect x="136" y="590" width="128" height="40" rx="10" fill="#9fbbe0"/>'))


PEOPLE = {"zara": zara, "mom": mom, "dad": dad}
for _n, _f in PEOPLE.items():
    _f()   # fills PIVOTS
