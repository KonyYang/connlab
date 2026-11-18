import type { ReactElement, ReactNode } from "react";
import { ProjectWorkbenchMatrixProjectionPanel } from "./ProjectWorkbenchMatrixProjectionPanel";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

import { StepReportEvidence } from '../report-workspace/StepReportEvidence';

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
    selectedProjectionToken?.evidenceStep?.token ?? selectedProjectionToken?.rawToken ?? selectedWorkspaceToken?.raw_token ?? null;
  const selectedStepItemLabel =
    selectedProjectionToken?.testItem ?? selectedWorkspaceToken?.test_item_label ?? null;
  const stepContextLine =
    hasSelectedStep &&
    selectedGroupLabel &&
    selectedStepToken &&
    selectedStepItemLabel
      ? `${normalizeStepWorkspaceGroupLabel(selectedGroupLabel)} Step ${selectedStepToken}: ${selectedStepItemLabel}`
      : "Select a Matrix step from the Matrix table";
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
              <p className="eyebrow">Step Actions</p>
              <p className="runtime-console-step-breadcrumb">{stepContextLine}</p>
            </div>
          </header>

          {selectedProjectionToken?.evidenceStep ? <StepReportEvidence projectId={projectId} step={selectedProjectionToken.evidenceStep} />
            : hasSelectedStep && <p>Report evidence unavailable without a confirmed step identity.</p>}

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
      </dl>
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

function normalizeStepWorkspaceGroupLabel(groupLabel: string): string {
  const normalized = groupLabel.trim();
  if (/^group\b/i.test(normalized)) {
    return `Group ${normalized.replace(/^group\b[:\s-]*/i, "").trim()}`.trim();
  }
  return `Group ${normalized}`;
}
