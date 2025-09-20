import { ChangeEvent, FormEvent, useMemo, useState } from "react";
import api from "../api";
import { ArtifactUploadResponse, SubmissionArtifact } from "../types";

interface Props {
  sessionId: string | null;
  disabled?: boolean;
  artifacts: SubmissionArtifact[];
  onArtifactAdded: (artifact: SubmissionArtifact) => void;
}

const DOWNLOADABLE_EXTENSIONS = [
  ".xlsx",
  ".xls",
  ".xlsm",
  ".xlsb",
  ".csv",
  ".tsv",
  ".ods"
];

function formatBytes(size?: number | null) {
  if (!size || size <= 0) {
    return "";
  }
  const units = ["B", "KB", "MB", "GB"];
  let value = size;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }
  return `${value.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

export default function SubmissionPanel({
  sessionId,
  disabled,
  artifacts,
  onArtifactAdded
}: Props) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileDescription, setFileDescription] = useState("");
  const [fileKey, setFileKey] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [linkUrl, setLinkUrl] = useState("");
  const [linkDescription, setLinkDescription] = useState("");
  const [submittingLink, setSubmittingLink] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submissionDisabled = useMemo(() => disabled || !sessionId, [disabled, sessionId]);

  const baseDownloadUrl = useMemo(() => {
    if (!sessionId) {
      return null;
    }
    const base = api.defaults.baseURL ?? "";
    return `${base.replace(/\/$/, "")}/session/${sessionId}/artifacts`;
  }, [sessionId]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setError(null);
  };

  const handleFileUpload = async (event: FormEvent) => {
    event.preventDefault();
    if (!sessionId || !selectedFile) {
      return;
    }
    try {
      setUploading(true);
      setError(null);
      const formData = new FormData();
      formData.append("file", selectedFile);
      if (fileDescription.trim()) {
        formData.append("description", fileDescription.trim());
      }
      const response = await api.post<ArtifactUploadResponse>(
        `/session/${sessionId}/artifacts/upload`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" }
        }
      );
      onArtifactAdded(response.data.artifact);
      setSelectedFile(null);
      setFileDescription("");
      setFileKey(previous => previous + 1);
    } catch (err) {
      console.error(err);
      setError(
        "Unable to upload file. Confirm it is an Excel-compatible format under 10 MB and try again."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleLinkSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!sessionId || !linkUrl.trim()) {
      return;
    }
    try {
      setSubmittingLink(true);
      setError(null);
      const payload = {
        url: linkUrl.trim(),
        description: linkDescription.trim()
      };
      const response = await api.post<ArtifactUploadResponse>(
        `/session/${sessionId}/artifacts/link`,
        payload
      );
      onArtifactAdded(response.data.artifact);
      setLinkUrl("");
      setLinkDescription("");
    } catch (err) {
      console.error(err);
      setError("Unable to record link. Provide a shareable URL that begins with http:// or https://.");
    } finally {
      setSubmittingLink(false);
    }
  };

  return (
    <div className="space-y-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">
          Candidate submissions
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          Upload finished workbooks or share live spreadsheet links so the interviewer can review formulas,
          pivots, and notes directly.
        </p>
      </div>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleFileUpload} className="space-y-2">
        <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Upload workbook file
        </div>
        <input
          key={fileKey}
          type="file"
          accept={DOWNLOADABLE_EXTENSIONS.join(",")}
          className="block w-full text-sm text-slate-700 file:mr-3 file:cursor-pointer file:rounded-md file:border-0 file:bg-primary-600 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white"
          onChange={handleFileChange}
          disabled={submissionDisabled || uploading}
        />
        <input
          type="text"
          value={fileDescription}
          onChange={event => setFileDescription(event.target.value)}
          placeholder="Optional context (tabs to review, validation steps, etc.)"
          className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
          disabled={submissionDisabled || uploading}
        />
        <button
          type="submit"
          className="rounded-md bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-500 disabled:cursor-not-allowed disabled:bg-slate-400"
          disabled={submissionDisabled || uploading || !selectedFile}
        >
          {uploading ? "Uploading..." : "Upload workbook"}
        </button>
        <p className="text-xs text-slate-500">
          Accepted formats: {DOWNLOADABLE_EXTENSIONS.join(", ")} (max 10 MB).
        </p>
      </form>

      <form onSubmit={handleLinkSubmit} className="space-y-2">
        <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Share Google Sheets or online Excel link
        </div>
        <input
          type="url"
          value={linkUrl}
          onChange={event => setLinkUrl(event.target.value)}
          placeholder="https://docs.google.com/..."
          className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
          disabled={submissionDisabled || submittingLink}
          required
        />
        <input
          type="text"
          value={linkDescription}
          onChange={event => setLinkDescription(event.target.value)}
          placeholder="Optional description (filters applied, tabs to inspect)"
          className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none"
          disabled={submissionDisabled || submittingLink}
        />
        <button
          type="submit"
          className="rounded-md border border-primary-200 bg-white px-4 py-2 text-sm font-semibold text-primary-600 shadow-sm transition hover:bg-primary-50 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400"
          disabled={submissionDisabled || submittingLink || !linkUrl.trim()}
        >
          {submittingLink ? "Saving..." : "Save live spreadsheet link"}
        </button>
      </form>

      <div className="space-y-2">
        <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">Shared artifacts</div>
        {sessionId ? (
          artifacts.length ? (
            <ul className="space-y-2 text-sm text-slate-700">
              {artifacts.map(artifact => {
                const uploaded = new Date(artifact.uploaded_at).toLocaleString();
                const detail = [
                  artifact.filename,
                  formatBytes(artifact.size_bytes)
                ]
                  .filter(Boolean)
                  .join(" • ");
                const description = artifact.description?.trim();
                const href =
                  artifact.source === "file" && baseDownloadUrl
                    ? `${baseDownloadUrl}/${artifact.id}`
                    : artifact.url ?? undefined;
                return (
                  <li key={artifact.id} className="rounded-md border border-slate-200 px-3 py-2">
                    <div className="flex items-center justify-between gap-3">
                      <div className="font-semibold text-slate-900">
                        {artifact.source === "file" ? artifact.filename ?? "Workbook" : "Live spreadsheet link"}
                      </div>
                      {href && (
                        <a
                          href={href}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs font-medium text-primary-600 hover:text-primary-500"
                        >
                          {artifact.source === "file" ? "Download" : "Open"}
                        </a>
                      )}
                    </div>
                    {detail && <div className="text-xs text-slate-500">{detail}</div>}
                    {description && <div className="mt-1 text-xs text-slate-600">{description}</div>}
                    <div className="mt-1 text-[11px] uppercase tracking-wide text-slate-400">Submitted {uploaded}</div>
                  </li>
                );
              })}
            </ul>
          ) : (
            <div className="rounded-md border border-dashed border-slate-200 px-3 py-3 text-xs text-slate-500">
              No submissions yet. Encourage the candidate to upload their workbook or share a link when ready.
            </div>
          )
        ) : (
          <div className="rounded-md border border-dashed border-slate-200 px-3 py-3 text-xs text-slate-500">
            Start an interview to enable workbook uploads and link sharing.
          </div>
        )}
      </div>
    </div>
  );
}
