from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPLOADS = ROOT / "uploads"
REPORT_DIR = ROOT / "outputs" / "_retest"
sys.path.insert(0, str(ROOT))

from backend.video_pipeline.rally_detector import process_video


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    seen: dict[str, Path] = {}
    results = []

    for input_path in sorted(UPLOADS.glob("*/input.*")):
        digest = sha256(input_path)
        if digest in seen:
            continue
        seen[digest] = input_path
        output_dir = REPORT_DIR / input_path.parent.name
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True)

        metadata = process_video(str(input_path), str(output_dir))
        highlight_path = output_dir / "highlights.mp4"
        highlight_duration = ffprobe_duration(highlight_path) if highlight_path.exists() else None
        results.append(
            {
                "job_id": input_path.parent.name,
                "input": str(input_path.relative_to(ROOT)),
                "duration_sec": metadata["total_duration_sec"],
                "rally_count": metadata["rally_count"],
                "highlight_count": metadata["highlight_count"],
                "highlight_duration_sec": highlight_duration,
                "rallies": metadata["rallies"],
                "outputs": metadata["outputs"],
            }
        )

    report_path = REPORT_DIR / "report.json"
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    for result in results:
        print(
            f"{result['job_id']} input={result['duration_sec']:.2f}s "
            f"rallies={result['rally_count']} highlights={result['highlight_count']} "
            f"highlight_duration={result['highlight_duration_sec']}"
        )
        for rally in result["rallies"]:
            print(
                f"  {rally['start']:.2f}-{rally['end']:.2f}s "
                f"duration={rally['duration']:.2f}s motion={rally['motion_score']:.2f} "
                f"highlight={rally['is_highlight']}"
            )
    print(f"Report: {report_path}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ffprobe_duration(path: Path) -> float:
    import subprocess

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return round(float(result.stdout.strip()), 3)


if __name__ == "__main__":
    main()
