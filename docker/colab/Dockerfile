# Google's official Colab CLI (Linux/macOS only) in a container, so make_video.py can drive Colab GPUs from Windows.
FROM python:3.12-slim
RUN pip install --no-cache-dir google-colab-cli==0.8.0 keyrings.alt==5.0.2
# keep the Google sign-in in a file (mounted volume) instead of an OS keyring, which containers do not have
ENV PYTHON_KEYRING_BACKEND=keyrings.alt.file.PlaintextKeyring
WORKDIR /work
ENTRYPOINT ["colab"]
