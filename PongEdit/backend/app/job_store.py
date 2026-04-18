from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Any

from backend.app.models import JobRecord, JobStatus


class JobStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _path(self, job_id: str) -> Path:
        return self.root / f"{job_id}.json"

    def create(self, job_id: str, input_path: Path, output_dir: Path) -> JobRecord:
        record = JobRecord(
            job_id=job_id,
            status=JobStatus.pending,
            input_path=str(input_path),
            output_dir=str(output_dir),
        )
        self.save(record)
        return record

    def save(self, record: JobRecord) -> None:
        with self._lock:
            self._path(record.job_id).write_text(
                record.model_dump_json(indent=2),
                encoding="utf-8",
            )

    def get(self, job_id: str) -> JobRecord | None:
        path = self._path(job_id)
        if not path.exists():
            return None
        return JobRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def update(
        self,
        job_id: str,
        *,
        status: JobStatus | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
        stage: str | None = None,
        progress: int | None = None,
    ) -> JobRecord:
        record = self.get(job_id)
        if record is None:
            raise KeyError(f"Job not found: {job_id}")
        if status is not None:
            record.status = status
        if error is not None:
            record.error = error
        if metadata is not None:
            record.metadata = metadata
        if stage is not None:
            record.stage = stage
        if progress is not None:
            record.progress = progress
        self.save(record)
        return record
