# Kaggle GPU job, step 4: one ~5 s video clip per scene with LTX-Video (diffusers).
# make_video.py fills in JOB below. Both T4 GPUs work at once, each on half of the scenes.
# Outputs in /kaggle/working/scenes/scene_001.mp4 ... and info.json (speed per scene).
import json
import os
import subprocess
import sys
import time

JOB = json.loads(r'''__JOB__''')
OUT = os.environ.get("JOB_OUT", "/kaggle/working")   # Kaggle; Colab sets JOB_OUT (a Google Drive folder)
os.makedirs(os.path.join(OUT, "scenes"), exist_ok=True)
t0 = time.time()


def sh(cmd):
    print("$", cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)


if not os.environ.get("JOB_PREINSTALLED"):   # Modal's image already has everything (modal_gpu.py)
    sh("pip install -q -U diffusers transformers accelerate sentencepiece imageio imageio-ffmpeg")

WORKER = r'''
import gc, json, os, sys, time, torch
from diffusers import LTXPipeline
from diffusers.utils import export_to_video
from transformers import AutoTokenizer, T5EncoderModel, T5Tokenizer

OUT = os.environ.get("JOB_OUT", "/kaggle/working")
job = json.loads(open(os.path.join(OUT, "job.json")).read())
gpu, ngpu = int(sys.argv[1]), int(sys.argv[2])
out = os.path.join(OUT, "scenes")
scenes = [s for i, s in enumerate(job["scenes"]) if i % ngpu == gpu
          and not os.path.exists(os.path.join(out, "scene_%03d.mp4" % s["n"]))]
model = job.get("model", "Lightricks/LTX-Video")
# bf16 only on GPUs that run it natively (compute 8.0+); a T4 (7.5) "supports" it by emulation, but its conv
# kernels fail ("GET was unable to find an engine"), so it gets float16
dtype = torch.bfloat16 if torch.cuda.get_device_capability(0)[0] >= 8 else torch.float16

# Stage 1: only the T5 text encoder (~9.5 GB), loaded straight onto the GPU (free Colab has ~12.7 GB of RAM, too
# little to hold T5 and the video model in RAM together). bf16 matmuls work on any recent GPU, and T5 overflows in
# float16. All prompts are turned into embeddings, then T5 is freed.
t = time.time()
try:   # the classic SentencePiece tokenizer: newer transformers misreads spiece.model as a tiktoken file
    tok = T5Tokenizer.from_pretrained(model, subfolder="tokenizer")
except Exception as e:  # noqa: BLE001
    print("T5Tokenizer failed, trying AutoTokenizer:", e, flush=True)
    tok = AutoTokenizer.from_pretrained(model, subfolder="tokenizer")
te = T5EncoderModel.from_pretrained(model, subfolder="text_encoder", torch_dtype=torch.bfloat16,
                                    device_map={"": 0}, low_cpu_mem_usage=True).eval()


def encode(text):   # same as LTXPipeline._get_t5_prompt_embeds (max 128 tokens, no mask into T5)
    ids = tok(text, padding="max_length", max_length=128, truncation=True, add_special_tokens=True,
              return_tensors="pt")
    with torch.no_grad():
        emb = te(ids.input_ids.to("cuda"))[0]
    return emb.to(dtype).cpu(), ids.attention_mask.bool().cpu()


neg = encode(job["negative"])
embeds = {s["n"]: encode(job["style"] + " " + s["prompt"]) for s in scenes}
del te
gc.collect()
torch.cuda.empty_cache()
print(f"GPU {gpu}: {len(embeds)} prompts encoded in {round(time.time() - t)} s", flush=True)

# Stage 2: the video model and decoder only (~5 GB), fully on the GPU: no CPU offload, so it is faster too
pipe = LTXPipeline.from_pretrained(model, text_encoder=None, tokenizer=None, torch_dtype=dtype)
pipe.to("cuda")
pipe.vae.enable_tiling()
times = []
for s in scenes:
    path = os.path.join(out, "scene_%03d.mp4" % s["n"])
    if os.path.exists(path):
        continue
    t = time.time()
    emb, mask = embeds[s["n"]]
    frames = pipe(
        prompt_embeds=emb.to("cuda"), prompt_attention_mask=mask.to("cuda"),
        negative_prompt_embeds=neg[0].to("cuda"), negative_prompt_attention_mask=neg[1].to("cuda"),
        width=job["width"], height=job["height"], num_frames=job["frames"],
        num_inference_steps=job["steps"], guidance_scale=job.get("guidance", 3.0),
        generator=torch.Generator("cpu").manual_seed(job.get("seed", 42) + s["n"]),
    ).frames[0]
    export_to_video(frames, path, fps=job["fps"])
    times.append(round(time.time() - t, 1))
    print(f"GPU {gpu}: scene {s['n']} done in {times[-1]} s", flush=True)
json.dump({"gpu": gpu, "dtype": str(dtype), "seconds_per_scene": times}, open(os.path.join(OUT, f"speed_gpu{gpu}.json"), "w"))
'''

open(os.path.join(OUT, "job.json"), "w").write(json.dumps(JOB))
open(os.path.join(OUT, "worker.py"), "w").write(WORKER)
import torch  # noqa: E402

n = max(1, torch.cuda.device_count())
print("GPUs:", [torch.cuda.get_device_name(i) for i in range(n)], flush=True)
procs = [subprocess.Popen([sys.executable, os.path.join(OUT, "worker.py"), str(i), str(n)],
                          env={**os.environ, "CUDA_VISIBLE_DEVICES": str(i)}) for i in range(n)]
codes = [p.wait() for p in procs]
done = sorted(f for f in os.listdir(os.path.join(OUT, "scenes")) if f.endswith(".mp4"))
info = {"gpus": n, "exit_codes": codes, "scenes_done": len(done), "scenes_asked": len(JOB["scenes"]),
        "total_s": round(time.time() - t0)}
for i in range(n):
    p = os.path.join(OUT, f"speed_gpu{i}.json")
    if os.path.exists(p):
        info[f"gpu{i}"] = json.load(open(p))
json.dump(info, open(os.path.join(OUT, "info.json"), "w"), indent=1)
for f in ("job.json", "worker.py"):
    os.remove(os.path.join(OUT, f))
print("done:", json.dumps(info), flush=True)
if len(done) < len(JOB["scenes"]):
    sys.exit(f"only {len(done)} of {len(JOB['scenes'])} scenes were made")
