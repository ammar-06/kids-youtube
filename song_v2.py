"""A second take of a video's song with ACE-Step 1.5 (much better singing than v1), then the same clips rebuilt
with it as final_v2.mp4. The first video (final.mp4) is left untouched for comparison.

    python song_v2.py "ABC song with friendly animals"

Outputs in the video folder: song_v2.wav (used), song_v2_take_b.wav (a second take to compare),
words_v2.json, captions_v2.ass, final_v2.mp4.
"""
import argparse
import json
import os
import re
import shutil
import sys

import make_video as mv

# ACE-Step needs vocal tags to sing (take 1 had none and sounded spoken)
VOCALS = ("cheerful bright female lead vocal, clear melodic singing, kids choir joins the chorus, "
          "catchy sing-along melody, nursery rhyme")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topic")
    ap.add_argument("--dit", default="acestep-v15-sft", help="ACE-Step 1.5 model (acestep-v15-sft or -turbo)")
    a = ap.parse_args()
    slug = re.sub(r"[^\w\- ]", "", a.topic).strip()[:60]
    found = [d for d in os.listdir(os.path.join(mv.HERE, "videos")) if d.endswith(f" - {slug}")]
    if not found:
        sys.exit(f"no video folder for {a.topic!r}: run make_video.py first")
    folder = os.path.join(mv.HERE, "videos", sorted(found)[-1])
    L = json.load(open(os.path.join(folder, "lyrics.json"), encoding="utf-8"))
    scenes = json.load(open(os.path.join(folder, "scenes.json"), encoding="utf-8"))["scenes"]
    files = [os.path.join(folder, "scenes", f"scene_{s['n']:03d}.mp4") for s in scenes]
    missing = [f for f in files if not os.path.exists(f)]
    if missing:
        sys.exit(f"{len(missing)} scene clips are missing: finish make_video.py first")

    song = os.path.join(folder, "song_v2.wav")
    words_path = os.path.join(folder, "words_v2.json")
    if not (os.path.exists(song) and os.path.exists(words_path)):
        mv.log("ACE-Step 1.5 on a free Colab T4: singing take 2...")
        job = {"seconds": L["seconds"], "style": f"{L['music_style']}, {VOCALS}", "lyrics": L["lyrics"],
               "lyrics_plain": L["lyrics_plain"], "seed": 42, "dit": a.dit, "steps15": 50}
        out = mv.colab_auto_run("song15", "song15.py", job, folder)
        shutil.copy(os.path.join(out, "song.wav"), song)
        shutil.copy(os.path.join(out, "words.json"), words_path)
        for f, to in (("song_take_b.wav", "song_v2_take_b.wav"), ("info.json", "song_v2_info.json"),
                      ("ace15_info.json", "song_v2_ace15.json")):
            if os.path.exists(os.path.join(out, f)):
                shutil.copy(os.path.join(out, f), os.path.join(folder, to))
    duration = mv.probe_duration(song)
    timed = mv.time_lines(mv.lyric_lines(L["lyrics"]), json.load(open(words_path, encoding="utf-8")), duration)
    mv.log(f"  take 2: {duration:.0f} s, {len(timed)} lyric lines timed")
    caps = os.path.join(folder, "captions_v2.ass")
    mv.write_captions(timed, caps, duration)
    final = os.path.join(folder, "final_v2.mp4")
    mv.assemble(folder, song, files, caps, final)
    mv.log(f"DONE: {final}")


if __name__ == "__main__":
    main()
