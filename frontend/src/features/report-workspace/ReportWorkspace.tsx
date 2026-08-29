import { useCallback, useEffect, useMemo, useState, type ReactElement } from "react";
import {
  cancelLlcrResultPreview,
  confirmLlcrResultImport,
  downloadReportDraftRevision,
  fetchReportWorkspace,
  generateInitialReportRevision,
  generateLlcrReportRevision,
  inspectLlcrResultWorkbook,
  type LlcrImportPreview,
  type ReportDraftRevision,
  type ReportWorkspaceState,
} from "../../api/client";
import { ErrorMessage } from "../../components/common/ErrorMessage";
import { LlcrImportPreviewDialog } from "./LlcrImportPreviewDialog";
import {
  buildLlcrConfirmationDecisions,
  createLlcrDecisionDrafts,
  deriveReportWorkspaceReadiness,
  type LlcrDecisionDrafts,
  type LlcrOutcome,
} from "./reportWorkspaceModel";

type ReportWorkspaceProps = {
  projectId: string;
  onBack: () => void;
};

type BusyAction = "load" | "initial" | "inspect" | "confirm" | "cancel" | "llcr" | "download" | null;

export function ReportWorkspace({ projectId, onBack }: ReportWorkspaceProps): ReactElement {
  const [state, setState] = useState<ReportWorkspaceState | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<LlcrImportPreview | null>(null);
  const [decisionDrafts, setDecisionDrafts] = useState<LlcrDecisionDrafts>({});
  const [busyAction, setBusyAction] = useState<BusyAction>("load");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const nextState = await fetchReportWorkspace(projectId);
    setState(nextState);
    return nextState;
  }, [projectId]);

  useEffect(() => {
    let active = true;
    setBusyAction("load");
    setError(null);
    fetchReportWorkspace(projectId)
      .then((nextState) => {
        if (active) {
          setState(nextState);
        }
      })
      .catch((reason: unknown) => {
        if (active) {
          setError(errorMessage(reason, "Unable to load Report Workspace."));
        }
      })
      .finally(() => {
        if (active) {
          setBusyAction(null);
        }
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  const readiness = useMemo(
    () => state ? deriveReportWorkspaceReadiness(state) : null,
    [state]
  );
  const latestDataset = state?.datasets.at(-1) ?? null;

  async function runAction(
    action: Exclude<BusyAction, "load" | null>,
    operation: () => Promise<string | null>
  ): Promise<void> {
    if (busyAction) {
      return;
    }
    setBusyAction(action);
    setError(null);
    setMessage(null);
    try {
      setMessage(await operation());
    } catch (reason) {
      setError(errorMessage(reason, "Report workflow failed."));
    } finally {
      setBusyAction(null);
    }
  }

  async function handleInspect(): Promise<void> {
    if (!selectedFile) {
      setError("Select an LLCR result workbook first.");
      return;
    }
    await runAction("inspect", async () => {
      const result = await inspectLlcrResultWorkbook(projectId, selectedFile);
      setPreview(result);
      setDecisionDrafts(createLlcrDecisionDrafts(result));
      return result.can_confirm
        ? `Previewed ${result.result_count} LLCR report target${result.result_count === 1 ? "" : "s"}.`
        : null;
    });
  }

  async function handleConfirm(): Promise<void> {
    if (!preview) {
      return;
    }
    await runAction("confirm", async () => {
      const dataset = await confirmLlcrResultImport(projectId, {
        preview_id: preview.preview_id,
        confirmed_by: "Lab User",
        decisions: buildLlcrConfirmationDecisions(preview, decisionDrafts),
      });
      setPreview(null);
      setDecisionDrafts({});
      await refresh();
      return `Confirmed LLCR Result Dataset revision ${dataset.revision}.`;
    });
  }

  async function handleCancelPreview(): Promise<void> {
    if (!preview || busyAction) {
      return;
    }
    setBusyAction("cancel");
    setError(null);
    try {
      await cancelLlcrResultPreview(projectId, preview.preview_id);
      setPreview(null);
      setDecisionDrafts({});
    } catch (reason) {
      setError(errorMessage(reason, "Unable to cancel the LLCR preview."));
    } finally {
      setBusyAction(null);
    }
  }

  async function handleDownload(revision: ReportDraftRevision): Promise<void> {
    await runAction("download", async () => {
      const response = await downloadReportDraftRevision(projectId, revision.report_revision_id);
      downloadBlob(response.blob, response.fileName || revision.file_name);
      return `Downloaded report draft revision ${revision.revision}.`;
    });
  }

  if (!state && busyAction === "load" && !error) {
    return (
      <section aria-busy="true" className="report-workspace-page">
        <div className="panel" role="status">Loading Report Workspace...</div>
      </section>
    );
  }

  return (
    <section className="report-workspace-page">
      <header className="report-workspace-header">
        <div>
          <button className="report-workspace-back" onClick={onBack} type="button">← Project Workbench</button>
          <p className="report-workspace-eyebrow">Controlled internal report drafts</p>
          <h1>Report Workspace</h1>
          <p>Import, review, confirm, and synchronize test results without overwriting source files or prior report revisions.</p>
        </div>
        {state ? (
          <div className="report-workspace-authority-card">
            <span>Current authority</span>
            <small>Project {state.project_id}</small>
            <strong>{state.active_confirmed_matrix_id ? `Confirmed Matrix revision ${state.active_confirmed_matrix_revision}` : "No active Confirmed Matrix"}</strong>
            <small>{state.basic_information_status === "confirmed" ? `Basic Information version ${state.confirmed_basic_information_version}` : "Basic Information not confirmed"}</small>
            <small>{state.latest_report_revision ? `Latest report draft revision ${state.latest_report_revision.revision}` : "No report draft yet"}</small>
          </div>
        ) : null}
      </header>

      {error ? <ErrorMessage message={error} /> : null}
      {message ? <p className="report-workspace-message" role="status">{message}</p> : null}

      {state && readiness ? (
        <div className="report-workspace-grid">
          <article className="report-workspace-card">
            <div className="report-workspace-card-heading">
              <span className="report-workspace-step">01</span>
              <div><h2>Start or refresh the report</h2><p>Create a new non-overwriting E-3707_H initialization draft from current confirmed authorities.</p></div>
            </div>
            <button
              className="primary-action"
              disabled={!readiness.canGenerateInitialDraft || Boolean(busyAction)}
              onClick={() => void runAction("initial", async () => {
                const revision = await generateInitialReportRevision(projectId);
                await refresh();
                return `Generated initial report draft revision ${revision.revision}.`;
              })}
              type="button"
            >
              {busyAction === "initial" ? "Generating..." : "Generate initial draft"}
            </button>
            {readiness.initialDraftBlocker ? <p className="report-workspace-blocker">{readiness.initialDraftBlocker}</p> : null}
          </article>

          <article className="report-workspace-card">
            <div className="report-workspace-card-heading">
              <span className="report-workspace-step">02</span>
              <div><h2>Import LLCR results</h2><p>Inspect a workbook against the active Matrix before creating an immutable Result Dataset.</p></div>
            </div>
            <label className="report-workspace-file-field">
              LLCR result workbook
              <input
                accept=".xlsx"
                disabled={Boolean(busyAction)}
                onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                type="file"
              />
            </label>
            <button disabled={!selectedFile || Boolean(busyAction)} onClick={() => void handleInspect()} type="button">
              {busyAction === "inspect" ? "Inspecting..." : "Inspect LLCR workbook"}
            </button>
            <p className="report-workspace-note">Preview does not update the database or report. Confirming always creates a new dataset revision.</p>
          </article>

          <article className="report-workspace-card">
            <div className="report-workspace-card-heading">
              <span className="report-workspace-step">03</span>
              <div><h2>Synchronize confirmed LLCR results</h2><p>Copy the latest internal draft and update only controlled LLCR Result and Comment cells.</p></div>
            </div>
            {latestDataset ? (
              <dl className="report-workspace-dataset-summary">
                <div><dt>Latest dataset</dt><dd>Revision {latestDataset.revision}</dd></div>
                <div><dt>Source</dt><dd>{latestDataset.source_file_name}</dd></div>
                <div><dt>Confirmed</dt><dd>{formatDateTime(latestDataset.confirmed_at)}</dd></div>
                <div><dt>Results</dt><dd>{latestDataset.entries.length}</dd></div>
              </dl>
            ) : <p className="report-workspace-empty">No confirmed LLCR Result Dataset yet.</p>}
            <button
              className="primary-action"
              disabled={!readiness.canGenerateLlcrDraft || Boolean(busyAction) || !latestDataset}
              onClick={() => latestDataset && void runAction("llcr", async () => {
                const revision = await generateLlcrReportRevision(projectId, latestDataset.dataset_id);
                await refresh();
                return `Generated LLCR report draft revision ${revision.revision}.`;
              })}
              type="button"
            >
              {busyAction === "llcr" ? "Synchronizing..." : "Generate new LLCR report draft"}
            </button>
            {readiness.llcrDraftBlocker ? <p className="report-workspace-blocker">{readiness.llcrDraftBlocker}</p> : null}
          </article>

          <article className="report-workspace-card report-workspace-history">
            <div className="report-workspace-card-heading">
              <span className="report-workspace-step">04</span>
              <div><h2>Report draft history</h2><p>Every generation creates a separate downloadable revision.</p></div>
            </div>
            {state.report_revisions.length ? (
              <ol>
                {[...state.report_revisions].reverse().map((revision) => (
                  <li key={revision.report_revision_id}>
                    <div><strong>Revision {revision.revision}</strong><span>{revision.file_name}</span><small>{formatDateTime(revision.created_at)} · {revision.result_dataset_id ? "LLCR synchronized" : "Initialization"}</small></div>
                    <button disabled={Boolean(busyAction)} onClick={() => void handleDownload(revision)} type="button">Download</button>
                  </li>
                ))}
              </ol>
            ) : <p className="report-workspace-empty">No report draft revisions yet.</p>}
          </article>
        </div>
      ) : null}

      {preview ? (
        <LlcrImportPreviewDialog
          canceling={busyAction === "cancel"}
          confirming={busyAction === "confirm"}
          drafts={decisionDrafts}
          onCancel={() => void handleCancelPreview()}
          onConfirm={() => void handleConfirm()}
          onDraftChange={(resultId, outcome: LlcrOutcome, overrideReason) => setDecisionDrafts((current) => ({
            ...current,
            [resultId]: { outcome, overrideReason },
          }))}
          preview={preview}
        />
      ) : null}
    </section>
  );
}

function formatDateTime(value: string): string {
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

function errorMessage(reason: unknown, fallback: string): string {
  return reason instanceof Error ? reason.message : fallback;
}

function downloadBlob(blob: Blob, fileName: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);
}
