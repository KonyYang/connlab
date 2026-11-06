import { useEffect, useRef, useState, type ChangeEvent, type ReactElement } from "react";
import { CustomerReportProgress } from "../components/common/CustomerReportProgress";
import {
  downloadStandaloneCustomerReport,
  readStandaloneCustomerReportJob,
  startStandaloneCustomerReport,
  type BlobDownloadResponse,
  type StandaloneCustomerReportJob,
} from "../api/client";
import { EquipmentListTool } from "../features/tools/EquipmentListTool";
import { MechanicalSummaryTool } from "../features/tools/MechanicalSummaryTool";
import { EncryptionTool } from "../features/tools/EncryptionTool";
import { ToolsFeedback, ToolsFeedbackTarget } from "../features/tools/ToolsFeedback";
import "../tools.css";
import { MatrixEditorWorkspace } from '../features/matrix-editor/MatrixEditorWorkspace';
import { ToolsFeeWorkspace } from '../features/tools/ToolsFeeWorkspace';
import { clearPlanningSession } from '../api/toolsPlanning';

type ToolKey = "customer-report";

type ToolState = {
  file: File | null;
  busy: boolean;
  error: string | null;
  downloadedFileName: string | null;
  progress: StandaloneCustomerReportJob | null;
};

const INITIAL_STATE: Record<ToolKey, ToolState> = {
  "customer-report": { file: null, busy: false, error: null, downloadedFileName: null, progress: null },
};

const CUSTOMER_REPORT_POLL_DELAY_MS = 750;

