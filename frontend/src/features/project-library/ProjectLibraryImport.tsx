import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import { getLibraryMember, planLibraryIntake } from "../../api/projectLibrary";
import { getLibraryRuntime, listLibraryMembers, scanLibrarySources, startLibraryBatch, getLibraryBatch, resumeLibraryBatch, pickLibraryFolder, planPortableRestore, type LibraryRuntime, type LibraryMember, type LibraryFileAssignment, type LibraryScan, type LibraryIntakePlan, type LibraryBatch, type LibraryBatchRequest, type PortableRestorePlan, type PortableResolution } from "../../api/projectLibrary";
import { ProjectImportResults, type ImportResultDetails } from "./ProjectImportResults";
import { ProjectImportReviewList } from "./ProjectImportReviewList";
import { combinedImportResults, intakeReviewKey, readyImportPaths, receiveSavedProjects, reviewImportCandidates, selectedImportProblem, type SnapshotImportOutcome } from "./projectImportReview";
import "./project-library.css";

type Props = { onBack: () => void; onViewLibrary: (batchId?: string) => void; onOpenMember: (id: string, batchId?: string) => void; onOpenProject?: (id: string) => void; onOpenSettings?: () => void; backLabel?: string; onLegacyPreview?: () => void };

export function ProjectLibraryImport({ onBack, onViewLibrary, onOpenMember, onOpenProject, onOpenSettings, onLegacyPreview, backLabel = "Back to Projects" }: Props) {
  const [runtime, setRuntime] = useState<LibraryRuntime | null>(null);
  const [sources, setSources] = useState("");
  const sourcePaths = [...new Set(sources.split(/\r?\n/).map(value => value.trim().replace(/^"|"$/g, "")).filter(Boolean))];
  const [scan, setScan] = useState<LibraryScan | null>(null);
  const [plan, setPlan] = useState<LibraryIntakePlan | null>(null);
  const [snapshots, setSnapshots] = useState<PortableRestorePlan[]>([]);
  const [snapshotResults, setSnapshotResults] = useState<SnapshotImportOutcome[]>([]);
  const [assignments, setAssignments] = useState<Record<string, { target: string; title: string }>>({});
  const [existingMembers, setExistingMembers] = useState<LibraryMember[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [separate, setSeparate] = useState<string[]>([]);
  const [filesOnly, setFilesOnly] = useState<string[]>([]);
  const openedOutcome = useRef("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [busyMessage, setBusyMessage] = useState("Checking selected folders…");
  const [manualOpen, setManualOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const [setupAttempt, setSetupAttempt] = useState(0);
  const [batch, setBatch] = useState<LibraryBatch | null>(null);
  const [recoveryId, setRecoveryId] = useState("");
  const [recoveredCompletedId, setRecoveredCompletedId] = useState("");
  const [submission, setSubmission] = useState<LibraryBatchRequest | null>(null);
  const interactionEpoch = useRef(0);
  const live = useRef(true);
  const request = useRef<AbortController | null>(null);
  const topBar = useTopBarActionsRoot();
  useEffect(() => {
    live.current = true;
    const controller = new AbortController();
    const recoveryEpoch = interactionEpoch.current;
    let setupLoaded = false;
    void getLibraryRuntime(controller.signal).then(async value => {
      if (controller.signal.aborted) return;
      setupLoaded = true;
      setRuntime(value);
      const previousBatch = localStorage.getItem(`connlab.projectLibrary.lastBatch:${value.projects_root}`);
      if (previousBatch && recoveryEpoch === interactionEpoch.current) {
        setRecoveryId(previousBatch);
        try {
          const saved: LibraryBatchRequest = JSON.parse(localStorage.getItem(`connlab.projectLibrary.lastBatchRequest:${value.projects_root}`) ?? "null");
          if (saved?.batch_id === previousBatch && /^[a-f0-9]{32}$/.test(saved.batch_id) && typeof saved.plan_id === "string" && typeof saved.fingerprint === "string" && Array.isArray(saved.selected) && saved.selected.every(path => typeof path === "string") && Array.isArray(saved.keep_separate) && saved.keep_separate.every(path => typeof path === "string")) setSubmission(saved);
        } catch { /* A damaged local recovery hint cannot authorize a new submission. */ }
        const previous = await getLibraryBatch(previousBatch, controller.signal);
        if (!controller.signal.aborted && recoveryEpoch === interactionEpoch.current) {
          setBatch(previous); setSubmission(null);
          if (previous.status === "completed" && previous.counts.review === 0 && previous.counts.failed === 0) setRecoveredCompletedId(previous.batch_id);
        }
      }
    }).catch(cause => { if (!controller.signal.aborted && recoveryEpoch === interactionEpoch.current) setError(setupLoaded ? (cause as Error).message : "Could not load the import save location. Retry, or reopen ConnLab if this continues."); });
    return () => { live.current = false; controller.abort(); request.current?.abort(); };
  }, [setupAttempt]);
  useEffect(() => {
    if (batch?.status !== "running") return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => { void getLibraryBatch(batch.batch_id, controller.signal).then(next => { if (!controller.signal.aborted) setBatch(next); }).catch(cause => { if (!controller.signal.aborted) setError((cause as Error).message); }); }, 750);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [batch]);
  function changeSources(value: string) {
    interactionEpoch.current += 1; setRecoveryId(""); setSubmission(null); setRecoveredCompletedId("");
    request.current?.abort(); request.current = null;
    setSources(value); setAssignments({}); setScan(null); setPlan(null); setSelected([]); setSeparate([]); setFilesOnly([]); setBatch(null); setError("");
    setSnapshots([]); setSnapshotResults([]);
    setBusy(false);
  }
  async function choose(replace = false) {
    const epoch = ++interactionEpoch.current;
    setManualOpen(false);
    setBusy(true); setBusyMessage("Choose a project folder in the system window…"); setError("");
    try {
      const folder = await pickLibraryFolder();
      if (!live.current || epoch !== interactionEpoch.current) return;
      if (folder && (!sourcePaths.includes(folder) || replace && sourcePaths.length > 1)) {
        const next = replace ? [folder] : [...sourcePaths, folder]; changeSources(next.join("\n")); await review(next);
      } else setBusy(false);
    } catch (cause) { if (live.current && epoch === interactionEpoch.current) { setBusy(false); setManualOpen(true); setError(`Could not choose a folder. Enter its path below and check it again. ${(cause as Error).message}`); } }
  }
  async function review(paths = sourcePaths) {
    if (!paths.length || !runtime?.configured) return;
    interactionEpoch.current += 1;
    const controller = new AbortController(); request.current = controller;
    setBusy(true); setBusyMessage("Checking selected folders…"); setError(""); setPlan(null); setSnapshots([]); setSnapshotResults([]); setBatch(null); setSelected([]); setSeparate([]);
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
      const checked = await reviewImportCandidates(found.items, controller.signal);
      if (!live.current || controller.signal.aborted) return;
      acceptReview(checked);
    } catch (cause) { if (live.current && !controller.signal.aborted) setError((cause as Error).message); }
    finally { if (live.current && request.current === controller) { request.current = null; setBusy(false); } }
  }
  function acceptReview(checked: Awaited<ReturnType<typeof reviewImportCandidates>>) {
    setManualOpen(false);
    setMoreOpen(false);
    setPlan(checked.plan); setSnapshots(checked.snapshots);
    setSelected(readyImportPaths(checked.plan, checked.snapshots));
    const root = checked.projectsRoot;
    if (root) setRuntime(value => value ? { ...value, projects_root: root } : value);
  }
  async function reviewBoundary(paths: string[]) {
    if (!paths.length || busy || batch?.status === "running") return;
    interactionEpoch.current += 1;
    request.current?.abort();
    const controller = new AbortController(); request.current = controller;
    setSources(paths.join("\n")); setAssignments({}); setRecoveryId(""); setSubmission(null);
    setBusy(true); setBusyMessage("Checking the selected project folders…"); setError(""); setPlan(null); setSnapshots([]); setSnapshotResults([]); setBatch(null); setSelected([]); setSeparate([]);
    try {
      const found = await scanLibrarySources(paths, controller.signal);
      if (!live.current || controller.signal.aborted) return;
      const exact = paths.map(path => [...(found.boundary_roots ?? []), ...found.items].find(row => row.source_path === path));
      if (exact.some(row => !row)) throw new Error("Some selected project folders could not be checked. Choose them again.");
      const checked = await reviewImportCandidates(exact.filter(row => row !== undefined), controller.signal);
      if (!live.current || controller.signal.aborted) return;
      setScan(found); acceptReview(checked);
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
      const checked = await reviewImportCandidates(scan.items, controller.signal, choices);
      if (live.current && !controller.signal.aborted) {
        acceptReview(checked);
      }
    } catch (cause) { if (live.current && !controller.signal.aborted) setError((cause as Error).message); }
    finally { if (live.current && request.current === controller) { request.current = null; setBusy(false); } }
  }
  async function importFilesOnly(path: string) {
    if (locked || !plan) return;
    const controller = new AbortController(); request.current = controller;
    setBusy(true); setError(""); setBusyMessage("Checking files-only import…");
    const nextChoices = [...new Set([...filesOnly, path])];
    try {
      const choices = plan.items.map(row => ({ source_path: row.source_path,
        ...(row.target_member_id ? { target_member_id: row.target_member_id } : {}),
        ...(row.new_project_title ? { new_project_title: row.new_project_title } : {}),
        ...(nextChoices.includes(row.source_path) ? { files_only: true } : {}) }));
      const next = await planLibraryIntake(plan.items.map(row => row.source_path), controller.signal, choices);
      if (!live.current || controller.signal.aborted) return;
      if (next.projects_root && next.projects_root !== runtime?.projects_root) {
        changeSources(sources); setRuntime(value => value ? { ...value, projects_root: next.projects_root! } : value);
        setError("The save location changed. Check the selected folders again before importing."); return;
      }
      const unchanged = new Set(next.items.filter(row => plan.items.some(previous => previous.source_path === row.source_path && intakeReviewKey(previous) === intakeReviewKey(row))).map(row => row.source_path));
      const retainedSeparate = separate.filter(value => unchanged.has(value) && next.items.some(row => row.source_path === value && row.status === "conflict" && row.can_keep_separate));
      setPlan(next); setFilesOnly(nextChoices); setSeparate(retainedSeparate);
      setSelected(values => [...new Set([...values.filter(value => unchanged.has(value) && next.items.some(row => row.source_path === value && (row.status === "ready" || retainedSeparate.includes(value))) || snapshots.some(row => row.source_path === value)), ...next.items.filter(row => row.source_path === path && row.status === "ready").map(row => row.source_path)])]);
    } catch (cause) { if (live.current && !controller.signal.aborted) setError((cause as Error).message); }
    finally { if (live.current && request.current === controller) { request.current = null; setBusy(false); } }
  }
  async function resolveSnapshot(path: string, resolution?: PortableResolution) {
    if (busy) return;
    const controller = new AbortController(); request.current = controller;
    setBusy(true); setBusyMessage("Checking the selected conflict handling…"); setError("");
    try {
      const next = await planPortableRestore(path, resolution, controller.signal);
      if (!live.current || controller.signal.aborted) return;
      if (next.projects_root && next.projects_root !== runtime?.projects_root) {
        changeSources(sources); setRuntime(value => value ? { ...value, projects_root: next.projects_root! } : value);
        setError("The save location changed. Check the selected folders again before importing."); return;
      }
      if ((next.resolution ?? undefined) !== resolution) throw new Error("The available choices changed. Check this project again before importing.");
      setSnapshots(values => values.map(row => row.source_path === path ? next : row));
      setSelected(values => [...values.filter(value => value !== path), ...(next.status === "ready" && !next.blockers.length ? [path] : [])]);
    } catch (cause) { if (live.current && !controller.signal.aborted) setError((cause as Error).message); }
    finally { if (live.current && request.current === controller) { request.current = null; setBusy(false); } }
  }
  async function receive(resume = false, retrySubmission = false) {
    if (busy || (resume ? !batch : retrySubmission ? !submission : (!plan && !snapshots.length)) || !runtime) return;
    if (!resume && !retrySubmission && (!selected.length || selectedImportProblem(plan, snapshots, selected))) return;
    const currentEpoch = ++interactionEpoch.current;
    setBusy(true); setBusyMessage("Importing selected projects…"); setError(""); setRecoveredCompletedId("");
    try {
      let next: LibraryBatch | null = null;
      const ordinary = selected.filter(path => plan?.items.some(row => row.source_path === path));
      if (resume && batch) next = await resumeLibraryBatch(batch.batch_id);
      else if (retrySubmission || ordinary.length) {
        const intent: LibraryBatchRequest = retrySubmission ? submission! : { batch_id: crypto.randomUUID().replaceAll("-", ""), plan_id: plan!.plan_id, fingerprint: plan!.fingerprint, selected: ordinary, keep_separate: separate.filter(path => ordinary.includes(path)) };
        // Persist the already-confirmed identity before POST, including the first attempt.
        localStorage.setItem(`connlab.projectLibrary.lastBatch:${runtime.projects_root}`, intent.batch_id!);
        localStorage.setItem(`connlab.projectLibrary.lastBatchRequest:${runtime.projects_root}`, JSON.stringify(intent));
        setRecoveryId(intent.batch_id!); setSubmission(intent);
        next = await startLibraryBatch(intent);
      }
      const outcomes = resume ? [] : await receiveSavedProjects(snapshots.filter(row => selected.includes(row.source_path) && row.status === "ready" && !row.blockers.length), () => live.current && currentEpoch === interactionEpoch.current);
      if (live.current && currentEpoch === interactionEpoch.current) {
        setBatch(next); setSelected([]); setSubmission(null);
        if (!resume) setSnapshotResults(outcomes);
        if (next) {
          setRecoveryId(next.batch_id);
          localStorage.setItem(`connlab.projectLibrary.lastBatch:${runtime.projects_root}`, next.batch_id);
          localStorage.removeItem(`connlab.projectLibrary.lastBatchRequest:${runtime.projects_root}`);
        }
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
  const locked = busy || batch?.status === "running";
  const displayBatch = combinedImportResults(batch, snapshotResults);
  const freshSuccess = displayBatch?.status === "completed" && displayBatch.batch_id !== recoveredCompletedId && displayBatch.counts.failed === 0 && displayBatch.counts.review === 0 && !error && !busy;
  const selectionProblem = selectedImportProblem(plan, snapshots, selected);
  const hasReview = Boolean(plan || snapshots.length);
  const boundaryRoots = (scan?.boundary_roots ?? scan?.items ?? []).filter(row => row.kind === "project" && row.child_folders.length > 0);
  const detailsBySource: Record<string, ImportResultDetails> = Object.fromEntries((plan?.items ?? []).map(row => [row.source_path, { ltrNumber: row.ltr_number, kind: row.target_member_id ? "existing_files" : "files", warnings: [...new Set(row.warnings)] }]));
  for (const row of snapshots) detailsBySource[row.source_path] = { ltrNumber: row.ltr_number, warnings: [...new Set(row.warnings)] };
  for (const row of snapshotResults) {
    if (!row.result) continue;
    const { member, status, warnings } = row.result;
    detailsBySource[row.source_path] = {
      ltrNumber: member.ltr_number,
      kind: status === "history_kept" || member.is_history ? "history" : member.can_continue && member.project_id ? "restored" : undefined,
      warnings: [...new Set([...warnings, ...member.warnings])],
    };
  }
  async function openImportedMember(memberId: string) {
    const restored = snapshotResults.find(row => row.member_id === memberId)?.result;
    if (restored) {
      if (onOpenProject && restored.status !== "history_kept" && !restored.member.is_history && restored.member.can_continue && restored.member.project_id) onOpenProject(restored.member.project_id);
      else onOpenMember(memberId);
      return;
    }
    if (!onOpenProject) { onOpenMember(memberId); return; }
    // Resolve the completed ordinary intake's identity, never infer a project from its LTR.
    const epoch = interactionEpoch.current;
    setBusy(true); setError(""); setBusyMessage("Opening project…");
    try {
      const member = await getLibraryMember(memberId);
      if (!live.current || epoch !== interactionEpoch.current) return;
      if (member.project_id && member.can_continue && !member.is_history) onOpenProject(member.project_id);
      else onOpenMember(memberId);
    } catch (cause) {
      if (live.current && epoch === interactionEpoch.current) setError(cause instanceof Error ? cause.message : "Could not open the imported project. Try again.");
    } finally {
      if (live.current && epoch === interactionEpoch.current) setBusy(false);
    }
  }
  useEffect(() => {
    if (!freshSuccess || !onOpenProject || !displayBatch || displayBatch.items.length !== 1 || (plan?.items.length ?? 0) + snapshots.length !== 1) return;
    const item = displayBatch.items[0], details = detailsBySource[item.source_path];
    const restored = snapshotResults.some(row => row.member_id === item.member_id);
    if (!item.member_id || item.status !== "added" || restored && details?.warnings.length || details?.kind === "history") return;
    const key = `${displayBatch.batch_id}:${item.member_id}`;
    if (openedOutcome.current === key) return;
    openedOutcome.current = key;
    void openImportedMember(item.member_id);
  }, [freshSuccess, displayBatch?.batch_id]);
  const back = <button type="button" className="ui-secondary-action" disabled={locked} onClick={onBack}>{backLabel}</button>;
  const results = displayBatch && <ProjectImportResults batch={displayBatch} titlesBySource={Object.fromEntries([...(plan?.items ?? []), ...snapshots, ...snapshotResults].map(item => [item.source_path, item.title]))}
    detailsBySource={detailsBySource}
    busy={busy} onOpenMember={openImportedMember} onViewLibrary={() => onViewLibrary()} onRefresh={() => void refreshBatch()}
    onResume={() => void receive(true)} onReceiveMore={() => changeSources("")} heading={displayBatch.batch_id === recoveredCompletedId ? "Import Result" : undefined} />;
  return <section className="project-library" aria-label="Import projects">
    {topBar ? createPortal(back, topBar) : <header className="library-heading"><h1>Import Projects</h1>{back}</header>}
    {!runtime && !error && <p role="status">Loading import setup…</p>}
    {error && !runtime?.configured && <div><p role="alert">{error}</p>{!runtime && <button type="button" onClick={() => { setError(""); setSetupAttempt(value => value + 1); }}>Retry Setup</button>}</div>}
    {runtime && !runtime.configured && <p role="alert">{runtime.location_error && <>{runtime.location_error} </>}Set a valid Project default save location in Settings before importing projects.</p>}
    {runtime?.configured && !freshSuccess && <section className={`library-panel${hasReview && !manualOpen ? " library-source-panel" : ""}`}>
      {hasReview && !manualOpen ? <div className="library-source-summary" aria-label="Selected folders">
        <span title={sourcePaths.join("\n")}>Source: {sourcePaths.map(path => path.split(/[\\/]/).pop()).join(", ")}</span>
        <button type="button" className="library-text-action" disabled={locked} onClick={() => void choose(true)}>Change Folder</button>
      </div> : <>
      <h2>Choose projects</h2>
      <p>Select a project folder or a folder containing several projects. We will check them before you confirm. Original files stay in place.</p>
      <div className="library-actions"><button type="button" className="primary-action" disabled={locked} title="Choose existing project folders. Selection only checks the files; copying requires your final confirmation." onClick={() => void choose()}>Choose Project Folders</button>{sourcePaths.length > 1 && <button type="button" disabled={locked} title="Clear this selection. Original folders and files stay unchanged." onClick={() => changeSources("")}>Clear All</button>}</div>
      {sourcePaths.length > 0 && <p>{sourcePaths.length} {sourcePaths.length === 1 ? "location" : "locations"} selected</p>}
      {sourcePaths.length > 0 && !manualOpen && <>
        <ul className="library-source-list" aria-label="Selected sources">{sourcePaths.map((path, index) => <li key={path}><span>{path}</span><button type="button" aria-label={`Remove ${path} from selection`} title="Cancel this selection. Original folders and files stay unchanged." disabled={locked} onClick={() => { const next = sourcePaths.filter((_, position) => position !== index); changeSources(next.join("\n")); if (next.length) void review(next); }}>×</button></li>)}</ul>
      </>}
      <details open={manualOpen} onToggle={event => setManualOpen(event.currentTarget.open)}><summary>Enter Paths Manually</summary>
        <label>Source paths<textarea value={sources} rows={3} disabled={locked} onChange={event => changeSources(event.target.value)} placeholder="One folder or file path per line" /></label><button type="button" disabled={locked || !sourcePaths.length} onClick={() => void review()}>Check Paths</button>
      </details>
      </>}
      {(hasReview || boundaryRoots.length > 0 || onLegacyPreview) && <details open={moreOpen} onToggle={event => setMoreOpen(event.currentTarget.open)}><summary>More Options</summary>
        {hasReview && <p className="library-save-summary">Save location: {runtime.projects_root}{onOpenSettings && <> · <button type="button" className="library-text-action" disabled={locked} onClick={onOpenSettings}>Change</button></>}</p>}
        {hasReview && <div className="library-actions"><button type="button" disabled={locked} onClick={() => void choose()}>Add Folder</button><button type="button" disabled={locked} onClick={() => setManualOpen(true)}>Enter Paths Manually</button></div>}
        {hasReview && !manualOpen && <><p>{sourcePaths.length} {sourcePaths.length === 1 ? "location" : "locations"} selected</p><ul className="library-source-list" aria-label="Selected sources">{sourcePaths.map(path => <li key={path}><span>{path}</span><button type="button" disabled={locked} aria-label={`Remove ${path} from selection`} onClick={() => { const next = sourcePaths.filter(value => value !== path); changeSources(next.join("\n")); if (next.length) void review(next); }}>×</button></li>)}</ul>{sourcePaths.length > 1 && <button type="button" disabled={locked} onClick={() => changeSources("")}>Clear All</button>}</>}
        {boundaryRoots.length > 0 && <div><h3>Adjust Folder Selection</h3><p>Keep each project together. Change this only if the detected projects are incorrect.</p>{boundaryRoots.map(row => <div key={row.source_path} role="group" aria-label={`Project boundary ${row.title}`}><strong>{row.title}</strong><p>Import this complete folder, or choose its subfolders only when each is a separate project.</p><div className="library-actions"><button type="button" disabled={locked} onClick={() => void reviewBoundary([row.source_path])}>Import as One Project</button><button type="button" disabled={locked || !row.child_folders.length} onClick={() => void reviewBoundary(row.child_folders)}>Find Projects Inside</button></div></div>)}</div>}
        {onLegacyPreview && <button type="button" disabled={locked} title="Keep folders at their current locations and register links without copying files." onClick={onLegacyPreview}>Link Folders Without Copying</button>}
      </details>}
      {busy && <p role="status">{busyMessage}</p>}
      {!hasReview && !displayBatch && <p>{sourcePaths.length ? "Check the selected folders before importing." : "Choose a project folder to begin."}</p>}
      {error && <div><p role="alert">{error}</p>{recoveryId && !batch && <button type="button" disabled={busy} onClick={() => void refreshBatch()}>Recover Last Batch</button>}{submission && !batch && <button type="button" disabled={busy} onClick={() => void receive(false, true)}>Retry Batch Submission</button>}{!submission && !batch && sourcePaths.length > 0 && <button type="button" disabled={locked} onClick={() => void review()}>Check Again</button>}</div>}
      {scan?.truncated && !plan && <p role="alert">Incomplete results. Choose a smaller source folder before importing projects.</p>}
      {scan && !plan && !scan.items.length && <p>No projects found. Choose a specific project folder or file.</p>}
      {scan?.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}
      {!hasReview && <p className="library-save-summary" title={runtime.projects_root}>Save to: {runtime.projects_root.split(/[\\/]/).pop() || runtime.projects_root}{onOpenSettings && <> · <button type="button" className="library-text-action" disabled={locked} onClick={onOpenSettings} title="Change Project default save location in Settings">Change</button></>}</p>}
    </section>}
    {scan && !plan && !batch && scan.items.some(row => row.kind === "file") && <section className="library-panel" aria-label="Loose file assignments">
      <h2>Choose Where Files Belong</h2>
      <p>Add files to an existing project, or give a shared title to files that belong to a new project.</p>
      {scan.items.filter(row => row.kind === "file").map(row => <div key={row.source_path} className="library-editor"><strong>{row.title}</strong><label>Assign {row.title}<select disabled={locked} value={assignments[row.source_path]?.target ?? ""} onChange={event => setAssignments(values => ({ ...values, [row.source_path]: { target: event.target.value, title: values[row.source_path]?.title ?? "" } }))}><option value="">Choose a Project</option><option value="new">Create a Project to Organize</option>{existingMembers.filter(member => !member.is_history).map(member => <option key={member.member_id} value={member.member_id}>{member.ltr_number ? `${member.ltr_number} · ` : ""}{member.title}</option>)}</select></label>{assignments[row.source_path]?.target === "new" && <label>New project title for {row.title}<input disabled={locked} value={assignments[row.source_path].title} onChange={event => setAssignments(values => ({ ...values, [row.source_path]: { ...values[row.source_path], title: event.target.value } }))} /></label>}</div>)}
      <button type="button" className="primary-action" disabled={locked || scan.items.filter(row => row.kind === "file").some(row => !assignments[row.source_path]?.target || assignments[row.source_path]?.target === "new" && !assignments[row.source_path]?.title.trim())} onClick={() => void reviewAssignments()}>Review File Assignments</button>
    </section>}
    {(plan || snapshots.length > 0) && !displayBatch && <section className="library-panel">
      <ProjectImportReviewList plan={plan} snapshots={snapshots} selected={selected} separate={separate} disabled={locked}
        onToggle={(path, checked) => setSelected(values => checked ? [...new Set([...values, path])] : values.filter(value => value !== path))}
        onKeepSeparate={(path, keep) => {
          setSeparate(values => keep ? [...new Set([...values, path])] : values.filter(value => value !== path));
          setSelected(values => keep ? [...new Set([...values, path])] : values.filter(value => value !== path));
        }}
        onResolveSnapshot={(path, resolution) => void resolveSnapshot(path, resolution)} onOpenMember={openImportedMember} onFilesOnly={path => void importFilesOnly(path)}
        onSelectReady={() => setSelected([...new Set([...readyImportPaths(plan, snapshots), ...separate])])} onClear={() => setSelected([])} />
      {selectionProblem && <p role="alert">{selectionProblem}</p>}
      {(selected.length > 0 || (plan?.items.length ?? 0) + snapshots.length > 1) && <section className="library-import-confirm" aria-label="Confirm import selection">
        <p>Will copy to <strong title={runtime?.projects_root}>{runtime?.projects_root.split(/[\\/]/).filter(Boolean).pop() || runtime?.projects_root}</strong>. Original files stay in place.</p>
        <button type="button" className="primary-action" disabled={locked || !selected.length || Boolean(selectionProblem)} onClick={() => void receive()}>{(plan?.items.length ?? 0) + snapshots.length === 1 ? "Import Project" : `Import Projects (${selected.length})`}</button>
      </section>}
    </section>}
    {displayBatch && (displayBatch.batch_id === recoveredCompletedId
      ? <details><summary>Last Import ({displayBatch.counts.added} added; {displayBatch.counts.already_added} already added)</summary>{results}</details>
      : results)}
    {snapshotResults.some(row => row.status === "failed") && <button type="button" disabled={locked} onClick={() => { const failed = snapshotResults.filter(row => row.status === "failed").map(row => row.source_path); changeSources(failed.join("\n")); void review(failed); }}>Check Failed Projects Again</button>}
  </section>;
}
