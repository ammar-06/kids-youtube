# Modal GPU backend for make_video.py (--gpu modal): runs kaggle_jobs/song.py and scenes.py on Modal's GPUs.
# The images are built once and cached by Modal; model weights stay in the "kids-cache" volume between runs.
# One-time setup: pip install modal==1.6.4, then: python -m modal setup
import os
import subprocess
import sys

import modal

app = modal.App("kids-youtube")
cache = modal.Volume.from_name("kids-cache", create_if_missing=True)

SITE = "/usr/local/lib/python3.11/site-packages/nvidia"
base = (
    modal.Image.debian_slim(python_version="3.11")   # ACE-Step's own Python: its pinned packages install as-is
    .apt_install("git", "ffmpeg", "libsndfile1")
    .pip_install("torch==2.5.1", "torchaudio==2.5.1", "torchvision==0.20.1",
                 index_url="https://download.pytorch.org/whl/cu124")
    .env({"LD_LIBRARY_PATH": f"{SITE}/cudnn/lib:{SITE}/cublas/lib", "HF_HOME": "/cache/hf"})
)
song_image = (
    base.pip_install("git+https://github.com/ace-step/ACE-Step.git@1bee4c9f5b43e30995f8d4d33b3919197ce1bd68",
                     "diffusers==0.33.1", "faster-whisper==1.2.1", "soundfile")
)
scenes_image = base.pip_install("diffusers==0.35.2", "transformers==4.57.1", "accelerate==1.10.1",
                                "sentencepiece", "imageio", "imageio-ffmpeg")


# Hard time limits (Modal kills a container at its timeout). make_video.py budgets the worst case from these.
SONG_TIMEOUT = 30 * 60
SCENES_TIMEOUT = 75 * 60
SCENES_MAX_GPUS = 5


def _run(code):
    """Run one job script with JOB_OUT=/out and return (exit code, {relative path: bytes}, seconds used)."""
    import time
    t0 = time.time()
    # keep every model download (Hugging Face, ACE-Step checkpoints) in the persistent volume
    os.makedirs("/cache/dotcache", exist_ok=True)
    home_cache = os.path.expanduser("~/.cache")
    if not os.path.islink(home_cache):
        subprocess.run(["rm", "-rf", home_cache])
        os.symlink("/cache/dotcache", home_cache)
    os.makedirs("/out", exist_ok=True)
    open("/tmp/job.py", "w").write(code)
    env = {**os.environ, "JOB_OUT": "/out", "JOB_PREINSTALLED": "1"}
    rc = subprocess.run([sys.executable, "-u", "/tmp/job.py"], env=env).returncode
    cache.commit()
    files = {}
    for dp, _, fs in os.walk("/out"):
        for f in fs:
            p = os.path.join(dp, f)
            files[os.path.relpath(p, "/out")] = open(p, "rb").read()
    return rc, files, time.time() - t0


@app.function(image=song_image, gpu="L4", volumes={"/cache": cache}, timeout=SONG_TIMEOUT)
def song(code):
    return _run(code)


@app.function(image=scenes_image, gpu="L4", volumes={"/cache": cache}, timeout=SCENES_TIMEOUT,
              max_containers=SCENES_MAX_GPUS)
def scenes(code):
    return _run(code)


@app.function(image=scenes_image, volumes={"/cache": cache}, timeout=1800)   # CPU only, no GPU cost
def fetch_video_model(model):
    """Download the video model into the volume once, before several GPU containers start in parallel."""
    from diffusers import LTXPipeline
    LTXPipeline.download(model)
    cache.commit()
