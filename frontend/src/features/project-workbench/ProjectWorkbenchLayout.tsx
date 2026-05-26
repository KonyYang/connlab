import { useState, type ReactElement } from "react";
import type { Project } from "../../api/client";
import { ProjectWorkbenchMatrixProjectionPanel } from "./ProjectWorkbenchMatrixProjectionPanel";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

type ProjectWorkbenchLayoutProps = {
  runtimeModel: ProjectRuntimeConsoleModel;
  project: Project;
  onBack: () => void;
  onOpenMatrixEditor: () => void;
};

type MockStepDetail = {
  reference: string;
  group: string;
  token: string;
  title: string;
  status: "FAILED" | "IN PROGRESS" | "PASS" | "NOT STARTED";
};

type SetupMaterialItem = {
  title: string;
  value: string;
  placeholder?: boolean;
};

const DEFAULT_STEP_DETAIL: MockStepDetail = {
  reference: "mock:G3:2",
  group: "Group 3",
  token: "2",
  title: "Step 2 - LLCR",
  status: "FAILED",
};

const MOCK_STEP_DETAILS: MockStepDetail[] = [
  DEFAULT_STEP_DETAIL,
  {
    reference: "mock:G2:2",
    group: "Group 2",
    token: "2",
    title: "Step 2 - LLCR",
    status: "IN PROGRESS",
  },
  {
    reference: "mock:G5:1",
    group: "Group 5",
    token: "1",
    title: "Step 1 - Examination",
    status: "PASS",
  },
];

const STEP_STATUS_BY_TONE: Record<
  MatrixProjectionTokenCell["statusTone"],
  MockStepDetail["status"]
> = {
  not_started: "NOT STARTED",
  in_progress: "IN PROGRESS",
  passed: "PASS",
  failed: "FAILED",
  review: "IN PROGRESS",
  retest: "IN PROGRESS",
};

const MOCK_STATUS_BY_TONE: Record<
  MatrixProjectionTokenCell["statusTone"],
  MockStepDetail["status"]
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
}: ProjectWorkbenchLayoutProps): ReactElement {
  const [selectedProjectionToken, setSelectedProjectionToken] =
    useState<MatrixProjectionTokenCell | null>(null);
  const {
    folderReady,
    latestLtr,
    matrixAuthorityDraft,
    runtimeProjectionSnapshot,
    runtimeSelectedTokenReference,
  } = runtimeModel;
  const projectIdentity =
    latestLtr ?? `Temporary project ${project.project_id.slice(0, 8)}`;
  const testDescription = deriveWorkbenchTestDescription(
    matrixAuthorityDraft?.source_document_name ?? null
  );
  const headerIdentityLine = `${projectIdentity} · ${project.product_name} · ${testDescription}`;
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
    { title: "Sample images", value: "Future evidence input", placeholder: true },
    { title: "Approval package", value: "Future output package", placeholder: true },
  ];

  const selectedWorkspace = runtimeProjectionSnapshot?.step_workspace ?? null;
  const selectedProjectionStatus = selectedProjectionToken
    ? STEP_STATUS_BY_TONE[selectedProjectionToken.statusTone]
    : null;
  const fallbackMockStepDetail =
    MOCK_STEP_DETAILS.find(
      (item) => item.reference === runtimeSelectedTokenReference
    ) ?? DEFAULT_STEP_DETAIL;
  const mockStepDetail = selectedProjectionToken
    ? {
        ...fallbackMockStepDetail,
        group: selectedProjectionToken.groupLabel,
        token: selectedProjectionToken.rawToken,
        title: `Step ${selectedProjectionToken.rawToken} - ${selectedProjectionToken.testItem}`,
        status: MOCK_STATUS_BY_TONE[selectedProjectionToken.statusTone],
      }
    : fallbackMockStepDetail;
  const activeStepTitle = selectedProjectionToken
    ? `Step ${selectedProjectionToken.rawToken} - ${selectedProjectionToken.testItem}`
    : selectedWorkspace?.selected_token?.test_item_label
      ? `Step ${selectedWorkspace.selected_token.raw_token} - ${selectedWorkspace.selected_token.test_item_label}`
      : mockStepDetail.title;

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
                <p className="runtime-console-step-breadcrumb">
                  {mockStepDetail.group} · Step {mockStepDetail.token}
                </p>
                <h3>{activeStepTitle}</h3>
              </div>
            </header>

            <section className="runtime-console-step-status-card runtime-console-step-status-compact">
              <div>
                <span>Lifecycle status</span>
                <strong
                  className={`runtime-console-step-status-${mockStepDetail.status
                    .toLowerCase()
                    .replace(/\s+/g, "-")}`}
                >
                  {selectedProjectionStatus ??
                    selectedWorkspace?.selected_token?.lifecycle_projection?.toUpperCase() ??
                    mockStepDetail.status}
                </strong>
              </div>
            </section>

            {selectedProjectionToken ? (
              <StepExecutionContent
                method={selectedProjectionToken.method}
                condition={selectedProjectionToken.condition}
                requirement={selectedProjectionToken.requirement}
              />
            ) : selectedWorkspace?.selected_token ? (
              <StepExecutionContent
                method={selectedWorkspace.selected_token.method}
                condition={selectedWorkspace.selected_token.condition}
                requirement={selectedWorkspace.selected_token.requirement}
              />
            ) : (
              <StepExecutionContent
                method="EIA-364-23E"
                condition="20mV max, 100mA max"
                requirement="Initial: <= 0.40mO; After test: <= 0.40mO"
              />
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
              <textarea placeholder="Pending judgement input" />
            </label>
          </aside>
          <FeeEstimateSurface />
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

function FeeEstimateSurface(): ReactElement {
  return (
    <section className="runtime-console-fee" aria-label="Fee estimate">
      <header>
        <p className="eyebrow">Fee estimate</p>
        <h3>Total estimated fee</h3>
      </header>
      <div className="runtime-console-fee-grid">
        <div>
          <span>Total</span>
          <strong>Pending estimate</strong>
        </div>
      </div>
    </section>
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
