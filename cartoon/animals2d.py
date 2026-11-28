"""Farm animals in the soft 2D family style (after character/farm-animals.jpg).

viewBox 0 0 400 420, feet on y=410, facing the camera. Rigged parts (prefix p):
  .{p}-head .{p}-ear-l .{p}-ear-r .{p}-tail .{p}-leg-a .{p}-leg-b (alternating leg sets) .{p}-body
  birds also .{p}-wing-l .{p}-wing-r ; eyes .{p}-lid .{p}-pupils ; mouths .{p}-m-smile/-open/-o/-wide
"""
from family2d import radial, common_defs, eye, mouths, fluff_path


def critter_eyes(p, cy, dx, rx, skin):
    return (eye(p, 200 - dx, cy, rx, round(rx * 1.1, 1), round(rx * 0.86, 1), "r", skin, lid_line=False)
            + eye(p, 200 + dx, cy, rx, round(rx * 1.1, 1), round(rx * 0.86, 1), "l", skin, lid_line=False))


def quad(p, fur, dark, light, legcol, hoof, head_r=96, body=(200, 300, 118, 84), head_y=170, ears="", muzzle="",
         extra_head="", extra_body="", tail="", eyes_y=None, eye_dx=46, eye_r=24, mouth_y=None, mouth_s=0.8,
         top="", front_legs=(152, 248), back_legs=(112, 288), more_defs=""):
    defs = (radial(p, "skin", light, fur, dark) + radial(p, "sclera", "#ffffff", "#fbfaf9", "#e3dfdc")
            + radial(p, "iris", "#7a4a2a", "#4e2c16", "#1e0e06") + radial(p, "leg", *legcol) + common_defs(p) + more_defs)
    F = f"url(#{p}-skin)"
    bx, by, brx, bry = body
    sh = f'<ellipse cx="200" cy="410" rx="150" ry="13" fill="url(#{p}-shade)"/>'

    def legs(cls, xs, y0, w, shade):
        h = 410 - y0
        out = f'<g class="{p}-{cls}">'
        for x in xs:
            out += f'<rect x="{x - w / 2}" y="{y0}" width="{w}" height="{h}" rx="{w * 0.42:.0f}" fill="url(#{p}-leg)"/>'
            if hoof:
                out += f'<rect x="{x - w / 2 - 2}" y="{410 - 22}" width="{w + 4}" height="24" rx="9" fill="{hoof}"/>'
            if shade:
                out += f'<rect x="{x - w / 2}" y="{y0}" width="{w}" height="{h}" rx="{w * 0.42:.0f}" fill="#000" opacity="0.16"/>'
        return out + '</g>'
    back = legs("leg-a", [back_legs[1]], by + 10, 40, True) + legs("leg-b", [back_legs[0]], by + 10, 40, True)
    front = legs("leg-a", [front_legs[0]], by + 34, 46, False) + legs("leg-b", [front_legs[1]], by + 34, 46, False)
    bodyg = f'<g class="{p}-body"><ellipse cx="{bx}" cy="{by}" rx="{brx}" ry="{bry}" fill="{F}"/>{extra_body}</g>'
    ey = eyes_y if eyes_y else head_y - 18
    my = mouth_y if mouth_y else head_y + 52
    head = (f'<g class="{p}-head">{ears}<circle cx="200" cy="{head_y}" r="{head_r}" fill="{F}"/>{extra_head}'
            f'<ellipse cx="{200 - eye_dx - 24}" cy="{ey + 42}" rx="22" ry="15" fill="url(#{p}-blush)"/>'
            f'<ellipse cx="{200 + eye_dx + 24}" cy="{ey + 42}" rx="22" ry="15" fill="url(#{p}-blush)"/>'
            f'{critter_eyes(p, ey, eye_dx, eye_r, p + "-skin")}{muzzle}<g class="{p}-mouth">{mouths(p, 200, my, mouth_s)}</g>{top}</g>')
    return defs, sh + f'<g class="{p}-tail">{tail}</g>' + back + bodyg + front + head


