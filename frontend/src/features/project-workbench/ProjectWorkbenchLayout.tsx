import { useState, type ReactElement } from "react";
import type { Project } from "../../api/client";
import { FeeEvaluationStatusSummary } from "./FeeEvaluationStatusSummary";
import { ProjectFolderCreationPanel } from "./ProjectFolderCreationPanel";
import { ProjectSection2SyncPanel } from "./ProjectSection2SyncPanel";
import { ProjectWorkbenchMatrixProjectionPanel } from "./ProjectWorkbenchMatrixProjectionPanel";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

type ProjectWorkbenchLayoutProps = {
  runtimeModel: ProjectRuntimeConsoleModel;
  project: Project;
  onBack: () => void;
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
};

type SetupMaterialItem = {
  title: string;
  value: string;
  placeholder?: boolean;
};

type StepLifecycleStatus = "FAILED" | "IN PROGRESS" | "PASS" | "NOT STARTED";

const STEP_STATUS_BY_TONE: Record<
  MatrixProjectionTokenCell["statusTone"],
  StepLifecycleStatus
> = {
  not_started: "NOT STARTED",
  in_progress: "IN PROGRESS",
  passed: "PASS",
  failed: "FAILED",
  review: "IN PROGRESS",
  retest: "IN PROGRESS",
};

export function ProjectWorkbenchLayout({
  runtimeModel,
  project,
  onBack,
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
}: ProjectWorkbenchLayoutProps): ReactElement {
  const [selectedProjectionToken, setSelectedProjectionToken] =
    useState<MatrixProjectionTokenCell | null>(null);
  const {
    folderReady,
    folderResources,
    latestLtr,
    matrixAuthorityDraft,
    onFolderCreated,
    onRefreshSection2Sync,
    onSyncSection2,
    runtimeProjectionSnapshot,
    section2SyncError,
    section2SyncLoading,
    section2SyncPreview,
    section2SyncSyncing,
  } = runtimeModel;
  const projectIdentity =
    latestLtr ?? `Temporary project ${project.project_id.slice(0, 8)}`;
  const testDescription = deriveWorkbenchTestDescription(
    matrixAuthorityDraft?.source_document_name ?? null
  );
  const headerIdentityLine = `${projectIdentity} | ${project.product_name} | ${testDescription}`;
  const setupMaterials: SetupMaterialItem[] = [
    { title: "Project folder", value: folderReady ? "Created" : "Not recorded" },
    {
      title: "Source materials",
      value: folderReady
        ? "Available from project folder"
        : "Available after folder creation",
    },
    {
      title: "Test Record",
      value: matrixAuthorityDraft
        ? "Ready for draft generation"
        : "Ready after Matrix confirmation",
      placeholder: !matrixAuthorityDraft,
    },
    {
      title: "Fee Evaluation",
      value: matrixAuthorityDraft ? "Ready for review" : "Ready after Matrix confirmation",
      placeholder: !matrixAuthorityDraft,
    },
    { title: "Approval package", value: "Future output package", placeholder: true },
  ];

  const selectedWorkspace = runtimeProjectionSnapshot?.step_workspace ?? null;
  const feeEvaluationOutputStatus =
    runtimeModel.versionStatus.downstream.find(
      (item) => item.key === "fee_evaluation"
    ) ?? null;
  const selectedWorkspaceToken = selectedWorkspace?.selected_token ?? null;
  const hasSelectedStep =
    selectedProjectionToken !== null || selectedWorkspaceToken !== null;
  const selectedGroupLabel =
    selectedProjectionToken?.groupLabel ?? selectedWorkspace?.group_label ?? null;
  const selectedStepToken =
    selectedProjectionToken?.rawToken ?? selectedWorkspaceToken?.raw_token ?? null;
  const selectedStepItemLabel =
    selectedProjectionToken?.testItem ?? selectedWorkspaceToken?.test_item_label ?? null;
  const stepContextLine =
    hasSelectedStep &&
    selectedGroupLabel &&
    selectedStepToken &&
    selectedStepItemLabel
      ? `${normalizeStepWorkspaceGroupLabel(selectedGroupLabel)} Step ${selectedStepToken}: ${selectedStepItemLabel}`
      : "Select a Matrix step from the Matrix table";
  const displayLifecycleStatus = selectedProjectionToken
    ? STEP_STATUS_BY_TONE[selectedProjectionToken.statusTone]
    : normalizeLifecycleStatus(selectedWorkspaceToken?.lifecycle_projection);
  const lifecycleStatusClassSuffix = displayLifecycleStatus
    .toLowerCase()
    .replace(/\s+/g, "-");

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
          <h2 className="runtime-console-project-identity">{headerIdentityLine}</h2>
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

      <section
        className="runtime-console-readiness"
        aria-label="Project setup and output materials"
      >
        <div className="runtime-console-readiness-title">
          <p className="eyebrow">Project setup / output materials</p>
          <strong>Preparation</strong>
        </div>
        {setupMaterials.map((item) => (
          <RuntimeSetupItem key={item.title} item={item} />
        ))}
      </section>

      <ProjectFolderCreationPanel
        configuredOutputRoot={folderResources.outputRoot}
        configuredTemplate={folderResources.template}
        folderReady={folderReady}
        latestLtrNumber={latestLtr}
        onFolderCreated={onFolderCreated}
        projectId={project.project_id}
        projectStatus={project.status}
      />

      <ProjectSection2SyncPanel
        preview={section2SyncPreview}
        loading={section2SyncLoading}
        syncing={section2SyncSyncing}
        error={section2SyncError}
        onRefresh={onRefreshSection2Sync}
        onSync={onSyncSection2}
      />

      <section className="runtime-console-workspace">
        <div className="runtime-console-main">
          <ProjectWorkbenchMatrixProjectionPanel
            projectId={project.project_id}
            onOpenMatrixEditor={onOpenMatrixEditor}
            onTokenSelect={setSelectedProjectionToken}
          />
        </div>

        <div className="runtime-console-side-column">
          <aside className="runtime-console-step-workspace" aria-label="Step workspace">
            <header>
              <div>
                <p className="eyebrow">Step Workspace</p>
                <p className="runtime-console-step-breadcrumb">{stepContextLine}</p>
              </div>
            </header>

            <section className="runtime-console-step-status-card runtime-console-step-status-compact">
              <div>
                <span>Lifecycle status</span>
                {hasSelectedStep ? (
                  <strong
                    className={`runtime-console-step-status-${lifecycleStatusClassSuffix}`}
                  >
                    {displayLifecycleStatus}
                  </strong>
                ) : (
                  <strong className="runtime-console-step-status-empty">
                    Select a Matrix step
                  </strong>
                )}
              </div>
            </section>

            {selectedProjectionToken ? (
              <StepExecutionContent
                method={selectedProjectionToken.method}
                condition={selectedProjectionToken.condition}
                requirement={selectedProjectionToken.requirement}
              />
            ) : selectedWorkspaceToken ? (
              <StepExecutionContent
                method={selectedWorkspaceToken.method}
                condition={selectedWorkspaceToken.condition}
                requirement={selectedWorkspaceToken.requirement}
              />
            ) : (
              <StepExecutionPlaceholder />
            )}

            <div className="runtime-console-step-actions">
              <button disabled type="button">
                Import data
              </button>
              <button disabled type="button">
                Image
              </button>
            </div>

            <label className="runtime-console-note-box">
              Result judgement
              <textarea
                readOnly
                disabled
                value="Pending result judgement placeholder (read-only in this task)."
              />
            </label>
          </aside>
          <FeeEvaluationStatusSummary
            projectId={project.project_id}
            outputStatus={feeEvaluationOutputStatus}
            canOpen={Boolean(matrixAuthorityDraft)}
            onOpenFeeEvaluation={onOpenFeeEvaluation}
          />
        </div>
      </section>
    </section>
  );
}

