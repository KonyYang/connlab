import { useEffect, useRef, useState, type ReactElement } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import {
  deleteTemporaryProject,
  fetchOfficialWorkspaceRelocationPreview,
  getProjectFolderGeneration,
  relocateOfficialWorkspace,
  type OfficialWorkspaceConflictStrategy,
  type OfficialWorkspaceRelocationAction,
  type OfficialWorkspaceRelocationPreview,
  previewTemporaryProjectDelete,
  type PublicFolderWorkflowOperationType,
  type ProjectCloseReasonCategory,
  type Project,
  type TemporaryProjectDeletePreview,
} from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import type {
  FolderUpdateReview,
  ProjectFolderUpdateAction,
} from "./useProjectFolderGeneration";
import {
  deriveActiveMatrixFolderCommand,
  ProjectWorkbenchActiveMatrixWorkspace,
} from "./ProjectWorkbenchActiveMatrixWorkspace";
import {
  NoMatrixWorkspaceEmptyState,
  ProjectLifecycleManagementPanel,
} from "./ProjectWorkbenchLifecycleSections";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import {
  deriveProjectFolderTasks,
  selectProjectFolderOneClickBlocker,
  type ProjectFolderTaskActionTarget,
} from "./projectFolderTaskSelectors";
import {
  deriveProjectWorkbenchLifecycle,
  deriveProjectWorkbenchLifecycleActions,
} from "./projectWorkbenchLifecycleSelectors";
import {
  deriveProjectWorkbenchShellModel,
} from "./projectWorkbenchShellModel";
import { deriveProjectLifecycleReadonlyView } from "../project-lifecycle/projectLifecycleReadonlyModel";
import {
  buildProjectIdentityLine,
  deriveRegisteredProjectReference,
} from "../projectIdentity";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";
import { TestReportDraftButton } from "./TestReportDraftButton";

type ProjectWorkbenchLayoutProps = {
  runtimeModel: ProjectRuntimeConsoleModel;
  project: Project;
  onBack: () => void;
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
  onOpenBasicInformation: () => void;
  onOpenReportWorkspace: () => void;
  onOpenSettings: () => void;
};

