from __future__ import annotations

import logging
import shutil
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
from threading import Thread
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.app.job_store import JobStore
from backend.app.models import JobStatus
from backend.video_pipeline.rally_detector import process_video

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
UPLOADS_DIR = ROOT / "uploads"
OUTPUTS_DIR = ROOT / "outputs"
JOBS_DIR = ROOT / "jobs"

for directory in (UPLOADS_DIR, OUTPUTS_DIR, JOBS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

store = JobStore(JOBS_DIR)
app = FastAPI(title="PongEdit API")
ALLOWED_VIDEO_SUFFIXES = {".mp4", ".mov"}
PROCESSING_TIMEOUT_SEC = 90
SENSITIVITY_CONFIG = {
    "strict": {"threshold": 14.0, "min_motion_score": 18.0},
    "balanced": {"threshold": 12.0, "min_motion_score": 16.0},
    "loose": {"threshold": 8.0, "min_motion_score": 9.0},
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/upload")
async def upload_video(
    file: UploadFile = File(...),
    sensitivity: str = Form("balanced"),
) -> dict[str, str]:
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_VIDEO_SUFFIXES:
        raise HTTPException(status_code=400, detail="Upload a single .mp4 or .mov file.")
    if sensitivity not in SENSITIVITY_CONFIG:
        raise HTTPException(status_code=400, detail="Choose strict, balanced, or loose sensitivity.")

    job_id = uuid4().hex
    upload_dir = UPLOADS_DIR / job_id
    output_dir = OUTPUTS_DIR / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_path = upload_dir / f"input{suffix}"
    with input_path.open("wb") as destination:
        shutil.copyfileobj(file.file, destination)

    store.create(job_id, input_path, output_dir)
    Thread(target=_run_job, args=(job_id, input_path, output_dir, sensitivity), daemon=True).start()
    return {"job_id": job_id, "status": JobStatus.pending.value}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    record = _require_job(job_id)
    payload = record.model_dump()
    payload.pop("input_path", None)
    payload.pop("output_dir", None)
    if record.status == JobStatus.complete:
        payload["downloads"] = _download_urls(job_id, record.metadata or {})
    return payload


@app.get("/api/jobs/{job_id}/metadata")
def get_metadata(job_id: str) -> dict:
    record = _require_job(job_id)
    metadata_path = record.output_path / "metadata.json"
    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="Metadata is not ready yet.")
    return FileResponse(metadata_path, media_type="application/json", filename="metadata.json")


@app.get("/api/jobs/{job_id}/download/full")
def download_full(job_id: str) -> FileResponse:
    return _download_file(job_id, "full_rallies.mp4")


@app.get("/api/jobs/{job_id}/download/highlights")
def download_highlights(job_id: str) -> FileResponse:
    return _download_file(job_id, "highlights.mp4")


def _run_job(job_id: str, input_path: Path, output_dir: Path, sensitivity: str) -> None:
    try:
        store.update(job_id, status=JobStatus.processing, stage="Scanning video", progress=20)
        logger.info("Processing job %s", job_id)
        config = SENSITIVITY_CONFIG[sensitivity]
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                process_video,
                str(input_path),
                str(output_dir),
                threshold=config["threshold"],
                min_motion_score=config["min_motion_score"],
            )
            try:
                metadata = future.result(timeout=PROCESSING_TIMEOUT_SEC)
            except TimeoutError as exc:
                future.cancel()
                raise TimeoutError(
                    f"Processing took longer than {PROCESSING_TIMEOUT_SEC} seconds. "
                    "Try a shorter clip or export a smaller video."
                ) from exc
        store.update(
            job_id,
            status=JobStatus.complete,
            metadata=metadata,
            stage="Complete",
            progress=100,
        )
        logger.info("Completed job %s", job_id)
    except Exception as exc:
        logger.exception("Failed job %s", job_id)
        store.update(job_id, status=JobStatus.failed, error=str(exc), stage="Failed", progress=100)


def _require_job(job_id: str):
    record = store.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return record


def _download_file(job_id: str, filename: str) -> FileResponse:
    record = _require_job(job_id)
    path = record.output_path / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{filename} is not ready.")
    return FileResponse(path, media_type="video/mp4", filename=filename)


def _download_urls(job_id: str, metadata: dict) -> dict[str, str | None]:
    outputs = metadata.get("outputs", {})
    return {
        "highlights": (
            f"/api/jobs/{job_id}/download/highlights"
            if outputs.get("highlights")
            else None
        ),
    }
