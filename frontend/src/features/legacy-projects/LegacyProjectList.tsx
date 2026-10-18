import { useDeferredValue, useEffect, useState } from "react";
import { listLegacyProjects, type LegacyProjectRecord } from "../../api/legacyProjects";
import "./legacy-project-preview.css";

const SEARCH_KEY = "connlab.legacyProjects.search";

export function LegacyProjectList({ onOpen, onBack }: { onOpen: (recordId: string) => void; onBack: () => void }) {
  const [search, setSearch] = useState(() => sessionStorage.getItem(SEARCH_KEY) ?? "");
  const query = useDeferredValue(search);
  const [rows, setRows] = useState<LegacyProjectRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  const [page, setPage] = useState(1);
  useEffect(() => { sessionStorage.setItem(SEARCH_KEY, search); }, [search]);
  useEffect(() => {
    const request = new AbortController();
    setLoading(true); setError(null); setPage(1);
    void listLegacyProjects(query, request.signal).then(next => {
      if (!request.signal.aborted) setRows(next);
    }).catch(cause => { if (!request.signal.aborted) setError((cause as Error).message); })
      .finally(() => { if (!request.signal.aborted) setLoading(false); });
    return () => request.abort();
  }, [query, revision]);
  const pages = Math.max(1, Math.ceil(rows.length / 20));
  const currentPage = Math.min(page, pages);
  return <section className="legacy-preview legacy-project-list" aria-label="Legacy projects">
    <section className="legacy-preview-panel">
      <div className="legacy-preview-actions"><nav className="legacy-preview-actions" aria-label="Project management areas"><button type="button" className="ui-secondary-action" onClick={onBack}>Active</button><button type="button" className="ui-secondary-action" aria-pressed="true">Legacy</button></nav></div>
      <h2>Legacy Projects</h2>
      <label>Search legacy projects<input type="search" value={search} maxLength={4096} onChange={event => setSearch(event.target.value)} placeholder="Old number, name, folder or path" /></label>
      {loading && <p role="status">Loading legacy projects…</p>}
      {error && <><p role="alert">{error}</p><button type="button" onClick={() => setRevision(value => value + 1)}>Retry</button></>}
      {!loading && !error && <><p>{rows.length} legacy projects</p>{!rows.length ? <p>No matching legacy projects. Add folders from Tools → Import Legacy Projects.</p> : <>
        <div className="legacy-preview-table"><table aria-label="Legacy projects"><thead><tr><th>Old Number / Name</th><th>Folder</th><th>Action</th></tr></thead><tbody>{rows.slice((currentPage - 1) * 20, currentPage * 20).map(row => <tr key={row.record_id}><td><strong>{row.number || "No old number"}</strong><span>{row.name}</span><span>Legacy</span></td><td className="legacy-preview-folder">{row.folder_path}</td><td><button type="button" aria-label={`Browse ${row.name}`} onClick={() => onOpen(row.record_id)}>Browse</button></td></tr>)}</tbody></table></div>
        <div className="legacy-preview-actions"><button type="button" disabled={currentPage <= 1} onClick={() => setPage(currentPage - 1)}>Previous</button><span>Page {currentPage} of {pages}</span><button type="button" disabled={currentPage >= pages} onClick={() => setPage(currentPage + 1)}>Next</button></div>
      </>}</>}
    </section>
  </section>;
}
