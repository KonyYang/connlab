import { useDeferredValue, useEffect, useMemo, useState, type ReactElement } from "react";
import {
  listProjectRegistryRows,
  type ProjectRegistryRow
} from "../api/client";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { UiIcon } from "../components/common/UiIcon";
import "../project-dashboard.css";

type ProjectListPageProps = {
  onOpenProject: (projectId: string) => void;
};

type RegistryRow = ProjectRegistryRow;

type QueueName =
  | "all"
  | "planning"
  | "matrix_needed"
  | "ready_to_test"
  | "folder_blocked"
  | "completed";
type ClassifiedQueueName = Exclude<QueueName, "all">;

const QUEUE_LABELS: Record<QueueName, string> = {
  all: "All",
  planning: "Planning",
  matrix_needed: "Matrix Needed",
  ready_to_test: "Ready to Test",
  folder_blocked: "Folder Blocked",
  completed: "Completed",
};

const QUEUE_DESCRIPTIONS: Record<QueueName, string> = {
  all: "All projects in the current cancelled visibility scope.",
  planning: "Temporary projects without a formal registered LTR or DL number.",
  matrix_needed: "Registered projects that need an active Matrix authority map.",
  ready_to_test: "Projects with active Matrix authority available for Matrix-based testing.",
  folder_blocked: "Registered projects blocked by formal Project Folder preparation.",
  completed: "Projects already completed or closed.",
};

const QUEUE_ORDER: QueueName[] = [
  "all",
  "planning",
  "matrix_needed",
  "ready_to_test",
  "folder_blocked",
  "completed",
];

export function ProjectListPage({
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

  const [activeQueue, setActiveQueue] = useState<QueueName>("all");

  useEffect(() => {
    void refreshProjects();
    setLastLtrApplyResult(readLastLtrApplyResult());
  }, []);

  useEffect(() => {
    setCurrentPage(1);
  }, [deferredSearch, showCancelled, activeQueue]);

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
  const queueCounts = useMemo(() => {
    const counts: Record<QueueName, number> = {
      all: scopedRows.length,
      planning: 0,
      matrix_needed: 0,
      ready_to_test: 0,
      folder_blocked: 0,
      completed: 0,
    };
    for (const row of scopedRows) {
      if (row.status === "cancelled") {
        continue;
      }
      const queue = classifyQueue(row);
      if (queue) {
        counts[queue] += 1;
      }
    }
    return counts;
  }, [scopedRows]);
  const queueFilteredRows = useMemo(() => {
    if (activeQueue === "all") {
      return scopedRows;
    }
    return scopedRows.filter(
      (row) => row.status !== "cancelled" && classifyQueue(row) === activeQueue
    );
  }, [activeQueue, scopedRows]);
  const filteredRows = useMemo(
    () => filterRows(queueFilteredRows, deferredSearch),
    [deferredSearch, queueFilteredRows]
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
        <div className="queue-filter-bar" role="tablist" aria-label="Project queue filter">
          {QUEUE_ORDER.map((queue) => (
            <button
              key={queue}
              className={`queue-filter-button${activeQueue === queue ? " queue-filter-button-active" : ""}`}
              role="tab"
              aria-selected={activeQueue === queue}
              aria-label={`${QUEUE_LABELS[queue]}: ${QUEUE_DESCRIPTIONS[queue]}`}
              title={QUEUE_DESCRIPTIONS[queue]}
              type="button"
              onClick={() => setActiveQueue(queue)}
            >
              <span className="queue-filter-label">{QUEUE_LABELS[queue]}</span>
              <span className="queue-filter-count">{queueCounts[queue]}</span>
            </button>
          ))}
        </div>
        <div className="register-toolbar">
          <div>
            <h3>Project registry</h3>
            <p>Search and open existing projects. Project ID shows either registered LTR/DL identity or a temporary planning ID.</p>
          </div>
          <div className="registry-tools">
            <label className="project-search">
              <span>Search projects</span>
              <span className="project-search-input">
                <UiIcon name="search" />
                <input
                  placeholder="Search Project ID, sample, test item, requestor..."
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
            message="Use the left navigation New Project entry to import a request package or create a manual project request."
          />
        )}
        {!loading && !error && rows.length > 0 && scopedRows.length === 0 && (
          <EmptyState
            title="No active projects in this view"
            message='Enable "Show cancelled" to inspect cancelled projects.'
          />
        )}
        {!loading && !error && scopedRows.length > 0 && queueFilteredRows.length === 0 && activeQueue !== "all" && (
          <EmptyState
            title="No projects in this queue"
            message="Select All or another queue to see more projects."
          />
        )}
        {!loading && !error && queueFilteredRows.length > 0 && filteredRows.length === 0 && (
          <EmptyState
            title="No matching projects"
            message="Adjust the search text to return to the current queue view."
          />
        )}
        {!loading && !error && filteredRows.length > 0 && (
          <div className="project-table-wrap">
            <table className="project-table">
              <thead>
                <tr>
                  <th>Project ID</th>
                  <th>Sample Description</th>
                  <th className="registry-test-item-column">Test Item</th>
                  <th>Status</th>
                  <th>Next Step</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {pagedRows.map((row) => (
                  <tr key={row.project_id}>
                    <td className="project-no">
                      {businessIdentifier(row)}
                      {row.display_project_id_kind === "temporary" ? (
                        <span className="registry-temp-badge">Temporary Planning</span>
                      ) : null}
                    </td>
                    <td>{displayText(row.sample_description, "Not recorded")}</td>
                    <td className="registry-test-item-column">{displayText(row.test_item, "Not recorded")}</td>
                    <td>
                      <span className="registry-status-badge">{registryStatusLabel(row)}</span>
                    </td>
                    <td className="registry-next-step">{nextStepLabel(row)}</td>
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

function classifyQueue(row: RegistryRow): ClassifiedQueueName | null {
  if (["closed", "folder_created"].includes(row.status)) {
    return "completed";
  }
  if (row.status === "ltr_registered") {
    return "matrix_needed";
  }
  if (!hasRegisteredLtr(row)) {
    return "planning";
  }
  // TASK_317B follow-up: current registry rows do not expose active Matrix or
  // formal folder readiness fields. Use the safest registered-project queue
  // rather than inferring Ready to Test or Folder Blocked from generic status.
  return "matrix_needed";
}

function hasRegisteredLtr(row: RegistryRow): boolean {
  return row.has_registered_ltr || hasDisplayText(row.ltr_number);
}

function businessIdentifier(row: RegistryRow): string {
  return row.display_project_id;
}

function registryStatusLabel(row: RegistryRow): string {
  if (row.status === "cancelled") {
    return "Cancelled";
  }
  const queue = classifyQueue(row);
  return queue ? QUEUE_LABELS[queue] : "Planning";
}

function nextStepLabel(row: RegistryRow): string {
  if (row.status === "cancelled") {
    return "No action";
  }
  const queue = classifyQueue(row);
  switch (queue) {
    case "planning":
      return "Continue planning";
    case "matrix_needed":
      return "Open Matrix authority";
    case "ready_to_test":
      return "Open Execution map";
    case "folder_blocked":
      return "Review request material";
    case "completed":
      return "No action";
    default:
      return "Continue planning";
  }
}

function displayText(value: string | null | undefined, fallback: string): string {
  const text = value?.trim();
  return text || fallback;
}

function hasDisplayText(value: string | null | undefined): boolean {
  return Boolean(value?.trim());
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
