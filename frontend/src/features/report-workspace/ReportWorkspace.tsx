import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type Dispatch,
  type ReactElement,
  type SetStateAction,
} from "react";
import {
  cancelLlcrResultPreview,
  confirmLlcrResultImport,
  downloadCurrentCustomerReport,
  downloadCurrentReport,
  fetchCurrentCustomerReport,
  fetchCurrentReport,
  fetchReportWorkspace,
  generateInitialReportRevision,
  generateCurrentCustomerReport,
  inspectLlcrResultWorkbook,
  publishManagedReport,
  previewCurrentReportLlcrUpdate,
  previewCurrentReportEquipmentList,
  updateCurrentReportLlcr,
  updateCurrentReportEquipmentList,
  type CurrentReport,
  type CustomerReportState,
  type EquipmentListPreview,
  type LlcrImportPreview,
  type ReportWorkspaceState,
} from "../../api/client";
import { ErrorMessage } from "../../components/common/ErrorMessage";
import { LlcrImportPreviewDialog } from "./LlcrImportPreviewDialog";
import {
  buildLlcrConfirmationDecisions,
  buildEquipmentExternalOverrides,
  createEquipmentOverrideDrafts,
  createLlcrDecisionDrafts,
  deriveReportEntryState,
  deriveReportWorkspaceReadiness,
  validateEquipmentOverrideDrafts,
  type EquipmentOverrideDrafts,
  type LlcrDecisionDrafts,
  type LlcrOutcome,
} from "./reportWorkspaceModel";

type ReportWorkspaceProps = {
  projectId: string;
  onBack: () => void;
};

type BusyAction = "load" | "initial" | "inspect" | "confirm" | "cancel" | "llcr" | "equipment-preview" | "equipment-update" | "publish" | "download" | "customer" | "customer-download" | null;

