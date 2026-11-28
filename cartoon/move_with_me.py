"""'Move With Me!' (2D family action song). Builds the Hyperframes project from the song's word timings.

    python cartoon/move_with_me.py        # needs videos/2026-11-29 - Move With Me/{song.wav, words.json, lyrics.txt}
    (then: cd cartoon3d/movewithme && npx hyperframes@0.9.40 render)
Video script (one action per sung word; see song_brief.md section E):
  intro    title card on the instrumental, the family walks in; Mo steps up, waves, counts 1-2-3 with hops
  verse 1  Mo (camera pushes in) claps on every "clap", claps up high on "high"; everyone copies
  chorus   whole family dances in a line, everyone hops on "whee"
  verse 2  Grandpa stomps on every "stomp" (camera shakes), "up and down" are stomps too
  verse 3  Biscuit wags his tail, wiggles left on "left" and right on "right"
  verse 4  Zara hops on every "jump" and on "up"
  verse 5  Mom and Dad step up together and spin on every "spin" and "round"
  outro    each move by its owner on its word, everyone waves goodbye, big hop on "again", bye card
"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import make_video as mv  # noqa: E402
from rig2d import Stage, backyard, HUMAN  # noqa: E402

F = os.path.join(ROOT, "videos", "2026-11-29 - Move With Me")
OUT = os.path.join(ROOT, "cartoon3d", "movewithme")
rnd = random.Random(11)


def main():
    lines = mv.lyric_lines(open(os.path.join(F, "lyrics.txt"), encoding="utf-8").read())
    words = json.load(open(os.path.join(F, "words.json"), encoding="utf-8"))
    song = os.path.join(F, "song.wav")
    D = mv.probe_duration(song)
    T = mv.time_lines(lines, words, D)
    assert len(T) == 38, len(T)
    bj = os.path.join(OUT, "beats", "assets", "song.wav.json")
    beat = 60 / 112
    if os.path.exists(bj):
        bt = [b["time"] for b in json.load(open(bj))["beats"]]
        gaps = sorted(b - a for a, b in zip(bt, bt[1:]))
        if gaps:
            beat = gaps[len(gaps) // 2]
    first, last = T[0]["start"], T[-1]["end"]
    end_card = min(D - 3.0, last + 0.8)

    st = Stage(D, unit_px=360, ground_y=945)
    st.scenery(backyard())
    slots = {"mo": 250, "zara": 510, "mom": 790, "dad": 1080, "grandpa": 1380, "biscuit": 1660}
    for n, x in slots.items():
        st.add(n, x, z=10 + (5 if n in ("mo", "zara", "biscuit") else 0), hidden=True)
    people = list(slots)
    humans = [n for n in people if n != "biscuit"]

    def sec(a, b):
        return T[a:b + 1]

    def wtimes(a, b, *toks):
        out = []
        for ln in sec(a, b):
            for w in ln["words"]:
                tk = mv.tokens(w["w"])
                if tk and tk[0] in toks:
                    out.append((tk[0], w["s"]))
        return out

    def words_of(a, b):
        return [w for ln in sec(a, b) for w in ln["words"]]

    # ---------------- feature: step forward to the centre (camera pushes in), then back to the line
    def feature(names_x, t0, t1, cam=1.22):
        t0 = max(t0, 5.6)   # after everyone has walked in
        for n, x in names_x:
            st.set(f"#c-{n}", {"zIndex": 40}, t0 - 0.9)
            st.tw(f"#c-{n}", {"x": x - slots[n], "scale": 1.18, "transformOrigin": "50% 100%", "duration": 0.85, "ease": "power2.inOut"}, t0 - 0.9)
            st.walk_legs(n, t0 - 0.9, t0 - 0.05, 0.22)
            st.tw(f"#c-{n}", {"x": 0, "scale": 1, "duration": 0.8, "ease": "power2.inOut"}, t1 + 0.1)
            st.walk_legs(n, t1 + 0.1, t1 + 0.9, 0.22)
            st.set(f"#c-{n}", {"zIndex": 15}, t1 + 0.9)
        st.tw("#cam", {"scale": cam, "y": 60, "duration": 1.0, "ease": "power2.inOut"}, t0 - 0.9)
        st.tw("#cam", {"scale": 1, "y": 0, "duration": 0.9, "ease": "power2.inOut"}, t1 + 0.1)

    # ---------------- pop-up action words (outside the camera)
    pops = []

    def popword(text, t, col):
        i = len(pops)
        x = 960 + rnd.choice([-1, 1]) * rnd.uniform(300, 640)
        y = rnd.uniform(150, 330)
        pops.append(f'<div class="abs pop" id="pw{i}" style="left:{x:.0f}px;top:{y:.0f}px;color:{col}">{text}</div>')
        st.set(f"#pw{i}", {"opacity": 1, "scale": 0, "rotation": rnd.uniform(-14, 14)}, t - 0.02)
        st.tw(f"#pw{i}", {"scale": 1, "duration": 0.25, "ease": "back.out(3)"}, t)
        st.tw(f"#pw{i}", {"scale": 0.2, "opacity": 0, "duration": 0.25, "ease": "power2.in"}, t + 0.55)

    # ---------------- intro
    st.overlay('<div class="abs" id="title"><div>' + "".join(f'<span>{c if c != " " else "&nbsp;"}</span>' for c in "Move With Me!") + '</div></div>', ui=True)
    st.set("#title span", {"y": -420, "opacity": 0}, 0)
    st.tw("#title span", {"y": 0, "opacity": 1, "duration": 0.75, "ease": "bounce.out", "stagger": 0.05}, 0.4)
    for i in range(int(max(1, (first - 2.0) / 1.0))):
        st.tw("#title", {"scale": 1.06 if i % 2 == 0 else 1, "duration": 0.5, "ease": "sine.inOut"}, 1.6 + i * 1.0)
    st.tw("#title", {"scale": 0.2, "opacity": 0, "duration": 0.45, "ease": "back.in(1.6)"}, max(2.4, first - 1.4))
    order = ["mo", "zara", "biscuit", "mom", "dad", "grandpa"]
    for i, n in enumerate(order):
        t = 0.6 + i * 0.45
        st.enter(n, t, frm="left" if slots[n] < 960 else "right", dur=1.7)
    for n in people:
        st.blinks(n, 0, D - 1)
        st.bob(n, 3.5, end_card, beat, 4)
    st.tw("#cl0", {"x": 220, "duration": D, "ease": "none"}, 0)
    st.tw("#cl1", {"x": -160, "duration": D, "ease": "none"}, 0)
    st.tw("#cl2", {"x": 140, "duration": D, "ease": "none"}, 0)
    st.tw("#cl3", {"x": -90, "duration": D, "ease": "none"}, 0)
    st.tw("#sunrays", {"rotation": 180, "svgOrigin": "0 0", "duration": D, "ease": "none"}, 0)

    # lines 0-1 intro + 2-5 verse 1: Mo
    v1_end = T[5]["end"]
    feature([("mo", 960)], first, v1_end, 1.25)
    st.wave("mo", T[0]["start"], max(1.6, T[0]["end"] - T[0]["start"] + 0.3))
    nums = {"one": "1", "two": "2", "three": "3"}
    for tok, t in wtimes(1, 1, "one", "two", "three"):
        popword(nums[tok], t, ["#ff5a5f", "#ffb400", "#3ec300"][int(nums[tok]) - 1])
        st.hop("mo", t, 60, 0.4)
    st.sing("mo", words_of(0, 5))
    claps = wtimes(2, 5, "clap")
    high = [t for (tok, t) in wtimes(4, 4, "clap")][:1]
    ct = [t for _, t in claps]
    if ct:
        for n in humans + ["biscuit"]:
            st.clap(n, ct[0] - 0.4, [t for t in ct if t not in high])
        for t in high:
            for n in humans + ["biscuit"]:
                st.clap_high(n, t)
        for t in ct:
            popword("CLAP!", t, "#ff6a00")

    def chorus(a):
        t0, t1 = T[a]["start"] - 0.2, T[a + 3]["end"] + 0.2
        for n in people:
            st.dance(n, t0, t1, beat)
            st.sing(n, words_of(a, a + 3))
        for tok, t in wtimes(a, a + 3, "whee"):
            for n in people:
                st.hop(n, t, 110, 0.55)
            popword("WHEE!", t, "#a259ff")
        st.tw("#cam", {"scale": 1.04, "duration": (t1 - t0) / 2, "ease": "sine.inOut"}, t0)
        st.tw("#cam", {"scale": 1.0, "duration": (t1 - t0) / 2, "ease": "sine.inOut"}, t0 + (t1 - t0) / 2)

    chorus(6)

    # verse 2: Grandpa stomps
    feature([("grandpa", 960)], T[10]["start"], T[13]["end"], 1.2)
    st.sing("grandpa", words_of(10, 13))
    for k, (tok, t) in enumerate(wtimes(10, 13, "stomp", "up", "down")):
        st.stomp("grandpa", t - 0.2, "r" if k % 2 == 0 else "l")
        for n in humans:
            if n != "grandpa":
                st.stomp(n, t - 0.2, "l" if k % 2 == 0 else "r")
        st.tw("#cam", {"x": 6, "duration": 0.05}, t + 0.06)
        st.tw("#cam", {"x": -5, "duration": 0.05}, t + 0.11)
        st.tw("#cam", {"x": 0, "duration": 0.08}, t + 0.16)
        if tok == "stomp":
            popword("STOMP!", t, "#8a4a2a")

    # verse 3: Biscuit wags
    feature([("biscuit", 960)], T[14]["start"], T[17]["end"], 1.3)
    st.sing("biscuit", words_of(14, 17))
    st.wag("biscuit", T[14]["start"], T[17]["end"], 0.14)
    for tok, t in wtimes(14, 17, "wag", "left", "right"):
        ang = -9 if tok == "left" else 9 if tok == "right" else rnd.choice([-6, 6])
        for n in people:
            st.tw(f"#c-{n} svg", {"rotation": ang, "transformOrigin": "50% 100%", "duration": 0.15, "ease": "power2.out"}, t)
            st.tw(f"#c-{n} svg", {"rotation": 0, "duration": 0.25, "ease": "power2.inOut"}, t + 0.3)
        if tok == "wag":
            popword("WAG!", t, "#c98a3a")

    chorus(18)

    # verse 4: Zara jumps
    feature([("zara", 960)], T[22]["start"], T[25]["end"], 1.25)
    st.sing("zara", words_of(22, 25))
    for tok, t in wtimes(22, 25, "jump", "up"):
        st.hop("zara", t - 0.1, 140, 0.5)
        for n in people:
            if n != "zara":
                st.hop(n, t - 0.1, 50, 0.45)
        if tok == "jump":
            popword("JUMP!", t, "#3ec300")

    # verse 5: Mom and Dad spin
    feature([("mom", 820), ("dad", 1100)], T[26]["start"], T[29]["end"], 1.12)
    st.sing("mom", words_of(26, 29))
    st.sing("dad", words_of(26, 29))
    for tok, t in wtimes(26, 29, "spin", "round"):
        st.spin("mom", t - 0.05, 0.5)
        st.spin("dad", t - 0.05, 0.5)
        for n in ("mo", "zara", "biscuit", "grandpa"):
            st.tw(f"#c-{n} svg", {"rotation": 5, "transformOrigin": "50% 100%", "duration": 0.2}, t)
            st.tw(f"#c-{n} svg", {"rotation": 0, "duration": 0.2}, t + 0.25)
        if tok == "spin":
            popword("SPIN!", t, "#1fa2ff")

    chorus(30)

    # outro
    for n in people:
        st.sing(n, words_of(34, 37))
    for tok, t in wtimes(34, 34, "clap", "stomp", "wag", "jump"):
        if tok == "clap":
            st.clap("mo", t - 0.4, [t])
        elif tok == "stomp":
            st.stomp("grandpa", t - 0.2)
        elif tok == "wag":
            st.wag("biscuit", t - 0.1, t + 0.8)
        elif tok == "jump":
            st.hop("zara", t - 0.1, 120)
        popword(tok.upper() + "!", t, {"clap": "#ff6a00", "stomp": "#8a4a2a", "wag": "#c98a3a", "jump": "#3ec300"}[tok])
    for tok, t in wtimes(35, 35, "spin"):
        st.spin("mom", t, 0.6)
        st.spin("dad", t, 0.6)
        popword("SPIN!", t, "#1fa2ff")
    for n in humans:
        st.wave(n, T[36]["start"] - 0.2, T[36]["end"] - T[36]["start"] + 0.8, "r" if n != "grandpa" else "l")
    st.wag("biscuit", T[36]["start"], T[37]["end"] + 1.5)
    for tok, t in wtimes(37, 37, "again"):
        for n in people:
            st.hop(n, t, 130, 0.6)
    # bye card + confetti
    st.overlay('<div class="abs" id="bye">Bye bye, friends!</div>', ui=True)
    st.set("#bye", {"scale": 0, "opacity": 1}, 0)
    st.tw("#bye", {"scale": 1, "duration": 0.6, "ease": "back.out(2)"}, end_card)
    for i in range(40):
        c = ["#ff5a5f", "#ffb400", "#3ec300", "#1fa2ff", "#a259ff", "#ff7ac6"][i % 6]
        st.overlay(f'<div class="abs confetti" id="cf{i}" style="background:{c};left:{rnd.randint(40, 1880)}px"></div>', ui=True)
        st.tw(f"#cf{i}", {"y": 1250, "rotation": rnd.randint(200, 720), "x": rnd.randint(-120, 120), "duration": rnd.uniform(2.4, 3.6), "ease": "none"},
              end_card - 0.1 + rnd.uniform(0, 1.2))
    st.tw("#fade", {"opacity": 1, "duration": 0.8}, D - 0.9)

    # ---------------- karaoke captions
    for i, ln in enumerate(T):
        ws = "".join(f'<span class="w" id="w{i}_{k}">{w}</span> ' for k, w in enumerate(ln["line"].split()))
        st.overlay(f'<div class="abs cap" id="cap{i}"><div class="pill">{ws}</div></div>', ui=True)
        s = ln["start"] - 0.25
        nxt = T[i + 1]["start"] - 0.25 if i + 1 < len(T) else ln["end"] + 1.5
        e = min(nxt, ln["end"] + 1.2)
        st.set(f"#cap{i}", {"opacity": 0}, 0)
        st.tw(f"#cap{i}", {"opacity": 1, "y": 0, "duration": 0.2, "ease": "power2.out"}, s)
        st.tw(f"#cap{i}", {"opacity": 0, "duration": 0.15}, e - 0.15)
        k = 0
        for j, w in enumerate(ln["line"].split()):
            tk = mv.tokens(w)
            if not tk:
                continue
            st.tw(f"#w{i}_{j}", {"color": "#ff6a00", "scale": 1.12, "duration": 0.08}, ln["words"][min(k, len(ln["words"]) - 1)]["s"])
            st.tw(f"#w{i}_{j}", {"scale": 1, "duration": 0.2}, ln["words"][min(k, len(ln["words"]) - 1)]["s"] + 0.1)
            k += len(tk)
    for p in pops:
        st.overlay(p, ui=True)

    css = """
