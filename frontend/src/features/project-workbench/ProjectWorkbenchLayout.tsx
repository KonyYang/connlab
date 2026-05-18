import type { ReactElement } from "react";
import { ProjectStatusBadge } from "../../components/project/ProjectStatusBadge";
import type { Project, RuntimeProjectionSnapshotResponse } from "../../api/client";
import { ProjectWorkbenchMatrixOverview } from "./ProjectWorkbenchMatrixOverview";
import type { WorkbenchBaselineItem } from "./useProjectWorkbenchModel";
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

export function ProjectWorkbenchLayout({
  runtimeModel,
  project,
  onBack,
  onOpenMatrixEditor
}: ProjectWorkbenchLayoutProps): ReactElement {
  const {
    baselineItems,
    latestLtr,
    matrixAuthorityDraft,
    matrixDraft,
    matrixDraftError,
    matrixDraftLoading,
    runtimeProjectionError,
    runtimeProjectionLoading,
    runtimeProjectionSnapshot,
    runtimeAuthoritySync,
    runtimeSelectedTokenReference,
    setRuntimeSelectedTokenReference
  } = runtimeModel;

  const projectionDraft = matrixAuthorityDraft ?? matrixDraft;
  const runtimeMetrics = buildRuntimeMetrics(runtimeProjectionSnapshot);
  const selectedWorkspace = runtimeProjectionSnapshot?.step_workspace ?? null;
  const mockStepDetail =
    MOCK_STEP_DETAILS.find((item) => item.reference === runtimeSelectedTokenReference) ?? DEFAULT_STEP_DETAIL;
  const activeStepTitle = selectedWorkspace?.selected_token?.test_item_label
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
            <h2>
              {project.product_name}
              <ProjectStatusBadge status={project.status} />
            </h2>
            <div className="runtime-console-project-meta">
              <span>LTR: {latestLtr ?? "Not registered"}</span>
              <span>BU: {project.business_unit || "Not set"}</span>
              <span>Requestor: {project.requestor}</span>
            </div>
          </div>
          <div className="runtime-console-authority">
            <span>Project progress</span>
            <strong>
              {runtimeProjectionSnapshot ? "62%" : "62%"}
            </strong>
            <div className="runtime-console-progress-track" aria-hidden="true">
              <span style={{ width: "62%" }} />
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
            <div className="runtime-console-top-actions">
              <button aria-label="Refresh" type="button">Refresh</button>
              <button type="button" onClick={onOpenMatrixEditor}>Edit Matrix Definition</button>
            </div>
          </div>
        </header>

        <section className="runtime-console-authority-sync" aria-label="Matrix authority sync">
          <span>
            Authority v{runtimeAuthoritySync.authorityVersion ?? "-"}
            {runtimeAuthoritySync.hasUnconfirmedCandidate
              ? ` | Candidate v${runtimeAuthoritySync.candidateVersion ?? "-"} pending`
              : " | No unconfirmed candidate"}
          </span>
          <span>Projection: {runtimeAuthoritySync.projectionMatrixReference ?? "not loaded"}</span>
          <span
            className={
              runtimeAuthoritySync.projectionMatchesAuthority === false
                ? "runtime-console-sync-warning"
                : "runtime-console-sync-ok"
            }
          >
            {runtimeAuthoritySync.projectionMatchesAuthority === false
              ? "Projection not aligned with current authority"
              : "Projection aligned with authority"}
          </span>
          {runtimeAuthoritySync.selectedTokenCleared ? (
            <span className="runtime-console-sync-warning">
              Selected token was cleared after projection refresh.
            </span>
          ) : null}
        </section>

        <section className="runtime-console-readiness" aria-label="Runtime readiness">
          <div className="runtime-console-readiness-title">
            <p className="eyebrow">Project readiness status</p>
            <strong>Actionable</strong>
          </div>
          {baselineItems.map((item) => (
            <RuntimeReadinessItem key={item.title} item={item} />
          ))}
          <RuntimeReadinessItem item={{ title: "Matrix Authority", value: matrixAuthorityDraft ? "Ready" : "Pending confirmation" }} />
          <button className="runtime-console-setup-button" type="button">Open Setup Manager</button>
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
            {["All", "Not started", "In progress", "Pass", "Failed", "Missing data"].map((item) => (
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
                <p className="eyebrow">Matrix Overview</p>
                <h3>Runtime execution map</h3>
              </div>
              <span className="runtime-console-muted">
                {runtimeProjectionLoading ? "Loading projection..." : "Read-only projection"}
              </span>
            </div>
            {matrixDraftLoading ? <p className="fine-print">Loading Matrix authority...</p> : null}
            {matrixDraftError ? <p className="error">Unable to load Matrix authority: {matrixDraftError}</p> : null}
            {runtimeProjectionError ? <p className="error">Runtime projection unavailable: {runtimeProjectionError}</p> : null}
            {projectionDraft && runtimeProjectionSnapshot ? (
              <ProjectWorkbenchMatrixOverview
                draft={projectionDraft}
                selectedTokenReference={runtimeSelectedTokenReference}
                snapshot={runtimeProjectionSnapshot}
                onTokenSelect={setRuntimeSelectedTokenReference}
              />
            ) : (
              <ProjectWorkbenchMatrixOverview
                draft={projectionDraft ?? buildPlaceholderDraft(project.project_id)}
                selectedTokenReference={runtimeSelectedTokenReference ?? DEFAULT_STEP_DETAIL.reference}
                onTokenSelect={setRuntimeSelectedTokenReference}
              />
            )}
          </div>

          <aside className="runtime-console-step-workspace" aria-label="Step workspace">
            <header>
              <div>
                <p className="eyebrow">Step Workspace</p>
                <p className="runtime-console-step-breadcrumb">{mockStepDetail.group} › Step {mockStepDetail.token}</p>
                <h3>{activeStepTitle}</h3>
              </div>
              <div className="runtime-console-step-tools">
                <button type="button" onClick={onOpenMatrixEditor}>Matrix</button>
                <button type="button">Image</button>
                <button type="button">Record</button>
              </div>
            </header>
            <section className="runtime-console-step-status-card">
              <div>
                <span>Status</span>
                <strong className={`runtime-console-step-status-${mockStepDetail.status.toLowerCase().replace(/\s+/g, "-")}`}>
                  {selectedWorkspace?.selected_token?.lifecycle_projection?.toUpperCase() ?? mockStepDetail.status}
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
                <button className={index === 0 ? "is-active" : ""} key={item} type="button">
                  {item}
                </button>
              ))}
            </nav>
            {selectedWorkspace?.selected_token ? (
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
          <RecentActivitySurface />
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

function RecentActivitySurface(): ReactElement {
  return (
    <section className="runtime-console-activity" aria-label="Recent activity">
      <header>
        <p className="eyebrow">Recent activity</p>
        <h3>Recent activity</h3>
      </header>
      <ul>
        <li><span>Step 2 (Group 3 - LLCR) data updated</span><time>14:20</time></li>
        <li><span>Step 4(b) (Group 1 - High temp life) passed</span><time>13:55</time></li>
        <li><span>Uploaded 3 images for Step 8 (Group 2)</span><time>13:40</time></li>
      </ul>
      <button disabled type="button">View all activity</button>
    </section>
  );
}

function FeeEstimateSurface(): ReactElement {
  return (
    <section className="runtime-console-fee" aria-label="Fee estimate">
      <header>
        <p className="eyebrow">Fee estimate</p>
        <h3>Fee estimate</h3>
      </header>
      <div className="runtime-console-fee-grid">
        <div><span>Estimated</span><strong>RMB 12,450.00</strong></div>
        <div><span>Spent</span><strong>RMB 8,760.00</strong></div>
        <div><span>Remaining</span><strong>RMB 3,690.00</strong></div>
      </div>
      <button disabled type="button">View fee details</button>
    </section>
  );
}

function RuntimeReadinessItem({ item }: { item: WorkbenchBaselineItem }): ReactElement {
  const ready = /yes|created|available|evidence placement/i.test(item.value);
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
        <AttentionTile label="In progress" value={countProjectionValue(snapshot, "attention_counts", "none")} tone="muted" />
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
      { label: "PASS", value: 18, tone: "success" },
      { label: "FAILED", value: 2, tone: "danger" },
      { label: "IN PROGRESS", value: 5, tone: "current" },
      { label: "NOT STARTED", value: 12, tone: "muted" },
      { label: "MISSING EVIDENCE", value: 3, tone: "warning" }
    ];
  }

  return [
    {
      label: "PASS",
      value: countProjectionValue(snapshot, "lifecycle_counts", "passed"),
      tone: "success"
    },
    {
      label: "FAILED",
      value: countProjectionValue(snapshot, "lifecycle_counts", "failed"),
      tone: "danger"
    },
    {
      label: "IN PROGRESS",
      value: countProjectionValue(snapshot, "lifecycle_counts", "in_progress"),
      tone: "current"
    },
    {
      label: "NOT STARTED",
      value: countProjectionValue(snapshot, "lifecycle_counts", "not_started"),
      tone: "muted"
    },
    {
      label: "MISSING EVIDENCE",
      value: countProjectionValue(snapshot, "evidence_counts", "missing"),
      tone: "warning"
    }
  ];
}

function buildPlaceholderDraft(projectId: string) {
  return {
    draft_id: "placeholder-runtime-console",
    project_id: projectId,
    source_document_path: "placeholder://runtime-console",
    source_document_name: "Runtime Console placeholder Matrix",
    source_format: "placeholder",
    status: "draft" as const,
    version: 1,
    payload: {
      groups: [],
      warnings: [],
      blockers: []
    },
    created_at: "2026-05-16T00:00:00",
    updated_at: "2026-05-16T00:00:00"
  };
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
