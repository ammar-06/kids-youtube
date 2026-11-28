"""14 s motion test for the 2D Mo -> cartoon3d/mo2dtest (render with hyperframes)."""
import json, math, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mo2d

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cartoon3d", "mo2dtest")
os.makedirs(OUT, exist_ok=True)
for f in ("hyperframes.json", "package.json"):
    shutil.copy(os.path.join(OUT, "..", "compare2d", f), os.path.join(OUT, f))
open(os.path.join(OUT, "meta.json"), "w").write('{"id":"mo2dtest","name":"mo2dtest","createdAt":"2026-11-29T00:30:00.000Z"}')
D = 14.0
P = mo2d.PIVOTS
js = []


def tw(sel, props, t, kind="to"):
    js.append(f'tl.{kind}({json.dumps(sel)}, {json.dumps(props)}, {t:.3f});')


def rot(part, ang, t, dur, ease="sine.inOut"):
    x, y = P[part]
    tw(f".{part}", {"rotation": ang, "svgOrigin": f"{x} {y}", "duration": dur, "ease": ease}, t)


# idle body bob + head sway (whole time)
for i in range(int(D / 0.8)):
    t = i * 0.8
    tw("#mo", {"y": -6 if i % 2 == 0 else 0, "duration": 0.4, "ease": "sine.inOut"}, t)
    tw("#mo", {"y": 0, "duration": 0.4, "ease": "sine.inOut"}, t + 0.4)
for i in range(int(D / 1.6)):
    rot("mo-head", 3 if i % 2 == 0 else -3, i * 1.6, 1.6)
# blinks
for t in (0.9, 3.4, 5.9, 6.2, 8.8, 11.6, 13.2):
    tw(".mo-lid", {"scaleY": 1, "transformOrigin": "50% 0%", "duration": 0.07}, t)
    tw(".mo-lid", {"scaleY": 0, "transformOrigin": "50% 0%", "duration": 0.09}, t + 0.1)
# wave (his right hand, screen-left) 0.8 - 3.6
rot("mo-arm-r", 98, 0.8, 0.45, "back.out(1.6)")
rot("mo-fore-r", 50, 0.8, 0.45)
for i in range(6):
    rot("mo-fore-r", 25 if i % 2 == 0 else 62, 1.25 + i * 0.32, 0.32)
rot("mo-arm-r", 0, 3.3, 0.45, "power2.inOut"); rot("mo-fore-r", 0, 3.3, 0.45)
# sing 3.8 - 7.0 (mouth shapes)
shapes = ["mo-m-open", "mo-m-o", "mo-m-wide", "mo-m-open", "mo-m-smile", "mo-m-wide", "mo-m-o", "mo-m-open", "mo-m-wide", "mo-m-open", "mo-m-o", "mo-m-smile"]
t = 3.8
prev = "mo-m-smile"
for sh in shapes:
    if sh != prev:
        tw(f".{prev}", {"opacity": 0, "duration": 0.04}, t)
        tw(f".{sh}", {"opacity": 1, "duration": 0.04}, t)
    prev = sh
    t += 0.27
tw(f".{prev}", {"opacity": 0, "duration": 0.04}, t); tw(".mo-m-smile", {"opacity": 1, "duration": 0.04}, t)
tw(".mo-pupils", {"x": 6, "duration": 0.3}, 4.4); tw(".mo-pupils", {"x": -6, "duration": 0.4}, 5.4); tw(".mo-pupils", {"x": 0, "duration": 0.3}, 6.4)
tw(".mo-brows", {"y": -6, "duration": 0.2, "yoyo": True, "repeat": 3}, 4.0)
# clap 7.0 - 9.0: hands meet in front of the chest
rot("mo-arm-r", -32, 7.0, 0.35); rot("mo-fore-r", -78, 7.0, 0.35)
rot("mo-arm-l", 32, 7.0, 0.35); rot("mo-fore-l", 78, 7.0, 0.35)
for i in range(5):
    t = 7.4 + i * 0.3
    rot("mo-fore-r", -64, t, 0.15); rot("mo-fore-l", 64, t, 0.15)
    rot("mo-fore-r", -84, t + 0.15, 0.15); rot("mo-fore-l", 84, t + 0.15, 0.15)
for p in ("mo-arm-r", "mo-fore-r", "mo-arm-l", "mo-fore-l"):
    rot(p, 0, 9.0, 0.3)
# jump 9.3 - 10.9: squash, fly with arms up, land
tw("#mo", {"scaleY": 0.9, "scaleX": 1.06, "transformOrigin": "50% 100%", "duration": 0.15}, 9.3)
tw("#mo", {"scaleY": 1.05, "scaleX": 0.97, "y": -160, "duration": 0.38, "ease": "power2.out"}, 9.45)
rot("mo-arm-r", 140, 9.45, 0.3); rot("mo-arm-l", -140, 9.45, 0.3)
tw(".mo-m-smile", {"opacity": 0, "duration": 0.05}, 9.45); tw(".mo-m-wide", {"opacity": 1, "duration": 0.05}, 9.45)
tw("#mo", {"scaleY": 1, "scaleX": 1, "y": 0, "duration": 0.36, "ease": "power2.in"}, 9.85)
tw("#mo", {"scaleY": 0.9, "scaleX": 1.06, "duration": 0.1}, 10.21)
tw("#mo", {"scaleY": 1, "scaleX": 1, "duration": 0.25, "ease": "back.out(3)"}, 10.31)
rot("mo-arm-r", 0, 10.2, 0.3); rot("mo-arm-l", 0, 10.2, 0.3)
tw(".mo-m-wide", {"opacity": 0, "duration": 0.05}, 10.6); tw(".mo-m-smile", {"opacity": 1, "duration": 0.05}, 10.6)
# dance 10.9 - 13.6: sway, arms up alternating, legs stepping
for i in range(8):
    t = 10.9 + i * 0.34
    s = 1 if i % 2 == 0 else -1
    tw("#mo", {"rotation": 4 * s, "x": 14 * s, "transformOrigin": "50% 100%", "duration": 0.34, "ease": "sine.inOut"}, t)
    rot("mo-arm-r", 120 if s > 0 else 40, t, 0.34); rot("mo-arm-l", -40 if s > 0 else -120, t, 0.34)
    rot("mo-fore-r", 25 * s, t, 0.34); rot("mo-fore-l", 25 * s, t, 0.34)
    rot("mo-leg-r", -10 if s > 0 else 0, t, 0.34); rot("mo-leg-l", 0 if s > 0 else 10, t, 0.34)
for p in ("mo-arm-r", "mo-fore-r", "mo-arm-l", "mo-fore-l", "mo-leg-r", "mo-leg-l"):
    rot(p, 0, 13.6, 0.3)
tw("#mo", {"rotation": 0, "x": 0, "duration": 0.3}, 13.6)

page = f'''<!doctype html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" /><title>Mo 2D test</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#bfe6ff}}
#root{{position:relative;width:1920px;height:1080px;background:linear-gradient(#a9dcff 0%,#d9f1ff 58%,#8fd36a 58%,#6fbf4f 100%)}}
#mo{{position:absolute;left:700px;top:90px;width:520px;height:832px}}#mo svg{{width:100%;height:100%}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D}" data-width="1920" data-height="1080" data-fps="30">
<div id="mo">{mo2d.mo_svg()}</div></div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.set(".mo-lid", {{ scaleY: 0, transformOrigin: "50% 0%" }}, 0);
{chr(10).join(js)}
tl.set({{}}, {{}}, {D});
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = tl;
</script></body></html>'''
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
print("tweens", len(js))