export function ProjectWorkbenchLayout({
  runtimeModel,
  project,
  onBack,
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
  onOpenBasicInformation,
  onOpenReportWorkspace,
  onOpenSettings,
}: ProjectWorkbenchLayoutProps): ReactElement {
  const [selectedProjectionToken, setSelectedProjectionToken] =
    useState<MatrixProjectionTokenCell | null>(null);
  const [deletePreview, setDeletePreview] =
    useState<TemporaryProjectDeletePreview | null>(null);
  const [lifecycleBusy, setLifecycleBusy] = useState(false);
  const [lifecycleError, setLifecycleError] = useState<string | null>(null);
  const [showFolderConflictDialog, setShowFolderConflictDialog] = useState(false);
  const [folderUpdateReview, setFolderUpdateReview] = useState<FolderUpdateReview | null>(null);
  const [folderRelocationReview, setFolderRelocationReview] = useState<OfficialWorkspaceRelocationPreview | null>(null);
  const [folderRelocationError, setFolderRelocationError] = useState<string | null>(null);
  const [folderRelocationBusy, setFolderRelocationBusy] = useState(false);
  const [folderNameUpdatedNotice, setFolderNameUpdatedNotice] = useState(false);
  const folderRelocationInFlight = useRef(false);
  const [recoveryPreviewCheckedProject, setRecoveryPreviewCheckedProject] = useState<string | null>(null);
  const topBarActionsRoot = useTopBarActionsRoot();

  const {
    activeConfirmedMatrixSnapshot,
    folderReady,
    folderResources,
    latestLtr,
    matrixCandidateDraft,
    matrixDraft,
    packagePreview,
    packagePreviewError,
    officialWorkspacePreview,
    officialWorkspaceCreating,
    officialWorkspaceCanRestart,
    onRefreshOfficialWorkspacePreview,
    officialWorkspaceProgressLabel,
    officialWorkspaceError,
    onUpdateOfficialWorkspace,
    officialFolderCheckPreview,
    officialFolderCheckError,
    onRefreshOfficialFolderCheck,
    onRepairOfficialFolderStructure,
    publicDriveUploadPreview,
    publicDriveUploadLoading,
    publicDriveUploading,
    publicDriveUploadError,
    publicFolderWorkflowContext,
    publicFolderWorkflowContextLoading,
    publicFolderWorkflowContextError,
    onRefreshPublicFolderWorkflowContext,
    publicFolderWorkflowPreviews,
    publicFolderWorkflowResults,
    publicFolderWorkflowBusyOperation,
    publicFolderWorkflowConfirmingOperation,
    publicFolderWorkflowError,
    publicFolderWorkflowMessage,
    publicFolderWorkflowAutoSyncBusy,
    onSetPublicFolderWorkflowAutoSync,
    onOpenLocalProjectFolder,
    onPreviewPublicFolderWorkflowOperation,
    onConfirmPublicFolderWorkflowOperation,
    onCancelPublicFolderWorkflowOperation,
    onActivateLifecycle,
    onCloseLifecycle,
    outputStatusSummary,
    requestMaterialPreview,
    requestMaterialLoading,
    requestMaterialCollecting,
    requestMaterialError,
    onCollectRequestMaterial,
    requiredFormsPreview,
    requiredFormsLoading,
    requiredFormsGenerating,
    requiredFormsError,
    onRefreshRequiredForms,
    onGenerateRequiredForms,
    runtimeProjectionSnapshot,
    section2SyncPreview,
    confirmedFeeLatest,
  } = runtimeModel;
  const refreshOfficialWorkspacePreview = useRef(onRefreshOfficialWorkspacePreview);
  refreshOfficialWorkspacePreview.current = onRefreshOfficialWorkspacePreview;

  useEffect(() => {
    let active = true;
    setRecoveryPreviewCheckedProject(null);
    if (!officialWorkspaceCanRestart) {
      return () => {
        active = false;
      };
    }
    void refreshOfficialWorkspacePreview.current()
      .catch(() => { /* The model retains the preview error for the operator. */ })
      .finally(() => {
        if (active) setRecoveryPreviewCheckedProject(project.project_id);
      });
    return () => {
      active = false;
    };
  }, [officialWorkspaceCanRestart, project.project_id]);

  const projectNumber = deriveRegisteredProjectReference(latestLtr, project.project_no);
  const lifecycleReadonlyView = deriveProjectLifecycleReadonlyView(runtimeModel.lifecycle);
  const activeMatrixAuthorityReady = Boolean(activeConfirmedMatrixSnapshot);
  const effectiveFolderReady =
    folderReady || officialWorkspacePreview?.status === "completed";
  const titleParts = [buildProjectIdentityLine({ project, latestLtr, projectId: project.project_id })];
  const lifecycle = deriveProjectWorkbenchLifecycle(
    {
      hasLtr: Boolean(projectNumber),
      isCancelled: project.status === "cancelled",
      hasActiveMatrix: activeMatrixAuthorityReady,
      hasCandidateMatrix: Boolean(matrixCandidateDraft ?? matrixDraft),
      folderReady: effectiveFolderReady,
      folderTemplateReady: deriveFolderTemplateReady(folderResources.template),
      packageStatus: packagePreview?.status ?? null,
      packageBlockers: packagePreview?.blockers ?? [],
      packageWarnings: packagePreview?.warnings ?? [],
      requestMaterialStatus: requestMaterialPreview?.status ?? null,
      requestMaterialBlockers: requestMaterialPreview?.blockers ?? [],
      requestMaterialWarnings: requestMaterialPreview?.warnings ?? [],
      hasRequestMaterialPreviewError: Boolean(requestMaterialError),
      officialFolderCheckStatus: officialFolderCheckPreview?.status ?? null,
      officialFolderCheckBlockers: officialFolderCheckPreview?.blockers ?? [],
      officialFolderCheckWarnings: officialFolderCheckPreview?.warnings ?? [],
      hasOfficialFolderCheckError: Boolean(officialFolderCheckError),
      publicDrivePreviewStatus: publicDriveUploadPreview?.status ?? null,
      publicDrivePreviewBlockers: publicDriveUploadPreview?.blockers ?? [],
      publicDrivePreviewWarnings: publicDriveUploadPreview?.warnings ?? [],
      hasPublicDrivePreviewError: Boolean(publicDriveUploadError),
      section2Status: section2SyncPreview?.status ?? null,
      hasPackagePreviewError: Boolean(packagePreviewError),
      lifecycleReadonlyView,
    }
  );
  const lifecycleActions = deriveProjectWorkbenchLifecycleActions(
    runtimeModel.lifecycle,
    lifecycleReadonlyView,
    { hasRegisteredProject: Boolean(projectNumber) }
  );
  const projectFolderWorkflowTasks = deriveProjectFolderTasks({
    folderReady: effectiveFolderReady,
    matrixAuthorityReady: Boolean(projectNumber) && activeMatrixAuthorityReady,
    officialFolderCheckPreview,
    requestMaterialPreview,
    requestMaterialError,
    publicFolderWorkflowContext,
    publicFolderWorkflowContextLoading,
    publicFolderWorkflowContextError,
    publicFolderWorkflowPreviews,
    publicFolderWorkflowResults,
    publicFolderWorkflowBusyOperation,
    publicFolderWorkflowConfirmingOperation,
    publicFolderWorkflowError,
    publicFolderWorkflowMessage,
    publicFolderWorkflowAutoSyncBusy,
    requiredFormsPreview,
    requiredFormsError,
    section2SyncPreview,
    versionStatus: runtimeModel.versionStatus,
    confirmedFeeAuthorityStatus: deriveConfirmedFeeAuthorityStatus(confirmedFeeLatest),
    lifecycleReadonlyReason: lifecycleReadonlyView.readonly
      ? lifecycleReadonlyView.message
      : null,
  });
  const isActiveMatrixWorkspace = activeMatrixAuthorityReady;
  const shellModel = deriveProjectWorkbenchShellModel({
    projectIdentity: titleParts.join(" "),
    hasRegisteredProject: Boolean(projectNumber),
    latestLtr: projectNumber,
    hasActiveMatrix: activeMatrixAuthorityReady,
    hasCandidateMatrix: Boolean(matrixCandidateDraft ?? matrixDraft),
    folderReady: effectiveFolderReady,
    basicInformationStatus: deriveBasicInformationShellStatus(
      runtimeModel.basicInformation
    ),
    packageStatus: packagePreview?.status ?? null,
    requiredFormsStatus: requiredFormsPreview?.status ?? null,
    confirmedFeeStatus: confirmedFeeLatest?.status ?? null,
    publicDriveStatus: publicDriveUploadPreview?.status ?? null,
    lifecycle: runtimeModel.lifecycle,
    lifecycleReadonlyView,
  });
  const activeMatrixFolderCommand = deriveActiveMatrixFolderCommand({
    activeMatrixAuthorityReady,
    confirmedFeeLatest,
    creatingFolder: officialWorkspaceCreating,
    projectFolderBlocker:
      officialWorkspacePreview?.blockers?.find((blocker) =>
        blocker.includes("Basic Information")
      ) ?? selectProjectFolderOneClickBlocker(projectFolderWorkflowTasks, effectiveFolderReady),
  });
  const visibleActiveMatrixFolderCommand = lifecycleReadonlyView.readonly
    ? {
        ...activeMatrixFolderCommand,
        disabled: true,
        disabledReason: lifecycleReadonlyView.message,
      }
    : activeMatrixFolderCommand;
  const feeEvaluationButtonState = deriveFeeEvaluationButtonState(confirmedFeeLatest);
  const officialWorkspaceConflictPaths =
    deriveOfficialWorkspaceConflictPaths(officialWorkspacePreview);
  const basicInformationGenerationGuidance = deriveBasicInformationGenerationGuidance(
    officialWorkspaceError,
    runtimeModel.basicInformation
  );
  const isBasicInformationGenerationBlocker = Boolean(
    basicInformationGenerationGuidance
  );
  // A persisted failure is history until the initial recovery preview has settled.
  // Derive the initial pending state during render so no error paints before the effect runs.
  const checkingRecoveryPreview = Boolean(
    officialWorkspaceCanRestart && recoveryPreviewCheckedProject !== project.project_id
  );
  const workspaceStatus = officialWorkspacePreview?.status ?? "ready";
  const initialWorkspaceResourceBlocker =
    workspaceStatus === "blocked"
      ? officialWorkspacePreview?.blockers.find(isSettingsTemplateResourceBlocker) ?? null
      : null;
  const displayedOfficialWorkspaceError =
    basicInformationGenerationGuidance
    ?? folderRelocationError
    ?? officialWorkspaceError
    ?? initialWorkspaceResourceBlocker;
  const isSettingsTemplateGenerationBlocker = Boolean(
    displayedOfficialWorkspaceError
    && isSettingsTemplateResourceBlocker(displayedOfficialWorkspaceError)
  );
  const hasMatrixDraftForPlanning =
    activeMatrixAuthorityReady || Boolean(matrixCandidateDraft ?? matrixDraft);
  const visibleFeeEvaluationButtonState =
    lifecycleReadonlyView.readonly
      ? {
          className: feeEvaluationButtonState.className,
          disabled: true,
          title: lifecycleReadonlyView.message,
        }
      : !isActiveMatrixWorkspace && !hasMatrixDraftForPlanning
      ? {
          className: feeEvaluationButtonState.className,
          disabled: true,
          title: "Create or import a Matrix draft before opening Fee Evaluation.",
        }
      : {
          ...feeEvaluationButtonState,
          disabled: false,
        };
  const visibleWorkbenchFolderCommand = isActiveMatrixWorkspace && Boolean(projectNumber)
    ? visibleActiveMatrixFolderCommand
    : {
        disabled: true,
        disabledReason: !projectNumber
          ? "LTR registration is required before project folder outputs can be prepared."
          : "Active Matrix authority is required before project folder outputs can be prepared.",
      };
  const projectFolderTasks = projectFolderWorkflowTasks;
  const projectFolderHeaderAction = {
    label:
      workspaceStatus === "completed"
        ? "Create folder"
        : workspaceStatus === "adoptable"
        ? "Link existing folder"
        : ["conflict", "exists", "inconsistent"].includes(workspaceStatus)
        ? "Review folder"
        : "Create folder",
    disabled:
      checkingRecoveryPreview
      || officialWorkspaceCreating
      || folderRelocationBusy
      || lifecycleReadonlyView.readonly
      || Boolean(initialWorkspaceResourceBlocker)
      || (["ready", "blocked"].includes(workspaceStatus) && visibleWorkbenchFolderCommand.disabled),
    title: checkingRecoveryPreview
      ? "Checking project folder generation status..."
      : initialWorkspaceResourceBlocker ?? visibleWorkbenchFolderCommand.disabledReason,
    onClick: () => {
      if (workspaceStatus === "adoptable") {
        void performFolderUpdate("adopt_existing");
      } else {
        handleProjectFolderCreateClick();
      }
    },
  };

  useEffect(() => {
    let cancelled = false;
    if (project.status === "cancelled" || projectNumber) {
      setDeletePreview(null);
      return;
    }
    previewTemporaryProjectDelete(project.project_id)
      .then((preview) => {
        if (!cancelled) {
          setDeletePreview(preview);
          setLifecycleError(null);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setDeletePreview(null);
          setLifecycleError((err as Error).message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [project.project_id, project.status, projectNumber]);

  async function handleActivateProject(reason: string): Promise<void> {
    setLifecycleBusy(true);
    try {
      await onActivateLifecycle(reason);
      setLifecycleError(null);
    } catch (err) {
      setLifecycleError((err as Error).message);
    } finally {
      setLifecycleBusy(false);
    }
  }

  async function handleCloseProject(
    reasonCategory: ProjectCloseReasonCategory,
    note: string
  ): Promise<void> {
    setLifecycleBusy(true);
    try {
      await onCloseLifecycle(reasonCategory, note);
      setLifecycleError(null);
    } catch (err) {
      setLifecycleError((err as Error).message);
    } finally {
      setLifecycleBusy(false);
    }
  }

  async function handleDeleteTemporaryProject(): Promise<void> {
    if (!deletePreview?.can_delete) {
      return;
    }
    if (
      !window.confirm(
        "Delete this mistaken temporary project from ConnLab? This does not touch public-drive files or LTR workbooks."
      )
    ) {
      return;
    }
    setLifecycleBusy(true);
    try {
      await deleteTemporaryProject(project.project_id);
      setLifecycleError(null);
      onBack();
    } catch (err) {
      setLifecycleError((err as Error).message);
    } finally {
      setLifecycleBusy(false);
    }
  }

  function handleProjectFolderTaskAction(
    actionTarget: ProjectFolderTaskActionTarget
  ): void {
    if (lifecycleReadonlyView.readonly && isProjectFolderWriteAction(actionTarget)) {
      setLifecycleError(lifecycleReadonlyView.message);
      return;
    }
    if (actionTarget === "folder") {
      handleProjectFolderCreateClick();
      return;
    }
    if (actionTarget === "project_folder_open") {
      void onOpenLocalProjectFolder();
      return;
    }
    if (actionTarget === "request_material") {
      void onCollectRequestMaterial();
      return;
    }
    if (actionTarget === "fee") {
      onOpenFeeEvaluation();
      return;
    }
    if (actionTarget === "required_forms_generate") {
      void onGenerateRequiredForms();
      return;
    }
    if (actionTarget === "required_forms_refresh") {
      void onRefreshRequiredForms();
      return;
    }
    if (actionTarget === "official_folder_repair") {
      void onRepairOfficialFolderStructure();
      return;
    }
    if (actionTarget === "official_folder_refresh") {
      void onRefreshOfficialFolderCheck();
      return;
    }
    if (actionTarget === "public_folder_workflow_sync") {
      void onPreviewPublicFolderWorkflowOperation("sync");
      return;
    }
    if (actionTarget === "public_folder_workflow_submit") {
      void onPreviewPublicFolderWorkflowOperation("submit");
      return;
    }
    if (actionTarget === "public_folder_workflow_pull") {
      void onPreviewPublicFolderWorkflowOperation("pull");
    }
  }

  function handleProjectFolderTaskConfirm(
    operation: PublicFolderWorkflowOperationType
  ): void {
    void onConfirmPublicFolderWorkflowOperation(operation);
  }

  function handleProjectFolderTaskCancel(
    operation: PublicFolderWorkflowOperationType
  ): void {
    onCancelPublicFolderWorkflowOperation(operation);
  }

  function handleProjectFolderCreateClick(): void {
    if (lifecycleReadonlyView.readonly) {
      setLifecycleError(lifecycleReadonlyView.message);
      return;
    }
    if (workspaceStatus === "completed") {
      void performFolderUpdate("backup_and_recreate");
    } else if (["conflict", "exists", "inconsistent"].includes(workspaceStatus)) {
      void performFolderRelocationReview();
    } else {
      void performFolderUpdate();
    }
  }

  const currentFolderProject = useRef(project.project_id);
  currentFolderProject.current = project.project_id;
  useEffect(() => {
    setShowFolderConflictDialog(false);
    setFolderUpdateReview(null);
    setFolderRelocationReview(null);
    setFolderRelocationError(null);
    setFolderRelocationBusy(false);
    setFolderNameUpdatedNotice(false);
    folderRelocationInFlight.current = false;
  }, [project.project_id]);

  async function performFolderRelocationReview(): Promise<void> {
    if (folderRelocationInFlight.current) return;
    folderRelocationInFlight.current = true;
    setFolderRelocationBusy(true);
    setFolderRelocationError(null);
    try {
      const result = await fetchOfficialWorkspaceRelocationPreview(project.project_id);
      if (currentFolderProject.current !== project.project_id) return;
      if (result.status === "not_needed") {
        void performFolderUpdate();
      } else {
        setFolderRelocationReview(result);
      }
    } catch {
      if (currentFolderProject.current === project.project_id) {
        setFolderRelocationError("Unable to check the project folder. Verify local storage and try again.");
      }
    } finally {
      if (currentFolderProject.current === project.project_id) {
        folderRelocationInFlight.current = false;
        setFolderRelocationBusy(false);
      }
    }
  }

  async function handleFolderRelocationChoice(action: OfficialWorkspaceRelocationAction): Promise<void> {
    if (!folderRelocationReview || folderRelocationInFlight.current) return;
    folderRelocationInFlight.current = true;
    setFolderRelocationBusy(true);
    setFolderRelocationError(null);
    try {
      const fresh = await fetchOfficialWorkspaceRelocationPreview(project.project_id);
      if (currentFolderProject.current !== project.project_id) return;
      if (!folderRelocationReview.expected_context || fresh.expected_context !== folderRelocationReview.expected_context) {
        throw new Error("Project folder preview changed. Review the latest folder state before choosing again.");
      }
      if (fresh.blockers.length || !fresh.actions.some(item => item.key === action)) {
        throw new Error("This folder action is no longer available. Review the latest folder state.");
      }
      const operation = await getProjectFolderGeneration(project.project_id);
      if (currentFolderProject.current !== project.project_id) return;
      if (operation && ["queued", "running"].includes(operation.status)) {
        throw new Error("Project folder generation is still running. Wait for it to finish before changing the folder.");
      }
      try {
        await relocateOfficialWorkspace(project.project_id, { action, expected_context: fresh.expected_context });
      } catch {
        throw new Error("The folder change needs review. Refresh the page to check its current state before trying again.");
      }
      if (currentFolderProject.current !== project.project_id) return;
      setFolderRelocationReview(null);
      if (action === "rename_to_confirmed" || action === "rebind_and_rename") {
        setFolderNameUpdatedNotice(true);
      }
      try {
        await Promise.all([onRefreshOfficialWorkspacePreview(), onRefreshRequiredForms(),
          onRefreshOfficialFolderCheck(), onRefreshPublicFolderWorkflowContext()]);
        if (action === "keep_current_name" || action === "rebind_keep_custom") {
          await performFolderUpdate();
        }
      } catch {
        setFolderRelocationError("Folder updated, but its displayed status could not refresh. Refresh this page to reconnect.");
      }
    } catch (err) {
      if (currentFolderProject.current === project.project_id) setFolderRelocationError((err as Error).message);
    } finally {
      if (currentFolderProject.current === project.project_id) {
        folderRelocationInFlight.current = false;
        setFolderRelocationBusy(false);
      }
    }
  }

  async function performFolderUpdate(strategy?: ProjectFolderUpdateAction, reviewed?: FolderUpdateReview, resumeRebuild = false): Promise<void> {
    if (lifecycleReadonlyView.readonly) {
      setLifecycleError(lifecycleReadonlyView.message);
      return;
    }
    const result = await onUpdateOfficialWorkspace(strategy, reviewed, resumeRebuild);
    if (currentFolderProject.current !== project.project_id) return;
    if (result) {
      setFolderUpdateReview(result);
      setShowFolderConflictDialog(true);
    }
  }

  function handleProjectFolderConflictChoice(
    strategy: OfficialWorkspaceConflictStrategy
  ): void {
    setShowFolderConflictDialog(false);
    if (folderUpdateReview) {
      void performFolderUpdate(strategy, folderUpdateReview);
      return;
    }
  }

  const runtimeConsoleTopbar = (
    <div className="runtime-console-topbar">
      <div className="runtime-console-app-title">
        <button
          aria-label="Back to projects"
          className="runtime-console-menu-button"
          title="Back to Projects overview"
          type="button"
          onClick={onBack}
        >
          <UiIcon name="project-overview" />
        </button>
      </div>
      <section className="runtime-console-project-state" aria-label="Project State">
        <div className="runtime-console-project-title">
          <h2 className="runtime-console-project-identity">
            {shellModel.projectIdentity}
          </h2>
        </div>
      </section>
      <div className="runtime-console-commandbar-actions" aria-label="Project Workbench actions">
        {!lifecycleReadonlyView.readonly ? (
          <button type="button" onClick={onOpenMatrixEditor}>
            Matrix Editor
          </button>
        ) : null}
        <button
          type="button"
          className={visibleFeeEvaluationButtonState.className}
          disabled={visibleFeeEvaluationButtonState.disabled}
          title={visibleFeeEvaluationButtonState.title}
          onClick={onOpenFeeEvaluation}
        >
          Fee Evaluation
        </button>
        <button type="button" onClick={onOpenBasicInformation}>
          Basic Information
        </button>
        <TestReportDraftButton onOpen={onOpenReportWorkspace} />
      </div>
    </div>
  );

  return (
    <section className="runtime-console-shell" aria-label="Project runtime console">
      {topBarActionsRoot ? createPortal(runtimeConsoleTopbar, topBarActionsRoot) : runtimeConsoleTopbar}

      {checkingRecoveryPreview ? (
        <div className="runtime-console-workflow-alert" role="status" aria-busy="true">
          <strong>Project folder workflow</strong>
          <span>Checking project folder generation status...</span>
        </div>
      ) : displayedOfficialWorkspaceError ? (
        <div
          className="runtime-console-workflow-alert is-danger"
          role="alert"
        >
          <strong>Project folder workflow</strong>
          <span>{displayedOfficialWorkspaceError?.replace(/\s*\[Stage:[\s\S]*$/, "")}</span>
          {displayedOfficialWorkspaceError?.includes("[Stage:") ? <details><summary>Diagnostic details</summary><span>{displayedOfficialWorkspaceError.slice(displayedOfficialWorkspaceError.indexOf("[Stage:"))}</span></details> : null}
          {isBasicInformationGenerationBlocker &&
          runtimeModel.basicInformation?.status !== "confirmed" ? (
            <button type="button" onClick={onOpenBasicInformation}>
              Open Basic Information
            </button>
          ) : null}
          {!isBasicInformationGenerationBlocker && isSettingsTemplateGenerationBlocker ? (
            <button type="button" onClick={onOpenSettings}>
              Open Settings
            </button>
          ) : null}
          <span>After resolving the issue, use the project folder action in Folder Actions.</span>
        </div>
      ) : null}

      {folderNameUpdatedNotice ? (
        <div className="runtime-console-workflow-alert" role="status" aria-label="Folder name updated">
          <strong>Folder name updated</strong>
          <span>Review Update existing folder to refresh generated outputs such as Fee Form and Customer Feedback. Renaming alone does not regenerate their contents.</span>
          <button type="button" disabled={officialWorkspaceCreating || folderRelocationBusy || lifecycleReadonlyView.readonly}
            onClick={() => void performFolderUpdate()}>Review update existing folder</button>
          <button type="button" onClick={() => setFolderNameUpdatedNotice(false)}>Dismiss</button>
        </div>
      ) : null}

      <section
        className={`runtime-console-shell-primary workspace-${shellModel.primaryWorkspace}`}
        aria-label="Matrix"
      >
        {shellModel.primaryWorkspace === "readonly_archive" ? (
          <div className="runtime-console-region-heading" role="status">
            <h3>{shellModel.primaryWorkspaceLabel}</h3>
            <strong>{lifecycleReadonlyView.title}</strong>
            <p>Read-only project</p>
            <p>{lifecycleReadonlyView.message}</p>
          </div>
        ) : null}
        {isActiveMatrixWorkspace ? (
          <>
            <ProjectWorkbenchActiveMatrixWorkspace
              effectiveFolderReady={effectiveFolderReady}
              officialWorkspaceStatus={officialWorkspacePreview?.status}
              onProjectFolderTaskAction={handleProjectFolderTaskAction}
              onProjectFolderTaskConfirm={handleProjectFolderTaskConfirm}
              onProjectFolderTaskCancel={handleProjectFolderTaskCancel}
              onPublicFolderAutoSyncChange={(enabled) =>
                void onSetPublicFolderWorkflowAutoSync(enabled)
              }
              projectFolderTasks={projectFolderTasks}
              projectFolderHeaderAction={projectFolderHeaderAction}
              projectId={project.project_id}
              registeredLtrNumber={projectNumber}
              runtimeProjectionSnapshot={runtimeProjectionSnapshot}
              selectedProjectionToken={selectedProjectionToken}
              setSelectedProjectionToken={setSelectedProjectionToken}
              basicInformation={runtimeModel.basicInformation}
              basicInformationLoading={runtimeModel.basicInformationLoading}
              basicInformationError={runtimeModel.basicInformationError}
              lifecycleReadonlyView={lifecycleReadonlyView}
            />
            <ProjectLifecycleManagementPanel
              allowDelete={false}
              compactBottom
              deletePreview={null}
              lifecycleActions={lifecycleActions}
              lifecycleBusy={lifecycleBusy}
              lifecycleError={lifecycleError}
              outputStatusSummary={outputStatusSummary}
              onDeleteTemporaryProject={() => undefined}
              onActivateProject={(reason) => void handleActivateProject(reason)}
              onCloseProject={(reasonCategory, note) =>
                void handleCloseProject(reasonCategory, note)
              }
              projectIdentity={titleParts.join(" ")}
              projectReference={projectNumber}
            />
          </>
        ) : (
          <>
            <NoMatrixWorkspaceEmptyState
              projectFolderTasks={projectFolderTasks}
              projectFolderHeaderAction={projectFolderHeaderAction}
              matrixDraft={matrixCandidateDraft ?? matrixDraft ?? null}
              onProjectFolderTaskAction={handleProjectFolderTaskAction}
              onProjectFolderTaskConfirm={handleProjectFolderTaskConfirm}
              onProjectFolderTaskCancel={handleProjectFolderTaskCancel}
              onPublicFolderAutoSyncChange={(enabled) =>
                void onSetPublicFolderWorkflowAutoSync(enabled)
              }
              readonlyReason={
                lifecycleReadonlyView.readonly ? lifecycleReadonlyView.message : undefined
              }
            />
            <ProjectLifecycleManagementPanel
              allowDelete={lifecycle.mode === "temporary_planning"}
              compactBottom={shellModel.primaryWorkspace !== "readonly_archive"}
              deletePreview={lifecycle.mode === "temporary_planning" ? deletePreview : null}
              lifecycleActions={lifecycleActions}
              lifecycleBusy={lifecycleBusy}
              lifecycleError={lifecycleError}
              outputStatusSummary={outputStatusSummary}
              onDeleteTemporaryProject={
                lifecycle.mode === "temporary_planning"
                  ? () => void handleDeleteTemporaryProject()
                  : () => undefined
              }
              onActivateProject={(reason) => void handleActivateProject(reason)}
              onCloseProject={(reasonCategory, note) =>
                void handleCloseProject(reasonCategory, note)
              }
              projectIdentity={titleParts.join(" ")}
              projectReference={projectNumber}
            />
          </>
        )}
      </section>

      {showFolderConflictDialog ? (
        <ProjectFolderConflictDialog
          resumeRebuild={folderUpdateReview?.resumeRebuild ?? false}
          intent={folderUpdateReview?.intent ?? "backup_rebuild"}
          onResumeRebuild={() => { setShowFolderConflictDialog(false); if (folderUpdateReview) void performFolderUpdate(undefined, folderUpdateReview, true); }}
          conflictPaths={folderUpdateReview ? deriveOfficialWorkspaceConflictPaths(folderUpdateReview.preview.workspace_preview) : officialWorkspaceConflictPaths}
          newFolderPath={folderUpdateReview?.preview.workspace_preview.official_project_folder_path ?? null}
          onBackup={() => handleProjectFolderConflictChoice("backup_and_recreate")}
          onUpdateInPlace={() => handleProjectFolderConflictChoice("update_in_place")}
          onCancel={() => setShowFolderConflictDialog(false)}
        />
      ) : null}
      {folderRelocationReview ? (
        <ProjectFolderRelocationDialog
          preview={folderRelocationReview}
          busy={folderRelocationBusy}
          error={folderRelocationError}
          onChoose={(action) => void handleFolderRelocationChoice(action)}
          onCancel={() => setFolderRelocationReview(null)}
        />
      ) : null}
      {officialWorkspaceCreating ? (
        <ProjectFolderProgressDialog currentStep={officialWorkspaceProgressLabel} />
      ) : null}
    </section>
  );
}

function isProjectFolderWriteAction(actionTarget: ProjectFolderTaskActionTarget): boolean {
  if (!actionTarget) {
    return false;
  }
  return [
    "folder",
    "request_material",
    "required_forms_generate",
    "official_folder_repair",
    "public_folder_workflow_sync",
    "public_folder_workflow_submit",
    "public_folder_workflow_pull",
  ].includes(actionTarget);
}

function deriveBasicInformationShellStatus(
  basicInformation: ProjectRuntimeConsoleModel["basicInformation"]
): "confirmed" | "draft" | "missing" | "unknown" {
  if (!basicInformation) {
    return "missing";
  }
  if (basicInformation.latest_confirmed) {
    return "confirmed";
  }
  if (basicInformation.draft) {
    return "draft";
  }
  return "unknown";
}

function deriveBasicInformationGenerationGuidance(
  workflowError: string | null,
  basicInformation: ProjectRuntimeConsoleModel["basicInformation"]
): string | null {
  if (!workflowError?.includes("Basic Information") || !basicInformation) {
    return null;
  }
  if (basicInformation.missing_required_labels.length > 0) {
    return `Basic Information is incomplete. Complete these required fields before generating Project Folder outputs: ${basicInformation.missing_required_labels.join(", ")}.`;
  }
  if (basicInformation.status === "needs_review") {
    return "Basic Information source data changed after confirmation. Review and confirm the current Basic Information before generating Project Folder outputs.";
  }
  if (basicInformation.status === "unconfirmed") {
    return "Basic Information is complete but not confirmed. Open Basic Information and click Confirm before generating Project Folder outputs.";
  }
  return "Basic Information is now confirmed. Refresh the generation preview and start a new generation.";
}

function isSettingsTemplateResourceBlocker(message: string): boolean {
  const normalized = message.toLowerCase();
  return (
    normalized.includes("template")
    || normalized.includes("save location")
    || normalized.includes("settings")
  );
}

function deriveOfficialWorkspaceConflictPaths(
  preview: ProjectRuntimeConsoleModel["officialWorkspacePreview"]
): string[] {
  if (!preview) {
    return [];
  }
  if (preview.conflict_paths?.length) {
    return preview.conflict_paths;
  }
  if (preview.status === "completed" && preview.official_project_folder_path) {
    return [preview.official_project_folder_path];
  }
  return [];
}

function deriveFeeEvaluationButtonState(
  confirmedFeeLatest: ProjectRuntimeConsoleModel["confirmedFeeLatest"]
): {
  className?: string;
  title?: string;
} {
  const reviewCount = confirmedFeeLatest?.fee_review_required_count ?? 0;
  if (reviewCount <= 0) {
    return {};
  }
  return {
    className: "is-review-required",
    title: `${reviewCount} Fee Evaluation row${reviewCount === 1 ? "" : "s"} need pricing review.`,
  };
}

function ProjectFolderConflictDialog({
  resumeRebuild,
  intent,
  onResumeRebuild,
  conflictPaths,
  newFolderPath,
  onBackup,
  onUpdateInPlace,
  onCancel,
}: {
  resumeRebuild: boolean;
  intent: "backup_rebuild" | "update_in_place";
  onResumeRebuild: () => void;
  conflictPaths: string[];
  newFolderPath: string | null;
  onBackup: () => void;
  onUpdateInPlace: () => void;
  onCancel: () => void;
}): ReactElement {
  const visiblePath = conflictPaths[0] ?? "Existing project folder";
  const extraPathCount = Math.max(conflictPaths.length - 1, 0);
  return (
    <div className="runtime-console-modal-backdrop">
      <section
        aria-label="Project folder already exists"
        aria-modal="true"
        className="runtime-console-conflict-dialog"
        role="dialog"
      >
        <div className="runtime-console-conflict-path">
          <span>Existing folder</span>
          <strong>{visiblePath}</strong>
          {extraPathCount > 0 ? <em>+{extraPathCount} more</em> : null}
        </div>
        {!resumeRebuild && intent === "backup_rebuild" && newFolderPath && newFolderPath !== visiblePath ? (
          <div className="runtime-console-conflict-path">
            <span>New folder from confirmed information</span>
            <strong>{newFolderPath}</strong>
          </div>
        ) : null}
        <p>
          {resumeRebuild
            ? "An earlier generation has unfinished file or cleanup work. Resume its saved progress using the previously confirmed choices; this does not create a new generation."
            : intent === "update_in_place"
            ? "Update generated files inside the current project folder without renaming or archiving the whole folder. Existing file safeguards still apply."
            : "The existing project folder and all its files will move to timestamped History. A new folder will be built from the template and latest confirmed information; old files are not copied into the new folder."}
        </p>
        <div className="runtime-console-conflict-actions">
          {resumeRebuild
            ? <button type="button" className="is-primary" onClick={onResumeRebuild}>Resume previous generation</button>
            : intent === "update_in_place"
            ? <>
                <button type="button" className="is-primary" onClick={onUpdateInPlace}>Update existing folder</button>
                <button type="button" onClick={onBackup}>Backup and Rebuild</button>
              </>
            : <button type="button" className="is-primary" onClick={onBackup}>Backup and Rebuild</button>}
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </section>
    </div>
  );
}

function folderName(path: string | null): string | null {
  if (!path) return null;
  return path.replace(/[\\/]+$/, "").split(/[\\/]/).at(-1) ?? null;
}

function safeRelocationBlocker(message: string): string {
  if (/foreign|ownership|manifest.*(?:project|mismatch)|does not match.*project/i.test(message)) {
    return "Folder ownership does not match this project. Check which project created it.";
  }
  if (/(?:[A-Za-z]:[\\/]|\\\\|(?:^|\s)\/[^\s]|\b[0-9a-f]{32}\b|\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b)/i.test(message)) {
    return "The folder path or identity could not be verified. Review the existing LTR folders manually.";
  }
  return message.replace(/\s*\[Stage:[\s\S]*$/, "");
}

function ProjectFolderRelocationDialog({
  preview, busy, error, onChoose, onCancel,
}: {
  preview: OfficialWorkspaceRelocationPreview;
  busy: boolean;
  error: string | null;
  onChoose: (action: OfficialWorkspaceRelocationAction) => void;
  onCancel: () => void;
}): ReactElement {
  const existingName = folderName(preview.candidate_path ?? preview.current_path);
  const suggestedName = folderName(preview.suggested_path);
  return (
    <div className="runtime-console-modal-backdrop">
      <section aria-label="Review project folder name" aria-modal="true" role="dialog" className="runtime-console-conflict-dialog">
        <h3>Review project folder name</h3>
        {preview.status === "blocked" ? (
          <div role="alert">
            <p>The existing folder cannot be linked safely. No files were changed.</p>
            <ul>{(preview.blockers.length ? preview.blockers : ["Folder ownership or location needs manual review."])
              .map((blocker, index) => <li key={index}>{safeRelocationBlocker(blocker)}</li>)}</ul>
          </div>
        ) : (
          <>
            {existingName ? <div className="runtime-console-conflict-path"><span>Existing folder</span><strong>{existingName}</strong></div> : null}
            {suggestedName ? <div className="runtime-console-conflict-path"><span>Name from confirmed Basic Information</span><strong>{suggestedName}</strong></div> : null}
            <p>{preview.status === "interrupted"
              ? "An earlier folder change was interrupted. Resume its saved progress after reviewing the folder name."
              : "Choose how to keep this project's existing files. Nothing changes until you select an action."}</p>
          </>
        )}
        {error ? <p role="alert">{error}</p> : null}
        <div className="runtime-console-conflict-actions">
          {preview.actions.map(item => (
            <button key={item.key} type="button" className="is-primary" title={item.description} disabled={busy} onClick={() => onChoose(item.key)}>
              {item.label}
            </button>
          ))}
          <button type="button" disabled={busy} onClick={onCancel}>Cancel</button>
        </div>
      </section>
    </div>
  );
}

function ProjectFolderProgressDialog({
  currentStep,
}: {
  currentStep: string | null;
}): ReactElement {
  const visibleStep = currentStep ?? "Preparing project folder files";
  return (
    <div className="runtime-console-modal-backdrop">
      <section
        aria-label="Project folder update in progress"
        aria-live="polite"
        className="runtime-console-conflict-dialog runtime-console-progress-dialog"
        role="dialog"
      >
        <div className="runtime-console-progress-dialog-indicator" aria-hidden="true" />
        <dl className="runtime-console-progress-dialog-step">
          <div>
            <dt>Current step</dt>
            <dd>{visibleStep}</dd>
          </div>
        </dl>
      </section>
    </div>
  );
}

function deriveFolderTemplateReady(
  template: ProjectRuntimeConsoleModel["folderResources"]["template"]
): boolean {
  if (!template) {
    return false;
  }
  return template.active && template.validation_status === "valid";
}

function deriveConfirmedFeeAuthorityStatus(
  confirmedFeeLatest: ProjectRuntimeConsoleModel["confirmedFeeLatest"]
): "missing" | "confirmed" | "stale" | "unknown" {
  if (!confirmedFeeLatest) {
    return "unknown";
  }
  if (confirmedFeeLatest.status === "current") {
    return "confirmed";
  }
  if (confirmedFeeLatest.status === "stale") {
    return "stale";
  }
  return "missing";
}
