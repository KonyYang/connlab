import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactElement,
} from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import {
  cancelLlcrResultPreview,
  confirmLlcrResultImport,
  downloadCurrentReport,
  fetchCurrentCustomerReport,
  fetchCurrentReport,
  fetchReportWorkspace,
  generateInternalReport,
  previewInternalReportGeneration,
  openLocalProjectFolder,
  getPublicFolderWorkflowContext,
  inspectLlcrResultWorkbook,
  isCustomerReportMissingAfterPreviewError,
  publishManagedReport,
  previewCurrentReportLlcrUpdate,
  updateCurrentReportLlcr,
  updateEquipmentListOneClick,
  type CurrentReport,
  type CustomerReportState,
  type EquipmentListOneClickResult,
  type LlcrImportPreview,
  type ReportWorkspaceState,
  type InternalReportGenerationPreview,
} from "../../api/client";
import { ErrorMessage } from "../../components/common/ErrorMessage";
import { CustomerReportProgress } from "../../components/common/CustomerReportProgress";
import { useCustomerReportJob } from "./useCustomerReportJob";
import { useUploadedCustomerReportJob } from "./useUploadedCustomerReportJob";
import { CustomerReportSourceDialog } from "./CustomerReportSourceDialog";
import { CustomerReportRegenerationDialog } from "./CustomerReportRegenerationDialog";
import { LlcrImportPreviewDialog } from "./LlcrImportPreviewDialog";
import {
  buildLlcrConfirmationDecisions,
  buildEquipmentSelectionInput,
  createLlcrDecisionDrafts,
  deriveReportEntryState,
  deriveReportWorkspaceReadiness,
  type LlcrDecisionDrafts,
  type LlcrOutcome,
} from "./reportWorkspaceModel";

type ReportWorkspaceProps = {
  projectId: string;
  onBack: () => void;
  identityLabel?: string;
};

type BusyAction = "load" | "initial" | "open-folder" | "inspect" | "confirm" | "cancel" | "llcr" | "equipment-update" | "publish" | "download" | "customer" | "customer-source" | null;

type ProjectFolderAvailability = {
  projectId: string;
  status: "checking" | "available" | "missing" | "unavailable" | "failed";
  reason?: string;
};

type CustomerRegenerationApproval = {
  projectId: string;
  internalSha: string;
  customerSha: string | null;
  fileName: string | null;
  returnFocusTarget: HTMLButtonElement;
};