export function ReportWorkspace({ projectId, onBack }: ReportWorkspaceProps): ReactElement {
  const [state, setState] = useState<ReportWorkspaceState | null>(null);
  const [currentReport, setCurrentReport] = useState<CurrentReport | null>(null);
  const [customerReport, setCustomerReport] = useState<CustomerReportState | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<LlcrImportPreview | null>(null);
  const [decisionDrafts, setDecisionDrafts] = useState<LlcrDecisionDrafts>({});
  const [equipmentPreview, setEquipmentPreview] = useState<EquipmentListPreview | null>(null);
  const [equipmentDrafts, setEquipmentDrafts] = useState<EquipmentOverrideDrafts>({});
  const [acknowledgeExpired, setAcknowledgeExpired] = useState(false);
  const [busyAction, setBusyAction] = useState<BusyAction>("load");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const [nextState, nextReport, nextCustomerReport] = await Promise.all([
      fetchReportWorkspace(projectId),
      fetchCurrentReport(projectId),
      fetchCurrentCustomerReport(projectId),
    ]);
    setState(nextState);
    setCurrentReport(nextReport);
    setCustomerReport(nextCustomerReport);
    return nextState;
  }, [projectId]);

  useEffect(() => {
    let active = true;
    setBusyAction("load");
    setError(null);
    Promise.all([
      fetchReportWorkspace(projectId),
      fetchCurrentReport(projectId),
      fetchCurrentCustomerReport(projectId),
    ])
      .then(([nextState, nextReport, nextCustomerReport]) => {
        if (active) {
          setState(nextState);
          setCurrentReport(nextReport);
          setCustomerReport(nextCustomerReport);
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
  const reportEntry = useMemo(
    () => deriveReportEntryState(currentReport),
    [currentReport]
  );
  const equipmentDraftErrors = useMemo(
    () => equipmentPreview
      ? validateEquipmentOverrideDrafts(equipmentPreview, equipmentDrafts)
      : [],
    [equipmentDrafts, equipmentPreview]
  );

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

  async function handleGenerateCustomerReport(): Promise<void> {
    if (!customerReport?.can_generate || !customerReport.internal_report_sha256) {
      return;
    }
    await runAction("customer", async () => {
      const generated = await generateCurrentCustomerReport(projectId, {
        expected_internal_report_sha256: customerReport.internal_report_sha256!,
        expected_customer_report_sha256: customerReport.file_sha256,
      });
      if (generated.kind === "download") {
        downloadBlob(
          generated.download.blob,
          generated.download.fileName || "Customer Report.docx"
        );
        return "Generated and downloaded the customer report.";
      }
      await refresh();
      if (!customerReport.file_name) {
        return `Generated the customer report (${generated.result.file_name}) in the official project folder.`;
      }
      if (!generated.result.changed) {
        return `The customer report (${generated.result.file_name}) was already current.`;
      }
      return generated.result.archive_path
        ? `Updated the customer report (${generated.result.file_name}). The previous customer report was archived automatically.`
        : `Updated the customer report (${generated.result.file_name}).`;
    });
  }

  async function handleDownloadCustomerReport(): Promise<void> {
    await runAction("customer-download", async () => {
      const response = await downloadCurrentCustomerReport(projectId);
      downloadBlob(
        response.blob,
        response.fileName || customerReport?.file_name || "Customer Report.docx"
      );
      return "Downloaded the current customer report.";
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

  async function handleEquipmentPreview(useDrafts = false): Promise<void> {
    await runAction("equipment-preview", async () => {
      const overrides = useDrafts && equipmentPreview
        ? buildEquipmentExternalOverrides(equipmentPreview, equipmentDrafts)
        : [];
      const result = await previewCurrentReportEquipmentList(projectId, overrides);
      setEquipmentPreview(result);
      setEquipmentDrafts((current) => {
        const created = createEquipmentOverrideDrafts(result);
        return Object.fromEntries(
          Object.entries(created).map(([key, value]) => [key, current[key] ?? value])
        );
      });
      setAcknowledgeExpired(false);
      return result.status === "ready"
        ? `Previewed ${result.rows.length} Equipment List row${result.rows.length === 1 ? "" : "s"}.`
        : null;
    });
  }

  async function handleEquipmentUpdate(): Promise<void> {
    if (
      !equipmentPreview
      || !equipmentPreview.current_report.file_sha256
      || !equipmentPreview.source_sha256
      || !equipmentPreview.catalog_sha256
    ) {
      return;
    }
    await runAction("equipment-update", async () => {
      const result = await updateCurrentReportEquipmentList(projectId, {
        expected_report_sha256: equipmentPreview.current_report.file_sha256!,
        expected_source_sha256: equipmentPreview.source_sha256!,
        expected_catalog_sha256: equipmentPreview.catalog_sha256!,
        acknowledge_expired: acknowledgeExpired,
        external_overrides: buildEquipmentExternalOverrides(
          equipmentPreview,
          equipmentDrafts
        ),
        updated_by: "Lab User",
      });
      setEquipmentPreview(null);
      setEquipmentDrafts({});
      setAcknowledgeExpired(false);
      await refresh();
      return result.changed
        ? `Updated Equipment List in ${result.file_name}. The previous report was archived automatically.`
        : `Equipment List in ${result.file_name} was already up to date.`;
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
      return `Published the current report to the official project folder (${published.file_name}).`;
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
            <small>{reportEntry.statusLabel}</small>
          </div>
        ) : null}
      </header>

      {error ? <ErrorMessage message={error} /> : null}
      {message ? <p className="report-workspace-message" role="status">{message}</p> : null}

      {state && readiness ? (
        <div className="report-workspace-grid">
          <article className="report-workspace-card report-workspace-card-wide">
            <div className="report-workspace-card-heading">
              <span className="report-workspace-step">01</span>
              <div><h2>{reportEntry.title}</h2><p>{reportEntry.description}</p></div>
            </div>
            <div className="report-workspace-current-report">
              <span className={`report-workspace-status report-workspace-status-${reportEntry.kind}`}>
                {reportEntry.statusLabel}
              </span>
              {currentReport?.file_name ? <strong>{currentReport.file_name}</strong> : null}
              {reportEntry.locationLabel ? <small>{reportEntry.locationLabel}</small> : null}
            </div>
            <div className="report-workspace-action-row">
              {reportEntry.kind === "generate" ? (
                <button
                  className="primary-action"
                  disabled={!readiness.canGenerateInitialDraft || Boolean(busyAction)}
                  onClick={() => void runAction("initial", async () => {
                    const revision = await generateInitialReportRevision(projectId);
                    await refresh();
                    return `Generated the initial internal report (${revision.file_name}).`;
                  })}
                  type="button"
                >
                  {busyAction === "initial" ? "Generating..." : "Generate initial report"}
                </button>
              ) : null}
              {reportEntry.kind === "publish" ? (
                <button
                  className="primary-action"
                  disabled={Boolean(busyAction)}
                  onClick={() => void handlePublishManagedReport()}
                  type="button"
                >
                  {busyAction === "publish" ? "Publishing..." : "Publish current draft to project folder"}
                </button>
              ) : null}
              {currentReport?.status === "ready" ? (
                <button disabled={Boolean(busyAction)} onClick={() => void handleDownloadCurrent()} type="button">Download current report</button>
              ) : null}
            </div>
            {reportEntry.kind === "generate" && readiness.initialDraftBlocker ? <p className="report-workspace-blocker">{readiness.initialDraftBlocker}</p> : null}
            {reportEntry.kind === "ready" ? <p className="report-workspace-note">Use the section actions below to update test results while preserving manual edits.</p> : null}
            {reportEntry.kind === "managed" ? <p className="report-workspace-note">Create the official project folder before publishing this draft.</p> : null}
            {reportEntry.kind === "blocked" ? <p className="report-workspace-blocker">Multiple internal reports were found. Resolve that conflict before creating or updating a report.</p> : null}
          </article>

          <article className="report-workspace-card report-workspace-card-wide">
            <div className="report-workspace-card-heading">
              <span className="report-workspace-step">02</span>
              <div>
                <h2>Customer report</h2>
                <p>Generate the controlled E-4515_F customer projection from the current Internal Report. Internal-only detail and appendices are excluded.</p>
              </div>
            </div>
            <div className="report-workspace-current-report">
              <span className={`report-workspace-status report-workspace-status-${customerReportStatusTone(customerReport)}`}>
                {customerReportStatusLabel(customerReport)}
              </span>
              {customerReport?.file_name ? <strong>{customerReport.file_name}</strong> : null}
              <small>
                {customerReport?.mode === "official"
                  ? "Same folder as the current Internal Report"
                  : "Browser download (no official project folder)"}
              </small>
            </div>
            {customerReport?.warnings.map((warning) => (
              <p className="report-workspace-warning" key={warning}>{warning}</p>
            ))}
            {customerReport?.blockers.map((blocker) => (
              <p className="report-workspace-blocker" key={blocker}>{blocker}</p>
            ))}
            <div className="report-workspace-action-row">
              <button
                className="primary-action"
                disabled={!customerReport?.can_generate || Boolean(busyAction)}
                onClick={() => void handleGenerateCustomerReport()}
                type="button"
              >
                {busyAction === "customer"
                  ? "Generating customer report..."
                  : customerReport?.mode === "managed_download"
                    ? "Generate and download customer report"
                    : customerReport?.file_name
                      ? "Update customer report"
                      : "Generate customer report"}
              </button>
              {customerReport?.download_url ? (
                <button
                  disabled={Boolean(busyAction)}
                  onClick={() => void handleDownloadCustomerReport()}
                  type="button"
                >Download customer report</button>
              ) : null}
            </div>
            <div className="report-workspace-owned-regions" aria-label="Customer report projection boundary">
              <strong>Source authority</strong>
              <span>Current Internal Report only</span>
              <small>An existing customer report is archived before a successful replacement. It is never used as the generation source.</small>
            </div>
          </article>

          <article className="report-workspace-card">
            <div className="report-workspace-card-heading">
              <span className="report-workspace-step">03</span>
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
              <span className="report-workspace-step">04</span>
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
            <div className="report-workspace-owned-regions" aria-label="Update boundary">
              <strong>This action owns</strong>
              <span>LLCR Result and Comment cells only</span>
              <small>Manually edited Purpose and Conclusions are preserved.</small>
            </div>
          </article>

          <article className="report-workspace-card report-workspace-card-wide">
            <div className="report-workspace-card-heading">
              <span className="report-workspace-step">05</span>
              <div>
                <h2>Update Equipment List</h2>
                <p>Read EquipmentID.docx from the project folder and match it to the active Equipment calibration Excel configured in Settings.</p>
              </div>
            </div>
            <button
              className="primary-action"
              disabled={Boolean(busyAction) || currentReport?.status !== "ready"}
              onClick={() => void handleEquipmentPreview()}
              type="button"
            >
              {busyAction === "equipment-preview" ? "Previewing..." : "Preview Equipment List"}
            </button>
            {currentReport?.status !== "ready" ? (
              <p className="report-workspace-blocker">Generate or publish the current report before updating Equipment List.</p>
            ) : null}
            <div className="report-workspace-owned-regions" aria-label="Equipment update boundary">
              <strong>This action owns</strong>
              <span>Section 7 Equipment table body only</span>
              <small>Purpose, Conclusions, results, images, appendices, and other manual edits are preserved.</small>
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

      {equipmentPreview ? (
        <div className="report-workspace-dialog-backdrop">
          <section
            aria-label="Equipment List preview"
            aria-modal="true"
            className="report-workspace-dialog"
            role="dialog"
          >
            <header className="report-workspace-dialog-header">
              <div>
                <h2>Equipment List preview</h2>
                <p>Review every matched or external row before replacing the Section 7 table body.</p>
              </div>
              <button
                disabled={Boolean(busyAction)}
                onClick={() => {
                  setEquipmentPreview(null);
                  setEquipmentDrafts({});
                  setAcknowledgeExpired(false);
                }}
                type="button"
              >Close</button>
            </header>
            <dl className="report-workspace-preview-facts">
              <div><dt>Selection source</dt><dd>{equipmentPreview.source_file_name ?? "Unavailable"}</dd></div>
              <div><dt>Calibration source</dt><dd>{equipmentPreview.catalog_file_name ?? "Unavailable"}</dd></div>
              <div><dt>Rows</dt><dd>{equipmentPreview.rows.length}</dd></div>
              <div><dt>Preview status</dt><dd>{equipmentPreview.status === "ready" ? "Ready to update" : "Needs attention"}</dd></div>
            </dl>
            {equipmentPreview.blockers.length ? (
              <div className="report-workspace-confirm-errors">
                {equipmentPreview.blockers.map((item) => <p key={item}>{item}</p>)}
              </div>
            ) : null}
            {equipmentPreview.warnings.length ? (
              <div className="report-workspace-diagnostics">
                {equipmentPreview.warnings.map((item) => <p key={item}>{item}</p>)}
              </div>
            ) : null}
            <div className="report-workspace-table-wrap">
              <table className="report-workspace-table report-workspace-equipment-table">
                <thead><tr>
                  <th>Source reference</th><th>Item</th><th>Manufacturer</th><th>ID Number</th><th>Last Cal.</th><th>Cal. Due</th><th>Status</th>
                </tr></thead>
                <tbody>
                  {equipmentPreview.rows.map((row) => {
                    const draft = equipmentDrafts[row.source_reference];
                    const editable = (row.status === "unmatched" || row.status === "external") && draft;
                    return (
                      <tr key={row.source_reference}>
                        <td>{row.source_reference}</td>
                        <td>{editable ? <EquipmentInput label={`Item for ${row.source_reference}`} value={draft.item} onChange={(value) => updateEquipmentDraft(setEquipmentDrafts, row.source_reference, "item", value)} /> : row.item}</td>
                        <td>{editable ? <EquipmentInput label={`Manufacturer for ${row.source_reference}`} value={draft.manufacturer} onChange={(value) => updateEquipmentDraft(setEquipmentDrafts, row.source_reference, "manufacturer", value)} /> : row.manufacturer}</td>
                        <td>{editable ? <EquipmentInput label={`ID Number for ${row.source_reference}`} value={draft.idNumber} onChange={(value) => updateEquipmentDraft(setEquipmentDrafts, row.source_reference, "idNumber", value)} /> : row.id_number}</td>
                        <td>{editable ? <EquipmentInput label={`Last calibration for ${row.source_reference}`} value={draft.lastCalibration} onChange={(value) => updateEquipmentDraft(setEquipmentDrafts, row.source_reference, "lastCalibration", value)} /> : row.last_calibration}</td>
                        <td>{editable ? <EquipmentInput label={`Calibration due for ${row.source_reference}`} value={draft.calibrationDue} onChange={(value) => updateEquipmentDraft(setEquipmentDrafts, row.source_reference, "calibrationDue", value)} /> : row.calibration_due}</td>
                        <td>
                          <span className={`report-workspace-equipment-status ${row.status}`}>{equipmentStatusLabel(row.status)}</span>
                          {row.expired ? <small>Expired</small> : null}
                          {editable ? <EquipmentInput label={`Explanation for ${row.source_reference}`} value={draft.reason} onChange={(value) => updateEquipmentDraft(setEquipmentDrafts, row.source_reference, "reason", value)} /> : null}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {equipmentDraftErrors.length ? (
              <div className="report-workspace-confirm-errors">
                {equipmentDraftErrors.map((item) => <p key={item}>{item}</p>)}
              </div>
            ) : null}
            {equipmentPreview.requires_expired_acknowledgement ? (
              <label className="report-workspace-equipment-ack">
                <input
                  checked={acknowledgeExpired}
                  onChange={(event) => setAcknowledgeExpired(event.target.checked)}
                  type="checkbox"
                />
                I reviewed the expired calibration warning
              </label>
            ) : null}
            <div className="report-workspace-dialog-actions">
              {equipmentPreview.rows.some((row) => row.status === "unmatched") ? (
                <button
                  disabled={Boolean(busyAction) || equipmentDraftErrors.length > 0}
                  onClick={() => void handleEquipmentPreview(true)}
                  type="button"
                >{busyAction === "equipment-preview" ? "Rechecking..." : "Recheck external entries"}</button>
              ) : null}
              <button
                className="primary-action"
                disabled={
                  Boolean(busyAction)
                  || equipmentPreview.status !== "ready"
                  || equipmentDraftErrors.length > 0
                  || (equipmentPreview.requires_expired_acknowledgement && !acknowledgeExpired)
                }
                onClick={() => void handleEquipmentUpdate()}
                type="button"
              >{busyAction === "equipment-update" ? "Updating..." : "Update Equipment List"}</button>
            </div>
          </section>
        </div>
      ) : null}
    </section>
  );
}

function formatDateTime(value: string): string {
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

function customerReportStatusLabel(state: CustomerReportState | null): string {
  if (!state) return "Checking status";
  if (state.status === "ready") return "Current";
  if (state.status === "stale") return "Needs update";
  if (state.status === "untracked") return "Lineage not recorded";
  if (state.status === "missing") return "Not generated";
  if (state.status === "ambiguous") return "Multiple reports found";
  return "Blocked";
}

function customerReportStatusTone(
  state: CustomerReportState | null
): "ready" | "publish" | "generate" | "blocked" {
  if (!state || state.status === "blocked" || state.status === "ambiguous") {
    return "blocked";
  }
  if (state.status === "ready") return "ready";
  if (state.status === "missing") return "generate";
  return "publish";
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

function EquipmentInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}): ReactElement {
  return (
    <label className="report-workspace-equipment-input">
      <span>{label}</span>
      <input
        aria-label={label}
        onChange={(event) => onChange(event.target.value)}
        value={value}
      />
    </label>
  );
}

function updateEquipmentDraft(
  setDrafts: Dispatch<SetStateAction<EquipmentOverrideDrafts>>,
  sourceReference: string,
  field: keyof EquipmentOverrideDrafts[string],
  value: string
): void {
  setDrafts((current) => ({
    ...current,
    [sourceReference]: {
      ...current[sourceReference],
      [field]: value,
    },
  }));
}

function equipmentStatusLabel(status: EquipmentListPreview["rows"][number]["status"]): string {
  if (status === "matched") return "Matched";
  if (status === "external") return "External";
  if (status === "ambiguous") return "Ambiguous";
  if (status === "incomplete") return "Incomplete";
  return "Not found";
}
