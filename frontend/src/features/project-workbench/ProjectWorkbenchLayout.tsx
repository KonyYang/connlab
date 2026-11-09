import { useEffect, useRef, useState, type ReactElement } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import {
  deleteTemporaryProject,
  openPublicProjectFolder,
  previewTemporaryProjectDelete,
  type PublicFolderWorkflowOperationType,
  type ProjectCloseReasonCategory,
  type Project,
  type TemporaryProjectDeletePreview,
} from "../../api/client";
import { ProjectManagementDialog } from "../projects-registry/ProjectRegistryManagementDialog";
import { ProjectPublicFolderBindingDialog } from "./ProjectPublicFolderBindingDialog";
import { UiIcon } from "../../components/common/UiIcon";
import {
  ProjectWorkbenchActiveMatrixWorkspace,
} from "./ProjectWorkbenchActiveMatrixWorkspace";
import {
  NoMatrixWorkspaceEmptyState,
  ProjectLifecycleManagementPanel,
} from "./ProjectWorkbenchLifecycleSections";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import {
  deriveProjectFolderTasks,
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
import { TemporaryProjectRegistrationDialog } from "./TemporaryProjectRegistrationDialog";
import { ProjectBasicInformationSummaryCard } from "../project-basic-information/ProjectBasicInformationSummaryCard";

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
  const [showBasicFolderReview, setShowBasicFolderReview] = useState(false);
  const [showRegistration, setShowRegistration] = useState(false);
  const [publicFolderOpenError, setPublicFolderOpenError] = useState<string | null>(null);
  const [recoveryPreviewCheckedProject, setRecoveryPreviewCheckedProject] = useState<string | null>(null);
  const topBarActionsRoot = useTopBarActionsRoot();

  const {
    basicWorkspace,
    publicFolderBinding,
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
    basicWorkspace?.directoryAvailable ?? folderReady;
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
    publicFolderWorkflowError: publicFolderOpenError ?? publicFolderWorkflowError,
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
  const feeEvaluationButtonState = deriveFeeEvaluationButtonState(confirmedFeeLatest);
  const legacyRecovery = Boolean(runtimeModel.officialWorkspaceCanResume);
  const checkingRecoveryPreview = Boolean(legacyRecovery && officialWorkspaceCanRestart && recoveryPreviewCheckedProject !== project.project_id);
  const displayedOfficialWorkspaceError = basicWorkspace?.error
    ?? (!lifecycleReadonlyView.readonly && basicWorkspace?.preview?.status === "blocked" ? basicWorkspace.preview.blockers.join("\n") : null)
    ?? (legacyRecovery ? officialWorkspaceError : null);
  const folderAlert = deriveProjectFolderAlert(displayedOfficialWorkspaceError ?? "");
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
  const projectFolderTasks = projectFolderWorkflowTasks;
  const basicBlocked = basicWorkspace?.preview?.status === "blocked";
  const projectFolderHeaderAction = {
    label: legacyRecovery ? "Resume folder operation" : "Create folder",
    disabled: lifecycleReadonlyView.readonly || officialWorkspaceCreating || checkingRecoveryPreview
      || Boolean(basicWorkspace?.busy || basicWorkspace?.loading)
      || (!legacyRecovery && (!projectNumber || !basicWorkspace?.preview || basicBlocked)),
    title: lifecycleReadonlyView.readonly ? lifecycleReadonlyView.message
      : !projectNumber ? "LTR registration is required before creating a project folder."
      : basicBlocked ? basicWorkspace?.preview?.blockers.join("\n") : undefined,
    onClick: handleProjectFolderCreateClick,
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
    if (lifecycleBusy) return;
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
    if (actionTarget === "public_project_folder_open") {
      setPublicFolderOpenError(null);
      const targetProjectId = project.project_id;
      void openPublicProjectFolder(targetProjectId).then((result) => {
        if (currentFolderProject.current !== targetProjectId) return;
        if (result.status !== "opened") setPublicFolderOpenError(result.message);
      }).catch((error: unknown) => {
        if (currentFolderProject.current !== targetProjectId) return;
        setPublicFolderOpenError(error instanceof Error ? error.message : "Could not open the public folder.");
      });
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
    if (legacyRecovery) {
      void runtimeModel.onResumeLegacyWorkspace?.();
    } else if (basicWorkspace?.preview?.status === "review_required") {
      setShowBasicFolderReview(true);
    } else {
      void basicWorkspace?.create();
    }
  }

  const currentFolderProject = useRef(project.project_id);
  currentFolderProject.current = project.project_id;
  useEffect(() => {
    setShowBasicFolderReview(false);
    setPublicFolderOpenError(null);
    setShowRegistration(false);
  }, [project.project_id]);

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
        {lifecycle.mode === "temporary_planning" && !lifecycleReadonlyView.readonly ? (
          <button type="button" title="Apply a formal LTR number and keep this project's data" onClick={() => setShowRegistration(true)}>
            Apply LTR Number
          </button>
        ) : null}
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
      {showRegistration ? <TemporaryProjectRegistrationDialog key={project.project_id} projectId={project.project_id}
        onClose={() => setShowRegistration(false)} onRegistered={async () => {
          await runtimeModel.onRefreshLifecycle(true);
          setShowRegistration(false);
          void basicWorkspace?.refresh();
        }} /> : null}
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
          <span>{folderAlert.guidance}</span>
          {folderAlert.diagnostic ? <details><summary>Diagnostic details</summary><span>{folderAlert.diagnostic}</span></details> : null}
          <span>After resolving the issue, use the project folder action in Folder Actions.</span>
        </div>
      ) : null}

      {basicWorkspace?.directoryAvailable && basicWorkspace.result?.issues.length ? <div className="runtime-console-workflow-alert is-danger" role="alert">
        <strong>Project folder is available; some materials could not be archived.</strong>
        <ul>{basicWorkspace.result.issues.map((issue, index) => <li key={index}>{issue}</li>)}</ul>
      </div> : null}
      {showBasicFolderReview && basicWorkspace?.preview?.project_id === project.project_id && basicWorkspace.preview.status === "review_required" ? <ProjectManagementDialog title="Use existing project folder" busy={basicWorkspace.busy} onCancel={() => setShowBasicFolderReview(false)}>
        <p className="project-basic-folder-path">{basicWorkspace.folderPath}</p>
        <p>Confirm this is this project's folder. Existing files will be kept.</p>
        <div className="project-management-dialog-actions">
          <button className="secondary-action ui-secondary-action" type="button" disabled={basicWorkspace.busy} onClick={() => setShowBasicFolderReview(false)}>Cancel</button>
          <button className="primary-action ui-primary-action" type="button" disabled={basicWorkspace.busy} onClick={() => { setShowBasicFolderReview(false); void basicWorkspace.create(true); }}>Use this folder</button>
        </div>
      </ProjectManagementDialog> : null}
      {publicFolderBinding?.preview ? <ProjectPublicFolderBindingDialog key={`${project.project_id}:${publicFolderBinding.preview.expected_context}`}
        preview={publicFolderBinding.preview} busy={publicFolderBinding.busy} error={publicFolderBinding.error}
        onConfirm={publicFolderBinding.onConfirm} onCancel={publicFolderBinding.onCancel} /> : null}

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
              closeActionHost={topBarActionsRoot}
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
              showPlaceholderSteps={!project.library_member_id}
              ltrInformation={
                <ProjectBasicInformationSummaryCard
                  projectId={project.project_id}
                  basicInformation={runtimeModel.basicInformation}
                  registeredLtrNumber={projectNumber}
                  loading={runtimeModel.basicInformationLoading}
                  error={runtimeModel.basicInformationError}
                />
              }
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
              closeActionHost={topBarActionsRoot}
              compactBottom
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

      {officialWorkspaceCreating ? (
        <ProjectFolderProgressDialog currentStep={officialWorkspaceProgressLabel} />
      ) : null}
    </section>
  );
}

function deriveProjectFolderAlert(message: string): { guidance: string; diagnostic: string | null } {
  // Only the backend's complete diagnostic suffix is metadata. Other bracketed
  // operator guidance remains part of the primary message.
  const suffix = message.match(/\s*(\[(?:(?:Windows error|Office HRESULT): -?\d+; )?Stage: [A-Za-z0-9_-]+; Diagnostic ID: [A-Za-z0-9_-]+\])$/);
  const primary = suffix ? message.slice(0, suffix.index).trim() : message;
  const legacyArchiveMessage = "Windows denied access to the existing project folder. "
    + "Check permissions or file locks, then resume, or start a new generation and "
    + "choose a rebuild option after resolving file access.";
  return {
    guidance: primary === legacyArchiveMessage
      ? "The existing project folder could not be moved to History. "
        + "Close documents opened from this folder and File Explorer windows or tabs "
        + "viewing this folder or its subfolders, then click Create folder again. "
        + "If it still fails, check your permission to move the folder."
      : primary,
    diagnostic: suffix?.[1] ?? null,
  };
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
