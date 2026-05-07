import { useDeferredValue, useEffect, useMemo, useState, type ReactElement } from "react";
import {
  discardSavedProjectCreationDraft,
  listProjectLtrs,
  listProjectCreationDrafts,
  listProjects,
  type LtrRecord,
  type Project,
  type ProjectCreationDraft
} from "../api/client";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { UiIcon, type UiIconName } from "../components/common/UiIcon";
import { ProjectStatusBadge } from "../components/project/ProjectStatusBadge";
import "../project-dashboard.css";

type ProjectListPageProps = {
  onContinueDraft: (draft: ProjectCreationDraft) => void | Promise<void>;
  onNewProject: () => void;
  onOpenProject: (projectId: string) => void;
};

type RegistryRow = {
  project: Project;
  ltrNumbers: string[];
};

export function ProjectListPage({
  onContinueDraft,
  onNewProject,
  onOpenProject
}: ProjectListPageProps): ReactElement {
  const [rows, setRows] = useState<RegistryRow[]>([]);
  const [drafts, setDrafts] = useState<ProjectCreationDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [draftsLoading, setDraftsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [draftError, setDraftError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [discardingDraftId, setDiscardingDraftId] = useState<string | null>(null);
  const [confirmDiscardDraftId, setConfirmDiscardDraftId] = useState<string | null>(null);
  const deferredSearch = useDeferredValue(search);

  useEffect(() => {
    void refreshProjects();
  }, []);

  const metrics = useMemo(() => buildMetrics(rows), [rows]);
  const filteredDrafts = useMemo(
    () => filterDrafts(drafts, deferredSearch),
    [deferredSearch, drafts]
  );
  const filteredRows = useMemo(
    () => filterRows(rows, deferredSearch),
    [deferredSearch, rows]
  );

  async function refreshProjects(): Promise<void> {
    setLoading(true);
    setDraftsLoading(true);
    try {
      const projects = await listProjects();
      const nextDrafts = await listProjectCreationDrafts();
      const nextRows = await Promise.all(
        projects.map(async (project) => ({
          project,
          ltrNumbers: await safeLtrNumbers(project.project_id)
        }))
      );
      setRows(nextRows);
      setDrafts(nextDrafts);
      setError(null);
      setDraftError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
      setDraftsLoading(false);
    }
  }

  async function handleDiscardDraft(draft: ProjectCreationDraft): Promise<void> {
    if (confirmDiscardDraftId !== draft.package_id) {
      setConfirmDiscardDraftId(draft.package_id);
      return;
    }
    setDiscardingDraftId(draft.package_id);
    setDraftError(null);
    try {
      await discardSavedProjectCreationDraft(draft.package_id);
      setDrafts((current) =>
        current.filter((item) => item.package_id !== draft.package_id)
      );
      setConfirmDiscardDraftId(null);
    } catch (err) {
      setDraftError((err as Error).message);
    } finally {
      setDiscardingDraftId(null);
    }
  }

  return (
    <section className="project-dashboard">
      <div className="project-metric-grid" aria-label="Project metrics">
        {metrics.map((metric) => (
          <article className="project-metric-card" key={metric.label}>
            <span className={`metric-icon metric-icon-${metric.tone}`}>
              <UiIcon name={metric.icon} />
            </span>
            <div>
              <strong>{metric.value}</strong>
              <span>{metric.label}</span>
              <small>{metric.caption}</small>
            </div>
          </article>
        ))}
      </div>

      <div className="project-register-panel">
        <div className="register-toolbar">
          <div>
            <h3>Project registry</h3>
            <p>Search and open existing projects. LTR Number is the business identifier after registration.</p>
          </div>
          <div className="registry-tools">
            <label className="project-search">
              <span>Search projects</span>
              <span className="project-search-input">
                <UiIcon name="search" />
                <input
                  placeholder="Search LTR Number, product, requestor..."
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </span>
            </label>
            <button className="toolbar-button" disabled title="Filter is not active in this phase" type="button">
              <UiIcon name="filter" />
              Filter
            </button>
            <button className="toolbar-button" disabled title="Column presets are not active in this phase" type="button">
              <UiIcon name="columns" />
              Columns
            </button>
            <div className="view-toggle" aria-label="Registry view">
              <button className="view-toggle-active" type="button" title="List view">
                <UiIcon name="list" />
              </button>
              <button disabled type="button" title="Grid view is not active in this phase">
                <UiIcon name="grid" />
              </button>
            </div>
            <button className="toolbar-button toolbar-icon-button" type="button" onClick={() => void refreshProjects()}>
              <UiIcon name="refresh" />
            </button>
            <button className="primary-action" type="button" onClick={onNewProject}>
              New Project
            </button>
          </div>
        </div>

        {loading && <LoadingState label="Loading project registry..." />}
        {error && <ErrorMessage message={error} />}
        {!loading && !error && rows.length === 0 && (
          <EmptyState
            title="No projects yet"
            message="Use New Project to import a request package or create a manual project request."
          />
        )}
        {!loading && !error && rows.length > 0 && filteredRows.length === 0 && (
          <EmptyState
            title="No matching projects"
            message="Adjust the search text to return to the full project registry."
          />
        )}
        {!loading && !error && filteredRows.length > 0 && (
          <div className="project-table-wrap">
            <table className="project-table">
              <thead>
                <tr>
                  <th>LTR Number</th>
                  <th>Project Name</th>
                  <th>Product</th>
                  <th>Requestor</th>
                  <th>Business Unit</th>
                  <th>Status</th>
                  <th>Progress</th>
                  <th>Recent Activity</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((row) => (
                  <tr key={row.project.project_id}>
                    <td className="project-no">{businessIdentifier(row)}</td>
                    <td>{projectDisplayName(row.project)}</td>
                    <td>{row.project.product_name}</td>
                    <td>{row.project.requestor}</td>
                    <td>{row.project.business_unit || "Not set"}</td>
                    <td><ProjectStatusBadge status={row.project.status} /></td>
                    <td>
                      <div className="progress-cell">
                        <span>
                          <i style={{ width: `${statusProgress(row.project.status)}%` }} />
                        </span>
                        <strong>{statusProgress(row.project.status)}%</strong>
                      </div>
                    </td>
                    <td>{activityText(row)}</td>
                    <td>
                      <button
                        className="row-action"
                        type="button"
                        onClick={() => onOpenProject(row.project.project_id)}
                      >
                        Open
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="registry-footer">
              <span>
                Showing {filteredRows.length} of {rows.length} projects
              </span>
              <span>20 / page</span>
            </div>
          </div>
        )}
      </div>

      <div className="project-register-panel drafts-panel">
        <div className="register-toolbar">
          <div>
            <h3>Drafts / In Progress</h3>
            <p>Continue saved New Project work or discard drafts that should not become projects.</p>
          </div>
        </div>

        {draftsLoading && <LoadingState label="Loading saved drafts..." />}
        {draftError && <ErrorMessage message={draftError} />}
        {!draftsLoading && !draftError && drafts.length === 0 && (
          <EmptyState
            title="No saved drafts"
            message="Use Save draft and exit from New Project when work should continue later."
          />
        )}
        {!draftsLoading && !draftError && drafts.length > 0 && filteredDrafts.length === 0 && (
          <EmptyState
            title="No matching drafts"
            message="Adjust the search text to return to saved New Project drafts."
          />
        )}
        {!draftsLoading && !draftError && filteredDrafts.length > 0 && (
          <div className="project-table-wrap">
            <table className="project-table draft-table">
              <thead>
                <tr>
                  <th>Source</th>
                  <th>Product</th>
                  <th>Requestor</th>
                  <th>Step</th>
                  <th>Updated</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredDrafts.map((draft) => (
                  <tr key={draft.package_id}>
                    <td>
                      <strong>{draft.subject || draft.source_name}</strong>
                      <span className="draft-source-name">{draft.source_name}</span>
                    </td>
                    <td>{draft.product_name || "Not set"}</td>
                    <td>{draft.requester || "Not set"}</td>
                    <td><span className="status-badge status-badge-ready">{draftStepLabel(draft.current_step)}</span></td>
                    <td>{draft.updated_at || "Not recorded"}</td>
                    <td>
                      <div className="draft-actions">
                        <button
                          className="row-action"
                          type="button"
                          onClick={() => void onContinueDraft(draft)}
                        >
                          Continue
                        </button>
                        <button
                          className="row-action row-action-danger"
                          disabled={discardingDraftId === draft.package_id}
                          type="button"
                          onClick={() => void handleDiscardDraft(draft)}
                        >
                          {discardingDraftId === draft.package_id
                            ? "Discarding..."
                            : confirmDiscardDraftId === draft.package_id
                              ? "Confirm discard"
                              : "Discard"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="registry-footer">
              <span>
                Showing {filteredDrafts.length} of {drafts.length} saved drafts
              </span>
              <span>Drafts are separate from confirmed Projects</span>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

async function safeLtrNumbers(projectId: string): Promise<string[]> {
  try {
    const records = await listProjectLtrs(projectId);
    return records.map((record: LtrRecord) => record.ltr_number).filter(Boolean);
  } catch {
    return [];
  }
}

function filterRows(rows: RegistryRow[], search: string): RegistryRow[] {
  const query = search.trim().toLowerCase();
  if (!query) {
    return rows;
  }
  return rows.filter((row) =>
    [
      businessIdentifier(row),
      row.project.project_no ?? "",
      row.project.product_name,
      row.project.requestor,
      row.project.business_unit ?? "",
      row.project.status
    ]
      .join(" ")
      .toLowerCase()
      .includes(query)
  );
}

function filterDrafts(
  drafts: ProjectCreationDraft[],
  search: string,
): ProjectCreationDraft[] {
  const query = search.trim().toLowerCase();
  if (!query) {
    return drafts;
  }
  return drafts.filter((draft) =>
    [
      draft.subject ?? "",
      draft.source_name,
      draft.product_name ?? "",
      draft.requester ?? "",
      draft.current_step
    ]
      .join(" ")
      .toLowerCase()
      .includes(query)
  );
}

function draftStepLabel(step: string): string {
  if (step === "precheck") {
    return "Precheck";
  }
  return "Intake";
}

function buildMetrics(rows: RegistryRow[]): Array<{
  caption: string;
  icon: UiIconName;
  label: string;
  tone: string;
  value: number;
}> {
  return [
    {
      caption: "All time",
      icon: "projects",
      label: "Total projects",
      tone: "total",
      value: rows.length
    },
    {
      caption: "Active workflow",
      icon: "clock",
      label: "In progress",
      tone: "progress",
      value: rows.filter((row) => isInProgress(row.project.status)).length
    },
    {
      caption: "Awaiting action",
      icon: "hourglass",
      label: "Pending review",
      tone: "review",
      value: rows.filter((row) => isPendingReview(row.project.status)).length
    },
    {
      caption: "Closed or folder ready",
      icon: "new-project",
      label: "Completed",
      tone: "completed",
      value: rows.filter((row) => isCompleted(row.project.status)).length
    },
    {
      caption: "No LTR Number yet",
      icon: "package",
      label: "Draft",
      tone: "draft",
      value: rows.filter((row) => row.ltrNumbers.length === 0).length
    }
  ];
}

function businessIdentifier(row: RegistryRow): string {
  return row.ltrNumbers[0] ?? "Pending LTR Number";
}

function projectDisplayName(project: Project): string {
  return project.project_no || project.product_name;
}

function isCompleted(status: string): boolean {
  return ["closed", "folder_created"].includes(status);
}

function isInProgress(status: string): boolean {
  return !["cancelled", "closed", "draft", "folder_created"].includes(status);
}

function isPendingReview(status: string): boolean {
  return ["draft", "intake_received", "precheck_pending", "precheck_failed"].includes(status);
}

function statusProgress(status: string): number {
  const values: Record<string, number> = {
    cancelled: 0,
    closed: 100,
    confirmed: 45,
    draft: 10,
    folder_created: 100,
    intake_received: 25,
    ltr_registered: 70,
    precheck_failed: 35,
    precheck_passed: 55,
    precheck_pending: 30
  };
  return values[status] ?? 20;
}

function activityText(row: RegistryRow): string {
  if (row.ltrNumbers.length > 0) {
    return `LTR Number registered: ${row.ltrNumbers[0]}`;
  }
  if (row.project.status === "intake_received") {
    return "Project confirmed from request package";
  }
  return "Awaiting LTR Number registration";
}
