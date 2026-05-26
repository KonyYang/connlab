import { useState, type ReactElement } from "react";
import type { Project, RuntimeProjectionSnapshotResponse } from "../../api/client";
import { ProjectWorkbenchMatrixProjectionPanel } from "./ProjectWorkbenchMatrixProjectionPanel";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

type ProjectWorkbenchLayoutProps = {
  runtimeModel: ProjectRuntimeConsoleModel;
  project: Project;
  onBack: () => void;
  onOpenMatrixEditor: () => void;
};

type RuntimeMetric = {
  label: string;
  value: string | number;
  tone: "success" | "danger" | "current" | "warning" | "muted";
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
  status: "FAILED"
};

const MOCK_STEP_DETAILS: MockStepDetail[] = [
  DEFAULT_STEP_DETAIL,
  { reference: "mock:G2:2", group: "Group 2", token: "2", title: "Step 2 - LLCR", status: "IN PROGRESS" },
  { reference: "mock:G5:1", group: "Group 5", token: "1", title: "Step 1 - Examination", status: "PASS" },
  { reference: "mock:G9:6", group: "Group 9", token: "6", title: "Step 6 - Dielectric Withstanding Voltage", status: "PASS" }
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
  onOpenMatrixEditor
}: ProjectWorkbenchLayoutProps): ReactElement {
  const [selectedProjectionToken, setSelectedProjectionToken] =
    useState<MatrixProjectionTokenCell | null>(null);
  const {
    folderReady,
    latestLtr,
    matrixAuthorityDraft,
    runtimeProjectionLoading,
    runtimeProjectionSnapshot,
    runtimeSelectedTokenReference,
  } = runtimeModel;
  const projectIdentity = latestLtr ?? `Temporary project ${project.project_id.slice(0, 8)}`;
  const setupMaterials: SetupMaterialItem[] = [
    { title: "Project folder", value: folderReady ? "Created" : "Not recorded" },
    {
      title: "Source materials",
      value: folderReady ? "Available from project folder" : "Available after folder creation",
    },
    {
      title: "Test Record",
      value: matrixAuthorityDraft ? "Ready for draft generation" : "Ready after Matrix confirmation",
      placeholder: !matrixAuthorityDraft,
    },
    { title: "Fee estimate", value: "Pending estimate", placeholder: true },
    { title: "Sample images", value: "Future evidence input", placeholder: true },
    { title: "Approval package", value: "Future output package", placeholder: true },
  ];

  const runtimeMetrics = buildRuntimeMetrics(runtimeProjectionSnapshot);
  const selectedWorkspace = runtimeProjectionSnapshot?.step_workspace ?? null;
  const selectedProjectionStatus = selectedProjectionToken
    ? STEP_STATUS_BY_TONE[selectedProjectionToken.statusTone]
    : null;
  const fallbackMockStepDetail =
    MOCK_STEP_DETAILS.find((item) => item.reference === runtimeSelectedTokenReference) ?? DEFAULT_STEP_DETAIL;
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
    <>
      <section className="runtime-console-shell" aria-label="Project runtime console">
        <header className="runtime-console-topbar">
          <div className="runtime-console-app-title">
            <button aria-label="Back to projects" className="runtime-console-menu-button" type="button" onClick={onBack}>
              <span />
              <span />
              <span />
            </button>
            <strong>Project Workbench</strong>
          </div>
          <div className="runtime-console-project-title">
            <h2>{project.product_name}</h2>
            <div className="runtime-console-project-meta">
              <span>{projectIdentity}</span>
              <span>{project.business_unit || "Business unit not set"}</span>
              <span>{project.requestor}</span>
            </div>
          </div>
          <div className="runtime-console-top-metrics" aria-label="Runtime metrics">
            {runtimeMetrics.map((metric) => (
              <article className={`runtime-console-top-metric runtime-console-metric-${metric.tone}`} key={metric.label}>
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
              </article>
            ))}
          </div>
          <div className="runtime-console-last-update">
            <span>Last updated</span>
            <strong>2025-06-09 14:35</strong>
          </div>
        </header>

        <section className="runtime-console-readiness" aria-label="Project setup and output materials">
          <div className="runtime-console-readiness-title">
            <p className="eyebrow">Project setup / output materials</p>
            <strong>Preparation</strong>
          </div>
          {setupMaterials.map((item) => (
            <RuntimeSetupItem key={item.title} item={item} />
          ))}
          <button className="runtime-console-setup-button" type="button" disabled title="Planned future entry point.">
            View activity history
          </button>
        </section>

        <section className="runtime-console-filterbar" aria-label="Runtime filters">
          <label>
            Test item category
            <select defaultValue="all">
              <option value="all">All items</option>
              <option value="attention">Attention only</option>
            </select>
          </label>
          <label className="runtime-console-check">
            <input type="checkbox" defaultChecked />
            Show active items only
          </label>
          <label className="runtime-console-check">
            <input type="checkbox" defaultChecked />
            Show status icons
          </label>
          <label className="runtime-console-check">
            <input type="checkbox" defaultChecked />
            Show markers
          </label>
          <div className="runtime-console-radio-group">
            <span>Status filter:</span>
            {["All", "Not started", "In progress", "Pass", "Failed"].map((item) => (
              <label key={item}>
                <input defaultChecked={item === "All"} name="runtime-status-filter" type="radio" />
                {item}
              </label>
            ))}
          </div>
          <div className="runtime-console-filter-nav" aria-label="Matrix row navigation">
            <button aria-label="Previous rows" type="button">◀</button>
            <button aria-label="Next rows" type="button">▶</button>
          </div>
        </section>

        <section className="runtime-console-workspace">
          <div className="runtime-console-main">
            <div className="runtime-console-toolbar">
              <div>
                <p className="eyebrow">Matrix Projection</p>
                <h3>Matrix execution projection</h3>
              </div>
              <div className="runtime-console-toolbar-actions">
                <span className="runtime-console-muted">
                  {runtimeProjectionLoading ? "Loading projection..." : "Read-only projection"}
                </span>
                <button type="button" onClick={onOpenMatrixEditor}>Matrix</button>
              </div>
            </div>
            <ProjectWorkbenchMatrixProjectionPanel
              projectId={project.project_id}
              onTokenSelect={setSelectedProjectionToken}
            />
          </div>

          <aside className="runtime-console-step-workspace" aria-label="Step workspace">
            <header>
              <div>
                <p className="eyebrow">Step Workspace</p>
                <p className="runtime-console-step-breadcrumb">{mockStepDetail.group} › Step {mockStepDetail.token}</p>
                <h3>{activeStepTitle}</h3>
              </div>
              <div className="runtime-console-step-tools">
                <button type="button" disabled title="Planned future action in Step Workspace.">
                  Image
                </button>
              </div>
            </header>
            <section className="runtime-console-step-status-card">
              <div>
                <span>Status</span>
                <strong className={`runtime-console-step-status-${mockStepDetail.status.toLowerCase().replace(/\s+/g, "-")}`}>
                  {selectedProjectionStatus
                    ?? selectedWorkspace?.selected_token?.lifecycle_projection?.toUpperCase()
                    ?? mockStepDetail.status}
                </strong>
              </div>
              <div>
                <span>Executor</span>
                <strong>Jerry Wang</strong>
              </div>
              <div>
                <span>Completed</span>
                <strong>2025-06-09 14:20</strong>
              </div>
            </section>
            <nav className="runtime-console-step-tabs" aria-label="Step workspace tabs">
              {["Overview", "Test data", "Images/Evidence (4)", "Charts (1)", "Attachments (2)", "Report sync", "History"].map((item, index) => (
                <button
                  className={index === 0 ? "is-active" : ""}
                  key={item}
                  type="button"
                  disabled={index !== 0}
                  title={index === 0 ? undefined : "Planned future tab in Step Workspace."}
                >
                  {item}
                </button>
              ))}
            </nav>
            {selectedProjectionToken ? (
              <>
                <dl className="runtime-console-step-facts">
                  <div>
                    <dt>Token</dt>
                    <dd>{selectedProjectionToken.rawToken}</dd>
                  </div>
                  <div>
                    <dt>Group</dt>
                    <dd>{selectedProjectionToken.groupLabel}</dd>
                  </div>
                  <div>
                    <dt>Section</dt>
                    <dd>{selectedProjectionToken.section}</dd>
                  </div>
                  <div>
                    <dt>Lifecycle</dt>
                    <dd>{STEP_STATUS_BY_TONE[selectedProjectionToken.statusTone]}</dd>
                  </div>
                  <div>
                    <dt>Evidence</dt>
                    <dd>Not linked in this projection workspace</dd>
                  </div>
                  <div>
                    <dt>Report sync</dt>
                    <dd>Not linked in this projection workspace</dd>
                  </div>
                </dl>
                <div className="runtime-console-step-detail">
                  <span>Method</span>
                  <p>{selectedProjectionToken.method}</p>
                  <span>Condition</span>
                  <p>{selectedProjectionToken.condition}</p>
                  <span>Requirement</span>
                  <p>{selectedProjectionToken.requirement}</p>
                </div>
              </>
            ) : selectedWorkspace?.selected_token ? (
              <>
                <dl className="runtime-console-step-facts">
                  <div>
                    <dt>Token</dt>
                    <dd>{selectedWorkspace.selected_token.raw_token}</dd>
                  </div>
                  <div>
                    <dt>Group</dt>
                    <dd>{selectedWorkspace.group_label ?? "Not specified"}</dd>
                  </div>
                  <div>
                    <dt>Section</dt>
                    <dd>{selectedWorkspace.selected_token.section}</dd>
                  </div>
                  <div>
                    <dt>Lifecycle</dt>
                    <dd>{selectedWorkspace.selected_token.lifecycle_projection ?? "unknown"}</dd>
                  </div>
                  <div>
                    <dt>Evidence</dt>
                    <dd>{selectedWorkspace.selected_token.evidence_projection ?? "unknown"}</dd>
                  </div>
                  <div>
                    <dt>Report sync</dt>
                    <dd>{selectedWorkspace.selected_token.report_sync_projection ?? "unknown"}</dd>
                  </div>
                </dl>
                <div className="runtime-console-step-detail">
                  <span>Method</span>
                  <p>{selectedWorkspace.selected_token.method}</p>
                  <span>Condition</span>
                  <p>{selectedWorkspace.selected_token.condition}</p>
                  <span>Requirement</span>
                  <p>{selectedWorkspace.selected_token.requirement}</p>
                </div>
              </>
            ) : (
              <MockStepWorkspaceContent detail={mockStepDetail} />
            )}
            <StepDataSummary />
            <StepLifecycleFlow />
            <div className="runtime-console-step-actions">
              <button disabled type="button">Edit step</button>
              <button disabled type="button">Import data</button>
              <button disabled type="button">Copy to other steps</button>
              <button disabled type="button">Generate record</button>
            </div>
            <label className="runtime-console-note-box">
              Notes
              <textarea placeholder="Enter notes..." />
            </label>
            <button className="runtime-console-save-button" disabled type="button">
              Save
            </button>
          </aside>
        </section>

        <section className="runtime-console-bottom">
          <RuntimeAttentionSurface snapshot={runtimeProjectionSnapshot} />
          <FeeEstimateSurface />
        </section>
      </section>
    </>
  );
}

