import { useState, type ReactElement } from "react";
import type { Project } from "../../api/client";
import { ProjectWorkbenchExecutionConsole } from "./ProjectWorkbenchExecutionConsole";
import { OfficialWorkspaceActionPanel } from "./OfficialWorkspaceActionPanel";
import {
  PackagePreparationMode,
  ProjectOverviewMode,
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

  const {
    activeConfirmedMatrixSnapshot,
    folderReady,
    folderResources,
    latestLtr,
    matrixCandidateDraft,
    matrixDraft,
    onFolderCreated,
    onRefreshPackagePreview,
    onRefreshSection2Sync,
    onSyncSection2,
    packagePreview,
    packagePreviewError,
    packagePreviewLoading,
    officialWorkspacePreview,
    officialWorkspaceLoading,
    officialWorkspaceCreating,
    officialWorkspaceError,
    onCreateOfficialWorkspace,
    runtimeProjectionSnapshot,
    section2SyncError,
    section2SyncLoading,
    section2SyncPreview,
    section2SyncSyncing,
  } = runtimeModel;

  const projectNumber = deriveProjectNumber(latestLtr, project.project_no);
  const activeMatrixAuthorityReady = Boolean(activeConfirmedMatrixSnapshot);
  const effectiveFolderReady =
    folderReady || officialWorkspacePreview?.status === "completed";
  const projectIdentity =
    projectNumber ?? `Temporary project ${project.project_id.slice(0, 8)}`;
  const titleParts = [
    projectIdentity,
    project.sample_description?.trim() || project.product_name,
    project.test_item,
  ].filter(Boolean);
  const lifecycle = deriveProjectWorkbenchLifecycle(
    {
      hasLtr: Boolean(projectNumber),
      hasActiveMatrix: activeMatrixAuthorityReady,
      hasCandidateMatrix: Boolean(matrixCandidateDraft ?? matrixDraft),
      folderReady: effectiveFolderReady,
      folderTemplateReady: deriveFolderTemplateReady(folderResources.template),
      packageStatus: packagePreview?.status ?? null,
      packageBlockers: packagePreview?.blockers ?? [],
      packageWarnings: packagePreview?.warnings ?? [],
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
        <OfficialWorkspaceActionPanel
          preview={officialWorkspacePreview}
          loading={officialWorkspaceLoading}
          creating={officialWorkspaceCreating}
          error={officialWorkspaceError}
          onCreate={onCreateOfficialWorkspace}
        />
      ) : (
        <>
          <WorkbenchStageBanner
            lifecycle={lifecycle}
            onOpenMatrixEditor={onOpenMatrixEditor}
            onOpenFeeEvaluation={onOpenFeeEvaluation}
            onRefreshPackagePreview={onRefreshPackagePreview}
            onOpenSettings={onOpenSettings}
          />

          <WorkbenchModeTabs
            activeMode={lifecycle.mode}
            tabs={lifecycle.tabs}
            onSelect={setSelectedLifecycleMode}
          />

      {lifecycle.mode === "temporary_planning" ? (
        <TemporaryPlanningMode
          onOpenMatrixEditor={onOpenMatrixEditor}
          onOpenFeeEvaluation={onOpenFeeEvaluation}
        />
      ) : null}

      {lifecycle.mode === "overview" ? (
        <ProjectOverviewMode setupMaterials={setupMaterials} lifecycle={lifecycle} />
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
          folderResources={folderResources}
          folderReady={effectiveFolderReady}
          projectNumber={projectNumber}
          onFolderCreated={onFolderCreated}
          onOpenMatrixEditor={onOpenMatrixEditor}
          onOpenFeeEvaluation={onOpenFeeEvaluation}
          onRefreshPackagePreview={onRefreshPackagePreview}
          onRefreshSection2Sync={onRefreshSection2Sync}
          onSyncSection2={onSyncSection2}
          packagePreview={packagePreview}
          packagePreviewError={packagePreviewError}
          packagePreviewLoading={packagePreviewLoading}
          project={project}
          section2SyncError={section2SyncError}
          section2SyncLoading={section2SyncLoading}
          section2SyncPreview={section2SyncPreview}
          section2SyncSyncing={section2SyncSyncing}
          feeEvaluationOutputStatus={feeEvaluationOutputStatus}
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
        </>
      )}
    </section>
  );
}

function buildSetupMaterials({
  folderReady,
  matrixAuthorityReady,
  packagePreview,
  section2Status,
}: {
  folderReady: boolean;
  matrixAuthorityReady: boolean;
  packagePreview: ProjectRuntimeConsoleModel["packagePreview"];
  section2Status: string | null;
}): SetupMaterialItem[] {
  const packageStatus = packagePreview?.status ?? null;
  const confirmedFeeReady =
    packagePreview?.authority_context.confirmed_fee_status === "current" ||
    packagePreview?.authority_context.confirmed_fee_status === "ready";
  const customerFeedbackItem = packagePreview?.required_items.find(
    (item) => item.key === "customer_feedback_form"
  );
  const customerFeedbackStatus = customerFeedbackItem?.status ?? null;
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
      value: customerFeedbackStatus
        ? formatPackageItemStatus(customerFeedbackStatus)
        : "Refresh readiness",
      status: normalizeSetupStatus(customerFeedbackStatus),
    },
    {
      title: "Submitted Material",
      value:
        packageStatus === "ready" && folderReady
          ? "Ready"
          : packageStatus === "blocked"
            ? "Blocked"
            : "Refresh readiness",
      status: packageStatus === "ready" && folderReady ? "ready" : "blocked",
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

function formatSection2Status(status: string): string {
  return status
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
