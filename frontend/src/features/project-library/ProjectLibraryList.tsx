import { useDeferredValue, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import { listLibraryMembers, type LibraryMember } from "../../api/projectLibrary";
import { listLegacyProjects, type LegacyProjectRecord } from "../../api/legacyProjects";
import "./project-library.css";

const snapshotLabels = { missing: "Not Prepared", current: "Ready to Take", stale: "Needs Update", unavailable: "Unavailable", not_checked: "Not Checked" };
type ProjectRow = { kind: "managed"; record: LibraryMember } | { kind: "linked"; record: LegacyProjectRecord };
const titleOf = (row: ProjectRow) => row.kind === "managed" ? row.record.title : row.record.name;
type Props = { onOpen: (id: string) => void; onOpenLinked: (id: string) => void; onBack: () => void; onImport: () => void; batchId?: string; onViewAll?: () => void };

export function ProjectLibraryList(props: Props) {
  return <ProjectLibraryResults key={props.batchId ? `batch:${props.batchId}` : "all"} {...props} />;
}

function ProjectLibraryResults({ onOpen, onOpenLinked, onBack, onImport, batchId = "", onViewAll }: Props) {
  // A new batch must not inherit filters that can hide the projects just received.
  const storageKey = batchId ? `connlab.projectLibrary.batch:${batchId}` : "connlab.projectLibrary";
  const [search, setSearch] = useState(() => sessionStorage.getItem(`${storageKey}.search`) ?? "");
  const query = useDeferredValue(search);
  const [rows, setRows] = useState<ProjectRow[]>([]);
  const [page, setPage] = useState(() => Math.max(1, Number(sessionStorage.getItem(`${storageKey}.page`)) || 1));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [revision, setRevision] = useState(0);
  const previous = useRef({ query, batchId });
  const topBar = useTopBarActionsRoot();
  useEffect(() => { sessionStorage.setItem(`${storageKey}.search`, search); }, [storageKey, search]);
  useEffect(() => { sessionStorage.setItem(`${storageKey}.page`, String(page)); }, [storageKey, page]);
  useEffect(() => {
    const request = new AbortController();
    if (query !== previous.current.query || batchId !== previous.current.batchId) setPage(1);
    previous.current = { query, batchId };
    setLoading(true); setError("");
    // A receiving batch contains only its own members; the normal library includes linked folders.
    void Promise.allSettled([
      listLibraryMembers(query, batchId, request.signal),
      batchId ? Promise.resolve([] as LegacyProjectRecord[]) : listLegacyProjects(query, request.signal),
    ]).then(([managed, linked]) => {
      if (request.signal.aborted) return;
      const next: ProjectRow[] = [];
      if (managed.status === "fulfilled") next.push(...managed.value.items.map(record => ({ kind: "managed" as const, record })));
      if (linked.status === "fulfilled") next.push(...linked.value.map(record => ({ kind: "linked" as const, record })));
      next.sort((a, b) => titleOf(a).localeCompare(titleOf(b), undefined, { numeric: true }));
      setRows(next);
      setError(managed.status === "rejected" || linked.status === "rejected" ? "Some projects could not be loaded. Retry to load the complete list." : "");
      setLoading(false);
    });
    return () => request.abort();
  }, [query, batchId, revision]);
  const pages = Math.max(1, Math.ceil(rows.length / 20));
  const currentPage = Math.min(page, pages);
  const navigation = <nav className="library-actions" aria-label="Project management areas"><button type="button" className="ui-secondary-action" onClick={onBack}>Back to Projects</button><button type="button" className="primary-action" onClick={onImport}>Import Projects</button></nav>;
  return <section className="project-library library-member-list" aria-label="Project library">
    {topBar && createPortal(navigation, topBar)}
    <section className="library-panel">
      {!topBar && navigation}
      <header className="library-heading"><h1>Project Library</h1><button type="button" onClick={() => setRevision(value => value + 1)}>Refresh Library</button></header>
      {batchId && <div className="library-actions"><p>Showing the selected receiving batch.</p>{onViewAll && <button type="button" onClick={onViewAll}>Show All Projects</button>}</div>}
      <label>Search library<input type="search" value={search} maxLength={4096} placeholder="LTR, title, folder or path" onChange={event => setSearch(event.target.value)} /></label>
      {search && <div className="library-actions"><button type="button" onClick={() => { setSearch(""); setPage(1); }}>Clear Search</button></div>}
      {loading && <p role="status">Loading projects…</p>}
      {error && <div><p role="alert">{error}</p><button type="button" onClick={() => setRevision(value => value + 1)}>Retry</button></div>}
      {!loading && <>
        <p>{rows.length} projects</p>
        {!rows.length ? !error && <p>{query ? "No projects match this search. Clear Search to see the other projects." : batchId ? "No projects in this receiving batch." : "No projects yet. Use Import Projects to add existing projects."}</p> : <>
          <div className="library-table"><table aria-label="Library projects">
            <thead><tr><th>LTR / Project</th><th>Status</th><th>Action</th></tr></thead>
            <tbody>{rows.slice((currentPage - 1) * 20, currentPage * 20).map(row => {
              const title = titleOf(row);
              const id = row.kind === "managed" ? row.record.member_id : row.record.record_id;
              return <tr key={`${row.kind}:${id}`}>
                <td><strong>{(row.kind === "managed" ? row.record.ltr_number : row.record.number) || "No LTR yet"}</strong><span>{title}</span><details><summary>Details</summary><p>{row.record.folder_path}</p>{row.kind === "managed" && <p>{snapshotLabels[row.record.snapshot_status]}</p>}</details></td>
                <td>{row.kind === "managed" ? <><span>{row.record.is_history ? "Historical Copy" : row.record.project_id ? "Managed Project" : "Ready to Organize"}</span>{row.record.warnings.length > 0 && <span>{row.record.warnings.length} items to review</span>}</> : <span>Files Only</span>}</td>
                <td><button type="button" aria-label={`Open ${title}`} onClick={() => row.kind === "managed" ? onOpen(id) : onOpenLinked(id)}>Open</button></td>
              </tr>;
            })}</tbody>
          </table></div>
          <div className="library-actions"><button type="button" disabled={currentPage <= 1} onClick={() => setPage(currentPage - 1)}>Previous</button><span>Page {currentPage} of {pages}</span><button type="button" disabled={currentPage >= pages} onClick={() => setPage(currentPage + 1)}>Next</button></div>
        </>}
      </>}
    </section>
  </section>;
}
