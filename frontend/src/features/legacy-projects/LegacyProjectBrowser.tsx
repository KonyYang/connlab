import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import { changeLegacyProjectLocation, getLegacyProject, openLegacyProjectFolder, pickLegacyProjectDirectory, type LegacyProjectRecord } from "../../api/legacyProjects";
import "./legacy-project-preview.css";

export function LegacyProjectBrowser({ recordId, onBack, backLabel = "Back to Project Library" }: { recordId: string; backLabel?: string; onBack: () => void }) {
  const [record, setRecord] = useState<LegacyProjectRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [editing, setEditing] = useState(false);
  const [path, setPath] = useState("");
  const [busy, setBusy] = useState(false);
  const [reload, setReload] = useState(0);
  const live = useRef(true);
  const topBarRoot = useTopBarActionsRoot();
  useEffect(() => {
    live.current = true;
    const request = new AbortController();
    setRecord(null); setError(null); setMessage(""); setEditing(false);
    void getLegacyProject(recordId, request.signal).then(next => {
      if (!request.signal.aborted) { setRecord(next); setPath(next.folder_path); }
    }).catch(cause => { if (!request.signal.aborted) setError((cause as Error).message); });
    return () => { live.current = false; request.abort(); };
  }, [recordId, reload]);
  async function act(action: () => Promise<void>) {
    if (busy) return;
    setBusy(true); setError(null); setMessage("");
    try { await action(); } catch (cause) { if (live.current) setError((cause as Error).message); }
    finally { if (live.current) setBusy(false); }
  }
  const back = <button type="button" className="ui-secondary-action" disabled={busy} onClick={onBack}>{backLabel}</button>;
  return <section className="legacy-preview" aria-label="Legacy project details">
    {topBarRoot ? createPortal(back, topBarRoot) : back}
    {error && <p role="alert">{error}</p>}
    {!record && !error && <p role="status">Loading legacy project…</p>}
    {error && <button type="button" disabled={busy} onClick={() => setReload(value => value + 1)}>Reload Record</button>}
    {record && <section className="legacy-preview-panel">
      <h1>{record.name}</h1><span>Folder Kept in Place</span>
      <dl className="legacy-record-facts"><dt>Old Number</dt><dd>{record.number || "No old number"}</dd><dt>Number Evidence</dt><dd>{record.number_evidence.join(", ") || "None"}</dd><dt>Folder</dt><dd>{record.folder_path}</dd><dt>Added</dt><dd>{new Date(record.imported_at).toLocaleString()}</dd></dl>
      {record.notes.length > 0 && <details><summary>Identification Notes ({record.notes.length})</summary><ul>{record.notes.map((note, i) => <li key={i}>{note}</li>)}</ul></details>}
      <div className="legacy-preview-actions"><button type="button" className="primary-action" title="Browse original files in Windows File Explorer. ConnLab does not move or rewrite them." disabled={busy} onClick={() => void act(async () => { const next = await openLegacyProjectFolder(record.record_id); if (live.current) setMessage(next.message); })}>Open Folder</button><button type="button" disabled={busy} title="Reconnect a moved folder by updating its ConnLab location. Files remain unchanged." onClick={() => { setEditing(true); setPath(record.folder_path); }}>Change Location</button></div>
      {message && <p role="status">{message}</p>}
      {editing && <form className="legacy-location-form" onSubmit={event => { event.preventDefault(); void act(async () => { const next = await changeLegacyProjectLocation(record.record_id, path, record.revision); if (live.current) { setRecord(next); setEditing(false); setMessage("Folder location updated. Original files remain unchanged."); } }); }}><label>Folder Path<input value={path} maxLength={4096} disabled={busy} onChange={event => setPath(event.target.value)} /></label><div className="legacy-preview-actions"><button type="button" disabled={busy} onClick={() => void act(async () => { const next = await pickLegacyProjectDirectory(); if (live.current && next) setPath(next); })}>Choose Folder</button><button type="submit" className="primary-action" disabled={busy || !path.trim()}>Save Location</button><button type="button" disabled={busy} onClick={() => setEditing(false)}>Cancel</button></div></form>}
    </section>}
  </section>;
}