def cow():
    p = "cw"
    spots = ('<path d="M104 270 Q136 236 172 266 Q178 302 140 316 Q100 306 104 270z" fill="#262224"/>'
             '<path d="M246 300 Q272 270 304 294 Q314 332 282 346 Q246 342 246 300z" fill="#262224"/>')
    ears = (f'<g class="{p}-ear-r"><ellipse cx="96" cy="140" rx="46" ry="24" fill="#262224" transform="rotate(20 96 140)"/>'
            f'<ellipse cx="100" cy="142" rx="28" ry="12" fill="#f2a3ae" transform="rotate(20 100 142)"/></g>'
            f'<g class="{p}-ear-l"><ellipse cx="304" cy="140" rx="46" ry="24" fill="#262224" transform="rotate(-20 304 140)"/>'
            f'<ellipse cx="300" cy="142" rx="28" ry="12" fill="#f2a3ae" transform="rotate(-20 300 142)"/></g>'
            '<path d="M142 94 Q126 60 146 48 Q152 72 164 86z M258 94 Q274 60 254 48 Q248 72 236 86z" fill="#e8cf96"/>')
    patch = '<path d="M108 150 Q118 88 176 80 Q198 120 182 170 Q150 198 110 178z" fill="#262224"/>'
    muzzle = ('<ellipse cx="200" cy="224" rx="72" ry="46" fill="#f7a8b4"/>'
              '<ellipse cx="174" cy="214" rx="9" ry="12" fill="#c46a7a"/><ellipse cx="226" cy="214" rx="9" ry="12" fill="#c46a7a"/>')
    collar = ('<path d="M128 256 Q200 284 272 256 L274 272 Q200 300 126 272z" fill="#d8322c"/>'
              '<path d="M188 282 Q200 272 212 282 L218 308 Q200 316 182 308z" fill="#f2c23a"/><circle cx="200" cy="310" r="5" fill="#a8801a"/>')
    tail = ('<path d="M314 290 Q350 300 356 340" fill="none" stroke="#f4f1ec" stroke-width="10" stroke-linecap="round"/>'
            '<ellipse cx="358" cy="348" rx="12" ry="16" fill="#262224"/>')
    return quad(p, "#f8f6f2", "#d6d0c8", "#ffffff", ("#ffffff", "#f1ede6", "#cfc8be"), "#8a6a5a",
                ears=ears, extra_head=patch, muzzle=muzzle, extra_body=spots, tail=tail, top=collar, mouth_y=246, mouth_s=0.55)


def pig():
    p = "pg"
    ears = (f'<g class="{p}-ear-r"><path d="M112 112 Q98 60 140 46 Q158 82 152 114z" fill="#f4a3b4"/><path d="M122 104 Q116 72 138 60 Q146 86 142 106z" fill="#e57f98"/></g>'
            f'<g class="{p}-ear-l"><path d="M288 112 Q302 60 260 46 Q242 82 248 114z" fill="#f4a3b4"/><path d="M278 104 Q284 72 262 60 Q254 86 258 106z" fill="#e57f98"/></g>')
    muzzle = ('<ellipse cx="200" cy="198" rx="42" ry="30" fill="#f28fa6"/>'
              '<ellipse cx="186" cy="198" rx="8" ry="11" fill="#b9566e"/><ellipse cx="214" cy="198" rx="8" ry="11" fill="#b9566e"/>')
    tail = '<path d="M316 280 q30 -10 26 14 q-4 18 -18 8 q-10 -10 8 -18 q20 -6 26 8" fill="none" stroke="#f4a3b4" stroke-width="7" stroke-linecap="round"/>'
    return quad(p, "#f6b3c2", "#e3899e", "#ffd6df", ("#f8bccb", "#f1a5b6", "#d98499"), "#d88497",
                ears=ears, muzzle=muzzle, tail=tail, body=(200, 300, 126, 92), eyes_y=148, mouth_y=238, mouth_s=0.7)


