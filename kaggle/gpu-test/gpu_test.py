import subprocess, torch, shutil
print("torch", torch.__version__, "cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        p = torch.cuda.get_device_properties(i)
        print(f"GPU {i}: {p.name}, {p.total_memory/1e9:.1f} GB")
print(subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv"], capture_output=True, text=True).stdout)
total, used, free = shutil.disk_usage("/kaggle/working")
print(f"disk free: {free/1e9:.0f} GB")