export function ToolsPage({
  onOpenTemperatureRise = () => { window.location.assign('/tools/temperature-rise'); },
}: { onOpenTemperatureRise?: () => void } = {}): ReactElement {
  const [planning, setPlanning] = useState<'matrix' | 'fee' | null>(() => new URLSearchParams(window.location.search).has('planning') ? 'matrix' : null);
  const [planningKey,setPlanningKey] = useState(0);
  const [state, setState] = useState(INITIAL_STATE);
  const [feedbackTarget, setFeedbackTarget] = useState<HTMLDivElement | null>(null);
  const runningTools = useRef(new Set<ToolKey>());
  const runTokens = useRef<Record<ToolKey, number>>({
    "customer-report": 0,
  });

  useEffect(() => () => {
    runTokens.current["customer-report"] += 1;
  }, []);

  function selectFile(tool: ToolKey, event: ChangeEvent<HTMLInputElement>): void {
    const file = event.target.files?.[0] ?? null;
    if (runningTools.current.has(tool)) return;
    event.target.value = "";
    if (file) void run(tool, file);
  }

  async function run(tool: ToolKey, selectedFile?: File): Promise<void> {
    if (runningTools.current.has(tool)) return;
    const file = selectedFile ?? state[tool].file;
    if (!file) {
      setState((value) => ({
        ...value,
        [tool]: { ...value[tool], error: "Select a file first.", downloadedFileName: null },
      }));
      return;
    }
    runningTools.current.add(tool);
    setState((value) => ({
      ...value,
      [tool]: { file, busy: true, error: null, downloadedFileName: null, progress: null },
    }));
    const token = ++runTokens.current[tool];
    const isCurrentRun = () => runTokens.current[tool] === token;
    try {
      const response = await runCustomerReportJob(file, isCurrentRun, (progress) => {
        setState((value) => ({
          ...value,
          [tool]: { ...value[tool], progress },
        }));
      });
      if (!isCurrentRun()) return;
      const fileName = response.fileName ?? fallbackName(file);
      downloadBlob(response, fileName);
      setState((value) => ({
        ...value,
        [tool]: {
          ...value[tool],
          busy: false,
          progress: null,
          downloadedFileName: fileName,
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
    } finally {
      runningTools.current.delete(tool);
    }
  }

  if (planning === 'matrix') return <><div className="tools-planning-actions"><button type="button" onClick={() => {
    if (window.confirm('Clear this Tools Matrix and its fee estimate? Download any files you want to retain first.')) {
      clearPlanningSession(); setPlanningKey(value=>value+1);
    }
  }}>New planning Matrix</button></div><MatrixEditorWorkspace key={planningKey} standalone projectId="" onBackToWorkbench={()=>setPlanning(null)} onEvaluateFees={()=>setPlanning('fee')} /></>;
  if (planning === 'fee') return <ToolsFeeWorkspace onBack={()=>setPlanning('matrix')} />;
  return (
    <ToolsFeedbackTarget value={feedbackTarget}><section className="tools-page" aria-label="Tools">
      <div className="tools-grid" role="group" aria-label="Tool actions">
        <article className="tools-action-group" aria-label="Matrix and Fee planning"><button type="button" className="primary-action tools-picker-action" onClick={()=>setPlanning('matrix')}>Matrix and Fee planning</button></article>
        <EquipmentListTool />
        <MechanicalSummaryTool />
        <article className="tools-action-group" aria-label="Temperature Rise">
          <button className="primary-action tools-picker-action" type="button" title="Open the temperature rise and derating workspace." onClick={onOpenTemperatureRise}>Drawing T-rise</button>
        </article>
        <ToolCard
          title="Internal Report → Customer Report"
          accept=".docx"
          state={state["customer-report"]}
          inputLabel="Select Internal Report"
          actionLabel="Generate Customer Report"
          pickAndRun
          onSelect={(event) => selectFile("customer-report", event)}
          onRun={() => void run("customer-report")}
        />
        <EncryptionTool />
      </div>
      <div className="tools-feedback-stack" ref={setFeedbackTarget} />
    </section></ToolsFeedbackTarget>
  );
}

function ToolCard({
  title,
  hint,
  accept,
  state,
  inputLabel,
  actionLabel,
  onSelect,
  onRun,
  pickAndRun = false,
}: {
  title: string;
  hint?: string;
  accept: string;
  state: ToolState;
  inputLabel: string;
  actionLabel: string;
  onSelect: (event: ChangeEvent<HTMLInputElement>) => void;
  onRun: () => void;
  pickAndRun?: boolean;
}): ReactElement {
  const fileInput = useRef<HTMLInputElement>(null);
  return (
    <article className="tools-action-group" aria-label={title}>
      {pickAndRun ? <input ref={fileInput} type="file" hidden aria-label={inputLabel}
        accept={accept} disabled={state.busy} onChange={onSelect} /> : <label className="tools-file-picker">
        <span>{inputLabel}</span>
        <input type="file" accept={accept} disabled={state.busy} onChange={onSelect} />
      </label>}
      <button className={pickAndRun ? "primary-action tools-picker-action" : "primary-action"} type="button" title={inputLabel} disabled={state.busy}
        onClick={pickAndRun ? () => fileInput.current?.click() : onRun}>
        {state.busy ? (state.progress ? "Generating..." : "Starting...") : actionLabel}
      </button>
      {(hint || state.error || (state.busy && state.progress) || state.downloadedFileName) && <ToolsFeedback><div className="tools-action-feedback">
        {hint && <p className="tools-card-hint">{hint}</p>}
        {state.error && <p className="tools-feedback tools-feedback-error" role="alert">{state.error}</p>}
        {state.busy && state.progress && <CustomerReportProgress stage={state.progress.stage} elapsedSeconds={state.progress.elapsed_seconds} />}
        {state.downloadedFileName && <p className="tools-feedback tools-feedback-success" role="status" aria-label="Downloaded File">
          {state.downloadedFileName}
        </p>}
      </div></ToolsFeedback>}
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

function fallbackName(file: File): string {
  const dot = file.name.lastIndexOf(".");
  const stem = dot > 0 ? file.name.slice(0, dot) : file.name;
  const suffix = dot > 0 ? file.name.slice(dot) : ".docx";
  return `${stem}-CR${suffix}`;
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
