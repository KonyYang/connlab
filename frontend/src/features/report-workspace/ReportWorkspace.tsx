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
  downloadInternalReportDraft,
  previewInternalReportGeneration,
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
import { useReportDraftUpdates } from "./useReportDraftUpdates";
import { useUploadedCustomerReportJob } from "./useUploadedCustomerReportJob";
import { CustomerReportSourceDialog } from "./CustomerReportSourceDialog";
import { CustomerReportRegenerationDialog } from "./CustomerReportRegenerationDialog";
import { LlcrImportPreviewDialog } from "./LlcrImportPreviewDialog";
import { ReportContentEditor } from "./ReportContentEditor";
import { ReportAuthoringPanel } from "./ReportAuthoringPanel";
import { StepReportEvidence, type StepLink } from './StepReportEvidence';
import { getReportAuthoring, adoptCurrentReportWorkingCopy, updateWorkingCopyLlcr, updateWorkingCopyEquipment,
  uploadReportSource, selectReportBase, downloadReportArtifact, type ReportAuthoringState } from "../../api/reportAuthoring";
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
  evidenceStep?: StepLink | null;
  projectId: string;
  onBack: () => void;
  onOpenBasicInformation?: () => void;
  identityLabel?: string;
};

type BusyAction = "load" | "initial" | "inspect" | "confirm" | "cancel" | "llcr" | "equipment-update" | "publish" | "download" | "customer" | "customer-source" | "authoring" | null;

type CustomerRegenerationApproval = {
  projectId: string;
  internalSha: string;
  customerSha: string | null;
  fileName: string | null;
  returnFocusTarget: HTMLButtonElement;
};

