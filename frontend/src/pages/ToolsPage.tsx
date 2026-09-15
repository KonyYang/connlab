import { useEffect, useRef, useState, type ChangeEvent, type ReactElement } from "react";
import { CustomerReportProgress } from "../components/common/CustomerReportProgress";
import {
  downloadStandaloneCustomerReport,
  encryptStandaloneCopy,
  readStandaloneCustomerReportJob,
  startStandaloneCustomerReport,
  type BlobDownloadResponse,
  type StandaloneCustomerReportJob,
} from "../api/client";
import { UiIcon } from "../components/common/UiIcon";
import "../tools.css";

type ToolKey = "customer-report" | "encrypt-copy";

type ToolState = {
  file: File | null;
  busy: boolean;
  error: string | null;
  message: string | null;
  progress: StandaloneCustomerReportJob | null;
};

const INITIAL_STATE: Record<ToolKey, ToolState> = {
  "customer-report": { file: null, busy: false, error: null, message: null, progress: null },
  "encrypt-copy": { file: null, busy: false, error: null, message: null, progress: null },
};

const CUSTOMER_REPORT_POLL_DELAY_MS = 750;

export function ToolsPage(): ReactElement {
  const [state, setState] = useState(INITIAL_STATE);
  const runTokens = useRef<Record<ToolKey, number>>({
    "customer-report": 0,
    "encrypt-copy": 0,
  });

  useEffect(() => () => {
    runTokens.current["customer-report"] += 1;
    runTokens.current["encrypt-copy"] += 1;
  }, []);

  function selectFile(tool: ToolKey, event: ChangeEvent<HTMLInputElement>): void {
    const file = event.target.files?.[0] ?? null;
    setState((current) => ({
      ...current,
      [tool]: { file, busy: false, error: null, message: null, progress: null },
    }));
  }

  async function run(tool: ToolKey): Promise<void> {
    const current = state[tool];
    if (!current.file) {
      setState((value) => ({
        ...value,
        [tool]: { ...value[tool], error: "Select a file first.", message: null },
      }));
      return;
    }
    setState((value) => ({
      ...value,
      [tool]: { ...value[tool], busy: true, error: null, message: null, progress: null },
    }));
    const token = ++runTokens.current[tool];
    const isCurrentRun = () => runTokens.current[tool] === token;
    try {
      const response = tool === "customer-report"
        ? await runCustomerReportJob(current.file, isCurrentRun, (progress) => {
          setState((value) => ({
            ...value,
            [tool]: { ...value[tool], progress },
          }));
        })
        : await encryptStandaloneCopy(current.file);
      if (!isCurrentRun()) return;
      downloadBlob(response, response.fileName ?? fallbackName(tool, current.file));
      setState((value) => ({
        ...value,
        [tool]: {
          ...value[tool],
          busy: false,
          progress: null,
          message:
            tool === "customer-report"
              ? "Customer report generated and downloaded."
              : "Encrypted copy generated and downloaded. The original file was not changed.",
        },
      }));
    } catch (error) {
      if (!isCurrentRun()) return;
      setState((value) => ({
        ...value,
        [tool]: {
          ...value[tool],
          busy: false,
          progress: null,
          error: error instanceof Error ? error.message : "The tool could not complete.",
        },
      }));
    }
  }

  return (
    <section className="tools-page" aria-labelledby="tools-page-title">
      <header className="tools-page-header">
        <div>
          <span className="eyebrow">INDEPENDENT FILE TOOLS</span>
          <h2 id="tools-page-title">Tools</h2>
          <p>Run safe file operations without opening a project. Sources are kept unchanged.</p>
        </div>
        <span className="tools-page-icon" aria-hidden="true"><UiIcon name="tools" /></span>
      </header>

      <div className="tools-grid">
        <ToolCard
          title="Internal Report → Customer Report"
          description="Convert a compatible ConnLab Internal Report into a customer-facing report using the approved template."
          hint="Only .docx Internal Reports with the ConnLab report marker are accepted."
          accept=".docx"
          state={state["customer-report"]}
          inputLabel="Select Internal Report"
          actionLabel="Generate customer report"
          onSelect={(event) => selectFile("customer-report", event)}
          onRun={() => void run("customer-report")}
        />
        <ToolCard
          title="Encrypt a copy"
          description="Create a password-protected copy of one Word, Excel, or PowerPoint file."
          hint="The output receives a _Secured suffix. The original file is never replaced. The same ConnLab Office password is required to open and edit the copy. Excel files must start with a DL-YYYY-MM-NNN number."
          accept=".doc,.docx,.xls,.xlsx,.pptx"
          state={state["encrypt-copy"]}
          inputLabel="Select Office file"
          actionLabel="Create encrypted copy"
          onSelect={(event) => selectFile("encrypt-copy", event)}
          onRun={() => void run("encrypt-copy")}
        />
      </div>

      <p className="tools-page-note">
        Downloads use the browser's configured download location. No project folder is modified by these tools.
      </p>
    </section>
  );
}

