# PongEdit

PongEdit is a full-stack MVP for automatic table-tennis rally detection and video cutting. It uses a baseline heuristic pipeline: frame differencing with OpenCV, rally segmentation, highlight scoring, and FFmpeg cutting.

This is not a trained AI model. It works best with a static camera and a full-table view.

## Project Structure

```text
backend/
  app/
    main.py              FastAPI upload/job/download API
    job_store.py         Local JSON job state
  video_pipeline/
    rally_detector.py    OpenCV frame differencing and segmentation
    ffmpeg_utils.py      FFprobe duration and FFmpeg cutting helpers
frontend/
  src/
    main.tsx             React workbench UI
    styles.css           Dashboard styling
tests/
  test_rally_detector.py Unit tests for segmentation helpers
```

## Requirements

- Python 3.11+
- Node.js 20+
- FFmpeg and FFprobe on your `PATH`

Install FFmpeg on macOS:

```bash
brew install ffmpeg
```

## Backend Setup

```bash
cd /Users/garryyuan/python/PongEdit
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python3 -m backend.run
```

The API runs at `http://127.0.0.1:8000`.

## Frontend Setup

```bash
cd /Users/garryyuan/python/PongEdit/frontend
npm install
npm run dev
```

The dashboard runs at `http://127.0.0.1:5173`.

## How The Pipeline Works

1. OpenCV reads the uploaded `.mp4` or `.mov`.
2. Consecutive frames are converted to grayscale.
3. Each frame gets a motion score from mean absolute difference against the previous frame.
4. Motion scores are smoothed with a rolling average.
5. Frames above the threshold are marked active.
6. Consecutive active frames become rally segments.
7. Segments with gaps under 1 second are merged.
8. Segments shorter than 1.5 seconds are discarded.
9. Low-confidence segments with weak average motion are discarded.
10. The top 20% by duration and motion score are tagged as highlights.
11. FFmpeg adds 1 second of padding before/after each segment, then writes:
   - `highlights.mp4`
   - `metadata.json`

## API

- `POST /api/upload` accepts one `.mp4` or `.mov` file and returns a job id.
- `GET /api/jobs/{job_id}` returns `pending`, `processing`, `complete`, or `failed`.
- `GET /api/jobs/{job_id}/download/full` downloads `full_rallies.mp4`.
- `GET /api/jobs/{job_id}/download/highlights` downloads `highlights.mp4`.
- `GET /api/jobs/{job_id}/metadata` downloads `metadata.json`.

## Python Pipeline API

```python
from backend.video_pipeline.rally_detector import process_video

metadata = process_video(
    input_path="uploads/example/input.mp4",
    output_dir="outputs/example",
    threshold=12.0,
    smoothing_window=15,
    merge_gap_sec=1.0,
    min_rally_sec=1.5,
    min_motion_score=16.0,
    padding_sec=2.0,
    highlight_top_percent=0.2,
)
```

## Known Limitations

- Works best with a static camera.
- Works best when the full table is visible.
- May detect player movement between points as activity.
- Threshold may need adjustment depending on lighting, camera angle, and resolution.
- FFmpeg re-encodes clips for more accurate cut points.
- This is a baseline heuristic pipeline, not a trained AI model.
