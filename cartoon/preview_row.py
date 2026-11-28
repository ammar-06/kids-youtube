"""Still of several 2D characters side by side, optionally under a reference picture.

    python cartoon/preview_row.py ref.jpg cow pig duck sheep horse chicken
    python cartoon/preview_row.py - mo grandpa biscuit zara mom dad
"""
import os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import animals2d, family2d, mo2d, people2d

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "cartoon3d", "compare2d")


def svg_of(n):
    if n == "mo":
        return mo2d.mo_svg()
    if n in animals2d.ANIMALS:
        return animals2d.ANIMALS[n]()
    if n in people2d.PEOPLE:
        return people2d.PEOPLE[n]()
    return family2d.CHARS[n]()


ref, names = sys.argv[1], sys.argv[2:]
top = 0
img = ""
if ref != "-":
    shutil.copy(ref, os.path.join(P, "ref.jpg"))
    img = '<img src="ref.jpg" style="position:absolute;left:280px;top:0;width:1376px;height:330px;object-fit:cover">'
    top = 340
w = 1880 // len(names)
h = 1080 - top - 30
row = "".join(f'<div style="position:absolute;left:{20 + i * w}px;top:{top}px;width:{w - 10}px;height:{h}px">{svg_of(n)}</div>'
              for i, n in enumerate(names))
html = f'''<!doctype html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" /><title>row</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0}}html,body{{width:1920px;height:1080px;background:#e8e8e8}}#root{{position:relative;width:1920px;height:1080px;background:#e8e8e8}}
svg{{width:100%;height:100%}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="2" data-width="1920" data-height="1080" data-fps="30">{img}{row}</div>
<script>const tl=gsap.timeline({{paused:true}});tl.set({{}},{{}},2);window.__timelines=window.__timelines||{{}};window.__timelines["main"]=tl;</script></body></html>'''
open(os.path.join(P, "index.html"), "w", encoding="utf-8").write(html)
subprocess.run("npx --yes hyperframes@0.9.40 snapshot --at 1 --no-end -o snap", cwd=P, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(os.path.join(P, "snap", "frame-00-at-1s.png"))