export function ReportWorkspace({ projectId, onBack, identityLabel = "Connector Project" }: ReportWorkspaceProps): ReactElement {
  const topBarRoot = useTopBarActionsRoot();
  const [state, setState] = useState<ReportWorkspaceState | null>(null);
  const [currentReport, setCurrentReport] = useState<CurrentReport | null>(null);
  const [customerReport, setCustomerReport] = useState<CustomerReportState | null>(null);
  const [customerReportRecovery, setCustomerReportRecovery] = useState<CustomerReportState | null>(null);
  const [customerRegenerationApproval, setCustomerRegenerationApproval] = useState<CustomerRegenerationApproval | null>(null);
  const customerRequest = useRef(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<LlcrImportPreview | null>(null);
  const [decisionDrafts, setDecisionDrafts] = useState<LlcrDecisionDrafts>({});
  const [equipmentSourceOpen, setEquipmentSourceOpen] = useState(false);
  const [equipmentFile, setEquipmentFile] = useState<File | null>(null);
  const [equipmentIds, setEquipmentIds] = useState("");
  const [equipmentResult, setEquipmentResult] = useState<Extract<EquipmentListOneClickResult, { status: "completed" }> | null>(null);
  const equipmentRequest = useRef(false);
  const equipmentSequence = useRef(0);
  const equipmentTrigger = useRef<HTMLButtonElement>(null);
  const [pageBusyAction, setBusyAction] = useState<BusyAction>("load");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [internalGenerationPreview, setInternalGenerationPreview] = useState<InternalReportGenerationPreview | null>(null);
  const [folderAvailability, setFolderAvailability] = useState<ProjectFolderAvailability | null>(null);
  const [sourcePickerOpen, setSourcePickerOpen] = useState(false);
  const [checkingSource, setCheckingSource] = useState(false);
  const sourceRequest = useRef(false);
  const mounted = useRef(true);
  const internalRequest = useRef(0);
  const customerJob = useCustomerReportJob(projectId, (response) => {
    downloadBlob(response.blob, response.fileName || "Customer Report.docx");
  });
  const uploadedCustomerJob = useUploadedCustomerReportJob(projectId, (response) => {
    downloadBlob(response.blob, response.fileName || "Customer Report.docx");
  });
  const busyAction = pageBusyAction ?? (customerJob.busy || uploadedCustomerJob.busy ? "customer" : sourcePickerOpen || customerRegenerationApproval || equipmentSourceOpen || equipmentResult ? "customer-source" : null);
  const customerRun = useRef<{ regenerating: boolean; hadFile: boolean } | null>(null);
  const activeProject = useRef(projectId);
  activeProject.current = projectId;

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; internalRequest.current += 1; equipmentSequence.current += 1; };
  }, []);

  useEffect(() => {
    internalRequest.current += 1;
    setInternalGenerationPreview(null);
    setMessage(null);
    setSourcePickerOpen(false);
    setCheckingSource(false);
    sourceRequest.current = false;
    customerRequest.current = false;
    customerRun.current = null;
    setCustomerRegenerationApproval(null);
    equipmentSequence.current += 1;
    equipmentRequest.current = false;
    setEquipmentSourceOpen(false);
    setEquipmentResult(null);
    setEquipmentFile(null);
    setEquipmentIds("");
  }, [projectId]);

  useEffect(() => {
    let active = true;
    setFolderAvailability({ projectId, status: "checking" });
    void getPublicFolderWorkflowContext(projectId).then((context) => {
      if (active && mounted.current && activeProject.current === projectId) {
        setFolderAvailability({ projectId, status: context.local_official_folder_available ? "available"
          : context.local_official_folder_path ? "unavailable" : "missing" });
      }
    }).catch(() => {
      if (active && mounted.current && activeProject.current === projectId) {
        setFolderAvailability({ projectId, status: "failed" });
      }
    });
    return () => { active = false; };
  }, [projectId]);

  useEffect(() => {
    if (!message || (message !== "Generated the Internal Report." && !/^(Generated|Updated|The) .*customer report/.test(message))) return;
    const timer = window.setTimeout(() => setMessage(null), 5000);
    return () => window.clearTimeout(timer);
  }, [message]);

  const refresh = useCallback(async () => {
    const [nextState, nextReport, nextCustomerReport] = await Promise.all([
      fetchReportWorkspace(projectId),
      fetchCurrentReport(projectId),
      fetchCurrentCustomerReport(projectId),
    ]);
    if (mounted.current && activeProject.current === projectId) {
      setState(nextState);
      setCurrentReport(nextReport);
      setCustomerReport(nextCustomerReport);
    }
    return { state: nextState, customerReport: nextCustomerReport };
  }, [projectId]);

  useEffect(() => {
    const job = customerJob.job;
    if (!job || job.project_id !== projectId || (job.status !== "completed" && job.status !== "failed")) return;
    let active = true;
    if (job.status === "failed" && job.error_code !== "customer_report_missing_after_preview") return;
    void refresh().then(({ customerReport: next }) => {
      if (!active) return;
      if (job.status === "failed") {
        if (job.can_regenerate && next.status === "missing" && next.mode === "official" && next.can_generate && next.internal_report_sha256) {
          setCustomerReportRecovery(next);
        } else {
          setError("The customer report state changed again. Review the current state before continuing.");
        }
        return;
      }
      const result = job.result;
      if (result?.mode !== "official") return;
      if (!customerRun.current) return;
      if (customerRun.current.regenerating) {
        setMessage("Generated a new customer report. No previous file was archived.");
      } else if (!result.changed) {
        setMessage("The customer report was already current.");
      } else if (!customerRun.current.hadFile) {
        setMessage("Generated the customer report.");
      } else {
        setMessage(`Updated the customer report.${result.archive_path ? " The previous customer report was archived automatically." : ""}`);
      }
      customerRun.current = null;
    }).catch((reason: unknown) => {
      if (active) setError(errorMessage(reason, "Unable to refresh report status. The generation result is retained; reload to check it."));
    });
    return () => { active = false; };
  }, [customerJob.job, projectId, refresh]);

  useEffect(() => {
    let active = true;
    setBusyAction("load");
    setError(null);
    setCustomerReportRecovery(null);
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
  const reportFileName = currentReport?.status === "ready" ? currentReport.file_name : null;

  async function handleInternalAction(action: "initial" | "open-folder", operation: (isCurrent: () => boolean) => Promise<void>): Promise<void> {
    if (busyAction) return;
    const request = ++internalRequest.current;
    const isCurrent = () => mounted.current && activeProject.current === projectId && request === internalRequest.current;
    setBusyAction(action);
    setError(null);
    setMessage(null);
    try {
      await operation(isCurrent);
    } catch (reason) {
      if (isCurrent()) {
        setInternalGenerationPreview(null);
        setError(errorMessage(reason, "Unable to generate the Internal Report. Review the current report and preview again."));
      }
    } finally {
      if (isCurrent()) setBusyAction(null);
    }
  }

  async function performInternalGeneration(preview: InternalReportGenerationPreview, isCurrent: () => boolean): Promise<void> {
    if (!preview.preview_token || !isCurrent()) return;
    await generateInternalReport(projectId, preview.preview_token, preview.requires_confirmation);
    if (!isCurrent()) return;
    setInternalGenerationPreview(null);
    await refresh();
    if (isCurrent()) setMessage("Generated the Internal Report.");
  }

  async function handleGenerateInternalReport(): Promise<void> {
    await handleInternalAction("initial", async (isCurrent) => {
      const preview = await previewInternalReportGeneration(projectId);
      if (!isCurrent()) return;
      if (preview.status !== "ready" || !preview.preview_token) {
        setError(preview.blockers.join(" ") || "Resolve the report prerequisites and preview again.");
      } else if (preview.requires_confirmation) {
        setInternalGenerationPreview(preview);
      } else {
        await performInternalGeneration(preview, isCurrent);
      }
    });
  }
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

  async function handleGenerateCustomerReport(trigger: HTMLButtonElement): Promise<void> {
    if (!busyAction && !customerReportRecovery && currentReport?.status === "missing") {
      setError(null);
      setSourcePickerOpen(true);
      return;
    }
    if (
      busyAction ||
      customerReportRecovery ||
      !customerReport?.can_generate ||
      !customerReport.internal_report_sha256
    ) {
      return;
    }
    const approval = {
      projectId,
      internalSha: customerReport.internal_report_sha256,
      customerSha: customerReport.file_sha256,
      fileName: customerReport.file_name,
      returnFocusTarget: trigger,
    };
    if (approval.fileName) {
      if (!approval.customerSha) {
        setError("The customer report state is incomplete. Reload the latest report before generating.");
        return;
      }
      setError(null);
      setCustomerRegenerationApproval(approval);
      return;
    }
    await performCustomerGeneration(approval);
  }

  async function performCustomerGeneration(approval: CustomerRegenerationApproval): Promise<void> {
    if (customerRequest.current || customerJob.busy || approval.projectId !== activeProject.current) return;
    customerRequest.current = true;
    const token = internalRequest.current;
    const isCurrent = () => mounted.current && activeProject.current === approval.projectId && internalRequest.current === token;
    setBusyAction("customer");
    setError(null);
    setMessage(null);
    try {
      customerRun.current = { regenerating: false, hadFile: Boolean(approval.fileName) };
      await customerJob.start({
        expected_internal_report_sha256: approval.internalSha,
        expected_customer_report_sha256: approval.customerSha,
      });
      if (isCurrent()) setCustomerRegenerationApproval(null);
    } catch (reason) {
      if (!isCurrent()) return;
      setCustomerRegenerationApproval(null);
      if (isCustomerReportMissingAfterPreviewError(reason)) {
        try {
          const refreshed = await refresh();
          if (!isCurrent()) return;
          if (
            refreshed.customerReport.status === "missing" &&
            refreshed.customerReport.mode === "official" &&
            refreshed.customerReport.can_generate &&
            refreshed.customerReport.internal_report_sha256
          ) {
            setCustomerReportRecovery(refreshed.customerReport);
          } else {
            setError(
              "The customer report state changed again. Review the current state before continuing."
            );
          }
        } catch (refreshReason) {
          if (isCurrent()) setError(errorMessage(refreshReason, "Unable to refresh the customer report state."));
        }
      } else {
        setError(errorMessage(reason, "Unable to generate the customer report."));
      }
    } finally {
      if (isCurrent()) { customerRequest.current = false; setBusyAction(null); }
    }
  }

  async function handleGenerateFromUploadedSource(file: File): Promise<boolean> {
    if (sourceRequest.current || uploadedCustomerJob.busy) return false;
    sourceRequest.current = true;
    setCheckingSource(true);
    const token = internalRequest.current;
    const isCurrent = () => mounted.current && activeProject.current === projectId && internalRequest.current === token;
    try {
      // The report may have appeared since the picker opened. Never silently replace the default source.
      const latest = await fetchCurrentReport(projectId);
      if (!isCurrent()) return false;
      if (latest.status !== "missing") {
        await refresh();
        if (isCurrent()) {
          setSourcePickerOpen(false);
          setError("The current Internal Report changed. Review the current report before generating.");
        }
        return false;
      }
      const started = await uploadedCustomerJob.start(file);
      if (isCurrent() && started) setSourcePickerOpen(false);
      return started;
    } catch (reason) {
      if (isCurrent()) setError(errorMessage(reason, "Unable to check the current Internal Report. Try again."));
      return false;
    } finally {
      if (isCurrent()) { sourceRequest.current = false; setCheckingSource(false); }
    }
  }

  async function handleConfirmCustomerReportRegeneration(): Promise<void> {
    const recovery = customerReportRecovery;
    if (busyAction || !recovery?.internal_report_sha256) {
      return;
    }
    setBusyAction("customer");
    setError(null);
    setMessage(null);
    try {
      customerRun.current = { regenerating: true, hadFile: false };
      await customerJob.start({
        expected_internal_report_sha256: recovery.internal_report_sha256,
        expected_customer_report_sha256: null,
      });
      setCustomerReportRecovery(null);
    } catch (reason) {
      setError(errorMessage(reason, "Unable to regenerate the customer report."));
    } finally {
      setBusyAction(null);
    }
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

  async function handleEquipmentUpdate(input?: { file?: File; referencesText?: string }): Promise<void> {
    if (equipmentRequest.current || pageBusyAction || customerJob.busy || uploadedCustomerJob.busy) return;
    equipmentRequest.current = true;
    const sequence = ++equipmentSequence.current;
    const isCurrent = () => mounted.current && activeProject.current === projectId && equipmentSequence.current === sequence;
    setBusyAction("equipment-update");
    setError(null);
    setMessage(null);
    try {
      const result = await updateEquipmentListOneClick(projectId, input);
      if (!isCurrent()) return;
      if (result.status === "source_required") {
        setEquipmentSourceOpen(true);
        return;
      }
      setEquipmentSourceOpen(false);
      setEquipmentFile(null);
      setEquipmentIds("");
      setEquipmentResult(result);
      try { await refresh(); }
      catch { if (isCurrent()) setError("Equipment List was updated. Reload to refresh report status."); }
    } catch (reason) {
      if (isCurrent()) {
        if (input) setEquipmentSourceOpen(false);
        setError(errorMessage(reason, "Unable to update Equipment List. Check the selection file, calibration workbook and report access, then retry."));
      }
    } finally {
      if (isCurrent()) { equipmentRequest.current = false; setBusyAction(null); }
    }
  }

  function handleEquipmentSelection(): void {
    try {
      const input = buildEquipmentSelectionInput(equipmentFile, equipmentIds);
      if (input) void handleEquipmentUpdate(input);
    } catch (reason) {
      setError(errorMessage(reason, "Choose a .docx document or paste equipment IDs."));
    }
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

  const folderStatus = folderAvailability?.projectId === projectId ? folderAvailability.status : "checking";
  const folderDisabledReason = folderStatus === "checking" ? "Checking project folder availability..."
    : folderStatus === "failed" ? "Unable to check the project folder. Return to Workspace and retry."
    : folderStatus === "missing" ? "No project folder is linked. Create or link it in Workspace."
    : folderStatus === "unavailable" ? folderAvailability?.reason || "The project folder is unavailable. Restore or link it in Workspace."
    : busyAction ? busyAction === "open-folder" ? "Opening project folder..." : "Wait for the current operation to finish."
    : undefined;

  const commandbar = (
    <div className="report-workspace-commandbar" aria-label="Report Workspace actions">
      <span className="report-workspace-identity" title={identityLabel}>{identityLabel}</span>
      <div className="report-workspace-header-actions">
        <span className="report-workspace-folder-action" title={folderDisabledReason} tabIndex={folderDisabledReason ? 0 : undefined}>
          <button className="report-workspace-back" disabled={Boolean(folderDisabledReason)} onClick={() => void handleInternalAction("open-folder", async (isCurrent) => {
            try {
              const result = await openLocalProjectFolder(projectId);
              if (isCurrent() && result.status !== "opened") {
                const reason = result.message || "Unable to open the project folder. Check its location and try again.";
                setFolderAvailability({ projectId, status: "unavailable", reason });
                setError(reason);
              }
            } catch (reason) {
              if (isCurrent()) setError(errorMessage(reason, "Unable to open the project folder. Check its location and try again."));
            }
          })} type="button">Open project folder</button>
        </span>
        <button className="report-workspace-back" onClick={onBack} type="button">Back to Workspace</button>
      </div>
    </div>
  );

  return (
    <section className="report-workspace-page" aria-busy={!state && busyAction === "load" && !error}>
      {topBarRoot ? createPortal(commandbar, topBarRoot) : (
        <header className="report-workspace-header">
          <h1>Report Workspace</h1>
          {commandbar}
        </header>
      )}
      {!state && busyAction === "load" && !error ? <div className="panel" role="status">Loading Report Workspace...</div> : null}
      {error ? <ErrorMessage message={error} /> : null}
      {message ? <p className="report-workspace-message" role="status">{message}</p> : null}

      {state && readiness ? (
        <div className="report-workspace-grid">
          <section className="report-workspace-card report-workspace-generation" aria-label="Report generation">
            <section aria-label="Internal Report">
              <div className="report-workspace-report-row report-workspace-initial-report">
                <div className="report-workspace-action-row">
                  <button
                    className="primary-action"
                    disabled={!readiness.canGenerateInitialDraft || reportEntry.kind === "blocked" || Boolean(busyAction)}
                    onClick={() => void handleGenerateInternalReport()}
                    type="button"
                  >
                    {busyAction === "initial" ? "Generating..." : "Generate Internal Report"}
                  </button>
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
                  {currentReport?.status === "ready" && currentReport.mode !== "official" ? (
                    <button disabled={Boolean(busyAction)} onClick={() => void handleDownloadCurrent()} type="button">Download current report</button>
                  ) : null}
                </div>
                <div className="report-workspace-current-report">
                  {reportFileName ? <span className="report-workspace-report-name">{reportFileName}</span> : (
                    <span className={`report-workspace-status report-workspace-status-${reportEntry.kind}`}>{reportEntry.statusLabel}</span>
                  )}
                </div>
              </div>
              {readiness.initialDraftBlocker ? <p className="report-workspace-blocker">{readiness.initialDraftBlocker}</p> : null}
              {reportEntry.kind === "managed" ? <p className="report-workspace-note">Create the official project folder before publishing this draft.</p> : null}
              {reportEntry.kind === "blocked" ? <p className="report-workspace-blocker">Multiple internal reports were found. Resolve that conflict before creating or updating a report.</p> : null}
            </section>
            <section className="report-workspace-customer-generation" aria-label="Customer Report">
              <div className="report-workspace-action-row">
                <button
                  className="primary-action"
                  disabled={
                    (currentReport?.status !== "missing" && !customerReport?.can_generate) ||
                    Boolean(busyAction) ||
                    customerJob.downloading ||
                    Boolean(customerReportRecovery)
                  }
                  onClick={(event) => void handleGenerateCustomerReport(event.currentTarget)}
                  type="button"
                >
                  {busyAction === "customer" ? "Generating customer report..." : "Generate customer report"}
                </button>
                {customerJob.job?.status === "completed" && customerJob.job.result?.mode === "managed_download" ? (
                  <button type="button" disabled={customerJob.downloading || Boolean(busyAction)} onClick={() => void customerJob.download()}>
                    {customerJob.downloading ? "Downloading..." : customerJob.downloadError ? "Retry download" : "Download generated copy"}
                  </button>
                ) : null}
              </div>
              {uploadedCustomerJob.fileName || customerReport?.file_name || customerJob.job?.result?.file_name ? <span className="report-workspace-report-name">
                {uploadedCustomerJob.fileName || customerReport?.file_name || customerJob.job?.result?.file_name}
              </span> : null}
              {uploadedCustomerJob.fileName ? <small className="report-workspace-note">Downloaded copy · selected Internal Report</small> : null}
              {customerReport?.warnings.map((warning) => (
                <p className="report-workspace-warning" key={warning}>{warning}</p>
              ))}
              {currentReport?.status !== "missing" ? customerReport?.blockers.map((blocker) => (
                <p className="report-workspace-blocker" key={blocker}>{blocker}</p>
              )) : null}
              {uploadedCustomerJob.job?.status === "queued" || uploadedCustomerJob.job?.status === "running" ? <CustomerReportProgress stage={uploadedCustomerJob.job.stage}
                elapsedSeconds={uploadedCustomerJob.job.elapsed_seconds} running={uploadedCustomerJob.busy} /> : null}
              {uploadedCustomerJob.error ? <p role="alert" className="report-workspace-blocker">{uploadedCustomerJob.error}</p> : null}
              {uploadedCustomerJob.job?.status === "failed" ? <p role="alert" className="report-workspace-blocker">
                {uploadedCustomerJob.job.message || "Unable to generate the customer report. Select the source and try again."}
              </p> : null}
              {uploadedCustomerJob.queryWarning ? <div role="alert" className="report-workspace-warning">
                <p>{uploadedCustomerJob.queryWarning}</p>
                <button type="button" onClick={() => void uploadedCustomerJob.retryQuery()}>Retry status check</button>
              </div> : null}
              {uploadedCustomerJob.downloadError ? <div role="alert" className="report-workspace-blocker">
                <p>{uploadedCustomerJob.downloadError}</p>
                <button type="button" disabled={uploadedCustomerJob.busy} onClick={() => void uploadedCustomerJob.retryDownload()}>Retry download</button>
              </div> : null}
              {customerJob.job?.status === "queued" || customerJob.job?.status === "running" ? <CustomerReportProgress
                stage={customerJob.job.stage}
                elapsedSeconds={customerJob.elapsed}
                running={customerJob.job.status === "queued" || customerJob.job.status === "running"}
              /> : null}
              {customerJob.error ? <p role="alert" className="report-workspace-blocker">{customerJob.error}</p> : null}
              {customerJob.queryWarning ? <div role="alert" className="report-workspace-warning">
                <p>{customerJob.queryWarning}</p>
                <button type="button" onClick={() => void customerJob.retryQuery()}>Retry status check</button>
              </div> : null}
              {customerJob.job?.status === "failed" && customerJob.job.error_code !== "customer_report_missing_after_preview" ?
                <p role="alert" className="report-workspace-blocker">
                  {customerJob.job.error_code === "customer_report_publication_failed" ? "Publication failed: " : "Generation failed: "}
                  {customerJob.job.message || "Unable to generate the customer report."}
                </p> : null}
              {customerJob.downloadError ? <p role="alert" className="report-workspace-blocker">{customerJob.downloadError}</p> : null}
              {customerReportRecovery ? (
                <div
                  aria-labelledby="customer-report-recovery-title"
                  className="report-workspace-owned-regions"
                  role="alertdialog"
                >
                  <strong id="customer-report-recovery-title">Customer report not found</strong>
                  <span>
                    The customer report was deleted or moved from the project folder. Generate a new
                    report from the current Internal Report?
                  </span>
                  <small>No previous file exists, so no History copy will be created.</small>
                  <div className="report-workspace-action-row">
                    <button
                      autoFocus
                      className="primary-action"
                      disabled={Boolean(busyAction)}
                      onClick={() => void handleConfirmCustomerReportRegeneration()}
                      type="button"
                    >
                      {busyAction === "customer"
                        ? "Generating customer report..."
                        : "Generate new customer report"}
                    </button>
                    <button
                      disabled={Boolean(busyAction)}
                      onClick={() => setCustomerReportRecovery(null)}
                      type="button"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : null}
            </section>
          </section>

          <section className="report-workspace-card" aria-label="Update Internal Report">
            <div className="report-workspace-card-heading">
              <div><h2>Update Internal Report</h2><p>Update selected sections; other content and manual edits are preserved.</p></div>
            </div>
            <div className="report-workspace-update-row">
              <div className="report-workspace-update-content">
                <h3>LLCR results</h3>
                <div className="report-workspace-import-row">
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
                </div>
                {latestDataset ? (
                  <p className="report-workspace-note" title={`Confirmed ${formatDateTime(latestDataset.confirmed_at)}`}>
                    Dataset r{latestDataset.revision} · {latestDataset.entries.length} results · {latestDataset.source_file_name}
                  </p>
                ) : <p className="report-workspace-empty">No confirmed LLCR Result Dataset yet.</p>}
                <p className="report-workspace-note">LLCR Result and Comment cells and Appendix A</p>
                {latestDataset && readiness.llcrUpdateBlocker ? <p className="report-workspace-blocker">{readiness.llcrUpdateBlocker}</p> : null}
              </div>
              <button
                className="primary-action"
                disabled={!readiness.canUpdateLlcr || Boolean(busyAction) || !latestDataset || currentReport?.status !== "ready"}
                onClick={() => void handleUpdateLlcr()}
                type="button"
              >
                {busyAction === "llcr" ? "Updating..." : "Update LLCR results"}
              </button>
            </div>
            <div className="report-workspace-update-row">
              <div className="report-workspace-update-content">
                <h3>Equipment List</h3>
                <p className="report-workspace-note">Section 7 · Project equipment IDs and the configured calibration list</p>
              </div>
              <button
                className="primary-action"
                disabled={Boolean(busyAction) || currentReport?.status !== "ready"}
                ref={equipmentTrigger}
                onClick={() => void handleEquipmentUpdate()}
                type="button"
              >
                {busyAction === "equipment-update" ? "Updating..." : "Update Equipment List"}
              </button>
            </div>
            {currentReport?.status !== "ready" ? (
              <p className="report-workspace-blocker">
                {currentReport?.status === "ambiguous"
                  ? "Keep exactly one current Internal Report before updating its sections."
                  : "Generate an Internal Report to update its sections. LLCR import remains available."}
              </p>
            ) : null}
          </section>
        </div>
      ) : null}

      {sourcePickerOpen ? <CustomerReportSourceDialog busy={checkingSource || uploadedCustomerJob.busy} error={error || uploadedCustomerJob.error}
        onCancel={() => setSourcePickerOpen(false)} onGenerate={handleGenerateFromUploadedSource} /> : null}

      {customerRegenerationApproval?.fileName ? <CustomerReportRegenerationDialog
        fileName={customerRegenerationApproval.fileName}
        busy={pageBusyAction === "customer" || customerJob.busy}
        returnFocusTarget={customerRegenerationApproval.returnFocusTarget}
        onCancel={() => setCustomerRegenerationApproval(null)}
        onConfirm={() => void performCustomerGeneration(customerRegenerationApproval)} /> : null}

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

      {internalGenerationPreview ? (
        <div className="report-workspace-dialog-backdrop">
          <section className="report-workspace-dialog report-workspace-regeneration-dialog" role="dialog" aria-modal="true" aria-labelledby="internal-report-regeneration-title"
            onKeyDown={(event) => {
              if (event.key === "Escape" && !busyAction) setInternalGenerationPreview(null);
              if (event.key === "Tab") {
                const buttons = Array.from(event.currentTarget.querySelectorAll<HTMLButtonElement>("button:not(:disabled)"));
                const first = buttons[0], last = buttons.at(-1);
                if (event.shiftKey && document.activeElement === first && last) { event.preventDefault(); last.focus(); }
                else if (!event.shiftKey && document.activeElement === last && first) { event.preventDefault(); first.focus(); }
              }
            }}>
            <h2 id="internal-report-regeneration-title">Archive and regenerate Internal Report</h2>
            <p>The existing report, including manual content, results and photos, will be preserved in History/Report.</p>
            <p>The new report uses the approved E-3707_H template and latest confirmed Basic Information and Matrix. Previous manual content, results and photos are not copied; LLCR results and Equipment List can be updated separately.</p>
            <div className="report-workspace-action-row">
              <button autoFocus disabled={Boolean(busyAction)} type="button" onClick={() => setInternalGenerationPreview(null)}>Cancel</button>
              <button className="primary-action" disabled={Boolean(busyAction)} type="button" onClick={() => void handleInternalAction("initial", async (isCurrent) => {
                await performInternalGeneration(internalGenerationPreview, isCurrent);
              })}>{busyAction === "initial" ? "Generating..." : "Archive and regenerate"}</button>
            </div>
          </section>
        </div>
      ) : null}
      {equipmentSourceOpen ? (
        <EquipmentDialog title="Provide equipment IDs" busy={pageBusyAction === "equipment-update"}
          returnFocusTarget={equipmentTrigger.current} onClose={() => { setEquipmentSourceOpen(false); setEquipmentFile(null); setEquipmentIds(""); }}>
          <p>EquipmentID.docx was not found in the LTR folder. Choose a document or paste equipment IDs. The selection is saved there before updating the report.</p>
          <label className="report-workspace-file-field">EquipmentID document
            <input accept=".docx" type="file" disabled={pageBusyAction === "equipment-update"}
              onChange={(event) => { setEquipmentFile(event.target.files?.[0] ?? null); setEquipmentIds(""); }} />
          </label>
          <label className="report-workspace-file-field">Equipment IDs
            <textarea value={equipmentIds} disabled={pageBusyAction === "equipment-update"}
              placeholder="One equipment ID per line, or separated by commas"
              onChange={(event) => { setEquipmentIds(event.target.value); setEquipmentFile(null); }} />
          </label>
          {error ? <ErrorMessage message={error} /> : null}
          <div className="report-workspace-action-row">
            <button type="button" disabled={pageBusyAction === "equipment-update"}
              onClick={() => { setEquipmentSourceOpen(false); setEquipmentFile(null); setEquipmentIds(""); }}>Cancel</button>
            <button type="button" className="primary-action"
              disabled={pageBusyAction === "equipment-update" || (!equipmentFile && !equipmentIds.trim())}
              onClick={handleEquipmentSelection}>
              {pageBusyAction === "equipment-update" ? "Updating..." : "Save and update"}
            </button>
          </div>
        </EquipmentDialog>
      ) : null}
      {equipmentResult ? (
        <EquipmentDialog title="Equipment List update completed" busy={false}
          returnFocusTarget={equipmentTrigger.current} onClose={() => setEquipmentResult(null)}>
          <p>{equipmentResult.changed ? "Updated Equipment List." : "Equipment List was already up to date."}</p>
          <p>{equipmentResult.file_name}</p>
          {equipmentResult.archive_path ? <p>The previous report was archived in History/Report.</p> : null}
          <p>Equipment rows filled: {equipmentResult.statistics.filled}</p>
          <p>Not registered: {equipmentResult.statistics.unmatched.length}{equipmentResult.statistics.unmatched.length ? " — " + equipmentResult.statistics.unmatched.join(", ") : ""}</p>
          <p>Missing information: {equipmentResult.statistics.incomplete.length}{equipmentResult.statistics.incomplete.length ? " — " + equipmentResult.statistics.incomplete.join(", ") : ""}</p>
          <p>Expired calibration: {equipmentResult.statistics.expired.length}{equipmentResult.statistics.expired.length ? " — " + equipmentResult.statistics.expired.join(", ") + ". Calibration due dates are red in the report." : ""}</p>
          <div className="report-workspace-action-row"><button type="button" onClick={() => setEquipmentResult(null)}>Close</button></div>
        </EquipmentDialog>
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

function EquipmentDialog({ title, busy, onClose, returnFocusTarget, children }: {
  title: string; busy: boolean; onClose: () => void;
  returnFocusTarget: HTMLButtonElement | null; children: import("react").ReactNode;
}): ReactElement {
  const dialog = useRef<HTMLElement>(null);
  useEffect(() => {
    dialog.current?.querySelector<HTMLElement>("button, input, textarea")?.focus();
    return () => { window.setTimeout(() => { if (returnFocusTarget?.isConnected) returnFocusTarget.focus(); }, 0); };
  }, [returnFocusTarget]);
  return <div className="report-workspace-dialog-backdrop">
    <section ref={dialog} className="report-workspace-dialog" role="dialog" aria-modal="true" aria-label={title}
      onKeyDown={(event) => {
        if (event.key === "Escape" && !busy) onClose();
        if (event.key !== "Tab") return;
        const controls = Array.from(event.currentTarget.querySelectorAll<HTMLElement>("button:not(:disabled), input:not(:disabled), textarea:not(:disabled)"));
        const first = controls[0], last = controls.at(-1);
        if (!first) { event.preventDefault(); return; }
        if (event.shiftKey && document.activeElement === first && last) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }}>
      <h2>{title}</h2>
      {children}
    </section>
  </div>;
}
