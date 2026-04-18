import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type JobStatus = "pending" | "processing" | "complete" | "failed";
type Sensitivity = "strict" | "balanced" | "loose";

type Rally = {
  start: number;
  end: number;
  duration: number;
  is_highlight: boolean;
  motion_score: number;
};

type Metadata = {
  total_duration_sec: number;
  rally_count: number;
  highlight_count: number;
  rallies: Rally[];
  outputs: {
    full_rallies: string | null;
    highlights: string | null;
  };
};

type Job = {
  job_id: string;
  status: JobStatus;
  error?: string | null;
  metadata?: Metadata | null;
  stage?: string | null;
  progress?: number;
  downloads?: {
    highlights: string | null;
  };
};

const API_BASE = "";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [message, setMessage] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [sensitivity, setSensitivity] = useState<Sensitivity>("balanced");
  const [previewTime, setPreviewTime] = useState(0);
  const [previewDuration, setPreviewDuration] = useState(0);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const isBusy = isUploading || job?.status === "pending" || job?.status === "processing";
  const statusText = getStatusText(job, isUploading);
  const highlightUrl = job?.downloads?.highlights ?? null;

  useEffect(() => {
    if (!job || job.status === "complete" || job.status === "failed") {
      return;
    }

    const timer = window.setInterval(async () => {
      const response = await fetch(`${API_BASE}/api/jobs/${job.job_id}`);
      if (response.ok) {
        setJob(await response.json());
      }
    }, 1500);

    return () => window.clearInterval(timer);
  }, [job]);

  async function upload() {
    if (!file) {
      setMessage("Choose one .mp4 or .mov table-tennis match first.");
      return;
    }

    setIsUploading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("sensitivity", sensitivity);

    try {
      const response = await fetch(`${API_BASE}/api/upload`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || "Upload failed.");
      }

      const uploadResult = await response.json();
      setJob({
        job_id: uploadResult.job_id,
        status: uploadResult.status
      });
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  function setSelectedFile(nextFile: File | null) {
    if (!nextFile) {
      return;
    }
    if (!isSupportedVideo(nextFile)) {
      setMessage("Choose one .mp4 or .mov file.");
      return;
    }
    setMessage("");
    setFile(nextFile);
    setJob(null);
  }

  function onDrop(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
    if (isBusy) {
      return;
    }
    const nextFile = event.dataTransfer.files.item(0);
    setSelectedFile(nextFile);
  }

  return (
    <main className="app">
      <section className="shell">
        <header className="topbar">
          <div>
            <p className="eyebrow">PongEdit</p>
            <h1>Rally detection workbench</h1>
          </div>
          <StatusBadge status={job?.status ?? "pending"} active={Boolean(job)} />
        </header>

        <section className="grid">
          <div className="panel upload-panel">
            <h2>Upload match video</h2>
            <p>
              Upload one static-camera .mp4 or .mov. PongEdit looks for sustained table-tennis
              motion and exports the strongest highlight when a valid rally is found.
            </p>

            <div
              className={`dropzone ${isDragging ? "is-dragging" : ""} ${isBusy ? "is-disabled" : ""}`}
              onDragEnter={(event) => {
                event.preventDefault();
                event.stopPropagation();
                if (isBusy) {
                  return;
                }
                setIsDragging(true);
              }}
              onDragOver={(event) => {
                event.preventDefault();
                event.stopPropagation();
                if (isBusy) {
                  return;
                }
                event.dataTransfer.dropEffect = "copy";
                setIsDragging(true);
              }}
              onDragLeave={(event) => {
                event.preventDefault();
                event.stopPropagation();
                if (event.currentTarget === event.target) {
                  setIsDragging(false);
                }
              }}
              onDrop={onDrop}
              onClick={() => {
                if (!isBusy) {
                  inputRef.current?.click();
                }
              }}
              role="button"
              tabIndex={0}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  if (!isBusy) {
                    inputRef.current?.click();
                  }
                }
              }}
            >
              <input
                ref={inputRef}
                type="file"
                accept=".mp4,.mov,video/mp4,video/quicktime"
                disabled={isBusy}
                onChange={(event) => setSelectedFile(event.target.files?.item(0) ?? null)}
              />
              <span>{file ? file.name : "Drop an .mp4 or .mov here"}</span>
              <small>or click to choose a file</small>
            </div>

            {file ? <FileSummary file={file} /> : null}

            <label className="field-label">
              Detection sensitivity
              <select
                value={sensitivity}
                disabled={isBusy}
                onChange={(event) => setSensitivity(event.target.value as Sensitivity)}
              >
                <option value="balanced">Balanced</option>
                <option value="loose">Loose</option>
                <option value="strict">Strict</option>
              </select>
            </label>
            <p className="helper-copy">
              Use Loose if a real rally produces no export. Use Strict if non-rally motion is being exported.
            </p>

            <button className="primary" onClick={upload} disabled={isBusy}>
              {getProcessButtonLabel(job, isUploading)}
            </button>
            {message ? <p className="error">{message}</p> : null}
          </div>

          <div className="panel">
            <h2>Processing status</h2>
            <p className="status-copy">{statusText}</p>
            <dl className="status-list">
              <div>
                <dt>Job</dt>
                <dd>{job?.job_id ?? "No job yet"}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>{job?.status ?? "Waiting for upload"}</dd>
              </div>
              <div>
                <dt>Stage</dt>
                <dd>{job?.stage ?? (isUploading ? "Uploading" : "Idle")}</dd>
              </div>
              {job?.error ? (
                <div>
                  <dt>Error</dt>
                  <dd>{job.error}</dd>
                </div>
              ) : null}
            </dl>
          </div>
        </section>

        <Stats metadata={job?.metadata ?? null} />

        <section className="panel">
          <div className="section-heading">
            <h2>Downloads</h2>
            <span>{getDownloadHint(job)}</span>
          </div>
          {highlightUrl ? (
            <div className="download-row">
              <DownloadButton href={highlightUrl} label="Download highlights.mp4" />
            </div>
          ) : null}
          {job?.status === "complete" && !job.downloads?.highlights ? (
            <p className="empty">Scan finished, but export was skipped because no rally was detected. If this is a real rally clip, try Loose sensitivity and process it again.</p>
          ) : null}
        </section>

        <section className="panel">
          <div className="section-heading">
            <h2>Edited video preview</h2>
            <span>{highlightUrl ? "Ready" : "Waiting for highlight"}</span>
          </div>
          {highlightUrl ? (
            <div className="video-preview">
              <video
                ref={videoRef}
                src={highlightUrl}
                controls
                playsInline
                preload="metadata"
                onLoadedMetadata={(event) => {
                  setPreviewDuration(event.currentTarget.duration || 0);
                  setPreviewTime(event.currentTarget.currentTime || 0);
                }}
                onTimeUpdate={(event) => setPreviewTime(event.currentTarget.currentTime)}
              />
              <div className="scrubber-row">
                <span>{formatTime(previewTime)}</span>
                <input
                  aria-label="Preview timeline"
                  type="range"
                  min="0"
                  max={previewDuration || 0}
                  step="0.01"
                  value={Math.min(previewTime, previewDuration || 0)}
                  onChange={(event) => {
                    const nextTime = Number(event.target.value);
                    setPreviewTime(nextTime);
                    if (videoRef.current) {
                      videoRef.current.currentTime = nextTime;
                    }
                  }}
                />
                <span>{formatTime(previewDuration)}</span>
              </div>
            </div>
          ) : (
            <p className="empty">The edited highlight will play here after processing.</p>
          )}
        </section>

        <section className="panel">
          <div className="section-heading">
            <h2>Detected rallies</h2>
            <span>{job?.metadata?.rally_count ?? 0} segments</span>
          </div>
          <RallyTable rallies={job?.metadata?.rallies ?? []} />
        </section>

      </section>
    </main>
  );
}

