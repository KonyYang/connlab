import { useDeferredValue, useEffect, useMemo, useRef, useState, type ReactElement } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../components/layout/TopBarActionsContext";
import {
  getProjectLifecycle,
  listProjectRegistryRows,
  type ProjectLifecycleResponse,
  type ProjectRegistryRow,
} from "../api/client";
import { listManagedProjects } from "../api/projectRegistryManagement";
import { listLibraryMembers, type LibraryMember } from "../api/projectLibrary";
import { listLegacyProjects, type LegacyProjectRecord } from "../api/legacyProjects";
import { buildProjectCatalog, selectProjectCatalog, catalogIdentifier, type CatalogView, type ProjectCatalogRow } from "../features/projects-registry/projectCatalog";
import { ProjectFolderRow } from "../features/projects-registry/ProjectFolderRow";
import { ProjectRegistryManagementPanel } from "../features/projects-registry/ProjectRegistryManagementPanel";
import { ProjectRegistryManagementDialog } from "../features/projects-registry/ProjectRegistryManagementDialog";
import { useProjectRegistryManagement } from "../features/projects-registry/useProjectRegistryManagement";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { UiIcon } from "../components/common/UiIcon";
import {
  registryLifecycleClassName,
  registryRowActionAriaLabel,
  registryRowActionLabel,
  registryStatusLabel,
  type ProjectRegistryLifecycleRow,
} from "../features/projects-registry/projectRegistryLifecycleViews";
import "../project-dashboard.css";

type ProjectListPageProps = {
  onOpenProject: (projectId: string) => void;
  onImport?: () => void;
  onOpenMember?: (id: string) => void;
  onOpenLinked?: (id: string) => void;
  batchId?: string;
  onViewAll?: () => void;
};

type RegistryRow = ProjectRegistryRow;

type RegistryView = CatalogView;
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
  all: "All Projects",
  files: "Files Only",
  planning: "Planning",
  closed: "Closed",
  ongoing: "On-going",
};

const VIEW_ORDER: RegistryView[] = [
  "all",
  "ongoing",
  "planning",
  "closed",
  "files",
];
const PROJECT_REGISTRY_STATE_STORAGE_KEY = "connlab.projects.viewState";

export function ProjectListPage(props: ProjectListPageProps): ReactElement {
  return <BusinessProjectListPage key={props.batchId || "all"} {...props} />;
}

