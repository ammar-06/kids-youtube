"""'Meet the Family!' cast test (about 50 s, no song) -> cartoon3d/casttest ; render with hyperframes."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rig2d import Stage, backyard, NAMES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "cartoon3d", "casttest")
D = 50.0
st = Stage(D, unit_px=420, ground_y=930)
st.scenery(backyard())

FAM = [("mo", 300), ("zara", 560), ("mom", 820), ("dad", 1080), ("grandpa", 1360), ("biscuit", 1630)]
ANI = [("cow", 260, "MOO!"), ("pig", 560, "OINK!"), ("duck", 830, "QUACK!"), ("sheep", 1090, "BAA!"), ("horse", 1370, "NEIGH!"), ("chicken", 1650, "CLUCK!")]
for n, x in FAM:
    st.add(n, x, z=10, hidden=True)
for n, x, _ in ANI:
    st.add(n, x, scale=0.78, z=20, hidden=True, y=90)

css = """
#title{left:0;top:300px;width:1920px;text-align:center;z-index:50;font-family:Rounded,Arial Rounded MT Bold,sans-serif;font-size:150px;font-weight:900;color:#fff;
 -webkit-text-stroke:10px #ff6a00;paint-order:stroke fill;text-shadow:0 12px 0 rgba(0,0,0,.15)}
#title span{display:inline-block}
.card{z-index:60;font-family:Rounded,Arial Rounded MT Bold,sans-serif;font-size:64px;font-weight:900;color:#fff;padding:8px 34px;border-radius:40px;
 background:#ff6a00;box-shadow:0 8px 0 rgba(0,0,0,.15);transform:translateX(-50%)}
.bub{z-index:60;font-family:Rounded,Arial Rounded MT Bold,sans-serif;font-size:58px;font-weight:900;color:#e8322c;background:#fff;padding:10px 30px;
 border-radius:46px;box-shadow:0 8px 0 rgba(0,0,0,.12);transform:translateX(-50%)}
"""
st.overlay('<div class="abs" id="title">' + "".join(f'<span>{c if c != " " else "&nbsp;"}</span>' for c in "Meet the Family!") + '</div>')
cols = ["#2fae4a", "#9b6ad0", "#2c9a96", "#e8875a", "#d8322c", "#c98a3a"]
for i, (n, x) in enumerate(FAM):
    top = 930 - st.chars[n]["h"] - 110
    st.overlay(f'<div class="abs card" id="card-{n}" style="left:{x}px;top:{top:.0f}px;background:{cols[i]};opacity:0">{NAMES[n]}</div>')
for n, x, snd in ANI:
    top = 930 + 90 - st.chars[n]["h"] - 100
    st.overlay(f'<div class="abs bub" id="bub-{n}" style="left:{x}px;top:{top:.0f}px;opacity:0">{snd}</div>')


def pop(sel, t, hold):
    st.tw(sel, {"opacity": 1, "scale": 0, "duration": 0.01}, t - 0.01)
    st.tw(sel, {"scale": 1, "duration": 0.4, "ease": "back.out(2.4)"}, t)
    st.tw(sel, {"scale": 0, "opacity": 0, "duration": 0.25, "ease": "back.in(2)"}, t + hold)


# title
st.tw("#title span", {"y": -400, "opacity": 0, "duration": 0.01}, 0)
st.tw("#title span", {"y": 0, "opacity": 1, "duration": 0.7, "ease": "bounce.out", "stagger": 0.05}, 0.3)
st.tw("#title", {"scale": 0.3, "opacity": 0, "duration": 0.4, "ease": "back.in(1.6)"}, 2.6)
st.tw("#cl0", {"x": 160, "duration": D, "ease": "none"}, 0)
st.tw("#cl1", {"x": -120, "duration": D, "ease": "none"}, 0)
st.tw("#cl2", {"x": 100, "duration": D, "ease": "none"}, 0)
st.tw("#sunrays", {"rotation": 90, "svgOrigin": "0 0", "duration": D, "ease": "none"}, 0)

# family, one by one (4 s each from t=3)
t = 3.0
for n, x in FAM:
    st.enter(n, t, frm="right", dur=1.5)
    pop(f"#card-{n}", t + 1.5, 2.2)
    a = t + 1.6
    if n == "mo":
        st.wave(n, a, 2.2)
    elif n == "zara":
        st.jump(n, a); st.jump(n, a + 1.1)
    elif n == "mom":
        st.spin(n, a, 0.9); st.spin(n, a + 1.1, 0.9)
    elif n == "dad":
        st.clap(n, a, [a + 0.5 + i * 0.38 for i in range(5)])
    elif n == "grandpa":
        st.tip_hat(n, a)
    elif n == "biscuit":
        st.wag(n, a, a + 2.2); st.jump(n, a + 0.6, 110, arms=False)
    st.mouth(n, "open", a); st.mouth(n, "smile", a + 2.0)
    st.bob(n, t + 4.0, 27.5, 0.6, 5)
    t += 4.0
# t = 27: everyone dances
for n, x in FAM:
    st.dance(n, 27.5, 31.0, 0.5)
    st.mouth(n, "wide", 27.5); st.mouth(n, "smile", 31.0)
# family steps back (shrinks a bit and moves up) for the animals
for n, x in FAM:
    st.tw(f"#c-{n}", {"y": -60, "scale": 0.82, "transformOrigin": "50% 100%", "duration": 0.8, "ease": "power2.inOut"}, 31.2)
# animals pop in one by one with their sound
t = 32.4
for n, x, snd in ANI:
    st.pop_in(n, t)
    st.mouth(n, "wide", t + 0.5); st.mouth(n, "smile", t + 1.4)
    pop(f"#bub-{n}", t + 0.5, 1.1)
    st.nod(n, t + 0.5, 8, 0.6)
    st.bob(n, t + 1.8, 45.0, 0.5, 6)
    t += 2.0
# finale: everyone dances, animals march on the spot
for n, x in FAM:
    st.dance(n, 45.0, 48.6, 0.45)
    st.mouth(n, "wide", 45.0); st.mouth(n, "smile", 48.6)
for n, x, _ in ANI:
    st.walk_legs(n, 45.0, 48.6, 0.3)
for n in [f[0] for f in FAM] + [a[0] for a in ANI]:
    st.blinks(n, 0, D - 1)
st.tw("#fade", {"opacity": 1, "duration": 0.8}, D - 0.9)
fonts = os.path.join(ROOT, "videos", "oldmac", "anim", "assets", "fonts", "rounded.ttf")
print("tweens", st.write(OUT, "Meet the Family", extra_css=css, fonts_from=fonts))
