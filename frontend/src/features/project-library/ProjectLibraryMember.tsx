import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import { getLibraryMember, getLibraryFiles, getPortableInfo, openLibraryFolder, planLibraryTitle, updateLibraryTitle, planLibraryLocation, updateLibraryLocation, preparePortableProject, planLibraryTakeover, takeoverLibraryProject, pickLibraryFolder, type LibraryMember, type LibraryFiles, type LibraryLocationPlan, type PortableInfo, type LibraryTakeoverPlan } from "../../api/projectLibrary";
import { PortableCoverage } from "./PortableRestore";
import "./project-library.css";

export type LibraryProjectDestination = "workbench" | "matrix" | "report";
const snapshotLabels = { missing: "No Snapshot", current: "Ready to Take", stale: "Needs Update", unavailable: "Unavailable" };
export function ProjectLibraryMember({ memberId, onBack, onOpenProject }: { memberId: string; onBack: () => void; onOpenProject: (id: string, destination: LibraryProjectDestination) => void }) {
  const [member, setMember] = useState<LibraryMember | null>(null);
  const [files, setFiles] = useState<LibraryFiles | null>(null);
  const [relative, setRelative] = useState("");
  const [portable, setPortable] = useState<PortableInfo | null>(null);
  const [editor, setEditor] = useState<"title" | "location" | null>(null);
  const [value, setValue] = useState("");
  const [changePlan, setChangePlan] = useState<LibraryLocationPlan | null>(null);
  const [takeover, setTakeover] = useState<LibraryTakeoverPlan | null>(null);
  const [prepare, setPrepare] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [reload, setReload] = useState(0);
  const live = useRef(true);
  const epoch = useRef(0);
  const topBar = useTopBarActionsRoot();
  useEffect(() => {
    live.current = true;
    const current = ++epoch.current;
    const controller = new AbortController();
    setMember(null); setError(""); setFiles(null); setPortable(null); setEditor(null); setTakeover(null); setRelative("");
    setChangePlan(null); setPrepare(false); setBusy(false); setMessage(""); setValue("");
    const currentResponse = () => !controller.signal.aborted && current === epoch.current;
    void getLibraryMember(memberId, controller.signal).then(next => { if (currentResponse()) setMember(next); }).catch(cause => { if (currentResponse()) setError((cause as Error).message); });
    void getLibraryFiles(memberId, "", controller.signal).then(next => { if (currentResponse()) setFiles(next); }).catch(cause => { if (currentResponse()) setError((cause as Error).message); });
    void getPortableInfo(memberId, controller.signal).then(next => { if (currentResponse()) setPortable(next); }).catch(cause => { if (currentResponse()) setError((cause as Error).message); });
    return () => { live.current = false; controller.abort(); };
  }, [memberId, reload]);
  async function act(action: (current: () => boolean) => Promise<void>) {
    if (busy) return;
    const currentEpoch = epoch.current;
    const current = () => live.current && epoch.current === currentEpoch;
    setBusy(true); setError(""); setMessage("");
    try { await action(current); }
    catch (cause) { if (current()) { setError((cause as Error).message); setChangePlan(null); setPrepare(false); setTakeover(null); } }
    finally { if (current()) setBusy(false); }
  }
  async function refreshProjectData(current: () => boolean, path: string) {
    const [nextFiles, snapshot] = await Promise.allSettled([
      getLibraryFiles(memberId, path), getPortableInfo(memberId),
    ]);
    if (!current()) return;
    if (nextFiles.status === "fulfilled") { setFiles(nextFiles.value); setRelative(path); }
    if (snapshot.status === "fulfilled") setPortable(snapshot.value);
    if (nextFiles.status === "rejected") throw nextFiles.reason;
    if (snapshot.status === "rejected") throw snapshot.reason;
  }
  async function refreshFiles(path = relative) {
    await act(current => refreshProjectData(current, path));
  }
  const locked = busy || Boolean(changePlan) || prepare || Boolean(takeover);
  const back = <button type="button" className="ui-secondary-action" disabled={locked} onClick={onBack}>Back to Library</button>;
  return <section className="project-library" aria-label="Library project details">
    {topBar ? createPortal(back, topBar) : back}
    {error && <div><p role="alert">{error}</p>{!member && <button type="button" onClick={() => setReload(value => value + 1)}>Retry</button>}</div>}
    {!member && !error && <p role="status">Loading library project…</p>}
    {member && <>
      <section className="library-panel"><header className="library-heading"><div><p className="library-eyebrow">{member.ltr_number || "No LTR yet"}</p><h1>{member.title}</h1></div><button type="button" className="primary-action" disabled={locked} onClick={() => void act(async current => { const next = await openLibraryFolder(memberId); if (current()) setMessage(next.message); })}>Open Folder</button></header>
        <details><summary>Project Location</summary><p>{member.folder_path}</p></details>
        {member.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}{message && <p role="status">{message}</p>}
        <div className="library-actions"><button type="button" disabled={locked} title="Change the description while keeping this project's LTR and identity." onClick={() => { setEditor("title"); setValue(member.title); }}>Edit Title</button><button type="button" disabled={locked} onClick={() => { setEditor("location"); setValue(member.folder_path); }}>Locate Folder</button>{member.project_id && member.can_continue ? <><button type="button" disabled={locked} onClick={() => onOpenProject(member.project_id!, "workbench")}>Project Workbench</button><button type="button" disabled={locked} onClick={() => onOpenProject(member.project_id!, "matrix")}>Matrix</button><button type="button" disabled={locked} onClick={() => onOpenProject(member.project_id!, "report")}>Report</button></> : <button type="button" disabled={locked} onClick={() => void act(async current => { const next = await planLibraryTakeover(memberId); if (current()) setTakeover(next); })}>Continue Testing</button>}</div>
        {editor && <form className="library-editor" onSubmit={event => { event.preventDefault(); void act(async current => { const next = editor === "title" ? await planLibraryTitle(memberId, value.trim()) : await planLibraryLocation(memberId, value.trim()); if (current()) setChangePlan(next); }); }}><label>{editor === "title" ? "Project title" : "New project folder"}<input value={value} disabled={locked} onChange={event => { setValue(event.target.value); setChangePlan(null); }} /></label><div className="library-actions">{editor === "location" && <button type="button" disabled={locked} onClick={() => void act(async current => { const folder = await pickLibraryFolder(); if (current() && folder) setValue(folder); })}>Choose Location</button>}<button type="submit" disabled={locked || !value.trim()}>{editor === "title" ? "Review Title" : "Review Location"}</button><button type="button" disabled={locked} onClick={() => setEditor(null)}>Cancel Edit</button></div></form>}
        {changePlan && <div className="library-review" role="dialog" aria-modal="false" aria-labelledby="library-change-title"><h2 id="library-change-title">Confirm {editor === "title" ? "Title" : "Location"}</h2><dl className="library-location-pair"><dt>Current</dt><dd>{changePlan.source_path}</dd><dt>After Change</dt><dd>{changePlan.target_path}</dd></dl>{changePlan.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}<div className="library-actions"><button type="button" className="primary-action" autoFocus disabled={busy} onClick={() => void act(async current => { const token = { plan_id: changePlan.plan_id, fingerprint: changePlan.fingerprint }; const next = editor === "title" ? await updateLibraryTitle(memberId, token) : await updateLibraryLocation(memberId, token); if (!current()) return; setMember(next); setEditor(null); setChangePlan(null); setPortable(null); setFiles(null); setRelative(""); setMessage("Project location updated. LTR and project identity are retained."); await refreshProjectData(current, ""); })}>Confirm {editor === "title" ? "Title" : "Location"}</button><button type="button" disabled={busy} onClick={() => setChangePlan(null)}>Cancel Change</button></div></div>}
        {takeover && <div className="library-review" role="dialog" aria-modal="false" aria-labelledby="library-takeover-title"><h2 id="library-takeover-title">Review Takeover</h2>{takeover.missing.length > 0 && <><p>These facts need review in the project workbench:</p><ul>{takeover.missing.map((note, i) => <li key={i}>{note}</li>)}</ul></>}{takeover.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}{takeover.blockers.map((note, i) => <p key={i} role="alert">{note}</p>)}<div className="library-actions"><button type="button" className="primary-action" disabled={busy || takeover.blockers.length > 0 || takeover.status === "conflict"} onClick={() => void act(async current => { const next = await takeoverLibraryProject(memberId, { plan_id: takeover.plan_id, fingerprint: takeover.fingerprint }); if (!current()) return; setMember(next.member); setTakeover(null); setPortable(null); setFiles(null); setRelative(""); setMessage("Project is available in the workbench. Confirm missing information before formal outputs."); await refreshProjectData(current, ""); })}>Confirm Takeover</button><button type="button" disabled={busy} onClick={() => setTakeover(null)}>Cancel Takeover</button></div></div>}
      </section>
      <section className="library-panel"><header className="library-heading"><h2>Files</h2><button type="button" disabled={locked} onClick={() => void refreshFiles()}>Refresh Files</button></header><p>Files and folders can be added, edited or removed in Windows. Refresh to see changes.</p>{relative && <div className="library-actions"><button type="button" disabled={locked} onClick={() => void refreshFiles(relative.replaceAll("\\", "/").split("/").slice(0, -1).join("/"))}>Up One Folder</button><span>{relative}</span></div>}{files?.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}{files && !files.items.length && <p>No files in this folder.</p>}{files && files.items.length > 0 && <div className="library-table"><table aria-label="Project files"><thead><tr><th>Name</th><th>Size</th></tr></thead><tbody>{files.items.map(file => <tr key={file.relative_path}><td>{file.is_directory ? <button type="button" disabled={locked} onClick={() => void refreshFiles(file.relative_path)}>{file.name}</button> : file.name}</td><td>{file.is_directory ? "Folder" : file.size_bytes === null ? "—" : `${file.size_bytes.toLocaleString()} bytes`}</td></tr>)}</tbody></table></div>}</section>
      <section className="library-panel"><header className="library-heading"><h2>Take This Project to Another Computer</h2>{portable && <strong>{snapshotLabels[portable.status]}</strong>}</header>{portable && <><p>Prepared: {portable.created_at ? new Date(portable.created_at).toLocaleString() : "Not yet"}</p><PortableCoverage counts={portable.record_counts} fileCount={portable.file_count} label={portable.created_at ? "Saved Snapshot Data" : "Data to Prepare"} />{portable.status === "stale" && <p role="status">Saved snapshot does not include the latest project changes. Prepare again before taking this project to another computer.</p>}{portable.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}{portable.blockers.map((note, i) => <p key={i} role="alert">{note}</p>)}<p>Prepare the latest data, then copy the complete project folder, including its ConnLab data, to the other computer.</p><button type="button" className="primary-action" disabled={locked || portable.blockers.length > 0} onClick={() => setPrepare(true)}>Prepare to Take</button>{prepare && <div className="library-review" role="dialog" aria-modal="false" aria-labelledby="library-snapshot-title"><h3 id="library-snapshot-title">Confirm Snapshot</h3><p>Save the latest project data into this project's portable snapshot?</p><div className="library-actions"><button type="button" autoFocus disabled={busy} onClick={() => void act(async current => { const next = await preparePortableProject(memberId, portable.fingerprint); if (current()) { setPortable(next); setPrepare(false); } })}>Confirm Snapshot</button><button type="button" disabled={busy} onClick={() => setPrepare(false)}>Cancel Snapshot</button></div></div>}</>}</section>
    </>}
  </section>;
}
