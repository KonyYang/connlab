import { useDeferredValue, useEffect, useMemo, useState, type ReactElement } from "react";
import {
  listProjectLtrs,
  listProjects,
  type LtrRecord,
  type Project
} from "../api/client";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { UiIcon, type UiIconName } from "../components/common/UiIcon";
import { ProjectStatusBadge } from "../components/project/ProjectStatusBadge";
import "../project-dashboard.css";

type ProjectListPageProps = {
  onNewProject: () => void;
  onOpenProject: (projectId: string) => void;
};

type RegistryRow = {
  project: Project;
  ltrNumbers: string[];
};

export function ProjectListPage({
  onNewProject,
  onOpenProject
}: ProjectListPageProps): ReactElement {
  const [rows, setRows] = useState<RegistryRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [showCancelled, setShowCancelled] = useState(false);
  const [lastLtrApplyResult, setLastLtrApplyResult] = useState<LastLtrApplyResult | null>(null);
  const deferredSearch = useDeferredValue(search);
  const pageSize = 20;

  useEffect(() => {
    void refreshProjects();
    setLastLtrApplyResult(readLastLtrApplyResult());
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [deferredSearch, showCancelled]);

  const scopedRows = useMemo(
    () => visibleRowsForScope(rows, showCancelled),
    [rows, showCancelled]
  );
  const hiddenCancelledCount = useMemo(() => {
    if (showCancelled) {
      return 0;
    }
    return cancelledRowCount(rows);
  }, [rows, showCancelled]);
  const metrics = useMemo(() => buildMetrics(scopedRows), [scopedRows]);
  const filteredRows = useMemo(
    () => filterRows(scopedRows, deferredSearch),
    [deferredSearch, scopedRows]
  );
  const pageCount = Math.max(1, Math.ceil(filteredRows.length / pageSize));
  const page = Math.min(currentPage, pageCount);
  const pagedRows = useMemo(() => {
    const start = (page - 1) * pageSize;
    return filteredRows.slice(start, start + pageSize);
  }, [filteredRows, page, pageSize]);

  async function refreshProjects(): Promise<void> {
    setLoading(true);
    try {
      const projects = await listProjects();
      const nextRows = await Promise.all(
        projects.map(async (project) => ({
          project,
          ltrNumbers: await safeLtrNumbers(project.project_id)
        }))
      );
      setRows(nextRows);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
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
        {lastLtrApplyResult ? (
          <div className="registry-result-banner" role="status" aria-live="polite">
            <div className="registry-result-banner-text">
              <strong>LTR Number applied: {lastLtrApplyResult.ltr_number}</strong>
              <span>
                Project {lastLtrApplyResult.project_id}
                {lastLtrApplyResult.workbook_sheet_name && lastLtrApplyResult.workbook_row_number
                  ? `, workbook ${lastLtrApplyResult.workbook_sheet_name} row ${lastLtrApplyResult.workbook_row_number}`
                  : ""}
                {lastLtrApplyResult.workbook_backup_path
                  ? `, backup ${lastLtrApplyResult.workbook_backup_path}`
                  : ""}
              </span>
            </div>
            <button
              className="row-action"
              type="button"
              onClick={() => {
                clearLastLtrApplyResult();
                setLastLtrApplyResult(null);
              }}
            >
              Dismiss
            </button>
          </div>
        ) : null}
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
            <label className="registry-scope-toggle">
              <input
                checked={showCancelled}
                type="checkbox"
                onChange={(event) => setShowCancelled(event.target.checked)}
              />
              Show cancelled
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
        {hiddenCancelledCount > 0 ? (
          <p className="registry-scope-note">
            {hiddenCancelledCount} cancelled project{hiddenCancelledCount === 1 ? "" : "s"} hidden
          </p>
        ) : null}

        {loading && <LoadingState label="Loading project registry..." />}
        {error && <ErrorMessage message={error} />}
        {!loading && !error && rows.length === 0 && (
          <EmptyState
            title="No projects yet"
            message="Use New Project to import a request package or create a manual project request."
          />
        )}
        {!loading && !error && rows.length > 0 && scopedRows.length === 0 && (
          <EmptyState
            title="No active projects in this view"
            message='Enable "Show cancelled" to inspect cancelled projects.'
          />
        )}
        {!loading && !error && scopedRows.length > 0 && filteredRows.length === 0 && (
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
                {pagedRows.map((row) => (
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
                Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, filteredRows.length)} of {filteredRows.length} projects
              </span>
              <div className="registry-pagination">
                <button
                  className="row-action"
                  disabled={page <= 1}
                  type="button"
                  onClick={() => setCurrentPage((current) => Math.max(1, current - 1))}
                >
                  Prev
                </button>
                <span>Page {page} / {pageCount}</span>
                <button
                  className="row-action"
                  disabled={page >= pageCount}
                  type="button"
                  onClick={() => setCurrentPage((current) => Math.min(pageCount, current + 1))}
                >
                  Next
                </button>
              </div>
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

function visibleRowsForScope(rows: RegistryRow[], showCancelled: boolean): RegistryRow[] {
  if (showCancelled) {
    return rows;
  }
  return rows.filter((row) => row.project.status !== "cancelled");
}

function cancelledRowCount(rows: RegistryRow[]): number {
  return rows.filter((row) => row.project.status === "cancelled").length;
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

type LastLtrApplyResult = {
  project_id: string;
  ltr_number: string;
  workbook_sheet_name: string | null;
  workbook_row_number: number | null;
  workbook_backup_path: string | null;
  occurred_at: string;
};

const LAST_LTR_APPLY_RESULT_KEY = "connlab:last_ltr_apply_result";

function readLastLtrApplyResult(): LastLtrApplyResult | null {
  try {
    const raw = window.sessionStorage.getItem(LAST_LTR_APPLY_RESULT_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as LastLtrApplyResult;
    if (!parsed?.project_id || !parsed?.ltr_number) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

function clearLastLtrApplyResult(): void {
  try {
    window.sessionStorage.removeItem(LAST_LTR_APPLY_RESULT_KEY);
  } catch {
    // Ignore session-storage failures.
  }
}
