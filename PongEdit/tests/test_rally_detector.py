from __future__ import annotations

import pytest

from backend.video_pipeline.rally_detector import (
    RallySegment,
    filter_low_motion_segments,
    filter_short_segments,
    group_active_frames,
    merge_close_segments,
    rolling_average,
    tag_highlights,
)


def test_rolling_average_keeps_length() -> None:
    values = [0.0, 3.0, 6.0, 9.0]

    result = rolling_average(values, window=3)

    assert len(result) == len(values)
    assert result[1] == pytest.approx(3.0)


def test_group_active_frames_creates_segments() -> None:
    active = [False, True, True, False, True]
    motion_scores = [0.0, 8.0, 10.0, 0.0, 7.0]

    segments = group_active_frames(active, motion_scores, fps=2.0)

    assert len(segments) == 2
    assert segments[0].start_sec == pytest.approx(0.5)
    assert segments[0].end_sec == pytest.approx(1.5)
    assert segments[0].motion_score_avg == pytest.approx(9.0)


def test_merge_close_segments_combines_short_gaps() -> None:
    segments = [
        RallySegment(0.0, 2.0, 2.0, 4.0),
        RallySegment(2.5, 4.0, 1.5, 8.0),
        RallySegment(6.0, 8.0, 2.0, 5.0),
    ]

    merged = merge_close_segments(segments, merge_gap_sec=1.0)

    assert len(merged) == 2
    assert merged[0].start_sec == pytest.approx(0.0)
    assert merged[0].end_sec == pytest.approx(4.0)
    assert merged[0].duration_sec == pytest.approx(4.0)


def test_filter_short_segments_removes_false_positives() -> None:
    segments = [
        RallySegment(0.0, 1.0, 1.0, 10.0),
        RallySegment(3.0, 5.0, 2.0, 7.0),
    ]

    filtered = filter_short_segments(segments, min_rally_sec=1.5)

    assert filtered == [segments[1]]


def test_filter_low_motion_segments_removes_weak_candidates() -> None:
    segments = [
        RallySegment(0.0, 2.0, 2.0, 7.5),
        RallySegment(3.0, 5.0, 2.0, 10.0),
    ]

    filtered = filter_low_motion_segments(segments, min_motion_score=9.0)

    assert filtered == [segments[1]]


def test_tag_highlights_uses_duration_and_motion() -> None:
    segments = [
        RallySegment(0.0, 2.0, 2.0, 2.0),
        RallySegment(3.0, 9.0, 6.0, 8.0),
        RallySegment(10.0, 13.0, 3.0, 4.0),
        RallySegment(14.0, 15.0, 1.0, 30.0),
        RallySegment(16.0, 18.0, 2.0, 6.0),
    ]

    tagged = tag_highlights(segments, top_percent=0.2)

    assert sum(segment.is_highlight for segment in tagged) == 1
    assert tagged[1].is_highlight is True
