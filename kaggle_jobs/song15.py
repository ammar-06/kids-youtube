# GPU job, step 2 with ACE-Step 1.5 (quality "between Suno v4.5 and v5" per its authors): the song plus the time
# of every sung word. make_video.py fills in JOB. Outputs in JOB_OUT:
#   song.wav (take A, used for the video), song_take_b.wav, words.json, info.json
# ACE-Step 1.5 needs Python 3.11-3.12 (Colab has 3.13): uv builds its own environment from the repo's uv.lock.
import json
import os
import subprocess
import sys
import time

JOB = json.loads(r'''__JOB__''')
OUT = os.environ.get("JOB_OUT", "/kaggle/working")
REPO = "/content/ace15" if os.path.isdir("/content") else "/tmp/ace15"
COMMIT = "ca1e85fe9430179831e6bc6be790c332190a3866"
info = {"job": {k: v for k, v in JOB.items() if k != "lyrics"}, "engine": "ACE-Step 1.5"}
t0 = time.time()
os.makedirs(OUT, exist_ok=True)


def sh(cmd):
    print("$", cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)


song = os.path.join(OUT, "song.wav")
if os.path.exists(song):
    print("reusing the song.wav made earlier; skipping ACE-Step", flush=True)
else:
    sh("pip install -q uv")
    if not os.path.isdir(REPO):
        sh(f"git clone -q https://github.com/ace-step/ACE-Step-1.5 {REPO} && cd {REPO} && git checkout -q {COMMIT}")
    sh(f"cd {REPO} && uv sync -q")
    dit, lm = JOB.get("dit", "acestep-v15-sft"), JOB.get("lm", "acestep-5Hz-lm-1.7B")
    sh(f"cd {REPO} && uv run acestep-download")                       # main model: VAE, text encoder, 1.7B LM
    if dit != "acestep-v15-turbo":
        sh(f"cd {REPO} && uv run acestep-download --model {dit} --skip-main")
    info["install_s"] = round(time.time() - t0)
    gen = {"caption": JOB["style"], "lyrics": JOB["lyrics"], "seconds": JOB["seconds"], "seed": JOB.get("seed", 42),
           "dit": dit, "lm": lm, "steps": JOB.get("steps15", 50), "out": OUT}
    open(f"{REPO}/kids_job.json", "w").write(json.dumps(gen))
    open(f"{REPO}/kids_gen.py", "w").write(r'''
import json, os, shutil, sys, time
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music
J = json.load(open("kids_job.json"))
t = time.time()
dit = AceStepHandler()
print("DiT:", dit.initialize_service(project_root=os.getcwd(), config_path=J["dit"], device="cuda"), flush=True)
llm = LLMHandler()
print("LM:", llm.initialize(checkpoint_dir=os.path.join(os.getcwd(), "checkpoints"), lm_model_path=J["lm"],
                            backend="pt", device="cuda"), flush=True)
print("models loaded in", round(time.time() - t), "s", flush=True)
params = GenerationParams(caption=J["caption"], lyrics=J["lyrics"], duration=float(J["seconds"]), vocal_language="en",
                          inference_steps=int(J["steps"]), guidance_scale=7.0, use_adg=True, shift=3.0,
                          seed=int(J["seed"]), thinking=True)
config = GenerationConfig(batch_size=2, use_random_seed=False, seeds=[int(J["seed"]), int(J["seed"]) + 1],
                          audio_format="wav")
t = time.time()
res = generate_music(dit, llm, params, config, save_dir=os.path.join(J["out"], "ace15_raw"))
if not res.success:
    sys.exit("ACE-Step 1.5 failed: %s" % res.error)
paths = [a["path"] for a in res.audios]
shutil.copy(paths[0], os.path.join(J["out"], "song.wav"))
if len(paths) > 1:
    shutil.copy(paths[1], os.path.join(J["out"], "song_take_b.wav"))
meta = [{k: a.get(k) for k in ("key", "bpm", "duration") if k in a} for a in res.audios]
json.dump({"gen_s": round(time.time() - t), "takes": meta}, open(os.path.join(J["out"], "ace15_info.json"), "w"))
print("song done in", round(time.time() - t), "s", meta, flush=True)
''')
    sh(f"cd {REPO} && uv run python kids_gen.py")
    shutil_raw = os.path.join(OUT, "ace15_raw")
    subprocess.run(["rm", "-rf", shutil_raw])

# Word timings of the singing, in Colab's own Python (its PyTorch matches the machine's CUDA)
import numpy  # noqa: E402,F401
import soundfile  # noqa: E402
import torch  # noqa: E402
import torchaudio  # noqa: E402

t2 = time.time()
_wav, _sr = soundfile.read(song, dtype="float32", always_2d=True)
_audio = torchaudio.functional.resample(torch.from_numpy(_wav.mean(axis=1)), _sr, 16000).numpy()
_prompt = " ".join(JOB["lyrics_plain"].split())[:800]
try:
    import whisper  # noqa: E402
except ImportError:
    sh("pip install -q openai-whisper")
    import whisper  # noqa: E402
model = whisper.load_model("large-v3", device="cuda")
res = model.transcribe(_audio, language="en", word_timestamps=True, initial_prompt=_prompt, fp16=True,
                       condition_on_previous_text=False)
words = [{"w": w["word"].strip(), "s": round(w["start"], 2), "e": round(w["end"], 2)}
         for s in res["segments"] for w in s.get("words", [])]
json.dump(words, open(os.path.join(OUT, "words.json"), "w"), indent=1)
info["whisper_s"] = round(time.time() - t2)
info["words"] = len(words)
info["total_s"] = round(time.time() - t0)
json.dump(info, open(os.path.join(OUT, "info.json"), "w"), indent=1)
print("done:", json.dumps({k: v for k, v in info.items() if k != "job"}), flush=True)
