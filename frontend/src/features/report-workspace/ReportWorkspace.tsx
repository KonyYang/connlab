import { useCallback, useEffect, useMemo, useState, type ReactElement } from "react";
import {
  cancelLlcrResultPreview,
  confirmLlcrResultImport,
  downloadCurrentReport,
  fetchCurrentReport,
  fetchReportWorkspace,
  generateInitialReportRevision,
  inspectLlcrResultWorkbook,
  publishManagedReport,
  previewCurrentReportLlcrUpdate,
  updateCurrentReportLlcr,
  type CurrentReport,
  type LlcrImportPreview,
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

type BusyAction = "load" | "initial" | "inspect" | "confirm" | "cancel" | "llcr" | "publish" | "download" | null;

export function ReportWorkspace({ projectId, onBack }: ReportWorkspaceProps): ReactElement {
  const [state, setState] = useState<ReportWorkspaceState | null>(null);
  const [currentReport, setCurrentReport] = useState<CurrentReport | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<LlcrImportPreview | null>(null);
  const [decisionDrafts, setDecisionDrafts] = useState<LlcrDecisionDrafts>({});
  const [busyAction, setBusyAction] = useState<BusyAction>("load");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const [nextState, nextReport] = await Promise.all([
      fetchReportWorkspace(projectId),
      fetchCurrentReport(projectId),
    ]);
    setState(nextState);
    setCurrentReport(nextReport);
    return nextState;
  }, [projectId]);

  useEffect(() => {
    let active = true;
    setBusyAction("load");
    setError(null);
    Promise.all([fetchReportWorkspace(projectId), fetchCurrentReport(projectId)])
      .then(([nextState, nextReport]) => {
        if (active) {
          setState(nextState);
          setCurrentReport(nextReport);
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

  async function handleDownloadCurrent(): Promise<void> {
    await runAction("download", async () => {
      const response = await downloadCurrentReport(projectId);
      downloadBlob(response.blob, response.fileName || currentReport?.file_name || "Internal Report.docx");
      return "Downloaded the current internal report.";
    });
  }

  async function handleUpdateLlcr(): Promise<void> {
    if (!latestDataset) {
      return;
    }
    await runAction("llcr", async () => {
      const updatePreview = await previewCurrentReportLlcrUpdate(
        projectId,
        latestDataset.dataset_id
      );
      const expectedSha = updatePreview.current_report.file_sha256;
      if (updatePreview.status !== "ready" || !expectedSha) {
        throw new Error(
          updatePreview.blockers.join(" ") || "The current internal report cannot be updated."
        );
      }
      const result = await updateCurrentReportLlcr(projectId, {
        dataset_id: latestDataset.dataset_id,
        expected_report_sha256: expectedSha,
        updated_by: "Lab User",
      });
      await refresh();
      return result.changed
        ? `Updated LLCR results in ${result.file_name}. The previous report was archived automatically.`
        : `LLCR results in ${result.file_name} were already up to date.`;
    });
  }

  async function handlePublishManagedReport(): Promise<void> {
    const expectedSha = currentReport?.file_sha256;
    if (!expectedSha || !currentReport.can_publish_to_official) {
      return;
    }
    await runAction("publish", async () => {
      const published = await publishManagedReport(projectId, expectedSha);
      await refresh();
      return `Published the current report to ${published.folder_path ?? "the project folder"}.`;
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
          <p className="report-workspace-eyebrow">Controlled current internal report</p>
          <h1>Report Workspace</h1>
          <p>Import confirmed test data and update one controlled report region at a time. Successful changes archive the previous report automatically.</p>
        </div>
        {state ? (
          <div className="report-workspace-authority-card">
            <span>Current authority</span>
            <small>Project {state.project_id}</small>
            <strong>{state.active_confirmed_matrix_id ? `Confirmed Matrix revision ${state.active_confirmed_matrix_revision}` : "No active Confirmed Matrix"}</strong>
            <small>{state.basic_information_status === "confirmed" ? `Basic Information version ${state.confirmed_basic_information_version}` : "Basic Information not confirmed"}</small>
            <small>{currentReport?.file_name ?? "No current internal report"}</small>
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
              <div><h2>Create the initial report</h2><p>Use the approved E-3707_H template only when this project does not yet have a current internal report.</p></div>
            </div>
            <button
              className="primary-action"
              disabled={!readiness.canGenerateInitialDraft || Boolean(busyAction) || currentReport?.status !== "missing"}
              onClick={() => void runAction("initial", async () => {
                const revision = await generateInitialReportRevision(projectId);
                await refresh();
                return `Generated the initial internal report (${revision.file_name}).`;
              })}
              type="button"
            >
              {busyAction === "initial" ? "Generating..." : "Generate initial report"}
            </button>
            {readiness.initialDraftBlocker ? <p className="report-workspace-blocker">{readiness.initialDraftBlocker}</p> : null}
            {currentReport?.status === "ready" ? <p className="report-workspace-note">A current report already exists. Use a section update action below.</p> : null}
            {currentReport?.status === "ambiguous" ? <p className="report-workspace-blocker">Multiple internal reports were found. Resolve that conflict before creating or updating a report.</p> : null}
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
              <div><h2>Update LLCR report section</h2><p>Update only controlled LLCR Result and Comment cells. Purpose, Conclusions, Equipment, images, and appendices remain unchanged.</p></div>
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
              disabled={!readiness.canUpdateLlcr || Boolean(busyAction) || !latestDataset || currentReport?.status !== "ready"}
              onClick={() => void handleUpdateLlcr()}
              type="button"
            >
              {busyAction === "llcr" ? "Updating..." : "Update LLCR results"}
            </button>
            {readiness.llcrUpdateBlocker ? <p className="report-workspace-blocker">{readiness.llcrUpdateBlocker}</p> : null}
            {currentReport?.status !== "ready" ? <p className="report-workspace-blocker">{currentReport?.status === "ambiguous" ? "Multiple current internal reports were found. Keep exactly one before updating." : "Generate an initial report before updating LLCR results."}</p> : null}
            {currentReport?.mode === "managed_draft" ? <p className="report-workspace-note">No official project report is available. This update will use the controlled draft.</p> : null}
            {currentReport?.status === "ready" ? (
              <div className="report-workspace-current-actions">
                <span>
                  <strong>{currentReport.mode === "official" ? "Official project report" : "ConnLab managed draft"}</strong>
                  {currentReport.file_name}
                  {currentReport.folder_path ? <small title={currentReport.folder_path}>{currentReport.folder_path}</small> : null}
                </span>
                <button disabled={Boolean(busyAction)} onClick={() => void handleDownloadCurrent()} type="button">Download current report</button>
                {currentReport.can_publish_to_official ? (
                  <>
                    {currentReport.official_folder_path ? (
                      <small title={currentReport.official_folder_path}>
                        Publish destination: {currentReport.official_folder_path}
                      </small>
                    ) : null}
                    <button
                      className="primary-action"
                      disabled={Boolean(busyAction)}
                      onClick={() => void handlePublishManagedReport()}
                      type="button"
                    >
                      {busyAction === "publish" ? "Publishing..." : "Publish current draft to project folder"}
                    </button>
                  </>
                ) : null}
              </div>
            ) : null}
            <div className="report-workspace-owned-regions" aria-label="Update boundary">
              <strong>This action owns</strong>
              <span>LLCR Result and Comment cells only</span>
              <small>Manually edited Purpose and Conclusions are preserved.</small>
            </div>
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
