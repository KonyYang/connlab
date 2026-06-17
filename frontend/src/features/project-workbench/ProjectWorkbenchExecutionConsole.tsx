import type { ReactElement, ReactNode } from "react";
import { ProjectWorkbenchMatrixProjectionPanel } from "./ProjectWorkbenchMatrixProjectionPanel";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

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

export function ProjectWorkbenchExecutionConsole({
  projectId,
  runtimeProjectionSnapshot,
  selectedProjectionToken,
  setSelectedProjectionToken,
  sideColumnAfter,
}: {
  projectId: string;
  runtimeProjectionSnapshot: ProjectRuntimeConsoleModel["runtimeProjectionSnapshot"];
  selectedProjectionToken: MatrixProjectionTokenCell | null;
  setSelectedProjectionToken: (token: MatrixProjectionTokenCell | null) => void;
  sideColumnAfter?: ReactNode;
}): ReactElement {
  const selectedWorkspace = runtimeProjectionSnapshot?.step_workspace ?? null;
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
    <section className="runtime-console-workspace">
      <div className="runtime-console-main">
        <ProjectWorkbenchMatrixProjectionPanel
          projectId={projectId}
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
            <StepExecutionEmptyState />
          )}

          <p className="runtime-console-step-supporting">
            Data import and image evidence will be available after step records are implemented.
          </p>

          <label className="runtime-console-note-box">
            Result judgement
            <textarea readOnly disabled value="Result judgement is not available yet." />
          </label>
        </aside>
        {sideColumnAfter}
      </div>
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
        Execution evidence, charts, and attachments will be managed after step
        records are implemented.
      </p>
    </>
  );
}

function StepExecutionEmptyState(): ReactElement {
  return (
    <p className="runtime-console-step-supporting">
      Select a Matrix step to view method, condition, requirement, and execution
      context.
    </p>
  );
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
