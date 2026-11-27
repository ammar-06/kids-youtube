"""Make one kids song video, start to finish.

    python make_video.py "ABC song with friendly animals" [--minutes 2.5] [--gpu colab|modal|kaggle|colab-notebook] [--no-wait]

1. Gemini writes the lyrics, the music style and the look of the video     -> lyrics.json
2. Kaggle GPU: ACE-Step sings the song, Whisper times every sung word      -> song.wav, words.json
3. Gemini writes one scene per ~5 s of song, matched to the lyrics          -> scenes.json
4. Kaggle GPU: LTX-Video makes a clip per scene (both T4s at once)          -> scenes/scene_001.mp4 ...
5. This PC: clips + song + word-by-word lyric captions                      -> final.mp4, youtube.txt

Everything for one video lives in videos/<date> - <topic>/. Each step is skipped when its
output already exists, so running the same command again continues where it stopped.
"""
import argparse
import datetime as dt
import difflib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
JOBS = os.path.join(HERE, "kaggle_jobs")
GEMINI_MODELS = ["gemini-3.7-flash", "gemini-3.1-flash-lite"]   # creative model first, the light one if it is busy
SCENE_SECONDS = 121 / 24                                          # LTX: 121 frames at 24 fps
VIDEO = {"width": 768, "height": 512, "frames": 121, "fps": 24, "steps": 40, "guidance": 3.0,
         "model": "Lightricks/LTX-Video"}
NEGATIVE = ("worst quality, low quality, blurry, jittery, distorted, deformed, extra limbs, text, letters, "
            "watermark, logo, scary, dark, violent, realistic photo")
CAPTION_FONT = "Arial Rounded MT Bold"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- Gemini
def gemini_key():
    env = os.path.join(HERE, ".env")
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    for line in open(env, encoding="utf-8"):
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("No GEMINI_API_KEY in .env")


def gemini_json(prompt, tries=3):
    key = gemini_key()
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                       "generationConfig": {"responseMimeType": "application/json", "temperature": 0.9}}).encode()
    last = None
    for model in GEMINI_MODELS:
        for attempt in range(tries):
            try:
                req = urllib.request.Request(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    data=body, headers={"content-type": "application/json", "x-goog-api-key": key})
                with urllib.request.urlopen(req, timeout=120) as r:
                    j = json.load(r)
                return json.loads(j["candidates"][0]["content"]["parts"][0]["text"])
            except Exception as e:  # noqa: BLE001
                last = e
                time.sleep(5 * (attempt + 1))
        log(f"  Gemini model {model} did not answer ({last}); trying the next one")
    sys.exit(f"Gemini failed: {last}")


# ---------------------------------------------------------------- Kaggle
def kaggle_user():
    r = subprocess.run(["kaggle", "config", "view"], capture_output=True, text=True)
    m = re.search(r"username:\s*(\S+)", r.stdout)
    if not m:
        sys.exit("Kaggle is not set up (no username in `kaggle config view`). See README.")
    return m.group(1)


