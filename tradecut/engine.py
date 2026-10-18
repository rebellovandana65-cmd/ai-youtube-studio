from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg


def ffmpeg_path() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def run(cmd: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or "FFmpeg failed")[-3500:])
    return result


def duration_seconds(path: str) -> float:
    # FFmpeg reports duration in stderr; no separate ffprobe dependency needed.
    result = subprocess.run([ffmpeg_path(), "-i", path], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
    if not match:
        raise RuntimeError("Could not read video duration. Try an MP4 or MOV file.")
    h, m, s = match.groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def detect_keep_ranges(path: str, min_silence: float = 0.8, pad: float = 0.22):
    duration = duration_seconds(path)
    proc = subprocess.run(
        [ffmpeg_path(), "-hide_banner", "-i", path, "-vn", "-af",
         "silencedetect=noise=-36dB:d=0.8", "-f", "null", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=900
    )
    log = proc.stderr
    starts = [float(x) for x in re.findall(r"silence_start:\s*([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", log)]
    silences = []
    for i, start in enumerate(starts):
        end = ends[i] if i < len(ends) else duration
        if end - start >= min_silence:
            silences.append((max(0.0, start), min(duration, end)))

    ranges = []
    cursor = 0.0
    for start, end in silences:
        cut_start = min(duration, start + pad)
        cut_end = max(0.0, end - pad)
        if cut_start > cursor:
            ranges.append((cursor, cut_start))
        cursor = max(cursor, cut_end)
    if cursor < duration:
        ranges.append((cursor, duration))
    # Avoid producing a broken empty file when detection finds no useful ranges.
    ranges = [(a, b) for a, b in ranges if b - a >= 0.12]
    return ranges or [(0.0, duration)], duration


def make_srt(video_path: str, output_srt: str, model_size: str = "base") -> str:
    from faster_whisper import WhisperModel

    with tempfile.TemporaryDirectory() as temp_dir:
        wav = str(Path(temp_dir) / "speech.wav")
        run([ffmpeg_path(), "-y", "-i", video_path, "-vn", "-ac", "1",
             "-ar", "16000", "-c:a", "pcm_s16le", wav])
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(wav, vad_filter=True, word_timestamps=False)
        def stamp(seconds):
            ms = int(max(0, seconds) * 1000)
            hh, ms = divmod(ms, 3600000)
            mm, ms = divmod(ms, 60000)
            ss, ms = divmod(ms, 1000)
            return f"{hh:02}:{mm:02}:{ss:02},{ms:03}"
        rows = []
        transcript = []
        for i, seg in enumerate(segments, 1):
            text = seg.text.strip()
            if not text:
                continue
            rows.append(f"{len(rows)+1}\n{stamp(seg.start)} --> {stamp(seg.end)}\n{text}\n")
            transcript.append(text)
        Path(output_srt).write_text("\n".join(rows), encoding="utf-8")
        return " ".join(transcript)


def edit_video(input_path: str, output_path: str, music_path: str | None = None,
               trim_silence: bool = True, normalize_voice: bool = True):
    ranges, original_duration = detect_keep_ranges(input_path) if trim_silence else (
        [(0.0, duration_seconds(input_path))], duration_seconds(input_path))
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        segment_files = []
        for i, (start, end) in enumerate(ranges):
            part = temp / f"part_{i:04}.mp4"
            run([ffmpeg_path(), "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
                 "-i", input_path, "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264",
                 "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
                 "-avoid_negative_ts", "make_zero", str(part)])
            segment_files.append(part)

        concat_list = temp / "concat.txt"
        concat_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in segment_files),
                               encoding="utf-8")
        joined = temp / "joined.mp4"
        run([ffmpeg_path(), "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
             "-c", "copy", str(joined)])

        if music_path:
            # Quiet, non-intrusive music under speech; fade music out near the end.
            joined_duration = duration_seconds(str(joined))
            fade_start = max(0.0, joined_duration - 2.0)
            audio_filter = (
                "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[voice];"
                f"[1:a]volume=0.075,afade=t=in:st=0:d=1.5,afade=t=out:st={fade_start:.3f}:d=2[music];"
                "[voice][music]amix=inputs=2:duration=first:dropout_transition=2[outa]"
            )
            run([ffmpeg_path(), "-y", "-i", str(joined), "-stream_loop", "-1",
                 "-i", music_path, "-filter_complex", audio_filter, "-map", "0:v:0",
                 "-map", "[outa]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                 "-shortest", "-movflags", "+faststart", output_path])
        else:
            af = "loudnorm=I=-16:TP=-1.5:LRA=11" if normalize_voice else "anull"
            run([ffmpeg_path(), "-y", "-i", str(joined), "-map", "0:v:0", "-map", "0:a?",
                 "-c:v", "copy", "-af", af, "-c:a", "aac", "-b:a", "192k",
                 "-movflags", "+faststart", output_path])
    edited_duration = duration_seconds(output_path)
    return {
        "original_seconds": round(original_duration, 2),
        "edited_seconds": round(edited_duration, 2),
        "seconds_removed": round(max(0, original_duration - edited_duration), 2),
        "segments_kept": len(ranges),
    }
