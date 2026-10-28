import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import { pickLegacyProjectDirectory, previewLegacyProjects, planLegacyRegistration, importLegacyProjects,
  type LegacyProjectPreviewResult, type LegacyRegistrationPlan, type LegacyRegistrationResult } from "../../api/legacyProjects";
import "./legacy-project-preview.css";

export function LegacyProjectPreview({ onBack, onViewImported }: { onBack: () => void; onViewImported?: () => void }) {
  const topBarRoot = useTopBarActionsRoot();
  const [roots, setRoots] = useState<string[]>([]);
  const [manual, setManual] = useState("");
  const [result, setResult] = useState<LegacyProjectPreviewResult | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [picking, setPicking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [plan, setPlan] = useState<LegacyRegistrationPlan | null>(null);
  const [keepSeparate, setKeepSeparate] = useState<string[]>([]);
  const [checking, setChecking] = useState(false);
  const [importing, setImporting] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [importResult, setImportResult] = useState<LegacyRegistrationResult | null>(null);
  const request = useRef<AbortController | null>(null);
  const live = useRef(true);
  useEffect(() => {
    live.current = true;
    return () => { live.current = false; request.current?.abort(); };
  }, []);

  function changeRoots(next: string[]) {
    setPlan(null); setKeepSeparate([]); setImportResult(null); setConfirming(false);
    setRoots(next); setResult(null); setSelected([]); setError(null); setMessage("");
  }
  function addRoot(path: string) {
    const clean = path.trim().replace(/^"|"$/g, "");
    if (clean && !roots.includes(clean)) changeRoots([...roots, clean]);
  }
  async function choose() {
    if (picking) return;
    setPicking(true); setError(null);
    try {
      const path = await pickLegacyProjectDirectory();
      if (live.current && path) addRoot(path);
    } catch (cause) { if (live.current) setError((cause as Error).message); }
    finally { if (live.current) setPicking(false); }
  }
  async function preview() {
    if (request.current || !roots.length) return;
    const current = new AbortController();
    request.current = current; setBusy(true); setError(null); setResult(null); setSelected([]); setMessage("");
    setPlan(null); setKeepSeparate([]); setImportResult(null); setConfirming(false);
    try {
      const next = await previewLegacyProjects(roots, current.signal);
      if (!live.current || request.current !== current) return;
      setResult(next); setSelected(next.projects.filter(item => item.status === "ready").map(item => item.folder));
    } catch (cause) {
      if (live.current && request.current === current && !current.signal.aborted) setError((cause as Error).message);
    } finally {
      if (live.current && request.current === current) { request.current = null; setBusy(false); }
    }
  }
  function stop() {
    request.current?.abort(); request.current = null; setBusy(false);
    setMessage("Preview stopped. Selected folders are kept; you can start again.");
  }
  async function checkRegistration() {
    if (!result || request.current || checking || importing) return;
    const current = new AbortController();
    request.current = current; setChecking(true); setError(null); setConfirming(false);
    setPlan(null); setKeepSeparate([]); setImportResult(null);
    try {
      const next = await planLegacyRegistration(result.projects.map(row => row.folder), current.signal);
      if (!live.current || request.current !== current) return;
      setPlan(next);
      setSelected(values => values.filter(path => next.projects.some(row => row.folder === path && row.status === "ready")));
    } catch (cause) { if (live.current && !current.signal.aborted) setError((cause as Error).message); }
    finally { if (live.current && request.current === current) { request.current = null; setChecking(false); } }
  }
  async function importSelected() {
    if (!plan || !result || importing || !selected.length) return;
    setImporting(true); setConfirming(false); setError(null);
    try {
      const next = await importLegacyProjects(result.projects.map(row => row.folder), plan.projects.filter(row => selected.includes(row.folder)).map(row => ({ folder: row.folder, fingerprint: row.fingerprint, keep_separate: keepSeparate.includes(row.folder) })));
      if (!live.current) return;
      setImportResult(next); setPlan(null); setSelected([]); setKeepSeparate([]);
    } catch (cause) { if (live.current) { setError((cause as Error).message); setPlan(null); setSelected([]); } }
    finally { if (live.current) setImporting(false); }
  }
  const locked = busy || picking || checking || importing || confirming;
  const projects = plan?.projects ?? result?.projects ?? [];
  const backButton = <button type="button" className="ui-secondary-action" disabled={picking || checking || importing || confirming} onClick={onBack}>Back to Import Projects</button>;
  return <section className="legacy-preview" aria-label="Legacy project batch preview">
    {topBarRoot && createPortal(backButton, topBarRoot)}
    {!topBarRoot && <header className="legacy-preview-heading">
      <h1>Import Legacy Projects</h1>
      {backButton}
    </header>}
    <section className="legacy-preview-panel" aria-label="Choose legacy project folders">
      <h2>1. Choose Folders</h2>
      <div className="legacy-preview-actions">
        <button type="button" className="primary-action" title="Choose a project folder or a parent folder containing multiple projects. Add up to 20 locations, one at a time." disabled={locked || roots.length >= 20} onClick={() => void choose()}>{picking ? "Waiting for folder selection…" : "Choose Folder"}</button>
      </div>
      <details><summary title="Enter a folder path if you cannot use the folder picker.">Enter Folder Path Manually</summary>
        <div className="legacy-preview-manual"><label>Folder Path<input value={manual} maxLength={4096} disabled={locked} onChange={event => setManual(event.target.value)} placeholder="Paste a folder path accessible on this computer" /></label>
          <button type="button" title="Add this folder to the preview list. You can add up to 20 locations." disabled={locked || !manual.trim() || roots.length >= 20} onClick={() => { addRoot(manual); setManual(""); }}>Add Folder</button></div>
      </details>
      {roots.length > 0 && <ul className="legacy-preview-roots">{roots.map(path => <li key={path}><span>{path}</span><button type="button" disabled={locked} aria-label={`Remove ${path}`} title="Remove this location from the preview list. Files remain unchanged." onClick={() => changeRoots(roots.filter(item => item !== path))}>Remove</button></li>)}</ul>}
      <div className="legacy-preview-actions">
        <button type="button" className="primary-action" title="Read-only preview. Original files and folder structure remain unchanged. No projects will be registered." disabled={!roots.length || locked} onClick={() => void preview()}>Start Preview</button>
        {busy && <><span role="status">Checking selected folders and project boundaries…</span><button type="button" onClick={stop}>Stop Preview</button></>}
      </div>
      {error && <p role="alert">{error}</p>}{message && <p role="status">{message}</p>}
    </section>
    {result && <section className="legacy-preview-panel" aria-label="Preview results">
      <h2>2. Review Projects</h2>
      <p>{result.projects.length} projects found; {selected.length} selected.</p>
      {result.duplicate_roots > 0 && <p>{result.duplicate_roots} duplicate or overlapping folder selections combined.</p>}
      {result.truncated && <p role="alert">Incomplete results: the preview limit was reached. Choose a more specific folder and try again.</p>}
      {result.diagnostics.length > 0 && <details><summary>Unreadable or skipped folders ({result.diagnostics.length})</summary><ul>{result.diagnostics.map((text, i) => <li key={i}>{text}</li>)}</ul></details>}
      {!result.projects.length ? <p>No project files found. Choose a specific project folder and try again.</p> : <>
        <div className="legacy-preview-actions">
          <button type="button" disabled={locked} title="Select projects with no detected conflicts. Check Registration also compares existing ConnLab records." onClick={() => setSelected(projects.filter(item => item.status === "ready").map(item => item.folder))}>Select Clear Projects</button>
          <button type="button" disabled={locked} onClick={() => setSelected([])}>Clear Selection</button>
          <button type="button" disabled={locked || result.projects.length > 1000} title="Compare these folders with registered legacy and business projects. Checks do not register anything. Up to 1,000 projects per batch." onClick={() => void checkRegistration()}>{checking ? "Checking Registration…" : "Check Registration"}</button>
          {plan && <button type="button" className="primary-action" disabled={locked || !selected.length} title="Add selected historical records to ConnLab. Original files and directory structure remain unchanged." onClick={() => setConfirming(true)}>Import Selected</button>}
        </div>
        {result.projects.length > 1000 && <p role="alert">Choose a smaller batch of up to 1,000 projects to register.</p>}
        <div className="legacy-preview-table"><table aria-label="Legacy project preview"><thead><tr><th>Select</th><th>Suggested Number / Project Name</th><th>Folder</th><th>Check Result</th></tr></thead><tbody>{projects.map(item => <tr key={item.folder}>
          <td><input type="checkbox" aria-label={`Select ${item.name}`} disabled={locked || item.status === "already_added" || item.status === "failed" || Boolean(plan && item.status === "review" && !keepSeparate.includes(item.folder))} checked={selected.includes(item.folder)} onChange={event => setSelected(values => event.target.checked ? [...values, item.folder] : values.filter(value => value !== item.folder))} /></td>
          <td><strong>{item.number || "No old number"}</strong><span>{item.name}</span></td><td className="legacy-preview-folder">{item.folder}</td>
          <td><strong className={item.status === "review" || item.status === "failed" ? "legacy-preview-review" : "legacy-preview-ready"}>{item.status === "review" ? "Needs Review" : item.status === "already_added" ? "Already Added" : item.status === "failed" ? "Unavailable" : plan ? "Ready to Import" : "Ready for Preview"}</strong>
            {plan && "can_keep_separate" in item && item.can_keep_separate && <label className="legacy-keep-separate"><input type="checkbox" disabled={locked} checked={keepSeparate.includes(item.folder)} onChange={event => { const checked = event.target.checked; setKeepSeparate(values => checked ? [...values, item.folder] : values.filter(path => path !== item.folder)); setSelected(values => checked ? [...values, item.folder] : values.filter(path => path !== item.folder)); }} />Keep Separate</label>}
            {item.notes.length > 0 && <ul>{item.notes.map((note, i) => <li key={i}>{note}</li>)}</ul>}
            {item.duplicate_folders?.length > 0 && <details><summary>Other folders with matching numbers or legacy identifiers: {item.duplicate_count} (up to 5 shown)</summary><ul>{item.duplicate_folders.map(path => <li key={path}>{path}</li>)}</ul></details>}</td>
        </tr>)}</tbody></table></div>
      </>}
    </section>}
    {confirming && <section className="legacy-preview-panel" role="dialog" aria-modal="false" aria-labelledby="legacy-import-confirm-title"><h2 id="legacy-import-confirm-title">Confirm Import</h2><p>Add {selected.length} historical projects to ConnLab? Original files remain unchanged.</p><div className="legacy-preview-actions"><button type="button" className="primary-action" autoFocus onClick={() => void importSelected()}>Confirm Import</button><button type="button" onClick={() => setConfirming(false)}>Cancel</button></div></section>}
    {importing && <p role="status">Registering selected projects…</p>}
    {importResult && <section className="legacy-preview-panel" aria-label="Import result"><p role="status">{importResult.counts.added} added; {importResult.counts.already_added} already added; {importResult.counts.review} need review; {importResult.counts.failed} failed.</p>{importResult.items.filter(item => item.status === "failed" || item.status === "review").map(item => <p key={item.folder}>{item.folder}: {item.message}</p>)}<button type="button" className="primary-action" onClick={onViewImported}>View Imported Projects</button></section>}
  </section>;
}
