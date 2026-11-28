"""Side-by-side still: Gemini picture | 2D character.   python cartoon/compare2d.py grandpa"""
import os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import family2d, mo2d
name = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "cartoon3d", "compare2d")
shutil.copy(os.path.join(ROOT, "character", "1-apose-images", f"{name}-apose.jpg"), os.path.join(P, "ref.jpg"))
svg = mo2d.mo_svg() if name == "mo" else family2d.CHARS[name]()
html = f'''<!doctype html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" /><title>2D compare</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#e8e8e8}}#root{{position:relative;width:1920px;height:1080px;background:#e8e8e8}}
#ref{{position:absolute;left:0;top:0;width:960px;height:1080px;object-fit:cover}}#ch{{position:absolute;left:1000px;top:60px;width:880px;height:990px}}#ch svg{{width:100%;height:100%}}
.t{{position:absolute;top:20px;font:bold 40px sans-serif;color:#333}}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="2" data-width="1920" data-height="1080" data-fps="30">
<img id="ref" src="ref.jpg"><div id="ch">{svg}</div><div class="t" style="left:30px">Gemini</div><div class="t" style="left:990px">2D</div></div>
<script>const tl=gsap.timeline({{paused:true}});tl.set({{}},{{}},2);window.__timelines=window.__timelines||{{}};window.__timelines["main"]=tl;</script></body></html>'''
open(os.path.join(P, "index.html"), "w", encoding="utf-8").write(html)
subprocess.run("npx --yes hyperframes@0.9.40 snapshot --at 1 --no-end -o snap", cwd=P, shell=True, stdout=subprocess.DEVNULL)
print(os.path.join(P, "snap", "frame-00-at-1s.png"))
