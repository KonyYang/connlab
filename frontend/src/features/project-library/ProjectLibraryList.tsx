import { useDeferredValue, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import { listLibraryMembers, openLibraryFolder, type LibraryMember } from "../../api/projectLibrary";
import "./project-library.css";

const SEARCH_KEY = "connlab.projectLibrary.search";
const PAGE_KEY = "connlab.projectLibrary.page";
const snapshotLabels = { missing: "Not Prepared", current: "Ready to Take", stale: "Needs Update", unavailable: "Unavailable" };
export function ProjectLibraryList({ onOpen, onBack, onImport, batchId = "" }: { onOpen: (id: string) => void; onBack: () => void; onImport: () => void; batchId?: string }) {
  const [search, setSearch] = useState(() => sessionStorage.getItem(SEARCH_KEY) ?? "");
  const query = useDeferredValue(search);
  const [rows, setRows] = useState<LibraryMember[]>([]);
  const [page, setPage] = useState(() => Math.max(1, Number(sessionStorage.getItem(PAGE_KEY)) || 1));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [opening, setOpening] = useState("");
  const [revision, setRevision] = useState(0);
  const previous = useRef({ query, batchId });
  const live = useRef(true);
  const topBar = useTopBarActionsRoot();
  useEffect(() => { live.current = true; return () => { live.current = false; }; }, []);
  useEffect(() => { sessionStorage.setItem(SEARCH_KEY, search); }, [search]);
  useEffect(() => { sessionStorage.setItem(PAGE_KEY, String(page)); }, [page]);
  useEffect(() => {
    const request = new AbortController();
    if (query !== previous.current.query || batchId !== previous.current.batchId) setPage(1);
    previous.current = { query, batchId };
    setLoading(true); setError("");
    void listLibraryMembers(query, batchId, request.signal).then(next => { if (!request.signal.aborted) setRows(next.items); }).catch(cause => { if (!request.signal.aborted) setError((cause as Error).message); }).finally(() => { if (!request.signal.aborted) setLoading(false); });
    return () => request.abort();
  }, [query, batchId, revision]);
  async function openFolder(id: string) {
    if (opening) return;
    setOpening(id); setMessage(""); setError("");
    try { const next = await openLibraryFolder(id); if (live.current) setMessage(next.message); }
    catch (cause) { if (live.current) setError((cause as Error).message); }
    finally { if (live.current) setOpening(""); }
  }
  const pages = Math.max(1, Math.ceil(rows.length / 20));
  const currentPage = Math.min(page, pages);
  const navigation = <nav className="library-actions" aria-label="Project management areas"><button type="button" className="ui-secondary-action" onClick={onBack}>Active Projects</button><button type="button" className="ui-secondary-action" aria-current="page">Library</button><button type="button" className="primary-action" onClick={onImport}>Import Projects</button></nav>;
  return <section className="project-library library-member-list" aria-label="Project library">
    {topBar && createPortal(navigation, topBar)}
    <section className="library-panel">{!topBar && navigation}<header className="library-heading"><h1>Project Library</h1><button type="button" onClick={() => setRevision(value => value + 1)}>Refresh Library</button></header>
      {batchId && <p>Showing the selected receiving batch.</p>}
      <label>Search library<input type="search" value={search} maxLength={4096} placeholder="LTR, title, folder or path" onChange={event => setSearch(event.target.value)} /></label>
      {loading && <p role="status">Loading projects…</p>}{error && <div><p role="alert">{error}</p><button type="button" onClick={() => setRevision(value => value + 1)}>Retry</button></div>}{message && <p role="status">{message}</p>}
      {!loading && !error && <><p>{rows.length} projects</p>{!rows.length ? <p>No matching projects. Use Import Projects to receive folders or a portable project.</p> : <><div className="library-table"><table aria-label="Library projects"><thead><tr><th>LTR / Project</th><th>Data</th><th>Actions</th></tr></thead><tbody>{rows.slice((currentPage - 1) * 20, currentPage * 20).map(row => <tr key={row.member_id}><td><strong>{row.ltr_number || "No LTR yet"}</strong><span>{row.title}</span><details><summary>Location</summary><p>{row.folder_path}</p></details></td><td><span>{row.project_id ? "Managed Project" : "Ready to Organize"}</span><span>{snapshotLabels[row.snapshot_status]}</span>{row.warnings.length > 0 && <span>{row.warnings.length} items to review</span>}</td><td><div className="library-actions"><button type="button" aria-label={`Open Folder ${row.title}`} disabled={Boolean(opening)} onClick={() => void openFolder(row.member_id)}>Open Folder</button><button type="button" aria-label={`Manage ${row.title}`} onClick={() => onOpen(row.member_id)}>Manage</button></div></td></tr>)}</tbody></table></div><div className="library-actions"><button type="button" disabled={currentPage <= 1} onClick={() => setPage(currentPage - 1)}>Previous</button><span>Page {currentPage} of {pages}</span><button type="button" disabled={currentPage >= pages} onClick={() => setPage(currentPage + 1)}>Next</button></div></>}</>}
    </section>
  </section>;
}
