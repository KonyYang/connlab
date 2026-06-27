import { useDeferredValue, useEffect, useMemo, useRef, useState, type ReactElement } from "react";
import {
  getProjectLifecycle,
  listProjectRegistryRows,
  type ProjectLifecycleResponse,
  type ProjectRegistryRow
} from "../api/client";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { UiIcon } from "../components/common/UiIcon";
import {
  filterRegistryRowsForView,
  registryLifecycleClassName,
  registryNextStepLabel,
  registryStatusLabel,
  type ProjectRegistryLifecycleRow,
  type ProjectRegistryView,
} from "../features/projects-registry/projectRegistryLifecycleViews";
import "../project-dashboard.css";

type ProjectListPageProps = {
  onOpenProject: (projectId: string) => void;
};

type RegistryRow = ProjectRegistryRow;

type RegistryView = ProjectRegistryView;
type ProjectIdSortDirection = "asc" | "desc";
type ProjectRegistryViewState = {
  search: string;
  selectedView: RegistryView;
  projectIdSort: ProjectIdSortDirection;
  currentPage: number;
};
type ProjectLifecycleOverlay = {
  lifecycle: ProjectLifecycleResponse | null;
  error: string | null;
};

const VIEW_LABELS: Record<RegistryView, string> = {
  all: "All",
  planning: "Planning",
  closed: "Closed",
  ongoing: "On-going",
};

const VIEW_ORDER: RegistryView[] = [
  "ongoing",
  "planning",
  "closed",
  "all",
];
const PROJECT_REGISTRY_STATE_STORAGE_KEY = "connlab.projectRegistry.viewState";

