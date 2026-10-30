#!/usr/bin/env python3
"""Render a clearly labelled, original news-style visual/audio preview.

This is a design/renderer smoke test, not a real news bulletin. It deliberately
uses no unlicensed footage or copyrighted music. Requires ffmpeg and espeak-ng.
"""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NARRATION_LINES = [
    "This is a sample design preview, not a real news bulletin.",
    "Clearer visuals. Stronger storytelling.",
    "Subtitles that are easy to follow.",
    "Background music ducks under the narration. Facts come first.",
]
NARRATION = " ".join(NARRATION_LINES)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def make_music(path: Path, seconds: float, sample_rate: int = 48000) -> None:
    """Create a quiet, original ambient bed from synthesized tones."""
    total = int(seconds * sample_rate)
    chords = [(110.0, 164.81, 220.0), (98.0, 146.83, 196.0),
              (130.81, 196.0, 261.63), (110.0, 164.81, 220.0)]
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(total):
            t = i / sample_rate
            chord = chords[min(int(t // 5), len(chords) - 1)]
            fade_in = min(1.0, t / 1.5)
            fade_out = min(1.0, max(0.0, (seconds - t) / 2.0))
            sample = sum(math.sin(2 * math.pi * f * t) for f in chord) / 3
            # Soft, slow amplitude movement; no sampled/copyrighted music.
            sample *= 0.10 * fade_in * fade_out * (0.8 + 0.2 * math.sin(2 * math.pi * 0.12 * t))
            value = max(-32767, min(32767, int(sample * 32767)))
            frames.extend(value.to_bytes(2, "little", signed=True))
        wav.writeframes(frames)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(OUT / "news-style-preview.mp4"))
    args = parser.parse_args()
    for tool in ("ffmpeg", "ffprobe", "espeak-ng"):
        if not shutil.which(tool):
            raise SystemExit(f"Missing required tool: {tool}")
    OUT.mkdir(parents=True, exist_ok=True)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    voice = OUT / "preview-voice.wav"
    music = OUT / "original-ambient-bed.wav"
    captions = OUT / "preview-captions.srt"

    # Synthesize each caption line separately, then derive subtitle
    # timestamps from each generated WAV segment.
    segments = []
    subtitle_rows = []
    cursor = 0.0
    sample_rate = 22050
    for index, line in enumerate(NARRATION_LINES, start=1):
        segment = OUT / f"preview-voice-{index}.wav"
        run(["espeak-ng", "-v", "en-us", "-s", "148", "-w", str(segment), line])
        with wave.open(str(segment), "rb") as part:
            params = part.getparams()
            sample_rate = params.framerate
            frames = part.readframes(part.getnframes())
        segment_duration = len(frames) / (params.nchannels * params.sampwidth * params.framerate)
        start_time = cursor
        end_time = cursor + segment_duration
        subtitle_rows.append((start_time, end_time, line.upper()))
        segments.append(frames)
        cursor = end_time + 0.35

    with wave.open(str(voice), "wb") as combined:
        combined.setnchannels(1)
        combined.setsampwidth(2)
        combined.setframerate(sample_rate)
        for frames in segments:
            combined.writeframes(frames)
            combined.writeframes(b"\x00\x00" * int(0.35 * sample_rate))

    def stamp(seconds: float) -> str:
        millis = int(seconds * 1000)
        hours, millis = divmod(millis, 3_600_000)
        minutes, millis = divmod(millis, 60_000)
        secs, millis = divmod(millis, 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    captions.write_text(
        "\n\n".join(
            f"{i}\n{stamp(start_time)} --> {stamp(end_time)}\n{text}"
            for i, (start_time, end_time, text) in enumerate(subtitle_rows, start=1)
        ) + "\n",
        encoding="utf-8",
    )
    duration = max(18.0, cursor + 2.0)
    make_music(music, duration)

    # Motion is generated in FFmpeg: animated accent bar, changing story cards,
    # lower-third, ticker, and burn-in subtitles. No external media required.
    vf = (
        "drawbox=x=0:y=0:w=iw:h=ih:color=0x081426:t=fill,"
        "drawbox=x=0:y=0:w=iw:h=9:color=0xE11D48:t=fill,"
        "drawbox=x='mod(t*240,iw)':y=0:w=220:h=9:color=0xFBBF24:t=fill,"
        "drawbox=x=760:y=115:w=450:h=365:color=0x10243B@0.96:t=fill,"
        "drawbox=x=800:y=165:w=370:h=3:color=0xFBBF24:t=fill,"
        "drawbox=x=800:y=280:w=320:h=14:color=0x29435E:t=fill,"
        "drawbox=x=800:y=280:w='min(t*18,320)':h=14:color=0x38BDF8:t=fill,"
        "drawbox=x=800:y=325:w=270:h=14:color=0x29435E:t=fill,"
        "drawbox=x=800:y=325:w='min(max((t-3)*18,0),270)':h=14:color=0xFBBF24:t=fill,"
        "drawbox=x=800:y=370:w=220:h=14:color=0x29435E:t=fill,"
        "drawbox=x=800:y=370:w='min(max((t-6)*18,0),220)':h=14:color=0x34D399:t=fill,"
        f"drawtext=fontfile={FONT}:text='NEWS DESK  /  INDIA + WORLD':"
        "x=72:y=72:fontsize=27:fontcolor=0xFBBF24,"
        f"drawtext=fontfile={FONT}:text='THE STORY BEHIND':"
        "x=72:y=210:fontsize=48:fontcolor=white:"
        "enable='between(t,0,8)',"
        f"drawtext=fontfile={FONT}:text='THE HEADLINE':"
        "x=72:y=270:fontsize=48:fontcolor=white:"
        "enable='between(t,0,8)',"
        f"drawtext=fontfile={FONT}:text='CONTEXT. EVIDENCE.':"
        "x=72:y=210:fontsize=46:fontcolor=white:"
        "enable='between(t,8,16)',"
        f"drawtext=fontfile={FONT}:text='EXPLAINED.':"
        "x=72:y=270:fontsize=46:fontcolor=white:"
        "enable='between(t,8,16)',"
        f"drawtext=fontfile={FONT}:text='NO NOISE.':"
        "x=72:y=210:fontsize=50:fontcolor=white:"
        "enable='gte(t,16)',"
        f"drawtext=fontfile={FONT}:text='JUST THE FACTS.':"
        "x=72:y=270:fontsize=50:fontcolor=white:"
        "enable='gte(t,16)',"
        f"drawtext=fontfile={FONT}:text='SAMPLE DESIGN PREVIEW  |  NOT A REAL NEWS BULLETIN':"
        "x=72:y=590:fontsize=22:fontcolor=0xFBBF24,"
        f"drawtext=fontfile={FONT}:text='INDIA  •  WORLD  •  EXPLAINED':"
        "x=72:y=640:fontsize=25:fontcolor=white,"
        f"subtitles={captions.as_posix()}:force_style="
        "'FontName=DejaVu Sans,FontSize=18,Bold=1,PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00101010,BorderStyle=3,BackColour=&H9007111F,"
        "Outline=1,Shadow=0,Alignment=8,MarginV=640',scale=1920:1080:flags=lanczos"
    )
    filter_audio = (
        "[1:a]asplit=2[voice_sc][voice_mix];"
        "[2:a]volume=1.0,afade=t=in:st=0:d=1.5,afade=t=out:st="
        f"{max(0.0, duration-2):.2f}:d=2[music];"
        "[music][voice_sc]sidechaincompress=threshold=0.025:ratio=8:attack=20:release=400[ducked];"
        "[ducked][voice_mix]amix=inputs=2:duration=longest:dropout_transition=2,"
        "loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
    )
    run([
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"color=c=0x081426:s=1280x720:r=24:d={duration:.2f}",
        "-i", str(voice), "-i", str(music),
        "-filter_complex", f"[0:v]{vf}[vout];{filter_audio}",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", "-shortest", str(target),
    ])
    info = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_name,width,height,r_frame_rate,sample_rate",
         "-show_entries", "format=duration,size", "-of", "json", str(target)],
        check=True, capture_output=True, text=True)
    print(info.stdout)
    print(f"PREVIEW_OK={target}")
    print("NOTE=Design smoke test only; replace synthetic visuals and preview voice with verified news assets and production narration.")


if __name__ == "__main__":
    main()
