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


# ACE-Step pins exact old versions (e.g. spacy==3.8.4) that do not install on Python 3.13 (Colab and Kaggle now).
# So: each requirement at its pinned version if that installs, else the newest; then ACE-Step itself without pins.
if not os.environ.get("JOB_PREINSTALLED"):   # Modal's image already has everything (modal_gpu.py)
    sh("rm -rf /tmp/ace-step && git clone -q --depth 1 https://github.com/ace-step/ACE-Step /tmp/ace-step")
    for req in open("/tmp/ace-step/requirements.txt").read().split():
        name = req.split("==")[0].split(">=")[0]
        if name in ("torch", "torchaudio", "torchvision"):
            continue   # keep the GPU builds that are already installed
        if subprocess.run(f"pip install -q '{req}'", shell=True).returncode and req != name:
            print(f"{req} does not install here: using the newest {name}", flush=True)
            if subprocess.run(f"pip install -q '{name}'", shell=True).returncode:
                print(f"WARNING: {name} did not install", flush=True)
    sh("pip install -q --no-deps /tmp/ace-step")
    sh("pip install -q faster-whisper")
    # transformers==4.50 (ACE-Step's pin) pulls huggingface_hub back to 0.x; the newest diffusers needs hub 1.x
    # (ImportError: resolve_revision). diffusers 0.33.1 is ACE-Step's own era and works with hub 0.x.
    sh("pip install -q diffusers==0.33.1")
info["install_s"] = round(time.time() - t0)

import torch  # noqa: E402
import torchaudio  # noqa: E402
import soundfile  # noqa: E402

print("GPU:", torch.cuda.get_device_name(0), flush=True)


def _save(path, src, sample_rate, *a, **k):  # newer torchaudio needs torchcodec to save; soundfile does not
    soundfile.write(str(path), src.detach().float().cpu().numpy().T, int(sample_rate))


torchaudio.save = _save
from acestep.pipeline_ace_step import ACEStepPipeline  # noqa: E402
from acestep.music_dcae.music_dcae_pipeline import MusicDCAE  # noqa: E402


def _decode_fp32(fn):
    """T4 (compute 7.5) has no bfloat16 convolution engine: the song model runs in bf16 fine, but the audio
    decoder's conv2d fails ("GET was unable to find an engine"). Decode in float32 there."""
    def wrapped(self, latents, *a, **k):
        if torch.cuda.get_device_capability(0)[0] < 8:
            self.to(torch.float32)
            latents = latents.float()
        return fn(self, latents, *a, **k)
    return wrapped


MusicDCAE.decode = _decode_fp32(MusicDCAE.decode)
MusicDCAE.decode_overlap = _decode_fp32(MusicDCAE.decode_overlap)

song = os.path.join(OUT, "song.wav")
REUSE = os.path.exists(song)   # a song made by an earlier run (uploaded back): only the timing is redone
if REUSE:
    print("reusing the song.wav made earlier; skipping ACE-Step", flush=True)
else:
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
# read the audio ourselves: faster-whisper's own reader (PyAV) breaks when Colab's av version differs
_wav, _sr = soundfile.read(song, dtype="float32", always_2d=True)
_audio = torchaudio.functional.resample(torch.from_numpy(_wav.mean(axis=1)), _sr, 16000).numpy()
_prompt = " ".join(JOB["lyrics_plain"].split())[:800]
try:
    from faster_whisper import WhisperModel  # noqa: E402
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    segments, _ = model.transcribe(_audio, word_timestamps=True, language="en", vad_filter=False,
                                   initial_prompt=_prompt)
    words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)}
             for s in segments for w in (s.words or [])]
    info["whisper"] = "faster-whisper"
except Exception as e:  # noqa: BLE001  e.g. "libcublas.so.12 not found" when the GPU stack is CUDA 13
    # OpenAI's own Whisper runs on PyTorch, so it works with whatever CUDA PyTorch was built for
    print(f"faster-whisper unavailable ({e}); using openai-whisper", flush=True)
    del_model = globals().pop("model", None)
    torch.cuda.empty_cache()
    if not os.environ.get("JOB_PREINSTALLED"):
        sh("pip install -q openai-whisper")
    import whisper  # noqa: E402
    model = whisper.load_model("large-v3", device="cuda")
    res = model.transcribe(_audio, language="en", word_timestamps=True, initial_prompt=_prompt,
                           fp16=True, condition_on_previous_text=False)
    words = [{"w": w["word"].strip(), "s": round(w["start"], 2), "e": round(w["end"], 2)}
             for s in res["segments"] for w in s.get("words", [])]
    info["whisper"] = "openai-whisper"
json.dump(words, open(os.path.join(OUT, "words.json"), "w"), indent=1)
info["whisper_s"] = round(time.time() - t2)
info["words"] = len(words)
info["total_s"] = round(time.time() - t0)
json.dump(info, open(os.path.join(OUT, "info.json"), "w"), indent=1)
print("done:", json.dumps({k: v for k, v in info.items() if k != "job"}), flush=True)
