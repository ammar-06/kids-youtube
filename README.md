# Kids YouTube

Free pipeline for original kids song videos (2 to 5 minutes), for a long-video kids channel.

1. AI writes the song lyrics (Gemini, free API key)
2. The song with real singing is made from the lyrics (ACE-Step, on Kaggle's free GPU)
3. AI writes a scene-by-scene video script timed to the song (Gemini)
4. The video scenes are generated from the script (LTX-Video, on Kaggle's free GPU)
5. The scenes, the song and word-by-word lyric captions are put together into the final video (ffmpeg + Whisper, on this PC)

Work in progress.
