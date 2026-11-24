# Kids YouTube

Free pipeline for original kids song videos (2 to 5 minutes), for a long-video kids channel.

1. AI writes the song lyrics (Gemini, free API key)
2. The song with real singing is made from the lyrics (ACE-Step, on Kaggle's free GPU)
3. AI writes a scene-by-scene video script timed to the song (Gemini)
4. The video scenes are generated from the script (LTX-Video, on Kaggle's free GPU)
5. The scenes, the song and word-by-word lyric captions are put together into the final video (ffmpeg + Whisper, on this PC)

Work in progress.

## How to run

```
python make_video.py "ABC song with friendly animals"              # GPU steps on Kaggle (automatic)
python make_video.py "ABC song with friendly animals" --gpu colab  # GPU steps on Google Colab (backup)
```

With `--gpu colab`, each GPU step (the song, then the video scenes) creates a ready notebook in the
video's `colab` folder and stops with instructions: upload it on colab.research.google.com, choose the
T4 GPU, Run all, allow Google Drive. When it finishes, the browser downloads a results zip; run the same
command again and it picks the zip up from Downloads and continues.

Each video gets its own folder in `videos/`; running the same command again continues where it stopped.
