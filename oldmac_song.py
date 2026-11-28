"""Old MacDonald (public domain lyrics) sung by ACE-Step 1.5 on a free GPU: Kaggle first, Colab if Kaggle fails."""
import json, os, shutil, sys
import make_video as mv
F = os.path.join(mv.HERE, "videos", "oldmac")
lyrics = open(os.path.join(F, "lyrics.txt"), encoding="utf-8").read()
plain = "\n".join(l for l in lyrics.splitlines() if not l.startswith("["))
job = {"seconds": 150, "lyrics": lyrics, "lyrics_plain": plain, "seed": 7, "dit": "acestep-v15-sft", "steps15": 50,
       "style": ("children's nursery rhyme, happy country farm song, banjo, acoustic guitar, ukulele, upright bass, "
                 "hand claps, light drums, glockenspiel, upbeat, major key, 112 bpm, cheerful bright female lead "
                 "vocal, clear melodic singing, kids choir sings along on E-I-E-I-O, catchy, joyful")}
where = sys.argv[1] if len(sys.argv) > 1 else "kaggle"
if where == "kaggle":
    out = mv.kaggle_run("kids-song", "song15.py", job, F)
else:
    out = mv.colab_auto_run("song15", "song15.py", job, F)
for f in ("song.wav", "song_take_b.wav", "words.json", "info.json", "ace15_info.json"):
    p = os.path.join(out, f)
    if os.path.exists(p):
        shutil.copy(p, os.path.join(F, f))
print("SONG DONE", os.listdir(F))