function ToolCard({
  title,
  description,
  hint,
  accept,
  state,
  inputLabel,
  actionLabel,
  onSelect,
  onRun,
}: {
  title: string;
  description: string;
  hint: string;
  accept: string;
  state: ToolState;
  inputLabel: string;
  actionLabel: string;
  onSelect: (event: ChangeEvent<HTMLInputElement>) => void;
  onRun: () => void;
}): ReactElement {
  return (
    <article className="tools-card">
      <div className="tools-card-heading">
        <span className="tools-card-icon" aria-hidden="true"><UiIcon name="file" /></span>
        <h3>{title}</h3>
      </div>
      <p>{description}</p>
      <label className="tools-file-picker">
        <span>{inputLabel}</span>
        <input type="file" accept={accept} disabled={state.busy} onChange={onSelect} />
      </label>
      <div className="tools-selected-file" aria-live="polite">
        {state.file ? state.file.name : "No file selected"}
      </div>
      <p className="tools-card-hint">{hint}</p>
      {state.error && <p className="tools-feedback tools-feedback-error" role="alert">{state.error}</p>}
      {state.message && <p className="tools-feedback tools-feedback-success" role="status">{state.message}</p>}
      {state.progress && (
        <CustomerReportProgress stage={state.progress.stage} elapsedSeconds={state.progress.elapsed_seconds} />
      )}
      <button className="primary-action" type="button" disabled={state.busy} onClick={onRun}>
        {state.busy ? (state.progress ? "Generating..." : "Starting...") : actionLabel}
      </button>
    </article>
  );
}

async function runCustomerReportJob(
  file: File,
  isCurrentRun: () => boolean,
  onProgress: (progress: StandaloneCustomerReportJob) => void,
): Promise<BlobDownloadResponse> {
  let progress = await startStandaloneCustomerReport(file);
  if (!isCurrentRun()) {
    throw new Error("Customer report generation was cancelled.");
  }
  onProgress(progress);
  while (progress.status === "queued" || progress.status === "running") {
    progress = await readStandaloneCustomerReportJob(progress.operation_id);
    if (!isCurrentRun()) {
      throw new Error("Customer report generation was cancelled.");
    }
    onProgress(progress);
    if (progress.status === "queued" || progress.status === "running") {
      await delay(CUSTOMER_REPORT_POLL_DELAY_MS);
      if (!isCurrentRun()) {
        throw new Error("Customer report generation was cancelled.");
      }
    }
  }
  if (progress.status === "failed") {
    throw new Error(progress.message ?? "Customer report generation failed.");
  }
  return downloadStandaloneCustomerReport(progress.operation_id);
}

function delay(milliseconds: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function fallbackName(tool: ToolKey, file: File): string {
  if (tool === "customer-report") {
    const dot = file.name.lastIndexOf(".");
    const stem = dot > 0 ? file.name.slice(0, dot) : file.name;
    const suffix = dot > 0 ? file.name.slice(dot) : ".docx";
    return `${stem}-CR${suffix}`;
  }
  const dot = file.name.lastIndexOf(".");
  return `${dot > 0 ? file.name.slice(0, dot) : file.name}_Secured${dot > 0 ? file.name.slice(dot) : ""}`;
}

function downloadBlob(response: BlobDownloadResponse, fileName: string): void {
  const url = URL.createObjectURL(response.blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
