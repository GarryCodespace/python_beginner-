from __future__ import annotations

import logging
import math
import json
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from backend.video_pipeline.ffmpeg_utils import (
    create_analysis_proxy,
    cut_segments,
    get_video_duration_sec,
)

logger = logging.getLogger(__name__)


@dataclass
class RallySegment:
    start_sec: float
    end_sec: float
    duration_sec: float
    motion_score_avg: float
    is_highlight: bool = False

    def to_metadata(self) -> dict[str, float | bool]:
        return {
            "start": round(self.start_sec, 3),
            "end": round(self.end_sec, 3),
            "duration": round(self.duration_sec, 3),
            "is_highlight": self.is_highlight,
            "motion_score": round(self.motion_score_avg, 3),
        }


def rolling_average(values: list[float], window: int) -> list[float]:
    if window <= 1 or not values:
        return values[:]
    kernel = np.ones(window, dtype=np.float32) / float(window)
    return np.convolve(np.array(values, dtype=np.float32), kernel, mode="same").tolist()


def group_active_frames(
    active: list[bool],
    motion_scores: list[float],
    fps: float,
) -> list[RallySegment]:
    segments: list[RallySegment] = []
    start_idx: int | None = None

    for index, is_active in enumerate(active):
        if is_active and start_idx is None:
            start_idx = index
        elif not is_active and start_idx is not None:
            segments.append(_segment_from_frames(start_idx, index - 1, motion_scores, fps))
            start_idx = None

    if start_idx is not None:
        segments.append(_segment_from_frames(start_idx, len(active) - 1, motion_scores, fps))

    return segments


def merge_close_segments(
    segments: list[RallySegment],
    merge_gap_sec: float,
) -> list[RallySegment]:
    if not segments:
        return []

    merged = [segments[0]]
    for current in segments[1:]:
        previous = merged[-1]
        gap = current.start_sec - previous.end_sec
        if gap < merge_gap_sec:
            total_duration = current.end_sec - previous.start_sec
            weighted_motion = (
                previous.motion_score_avg * previous.duration_sec
                + current.motion_score_avg * current.duration_sec
            ) / max(previous.duration_sec + current.duration_sec, 1e-9)
            merged[-1] = RallySegment(
                start_sec=previous.start_sec,
                end_sec=current.end_sec,
                duration_sec=total_duration,
                motion_score_avg=weighted_motion,
            )
        else:
            merged.append(current)
    return merged


def filter_short_segments(
    segments: list[RallySegment],
    min_rally_sec: float,
) -> list[RallySegment]:
    return [segment for segment in segments if segment.duration_sec >= min_rally_sec]


def filter_low_motion_segments(
    segments: list[RallySegment],
    min_motion_score: float,
) -> list[RallySegment]:
    return [
        segment
        for segment in segments
        if segment.motion_score_avg >= min_motion_score
    ]


def tag_highlights(
    segments: list[RallySegment],
    top_percent: float = 0.2,
) -> list[RallySegment]:
    if not segments:
        return []

    count = max(1, math.ceil(len(segments) * top_percent))
    scored = sorted(
        enumerate(segments),
        key=lambda item: item[1].duration_sec * item[1].motion_score_avg,
        reverse=True,
    )
    highlight_indices = {index for index, _ in scored[:count]}

    return [
        RallySegment(
            start_sec=segment.start_sec,
            end_sec=segment.end_sec,
            duration_sec=segment.duration_sec,
            motion_score_avg=segment.motion_score_avg,
            is_highlight=index in highlight_indices,
        )
        for index, segment in enumerate(segments)
    ]


def detect_rallies(
    input_path: str | Path,
    threshold: float = 12.0,
    smoothing_window: int = 15,
    merge_gap_sec: float = 1.0,
    min_rally_sec: float = 1.5,
    min_motion_score: float = 16.0,
    highlight_top_percent: float = 0.2,
    analysis_fps: float = 10.0,
    analysis_width: int = 320,
) -> tuple[list[RallySegment], float]:
    input_path = Path(input_path)
    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        raise ValueError(f"Could not open video: {input_path}")

    source_fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / source_fps if frame_count else get_video_duration_sec(input_path)

    logger.info(
        "Reading frames from %s at %.2f source FPS, %.2f analysis FPS",
        input_path,
        source_fps,
        analysis_fps,
    )
    motion_scores, effective_fps = _read_motion_scores(
        capture,
        source_fps=source_fps,
        analysis_fps=analysis_fps,
        analysis_width=analysis_width,
    )
    capture.release()

    if not motion_scores:
        return [], duration

    smoothed = rolling_average(motion_scores, smoothing_window)
    active = [score >= threshold for score in smoothed]

    segments = group_active_frames(active, smoothed, effective_fps)
    segments = merge_close_segments(segments, merge_gap_sec)
    segments = filter_short_segments(segments, min_rally_sec)
    segments = filter_low_motion_segments(segments, min_motion_score)
    segments = tag_highlights(segments, highlight_top_percent)
    return segments, duration