#title{left:0;top:250px;width:1920px;text-align:center;z-index:50;font-family:Rounded,sans-serif;font-size:170px;font-weight:900;color:#fff;
 -webkit-text-stroke:12px #ff6a00;paint-order:stroke fill;text-shadow:0 14px 0 rgba(0,0,0,.15)}
#title span{display:inline-block}
.pop{z-index:55;font-family:Rounded,sans-serif;font-size:96px;font-weight:900;-webkit-text-stroke:9px #fff;paint-order:stroke fill;
 text-shadow:0 8px 0 rgba(0,0,0,.18);opacity:0;transform:translate(-50%,-50%)}
.cap{left:0;width:1920px;bottom:34px;text-align:center;z-index:60}
.pill{display:inline-block;background:rgba(255,255,255,.93);border-radius:60px;padding:14px 46px;box-shadow:0 8px 0 rgba(0,0,0,.12);
 font-family:Rounded,sans-serif;font-size:66px;font-weight:900;color:#3a2a6a}
.w{display:inline-block}
#bye{left:0;top:330px;width:1920px;text-align:center;z-index:70;font-family:Rounded,sans-serif;font-size:150px;font-weight:900;color:#fff;
 -webkit-text-stroke:12px #ff5a8a;paint-order:stroke fill}
.confetti{top:-60px;width:22px;height:30px;border-radius:5px;z-index:65}
"""
    fonts = os.path.join(ROOT, "videos", "oldmac", "anim", "assets", "fonts", "rounded.ttf")
    n = st.write(OUT, "Move With Me!", audio=song, extra_css=css, fonts_from=fonts)
    print(f"built {D:.1f} s, beat {beat:.3f}, first line {first:.1f} s, tweens {n}")


if __name__ == "__main__":
    main()