export function ProjectListPage({
  onOpenProject
}: ProjectListPageProps): ReactElement {
  const initialViewState = useMemo(loadProjectRegistryViewState, []);
  const didHydrateViewState = useRef(false);
  const [rows, setRows] = useState<RegistryRow[]>([]);
  const [lifecycleByProjectId, setLifecycleByProjectId] = useState<Record<string, ProjectLifecycleOverlay>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState(initialViewState.search);
  const [currentPage, setCurrentPage] = useState(initialViewState.currentPage);
  const [selectedView, setSelectedView] = useState<RegistryView>(initialViewState.selectedView);
  const [projectIdSort, setProjectIdSort] = useState<ProjectIdSortDirection>(initialViewState.projectIdSort);
  const [lastLtrApplyResult, setLastLtrApplyResult] = useState<LastLtrApplyResult | null>(null);
  const deferredSearch = useDeferredValue(search);
  const pageSize = 20;

  useEffect(() => {
    void refreshProjects();
    setLastLtrApplyResult(readLastLtrApplyResult());
  }, []);

  useEffect(() => {
    if (!didHydrateViewState.current) {
      didHydrateViewState.current = true;
      return;
    }
    setCurrentPage(1);
  }, [deferredSearch, selectedView, projectIdSort]);

  useEffect(() => {
    saveProjectRegistryViewState({
      search,
      selectedView,
      projectIdSort,
      currentPage,
    });
  }, [search, selectedView, projectIdSort, currentPage]);

  const lifecycleRows = useMemo<ProjectRegistryLifecycleRow[]>(
    () =>
      rows.map((row) => {
        const overlay = lifecycleByProjectId[row.project_id];
        return {
          row,
          lifecycle: overlay?.lifecycle ?? null,
          lifecycleError: overlay?.error ?? null,
        };
      }),
    [rows, lifecycleByProjectId]
  );
  const lifecycleOverlayErrorCount = useMemo(
    () => lifecycleRows.filter((entry) => entry.lifecycleError).length,
    [lifecycleRows]
  );
  const viewRows = useMemo(
    () => filterRegistryRowsForView(lifecycleRows, selectedView),
    [lifecycleRows, selectedView]
  );
  const filteredRows = useMemo(
    () => filterRows(viewRows, deferredSearch),
    [deferredSearch, viewRows]
  );
  const sortedRows = useMemo(
    () => sortRowsByProjectId(filteredRows, projectIdSort),
    [filteredRows, projectIdSort]
  );
  const pageCount = Math.max(1, Math.ceil(sortedRows.length / pageSize));
  const page = Math.min(currentPage, pageCount);
  const pagedRows = useMemo(() => {
    const start = (page - 1) * pageSize;
    return sortedRows.slice(start, start + pageSize);
  }, [sortedRows, page, pageSize]);

  async function refreshProjects(): Promise<void> {
    setLoading(true);
    try {
      const nextRows = await listProjectRegistryRows();
      setRows(nextRows);
      setLifecycleByProjectId({});
      setError(null);
      void refreshLifecycleOverlays(nextRows);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function refreshLifecycleOverlays(registryRows: RegistryRow[]): Promise<void> {
    const entries = await Promise.all(
      registryRows.map(async (row) => {
        try {
          const lifecycle = await getProjectLifecycle(row.project_id);
          return [row.project_id, { lifecycle, error: null }] as const;
        } catch (err) {
          return [
            row.project_id,
            {
              lifecycle: null,
              error: (err as Error).message || "Lifecycle status unavailable",
            },
          ] as const;
        }
      })
    );
    setLifecycleByProjectId(Object.fromEntries(entries));
  }

  function toggleProjectIdSort(): void {
    setProjectIdSort((current) => (current === "asc" ? "desc" : "asc"));
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
        <div className="register-toolbar">
          <div className="registry-tools">
            <label className="project-search">
              <span className="registry-control-sr-only">Search projects</span>
              <span className="project-search-input">
                <UiIcon name="search" />
                <input
                  aria-label="Search projects"
                  placeholder="Search Project ID, sample, test item, requestor..."
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </span>
            </label>
            <label className="registry-view-select">
              <span className="registry-control-sr-only">Project view</span>
              <select
                aria-label="Project view"
                value={selectedView}
                onChange={(event) => setSelectedView(normalizeRegistryView(event.target.value) ?? "ongoing")}
              >
                {VIEW_ORDER.map((view) => (
                  <option key={view} value={view}>
                    {VIEW_LABELS[view]}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
        {loading && <LoadingState label="Loading project registry..." />}
        {error && <ErrorMessage message={error} />}
        {!loading && !error && lifecycleOverlayErrorCount > 0 ? (
          <div className="registry-result-banner registry-lifecycle-warning" role="status" aria-live="polite">
            <div className="registry-result-banner-text">
              <strong>
                Lifecycle status unavailable for {lifecycleOverlayErrorCount}{" "}
                {lifecycleOverlayErrorCount === 1 ? "project" : "projects"}
              </strong>
              <span>
                Showing base registry information with compatibility labels. Refresh the registry before making lifecycle decisions.
              </span>
            </div>
          </div>
        ) : null}
        {!loading && !error && rows.length === 0 && (
          <EmptyState
            title="No projects yet"
            message="Use the left navigation New Project entry to import a request package or create a manual project request."
          />
        )}
        {!loading && !error && rows.length > 0 && viewRows.length === 0 && (
          <EmptyState
            title="No projects in this view"
            message="Choose another view or clear the search text."
          />
        )}
        {!loading && !error && viewRows.length > 0 && filteredRows.length === 0 && (
          <EmptyState
            title="No matching projects"
            message="Adjust the search text to return to the current view."
          />
        )}
        {!loading && !error && filteredRows.length > 0 && (
          <div className="project-table-wrap">
            <table className="project-table">
              <thead>
                <tr>
                  <th>
                    <button
                      className="project-id-sort-button"
                      type="button"
                      aria-label={
                        projectIdSort === "asc"
                          ? "Sort Project ID descending"
                          : "Sort Project ID ascending"
                      }
                      title={
                        projectIdSort === "asc"
                          ? "Sort Project ID descending"
                          : "Sort Project ID ascending"
                      }
                      onClick={toggleProjectIdSort}
                    >
                      <span>Project ID</span>
                      <UiIcon name={projectIdSort === "asc" ? "sort-ascending" : "sort-descending"} />
                    </button>
                  </th>
                  <th>Sample Description</th>
                  <th className="registry-test-item-column">Test Item</th>
                  <th>Status</th>
                  <th>Next Step</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {pagedRows.map(({ row, lifecycle }) => (
                  <tr key={row.project_id}>
                    <td className="project-no">
                      {businessIdentifier(row)}
                      {row.display_project_id_kind === "temporary" ? (
                        <span className="registry-temp-badge">Temporary Planning</span>
                      ) : null}
                    </td>
                    <td>{displayText(row.sample_description, "Not recorded")}</td>
                    <td className="registry-test-item-column">{displayText(row.test_item, "Not recorded")}</td>
                    <td className="registry-status-text">
                      <span className={`registry-lifecycle-badge ${registryLifecycleClassName(row, lifecycle)}`}>
                        {registryStatusLabel(row, lifecycle)}
                      </span>
                    </td>
                    <td className="registry-next-step">{registryNextStepLabel(row, lifecycle)}</td>
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
                Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, filteredRows.length)} of {filteredRows.length}{" "}
                {footerProjectLabel(selectedView)}
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

function loadProjectRegistryViewState(): ProjectRegistryViewState {
  const fallback: ProjectRegistryViewState = {
    search: "",
    selectedView: "ongoing",
    projectIdSort: "asc",
    currentPage: 1,
  };
  try {
    const raw = window.sessionStorage.getItem(PROJECT_REGISTRY_STATE_STORAGE_KEY);
    if (!raw) {
      return fallback;
    }
    const stored = JSON.parse(raw) as Partial<ProjectRegistryViewState>;
    return {
      search: typeof stored.search === "string" ? stored.search : fallback.search,
      selectedView: normalizeRegistryView(stored.selectedView) ?? fallback.selectedView,
      projectIdSort: isProjectIdSortDirection(stored.projectIdSort)
        ? stored.projectIdSort
        : fallback.projectIdSort,
      currentPage: isPositiveInteger(stored.currentPage) ? stored.currentPage : fallback.currentPage,
    };
  } catch {
    return fallback;
  }
}

function saveProjectRegistryViewState(state: ProjectRegistryViewState): void {
  try {
    window.sessionStorage.setItem(PROJECT_REGISTRY_STATE_STORAGE_KEY, JSON.stringify(state));
  } catch {
    // View-state persistence is a convenience only; the table still works if storage is unavailable.
  }
}

function isRegistryView(value: unknown): value is RegistryView {
  return typeof value === "string" && (VIEW_ORDER as string[]).includes(value);
}

function normalizeRegistryView(value: unknown): RegistryView | null {
  if (isRegistryView(value)) {
    return value;
  }
  if (value === "completed") {
    return "closed";
  }
  if (value === "stopped") {
    return "ongoing";
  }
  if (value === "matrix_needed" || value === "ready_to_test" || value === "folder_blocked") {
    return "ongoing";
  }
  return null;
}

function isProjectIdSortDirection(value: unknown): value is ProjectIdSortDirection {
  return value === "asc" || value === "desc";
}

function isPositiveInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value > 0;
}

function filterRows(rows: ProjectRegistryLifecycleRow[], search: string): ProjectRegistryLifecycleRow[] {
  const query = search.trim().toLowerCase();
  if (!query) {
    return rows;
  }
  return rows.filter(({ row, lifecycle }) =>
    [
      businessIdentifier(row),
      row.sample_description ?? "",
      row.test_item ?? "",
      registryStatusLabel(row, lifecycle),
      registryNextStepLabel(row, lifecycle),
      row.notes ?? ""
    ]
      .join(" ")
      .toLowerCase()
      .includes(query)
  );
}

function sortRowsByProjectId(
  rows: ProjectRegistryLifecycleRow[],
  direction: ProjectIdSortDirection
): ProjectRegistryLifecycleRow[] {
  const directionFactor = direction === "asc" ? 1 : -1;
  return rows
    .map((entry, index) => ({ entry, index, key: projectIdSortKey(entry.row) }))
    .sort((left, right) => {
      const comparison = compareProjectIdSortKeys(left.key, right.key);
      if (comparison !== 0) {
        return comparison * directionFactor;
      }
      return left.index - right.index;
    })
    .map((item) => item.entry);
}

type ProjectIdSortKey = {
  kindRank: number;
  year: number;
  month: number;
  sequence: number;
  suffix: string;
  original: string;
};

function projectIdSortKey(row: RegistryRow): ProjectIdSortKey {
  const original = businessIdentifier(row).trim();
  const normalized = original.toUpperCase();
  const registeredMatch = normalized.match(/^(?:DL|LTR)[-\s]*(\d{4})[-\s]*(\d{1,2})[-\s]*(\d+)/);
  if (registeredMatch) {
    return {
      kindRank: 0,
      year: Number(registeredMatch[1]),
      month: Number(registeredMatch[2]),
      sequence: Number(registeredMatch[3]),
      suffix: "",
      original: normalized,
    };
  }
  const temporaryMatch = normalized.match(/^TMP[-\s]*([A-Z0-9]{8,})/);
  if (temporaryMatch) {
    return {
      kindRank: 1,
      year: 0,
      month: 0,
      sequence: 0,
      suffix: temporaryMatch[1],
      original: normalized,
    };
  }
  return {
    kindRank: 2,
    year: 0,
    month: 0,
    sequence: 0,
    suffix: normalized,
    original: normalized,
  };
}

function compareProjectIdSortKeys(left: ProjectIdSortKey, right: ProjectIdSortKey): number {
  const numericFields: Array<keyof Pick<ProjectIdSortKey, "kindRank" | "year" | "month" | "sequence">> = [
    "kindRank",
    "year",
    "month",
    "sequence",
  ];
  for (const field of numericFields) {
    const difference = left[field] - right[field];
    if (difference !== 0) {
      return difference;
    }
  }
  const suffixComparison = left.suffix.localeCompare(right.suffix);
  if (suffixComparison !== 0) {
    return suffixComparison;
  }
  return left.original.localeCompare(right.original);
}

function businessIdentifier(row: RegistryRow): string {
  return row.display_project_id;
}

function footerProjectLabel(view: RegistryView): string {
  if (view === "all") {
    return "projects";
  }
  return `${VIEW_LABELS[view]} projects`;
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