def kaggle_run(slug, template, job, workdir, wait=True):
    """Send a GPU job (a script with JOB filled in) to Kaggle, wait for it, download its output."""
    user = kaggle_user()
    kdir = os.path.join(workdir, "jobs", slug)
    os.makedirs(kdir, exist_ok=True)
    code = open(os.path.join(JOBS, template), encoding="utf-8").read().replace("__JOB__", json.dumps(job))
    open(os.path.join(kdir, "job.py"), "w", encoding="utf-8").write(code)
    json.dump({"id": f"{user}/{slug}", "title": slug, "code_file": "job.py", "language": "python",
               "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_internet": True,
               "dataset_sources": [], "competition_sources": [], "kernel_sources": []},
              open(os.path.join(kdir, "kernel-metadata.json"), "w"), indent=1)
    r = subprocess.run(["kaggle", "kernels", "push", "-p", kdir, "--accelerator", "NvidiaTeslaT4"],
                       capture_output=True, text=True)
    if r.returncode != 0 or "successfully" not in r.stdout.lower():
        sys.exit(f"Kaggle push failed: {r.stdout}{r.stderr}")
    log(f"  sent to Kaggle: https://www.kaggle.com/code/{user}/{slug}")
    if not wait:
        sys.exit("Sent. Run the same command again later to continue.")
    last, t0 = "", time.time()
    while True:
        s = subprocess.run(["kaggle", "kernels", "status", f"{user}/{slug}"], capture_output=True, text=True).stdout
        state = (re.search(r'status "?([\w.]+)', s) or [None, s.strip()])[1]
        if state != last:
            log(f"  Kaggle: {state.split('.')[-1].lower()} (after {int((time.time() - t0) / 60)} min)")
            last = state
        if any(k in state.upper() for k in ("COMPLETE", "ERROR", "CANCEL")):
            break
        time.sleep(60)
    out = os.path.join(kdir, "out")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    subprocess.run(["kaggle", "kernels", "output", f"{user}/{slug}", "-p", out], capture_output=True, text=True)
    if "COMPLETE" not in state.upper():
        logf = [f for f in os.listdir(out) if f.endswith(".log")]
        tail = ""
        if logf:
            try:
                tail = "".join(e.get("data", "") for e in json.load(open(os.path.join(out, logf[0]), encoding="utf-8")))[-2500:]
            except Exception:  # noqa: BLE001
                tail = open(os.path.join(out, logf[0]), encoding="utf-8", errors="replace").read()[-2500:]
        sys.exit(f"Kaggle job {slug} ended with {state}. Last log lines:\n{tail}")
    return out


# ---------------------------------------------------------------- Google Colab (backup for a busy Kaggle)
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")


def colab_notebook(kind, template, job, token):
    """A ready Colab notebook for one GPU job: saves its work to Google Drive (a disconnect loses nothing),
    then downloads one results zip that make_video.py picks up from the Downloads folder."""
    code = open(os.path.join(JOBS, template), encoding="utf-8").read().replace("__JOB__", json.dumps(job))
    drive_dir = f"/content/drive/MyDrive/kids-youtube/{kind}_{token}"
    zip_name = f"kids_{kind}_{token}"

    def cell(src, kind_="code"):
        c = {"cell_type": kind_, "metadata": {}, "source": src.splitlines(True)}
        if kind_ == "code":
            c.update(outputs=[], execution_count=None)
        return c

    steps = (f"# Kids video: {kind} ({token})\n\n"
             "1. **Runtime → Change runtime type → T4 GPU → Save**\n"
             "2. **Runtime → Run all**, and allow Google Drive when it asks (the work is saved there, so a disconnect loses nothing)\n"
             f"3. When it finishes, your browser downloads **{zip_name}.zip**. Then run the same `make_video.py` command again on your PC.\n\n"
             "If the session disconnects, just do step 2 again: it continues where it stopped.")
    cells = [
        cell(steps, "markdown"),
        cell("import torch\nassert torch.cuda.is_available(), 'No GPU: Runtime -> Change runtime type -> T4 GPU, then Run all again'\n"
             "print('GPU:', torch.cuda.get_device_name(0))\n"
             "import os\n"
             "# Google Drive keeps the work if Colab disconnects; without it (popup closed or blocked) it still runs\n"
             f"OUT = {drive_dir!r}\n"
             "try:\n"
             "    from google.colab import drive\n"
             "    drive.mount('/content/drive')\n"
             "except Exception as e:\n"
             f"    OUT = '/content/{kind}_{token}'\n"
             "    print('Google Drive not connected (' + str(e) + '): working without it. If Colab disconnects, start again.')\n"
             "os.makedirs(OUT, exist_ok=True)\nos.environ['JOB_OUT'] = OUT\nprint('saving to', OUT)"),
        cell("JOB_SCRIPT = " + repr(code) + "\nopen('/content/job.py', 'w').write(JOB_SCRIPT)\n"
             "import subprocess, sys\n"
             "# show the job's messages here and keep them in log.txt (next to the results)\n"
             "logf = open(os.path.join(OUT, 'log.txt'), 'a')\n"
             "p = subprocess.Popen([sys.executable, '-u', '/content/job.py'], env=os.environ.copy(),\n"
             "                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)\n"
             "tail = []\n"
             "for line in p.stdout:\n"
             "    print(line, end='', flush=True); logf.write(line); logf.flush()\n"
             "    tail = (tail + [line])[-40:]\n"
             "p.wait(); logf.close()\n"
             "if p.returncode != 0:\n"
             "    print('\\n===== LAST LINES (screenshot these) =====\\n' + ''.join(tail))\n"
             "    if p.returncode in (-9, 137):\n"
             "        print('Killed: out of memory (RAM).')\n"
             "    raise SystemExit(f'The job failed (exit code {p.returncode})')"),
        cell(f"import shutil\nfrom google.colab import files\n"
             f"z = shutil.make_archive('/content/{zip_name}', 'zip', OUT)\nprint('results:', z)\nfiles.download(z)"),
    ]
    return {"cells": cells, "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"},
            "kernelspec": {"name": "python3", "display_name": "Python 3"}}, "nbformat": 4, "nbformat_minor": 0}