def process_video(
    input_path: str,
    output_dir: str,
    threshold: float = 12.0,
    smoothing_window: int = 15,
    merge_gap_sec: float = 1.0,
    min_rally_sec: float = 1.5,
    min_motion_score: float = 16.0,
    padding_sec: float = 2.0,
    highlight_top_percent: float = 0.2,
    analysis_fps: float = 10.0,
    analysis_width: int = 320,
    fallback_short_clip_sec: float = 20.0,
) -> dict:
    input_path_obj = Path(input_path)
    output_dir_obj = Path(output_dir)
    output_dir_obj.mkdir(parents=True, exist_ok=True)

    highlights_output = output_dir_obj / "highlights.mp4"
    analysis_proxy = output_dir_obj / "analysis_proxy.mp4"
    highlights_output.unlink(missing_ok=True)
    analysis_proxy.unlink(missing_ok=True)

    proxy_path = create_analysis_proxy(
        input_path_obj,
        analysis_proxy,
        fps=analysis_fps,
        width=analysis_width,
    )

    rallies, duration = detect_rallies(
        proxy_path,
        threshold=threshold,
        smoothing_window=smoothing_window,
        merge_gap_sec=merge_gap_sec,
        min_rally_sec=min_rally_sec,
        min_motion_score=min_motion_score,
        highlight_top_percent=highlight_top_percent,
        analysis_fps=analysis_fps,
        analysis_width=analysis_width,
    )
    duration = get_video_duration_sec(input_path_obj)
    used_short_clip_fallback = False

    if not rallies and 0 < duration <= fallback_short_clip_sec:
        rallies = [
            RallySegment(
                start_sec=0.0,
                end_sec=duration,
                duration_sec=duration,
                motion_score_avg=0.0,
                is_highlight=True,
            )
        ]
        used_short_clip_fallback = True

    if rallies:
        highlight_segments = [segment for segment in rallies if segment.is_highlight]
        if highlight_segments:
            cut_segments(
                input_path_obj,
                highlights_output,
                highlight_segments,
                total_duration_sec=duration,
                padding_sec=padding_sec,
            )

    metadata = {
        "total_duration_sec": round(duration, 3),
        "rally_count": len(rallies),
        "highlight_count": sum(1 for rally in rallies if rally.is_highlight),
        "rallies": [rally.to_metadata() for rally in rallies],
        "outputs": {
            "highlights": highlights_output.name if highlights_output.exists() else None,
        },
        "fallback_used": used_short_clip_fallback,
    }

    (output_dir_obj / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    return metadata


def _read_motion_scores(
    capture: cv2.VideoCapture,
    *,
    source_fps: float,
    analysis_fps: float,
    analysis_width: int,
) -> tuple[list[float], float]:
    frame_step = max(1, round(source_fps / analysis_fps))
    effective_fps = source_fps / frame_step
    success, previous = capture.read()
    if not success:
        raise ValueError("Video has no readable frames.")

    previous_gray = _prepare_frame(previous, analysis_width)
    scores = [0.0]
    frame_index = 0

    while True:
        success, frame = capture.read()
        if not success:
            break
        frame_index += 1
        if frame_index % frame_step != 0:
            continue
        gray = _prepare_frame(frame, analysis_width)
        diff = cv2.absdiff(gray, previous_gray)
        scores.append(float(np.mean(diff)))
        previous_gray = gray

    return scores, effective_fps


def _prepare_frame(frame: np.ndarray, analysis_width: int) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape[:2]
    if width <= analysis_width:
        return gray
    scale = analysis_width / width
    analysis_height = max(1, round(height * scale))
    return cv2.resize(gray, (analysis_width, analysis_height), interpolation=cv2.INTER_AREA)


def _segment_from_frames(
    start_idx: int,
    end_idx: int,
    motion_scores: list[float],
    fps: float,
) -> RallySegment:
    start_sec = start_idx / fps
    end_sec = (end_idx + 1) / fps
    duration_sec = end_sec - start_sec
    score_slice = motion_scores[start_idx : end_idx + 1]
    motion_score_avg = float(np.mean(score_slice)) if score_slice else 0.0
    return RallySegment(
        start_sec=start_sec,
        end_sec=end_sec,
        duration_sec=duration_sec,
        motion_score_avg=motion_score_avg,
    )
