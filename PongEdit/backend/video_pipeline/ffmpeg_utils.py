from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Protocol

FFMPEG_TIMEOUT_SEC = 45


class SegmentLike(Protocol):
    start_sec: float
    end_sec: float


def ensure_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg is not installed or is not on PATH.")
    if shutil.which("ffprobe") is None:
        raise RuntimeError("FFprobe is not installed or is not on PATH.")


def get_video_duration_sec(input_path: Path) -> float:
    ensure_ffmpeg()
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(input_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def create_analysis_proxy(
    input_path: Path,
    output_path: Path,
    *,
    fps: float,
    width: int,
) -> Path:
    ensure_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vf",
            f"fps={fps},scale={width}:-2",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "32",
            str(output_path),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=FFMPEG_TIMEOUT_SEC,
    )
    return output_path


def cut_segments(
    input_path: Path,
    output_path: Path,
    segments: list[SegmentLike],
    *,
    total_duration_sec: float,
    padding_sec: float,
) -> None:
    ensure_ffmpeg()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="pongedit-cuts-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        clip_paths = _write_clips(
            input_path,
            tmpdir_path,
            segments,
            total_duration_sec=total_duration_sec,
            padding_sec=padding_sec,
        )
        if not clip_paths:
            return

        manifest_path = tmpdir_path / "concat.txt"
        manifest_path.write_text(
            "".join(f"file '{clip_path.as_posix()}'\n" for clip_path in clip_paths),
            encoding="utf-8",
        )

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(manifest_path),
                "-c",
                "copy",
                str(output_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=FFMPEG_TIMEOUT_SEC,
        )


def _write_clips(
    input_path: Path,
    tmpdir_path: Path,
    segments: list[SegmentLike],
    *,
    total_duration_sec: float,
    padding_sec: float,
) -> list[Path]:
    clip_paths: list[Path] = []
    for index, segment in enumerate(segments):
        start = max(0.0, segment.start_sec - padding_sec)
        end = min(total_duration_sec, segment.end_sec + padding_sec)
        duration = end - start
        if duration <= 0:
            continue

        clip_path = tmpdir_path / f"clip_{index:04d}.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{start:.3f}",
                "-i",
                str(input_path),
                "-t",
                f"{duration:.3f}",
                "-c",
                "copy",
                "-avoid_negative_ts",
                "make_zero",
                "-movflags",
                "+faststart",
                str(clip_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=FFMPEG_TIMEOUT_SEC,
        )
        clip_paths.append(clip_path)
    return clip_paths
