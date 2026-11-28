"""Make a song with ACE-Step 1.5 on this PC's CPU (no GPU needed), then time its words with faster-whisper.

    python local_song15.py videos/oldmac            # reads lyrics.txt + style.txt there, writes song.wav, words.json

ACE-Step 1.5 lives in D:/ace15 (cloned at a fixed commit, installed with `uv sync`).
"""
import json
import os
import subprocess
import sys
import time

ACE = os.environ.get("ACE15_DIR", "D:/ace15")
HERE = os.path.dirname(os.path.abspath(__file__))
folder = os.path.abspath(sys.argv[1])
seconds = float(os.environ.get("SONG_SECONDS", "150"))
dit = os.environ.get("ACE15_DIT", "acestep-v15-turbo")
lm = os.environ.get("ACE15_LM", "acestep-5Hz-lm-0.6B")

GEN = r'''
import json, os, shutil, sys, time, torch
torch.set_num_threads(os.cpu_count())
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music
J = json.load(open(sys.argv[1]))
t = time.time()
dit = AceStepHandler()
print("DiT:", dit.initialize_service(project_root=os.getcwd(), config_path=J["dit"], device="cpu"), flush=True)
llm = LLMHandler()
if J["lm"] != "none":   # the 5 Hz planner LM makes better songs, but needs RAM
    print("LM:", llm.initialize(checkpoint_dir=os.path.join(os.getcwd(), "checkpoints"), lm_model_path=J["lm"],
                                backend="pt", device="cpu"), flush=True)
print("models loaded in", round(time.time() - t), "s", flush=True)
turbo = "turbo" in J["dit"]
params = GenerationParams(caption=J["caption"], lyrics=J["lyrics"], duration=float(J["seconds"]), vocal_language="en",
                          inference_steps=8 if turbo else 50, guidance_scale=1.0 if turbo else 7.0, shift=3.0,
                          seed=int(J["seed"]), thinking=J["lm"] != "none")
config = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[int(J["seed"])], audio_format="wav")
t = time.time()
res = generate_music(dit, llm, params, config, save_dir=os.path.join(J["out"], "ace15_raw"))
if not res.success:
    sys.exit("ACE-Step 1.5 failed: %s" % res.error)
shutil.copy(res.audios[0]["path"], os.path.join(J["out"], "song.wav"))
meta = [{k: a.get(k) for k in ("key", "bpm", "duration") if k in a} for a in res.audios]
json.dump({"gen_s": round(time.time() - t), "takes": meta, "dit": J["dit"], "lm": J["lm"]},
          open(os.path.join(J["out"], "ace15_info.json"), "w"))
print("song done in", round(time.time() - t), "s", meta, flush=True)
'''


def main():
    lyrics = open(os.path.join(folder, "lyrics.txt"), encoding="utf-8").read()
    style = open(os.path.join(folder, "style.txt"), encoding="utf-8").read().strip()
    song = os.path.join(folder, "song.wav")
    if not os.path.exists(song):
        if not os.path.isdir(os.path.join(ACE, "checkpoints", dit)):
            subprocess.run(["uv", "run", "acestep-download", "--model", dit, "--skip-main"], cwd=ACE, check=True)
        if lm != "none" and not os.path.isdir(os.path.join(ACE, "checkpoints", lm)):
            subprocess.run(["uv", "run", "acestep-download", "--model", lm, "--skip-main"], cwd=ACE, check=True)
        job = os.path.join(folder, "ace15_job.json")
        json.dump({"caption": style, "lyrics": lyrics, "seconds": seconds, "seed": int(os.environ.get("SEED", "7")),
                   "dit": dit, "lm": lm, "out": folder}, open(job, "w"))
        gen = os.path.join(ACE, "kids_gen_cpu.py")
        open(gen, "w").write(GEN)
        t = time.time()
        subprocess.run(["uv", "run", "python", gen, job], cwd=ACE, check=True)
        print(f"ACE-Step on CPU: {time.time() - t:.0f} s", flush=True)
    # word times of the singing (faster-whisper on the CPU)
    from faster_whisper import WhisperModel
    t = time.time()
    plain = " ".join(l for l in lyrics.splitlines() if not l.startswith("["))
    model = WhisperModel(os.environ.get("WHISPER_MODEL", "medium.en"), device="cpu", compute_type="int8")
    segs, _ = model.transcribe(song, language="en", word_timestamps=True, initial_prompt=plain[:800],
                               condition_on_previous_text=False, vad_filter=False)
    words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in (s.words or [])]
    json.dump(words, open(os.path.join(folder, "words.json"), "w"), indent=1)
    print(f"whisper: {len(words)} words in {time.time() - t:.0f} s", flush=True)


if __name__ == "__main__":
    main()
