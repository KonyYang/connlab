import { useEffect, useRef, useState } from "react";
import { openLibraryDestination, pickLibraryDestination, saveLibraryDestination, type LibraryRuntime } from "../../api/projectLibrary";

type Props = { runtime: LibraryRuntime; disabled: boolean; onChanged: (runtime: LibraryRuntime) => void };

export function ProjectImportDestination({ runtime, disabled, onChanged }: Props) {
  const [editing, setEditing] = useState(!runtime.configured);
  const [folder, setFolder] = useState(runtime.configured ? runtime.projects_root : "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const live = useRef(true);
  useEffect(() => { live.current = true; return () => { live.current = false; }; }, []);
  useEffect(() => {
    setEditing(!runtime.configured); setFolder(runtime.configured ? runtime.projects_root : ""); setError("");
  }, [runtime.configured, runtime.projects_root]);
  async function run(action: () => Promise<void>) {
    if (busy || disabled) return;
    setBusy(true); setError("");
    try { await action(); }
    catch (cause) { if (live.current) setError((cause as Error).message); }
    finally { if (live.current) setBusy(false); }
  }
  const locked = disabled || busy;
  return <section className="library-panel library-destination" aria-label="Import save location">
    <h2>Save imported projects to</h2>
    {runtime.configured && <div className="library-destination-current"><p>{runtime.projects_root}</p><div className="library-actions">
      {runtime.destination_editable !== false && <button type="button" disabled={locked || editing} title="Choose a different location for future imports. This clears the current selection and leaves existing projects in place." onClick={() => setEditing(true)}>Change</button>}
      <button type="button" disabled={locked} onClick={() => void run(async () => { const result = await openLibraryDestination(); if (result.status !== "opened") throw new Error(result.message); })}>Open Folder</button>
    </div></div>}
    {!runtime.configured && <p role="status">{runtime.location_error || "Choose a save location before selecting projects."}</p>}
    {editing && runtime.destination_editable !== false && <div className="library-destination-editor">
      <label>Save imported projects to<input value={folder} disabled={locked} placeholder="Choose an existing folder" onChange={event => { setFolder(event.target.value); setError(""); }} /></label>
      <div className="library-actions">
        <button type="button" disabled={locked} onClick={() => void run(async () => { const selected = await pickLibraryDestination(); if (live.current && selected) setFolder(selected); })}>Choose Save Location</button>
        <button type="button" className="primary-action" disabled={locked || !folder.trim()} onClick={() => void run(async () => { const next = await saveLibraryDestination(folder.trim()); if (live.current) { setEditing(false); onChanged(next); } })}>Use This Location</button>
        {runtime.configured && <button type="button" disabled={locked} onClick={() => { setEditing(false); setFolder(runtime.projects_root); setError(""); }}>Cancel</button>}
      </div>
    </div>}
    {!runtime.configured && runtime.destination_editable === false && <p>{runtime.projects_root}. Reconnect this managed project folder before importing.</p>}
    {busy && <p role="status">Checking the save location…</p>}
    {error && <p role="alert">{error}</p>}
  </section>;
}