def sheep():
    p = "sp"
    def wool(cx, cy, rx, ry, n, bump=0.16):
        puffs = "".join(f'<circle cx="{cx + rx * 0.55 * dx:.0f}" cy="{cy + ry * 0.45 * dy:.0f}" r="{min(rx, ry) * 0.32:.0f}" fill="#ffffff" opacity="0.55"/>'
                        for dx, dy in ((-0.6, -0.4), (0.2, -0.6), (0.7, 0.1), (-0.2, 0.5), (-0.9, 0.4)))
        return f'<path d="{fluff_path(cx, cy, rx, ry, 0, 360, n, bump)}z" fill="url(#{p}-wool)"/>' + puffs
    ears = (f'<g class="{p}-ear-r"><ellipse cx="104" cy="170" rx="36" ry="17" fill="#4a4650" transform="rotate(16 104 170)"/><ellipse cx="108" cy="172" rx="20" ry="8" fill="#e8a0ac" transform="rotate(16 108 172)"/></g>'
            f'<g class="{p}-ear-l"><ellipse cx="296" cy="170" rx="36" ry="17" fill="#4a4650" transform="rotate(-16 296 170)"/><ellipse cx="292" cy="172" rx="20" ry="8" fill="#e8a0ac" transform="rotate(-16 292 172)"/></g>')
    top = wool(200, 112, 82, 50, 18, 0.2)
    body_wool = wool(200, 300, 132, 96, 26)
    muzzle = '<path d="M190 216 q10 8 20 0" fill="none" stroke="#2a2630" stroke-width="3"/><ellipse cx="200" cy="208" rx="9" ry="6" fill="#2a2630"/>'
    return quad(p, "#5e5a66", "#3a3640", "#7a7682", ("#5a5662", "#4a4650", "#2e2a34"), None,
                ears=ears, muzzle=muzzle, extra_body=body_wool, top=top, head_r=78, head_y=180, eyes_y=168, eye_dx=34, eye_r=20,
                mouth_y=224, mouth_s=0.55, tail='<circle cx="330" cy="290" r="24" fill="#fbfaf8"/>',
                more_defs=radial(p, "wool", "#ffffff", "#f6f4f0", "#d9d4cc"))


def horse():
    p = "hs"
    ears = (f'<g class="{p}-ear-r"><path d="M132 98 Q118 40 150 26 Q166 60 162 96z" fill="#a8582a"/><path d="M140 92 Q132 54 150 42 Q158 68 156 92z" fill="#e8b08a"/></g>'
            f'<g class="{p}-ear-l"><path d="M268 98 Q282 40 250 26 Q234 60 238 96z" fill="#a8582a"/><path d="M260 92 Q268 54 250 42 Q242 68 244 92z" fill="#e8b08a"/></g>')
    blaze = '<path d="M190 72 Q200 62 210 72 L214 150 Q200 160 186 150z" fill="#fbf4ec"/>'
    muzzle = ('<ellipse cx="200" cy="208" rx="62" ry="44" fill="#a0705a"/>'
              '<ellipse cx="178" cy="200" rx="8" ry="10" fill="#5a3826"/><ellipse cx="222" cy="200" rx="8" ry="10" fill="#5a3826"/>')
    mane = ('<path d="M150 72 Q170 30 214 34 Q250 36 262 72 Q236 56 220 76 Q204 54 186 78 Q170 60 150 72z" fill="#4a2a1c"/>')
    tail = '<path d="M312 268 Q368 280 360 356 Q340 332 324 300z" fill="#4a2a1c"/>'
    return quad(p, "#b8642e", "#8a4418", "#d88a50", ("#b8642e", "#a3561f", "#7a3c12"), "#3a2418",
                ears=ears, extra_head=blaze, muzzle=muzzle, top=mane, tail=tail, head_r=92, head_y=156, eyes_y=138,
                mouth_y=232, mouth_s=0.6, body=(200, 296, 118, 82))