function BusinessProjectListPage({
  onOpenProject, onOpenMember, onOpenLinked, onImport, batchId = "", onViewAll
}: ProjectListPageProps): ReactElement {
  const storageKey = batchId ? `${PROJECT_REGISTRY_STATE_STORAGE_KEY}:batch:${batchId}` : PROJECT_REGISTRY_STATE_STORAGE_KEY;
  const initialViewState = useMemo(() => loadProjectRegistryViewState(storageKey), [storageKey]);
  const didHydrateViewState = useRef(false);
  const [rows, setRows] = useState<RegistryRow[]>([]);
  const [members, setMembers] = useState<LibraryMember[]>([]);
  const [linked, setLinked] = useState<LegacyProjectRecord[]>([]);
  const [retainedProjectIds, setRetainedProjectIds] = useState<string[]>([]);
  const [registryComplete, setRegistryComplete] = useState(false);
  const [lifecycleByProjectId, setLifecycleByProjectId] = useState<Record<string, ProjectLifecycleOverlay>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState(initialViewState.search);
  const [currentPage, setCurrentPage] = useState(initialViewState.currentPage);
  const [selectedView, setSelectedView] = useState<RegistryView>(initialViewState.selectedView);
  const [projectIdSort, setProjectIdSort] = useState<ProjectIdSortDirection>(initialViewState.projectIdSort);
  const [dateSort, setDateSort] = useState<"asc" | "desc" | null>(null);
  const [lastLtrApplyResult, setLastLtrApplyResult] = useState<LastLtrApplyResult | null>(null);
  const [area, setArea] = useState<"active" | "recycle">("active");
  const [managedRevision, setManagedRevision] = useState(0);
  const topBarActionsRoot = useTopBarActionsRoot();
  const refreshEpoch = useRef(0);
  const catalogRequest = useRef<AbortController | null>(null);
  const management = useProjectRegistryManagement(area, () => {
    setManagedRevision((value) => value + 1);
    void refreshProjects();
  });
  const deferredSearch = useDeferredValue(search);
  const pageSize = 20;

  useEffect(() => {
    void refreshProjects();
    setLastLtrApplyResult(readLastLtrApplyResult());
    return () => {refreshEpoch.current += 1; catalogRequest.current?.abort();};
  }, []);

  useEffect(() => {
    if (!didHydrateViewState.current) {
      didHydrateViewState.current = true;
      return;
    }
    setCurrentPage(1);
  }, [deferredSearch, selectedView, projectIdSort]);

  useEffect(() => {
    saveProjectRegistryViewState(storageKey, {
      search,
      selectedView,
      projectIdSort,
      currentPage,
    });
  }, [search, selectedView, projectIdSort, currentPage, storageKey]);

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
  const catalogRows = useMemo(() => buildProjectCatalog(lifecycleRows, members, linked, { batchId, retainedProjectIds, registryComplete }), [lifecycleRows, members, linked, batchId, retainedProjectIds, registryComplete]);
  const viewRows = useMemo(() => selectProjectCatalog(catalogRows, selectedView, ""), [catalogRows, selectedView]);
  const filteredRows = useMemo(
    () => selectProjectCatalog(viewRows, "all", deferredSearch),
    [deferredSearch, viewRows]
  );
  const sortedRows = useMemo(
    () => {
      const rows = sortRowsByProjectId(filteredRows, projectIdSort);
      return dateSort ? rows.sort((a, b) => {
        const left = a.kind === "registered" ? a.entry.row.estimated_completion_date : null, right = b.kind === "registered" ? b.entry.row.estimated_completion_date : null;
        if (!left || !right) return left ? -1 : right ? 1 : 0;
        return left.localeCompare(right) * (dateSort === "asc" ? 1 : -1);
      }) : rows;
    },
    [filteredRows, projectIdSort, dateSort]
  );
  const pageCount = Math.max(1, Math.ceil(sortedRows.length / pageSize));
  const page = Math.min(currentPage, pageCount);
  const pagedRows = useMemo(() => {
    const start = (page - 1) * pageSize;
    return sortedRows.slice(start, start + pageSize);
  }, [sortedRows, page, pageSize]);

  async function refreshProjects(): Promise<void> {
    const request = ++refreshEpoch.current;
    catalogRequest.current?.abort();
    const controller = new AbortController(); catalogRequest.current = controller;
    setLoading(true);
    const results = await Promise.allSettled([listProjectRegistryRows(), listLibraryMembers("", batchId, controller.signal), batchId ? Promise.resolve([] as LegacyProjectRecord[]) : listLegacyProjects("", controller.signal), listManagedProjects("trash"), listManagedProjects("history")]);
    if (request !== refreshEpoch.current) return;
    const [registry, managed, folders, trash, history] = results;
    const nextRows = registry.status === "fulfilled" ? registry.value : [];
    setRows(nextRows); setMembers(managed.status === "fulfilled" ? managed.value.items : []); setLinked(folders.status === "fulfilled" ? folders.value : []);
    setRetainedProjectIds([...(trash.status === "fulfilled" ? trash.value : []), ...(history.status === "fulfilled" ? history.value : [])].map(entry => entry.project_id));
    setRegistryComplete(registry.status === "fulfilled" && trash.status === "fulfilled" && history.status === "fulfilled");
    setLifecycleByProjectId({});
    setError(results.some(result => result.status === "rejected") ? "Some projects could not be loaded. Retry to load the complete list." : null);
    setLoading(false);
    void refreshLifecycleOverlays(nextRows, request);
  }

  async function refreshLifecycleOverlays(registryRows: RegistryRow[], request: number): Promise<void> {
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
    if (request === refreshEpoch.current) setLifecycleByProjectId(Object.fromEntries(entries));
  }

  function toggleProjectIdSort(): void {
    setDateSort(null);
    setProjectIdSort((current) => (current === "asc" ? "desc" : "asc"));
  }

  const registryControls = (
    <div className="register-toolbar">
      <div className="registry-tools">
        <label className="project-search">
          <span className="registry-control-sr-only">Search projects</span>
          <span className="project-search-input">
            <UiIcon name="search" />
            <input
              aria-label="Search projects"
              placeholder="Search projects…"
              title="Search LTR, title, sample, test item, requestor or folder path."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </span>
        </label>
        {area === "active" && <label className="registry-view-select">
          <span className="registry-control-sr-only">Project view</span>
          <select
            aria-label="Project view"
            value={selectedView}
            onChange={(event) => setSelectedView(normalizeRegistryView(event.target.value) ?? "all")}
          >
            {VIEW_ORDER.map((view) => (
              <option key={view} value={view}>
                {VIEW_LABELS[view]}
              </option>
            ))}
          </select>
        </label>}
      </div>
      <nav className="project-registry-areas" aria-label="Project management areas">
        {area === "active" && onImport && <button className="primary-action" type="button" disabled={management.busy} title="Add existing project folders. Review before receiving; original files stay in place." onClick={onImport}>Import Projects</button>}
        {area !== "active" && <button className="registry-area-button ui-secondary-action" type="button" disabled={management.busy} onClick={() => setArea("active")}>Back to Projects</button>}
        <button className="registry-area-button ui-secondary-action" type="button" aria-pressed={area === "recycle"} disabled={management.busy} onClick={() => setArea("recycle")}>Recycle</button>
      </nav>
    </div>
  );

  return (
    <section className="project-dashboard">
      <div className="project-register-panel">
        {topBarActionsRoot ? createPortal(registryControls, topBarActionsRoot) : registryControls}
        {management.lastChange && <div className="registry-result-banner" role="status">
          <span>{management.lastChange.display_project_id} {management.lastChange.registry_state === "trash" ? "moved to the recycle bin." : management.lastChange.registry_state === "history" ? "kept in Recycle as a retained record." : "restored to projects."}</span>
          {management.lastChange.registry_state === "trash" && <button className="row-action" type="button" onClick={() => void management.open(management.lastChange!.project_id, "restore")}>Undo</button>}
          <button className="row-action" type="button" onClick={management.clearLastChange}>Dismiss</button>
        </div>}
        {lastLtrApplyResult ? (
          <div className="registry-result-banner" role="status" aria-live="polite">
            <div className="registry-result-banner-text">
              <strong>LTR Number applied: {lastLtrApplyResult.ltr_number}</strong>
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
        {area !== "active" ? <ProjectRegistryManagementPanel search={deferredSearch} revision={managedRevision}
          onManage={(id, action) => void management.open(id, action)} onOpenProject={onOpenProject} /> : <>
        {loading && <LoadingState label="Loading project registry..." />}
        {error && <div><ErrorMessage message={error} /><button className="row-action" type="button" onClick={() => void refreshProjects()}>Retry</button></div>}
        {batchId && <div className="registry-result-banner" role="status"><span>Showing projects from this import.</span>{onViewAll && <button className="row-action" type="button" onClick={onViewAll}>Show All Projects</button>}</div>}
        {search && <button className="row-action" type="button" onClick={() => setSearch("")}>Clear Search</button>}
        {!loading && lifecycleOverlayErrorCount > 0 ? (
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
        {!loading && !error && catalogRows.length === 0 && (
          <EmptyState
            title="No projects yet"
            message="Use Import Projects to add existing folders, or New Project to start a new request."
          />
        )}
        {!loading && !error && catalogRows.length > 0 && viewRows.length === 0 && (
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
        {!loading && filteredRows.length > 0 && (
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
                  <th>Group completion</th>
                  <th><button className="project-id-sort-button" type="button" onClick={() => setDateSort((value) => value === "asc" ? "desc" : "asc")} aria-label="Sort estimated completion">Estimated completion</button></th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {pagedRows.map(item => {
                  if (item.kind !== "registered") return <ProjectFolderRow key={item.key} row={item} onOpenMember={onOpenMember} onOpenLinked={onOpenLinked} />;
                  const { row, lifecycle } = item.entry;
                  return (
                  <tr className="project-registry-row" key={item.key}>
                    <td className="project-no registry-project-id-cell" data-label="Project ID">
                      {businessIdentifier(row)}
                      {(lifecycle && lifecycle.lifecycle_state !== "active") || (!lifecycle && (row.status === "cancelled" || row.status === "closed")) ? <span className={`registry-lifecycle-badge ${registryLifecycleClassName(row, lifecycle)}`}>{registryStatusLabel(row, lifecycle)}</span> : null}
                      {row.display_project_id_kind === "temporary" ? (
                        <span className="registry-temp-badge">Temporary Planning</span>
                      ) : null}
                    </td>
                    <td className="registry-sample-cell" data-label="Sample Description">
                      {displayText(row.sample_description, "Not recorded")}
                      {item.members.length > 0 && <details><summary>Project Files</summary>{item.members.map(member => <div key={member.member_id}><p>{member.folder_path}</p><button className="row-action" type="button" disabled={!onOpenMember} onClick={() => onOpenMember?.(member.member_id)}>Browse Files</button></div>)}</details>}
                    </td>
                    <td className="registry-test-item-column registry-test-item-cell" data-label="Test Item">
                      {displayText(row.test_item, "Not recorded")}
                    </td>
                    <td className="registry-status-text registry-status-cell" data-label="Group completion" title={row.group_completion_details?.map((group) => `${group.group_label}: ${group.completed ? "Completed" : group.needs_review ? "Review needed" : "Not completed"}`).join("\n")}>
                      {row.total_group_count == null ? "—" : `${row.completed_group_count ?? 0} / ${row.total_group_count}`}
                    </td>
                    <td className="registry-next-step registry-next-step-cell" data-label="Estimated completion">
                      <span>{row.estimated_completion_date || "Not scheduled"}</span>
                      {(lifecycle ? lifecycle.lifecycle_state === "active" : row.status !== "closed" && row.status !== "cancelled") && row.estimated_completion_date && scheduleHint(row.estimated_completion_date) ? <small> {scheduleHint(row.estimated_completion_date)}</small> : null}
                    </td>
                    <td className="registry-action-cell" data-label="Action">
                      <div className="project-registry-action-buttons" role="group" aria-label={`Actions for ${row.display_project_id}`}>
                        <button
                          className="row-action project-registry-icon-action"
                          type="button"
                          aria-label={registryRowActionAriaLabel(row, lifecycle)}
                          title={registryRowActionLabel(row, lifecycle)}
                          onClick={() => onOpenProject(row.project_id)}
                        >
                          <UiIcon name="workbench" />
                        </button>
                        {Boolean(lifecycle && !lifecycle.readonly && (!lifecycle.registry_state || lifecycle.registry_state === "active")) && <button
                          className="row-action project-registry-icon-action"
                          type="button"
                          aria-label={`Delete project ${row.display_project_id}`}
                          title="Delete project"
                          onClick={() => void management.open(row.project_id, "trash")}
                        >
                          <UiIcon name="trash" />
                        </button>}
                      </div>
                    </td>
                  </tr>
                ); })}
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
        </>}
        {management.target && <ProjectRegistryManagementDialog key={`${management.target.projectId}:${management.target.action}`}
          action={management.target.action} preview={management.preview} loading={management.loading} busy={management.busy}
          error={management.error} stale={management.stale} onCancel={management.dismiss} onRefresh={() => void management.refresh()}
          onTrash={management.trash} onRestore={management.restore} />}
      </div>
    </section>
  );
}

function loadProjectRegistryViewState(storageKey: string): ProjectRegistryViewState {
  const fallback: ProjectRegistryViewState = {
    search: "",
    selectedView: "all",
    projectIdSort: "desc",
    currentPage: 1,
  };
  try {
    const raw = window.sessionStorage.getItem(storageKey);
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

function saveProjectRegistryViewState(storageKey: string, state: ProjectRegistryViewState): void {
  try {
    window.sessionStorage.setItem(storageKey, JSON.stringify(state));
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

function sortRowsByProjectId(
  rows: ProjectCatalogRow[],
  direction: ProjectIdSortDirection
): ProjectCatalogRow[] {
  const directionFactor = direction === "asc" ? 1 : -1;
  return rows
    .map((entry, index) => ({ entry, index, key: projectIdSortKey(catalogIdentifier(entry)) }))
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

function projectIdSortKey(identifier: string): ProjectIdSortKey {
  const original = identifier.trim();
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

function scheduleHint(value: string): string | null {
  const match = /^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$/.exec(value.trim());
  if (!match) return null;
  const year = Number(match[1]), month = Number(match[2]), day = Number(match[3]);
  const planned = new Date(Date.UTC(year, month - 1, day));
  if (planned.getUTCFullYear() !== year || planned.getUTCMonth() !== month - 1 || planned.getUTCDate() !== day) return null;
  const now = new Date();
  const today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
  const days = (planned.getTime() - today) / 86400000;
  return days < 0 ? "Past planned date" : days <= 3 ? "Due soon" : null;
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