export function ReportWorkspace({ projectId, onBack, onOpenBasicInformation, identityLabel = "Connector Project", evidenceStep }: ReportWorkspaceProps): ReactElement {
  const topBarRoot = useTopBarActionsRoot();
  const [state, setState] = useState<ReportWorkspaceState | null>(null);
  const [currentReport, setCurrentReport] = useState<CurrentReport | null>(null);
  const [authoringState, setAuthoringState] = useState<ReportAuthoringState | null>(null);
  const [authoringReadFailed, setAuthoringReadFailed] = useState(false);
  const wordPicker = useRef<HTMLInputElement>(null);
  const [directCustomer, setDirectCustomer] = useState(false);
  const workingCopy = authoringState?.outputs.at(-1);
  const [customerReport, setCustomerReport] = useState<CustomerReportState | null>(null);
  const [customerReadFailed, setCustomerReadFailed] = useState(false);
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
  const [equipmentStatus, setEquipmentStatus] = useState<string | null>(null);
  const [reportSourceFile, setReportSourceFile] = useState<File | null>(null);
  const draftUpdates = useReportDraftUpdates(projectId, {
    save: (response) => downloadBlob(response.blob, response.fileName || "Internal Report_Draft.docx"),
    onUpdated: () => refresh(),
    onEquipmentRequired: () => setEquipmentSourceOpen(true),
    onEquipmentCompleted: (result) => {
      setEquipmentSourceOpen(false); setEquipmentFile(null); setEquipmentIds("");
      const { unmatched, incomplete, expired } = result.statistics;
      setEquipmentResult(unmatched.length || incomplete.length || expired.length ? result : null);
      setEquipmentStatus(result.changed ? "Equipment List Updated." : "Equipment List Is Up To Date.");
    },
  });
  const draftMode = !workingCopy && currentReport?.status !== "ambiguous" && (draftUpdates.source?.mode === "download_draft"
    || currentReport?.mode === "managed_draft" || currentReport?.status === "missing");
  useEffect(() => { if (draftUpdates.selectOpen) setReportSourceFile(null); }, [draftUpdates.selectOpen]);
  const equipmentRequest = useRef(false);
  const equipmentSequence = useRef(0);
  const equipmentTrigger = useRef<HTMLButtonElement>(null);
  const [pageBusyAction, setPageBusyAction] = useState<BusyAction>("load");
  const pageActionRef = useRef<BusyAction>("load");
  function setBusyAction(action: BusyAction) { pageActionRef.current = action; setPageBusyAction(action); }
  const authoringOperation = useRef<object | null>(null);
  const [authoringBusy, setAuthoringBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [internalGenerationPreview, setInternalGenerationPreview] = useState<InternalReportGenerationPreview | null>(null);
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
  const legacyBusyAction = pageBusyAction ?? (draftUpdates.busy ? (draftUpdates.action === "equipment" ? "equipment-update" : "llcr")
    : customerJob.busy || uploadedCustomerJob.busy ? "customer" : sourcePickerOpen || directCustomer || customerRegenerationApproval || equipmentSourceOpen || equipmentResult || draftUpdates.selectOpen ? "customer-source" : null);
  const busyAction = legacyBusyAction ?? (authoringBusy ? "authoring" : !authoringState ? "load" : null);
  const customerRun = useRef<{ regenerating: boolean; hadFile: boolean } | null>(null);
  const activeProject = useRef(projectId);
  const refreshedDelivery = useRef('');
  activeProject.current = projectId;

  function acceptAuthoringState(next: ReportAuthoringState) {
    if (!mounted.current || activeProject.current !== next.project_id) return;
    setAuthoringReadFailed(false);
    setAuthoringState(previous => previous?.project_id === next.project_id && previous.revision > next.revision ? previous : next);
  }

  function beginAuthoringOperation(): (() => void) | null {
    if (!mounted.current || activeProject.current !== projectId || legacyBusyAction || pageActionRef.current || authoringOperation.current) return null;
    const token = {}; authoringOperation.current = token; setAuthoringBusy(true);
    return () => {
      if (authoringOperation.current !== token) return;
      authoringOperation.current = null;
      if (mounted.current) setAuthoringBusy(false);
    };
  }
  useEffect(() => {
    authoringOperation.current = null; setAuthoringBusy(false);
    return () => { authoringOperation.current = null; };
  }, [projectId]);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; internalRequest.current += 1; equipmentSequence.current += 1; };
  }, []);

  useEffect(() => {
    internalRequest.current += 1;
    setInternalGenerationPreview(null);
    setMessage(null);
    setSourcePickerOpen(false);
    setDirectCustomer(false);
    setCheckingSource(false);
    sourceRequest.current = false;
    customerRequest.current = false;
    customerRun.current = null;
    setCustomerRegenerationApproval(null);
    equipmentSequence.current += 1;
    equipmentRequest.current = false;
    setEquipmentSourceOpen(false);
    setEquipmentResult(null);
    setEquipmentStatus(null);
    setEquipmentFile(null);
    setEquipmentIds("");
    setReportSourceFile(null);
  }, [projectId]);

  useEffect(() => {
    if (!message || (message !== "Generated the Internal Report." && !/^(Generated|Updated|The) .*customer report/.test(message))) return;
    const timer = window.setTimeout(() => setMessage(null), 5000);
    return () => window.clearTimeout(timer);
  }, [message]);

  const refresh = useCallback(async () => {
    const [nextState, nextReport, nextCustomerReport, nextAuthoring] = await loadReportState(projectId);
    if (mounted.current && activeProject.current === projectId) {
      setState(nextState);
      setCurrentReport(nextReport);
      setCustomerReport(nextCustomerReport);
      setCustomerReadFailed(nextCustomerReport === null);
      if (nextAuthoring) acceptAuthoringState(nextAuthoring);
      else { setAuthoringState(null); setAuthoringReadFailed(true); }
    }
    return { state: nextState, customerReport: nextCustomerReport };
  }, [projectId]);

  useEffect(() => {
    const delivery = authoringState?.delivery;
    if (!delivery || delivery.status !== 'completed') return;
    const identity = `${projectId}:${delivery.operation_id}`;
    if (refreshedDelivery.current === identity) return;
    refreshedDelivery.current = identity;
    void refresh().catch(() => {
      if (activeProject.current === projectId) setError('Reports were saved, but current report status could not be refreshed. Reload the page; do not generate again.');
    });
  }, [projectId, authoringState?.delivery?.operation_id, authoringState?.delivery?.status, refresh]);

  async function runAuthoringReload() {
    if (pageBusyAction || authoringOperation.current) return;
    setBusyAction("load");
    try {
      const next = await getReportAuthoring(projectId);
      acceptAuthoringState(next);
    } catch {
      if (activeProject.current === projectId) setAuthoringReadFailed(true);
    } finally {
      if (activeProject.current === projectId) setBusyAction(null);
    }
  }

  useEffect(() => {
    const job = customerJob.job;
    if (!job || job.project_id !== projectId || (job.status !== "completed" && job.status !== "failed")) return;
    let active = true;
    if (job.status === "failed" && job.error_code !== "customer_report_missing_after_preview") return;
    void refresh().then(({ customerReport: next }) => {
      if (!active) return;
      if (job.status === "failed") {
        if (job.can_regenerate && next?.status === "missing" && next.mode === "official" && next.can_generate && next.internal_report_sha256) {
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
    setState(null);
    setCurrentReport(null);
    setAuthoringState(null); setAuthoringReadFailed(false); setDirectCustomer(false);
    setCustomerReport(null);
    setCustomerReadFailed(false);
    loadReportState(projectId)
      .then(([nextState, nextReport, nextCustomerReport, nextAuthoring]) => {
        if (active) {
          setState(nextState);
          setCurrentReport(nextReport);
          setCustomerReport(nextCustomerReport);
          setCustomerReadFailed(nextCustomerReport === null);
          setAuthoringState(nextAuthoring); setAuthoringReadFailed(nextAuthoring === null);
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
  const officialReport = currentReport?.status === "ready" && currentReport.mode === "official" ? currentReport : null;
  const resumeSource = officialReport ?? (currentReport?.status !== "ambiguous" && draftUpdates.source?.status === "ready" && draftUpdates.source.mode === "download_draft"
    ? draftUpdates.source : null);
  const hasDraft = !officialReport && (Boolean(resumeSource) || currentReport?.status === "ready");
  const generationLabel = officialReport ? "Regenerate internal report…" : hasDraft ? "Generate another internal report…" : "Create a new internal report";

  async function continueReport() {
    if (!resumeSource || !authoringState) return;
    await runAction("authoring", async () => {
      const selected = resumeSource;
      const current = officialReport ? await fetchCurrentReport(projectId) : await draftUpdates.refresh();
      if (!mounted.current || activeProject.current !== projectId) return null;
      if (current.status !== "ready" || !current.file_sha256 || selected.file_sha256 !== current.file_sha256 ||
          selected.file_name !== current.file_name || selected.file_path !== current.file_path || selected.mode !== current.mode ||
          (current.mode !== "official" && current.mode !== "download_draft")) {
        await refresh();
        throw new Error("The available report changed. Check the refreshed filename before continuing.");
      }
      const next = await adoptCurrentReportWorkingCopy(projectId, {
        expected_revision: authoringState.revision, source_sha256: current.file_sha256, source_mode: current.mode,
      });
      acceptAuthoringState(next);
      return null;
    });
  }

  async function handleInternalAction(action: "initial", operation: (isCurrent: () => boolean) => Promise<void>): Promise<void> {
    if (busyAction || authoringOperation.current) return;
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

  async function openWordCopy(file: File, isCurrent: () => boolean) {
    if (!authoringState || !isCurrent()) return;
    if (!/\.docx$/i.test(file.name)) throw new Error("Select a Word document (.docx).");
    if (!authoringState.context.dl_number) throw new Error("Register the project LTR number before choosing a Word working copy.");
    const revision = authoringState.revision;
    const digest = await crypto.subtle.digest("SHA-256", await file.arrayBuffer());
    if (!isCurrent()) return;
    const sha = Array.from(new Uint8Array(digest), n => n.toString(16).padStart(2, "0")).join("");
    const retained = await uploadReportSource(projectId, file, "original", revision);
    if (!isCurrent()) return;
    acceptAuthoringState(retained);
    const source = retained.sources.filter(item => item.role === "original" && item.sha256 === sha
      && !("source_locator" in item && item.source_locator)
      && item.file_name.localeCompare(file.name, "en", { sensitivity: "accent" }) === 0).at(-1);
    if (!source || retained.revision > revision + 1) throw new Error("The report sources changed. Choose the Word file again.");
    const next = await selectReportBase(projectId, source.source_id, retained.revision);
    if (isCurrent()) acceptAuthoringState(next);
  }

  async function performInternalGeneration(preview: InternalReportGenerationPreview, isCurrent: () => boolean): Promise<void> {
    if (!preview.preview_token || !isCurrent()) return;
    const generated = await generateInternalReport(projectId, preview.preview_token, preview.requires_confirmation);
    if (!isCurrent()) return;
    setInternalGenerationPreview(null);
    let refreshWarning = "";
    try { await refresh(); } catch {
      refreshWarning = "Report generated. Refresh the workspace to check the latest project report status.";
    }
    if (!isCurrent() || !authoringState) return;
    try {
      const next = await adoptCurrentReportWorkingCopy(projectId, {expected_revision: authoringState.revision,
        source_sha256: generated.file_sha256, source_mode: "official"});
      if (isCurrent()) {
        acceptAuthoringState(next);
        setMessage("Generated the Internal Report.");
        if (refreshWarning) setError(refreshWarning);
      }
    } catch (cause) {
      if (isCurrent()) setError("Internal report generated. Unable to prepare its working copy. " + (cause instanceof Error ? cause.message : "Choose the existing Word file to retry."));
    }
  }

  async function handleGenerateInternalReport(): Promise<void> {
    if (workingCopy || !authoringState) return;
    await handleInternalAction("initial", async (isCurrent) => {
      const preview = await previewInternalReportGeneration(projectId);
      if (!isCurrent()) return;
      if (preview.status !== "ready" || !preview.preview_token) {
        setError(preview.blockers.join(" ") || "Resolve the report prerequisites and preview again.");
      } else if (officialReport && (preview.mode !== "official" || !preview.requires_confirmation ||
          (officialReport.file_path && preview.current_path !== officialReport.file_path))) {
        await refresh();
        if (isCurrent()) setError("The official report changed. Check the refreshed report before generating again.");
      } else if (preview.mode === "managed_draft" || preview.mode === "download_draft") {
        const response = await downloadInternalReportDraft(projectId, preview.preview_token);
        if (!isCurrent()) return;
        const name = response.fileName || "Internal Report draft.docx";
        downloadBlob(response.blob, name);
        setMessage(`Downloaded draft: ${name}`);
        try { await openWordCopy(new File([response.blob], name), isCurrent); }
        catch (cause) { if (isCurrent()) setError("Draft downloaded. Unable to prepare its working copy. " + (cause instanceof Error ? cause.message : "Choose the downloaded Word file to retry.")); }
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
    if (busyAction || pageActionRef.current || authoringOperation.current) {
      return;
    }
    setBusyAction(action);
    setError(null);
    setMessage(null);
    try {
      const result = await operation();
      if (mounted.current && activeProject.current === projectId) setMessage(result);
    } catch (reason) {
      if (mounted.current && activeProject.current === projectId) setError(errorMessage(reason, "Report workflow failed."));
    } finally {
      if (mounted.current && activeProject.current === projectId) setBusyAction(null);
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
    if (workingCopy || !authoringState) return;
    if (authoringOperation.current) return;
    if (!busyAction && !customerReportRecovery && currentReport?.status === "missing" &&
        !(customerReport?.mode === "managed_download" && customerReport.can_generate)) {
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
    if (workingCopy || !authoringState) return;
    if (authoringOperation.current) return;
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
            refreshed.customerReport?.status === "missing" &&
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
    if (authoringOperation.current) return false;
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
    if (workingCopy || !authoringState) return;
    if (authoringOperation.current) return;
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
    if (authoringOperation.current) return;
    if (!latestDataset || !authoringState) {
      return;
    }
    if (workingCopy) {
      await runAction("llcr", async () => {
        if (!workingCopy.artifact?.sha256) throw new Error("Reload the selected working copy before updating it.");
        const next = await updateWorkingCopyLlcr(projectId, { expected_revision: authoringState.revision,
          expected_sha256: workingCopy.artifact.sha256, dataset_revision_id: latestDataset.dataset_id });
        acceptAuthoringState(next);
        return "LLCR results updated in the working copy. The official report is unchanged.";
      });
      return;
    }
    if (draftMode) { await draftUpdates.updateLlcr(latestDataset.dataset_id); return; }
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
    if (authoringOperation.current || !authoringState) return;
    if (draftMode) { await draftUpdates.updateEquipment(input); return; }
    if (equipmentRequest.current || pageBusyAction || customerJob.busy || uploadedCustomerJob.busy) return;
    equipmentRequest.current = true;
    const sequence = ++equipmentSequence.current;
    const isCurrent = () => mounted.current && activeProject.current === projectId && equipmentSequence.current === sequence;
    setBusyAction("equipment-update");
    setEquipmentStatus(null);
    setError(null);
    setMessage(null);
    try {
      if (workingCopy) {
        if (!workingCopy.artifact?.sha256) throw new Error("Reload the selected working copy before updating it.");
        const request = { expected_revision: authoringState.revision, expected_sha256: workingCopy.artifact.sha256 };
        const next = input ? await updateWorkingCopyEquipment(projectId, request, input) : await updateWorkingCopyEquipment(projectId, request);
        if (!isCurrent()) return;
        if ('status' in next) { setEquipmentSourceOpen(true); return; }
        acceptAuthoringState(next);
        setEquipmentSourceOpen(false); setEquipmentFile(null); setEquipmentIds("");
        const updated = next.outputs.at(-1);
        const statistics = updated?.evidence?.statistics;
        setEquipmentResult(statistics && (statistics.unmatched.length || statistics.incomplete.length || statistics.expired.length)
          ? { status: 'completed', project_id: projectId, file_name: updated!.file_name, changed: updated?.output_id !== workingCopy.output_id,
            current_sha256: updated?.artifact?.sha256 || '', archive_path: null, statistics } : null);
        setEquipmentStatus("Equipment List updated in the working copy. The official report is unchanged.");
        return;
      }
      const result = await updateEquipmentListOneClick(projectId, input);
      if (!isCurrent()) return;
      if (result.status === "source_required") {
        setEquipmentSourceOpen(true);
        return;
      }
      setEquipmentSourceOpen(false);
      setEquipmentFile(null);
      setEquipmentIds("");
      const { unmatched, incomplete, expired } = result.statistics;
      setEquipmentResult(unmatched.length || incomplete.length || expired.length ? result : null);
      setEquipmentStatus(result.changed ? "Equipment List Updated." : "Equipment List Is Up To Date.");
      try { await refresh(); }
      catch { if (isCurrent()) setError("Equipment List was updated. Reload to refresh report status."); }
    } catch (reason) {
      if (isCurrent()) {
        if (input) setEquipmentSourceOpen(false);
        setError(errorMessage(reason, "ConnLab could not complete the Equipment List update. In Settings, choose Export diagnostic package and send the ZIP for support."));
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
    if (workingCopy || !authoringState) return;
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

  const llcrControls = readiness && (<div className="report-workspace-update-row">
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
                    {busyAction === "inspect" ? "Inspecting..." : "Inspect LLCR Workbook"}
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
                disabled={!readiness.canUpdateLlcr || Boolean(busyAction) || !latestDataset || (!workingCopy && currentReport?.status !== "ready" && !draftMode)}
                onClick={() => void handleUpdateLlcr()}
                type="button"
              >
                {busyAction === "llcr" ? "Updating..." : "Update LLCR Results"}
              </button>
            </div>);
  const equipmentControls = (<div className="report-workspace-update-row report-workspace-equipment-action">
              <button
                className="primary-action"
                disabled={Boolean(busyAction) || (!workingCopy && currentReport?.status !== "ready" && !draftMode)}
                ref={equipmentTrigger}
                onClick={() => void handleEquipmentUpdate()}
                type="button"
              >
                {busyAction === "equipment-update" ? "Updating..." : "Update Equipment List"}
              </button>
              {equipmentStatus ? (
                <span className="report-workspace-equipment-completion" role="status" aria-label="Equipment List update status">
                  {equipmentStatus}
                </span>
              ) : null}
            </div>);

  const commandbar = (
    <div className="report-workspace-commandbar" aria-label="Report Workspace actions">
      <span className="report-workspace-identity" title={identityLabel}>{identityLabel}</span>
      <button className="report-workspace-back" onClick={onBack} type="button"
        aria-label="Back To Workspace" title="Back To Workspace">Back</button>
    </div>
  );

  const directCustomerAction = (
    <button type="button" className="report-editor-link" disabled={Boolean(legacyBusyAction || authoringBusy)} onClick={() => { setDirectCustomer(true); }}>
          Create customer copy from a finished internal report…
        </button>
  );
  return (
    <section className="report-workspace-page" aria-busy={!state && busyAction === "load" && !error}>
      {topBarRoot ? createPortal(commandbar, topBarRoot) : (
        <header className="report-workspace-header">
          <h1>Report</h1>
          {commandbar}
        </header>
      )}
      {!state && busyAction === "load" && !error ? <div className="panel" role="status">Loading Report Workspace...</div> : null}
      {error ? <ErrorMessage message={error} /> : null}
      {message ? <p className="report-workspace-message" role="status">{message}</p> : null}
      {evidenceStep && authoringState?.project_id === projectId && <section className="report-workspace-card">
        <StepReportEvidence projectId={projectId} step={evidenceStep} report={authoringState} />
      </section>}

      {state && authoringReadFailed && <div role="alert" className="report-workspace-blocker">
        <p>Unable to check the selected working copy. Report changes are paused; the official report has not been changed.</p>
        <button type="button" disabled={pageBusyAction !== null} onClick={() => void runAuthoringReload()}>Retry working-copy status</button>
      </div>}
      <input type="file" accept=".docx" ref={wordPicker} hidden aria-label="Working Word file"
        onChange={event => {
          const file = event.currentTarget.files?.[0]; event.currentTarget.value = "";
          if (file) void runAction("authoring", async () => {
            await openWordCopy(file, () => mounted.current && activeProject.current === projectId); return null;
          });
        }} />
      {workingCopy && authoringState ? <ReportContentEditor key={projectId + ":" + workingCopy.base_source_id}
        projectId={projectId} state={authoringState} disabled={Boolean(busyAction)}
        directCustomerAction={directCustomerAction} onChanged={acceptAuthoringState} beginOperation={beginAuthoringOperation} llcr={llcrControls} equipment={equipmentControls}
        fileActions={<div className="report-workspace-action-row">
          <button type="button" className="report-editor-link" disabled={Boolean(busyAction)} onClick={() => wordPicker.current?.click()}>Change file…</button>
          <button type="button" className="secondary-action" disabled={Boolean(busyAction)} onClick={() => void runAction("download", async () => {
            const response = await downloadReportArtifact(workingCopy.download_url);
            if (activeProject.current === projectId && mounted.current) downloadBlob(response.blob, response.fileName || workingCopy.file_name);
            return null;
          })}>Download working copy</button>
        </div>} /> : state && readiness && <section className="report-entry" aria-label="Report generation">
        <section aria-label="Internal Report">
          {resumeSource?.file_name && resumeSource.file_sha256 && <div className="report-entry-row">
            <button className="ui-primary-action report-entry-resume" type="button"
              disabled={Boolean(busyAction) || !authoringState?.context.dl_number} onClick={() => void continueReport()}>
              Continue with <span>{resumeSource.file_name}</span>
            </button>
          </div>}
          <div className="report-entry-row">
            <button className={officialReport || hasDraft ? "ui-secondary-action" : "ui-primary-action"} type="button"
              disabled={!readiness.canGenerateInitialDraft || reportEntry.kind === "blocked" || Boolean(busyAction)}
              onClick={() => void handleGenerateInternalReport()}>
              {busyAction === "initial" ? "Generating…" : generationLabel}
            </button>
            {state.basic_information_status !== "confirmed" && onOpenBasicInformation &&
              <button className="ui-secondary-action" type="button" onClick={onOpenBasicInformation}>Open Basic Information</button>}
            {readiness.initialDraftBlocker && <p className="report-workspace-blocker">{readiness.initialDraftBlocker}</p>}
            {reportEntry.kind === "blocked" && <p className="report-workspace-blocker">Multiple internal reports were found. Resolve that conflict before creating or updating a report.</p>}
            {currentReport?.status === "ready" && currentReport.mode !== "official" && <>
              {currentReport.file_name !== resumeSource?.file_name && <span className="report-workspace-report-name">{currentReport.file_name}</span>}
              <button type="button" disabled={Boolean(busyAction)} onClick={() => void handleDownloadCurrent()}>Download Current Report</button>
              {reportEntry.kind === "publish" && <button className="ui-secondary-action" type="button" disabled={Boolean(busyAction)}
                onClick={() => void handlePublishManagedReport()}>{busyAction === "publish" ? "Publishing..." : "Publish Current Draft To Project Folder"}</button>}
              {reportEntry.kind === "managed" && <p className="report-workspace-note">Create the official project folder before publishing this draft.</p>}
            </>}
          </div>
          <div className="report-entry-row">
            <button type="button" className="ui-secondary-action"
              aria-describedby={authoringState ? "report-entry-expected-ltr" : undefined}
              disabled={Boolean(busyAction) || !authoringState?.context.dl_number}
              onClick={() => wordPicker.current?.click()}>Continue this project’s Word report…</button>
            {authoringState && <p id="report-entry-expected-ltr">{authoringState.context.dl_number
              ? `Expected project LTR: ${authoringState.context.dl_number}`
              : "Register this project’s LTR number before selecting a report."}</p>}
          </div>
        </section>
        {directCustomerAction}
        <details open={Boolean(customerReportRecovery || customerJob.busy || customerJob.error || customerJob.job?.status === 'failed') || undefined}>
          <summary>Project report actions</summary>
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
                  {busyAction === "customer" ? "Generating Customer Report..." : "Generate Customer Report"}
                </button>
                {customerJob.job?.status === "completed" && customerJob.job.result?.mode === "managed_download" ? (
                  <button type="button" disabled={customerJob.downloading || Boolean(busyAction)} onClick={() => void customerJob.download()}>
                    {customerJob.downloading ? "Downloading..." : customerJob.downloadError ? "Retry Download" : "Download Generated Copy"}
                  </button>
                ) : null}
              </div>
              {customerReport?.file_name || customerJob.job?.result?.file_name ? <span className="report-workspace-report-name">
                {customerReport?.file_name || customerJob.job?.result?.file_name}
              </span> : null}
              {customerReadFailed ? <p role="alert" className="report-workspace-blocker">
                Unable to check the customer report. Check the connection and retry report status. Existing report files have not been changed.
              </p> : null}
              {customerReadFailed || customerReport?.status === "blocked" ? <button type="button"
                disabled={busyAction !== null}
                onClick={async () => {
                  setBusyAction("load");
                  try { await refresh(); }
                  catch { if (mounted.current && activeProject.current === projectId) setError("Unable to refresh report status. Check the connection and reload."); }
                  finally { if (mounted.current && activeProject.current === projectId) setBusyAction(null); }
                }}>Retry report status</button> : null}
              {customerReport?.warnings.map((warning) => (
                <p className="report-workspace-warning" key={warning}>{warning}</p>
              ))}
              {currentReport?.status !== "missing" ? customerReport?.blockers.map((blocker) => (
                <p className="report-workspace-blocker" key={blocker}>{blocker}</p>
              )) : null}
              {customerJob.job?.status === "queued" || customerJob.job?.status === "running" ? <CustomerReportProgress
                stage={customerJob.job.stage}
                elapsedSeconds={customerJob.elapsed}
                running={customerJob.job.status === "queued" || customerJob.job.status === "running"}
              /> : null}
              {customerJob.error ? <p role="alert" className="report-workspace-blocker">{customerJob.error}</p> : null}
              {customerJob.queryWarning ? <div role="alert" className="report-workspace-warning">
                <p>{customerJob.queryWarning}</p>
                <button type="button" onClick={() => void customerJob.retryQuery()}>Retry Status Check</button>
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
                        ? "Generating Customer Report..."
                        : "Generate New Customer Report"}
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

        </details>
        <details><summary>Report content</summary>
          <section aria-label="Update Internal Report">
            {llcrControls}{equipmentControls}
            {draftMode ? <div className="report-workspace-note">
              {draftUpdates.source?.file_name ? <p title={draftUpdates.source.file_name}>Draft source: {draftUpdates.source.file_name} · Updates download a copy.</p>
                : <p>Select an Internal Report draft to update its sections. Original files are preserved.</p>}
              <div className="report-workspace-action-row">
                <button type="button" disabled={Boolean(busyAction)} onClick={() => { setReportSourceFile(null); draftUpdates.choose(); }}>
                  {draftUpdates.source?.status === "ready" ? "Choose Another Draft" : "Select Internal Report"}
                </button>
                {draftUpdates.lastResult ? <button type="button" disabled={Boolean(busyAction)} onClick={() => void draftUpdates.download()}>
                  {draftUpdates.downloadError ? "Retry Draft Download" : "Download Updated Draft"}
                </button> : null}
                <button type="button" disabled={Boolean(busyAction)} onClick={() => void draftUpdates.refresh().catch(() => undefined)}>Reload Draft Source</button>
              </div>
              {draftUpdates.error ? <p role="alert" className="report-workspace-blocker">{draftUpdates.error}</p> : null}
              {draftUpdates.downloadError ? <p role="alert" className="report-workspace-blocker">{draftUpdates.downloadError}</p> : null}
            </div> : null}
            {!workingCopy && currentReport?.status !== "ready" && !draftMode ? (
              <p className="report-workspace-blocker">
                {currentReport?.status === "ambiguous"
                  ? "Keep exactly one current Internal Report before updating its sections."
                  : "Generate an Internal Report to update its sections. LLCR import remains available."}
              </p>
            ) : null}

          </section>
          {authoringState && <ReportAuthoringPanel projectId={projectId} sharedState={authoringState} disabled={Boolean(legacyBusyAction)}
            onChanged={acceptAuthoringState} onOperationStart={beginAuthoringOperation} />}
        </details>
      </section>}
              {uploadedCustomerJob.job?.status === "queued" || uploadedCustomerJob.job?.status === "running" ? <CustomerReportProgress stage={uploadedCustomerJob.job.stage}
                elapsedSeconds={uploadedCustomerJob.job.elapsed_seconds} running={uploadedCustomerJob.busy} /> : null}
              {uploadedCustomerJob.error ? <p role="alert" className="report-workspace-blocker">{uploadedCustomerJob.error}</p> : null}
              {uploadedCustomerJob.job?.status === "failed" ? <p role="alert" className="report-workspace-blocker">
                {uploadedCustomerJob.job.message || "Unable to generate the customer report. Select the source and try again."}
              </p> : null}
              {uploadedCustomerJob.queryWarning ? <div role="alert" className="report-workspace-warning">
                <p>{uploadedCustomerJob.queryWarning}</p>
                <button type="button" onClick={() => void uploadedCustomerJob.retryQuery()}>Retry Status Check</button>
              </div> : null}
              {uploadedCustomerJob.downloadError ? <div role="alert" className="report-workspace-blocker">
                <p>{uploadedCustomerJob.downloadError}</p>
                <button type="button" disabled={uploadedCustomerJob.busy} onClick={() => void uploadedCustomerJob.retryDownload()}>Retry Download</button>
              </div> : null}
      {uploadedCustomerJob.fileName && <p role="status">Downloaded customer copy: <strong>{uploadedCustomerJob.fileName}</strong></p>}
      {!state && error && directCustomerAction}
      {directCustomer && <CustomerReportSourceDialog direct busy={uploadedCustomerJob.busy} error={uploadedCustomerJob.error}
        onCancel={() => setDirectCustomer(false)} onGenerate={async file => {
          const ok = await uploadedCustomerJob.start(file);
          if (ok && mounted.current && activeProject.current === projectId) setDirectCustomer(false);
          return ok;
        }} />}
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
            {internalGenerationPreview.current_path && <p className="report-entry-confirm-file">{internalGenerationPreview.current_path.split(/[\\/]/).pop()}</p>}
            <p>The existing report, including manual content, results and photos, will be preserved in History/Report.</p>
            <p>The new report uses the approved E-3707_H template and latest confirmed Basic Information and Matrix. Previous manual content, results and photos are not copied; LLCR results and Equipment List can be updated separately.</p>
            <div className="report-workspace-action-row">
              <button autoFocus disabled={Boolean(busyAction)} type="button" onClick={() => setInternalGenerationPreview(null)}>Cancel</button>
              <button className="primary-action" disabled={Boolean(busyAction)} type="button" onClick={() => void handleInternalAction("initial", async (isCurrent) => {
                await performInternalGeneration(internalGenerationPreview, isCurrent);
              })}>{busyAction === "initial" ? "Generating..." : "Archive And Regenerate"}</button>
            </div>
          </section>
        </div>
      ) : null}
      {draftUpdates.selectOpen ? <EquipmentDialog title="Select Internal Report for Updates" busy={draftUpdates.busy}
        returnFocusTarget={equipmentTrigger.current} onClose={draftUpdates.close}>
        <p>Choose this project's E-3707 Internal Report. Updates use a new draft copy.</p>
        <label>Internal Report draft<input type="file" accept=".docx" disabled={draftUpdates.busy}
          onChange={(event) => setReportSourceFile(event.target.files?.[0] ?? null)} /></label>
        {draftUpdates.error ? <p role="alert" className="report-workspace-blocker">{draftUpdates.error}</p> : null}
        <div className="report-workspace-action-row">
          <button type="button" disabled={draftUpdates.busy} onClick={draftUpdates.close}>Cancel</button>
          <button type="button" disabled={draftUpdates.busy || !reportSourceFile}
            onClick={() => { if (reportSourceFile) void draftUpdates.select(reportSourceFile); }}>Use Draft</button>
        </div>
      </EquipmentDialog> : null}
      {equipmentSourceOpen ? (
        <EquipmentDialog title="Provide equipment IDs" busy={pageBusyAction === "equipment-update" || draftUpdates.busy}
          returnFocusTarget={equipmentTrigger.current} onClose={() => { setEquipmentSourceOpen(false); setEquipmentFile(null); setEquipmentIds(""); }}>
          <p>{draftMode ? "Choose an equipment document or paste equipment IDs. Only the draft copy will be updated."
            : "EquipmentID.docx was not found in the LTR folder. Choose a document or paste equipment IDs. The selection is saved there before updating the report."}</p>
          <label className="report-workspace-file-field">EquipmentID document
            <input accept=".docx" type="file" disabled={pageBusyAction === "equipment-update" || draftUpdates.busy}
              onChange={(event) => { setEquipmentFile(event.target.files?.[0] ?? null); setEquipmentIds(""); }} />
          </label>
          <label className="report-workspace-file-field">Equipment IDs
            <textarea value={equipmentIds} disabled={pageBusyAction === "equipment-update" || draftUpdates.busy}
              placeholder="One equipment ID per line, or separated by commas"
              onChange={(event) => { setEquipmentIds(event.target.value); setEquipmentFile(null); }} />
          </label>
          {error ? <ErrorMessage message={error} /> : null}
          {draftMode && draftUpdates.error ? <ErrorMessage message={draftUpdates.error} /> : null}
          <div className="report-workspace-action-row">
            <button type="button" disabled={pageBusyAction === "equipment-update" || draftUpdates.busy}
              onClick={() => { setEquipmentSourceOpen(false); setEquipmentFile(null); setEquipmentIds(""); }}>Cancel</button>
            <button type="button" className="primary-action"
              disabled={pageBusyAction === "equipment-update" || draftUpdates.busy || (!equipmentFile && !equipmentIds.trim())}
              onClick={handleEquipmentSelection}>
              {pageBusyAction === "equipment-update" || draftUpdates.busy ? "Updating..." : draftMode ? "Update And Download" : "Save And Update"}
            </button>
          </div>
        </EquipmentDialog>
      ) : null}
      {equipmentResult ? (
        <EquipmentDialog title="Equipment List Needs Review" busy={false} compact
          returnFocusTarget={equipmentTrigger.current} onClose={() => setEquipmentResult(null)}>
          {equipmentResult.statistics.unmatched.length ? <p>Equipment IDs not found in the calibration workbook: {equipmentResult.statistics.unmatched.join(", ")}. Use DG-Q-XXXX or DG-L-XXXX with four digits (e.g., DG-Q-0913). If an ID is correct but missing, add it to the workbook.</p> : null}
          {equipmentResult.statistics.incomplete.length ? <p>Incomplete Information: {equipmentResult.statistics.incomplete.join(", ")}. Complete equipment details and calibration dates.</p> : null}
          {equipmentResult.statistics.expired.length ? <p>Expired Calibration: {equipmentResult.statistics.expired.join(", ")}. Confirm calibration status before using these instruments. Calibration due dates are red in the report.</p> : null}
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

async function loadReportState(projectId: string) {
  // A customer-report read failure must not discard the usable Internal Report.
  return Promise.all([
    fetchReportWorkspace(projectId),
    fetchCurrentReport(projectId),
    fetchCurrentCustomerReport(projectId).catch(() => null),
    getReportAuthoring(projectId).catch(() => null),
  ] as const);
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

function EquipmentDialog({ title, busy, compact = false, onClose, returnFocusTarget, children }: {
  title: string; busy: boolean; onClose: () => void;
  compact?: boolean;
  returnFocusTarget: HTMLButtonElement | null; children: import("react").ReactNode;
}): ReactElement {
  const dialog = useRef<HTMLElement>(null);
  useEffect(() => {
    dialog.current?.querySelector<HTMLElement>("button, input, textarea")?.focus();
    return () => { window.setTimeout(() => { if (returnFocusTarget?.isConnected) returnFocusTarget.focus(); }, 0); };
  }, [returnFocusTarget]);
  return <div className="report-workspace-dialog-backdrop">
    <section ref={dialog} className={`report-workspace-dialog${compact ? " report-workspace-equipment-review" : ""}`} role="dialog" aria-modal="true" aria-label={title}
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
