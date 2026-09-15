import { useCallback, useEffect, useRef, useState } from "react";
import {
  ApiRequestError, downloadProjectCustomerReportJob, fetchLatestProjectCustomerReportJob,
  readProjectCustomerReportJob, startProjectCustomerReportJob,
  type BlobDownloadResponse, type ProjectCustomerReportInput, type ProjectCustomerReportJob,
} from "../../api/client";

const LOST_JOB = "The customer report task expired or the backend restarted. Review the current report before generating again.";
const isRunning = (job: ProjectCustomerReportJob | null) => job?.status === "queued" || job?.status === "running";
const detail = (reason: unknown) => reason instanceof Error ? reason.message : "Unknown error.";

// Storage is a recovery hint, never task authority. Restricted browser storage must not prevent generation.
function remember(projectId: string, operationId?: string): string | null {
  try {
    const key = `connlab.customer-report-job.${projectId}`;
    if (operationId !== undefined) sessionStorage.setItem(key, operationId);
    return sessionStorage.getItem(key);
  } catch { return null; }
}

export function useCustomerReportJob(projectId: string, save: (value: BlobDownloadResponse) => void, pollMs = 1000) {
  const [job, setJob] = useState<ProjectCustomerReportJob | null>(null);
  const [checking, setChecking] = useState(true);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [queryWarning, setQueryWarning] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  const [downloaded, setDownloaded] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const epoch = useRef(0);
  const startPending = useRef(false);
  const downloadPending = useRef(false);
  const queryPending = useRef(false);
  const current = useRef<ProjectCustomerReportJob | null>(null);
  const automaticDownload = useRef<string | null>(null);
  const saveRef = useRef(save);
  saveRef.current = save;

  const accept = useCallback((next: ProjectCustomerReportJob | null) => {
    current.current = next;
    setJob(next);
    setQueryWarning(null);
    if (next) remember(projectId, next.operation_id);
  }, [projectId]);

  const retryQuery = useCallback(async () => {
    if (queryPending.current) return;
    queryPending.current = true;
    const ticket = epoch.current;
    try {
      const known = current.current;
      const next = known
        ? await readProjectCustomerReportJob(projectId, known.operation_id)
        : await fetchLatestProjectCustomerReportJob(projectId);
      if (ticket !== epoch.current) return;
      accept(next);
      setChecking(false);
      if (!next && remember(projectId)) setError(LOST_JOB);
    } catch (reason) {
      if (ticket !== epoch.current) return;
      if (reason instanceof ApiRequestError && [404, 410].includes(reason.status)) {
        accept(null);
        setChecking(false);
        setError(LOST_JOB);
      } else {
        setQueryWarning(`Progress temporarily unavailable. The backend task may still be running. Retry the status check. ${detail(reason)}`);
      }
    } finally {
      if (ticket === epoch.current) queryPending.current = false;
    }
  }, [accept, projectId]);

  useEffect(() => {
    epoch.current += 1;
    current.current = null;
    startPending.current = false;
    downloadPending.current = false;
    queryPending.current = false;
    automaticDownload.current = null;
    setJob(null); setChecking(true); setStarting(false); setError(null);
    setQueryWarning(null); setDownloadError(null); setDownloading(false); setDownloaded(false);
    void retryQuery();
    return () => { epoch.current += 1; };
  }, [projectId, retryQuery]);

  useEffect(() => {
    if (!isRunning(job)) return;
    let stopped = false;
    let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      await retryQuery();
      if (!stopped) timer = setTimeout(() => void poll(), pollMs);
    };
    timer = setTimeout(() => void poll(), pollMs);
    return () => { stopped = true; clearTimeout(timer); };
  }, [job?.operation_id, job?.status, pollMs, retryQuery]);

  useEffect(() => {
    setElapsed(job?.elapsed_seconds ?? 0);
    if (!isRunning(job)) return;
    const receivedAt = Date.now();
    const timer = setInterval(() => setElapsed((job?.elapsed_seconds ?? 0) + (Date.now() - receivedAt) / 1000), 1000);
    return () => clearInterval(timer);
  }, [job]);

  const download = useCallback(async () => {
    const ready = current.current;
    if (downloadPending.current || ready?.status !== "completed" || ready.result?.mode !== "managed_download") return;
    downloadPending.current = true;
    const ticket = epoch.current;
    setDownloading(true); setDownloadError(null);
    try {
      const response = await downloadProjectCustomerReportJob(projectId, ready.operation_id);
      if (ticket !== epoch.current) return;
      saveRef.current(response);
      setDownloaded(true);
    } catch (reason) {
      if (ticket !== epoch.current) return;
      if (reason instanceof ApiRequestError && [404, 410].includes(reason.status)) {
        accept(null);
        setDownloaded(false);
        setError("The generated download expired or is no longer available. Review the current report and generate a new copy.");
      } else {
        setDownloadError(`Download failed; the report was generated. Retry download without regenerating. ${detail(reason)}`);
      }
    } finally {
      if (ticket === epoch.current) { downloadPending.current = false; setDownloading(false); }
    }
  }, [accept, projectId]);

  useEffect(() => {
    if (job?.status === "completed" && automaticDownload.current === job.operation_id) {
      automaticDownload.current = null;
      void download();
    }
  }, [job, download]);

  async function start(input: ProjectCustomerReportInput): Promise<void> {
    if (startPending.current || checking || isRunning(current.current) || downloadPending.current) return;
    startPending.current = true;
    const ticket = epoch.current;
    setStarting(true); setError(null); setDownloadError(null); setDownloaded(false);
    try {
      const next = await startProjectCustomerReportJob(projectId, input);
      if (ticket !== epoch.current) return;
      automaticDownload.current = next.operation_id;
      accept(next);
    } catch (reason) {
      if (ticket !== epoch.current) return;
      if (reason instanceof ApiRequestError && reason.status < 500) throw reason;
      // The start response may have been lost after acceptance. Reconcile before allowing another start.
      setChecking(true);
      setQueryWarning(`Unable to confirm whether generation started. Check task status before retrying. ${detail(reason)}`);
      current.current = null;
    } finally {
      if (ticket === epoch.current) { startPending.current = false; setStarting(false); }
    }
  }

  return { job, busy: checking || starting || isRunning(job), starting, elapsed, error,
    queryWarning, downloadError, downloading, downloaded, start, download, retryQuery };
}
