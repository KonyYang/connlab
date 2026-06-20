import { useEffect, useState, type ReactElement } from "react";
import {
  deleteTemporaryProject,
  type OfficialWorkspaceConflictStrategy,
  previewTemporaryProjectDelete,
  stopProject,
  type Project,
  type TemporaryProjectDeletePreview,
} from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import {
  deriveActiveMatrixFolderCommand,
  ProjectWorkbenchActiveMatrixWorkspace,
} from "./ProjectWorkbenchActiveMatrixWorkspace";
import {
  ProjectLifecycleManagementPanel,
  RegisteredSetupMode,
  TemporaryPlanningMode,
  WorkbenchModeTabs,
  WorkbenchStageBanner,
} from "./ProjectWorkbenchLifecycleSections";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import {
  deriveProjectFolderTasks,
  selectCurrentProjectFolderTaskKey,
  type ProjectFolderTaskActionTarget,
} from "./projectFolderTaskSelectors";
import {
  deriveProjectWorkbenchLifecycle,
  type WorkbenchLifecycleMode,
} from "./projectWorkbenchLifecycleSelectors";
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

  const projectNumber = deriveProjectNumber(latestLtr, project.project_no);
  const activeMatrixAuthorityReady = Boolean(activeConfirmedMatrixSnapshot);
  const effectiveFolderReady =
    folderReady || officialWorkspacePreview?.status === "completed";
  const projectIdentity =
    projectNumber ?? temporaryProjectId(project.project_id);
  const titleParts = [
    projectIdentity,
    project.sample_description?.trim() || project.product_name,
    project.test_item,
  ].filter(Boolean);
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
    },
    selectedLifecycleMode
  );
  const projectFolderTasks = deriveProjectFolderTasks({
    folderReady: effectiveFolderReady,
    matrixAuthorityReady: activeMatrixAuthorityReady,
    officialFolderCheckPreview,
    requestMaterialPreview,
    requestMaterialError,
    publicDriveUploadPreview,
    publicDriveUploadError,
    requiredFormsPreview,
    requiredFormsError,
    section2SyncPreview,
    versionStatus: runtimeModel.versionStatus,
    confirmedFeeAuthorityStatus: deriveConfirmedFeeAuthorityStatus(confirmedFeeLatest),
  });
  const currentProjectFolderTaskKey = selectCurrentProjectFolderTaskKey(projectFolderTasks);
  const isActiveMatrixWorkspace =
    Boolean(projectNumber) && activeMatrixAuthorityReady;
  const activeMatrixFolderCommand = deriveActiveMatrixFolderCommand({
    activeMatrixAuthorityReady,
    confirmedFeeLatest,
    creatingFolder: officialWorkspaceCreating,
    effectiveFolderReady,
    officialWorkspaceStatus: officialWorkspacePreview?.status,
  });
  const feeEvaluationButtonState = deriveFeeEvaluationButtonState(confirmedFeeLatest);
  const officialWorkspaceConflictPaths =
    deriveOfficialWorkspaceConflictPaths(officialWorkspacePreview);
  const hasOfficialWorkspaceConflict =
    effectiveFolderReady ||
    officialWorkspaceConflictPaths.length > 0 ||
    officialWorkspacePreview?.status === "exists" ||
    officialWorkspacePreview?.status === "completed";

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

  async function handleStopProject(): Promise<void> {
    const reason = window.prompt(
      "Reason for stopping this project",
      "Project will not continue."
    );
    if (reason === null) {
      return;
    }
    if (!window.confirm("Stop this project and keep its history for review?")) {
      return;
    }
    setLifecycleBusy(true);
    try {
      await stopProject(project.project_id, {
        reason,
        operator: null,
      });
      setLifecycleError(null);
      onBack();
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
    if (actionTarget === "public_drive_refresh") {
      void onRefreshPublicDriveUploadPreview();
      return;
    }
    if (actionTarget === "public_drive_upload") {
      void onUploadPublicDriveProjectFolder();
    }
  }

  function handleProjectFolderCreateClick(): void {
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
        <div className="runtime-console-project-title">
          <h2 className="runtime-console-project-identity">
            {titleParts.join(" ")}
          </h2>
        </div>
        {isActiveMatrixWorkspace ? (
          <div className="runtime-console-commandbar-actions" aria-label="Project Workbench actions">
            <button type="button" onClick={onOpenMatrixEditor}>
              Matrix Editor
            </button>
            <button
              type="button"
              className={feeEvaluationButtonState.className}
              title={feeEvaluationButtonState.title}
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
              disabled={activeMatrixFolderCommand.disabled}
              title={activeMatrixFolderCommand.disabledReason}
              onClick={handleProjectFolderCreateClick}
            >
              {activeMatrixFolderCommand.label}
            </button>
          </div>
        ) : (
          <div className="runtime-console-last-update">
            <button
              type="button"
              disabled
              title="Activity history is a planned future surface."
            >
              View activity history
            </button>
          </div>
        )}
      </header>

      {officialWorkspaceError ? (
        <div className="runtime-console-workflow-alert is-danger" role="alert">
          <strong>Project folder workflow</strong>
          <span>{officialWorkspaceError}</span>
        </div>
      ) : null}

      {isActiveMatrixWorkspace ? (
        <ProjectWorkbenchActiveMatrixWorkspace
          effectiveFolderReady={effectiveFolderReady}
          officialWorkspaceStatus={officialWorkspacePreview?.status}
          onProjectFolderTaskAction={handleProjectFolderTaskAction}
          projectFolderTasks={projectFolderTasks}
          projectId={project.project_id}
          currentProjectFolderTaskKey={currentProjectFolderTaskKey}
          runtimeProjectionSnapshot={runtimeProjectionSnapshot}
          selectedProjectionToken={selectedProjectionToken}
          setSelectedProjectionToken={setSelectedProjectionToken}
          basicInformation={runtimeModel.basicInformation}
          basicInformationLoading={runtimeModel.basicInformationLoading}
          basicInformationError={runtimeModel.basicInformationError}
        />
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

          {lifecycle.mode === "temporary_planning" ? (
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
              onStopProject={() => void handleStopProject()}
              onDeleteTemporaryProject={() => void handleDeleteTemporaryProject()}
              promotionMessage={temporaryPromotionMessage}
            />
          ) : null}

          {lifecycle.mode === "registered_setup" ? (
            <RegisteredSetupMode
              hasCandidateMatrix={Boolean(matrixCandidateDraft ?? matrixDraft)}
              onOpenMatrixEditor={onOpenMatrixEditor}
            />
          ) : null}

          {lifecycle.mode !== "temporary_planning" && project.status !== "cancelled" ? (
            <ProjectLifecycleManagementPanel
              allowDelete={false}
              deletePreview={null}
              lifecycleBusy={lifecycleBusy}
              lifecycleError={lifecycleError}
              onDeleteTemporaryProject={() => undefined}
              onStopProject={() => void handleStopProject()}
            />
          ) : null}
        </>
      )}
      {showFolderConflictDialog ? (
        <ProjectFolderConflictDialog
          conflictPaths={officialWorkspaceConflictPaths}
          onBackup={() => handleProjectFolderConflictChoice("backup_and_recreate")}
          onCancel={() => setShowFolderConflictDialog(false)}
          onOverwrite={() => handleProjectFolderConflictChoice("overwrite_rebuild")}
        />
      ) : null}
    </section>
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

function deriveFolderTemplateReady(
  template: ProjectRuntimeConsoleModel["folderResources"]["template"]
): boolean {
  if (!template) {
    return false;
  }
  return template.active && template.validation_status === "valid";
}

function deriveProjectNumber(
  latestLtr: string | null | undefined,
  projectNo: string | null | undefined
): string | null {
  const fromLatestLtr = latestLtr?.trim();
  if (fromLatestLtr) {
    return fromLatestLtr;
  }
  const fromProjectNo = projectNo?.trim();
  return fromProjectNo || null;
}

function temporaryProjectId(projectId: string): string {
  return `TMP-${projectId.slice(0, 8).toUpperCase()}`;
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
