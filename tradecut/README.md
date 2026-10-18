# TradeCut AI — phone-first trading-video editor MVP

This is an experimental, free/open-source editing MVP intended for short educational/trading commentary videos. It runs as a Streamlit app and uses FFmpeg plus optional local speech transcription.

## Features
- Upload an MP4/MOV recording
- Detect and shorten long silent gaps while preserving a little breathing room
- Normalize voice audio
- Optionally mix in music you own or have permission to use, ducked low under speech
- Generate an SRT caption file with a local Whisper model
- Suggest title ideas, thumbnail text, and editing notes from the transcript
- Export the edited MP4 and SRT file

## Deploy from Android (free tier; resource-limited)
1. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with the GitHub account that owns this repository.
2. Choose **Create app** and select repository `rebellovandana65-cmd/ai-youtube-studio`, branch `main`.
3. Set **Main file path** to `tradecut/app.py` and deploy.
4. Test with a small, non-sensitive 20–30 second clip first. If it fails during dependency installation or processing, check the app logs; free hosting may not have enough memory for transcription or larger files.

Keep the repository private if you don't want the source code public. Treat uploaded trading recordings as sensitive. Don't upload credentials or account identifiers.

## Run locally
1. Install Python 3.11 or newer.
2. In this folder run: `pip install -r requirements.txt`
3. Run: `streamlit run app.py`
4. Upload a short test clip first and preview the output before using a full recording.

The app obtains an FFmpeg executable through `imageio-ffmpeg`. The first transcription can take time because the speech model may need to download. Model downloads and processing require internet and sufficient memory/disk.

## Important limitations
- This is an MVP, not a guaranteed “perfect editor”. Automatic edits can cut a breath or a quiet word; always review the output.
- The free Streamlit hosting tier is resource-limited and may not reliably process video files. For private recordings, local processing is preferable.
- No service can honestly promise free hosting, unlimited usage, or lifetime availability.
- No AI API key is required. Transcription runs locally after the model is available.
- Music must be yours or properly licensed. The app does not download copyrighted tracks.
- It does not connect to Zerodha or verify trades. It edits the recording only; check all figures, captions, and claims yourself.
- Do not upload passwords, API keys, account numbers, client IDs, or other private financial information. Blur sensitive screen details before uploading.

## Quality defaults
- Keeps 0.22 seconds around detected long silences.
- Only shortens silences above 0.8 seconds.
- Keeps background music quiet and fades it in/out.
- Preserves the original aspect ratio and exports H.264/AAC MP4.
