import { useEffect, useRef, useState } from "react";
import { openReferenceFile, searchReferenceLibrary, type ReferenceResults } from "../api/referenceLibrary";
import "./reference-library.css";

const kinds: Record<string, string> = { application: "Application", plan: "Test plan", record: "Test record", report: "Report", photo: "Photo", other: "Other" };
const sources: Record<string, string> = { connlab: "ConnLab project", received: "Received materials", linked: "Linked folder" };
const saved = () => { try { return JSON.parse(sessionStorage.getItem("reference-search") ?? "{}"); } catch { return {}; } };
export function ReferenceLibraryPage({ onOpenProject, onOpenMember, onOpenLinked }: { onOpenProject: (id: string) => void; onOpenMember: (id: string) => void; onOpenLinked?: (id: string) => void }) {
  const [query, setQuery] = useState<string>(() => saved().query ?? "");
  const [search, setSearch] = useState<string>(() => saved().query ?? "");
  const [source, setSource] = useState<string>(() => saved().source ?? "all");
  const [kind, setKind] = useState<string>(() => saved().kind ?? "all");
  const [view, setView] = useState<string>(() => saved().view ?? "files");
  const [project, setProject] = useState<string>(() => saved().project ?? "");
  const [offset, setOffset] = useState(0);
  const [reload, setReload] = useState(0);
  const [data, setData] = useState<ReferenceResults | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const epoch = useRef(0);
  useEffect(() => {
    const controller = new AbortController();
    const current = ++epoch.current;
    setBusy(true); setError(""); setData(null);
    sessionStorage.setItem("reference-search", JSON.stringify({ query: search, source, kind, view, project }));
    void searchReferenceLibrary(search, source, kind, project, offset, controller.signal).then(result => {
      if (current === epoch.current && !controller.signal.aborted) setData(result);
    }).catch(cause => { if (!controller.signal.aborted) setError((cause as Error).message); })
      .finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [search, source, kind, project, offset, reload]);
  async function open(key: string, path = "", containing = false) {
    const current = epoch.current;
    setError("");
    try { await openReferenceFile(key, path, containing); }
    catch (cause) { if (current === epoch.current) setError((cause as Error).message); }
  }
  function selectView(next: string) {
    setView(next);
    sessionStorage.setItem("reference-search", JSON.stringify({ query: search, source, kind, view: next, project }));
  }
  return <section className="reference-library" aria-label="Project materials library">
    <form className="reference-search" onSubmit={event => { event.preventDefault(); setSearch(query); setOffset(0); setReload(value => value + 1); }}>
      <input aria-label="Search project materials" placeholder="Project number, product, test item or filename…" value={query} onChange={event => setQuery(event.target.value)} />
      <button type="submit" disabled={busy}>Search</button>
      <button type="button" disabled={busy} onClick={() => setReload(value => value + 1)}>Refresh</button>
    </form>
    <div className="reference-filters">
      <label>Source <select value={source} onChange={event => { setSource(event.target.value); setOffset(0); }}><option value="all">All sources</option>{Object.entries(sources).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
      <label>Material type <select value={kind} onChange={event => { setKind(event.target.value); setOffset(0); }}>{[ ["all", "All types"], ...Object.entries(kinds)].map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
      <button type="button" onClick={() => { setQuery(""); setSearch(""); setSource("all"); setKind("all"); setProject(""); setOffset(0); }}>Clear filters</button>
    </div>
    {error && <p role="alert">{error} <button onClick={() => setReload(value => value + 1)}>Retry</button></p>}
    {busy && <p role="status">Searching project materials…</p>}
    {data?.warnings.length ? <div role="status">{data.warnings.map(note => <p key={note}>{note}</p>)}</div> : null}
    {project && <div className="reference-filters"><span>Browsing project materials</span><button onClick={() => { setProject(""); setOffset(0); }}>All projects</button></div>}
    <div className="reference-filters"><button aria-pressed={view === "files"} onClick={() => selectView("files")}>Files</button><button aria-pressed={view === "projects"} onClick={() => selectView("projects")}>Projects</button></div>
    {data && (view === "projects" || !search && !project && kind === "all") ? <div className="reference-results"><table><thead><tr><th>Project / Product</th><th>Test item</th><th>Source / Location</th><th>Actions</th></tr></thead><tbody>{data.projects.map(row => <tr key={row.key}>
      <td><span>{row.number || "No number"}</span><strong>{row.title}</strong></td><td>{row.test_item || "Not recorded"}</td><td>{sources[row.source]}{!row.available && <p>Material location unavailable</p>}</td>
      <td><button onClick={() => { setProject(row.key); setOffset(0); selectView("files"); }}>Browse files</button><button disabled={!row.available} onClick={() => void open(row.key)}>Open folder</button>{row.member_id ? <button onClick={() => onOpenMember(row.member_id!)}>Details / Locate folder</button> : row.project_id ? <button onClick={() => onOpenProject(row.project_id!)}>Project workspace</button> : row.key.startsWith("linked:") ? <button onClick={() => onOpenLinked?.(row.key.slice(7))}>Details / Locate folder</button> : null}</td>
    </tr>)}</tbody></table>{!data.projects.length && <p>No matching projects. Check filters or refresh.</p>}</div> : data && <>
      <p>{data.total} matching files</p><div className="reference-results"><table><thead><tr><th>Filename</th><th>Project / Product</th><th>Material type</th><th>Directory</th><th>Actions</th></tr></thead><tbody>{data.files.map(row => <tr key={`${row.key}:${row.relative_path}`}>
        <td><button onClick={() => void open(row.key, row.relative_path, false)}>{row.name}</button></td><td><button onClick={() => { setProject(row.key); setOffset(0); }}>{row.number || "No number"}</button><span>{row.title}</span></td><td>{kinds[row.kind]}</td><td>{row.directory === "." ? "Project root" : row.directory}</td><td><button onClick={() => void open(row.key, row.relative_path, true)}>Open containing folder</button></td>
      </tr>)}</tbody></table></div>
      {!data.files.length && <p>No matching files. Check keywords and filters. Any incomplete locations are listed above.</p>}
      <div className="reference-filters"><button disabled={offset === 0 || busy} onClick={() => setOffset(value => Math.max(0, value - 100))}>Previous</button><button disabled={offset + 100 >= data.total || busy} onClick={() => setOffset(value => value + 100)}>Next</button></div>
    </>}
  </section>;
}
