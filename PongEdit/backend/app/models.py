from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    complete = "complete"
    failed = "failed"


class JobRecord(BaseModel):
    job_id: str
    status: JobStatus
    input_path: str
    output_dir: str
    error: str | None = None
    metadata: dict[str, Any] | None = None
    stage: str | None = None
    progress: int = 0

    @property
    def output_path(self) -> Path:
        return Path(self.output_dir)
