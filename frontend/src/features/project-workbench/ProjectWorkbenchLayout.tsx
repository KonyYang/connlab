import { useEffect, useState, type ReactElement } from "react";
import {
  deleteTemporaryProject,
  previewTemporaryProjectDelete,
  stopProject,
  type Project,
  type TemporaryProjectDeletePreview,
} from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import { ProjectWorkbenchExecutionConsole } from "./ProjectWorkbenchExecutionConsole";
import { OfficialWorkspaceActionPanel } from "./OfficialWorkspaceActionPanel";
import {
  PackagePreparationMode,
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
  type ProjectFolderTaskKey,
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
  onOpenSettings: () => void;
};

export function ProjectWorkbenchLayout({
  runtimeModel,
  project,
  onBack,
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
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
  const [selectedProjectFolderTaskKey, setSelectedProjectFolderTaskKey] =
    useState<ProjectFolderTaskKey | null>(null);

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
    officialWorkspaceLoading,
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
  const feeEvaluationOutputStatus =
    runtimeModel.versionStatus.downstream.find(
      (item) => item.key === "fee_evaluation"
    ) ?? null;
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
  const effectiveSelectedProjectFolderTaskKey =
    selectedProjectFolderTaskKey &&
    projectFolderTasks.some((task) => task.key === selectedProjectFolderTaskKey)
      ? selectedProjectFolderTaskKey
      : currentProjectFolderTaskKey;
  const shouldShowWorkspaceCreation =
    Boolean(projectNumber) &&
    activeMatrixAuthorityReady &&
    !effectiveFolderReady &&
    (officialWorkspacePreview?.status === "ready" ||
      officialWorkspacePreview?.status === "adoptable" ||
      officialWorkspacePreview?.status === "blocked" ||
      officialWorkspacePreview?.status === "inconsistent");

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
      void onCreateOfficialWorkspace();
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
          <strong>Project Workbench</strong>
        </div>
        <div className="runtime-console-project-title">
          <h2 className="runtime-console-project-identity">
            {titleParts.join(" ")}
          </h2>
        </div>
        <div className="runtime-console-last-update">
          <button
            type="button"
            disabled
            title="Activity history is a planned future surface."
          >
            View activity history
          </button>
        </div>
      </header>

      {shouldShowWorkspaceCreation ? (
        <>
          <OfficialWorkspaceActionPanel
            preview={officialWorkspacePreview}
            loading={officialWorkspaceLoading}
            creating={officialWorkspaceCreating}
            error={officialWorkspaceError}
            onCreate={onCreateOfficialWorkspace}
          />
          {project.status !== "cancelled" ? (
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

          {lifecycle.mode === "package_preparation" ? (
            <PackagePreparationMode
              projectFolderTasks={projectFolderTasks}
              currentProjectFolderTaskKey={currentProjectFolderTaskKey}
              selectedProjectFolderTaskKey={effectiveSelectedProjectFolderTaskKey}
              onSelectProjectFolderTask={setSelectedProjectFolderTaskKey}
              onProjectFolderTaskAction={handleProjectFolderTaskAction}
              requestMaterialPreview={requestMaterialPreview}
              requestMaterialError={requestMaterialError}
              requestMaterialLoading={requestMaterialLoading || requestMaterialCollecting}
              requiredFormsPreview={requiredFormsPreview}
              requiredFormsError={requiredFormsError}
              requiredFormsLoading={requiredFormsLoading || requiredFormsGenerating}
              publicDriveUploadPreview={publicDriveUploadPreview}
              publicDriveUploadError={publicDriveUploadError}
              publicDriveUploadLoading={publicDriveUploadLoading || publicDriveUploading}
            />
          ) : null}

          {lifecycle.mode === "execution_console" ? (
            <ProjectWorkbenchExecutionConsole
              feeEvaluationOutputStatus={feeEvaluationOutputStatus}
              activeMatrixAuthorityReady={activeMatrixAuthorityReady}
              onOpenFeeEvaluation={onOpenFeeEvaluation}
              onOpenMatrixEditor={onOpenMatrixEditor}
              projectId={project.project_id}
              runtimeProjectionSnapshot={runtimeProjectionSnapshot}
              selectedProjectionToken={selectedProjectionToken}
              setSelectedProjectionToken={setSelectedProjectionToken}
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
    </section>
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
