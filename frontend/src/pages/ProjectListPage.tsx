import { useDeferredValue, useEffect, useMemo, useState, type ReactElement } from "react";
import {
  listProjectRegistryRows,
  type ProjectRegistryRow
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

type RegistryRow = ProjectRegistryRow;

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
      setRows(await listProjectRegistryRows());
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
                  placeholder="Search LTR Number, sample, test item, requestor..."
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
                  <th>Sample Description</th>
                  <th className="registry-test-item-column">Test Item</th>
                  <th>Status</th>
                  <th>Progress</th>
                  <th>Notes</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {pagedRows.map((row) => (
                  <tr key={row.project_id}>
                    <td className="project-no">{businessIdentifier(row)}</td>
                    <td>{displayText(row.sample_description, "Not recorded")}</td>
                    <td className="registry-test-item-column">{displayText(row.test_item, "Not recorded")}</td>
                    <td><ProjectStatusBadge status={row.status} /></td>
                    <td>
                      <div className="progress-cell">
                        <span>
                          <i style={{ width: `${row.progress}%` }} />
                        </span>
                        <strong>{row.progress}%</strong>
                      </div>
                    </td>
                    <td>{displayText(row.notes, "None")}</td>
                    <td>
                      <button
                        className="row-action"
                        type="button"
                        onClick={() => onOpenProject(row.project_id)}
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

function filterRows(rows: RegistryRow[], search: string): RegistryRow[] {
  const query = search.trim().toLowerCase();
  if (!query) {
    return rows;
  }
  return rows.filter((row) =>
    [
      businessIdentifier(row),
      row.sample_description ?? "",
      row.test_item ?? "",
      row.status,
      row.notes ?? ""
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
  return rows.filter((row) => row.status !== "cancelled");
}

function cancelledRowCount(rows: RegistryRow[]): number {
  return rows.filter((row) => row.status === "cancelled").length;
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
      value: rows.filter((row) => isInProgress(row.status)).length
    },
    {
      caption: "Awaiting action",
      icon: "hourglass",
      label: "Pending review",
      tone: "review",
      value: rows.filter((row) => isPendingReview(row.status)).length
    },
    {
      caption: "Closed or folder ready",
      icon: "new-project",
      label: "Completed",
      tone: "completed",
      value: rows.filter((row) => isCompleted(row.status)).length
    },
    {
      caption: "No LTR Number yet",
      icon: "package",
      label: "Draft",
      tone: "draft",
      value: rows.filter((row) => !row.ltr_number).length
    }
  ];
}

function businessIdentifier(row: RegistryRow): string {
  return row.ltr_number ?? "Pending LTR Number";
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

function displayText(value: string | null | undefined, fallback: string): string {
  const text = value?.trim();
  return text || fallback;
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
