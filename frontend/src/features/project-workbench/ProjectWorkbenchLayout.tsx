import { useEffect, useState, type ReactElement } from "react";
import {
  deleteTemporaryProject,
  previewTemporaryProjectDelete,
  stopProject,
  type Project,
  type TemporaryProjectDeletePreview,
} from "../../api/client";
import { ProjectWorkbenchExecutionConsole } from "./ProjectWorkbenchExecutionConsole";
import { OfficialWorkspaceActionPanel } from "./OfficialWorkspaceActionPanel";
import {
  PackagePreparationMode,
  ProjectLifecycleManagementPanel,
  RegisteredSetupMode,
  TemporaryPlanningMode,
  WorkbenchModeTabs,
  WorkbenchStageBanner,
  type SetupMaterialItem,
} from "./ProjectWorkbenchLifecycleSections";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
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
    runtimeProjectionSnapshot,
    section2SyncPreview,
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
  const setupMaterials = buildSetupMaterials({
    folderReady: effectiveFolderReady,
    matrixAuthorityReady: activeMatrixAuthorityReady,
    packagePreview,
    officialFolderCheckPreview,
    requestMaterialPreview,
    publicDriveUploadPreview,
    section2Status: section2SyncPreview?.status ?? null,
  });
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

  return (
    <section className="runtime-console-shell" aria-label="Project runtime console">
      <header className="runtime-console-topbar">
        <div className="runtime-console-app-title">
          <button
            aria-label="Back to projects"
            className="runtime-console-menu-button"
            type="button"
            onClick={onBack}
          >
            <span />
            <span />
            <span />
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
              setupMaterials={setupMaterials}
              requestMaterialPreview={requestMaterialPreview}
              requestMaterialError={requestMaterialError}
              requestMaterialLoading={requestMaterialLoading || requestMaterialCollecting}
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

function buildSetupMaterials({
  folderReady,
  matrixAuthorityReady,
  packagePreview,
  officialFolderCheckPreview,
  requestMaterialPreview,
  publicDriveUploadPreview,
  section2Status,
}: {
  folderReady: boolean;
  matrixAuthorityReady: boolean;
  packagePreview: ProjectRuntimeConsoleModel["packagePreview"];
  officialFolderCheckPreview: ProjectRuntimeConsoleModel["officialFolderCheckPreview"];
  requestMaterialPreview: ProjectRuntimeConsoleModel["requestMaterialPreview"];
  publicDriveUploadPreview: ProjectRuntimeConsoleModel["publicDriveUploadPreview"];
  section2Status: string | null;
}): SetupMaterialItem[] {
  const packageStatus = packagePreview?.status ?? null;
  const confirmedFeeReady =
    packagePreview?.authority_context.confirmed_fee_status === "current" ||
    packagePreview?.authority_context.confirmed_fee_status === "ready";
  const folderStructureStatus = officialFolderCheckPreview?.status ?? null;
  const submittedMaterialItem = officialFolderCheckPreview?.required_files.find(
    (item) => item.key === "submitted_material"
  );
  const customerFeedbackItem = officialFolderCheckPreview?.required_files.find(
    (item) => item.key === "customer_feedback"
  );
  return [
    {
      title: "Project folder",
      value: folderReady ? "Created" : "Not recorded",
      status: folderReady ? "ready" : "blocked",
    },
    {
      title: "Matrix authority",
      value: matrixAuthorityReady ? "Ready" : "Missing",
      status: matrixAuthorityReady ? "ready" : "blocked",
    },
    {
      title: "Request material",
      value: formatRequestMaterialChecklistStatus(requestMaterialPreview?.status ?? null),
      status: normalizeRequestMaterialSetupStatus(requestMaterialPreview?.status ?? null),
    },
    {
      title: "Folder structure",
      value: formatOfficialFolderCheckStatus(folderStructureStatus),
      status: normalizeOfficialFolderSetupStatus(folderStructureStatus),
    },
    {
      title: "Submitted Material",
      value: submittedMaterialItem
        ? formatOfficialFolderItemStatus(submittedMaterialItem.status)
        : "Not checked",
      status: normalizeSetupStatus(submittedMaterialItem?.status ?? null),
    },
    {
      title: "Confirmed Fee",
      value: confirmedFeeReady ? "Ready" : "Blocked",
      status: confirmedFeeReady ? "ready" : "blocked",
    },
    {
      title: "Section 2 dates",
      value: section2Status
        ? formatSection2Status(section2Status)
        : "Refresh readiness before sync",
      status: section2Status === "blocked" ? "blocked" : "neutral",
    },
    {
      title: "Customer Feedback form",
      value: customerFeedbackItem
        ? formatOfficialFolderItemStatus(customerFeedbackItem.status)
        : "Refresh readiness",
      status: normalizeSetupStatus(customerFeedbackItem?.status ?? null),
    },
    {
      title: "Public drive upload",
      value: formatPublicDriveUploadStatus(publicDriveUploadPreview?.status ?? null),
      status: normalizePublicDriveUploadSetupStatus(publicDriveUploadPreview?.status ?? null),
    },
  ];
}

function deriveFolderTemplateReady(
  template: ProjectRuntimeConsoleModel["folderResources"]["template"]
): boolean {
  if (!template) {
    return false;
  }
  return template.active && template.validation_status === "valid";
}

function normalizeSetupStatus(
  status: string | null
): SetupMaterialItem["status"] {
  if (status === "ready") {
    return "ready";
  }
  if (status === "warning" || status === "deferred") {
    return "warning";
  }
  if (status === "blocked") {
    return "blocked";
  }
  return "neutral";
}

function formatPackageItemStatus(status: string): string {
  return status
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatOfficialFolderCheckStatus(status: string | null): string {
  if (status === "ready") {
    return "Ready";
  }
  if (status === "missing") {
    return "Missing folders";
  }
  if (status === "conflict") {
    return "Conflict";
  }
  if (status === "warning") {
    return "Needs review";
  }
  if (status === "blocked") {
    return "Blocked";
  }
  return "Not checked";
}

function normalizeOfficialFolderSetupStatus(
  status: string | null
): SetupMaterialItem["status"] {
  if (status === "ready") {
    return "ready";
  }
  if (status === "missing" || status === "warning") {
    return "warning";
  }
  if (status === "blocked" || status === "conflict") {
    return "blocked";
  }
  return "neutral";
}

function formatOfficialFolderItemStatus(status: string): string {
  if (status === "ready") {
    return "Ready";
  }
  if (status === "missing") {
    return "Missing files";
  }
  if (status === "warning") {
    return "Needs review";
  }
  if (status === "deferred" || status === "not_applicable") {
    return "Deferred";
  }
  if (status === "conflict") {
    return "Conflict";
  }
  return formatPackageItemStatus(status);
}

function formatRequestMaterialChecklistStatus(status: string | null): string {
  if (status === "collected") {
    return "Collected";
  }
  if (status === "ready") {
    return "Ready to collect";
  }
  if (status === "partial") {
    return "Partial";
  }
  if (status === "review_required") {
    return "Needs review";
  }
  if (status === "blocked" || status === "conflict") {
    return "Needs review";
  }
  return "Not checked";
}

function formatPublicDriveUploadStatus(status: string | null): string {
  if (status === "ready") {
    return "Ready to upload";
  }
  if (status === "current") {
    return "Already current";
  }
  if (status === "conflict") {
    return "Conflict";
  }
  if (status === "warning") {
    return "Warning";
  }
  if (status === "blocked") {
    return "Blocked";
  }
  return "Not checked";
}

function normalizePublicDriveUploadSetupStatus(
  status: string | null
): SetupMaterialItem["status"] {
  if (status === "ready" || status === "current") {
    return "ready";
  }
  if (status === "warning") {
    return "warning";
  }
  if (status === "blocked" || status === "conflict") {
    return "blocked";
  }
  return "neutral";
}

function normalizeRequestMaterialSetupStatus(
  status: string | null
): SetupMaterialItem["status"] {
  if (status === "collected") {
    return "ready";
  }
  if (status === "partial" || status === "ready" || status === "review_required") {
    return "warning";
  }
  if (status === "blocked" || status === "conflict") {
    return "blocked";
  }
  return "neutral";
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

function formatSection2Status(status: string): string {
  return status
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
