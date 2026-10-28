import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import { getLibraryRuntime, listLibraryMembers, scanLibrarySources, planLibraryIntake, startLibraryBatch, getLibraryBatch, resumeLibraryBatch, pickLibraryFolder, type LibraryRuntime, type LibraryMember, type LibraryFileAssignment, type LibraryScan, type LibraryIntakePlan, type LibraryBatch, type LibraryBatchRequest } from "../../api/projectLibrary";
import { PortableRestore } from "./PortableRestore";
import "./project-library.css";

type Props = { onBack: () => void; onViewLibrary: (batchId?: string) => void; onOpenMember: (id: string) => void; onLegacyPreview?: () => void };
const labels = { ready: "Ready to Add", conflict: "Needs Review", already_added: "Already Added", unavailable: "Unavailable" };

export function ProjectLibraryImport({ onBack, onViewLibrary, onOpenMember, onLegacyPreview }: Props) {
  const [runtime, setRuntime] = useState<LibraryRuntime | null>(null);
  const [sources, setSources] = useState("");
  const [scan, setScan] = useState<LibraryScan | null>(null);
  const [plan, setPlan] = useState<LibraryIntakePlan | null>(null);
  const [assignments, setAssignments] = useState<Record<string, { target: string; title: string }>>({});
  const [existingMembers, setExistingMembers] = useState<LibraryMember[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [separate, setSeparate] = useState<string[]>([]);
  const [filter, setFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [busy, setBusy] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState("");
  const [batch, setBatch] = useState<LibraryBatch | null>(null);
  const [recoveryId, setRecoveryId] = useState("");
  const [submission, setSubmission] = useState<LibraryBatchRequest | null>(null);
  const interactionEpoch = useRef(0);
  const live = useRef(true);
  const request = useRef<AbortController | null>(null);
  const topBar = useTopBarActionsRoot();
  useEffect(() => {
    live.current = true;
    const controller = new AbortController();
    const recoveryEpoch = interactionEpoch.current;
    void getLibraryRuntime(controller.signal).then(async value => {
      if (controller.signal.aborted) return;
      setRuntime(value);
      const previousBatch = localStorage.getItem(`connlab.projectLibrary.lastBatch:${value.projects_root}`);
      if (previousBatch && recoveryEpoch === interactionEpoch.current) {
        setRecoveryId(previousBatch);
        try {
          const saved: LibraryBatchRequest = JSON.parse(localStorage.getItem(`connlab.projectLibrary.lastBatchRequest:${value.projects_root}`) ?? "null");
          if (saved?.batch_id === previousBatch && /^[a-f0-9]{32}$/.test(saved.batch_id) && typeof saved.plan_id === "string" && typeof saved.fingerprint === "string" && Array.isArray(saved.selected) && saved.selected.every(path => typeof path === "string") && Array.isArray(saved.keep_separate) && saved.keep_separate.every(path => typeof path === "string")) setSubmission(saved);
        } catch { /* A damaged local recovery hint cannot authorize a new submission. */ }
        const previous = await getLibraryBatch(previousBatch, controller.signal);
        if (!controller.signal.aborted && recoveryEpoch === interactionEpoch.current) { setBatch(previous); setSubmission(null); }
      }
    }).catch(cause => { if (!controller.signal.aborted && recoveryEpoch === interactionEpoch.current) setError((cause as Error).message); });
    return () => { live.current = false; controller.abort(); request.current?.abort(); };
  }, []);
  useEffect(() => {
    if (batch?.status !== "running") return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => { void getLibraryBatch(batch.batch_id, controller.signal).then(next => { if (!controller.signal.aborted) setBatch(next); }).catch(cause => { if (!controller.signal.aborted) setError((cause as Error).message); }); }, 750);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [batch]);
  function changeSources(value: string) {
    interactionEpoch.current += 1; setRecoveryId(""); setSubmission(null);
    request.current?.abort(); request.current = null;
    setSources(value); setAssignments({}); setScan(null); setPlan(null); setSelected([]); setSeparate([]); setBatch(null); setError(""); setConfirming(false); setPage(1);
  }
  async function choose() {
    interactionEpoch.current += 1;
    setBusy(true); setError("");
    try { const folder = await pickLibraryFolder(); if (live.current && folder) changeSources([...new Set([...sources.split(/\r?\n/).filter(Boolean), folder])].join("\n")); }
    catch (cause) { if (live.current) setError((cause as Error).message); }
    finally { if (live.current) setBusy(false); }
  }
  async function review(paths = sources.split(/\r?\n/).map(value => value.trim().replace(/^"|"$/g, "")).filter(Boolean)) {
    if (!paths.length || busy) return;
    interactionEpoch.current += 1;
    const controller = new AbortController(); request.current = controller;
    setBusy(true); setError(""); setPlan(null); setBatch(null); setSelected([]); setSeparate([]); setPage(1);
    try {
      const found = await scanLibrarySources(paths, controller.signal);
      if (!live.current || controller.signal.aborted) return;
      setScan(found);
      if (!found.items.length || found.truncated) return;
      if (found.items.some(row => row.kind === "file")) {
        const available = await listLibraryMembers("", "", controller.signal);
        if (live.current && !controller.signal.aborted) { setExistingMembers(available.items); setAssignments({}); }
        return;
      }
      const checked = await planLibraryIntake(found.items.map(row => row.source_path), controller.signal);
      if (!live.current || controller.signal.aborted) return;
      setPlan(checked); setSelected(checked.items.filter(row => row.status === "ready").map(row => row.source_path));
    } catch (cause) { if (live.current && !controller.signal.aborted) setError((cause as Error).message); }
    finally { if (live.current && request.current === controller) { request.current = null; setBusy(false); } }
  }
  async function reviewBoundary(paths: string[]) {
    if (!paths.length || busy || confirming || batch?.status === "running") return;
    interactionEpoch.current += 1;
    request.current?.abort();
    const controller = new AbortController(); request.current = controller;
    setSources(paths.join("\n")); setAssignments({}); setRecoveryId(""); setSubmission(null);
    setBusy(true); setError(""); setPlan(null); setBatch(null); setSelected([]); setSeparate([]); setFilter("all"); setPage(1);
    try {
      const checked = await planLibraryIntake(paths, controller.signal);
      if (!live.current || controller.signal.aborted) return;
      setPlan(checked); setSelected(checked.items.filter(row => row.status === "ready").map(row => row.source_path));
    } catch (cause) { if (live.current && !controller.signal.aborted) setError((cause as Error).message); }
    finally { if (live.current && request.current === controller) { request.current = null; setBusy(false); } }
  }
  async function reviewAssignments() {
    if (!scan || busy) return;
    const controller = new AbortController(); request.current = controller;
    setBusy(true); setError("");
    const choices: LibraryFileAssignment[] = scan.items.filter(row => row.kind === "file").map(row => {
      const choice = assignments[row.source_path];
      return choice.target === "new" ? { source_path: row.source_path, new_project_title: choice.title.trim() } : { source_path: row.source_path, target_member_id: choice.target };
    });
    try {
      const checked = await planLibraryIntake(scan.items.map(row => row.source_path), controller.signal, choices);
      if (live.current && !controller.signal.aborted) { setPlan(checked); setSelected(checked.items.filter(row => row.status === "ready").map(row => row.source_path)); }
    } catch (cause) { if (live.current && !controller.signal.aborted) setError((cause as Error).message); }
    finally { if (live.current && request.current === controller) { request.current = null; setBusy(false); } }
  }
  async function receive(resume = false, retrySubmission = false) {
    if (busy || (resume ? !batch : retrySubmission ? !submission : !plan) || !runtime) return;
    const currentEpoch = ++interactionEpoch.current;
    setBusy(true); setConfirming(false); setError("");
    try {
      let next: LibraryBatch;
      if (resume && batch) next = await resumeLibraryBatch(batch.batch_id);
      else {
        const intent: LibraryBatchRequest = retrySubmission ? submission! : { batch_id: crypto.randomUUID().replaceAll("-", ""), plan_id: plan!.plan_id, fingerprint: plan!.fingerprint, selected, keep_separate: separate };
        // Persist the already-confirmed identity before POST, including the first attempt.
        localStorage.setItem(`connlab.projectLibrary.lastBatch:${runtime.projects_root}`, intent.batch_id!);
        localStorage.setItem(`connlab.projectLibrary.lastBatchRequest:${runtime.projects_root}`, JSON.stringify(intent));
        setRecoveryId(intent.batch_id!); setSubmission(intent);
        next = await startLibraryBatch(intent);
      }
      if (live.current && currentEpoch === interactionEpoch.current) {
        setBatch(next); setSelected([]); setRecoveryId(next.batch_id); setSubmission(null);
        localStorage.setItem(`connlab.projectLibrary.lastBatch:${runtime.projects_root}`, next.batch_id);
        localStorage.removeItem(`connlab.projectLibrary.lastBatchRequest:${runtime.projects_root}`);
      }
    } catch (cause) { if (live.current && currentEpoch === interactionEpoch.current) setError((cause as Error).message); }
    finally { if (live.current && currentEpoch === interactionEpoch.current) setBusy(false); }
  }
  async function refreshBatch() {
    if ((!batch && !recoveryId) || busy) return;
    setBusy(true); setError("");
    try { const next = await getLibraryBatch(batch?.batch_id ?? recoveryId); if (live.current) setBatch(next); }
    catch (cause) { if (live.current) setError((cause as Error).message); }
    finally { if (live.current) setBusy(false); }
  }
  const locked = busy || confirming || batch?.status === "running";
  const boundaryRoots = (scan?.boundary_roots ?? scan?.items ?? []).filter(row => row.kind === "project");
  const visible = (plan?.items ?? []).filter(row => filter === "all" || row.status === filter);
  const pages = Math.max(1, Math.ceil(visible.length / 20));
  const currentPage = Math.min(page, pages);
  const back = <button type="button" className="ui-secondary-action" disabled={locked} onClick={onBack}>Back to Projects</button>;
  return <section className="project-library" aria-label="Import projects">
    {topBar ? createPortal(back, topBar) : <header className="library-heading"><h1>Import Projects</h1>{back}</header>}
    <section className="library-panel">
      <h2>1. Choose Sources</h2>
      {runtime && <p className="library-location">Receiving into: <span>{runtime.projects_root}</span></p>}
      <div className="library-actions"><button type="button" disabled={locked} onClick={() => void choose()}>Choose Folder</button></div>
      <label>Source paths<textarea value={sources} rows={3} disabled={locked} onChange={event => changeSources(event.target.value)} placeholder="One folder or file path per line" /></label>
      <div className="library-actions"><button type="button" className="primary-action" disabled={locked || !sources.trim() || !runtime} onClick={() => void review()}>Review Projects</button></div>
      {busy && !confirming && <p role="status">Checking or receiving projects…</p>}
      {error && <div><p role="alert">{error}</p>{recoveryId && !batch && <button type="button" disabled={busy} onClick={() => void refreshBatch()}>Recover Last Batch</button>}{submission && !batch && <button type="button" disabled={busy} onClick={() => void receive(false, true)}>Retry Batch Submission</button>}</div>}
      {scan?.truncated && !plan && <p role="alert">Incomplete results. Choose a smaller source folder before receiving projects.</p>}
      {scan && !plan && !scan.items.length && <p>No projects found. Choose a specific project folder or file.</p>}
      {scan?.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}
      {boundaryRoots.length > 0 && <details><summary>Check Project Boundaries</summary><p>These choices only update the preview. Nothing is copied until Confirm Add.</p>{boundaryRoots.map(row => <div key={row.source_path} role="group" aria-label={`Project boundary ${row.title}`}><strong>{row.title}</strong><p>Keep the complete project folder, including its Source Book. Use its subfolders only when each is a separate project.</p><div className="library-actions"><button type="button" disabled={locked} onClick={() => void reviewBoundary([row.source_path])}>Use This Folder</button><button type="button" disabled={locked || !row.child_folders.length} onClick={() => void reviewBoundary(row.child_folders)}>Use Subfolders as Projects</button></div></div>)}</details>}
    </section>
    {scan && !plan && !batch && scan.items.some(row => row.kind === "file") && <section className="library-panel" aria-label="Loose file assignments">
      <h2>Choose Where Files Belong</h2>
      <p>Add files to an existing project, or give a shared title to files that belong to a new project.</p>
      {scan.items.filter(row => row.kind === "file").map(row => <div key={row.source_path} className="library-editor"><strong>{row.title}</strong><label>Assign {row.title}<select disabled={locked} value={assignments[row.source_path]?.target ?? ""} onChange={event => setAssignments(values => ({ ...values, [row.source_path]: { target: event.target.value, title: values[row.source_path]?.title ?? "" } }))}><option value="">Choose a Project</option><option value="new">Create a Project to Organize</option>{existingMembers.filter(member => !member.is_history).map(member => <option key={member.member_id} value={member.member_id}>{member.ltr_number ? `${member.ltr_number} · ` : ""}{member.title}</option>)}</select></label>{assignments[row.source_path]?.target === "new" && <label>New project title for {row.title}<input disabled={locked} value={assignments[row.source_path].title} onChange={event => setAssignments(values => ({ ...values, [row.source_path]: { ...values[row.source_path], title: event.target.value } }))} /></label>}</div>)}
      <button type="button" className="primary-action" disabled={locked || scan.items.filter(row => row.kind === "file").some(row => !assignments[row.source_path]?.target || assignments[row.source_path]?.target === "new" && !assignments[row.source_path]?.title.trim())} onClick={() => void reviewAssignments()}>Review File Assignments</button>
    </section>}
    {plan && !batch && <section className="library-panel">
      <h2>2. Review Projects</h2><p>{plan.items.length} found; {selected.length} selected.</p>
      {plan.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}
      <div className="library-actions"><label>Show<select value={filter} disabled={locked} onChange={event => { setFilter(event.target.value); setPage(1); }}><option value="all">All ({plan.items.length})</option>{Object.entries(labels).map(([key, label]) => <option key={key} value={key}>{label} ({plan.items.filter(row => row.status === key).length})</option>)}</select></label><button type="button" disabled={locked} onClick={() => setSelected(plan.items.filter(row => row.status === "ready").map(row => row.source_path))}>Select Ready Projects</button><button type="button" disabled={locked} onClick={() => setSelected([])}>Clear Selection</button></div>
      <div className="library-table"><table aria-label="Projects to receive"><thead><tr><th>Select</th><th>Project</th><th>Result</th></tr></thead><tbody>{visible.slice((currentPage - 1) * 20, currentPage * 20).map(row => <tr key={row.source_path}><td><input type="checkbox" aria-label={`Select ${row.title}`} disabled={locked || row.status === "already_added" || row.status === "unavailable" || row.status === "conflict" && !separate.includes(row.source_path)} checked={selected.includes(row.source_path)} onChange={event => setSelected(values => event.target.checked ? [...values, row.source_path] : values.filter(value => value !== row.source_path))} /></td><td><strong>{row.ltr_number || "No LTR yet"}</strong><span>{row.title}</span><details><summary>Locations</summary><dl><dt>From</dt><dd>{row.source_path}</dd><dt>To</dt><dd>{row.target_path}</dd></dl></details></td><td><strong>{labels[row.status]}</strong>{row.warnings.map((note, i) => <p key={i}>{note}</p>)}{row.can_keep_separate && <label><input type="checkbox" aria-label={`Keep ${row.title} separate`} disabled={locked} checked={separate.includes(row.source_path)} onChange={event => { const checked = event.target.checked; setSeparate(values => checked ? [...values, row.source_path] : values.filter(value => value !== row.source_path)); setSelected(values => checked ? [...new Set([...values, row.source_path])] : values.filter(value => value !== row.source_path)); }} />Keep as a Separate Project</label>}</td></tr>)}</tbody></table></div>
      <div className="library-actions"><button type="button" disabled={locked || currentPage <= 1} onClick={() => setPage(currentPage - 1)}>Previous</button><span>Page {currentPage} of {pages}</span><button type="button" disabled={locked || currentPage >= pages} onClick={() => setPage(currentPage + 1)}>Next</button><button type="button" className="primary-action" disabled={locked || !selected.length} onClick={() => setConfirming(true)}>Add Selected</button></div>
    </section>}
    {confirming && <section className="library-panel" role="dialog" aria-modal="false" aria-labelledby="library-confirm-title"><h2 id="library-confirm-title">Confirm Add</h2><p>Copy {selected.length} selected projects into the library? Source files stay in place.</p><div className="library-actions"><button type="button" className="primary-action" autoFocus onClick={() => void receive()}>Confirm Add</button><button type="button" onClick={() => setConfirming(false)}>Cancel</button></div></section>}
    {batch && <section className="library-panel" aria-label="Receiving result"><h2>3. Receiving Result</h2><p role="status">{batch.counts.added} added; {batch.counts.already_added} already added; {batch.counts.review} need review; {batch.counts.failed} failed.</p>{batch.items.map(item => <div key={item.source_path} className="library-result"><span>{plan?.items.find(row => row.source_path === item.source_path)?.title ?? item.source_path}</span>{item.status !== "added" && <p>{item.message}</p>}{item.member_id && <button type="button" onClick={() => onOpenMember(item.member_id!)}>Open {plan?.items.find(row => row.source_path === item.source_path)?.title ?? "Project"}</button>}</div>)}<div className="library-actions">{batch.status === "running" && <button type="button" disabled={busy} onClick={() => void refreshBatch()}>Refresh Batch Status</button>}{batch.status === "interrupted" && <button type="button" disabled={busy} onClick={() => void receive(true)}>Resume Batch</button>}<button type="button" disabled={batch.status === "running"} onClick={() => onViewLibrary(batch.batch_id)}>View This Batch</button><button type="button" disabled={locked} onClick={() => { setBatch(null); setPlan(null); setScan(null); }}>Receive More Projects</button></div></section>}
    <details className="library-panel"><summary>More Import Options</summary>
      {onLegacyPreview && <button type="button" disabled={locked} title="Keep folders at their current locations using the existing read-only preview and registration flow." onClick={onLegacyPreview}>Link Existing Folders</button>}
      <PortableRestore onOpenMember={onOpenMember} disabled={locked} />
    </details>
  </section>;
}