# ---------------------------------------------------------------- Colab, automatic (official Colab CLI in Docker)
# docker/colab/Dockerfile holds Google's colab-cli (Linux only); the Google sign-in lives in the
# "kids-colab-home" Docker volume, so it is asked once. One-time: docker build -t kids-colab docker/colab
COLAB_POLL_S = 60
COLAB_NEW_TRIES = 12            # no free T4 right now: try again every 5 minutes, up to an hour


def colab_cli(*args, stdin=None, check=True):
    cmd = ["docker", "run", "-i", "--rm", "-v", "kids-colab-home:/root", "-v", f"{HERE}:/work", "kids-colab", *args]
    r = subprocess.run(cmd, input=stdin, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"colab {args[0]} failed: {(r.stdout + r.stderr).strip()[-800:]}")
    return r


def to_work(path):   # a path under this folder as the container sees it
    return "/work/" + os.path.relpath(path, HERE).replace(os.sep, "/")


START = r'''
import os, subprocess
os.makedirs("/content/out", exist_ok=True)
for f in ("/content/job.log", "/content/job.rc"):
    if os.path.exists(f): os.remove(f)
subprocess.Popen("python -u /content/job.py > /content/job.log 2>&1; echo $? > /content/job.rc", shell=True,
                 env=dict(os.environ, JOB_OUT="/content/out"), start_new_session=True)
print("started")
'''
POLL = r'''
import os
log = open("/content/job.log", errors="replace").read() if os.path.exists("/content/job.log") else ""
print(log[{off}:][-20000:], end="")
print("\n@@LEN", len(log))
print("@@RC", open("/content/job.rc").read().strip() if os.path.exists("/content/job.rc") else "")
print("@@FILES", " ".join(sorted(os.path.relpath(os.path.join(d, f), "/content/out") for d, _, fs in os.walk("/content/out") for f in fs)))
'''


