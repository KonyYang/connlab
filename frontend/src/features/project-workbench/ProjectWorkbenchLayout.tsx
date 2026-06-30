import { useEffect, useState, type ReactElement } from "react";
import {
  deleteTemporaryProject,
  type OfficialWorkspaceConflictStrategy,
  previewTemporaryProjectDelete,
  type PublicFolderWorkflowOperationType,
  type ProjectCloseReasonCategory,
  type Project,
  type TemporaryProjectDeletePreview,
} from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import {
  deriveActiveMatrixFolderCommand,
  ProjectWorkbenchActiveMatrixWorkspace,
} from "./ProjectWorkbenchActiveMatrixWorkspace";
import {
  NoMatrixWorkspaceEmptyState,
  ProjectLifecycleManagementPanel,
  RegisteredSetupMode,
  TemporaryPlanningMode,
  WorkbenchModeTabs,
  WorkbenchStageBanner,
} from "./ProjectWorkbenchLifecycleSections";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import {
  deriveProjectFolderTasks,
  selectProjectFolderOneClickBlocker,
  selectCurrentProjectFolderTaskKey,
  type ProjectFolderTaskActionTarget,
} from "./projectFolderTaskSelectors";
import {
  deriveProjectWorkbenchLifecycle,
  deriveProjectWorkbenchLifecycleActions,
  type WorkbenchLifecycleMode,
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

type ProjectWorkbenchLayoutProps = {
  runtimeModel: ProjectRuntimeConsoleModel;
  project: Project;
  onBack: () => void;
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
  onOpenBasicInformation: () => void;
  onOpenSettings: () => void;
};

export function ProjectWorkbenchLayout({
  runtimeModel,
  project,
  onBack,
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
  onOpenBasicInformation,
  onOpenSettings,
}: ProjectWorkbenchLayoutProps): ReactElement {
  const [selectedProjectionToken, setSelectedProjectionToken] =
    useState<MatrixProjectionTokenCell | null>(null);
  const [selectedLifecycleMode, setSelectedLifecycleMode] =
    useState<WorkbenchLifecycleMode | null>(null);
  const [temporaryPromotionMessage, setTemporaryPromotionMessage] =
    useState<string | null>(null);
  const [deletePreview, setDeletePreview] =
    useState<TemporaryProjectDeletePreview | null>(null);
  const [lifecycleBusy, setLifecycleBusy] = useState(false);
  const [lifecycleError, setLifecycleError] = useState<string | null>(null);
  const [showFolderConflictDialog, setShowFolderConflictDialog] = useState(false);

  const {
    activeConfirmedMatrixSnapshot,
    folderReady,
    folderResources,
    latestLtr,
    matrixCandidateDraft,
    matrixDraft,
    onRefreshPackagePreview,
    packagePreview,
    packagePreviewError,
    officialWorkspacePreview,
    officialWorkspaceCreating,
    officialWorkspaceProgressLabel,
    officialWorkspaceError,
    onCreateOfficialWorkspace,
    officialFolderCheckPreview,
    officialFolderCheckError,
    onRefreshOfficialFolderCheck,
    onRepairOfficialFolderStructure,
    publicDriveUploadPreview,
    publicDriveUploadLoading,
    publicDriveUploading,
    publicDriveUploadError,
    onRefreshPublicDriveUploadPreview,
    onUploadPublicDriveProjectFolder,
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
    },
    selectedLifecycleMode
  );
  const lifecycleActions = deriveProjectWorkbenchLifecycleActions(
    runtimeModel.lifecycle,
    lifecycleReadonlyView,
    { hasRegisteredProject: Boolean(projectNumber) }
  );
  const projectFolderTasks = deriveProjectFolderTasks({
    folderReady: effectiveFolderReady,
    matrixAuthorityReady: activeMatrixAuthorityReady,
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
  const currentProjectFolderTaskKey = selectCurrentProjectFolderTaskKey(projectFolderTasks);
  const isActiveMatrixWorkspace =
    Boolean(projectNumber) && activeMatrixAuthorityReady;
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
    effectiveFolderReady,
    officialWorkspaceStatus: officialWorkspacePreview?.status,
    projectFolderBlocker: selectProjectFolderOneClickBlocker(
      projectFolderTasks,
      effectiveFolderReady
    ),
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
  const hasOfficialWorkspaceConflict =
    effectiveFolderReady ||
    officialWorkspaceConflictPaths.length > 0 ||
    officialWorkspacePreview?.status === "exists" ||
    officialWorkspacePreview?.status === "completed";
  const isNoMatrixUnifiedWorkspace =
    shellModel.primaryWorkspace === "matrix_setup" ||
    shellModel.primaryWorkspace === "temporary_planning";
  const showWorkbenchActionBar = isActiveMatrixWorkspace || isNoMatrixUnifiedWorkspace;
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
  const visibleWorkbenchFolderCommand = isActiveMatrixWorkspace
    ? visibleActiveMatrixFolderCommand
    : {
        label:
          effectiveFolderReady || officialWorkspacePreview?.status === "completed"
            ? "Update project folder"
            : "Create project folder",
        disabled: true,
        disabledReason:
          "Active Matrix authority is required before project folder outputs can be prepared.",
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
    if (hasOfficialWorkspaceConflict) {
      setShowFolderConflictDialog(true);
      return;
    }
    void onCreateOfficialWorkspace();
  }

  function handleProjectFolderConflictChoice(
    strategy: OfficialWorkspaceConflictStrategy
  ): void {
    setShowFolderConflictDialog(false);
    void onCreateOfficialWorkspace(strategy);
  }

  return (
    <section className="runtime-console-shell" aria-label="Project runtime console">
      <header className="runtime-console-topbar">
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
        {showWorkbenchActionBar ? (
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
            <button
              type="button"
              className="is-primary"
              disabled={visibleWorkbenchFolderCommand.disabled}
              title={visibleWorkbenchFolderCommand.disabledReason}
              onClick={handleProjectFolderCreateClick}
            >
              {visibleWorkbenchFolderCommand.label}
            </button>
          </div>
        ) : null}
      </header>

      {officialWorkspaceError ? (
        <div className="runtime-console-workflow-alert is-danger" role="alert">
          <strong>Project folder workflow</strong>
          <span>{officialWorkspaceError}</span>
        </div>
      ) : null}

      <section
        className={`runtime-console-shell-primary workspace-${shellModel.primaryWorkspace}`}
        aria-label="Matrix"
      >
        {shellModel.primaryWorkspace === "active_matrix" ||
        isNoMatrixUnifiedWorkspace ? null : (
          <div className="runtime-console-region-heading">
            <p className="eyebrow">Matrix</p>
            <h3>{shellModel.primaryWorkspaceLabel}</h3>
            <p>{shellModel.primaryWorkspaceSummary}</p>
          </div>
        )}
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
              projectId={project.project_id}
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
        ) : isNoMatrixUnifiedWorkspace ? (
          <>
            <NoMatrixWorkspaceEmptyState
              projectFolderTasks={projectFolderTasks}
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
        ) : (
          <>
            <WorkbenchStageBanner
              lifecycle={lifecycle}
              onOpenMatrixEditor={onOpenMatrixEditor}
              onOpenFeeEvaluation={onOpenFeeEvaluation}
              onRefreshPackagePreview={onRefreshPackagePreview}
              onCollectRequestMaterial={onCollectRequestMaterial}
              onRefreshOfficialFolderCheck={onRefreshOfficialFolderCheck}
              onRepairOfficialFolderStructure={onRepairOfficialFolderStructure}
              onRefreshPublicDriveUploadPreview={onRefreshPublicDriveUploadPreview}
              onUploadPublicDriveProjectFolder={onUploadPublicDriveProjectFolder}
              onOpenSettings={onOpenSettings}
            />

            <WorkbenchModeTabs
              activeMode={lifecycle.mode}
              tabs={lifecycle.tabs}
              onSelect={setSelectedLifecycleMode}
            />

            {!lifecycleReadonlyView.readonly && lifecycle.mode === "temporary_planning" ? (
              <TemporaryPlanningMode
                deletePreview={deletePreview}
                lifecycleBusy={lifecycleBusy}
                lifecycleError={lifecycleError}
                feePlanningAvailable={Boolean(matrixCandidateDraft ?? matrixDraft)}
                onOpenMatrixEditor={onOpenMatrixEditor}
                onOpenFeeEvaluation={onOpenFeeEvaluation}
                onStartPromotion={() => {
                  setTemporaryPromotionMessage(
                    "Same-project LTR registration is not wired yet. This temporary project stays intact; no duplicate project was created."
                  );
                }}
                lifecycleActions={lifecycleActions}
                outputStatusSummary={outputStatusSummary}
                projectIdentity={titleParts.join(" ")}
                projectReference={projectNumber}
                onActivateProject={(reason) => void handleActivateProject(reason)}
                onCloseProject={(reasonCategory, note) =>
                  void handleCloseProject(reasonCategory, note)
                }
                onDeleteTemporaryProject={() => void handleDeleteTemporaryProject()}
                promotionMessage={temporaryPromotionMessage}
              />
            ) : null}

            {!lifecycleReadonlyView.readonly && lifecycle.mode === "registered_setup" ? (
              <RegisteredSetupMode
                hasCandidateMatrix={Boolean(matrixCandidateDraft ?? matrixDraft)}
                onOpenMatrixEditor={onOpenMatrixEditor}
              />
            ) : null}

            {(lifecycleActions.canClose || lifecycleActions.canActivate) &&
            lifecycle.mode !== "temporary_planning" ? (
              <ProjectLifecycleManagementPanel
                allowDelete={false}
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
            ) : null}
          </>
        )}
      </section>

      {showFolderConflictDialog ? (
        <ProjectFolderConflictDialog
          conflictPaths={officialWorkspaceConflictPaths}
          onBackup={() => handleProjectFolderConflictChoice("backup_and_recreate")}
          onCancel={() => setShowFolderConflictDialog(false)}
          onOverwrite={() => handleProjectFolderConflictChoice("overwrite_rebuild")}
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
  conflictPaths,
  onBackup,
  onCancel,
  onOverwrite,
}: {
  conflictPaths: string[];
  onBackup: () => void;
  onCancel: () => void;
  onOverwrite: () => void;
}): ReactElement {
  const visiblePath = conflictPaths[0] ?? "Existing project folder";
  const extraPathCount = Math.max(conflictPaths.length - 1, 0);
  return (
    <div className="runtime-console-modal-backdrop">
      <section
        aria-label="Project folder already exists"
        className="runtime-console-conflict-dialog"
        role="dialog"
      >
        <div className="runtime-console-conflict-path">
          <span>Existing folder</span>
          <strong>{visiblePath}</strong>
          {extraPathCount > 0 ? <em>+{extraPathCount} more</em> : null}
        </div>
        <div className="runtime-console-conflict-actions">
          <button type="button" onClick={onBackup}>
            Backup and Rebuild
          </button>
          <button type="button" className="is-danger" onClick={onOverwrite}>
            Overwrite
          </button>
          <button type="button" onClick={onCancel}>
            Cancel
          </button>
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
        <div>
          <h3>Project folder update in progress</h3>
          <p>
            ConnLab is preparing the project folder files. Keep this page open until the
            operation finishes.
          </p>
          <dl className="runtime-console-progress-dialog-step">
            <div>
              <dt>Current step</dt>
              <dd>{visibleStep}</dd>
            </div>
          </dl>
          <ul className="runtime-console-progress-dialog-steps" aria-label="Project folder update steps">
            {PROJECT_FOLDER_PROGRESS_STEPS.map((step) => (
              <li className={step === visibleStep ? "is-current" : undefined} key={step}>
                {step}
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}

const PROJECT_FOLDER_PROGRESS_STEPS = [
  "Creating or updating project folder",
  "Archiving request materials",
  "Checking project folder structure",
  "Updating Customer Feedback Form",
  "Updating Fee Form",
  "Updating Test Record",
  "Updating Application Form",
];

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