function MockStepWorkspaceContent({ detail }: { detail: MockStepDetail }): ReactElement {
  return (
    <>
      <dl className="runtime-console-step-facts">
        <div>
          <dt>Test item</dt>
          <dd>LLCR</dd>
        </div>
        <div>
          <dt>Section</dt>
          <dd>6.1</dd>
        </div>
        <div>
          <dt>Group</dt>
          <dd>{detail.group}</dd>
        </div>
        <div>
          <dt>Step token</dt>
          <dd>{detail.token}</dd>
        </div>
        <div>
          <dt>Method</dt>
          <dd>EIA-364-23E</dd>
        </div>
        <div>
          <dt>Condition</dt>
          <dd>20mV max, 100mA max</dd>
        </div>
        <div>
          <dt>Requirement</dt>
          <dd>Initial: {"<="} 0.40mO; After test: {"<="} 0.40mO</dd>
        </div>
        <div>
          <dt>Sample count</dt>
          <dd>5 pcs</dd>
        </div>
        <div>
          <dt>Fee estimate</dt>
          <dd>RMB 120.00</dd>
        </div>
        <div>
          <dt>Completed</dt>
          <dd>2025-06-09 11:45</dd>
        </div>
      </dl>
    </>
  );
}

function StepDataSummary(): ReactElement {
  const rows = [
    ["P1", "1.25", "1.85", "48%", "PASS"],
    ["P2", "1.18", "2.10", "78%", "FAIL"],
    ["P3", "1.32", "1.62", "23%", "PASS"],
    ["P4", "1.21", "1.88", "55%", "FAIL"],
    ["P5", "1.15", "1.48", "29%", "PASS"]
  ];

  return (
    <section className="runtime-console-data-summary">
      <h4>Test data summary</h4>
      <table>
        <thead>
          <tr>
            <th>Pin</th>
            <th>Initial (mO)</th>
            <th>After Test (mO)</th>
            <th>Change</th>
            <th>Judgement</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row[0]}>
              {row.map((cell) => (
                <td className={cell === "FAIL" ? "runtime-console-cell-fail" : ""} key={cell}>
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function StepLifecycleFlow(): ReactElement {
  return (
    <section className="runtime-console-step-flow">
      <h4>Step lifecycle</h4>
      <div>
        {["Not started", "In progress", "Completed", "Review", "Closed"].map((item, index) => (
          <span className={index <= 2 ? "is-done" : ""} key={item}>
            {item}
          </span>
        ))}
      </div>
    </section>
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
        <div><span>Total</span><strong>Pending estimate</strong></div>
      </div>
    </section>
  );
}

function RuntimeSetupItem({ item }: { item: SetupMaterialItem }): ReactElement {
  const ready = !item.placeholder;
  return (
    <article className="runtime-console-readiness-item">
      <span className={ready ? "runtime-console-state-dot runtime-console-state-ready" : "runtime-console-state-dot"} />
      <div>
        <strong>{item.title}</strong>
        <p>{item.value}</p>
      </div>
    </article>
  );
}

function RuntimeAttentionSurface({
  snapshot
}: {
  snapshot: RuntimeProjectionSnapshotResponse | null;
}): ReactElement {
  const p0 = countProjectionValue(snapshot, "attention_counts", "p0");
  const p1 = countProjectionValue(snapshot, "attention_counts", "p1");
  const p2 = countProjectionValue(snapshot, "attention_counts", "p2");
  const stale = countProjectionValue(snapshot, "stale_counts", "stale");

  return (
    <section className="runtime-console-attention" aria-label="Runtime attention">
      <header>
        <p className="eyebrow">Project issues / reminders</p>
        <h3>Project issues / reminders</h3>
      </header>
      <div className="runtime-console-attention-grid">
        <AttentionTile label="Failed items" value={p0} tone="danger" />
        <AttentionTile label="Missing evidence" value={p1} tone="warning" />
        <AttentionTile label="Unsynced report" value={p2 + stale} tone="current" />
      </div>
    </section>
  );
}

function AttentionTile({
  label,
  value,
  tone
}: {
  label: string;
  value: number;
  tone: RuntimeMetric["tone"];
}): ReactElement {
  return (
    <article className={`runtime-console-attention-tile runtime-console-metric-${tone}`}>
      <strong>{value}</strong>
      <span>{label}</span>
    </article>
  );
}

function buildRuntimeMetrics(snapshot: RuntimeProjectionSnapshotResponse | null): RuntimeMetric[] {
  if (!snapshot) {
    return [
      { label: "GROUPS NOT STARTED", value: 3, tone: "muted" },
      { label: "GROUPS IN PROGRESS", value: 4, tone: "current" },
      { label: "GROUPS PASSED", value: 2, tone: "success" },
      { label: "GROUPS FAILED", value: 1, tone: "danger" },
      { label: "FAILED ITEMS", value: 2, tone: "warning" }
    ];
  }

  const groupBuckets = snapshot.runtime_projection_summary.groups.reduce(
    (accumulator, group) => {
      const failed = countByLifecycle(group, "failed");
      const inProgress =
        countByLifecycle(group, "in_progress")
        + countByLifecycle(group, "review")
        + countByLifecycle(group, "retest");
      const notStarted = countByLifecycle(group, "not_started");
      const passed = countByLifecycle(group, "passed");

      if (failed > 0) {
        accumulator.failedGroups += 1;
      } else if (inProgress > 0) {
        accumulator.inProgressGroups += 1;
      } else if (passed > 0 && notStarted === 0) {
        accumulator.passedGroups += 1;
      } else {
        accumulator.notStartedGroups += 1;
      }
      return accumulator;
    },
    { notStartedGroups: 0, inProgressGroups: 0, passedGroups: 0, failedGroups: 0 }
  );

  return [
    {
      label: "GROUPS NOT STARTED",
      value: groupBuckets.notStartedGroups,
      tone: "muted"
    },
    {
      label: "GROUPS IN PROGRESS",
      value: groupBuckets.inProgressGroups,
      tone: "current"
    },
    {
      label: "GROUPS PASSED",
      value: groupBuckets.passedGroups,
      tone: "success"
    },
    {
      label: "GROUPS FAILED",
      value: groupBuckets.failedGroups,
      tone: "danger"
    },
    {
      label: "FAILED ITEMS",
      value: countProjectionValue(snapshot, "attention_counts", "p0"),
      tone: "warning"
    }
  ];
}

function countByLifecycle(
  group: RuntimeProjectionSnapshotResponse["runtime_projection_summary"]["groups"][number],
  lifecycle: string
): number {
  const match = group.aggregation_summary.lifecycle_counts.find((item) => item.value === lifecycle);
  return match?.count ?? 0;
}

function countProjectionValue(
  snapshot: RuntimeProjectionSnapshotResponse | null,
  key: keyof RuntimeProjectionSnapshotResponse["runtime_projection_summary"]["groups"][number]["aggregation_summary"],
  value: string
): number {
  if (!snapshot) {
    return 0;
  }
  return snapshot.runtime_projection_summary.groups.reduce((total, group) => {
    const match = group.aggregation_summary[key].find((item) => item.value === value);
    return total + (match?.count ?? 0);
  }, 0);
}