def colab_auto_once(kind, code, workdir, out, name):
    """One Colab session: run the job, stream its log, download its files as they appear. Returns the exit code."""
    jobs = os.path.join(workdir, "jobs", f"colab-{kind}")
    os.makedirs(jobs, exist_ok=True)
    job_py = os.path.join(jobs, "job.py")
    open(job_py, "w", encoding="utf-8").write(code)
    logf = open(os.path.join(jobs, "colab.log"), "a", encoding="utf-8")
    for i in range(COLAB_NEW_TRIES):
        r = colab_cli("new", "-s", name, "--gpu", "T4", check=False)
        if r.returncode == 0:
            break
        log(f"  Colab has no free T4 right now ({(r.stdout + r.stderr).strip()[-160:]}); trying again in 5 min")
        time.sleep(300)
    else:
        raise RuntimeError("Colab gave no T4 GPU for an hour")
    try:
        colab_cli("upload", "-s", name, to_work(job_py), "/content/job.py")
        colab_cli("exec", "-s", name, stdin=START)
        log(f"  Colab T4 running the {kind} job (log: {os.path.join(jobs, 'colab.log')})")
        off, got, rc = 0, set(), ""
        while True:
            time.sleep(COLAB_POLL_S)
            r = colab_cli("exec", "-s", name, stdin=POLL.replace("{off}", str(off)))
            text = r.stdout
            body, _, tail = text.rpartition("\n@@LEN ")
            if not tail:
                raise RuntimeError(f"unexpected Colab reply: {text[-300:]}")
            new = body
            if new.strip():
                print(new, end="" if new.endswith("\n") else "\n", flush=True)
                logf.write(new)
                logf.flush()
            m = re.search(r"^(\d+)", tail)
            off = int(m.group(1)) if m else off
            rc = (re.search(r"@@RC (.*)", tail) or [None, ""])[1].strip()
            files = (re.search(r"@@FILES (.*)", tail) or [None, ""])[1].split()
            for rel in files:   # download each finished file once (scenes come one by one)
                if rel in got or (not rc and not rel.startswith("scenes/")):
                    continue
                dest = os.path.join(out, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                colab_cli("download", "-s", name, f"/content/out/{rel}", to_work(dest))
                got.add(rel)
                if rel.startswith("scenes/"):   # straight into the video folder too: a rerun never redoes it
                    shutil.copy(dest, os.path.join(workdir, rel))
            if rc:
                return int(rc) if rc.lstrip("-").isdigit() else 1
    finally:
        colab_cli("stop", "-s", name, check=False)   # always give the GPU back


def colab_auto_run(kind, template, job, workdir, attempts=3):
    """Run a GPU job on a free Colab T4 with no clicks. A lost session is retried; for scenes only the
    clips still missing are made again."""
    src = open(os.path.join(JOBS, template), encoding="utf-8").read()
    out = os.path.join(workdir, "jobs", f"colab-{kind}", "out")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    os.makedirs(os.path.join(workdir, "scenes"), exist_ok=True)
    for attempt in range(1, attempts + 1):
        todo = job
        if kind == "scenes":
            left = [s for s in job["scenes"]
                    if not os.path.exists(os.path.join(workdir, "scenes", f"scene_{s['n']:03d}.mp4"))]
            if not left:
                return out
            todo = {**job, "scenes": left}
        try:
            rc = colab_auto_once(kind, src.replace("__JOB__", json.dumps(todo)), workdir, out, f"kids-{kind}")
        except RuntimeError as e:
            log(f"  Colab session problem: {e}")
            rc = None
        if rc == 0:
            return out
        if rc is not None and kind == "song":
            sys.exit(f"Colab {kind} job failed (exit code {rc}); its messages are printed above")
        log(f"  attempt {attempt} of {attempts} did not finish; starting a new session")
    sys.exit(f"Colab {kind} job did not finish after {attempts} sessions")


def colab_run(kind, template, job, workdir):
    """Use the results zip if it is in Downloads; otherwise write the notebook, explain, and stop."""
    import hashlib
    import zipfile
    token = hashlib.sha1(json.dumps(job, sort_keys=True).encode()).hexdigest()[:8]
    zips = [f for f in os.listdir(DOWNLOADS) if f.startswith(f"kids_{kind}_{token}") and f.endswith(".zip")] \
        if os.path.isdir(DOWNLOADS) else []
    out = os.path.join(workdir, "jobs", f"colab-{kind}", "out")
    if zips:
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        newest = max((os.path.join(DOWNLOADS, f) for f in zips), key=os.path.getmtime)
        zipfile.ZipFile(newest).extractall(out)
        log(f"  took the Colab results from {newest}")
        return out
    nb = os.path.join(workdir, "colab", f"{kind}.ipynb")
    os.makedirs(os.path.dirname(nb), exist_ok=True)
    json.dump(colab_notebook(kind, template, job, token), open(nb, "w", encoding="utf-8"), indent=1)
    sys.exit(f"""
  This step runs on Google Colab's free GPU:
    1. Open https://colab.research.google.com  ->  File  ->  Upload notebook  ->  choose:
         {nb}
    2. Runtime -> Change runtime type -> T4 GPU -> Save
    3. Runtime -> Run all   (allow Google Drive when asked)
    4. When it finishes, your browser downloads kids_{kind}_{token}.zip into Downloads.
    5. Run the same make_video.py command again: it picks the file up and continues.""")


# Modal budget guard: the account must never be charged. Modal gives $30 of free credit a month; GPU work
# here may use at most MODAL_GPU_BUDGET of it in any 31 days, which leaves room for model storage
# (~$0.09/GB/month) and a margin. Every GPU second is counted at a padded rate (L4 $0.80/h + CPU + RAM).
MODAL_GPU_BUDGET = 22.0          # dollars per 31 days, of the $30 free credit
MODAL_RATE_PER_HOUR = 1.25       # padded cost of one L4 container hour
MODAL_STARTUP_S = 180            # padded cold start per container (image pull, model load before the job)
MODAL_LEDGER = os.path.join(HERE, "modal_budget.json")


def modal_spent():
    """Estimated dollars of Modal GPU use in the last 31 days, from the local ledger."""
    runs = json.load(open(MODAL_LEDGER)) if os.path.exists(MODAL_LEDGER) else []
    cutoff = time.time() - 31 * 86400
    return sum(r["dollars"] for r in runs if r["t"] > cutoff), runs


def modal_record(kind, dollars, note):
    _, runs = modal_spent()
    runs.append({"t": time.time(), "date": time.strftime("%Y-%m-%d %H:%M"), "kind": kind,
                 "dollars": round(dollars, 3), "note": note})
    json.dump(runs, open(MODAL_LEDGER, "w"), indent=1)


def modal_run(kind, template, job, workdir):
    """Run a GPU job on Modal (modal_gpu.py) and write its files to <workdir>/jobs/modal-<kind>/out.
    The scenes are split over up to SCENES_MAX_GPUS GPUs at once. Refuses to start if the job's worst case
    (every container running to its timeout) could take Modal use past the budget."""
    import modal
    import modal_gpu
    k = max(1, min(modal_gpu.SCENES_MAX_GPUS, len(job["scenes"]))) if kind == "scenes" else 1
    limit_s = modal_gpu.SCENES_TIMEOUT if kind == "scenes" else modal_gpu.SONG_TIMEOUT
    worst = k * (limit_s + MODAL_STARTUP_S) / 3600 * MODAL_RATE_PER_HOUR + (0.10 if kind == "scenes" else 0)
    spent, _ = modal_spent()
    log(f"  Modal budget: ${spent:.2f} used of ${MODAL_GPU_BUDGET:.0f} (last 31 days); this job at most ${worst:.2f}")
    if spent + worst > MODAL_GPU_BUDGET:
        sys.exit(f"STOPPED to protect the free credit: this {kind} job could cost up to ${worst:.2f} and "
                 f"${spent:.2f} is already used of the ${MODAL_GPU_BUDGET:.0f} budget. Wait for older runs to "
                 f"fall out of the 31-day window, or use --gpu kaggle.")
    src = open(os.path.join(JOBS, template), encoding="utf-8").read()
    out = os.path.join(workdir, "jobs", f"modal-{kind}", "out")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    t0 = time.time()
    results = []
    try:
        with modal.enable_output(), modal_gpu.app.run():
            if kind == "scenes":
                modal_gpu.fetch_video_model.remote(job.get("model", "Lightricks/LTX-Video"))
                codes = [src.replace("__JOB__", json.dumps({**job, "scenes": job["scenes"][i::k]})) for i in range(k)]
                results = list(modal_gpu.scenes.map(codes, return_exceptions=True))
            else:
                results = [modal_gpu.song.remote(src.replace("__JOB__", json.dumps(job)))]
    finally:
        # count what ran: measured job time per container, or wall time for a container that did not report
        wall = time.time() - t0
        used = sum((r[2] if isinstance(r, tuple) else wall) + MODAL_STARTUP_S for r in results) or k * wall
        cost = used / 3600 * MODAL_RATE_PER_HOUR + (0.10 if kind == "scenes" else 0)
        modal_record(kind, cost, f"{len(results)} container(s), {used / 60:.0f} GPU-min")
        log(f"  Modal: this job ~${cost:.2f}; total ~${modal_spent()[0]:.2f} of ${MODAL_GPU_BUDGET:.0f}")
    failed = [r for r in results if not isinstance(r, tuple)]
    results = [r for r in results if isinstance(r, tuple)]
    infos = []
    for rc, files, _ in results:
        for rel, data in files.items():
            if rel == "info.json":
                infos.append(json.loads(data))
                continue
            for p in [os.path.join(out, rel)] + ([os.path.join(workdir, rel)] if rel.startswith("scenes") else []):
                os.makedirs(os.path.dirname(p), exist_ok=True)   # finished scenes go straight into the video
                open(p, "wb").write(data)                         # folder, so a rerun never pays for them twice
    json.dump(infos[0] if len(infos) == 1 else infos, open(os.path.join(out, "info.json"), "w"), indent=1)
    bad = [rc for rc, _, _ in results if rc]
    if bad or failed:
        sys.exit(f"Modal {kind} job failed (exit codes {bad}, errors {failed}); its messages are printed above. "
                 "Finished scenes are kept: run the same command again to make only the missing ones.")
    return out


def gpu_run(kind, slug, template, job, workdir, a):
    if a.gpu == "colab":
        return colab_auto_run(kind, template, job, workdir)
    if a.gpu == "colab-notebook":
        return colab_run(kind, template, job, workdir)
    if a.gpu == "modal":
        return modal_run(kind, template, job, workdir)
    return kaggle_run(slug, template, job, workdir, wait=not a.no_wait)


# ---------------------------------------------------------------- lyrics timing
def tokens(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def lyric_lines(lyrics):
    return [ln.strip() for ln in lyrics.splitlines() if ln.strip() and not re.match(r"^\[.*\]$", ln.strip())]


def time_lines(lines, words, duration):
    """Start/end (and per-word times) of every lyric line, by matching the lyric words to the words Whisper
    heard. Words Whisper missed get times in between their matched neighbours."""
    lyr = [(li, t) for li, ln in enumerate(lines) for t in tokens(ln)]
    heard = [tokens(w["w"])[0] if tokens(w["w"]) else "" for w in words]
    times = [None] * len(lyr)
    sm = difflib.SequenceMatcher(a=[t for _, t in lyr], b=heard, autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            w = words[blk.b + k]
            times[blk.a + k] = (w["s"], w["e"])
    known = [i for i, t in enumerate(times) if t]
    if not known:   # nothing matched: spread the lines evenly
        step = duration / max(1, len(lyr))
        times = [(i * step, (i + 1) * step) for i in range(len(lyr))]
    else:
        for i in range(len(times)):
            if times[i]:
                continue
            prev = max((k for k in known if k < i), default=None)
            nxt = min((k for k in known if k > i), default=None)
            a = times[prev][1] if prev is not None else 0.0
            b = times[nxt][0] if nxt is not None else min(duration, a + 2.0)
            lo, hi = (prev if prev is not None else -1), (nxt if nxt is not None else len(times))
            frac = (i - lo) / (hi - lo)
            s = a + (b - a) * frac
            times[i] = (s, s + max(0.15, (b - a) / (hi - lo)))
    out = []
    for li, ln in enumerate(lines):
        ws = [(t, times[i]) for i, (l2, t) in enumerate(lyr) if l2 == li]
        if ws:
            out.append({"line": ln, "start": round(ws[0][1][0], 2), "end": round(ws[-1][1][1], 2),
                        "words": [{"w": w, "s": round(s, 2), "e": round(e, 2)} for w, (s, e) in ws]})
    return out


# ---------------------------------------------------------------- captions + final video
def ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def write_captions(timed, path, duration):
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            f"Style: Lyric,{CAPTION_FONT},78,&H00FFFFFF,&H00FFFFFF,&H00602010,&H80000000,1,0,0,0,100,100,1,0,1,7,3,2,90,90,70,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    for i, ln in enumerate(timed):
        show_until = timed[i + 1]["start"] if i + 1 < len(timed) else min(duration, ln["end"] + 2.0)
        show_until = max(show_until, ln["end"])
        ws = ln["words"]
        for k, w in enumerate(ws):   # the line stays up; the word being sung turns yellow
            a = ln["start"] if k == 0 else w["s"]
            b = ws[k + 1]["s"] if k + 1 < len(ws) else show_until
            txt = " ".join(("{\\c&H00E6FF&}" + x["w"].upper() + "{\\c&HFFFFFF&}") if j == k else x["w"].upper()
                           for j, x in enumerate(ws))
            ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Lyric,,0,0,0,,{txt}")
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def assemble(folder, song, scene_files, captions, out):
    dur = probe_duration(song)
    lst = os.path.join(folder, "scenes", "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for s in scene_files:
            f.write(f"file '{os.path.basename(s)}'\n")
    ass = os.path.relpath(captions, folder).replace("\\", "/")
    # crop the 3:2 clips to 16:9, enlarge to 1080p; hold the last frame if the clips end before the song
    vf = (f"crop=iw:trunc(iw*9/32)*2,scale=1920:1080:flags=lanczos,fps=24,setsar=1,"
          f"tpad=stop_mode=clone:stop_duration=30,ass=filename='{ass}'")
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", os.path.relpath(lst, folder),
           "-i", os.path.relpath(song, folder), "-vf", vf, "-map", "0:v", "-map", "1:a", "-t", f"{dur:.2f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", os.path.relpath(out, folder)]
    subprocess.run(cmd, check=True, cwd=folder)


# ---------------------------------------------------------------- the pipeline
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topic", help='what the song is about, e.g. "ABC song with friendly animals"')
    ap.add_argument("--minutes", type=float, default=2.5, help="song length, 2 to 4 (default 2.5)")
    ap.add_argument("--no-wait", action="store_true", help="send the Kaggle job and stop (run again to continue)")
    ap.add_argument("--gpu", choices=["colab", "modal", "kaggle", "colab-notebook"], default="colab",
                    help="where the GPU steps run: colab (automatic, free T4 through the Colab CLI in Docker), "
                         "modal (automatic, needs a card on Modal), kaggle (automatic, free but often queued) or "
                         "colab-notebook (you upload a ready notebook)")
    a = ap.parse_args()
    seconds = int(min(240, max(120, a.minutes * 60)))   # ACE-Step sings up to 4 minutes in one go

    slug = re.sub(r"[^\w\- ]", "", a.topic).strip()[:60]
    existing = [d for d in os.listdir(os.path.join(HERE, "videos")) if d.endswith(f" - {slug}")] \
        if os.path.isdir(os.path.join(HERE, "videos")) else []
    folder = os.path.join(HERE, "videos", existing[0] if existing else f"{dt.date.today()} - {slug}")
    os.makedirs(os.path.join(folder, "scenes"), exist_ok=True)
    log(f"Video folder: {folder}")

    # 1. lyrics
    lyr_path = os.path.join(folder, "lyrics.json")
    if not os.path.exists(lyr_path):
        log("1/5 Gemini: writing the lyrics...")
        lines_wanted = int(seconds / 3.2)
        j = gemini_json(f"""You write original songs for a kids YouTube channel (ages 2-7). Topic: "{a.topic}".
Write a NEW, original, catchy, educational song about {seconds // 60} min {seconds % 60} s long (about {lines_wanted} short sung lines),
with simple words, strong rhymes and a chorus that repeats 3 times. Never copy existing songs or their lyrics.
Return JSON:
{{"title": "song title",
  "lyrics": "the lyrics with section tags on their own lines: [verse], [chorus], [bridge], [outro]; one sung line per line",
  "music_style": "comma-separated music tags for an AI music model, e.g. children's song, nursery rhyme, happy, upbeat, ukulele, glockenspiel, hand claps, cheerful female vocal, clear vocals, 110 bpm",
  "visual_style": "one sentence describing ONE consistent look for every scene, e.g. bright colorful 3D cartoon animation, soft sunny lighting, rounded friendly shapes, Pixar-like",
  "characters": "short fixed descriptions of the 1-3 recurring characters (species, colors, clothes) so they look the same in every scene"}}""")
        j["lyrics_plain"] = "\n".join(lyric_lines(j["lyrics"]))
        j["seconds"] = seconds
        json.dump(j, open(lyr_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        log(f"  \"{j['title']}\" ({len(lyric_lines(j['lyrics']))} lines)")
    L = json.load(open(lyr_path, encoding="utf-8"))

    # 2. song
    song = os.path.join(folder, "song.wav")
    words_path = os.path.join(folder, "words.json")
    if not (os.path.exists(song) and os.path.exists(words_path)):
        log(f"2/5 {a.gpu.capitalize()} GPU: singing the song (ACE-Step) and timing the words (Whisper)...")
        out = gpu_run("song", "kids-song", "song.py", {"seconds": L["seconds"], "style": L["music_style"],
                                                       "lyrics": L["lyrics"], "lyrics_plain": L["lyrics_plain"],
                                                       "seed": 42, "steps": 60}, folder, a)
        for f in ("song.wav", "words.json"):
            shutil.copy(os.path.join(out, f), os.path.join(folder, f))
        if os.path.exists(os.path.join(out, "info.json")):
            shutil.copy(os.path.join(out, "info.json"), os.path.join(folder, "song_info.json"))
    duration = probe_duration(song)
    timed = time_lines(lyric_lines(L["lyrics"]), json.load(open(words_path, encoding="utf-8")), duration)
    json.dump(timed, open(os.path.join(folder, "lyrics_timed.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    log(f"  song: {duration:.0f} s, {len(timed)} lyric lines timed")

    # 3. scene script
    sc_path = os.path.join(folder, "scenes.json")
    if not os.path.exists(sc_path):
        n = math.ceil(duration / SCENE_SECONDS)
        log(f"3/5 Gemini: writing {n} scenes...")
        slots = []
        for k in range(n):
            s, e = k * SCENE_SECONDS, (k + 1) * SCENE_SECONDS
            sung = " / ".join(t["line"] for t in timed if t["start"] < e and t["end"] > s)
            slots.append({"n": k + 1, "from": round(s, 1), "to": round(e, 1), "sung": sung or "(music only)"})
        j = gemini_json(f"""You direct an animated music video for a kids song. Song: "{L['title']}".
Look of every scene: {L['visual_style']}
Recurring characters (always describe them exactly like this): {L['characters']}
Here are {n} time slots of about 5 seconds and what is sung in each:
{json.dumps(slots, ensure_ascii=False)}
For EACH slot write one scene for an AI text-to-video model: a single continuous shot that shows what is being sung,
with the characters described in full every time, the setting, the action and one simple camera move.
3-4 sentences, concrete and visual, cheerful and safe for small children, no text or letters on screen
(write e.g. "a big red apple" instead of "the letter A").
Return JSON: {{"scenes": [{{"n": 1, "prompt": "..."}}, ...]}} with exactly {n} scenes in order.""")
        scenes = j["scenes"][:n]
        while len(scenes) < n:   # never leave a gap
            scenes.append({"n": len(scenes) + 1, "prompt": scenes[-1]["prompt"]})
        for k, s in enumerate(scenes):
            s["n"] = k + 1
        json.dump({"scenes": scenes}, open(sc_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    scenes = json.load(open(sc_path, encoding="utf-8"))["scenes"]

    # 4. video scenes
    scene_dir = os.path.join(folder, "scenes")
    missing = [s for s in scenes if not os.path.exists(os.path.join(scene_dir, f"scene_{s['n']:03d}.mp4"))]
    if missing:
        log(f"4/5 {a.gpu.capitalize()} GPU: making {len(missing)} video scenes (LTX-Video)...")
        job = dict(VIDEO, style=L["visual_style"], negative=NEGATIVE, seed=7,
                   scenes=[{"n": s["n"], "prompt": s["prompt"]} for s in missing])
        out = gpu_run("scenes", "kids-scenes", "scenes.py", job, folder, a)
        for f in os.listdir(os.path.join(out, "scenes")):
            shutil.copy(os.path.join(out, "scenes", f), os.path.join(scene_dir, f))
        if os.path.exists(os.path.join(out, "info.json")):
            shutil.copy(os.path.join(out, "info.json"), os.path.join(folder, "scenes_info.json"))
    files = [os.path.join(scene_dir, f"scene_{s['n']:03d}.mp4") for s in scenes]
    files = [f for f in files if os.path.exists(f)]
    if not files:
        sys.exit("No scenes to put together.")

    # 5. final video
    final = os.path.join(folder, "final.mp4")
    log("5/5 Putting the video together (scenes + song + lyric captions)...")
    caps = os.path.join(folder, "captions.ass")
    write_captions(timed, caps, duration)
    assemble(folder, song, files, caps, final)
    yt = os.path.join(folder, "youtube.txt")
    if not os.path.exists(yt):
        d = gemini_json(f"""Write YouTube metadata for a kids song video (ages 2-7), song title "{L['title']}", topic "{a.topic}".
Lyrics: {L['lyrics_plain'][:1500]}
Return JSON: {{"title": "max 90 chars, friendly, searchable", "description": "3-5 short lines about what kids learn, then the full lyrics",
"tags": ["12-20 search tags"]}}""")
        open(yt, "w", encoding="utf-8").write(
            f"TITLE:\n{d['title']}\n\nDESCRIPTION:\n{d['description']}\n\nTAGS:\n{', '.join(d['tags'])}\n\n"
            f"---\nAudience: Yes, it's made for kids. Length: {probe_duration(final):.0f} s.\n")
    log(f"DONE: {final}")


if __name__ == "__main__":
    main()