def bird(p, col, dark, light, bill, feet, crest="", wattle="", eye_r=26, tail=""):
    defs = (radial(p, "skin", light, col, dark) + radial(p, "sclera", "#ffffff", "#fbfaf9", "#e3dfdc")
            + radial(p, "iris", "#6a4028", "#3e2414", "#150a04") + radial(p, "bill", "#ffc26a", bill, "#d06a10") + common_defs(p))
    F = f"url(#{p}-skin)"
    sh = f'<ellipse cx="200" cy="410" rx="110" ry="12" fill="url(#{p}-shade)"/>'
    legs = "".join(f'<g class="{p}-leg-{c}"><path d="M{x} 360 L{x} 396" stroke="{feet}" stroke-width="9" stroke-linecap="round"/>'
                   f'<path d="M{x - 22} 408 Q{x} 390 {x + 22} 408z" fill="{feet}" stroke="{feet}" stroke-width="8" stroke-linejoin="round"/></g>'
                   for c, x in (("a", 170), ("b", 230)))
    wings = (f'<g class="{p}-wing-r"><path d="M100 268 Q58 300 80 352 Q110 342 122 300z" fill="{F}"/></g>'
             f'<g class="{p}-wing-l"><path d="M300 268 Q342 300 320 352 Q290 342 278 300z" fill="{F}"/></g>')
    bodyg = (f'<g class="{p}-body"><ellipse cx="200" cy="300" rx="106" ry="80" fill="{F}"/>'
             f'<ellipse cx="200" cy="318" rx="62" ry="50" fill="{light}" opacity="0.5"/></g>')
    beak = (f'<g class="{p}-beak"><path d="M160 190 Q200 170 240 190 Q228 212 200 212 Q172 212 160 190z" fill="url(#{p}-bill)"/>'
            f'<g class="{p}-m-smile"></g>'
            f'<g class="{p}-m-open" opacity="0"><path d="M170 206 Q200 240 230 206 Q200 220 170 206z" fill="url(#{p}-bill)"/><path d="M176 205 Q200 222 224 205" fill="#7a2a1c"/></g>'
            f'<g class="{p}-m-o" opacity="0"><path d="M176 206 Q200 232 224 206 Q200 216 176 206z" fill="url(#{p}-bill)"/></g>'
            f'<g class="{p}-m-wide" opacity="0"><path d="M164 206 Q200 254 236 206 Q200 226 164 206z" fill="url(#{p}-bill)"/><path d="M172 205 Q200 230 228 205" fill="#7a2a1c"/></g></g>')
    head = (f'<g class="{p}-head">{crest}<circle cx="200" cy="160" r="86" fill="{F}"/>'
            f'<ellipse cx="126" cy="196" rx="20" ry="13" fill="url(#{p}-blush)"/><ellipse cx="274" cy="196" rx="20" ry="13" fill="url(#{p}-blush)"/>'
            f'{critter_eyes(p, 146, 40, eye_r, p + "-skin")}{beak}{wattle}</g>')
    return defs, sh + legs + f'<g class="{p}-tail">{tail}</g>' + wings + bodyg + head


def duck():
    tuft = '<path d="M194 80 Q188 52 206 42 Q204 62 214 70 Q220 54 232 54 Q222 74 214 84z" fill="#ffd21f"/>'
    return bird("dk", "#ffd93a", "#e8ae0c", "#fff29a", "#f59a2a", "#f5922a", crest=tuft)


def hen():
    comb = '<path d="M166 86 Q160 56 186 56 Q190 34 210 44 Q228 30 238 54 Q256 58 246 84z" fill="#e8322c"/>'
    wattle = '<path d="M192 212 Q190 236 200 238 Q210 236 208 212z" fill="#e8322c"/>'
    tail = '<path d="M280 250 Q330 196 346 236 Q352 272 298 292z" fill="url(#hn-skin)"/>'
    return bird("hn", "#fbf9f6", "#d8d2ca", "#ffffff", "#f5c21a", "#f2b51a", crest=comb, wattle=wattle, eye_r=22, tail=tail)


def _svg(fn, name):
    def make():
        d, b = fn()
        return (f'<svg class="{name}2d" viewBox="0 0 400 420" xmlns="http://www.w3.org/2000/svg" overflow="visible">'
                f'<defs>{d}</defs>{b}</svg>')
    return make


ANIMALS = {n: _svg(f, n) for n, f in (("cow", cow), ("pig", pig), ("duck", duck), ("sheep", sheep), ("horse", horse), ("chicken", hen))}
PREFIX = {"cow": "cw", "pig": "pg", "duck": "dk", "sheep": "sp", "horse": "hs", "chicken": "hn"}
HEAD_PIVOT = {"cow": (200, 270), "pig": (200, 266), "duck": (200, 240), "sheep": (200, 262), "horse": (200, 250), "chicken": (200, 240)}
