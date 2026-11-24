# Kaggle GPU job, step 2: the song (ACE-Step) and the time of every sung word (faster-whisper).
# make_video.py fills in JOB below and sends this file to Kaggle. Outputs in /kaggle/working:
#   song.wav    the song
#   words.json  [{"w": word, "s": start, "e": end}, ...] for the lyric captions
#   info.json   timings and settings, for checking speed
import inspect
import json
import os
import subprocess
import sys
import time

JOB = json.loads(r'''__JOB__''')
OUT = os.environ.get("JOB_OUT", "/kaggle/working")   # Kaggle; Colab sets JOB_OUT (a Google Drive folder)
info = {"job": JOB}
t0 = time.time()


def sh(cmd):
    print("$", cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)


sh("pip install -q git+https://github.com/ace-step/ACE-Step.git faster-whisper")
info["install_s"] = round(time.time() - t0)

import torch  # noqa: E402

print("GPU:", torch.cuda.get_device_name(0), flush=True)
from acestep.pipeline_ace_step import ACEStepPipeline  # noqa: E402

# T4 has no native bfloat16: try it (PyTorch emulates it), else float32 with CPU offload to fit 16 GB.
t1 = time.time()
pipe = None
for dtype, offload in (("bfloat16", False), ("float32", True)):
    try:
        kw = {"checkpoint_dir": None, "dtype": dtype, "torch_compile": False}
        if "cpu_offload" in inspect.signature(ACEStepPipeline.__init__).parameters:
            kw["cpu_offload"] = offload
        pipe = ACEStepPipeline(**kw)
        info["dtype"] = dtype
        break
    except Exception as e:  # noqa: BLE001
        print(f"ACE-Step with {dtype} failed: {e}", flush=True)
if pipe is None:
    sys.exit("ACE-Step could not load")
print("ACE-Step call signature:", inspect.signature(pipe.__call__), flush=True)

song = os.path.join(OUT, "song.wav")
args = dict(
    audio_duration=float(JOB["seconds"]),
    prompt=JOB["style"],
    lyrics=JOB["lyrics"],
    infer_step=int(JOB.get("steps", 60)),
    guidance_scale=15.0,
    scheduler_type="euler",
    cfg_type="apg",
    omega_scale=10.0,
    manual_seeds=[int(JOB.get("seed", 42))],
    guidance_interval=0.5,
    guidance_interval_decay=0.0,
    min_guidance_scale=3.0,
    use_erg_tag=True,
    use_erg_lyric=True,
    use_erg_diffusion=True,
    oss_steps=[],
    guidance_scale_text=0.0,
    guidance_scale_lyric=0.0,
    save_path=song,
)
params = inspect.signature(pipe.__call__).parameters
if not any(p.kind == p.VAR_KEYWORD for p in params.values()):
    args = {k: v for k, v in args.items() if k in params}
for attempt in range(2):
    try:
        res = pipe(**args)
        break
    except TypeError as e:
        if attempt:
            raise
        # older/newer releases take the seed as text
        print("retrying with text seed:", e, flush=True)
        args["manual_seeds"] = str(JOB.get("seed", 42))
# Some versions add their own file name: find the newest audio file
if not os.path.exists(song):
    cands = [os.path.join(dp, f) for dp, _, fs in os.walk(OUT) for f in fs if f.endswith((".wav", ".mp3", ".flac"))]
    if not cands:
        sys.exit(f"no audio written (result: {res!r})")
    newest = max(cands, key=os.path.getmtime)
    os.replace(newest, song)
info["song_s"] = round(time.time() - t1)
print("song done in", info["song_s"], "s", flush=True)

del pipe
torch.cuda.empty_cache()

# Word timings of the singing (Whisper large-v3 on the GPU)
t2 = time.time()
from faster_whisper import WhisperModel  # noqa: E402

model = WhisperModel("large-v3", device="cuda", compute_type="float16")
segments, _ = model.transcribe(song, word_timestamps=True, language="en", vad_filter=False,
                               initial_prompt=" ".join(JOB["lyrics_plain"].split())[:800])
words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segments for w in (s.words or [])]
json.dump(words, open(os.path.join(OUT, "words.json"), "w"), indent=1)
info["whisper_s"] = round(time.time() - t2)
info["words"] = len(words)
info["total_s"] = round(time.time() - t0)
json.dump(info, open(os.path.join(OUT, "info.json"), "w"), indent=1)
print("done:", json.dumps({k: v for k, v in info.items() if k != "job"}), flush=True)