function StatusBadge({ status, active }: { status: JobStatus; active: boolean }) {
  return <div className={`badge ${active ? status : ""}`}>{active ? status : "ready"}</div>;
}

function FileSummary({ file }: { file: File }) {
  return (
    <div className="file-summary">
      <span>{file.name}</span>
      <strong>{formatBytes(file.size)}</strong>
    </div>
  );
}

function Stats({ metadata }: { metadata: Metadata | null }) {
  const stats = [
    ["Duration", metadata ? `${metadata.total_duration_sec.toFixed(1)}s` : "-"],
    ["Rallies", metadata?.rally_count ?? "-"],
    ["Highlights", metadata?.highlight_count ?? "-"]
  ];

  return (
    <section className="stats">
      {stats.map(([label, value]) => (
        <div className="stat-card" key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </section>
  );
}

function DownloadButton({ href, label }: { href: string | null; label: string }) {
  if (!href) {
    return null;
  }
  const filename = label.replace("Download ", "");
  return (
    <a className="secondary" href={href} download={filename}>
      {label}
    </a>
  );
}

function RallyTable({ rallies }: { rallies: Rally[] }) {
  if (rallies.length === 0) {
    return <p className="empty">Detected rally rows will appear here after processing.</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Start</th>
            <th>End</th>
            <th>Duration</th>
            <th>Motion</th>
            <th>Highlight</th>
          </tr>
        </thead>
        <tbody>
          {rallies.map((rally, index) => (
            <tr key={`${rally.start}-${rally.end}`}>
              <td>{index + 1}</td>
              <td>{rally.start.toFixed(2)}s</td>
              <td>{rally.end.toFixed(2)}s</td>
              <td>{rally.duration.toFixed(2)}s</td>
              <td>{rally.motion_score.toFixed(2)}</td>
              <td>
                <span className={rally.is_highlight ? "pill" : "muted-pill"}>
                  {rally.is_highlight ? "Highlight" : "Rally"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function getStatusText(job: Job | null, uploading: boolean) {
  if (uploading) {
    return "Uploading the video to the local processor.";
  }
  if (!job) {
    return "Ready for one .mp4 or .mov match video.";
  }
  if (job.status === "pending") {
    return "Queued locally and waiting for processing.";
  }
  if (job.status === "processing") {
    return "Scanning motion, grouping rallies, and exporting the highlight.";
  }
  if (job.status === "failed") {
    return "Processing failed. Check the error below.";
  }
  if (job.metadata?.highlight_count) {
    return "Highlight export is ready.";
  }
  return "Scan finished. Export was skipped because no valid rally was found.";
}

function getDownloadHint(job: Job | null) {
  if (!job) {
    return "Available after processing";
  }
  if (job.status === "processing" || job.status === "pending") {
    return "Working";
  }
  if (job.status === "failed") {
    return "Unavailable";
  }
  return job.downloads?.highlights ? "Ready" : "No highlight";
}

function getProcessButtonLabel(job: Job | null, uploading: boolean) {
  if (uploading) {
    return "Uploading...";
  }
  if (job?.status === "pending" || job?.status === "processing") {
    return "Processing...";
  }
  return "Process video";
}

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds)) {
    return "0:00";
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
}

function isSupportedVideo(file: File) {
  const filename = file.name.toLowerCase();
  return filename.endsWith(".mp4") || filename.endsWith(".mov");
}

createRoot(document.getElementById("root")!).render(<App />);