function StepExecutionContent({
  method,
  condition,
  requirement,
}: {
  method: string;
  condition: string;
  requirement: string;
}): ReactElement {
  return (
    <>
      <dl className="runtime-console-step-facts">
        <div>
          <dt>Method</dt>
          <dd>{method}</dd>
        </div>
        <div>
          <dt>Condition</dt>
          <dd>{condition}</dd>
        </div>
        <div>
          <dt>Requirement</dt>
          <dd>{requirement}</dd>
        </div>
        <div>
          <dt>Estimated completion</dt>
          <dd>Not scheduled</dd>
        </div>
        <div>
          <dt>Actual completion</dt>
          <dd>Pending execution data</dd>
        </div>
      </dl>
      <p className="runtime-console-step-supporting">
        Execution evidence, charts, and attachments stay read-only placeholders
        in this task.
      </p>
    </>
  );
}

function StepExecutionPlaceholder(): ReactElement {
  return (
    <p className="runtime-console-step-supporting">
      Select a Matrix step to view method, condition, requirement, and execution
      placeholders.
    </p>
  );
}

function RuntimeSetupItem({ item }: { item: SetupMaterialItem }): ReactElement {
  const ready = !item.placeholder;
  return (
    <article className="runtime-console-readiness-item">
      <span
        className={
          ready
            ? "runtime-console-state-dot runtime-console-state-ready"
            : "runtime-console-state-dot"
        }
      />
      <div>
        <strong>{item.title}</strong>
        <p>{item.value}</p>
      </div>
    </article>
  );
}

function deriveWorkbenchTestDescription(sourceDocumentName: string | null): string {
  const normalized = sourceDocumentName?.trim() ?? "";
  if (normalized.length > 0) {
    return normalized;
  }
  return "Test description unavailable";
}

function normalizeLifecycleStatus(
  lifecycle: string | null | undefined
): StepLifecycleStatus {
  const normalized = (lifecycle ?? "").trim().toLowerCase().replace(/[\s-]+/g, "_");
  if (normalized === "failed" || normalized === "fail") {
    return "FAILED";
  }
  if (normalized === "pass" || normalized === "passed") {
    return "PASS";
  }
  if (
    normalized === "in_progress" ||
    normalized === "progress" ||
    normalized === "review" ||
    normalized === "retest"
  ) {
    return "IN PROGRESS";
  }
  return "NOT STARTED";
}

function normalizeStepWorkspaceGroupLabel(groupLabel: string): string {
  const normalized = groupLabel.trim();
  if (/^group\b/i.test(normalized)) {
    return `Group ${normalized.replace(/^group\b[:\s-]*/i, "").trim()}`.trim();
  }
  return `Group ${normalized}`;
}
