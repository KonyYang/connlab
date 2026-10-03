import { useCallback, useEffect, useRef, useState } from "react";
import {
  ApiRequestError,
  downloadStandaloneCustomerReport,
  readStandaloneCustomerReportJob,
  startStandaloneCustomerReport,
  type BlobDownloadResponse,
  type StandaloneCustomerReportJob,
} from "../../api/client";

// Uploaded reports are download-only sources, never project report authority.
export function useUploadedCustomerReportJob(projectId: string, save: (response: BlobDownloadResponse) => void) {
  const [job, setJob] = useState<StandaloneCustomerReportJob | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queryWarning, setQueryWarning] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const context = useRef(projectId);
  context.current = projectId;
  const epoch = useRef(0);
  const locked = useRef(false);
  const automaticallyDownloaded = useRef<string | null>(null);
  const jobProject = useRef<string | null>(null);
  const saveRef = useRef(save);
  saveRef.current = save;
  const current = useCallback((token: number) => epoch.current === token && context.current === projectId, [projectId]);

  useEffect(() => {
    epoch.current += 1;
    locked.current = false;
    automaticallyDownloaded.current = null;
    jobProject.current = null;
    setJob(null);
    setPending(false);
    setError(null);
    setQueryWarning(null);
    setDownloadError(null);
    setFileName(null);
    return () => { epoch.current += 1; };
  }, [projectId]);

  const start = async (file: File): Promise<boolean> => {
    if (locked.current || job?.status === "running" || job?.status === "queued") return false;
    const token = epoch.current;
    locked.current = true;
    setPending(true);
    setError(null);
    setQueryWarning(null);
    setDownloadError(null);
    setFileName(null);
    setJob(null);
    try {
      const next = await startStandaloneCustomerReport(file);
      if (!current(token)) return false;
      jobProject.current = projectId;
      setJob(next);
      return true;
    } catch (reason) {
      if (current(token)) setError(reason instanceof Error ? reason.message : "Unable to upload the Internal Report. Try again.");
      return false;
    } finally {
      if (current(token)) { locked.current = false; setPending(false); }
    }
  };

  const query = useCallback(async (operationId: string) => {
    if (locked.current) return;
    const token = epoch.current;
    locked.current = true;
    try {
      const next = await readStandaloneCustomerReportJob(operationId);
      if (current(token)) { setJob(next); setQueryWarning(null); }
    } catch (reason) {
      // A failed GET does not mean generation failed. Keep the operation and avoid duplicate uploads.
      if (current(token)) {
        if (reason instanceof ApiRequestError && (reason.status === 404 || reason.status === 410)) {
          setJob(null);
          setQueryWarning(null);
          setError("The generation operation expired or is not available. Select the Internal Report and generate again.");
        } else setQueryWarning(reason instanceof Error ? reason.message : "Unable to check generation status.");
      }
    } finally {
      if (current(token)) locked.current = false;
    }
  }, [current]);

  useEffect(() => {
    if (jobProject.current !== projectId || !job || (job.status !== "queued" && job.status !== "running") || queryWarning) return;
    const timer = window.setTimeout(() => void query(job.operation_id), 750);
    return () => window.clearTimeout(timer);
  }, [job, projectId, query, queryWarning]);

  const download = useCallback(async (operationId: string) => {
    if (locked.current) return;
    const token = epoch.current;
    locked.current = true;
    setPending(true);
    setDownloadError(null);
    try {
      const response = await downloadStandaloneCustomerReport(operationId);
      if (!current(token)) return;
      saveRef.current(response);
      setFileName(response.fileName || "Customer Report.docx");
    } catch (reason) {
      if (current(token)) {
        if (reason instanceof ApiRequestError && (reason.status === 404 || reason.status === 410)) {
          setJob(null);
          setDownloadError(null);
          setError("The generated copy expired or is not available. Select the Internal Report and generate again.");
        } else setDownloadError(reason instanceof Error ? reason.message : "Unable to download the generated report. Retry download.");
      }
    } finally {
      if (current(token)) { locked.current = false; setPending(false); }
    }
  }, [current]);

  useEffect(() => {
    if (jobProject.current !== projectId || job?.status !== "completed" || automaticallyDownloaded.current === job.operation_id) return;
    automaticallyDownloaded.current = job.operation_id;
    void download(job.operation_id);
  }, [job, projectId, download]);

  return {
    job, error, queryWarning, downloadError, fileName, start,
    busy: pending || job?.status === "running" || job?.status === "queued",
    retryQuery: () => job && query(job.operation_id),
    retryDownload: () => job?.status === "completed" && download(job.operation_id),
  };
}
