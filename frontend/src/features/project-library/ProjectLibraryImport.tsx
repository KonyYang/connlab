import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useTopBarActionsRoot } from "../../components/layout/TopBarActionsContext";
import { getLibraryMember, planLibraryIntake } from "../../api/projectLibrary";
import { getLibraryRuntime, scanLibrarySources, startLibraryBatch, getLibraryBatch, resumeLibraryBatch, pickLibraryFolder, planPortableRestore, type LibraryRuntime, type LibraryScan, type LibraryIntakePlan, type LibraryBatch, type LibraryBatchRequest, type PortableRestorePlan, type PortableResolution } from "../../api/projectLibrary";
import { ProjectImportResults, type ImportResultDetails } from "./ProjectImportResults";
import { ProjectImportReviewList } from "./ProjectImportReviewList";
import { combinedImportResults, intakeReviewKey, readyImportPaths, receiveSavedProjects, reviewImportCandidates, selectedImportProblem, type SnapshotImportOutcome } from "./projectImportReview";
import "./project-library.css";

type Props = {
  onBack: () => void;
  onViewLibrary: (batchId?: string) => void;
  onOpenMember: (id: string, batchId?: string) => void;
  onOpenProject?: (id: string) => void;
  onOpenSettings?: () => void;
  backLabel?: string;
  onLegacyPreview?: () => void;
  presentation?: "page" | "dialog";
  startOnMount?: boolean;
  onDismiss?: () => void;
};

export function ProjectLibraryImport({ onBack, onViewLibrary, onOpenMember, onOpenProject, onOpenSettings, backLabel = "Back to Projects", presentation = "page", startOnMount = false, onDismiss }: Props) {
  const [runtime, setRuntime] = useState<LibraryRuntime | null>(null);
  const [sources, setSources] = useState("");
  const sourcePaths = [...new Set(sources.split(/\r?\n/).map(value => value.trim().replace(/^"|"$/g, "")).filter(Boolean))];
  const [scan, setScan] = useState<LibraryScan | null>(null);
  const [plan, setPlan] = useState<LibraryIntakePlan | null>(null);
  const [snapshots, setSnapshots] = useState<PortableRestorePlan[]>([]);
  const [snapshotResults, setSnapshotResults] = useState<SnapshotImportOutcome[]>([]);
  const [ltrNumber, setLtrNumber] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [separate, setSeparate] = useState<string[]>([]);
  const [filesOnly, setFilesOnly] = useState<string[]>([]);
  const openedOutcome = useRef("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [busyMessage, setBusyMessage] = useState("Checking selected folders…");
  const [manualOpen, setManualOpen] = useState(false);
  const [setupAttempt, setSetupAttempt] = useState(0);
  const [setupReady, setSetupReady] = useState(false);
  const [batch, setBatch] = useState<LibraryBatch | null>(null);
  const [recoveryId, setRecoveryId] = useState("");
  const [recoveredCompletedId, setRecoveredCompletedId] = useState("");
  const [submission, setSubmission] = useState<LibraryBatchRequest | null>(null);
  const startedIntake = useRef("");
  const openedExisting = useRef("");
  const startedPicker = useRef(false);
  const interactionEpoch = useRef(0);
  const live = useRef(true);
  const request = useRef<AbortController | null>(null);
  const topBar = useTopBarActionsRoot();
  useEffect(() => {
    live.current = true;
    setSetupReady(false);
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
    }).catch(cause => { if (!controller.signal.aborted && recoveryEpoch === interactionEpoch.current) setError(setupLoaded ? (cause as Error).message : "Could not load the import save location. Retry, or reopen ConnLab if this continues."); })
      .finally(() => { if (!controller.signal.aborted && recoveryEpoch === interactionEpoch.current) setSetupReady(true); });
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
    startedIntake.current = "";
    openedExisting.current = "";
    request.current?.abort(); request.current = null;
    setSources(value); setLtrNumber(""); setScan(null); setPlan(null); setSelected([]); setSeparate([]); setFilesOnly([]); setBatch(null); setError("");
    setSnapshots([]); setSnapshotResults([]);
    setBusy(false);
  }
  async function choose() {
    const hadSelection = sourcePaths.length > 0 || Boolean(plan) || snapshots.length > 0;
    const epoch = ++interactionEpoch.current;
    setManualOpen(false);
    setBusy(true); setBusyMessage("Choose a project folder in the system window…"); setError("");
    try {
      const folder = await pickLibraryFolder();
      if (!live.current || epoch !== interactionEpoch.current) return;
      if (folder && (!sourcePaths.includes(folder) || sourcePaths.length > 1)) {
        const next = [folder]; changeSources(folder); await review(next, "");
      } else {
        setBusy(false);
        if (!folder && startOnMount && !hadSelection) (onDismiss ?? onBack)();
      }
    } catch (cause) { if (live.current && epoch === interactionEpoch.current) { setBusy(false); setManualOpen(true); setError(`Could not choose a folder. Enter its path below and check it again. ${(cause as Error).message}`); } }
  }
  async function review(paths = sourcePaths, providedLtr = ltrNumber) {
    if (!paths.length || !runtime?.configured) return;
    if (paths.length !== 1) { setError("Choose one complete project folder at a time."); return; }
    interactionEpoch.current += 1;
    const controller = new AbortController(); request.current = controller;
    setBusy(true); setBusyMessage("Checking selected folders…"); setError(""); setPlan(null); setSnapshots([]); setSnapshotResults([]); setBatch(null); setSelected([]); setSeparate([]);
    try {
      const found = await scanLibrarySources(paths, controller.signal, true);
      if (!live.current || controller.signal.aborted) return;
      setScan(found);
      if (!found.items.length || found.truncated || found.selection_issue && found.selection_issue !== "needs_ltr") return;
      if (found.items.length !== 1 || found.items[0].kind !== "project") throw new Error("Choose one complete project folder at a time.");
      if (found.selection_issue === "needs_ltr" && !providedLtr.trim()) return;
      const assignments = found.selection_issue === "needs_ltr" ? [{ source_path: paths[0], ltr_number: providedLtr.trim().toUpperCase() }] : undefined;
      const checked = await reviewImportCandidates(found.items, controller.signal, assignments);
      if (!live.current || controller.signal.aborted) return;
      acceptReview(checked);
    } catch (cause) { if (live.current && !controller.signal.aborted) setError((cause as Error).message); }
    finally { if (live.current && request.current === controller) { request.current = null; setBusy(false); } }
  }
  function acceptReview(checked: Awaited<ReturnType<typeof reviewImportCandidates>>) {
    if ((checked.plan?.items.length ?? 0) + checked.snapshots.length !== 1) throw new Error("The check did not return one complete project. Choose the project folder again.");
    setManualOpen(false);
    setPlan(checked.plan); setSnapshots(checked.snapshots);
    setSelected(readyImportPaths(checked.plan, checked.snapshots));
    const root = checked.projectsRoot;
    if (root) setRuntime(value => value ? { ...value, projects_root: root } : value);
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
  const automaticIntakeKey = (() => {
    if (!onOpenProject) return "";
    const ordinary = plan?.items.length === 1 ? plan.items[0] : null;
    if (ordinary && selected.includes(ordinary.source_path)
        && (ordinary.status === "ready" || ordinary.status === "conflict" && ordinary.can_keep_separate && separate.includes(ordinary.source_path))) {
      return `ordinary:${plan!.plan_id}:${plan!.fingerprint}:${ordinary.source_path}`;
    }
    const saved = !plan && snapshots.length === 1 ? snapshots[0] : null;
    if (saved && selected.includes(saved.source_path) && saved.status === "ready" && !saved.blockers.length) {
      return `saved:${saved.plan_id}:${saved.fingerprint}:${saved.source_path}`;
    }
    return "";
  })();
  const automaticExistingMemberId = (() => {
    if (!onOpenProject || plan?.items.length !== 1 || snapshots.length) return "";
    const item = plan.items[0];
    return item.status === "already_added" && item.existing_member_id ? item.existing_member_id : "";
  })();
  const hasReview = Boolean(plan || snapshots.length);
  const showSourceSummary = !manualOpen && (hasReview || presentation === "dialog" && sourcePaths.length > 0);
  useEffect(() => {
    if (!startOnMount || startedPicker.current || !setupReady || !runtime?.configured) return;
    if (batch && batch.status !== "completed") return;
    startedPicker.current = true;
    void choose();
  }, [startOnMount, setupReady, runtime?.configured, batch?.status]);
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
  useEffect(() => {
    if (!automaticIntakeKey || locked || displayBatch || selectionProblem || startedIntake.current === automaticIntakeKey) return;
    startedIntake.current = automaticIntakeKey;
    void receive();
  }, [automaticIntakeKey, locked, displayBatch?.batch_id, selectionProblem]);
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
    if (!automaticExistingMemberId || locked || displayBatch || openedExisting.current === automaticExistingMemberId) return;
    openedExisting.current = automaticExistingMemberId;
    void openImportedMember(automaticExistingMemberId);
  }, [automaticExistingMemberId, locked, displayBatch?.batch_id]);
  useEffect(() => {
    if (!freshSuccess || !onOpenProject || !displayBatch || displayBatch.items.length !== 1 || (plan?.items.length ?? 0) + snapshots.length !== 1) return;
    const item = displayBatch.items[0], details = detailsBySource[item.source_path];
    if (!item.member_id || item.status !== "added" || details?.kind === "history") return;
    const key = `${displayBatch.batch_id}:${item.member_id}`;
    if (openedOutcome.current === key) return;
    openedOutcome.current = key;
    void openImportedMember(item.member_id);
  }, [freshSuccess, displayBatch?.batch_id]);
  const back = <button type="button" className="ui-secondary-action" disabled={locked} onClick={onBack}>{backLabel}</button>;
  const dismiss = <button type="button" className="ui-secondary-action" disabled={locked} onClick={onDismiss ?? onBack}>Cancel</button>;
  const results = displayBatch && <ProjectImportResults batch={displayBatch} titlesBySource={Object.fromEntries([...(plan?.items ?? []), ...snapshots, ...snapshotResults].map(item => [item.source_path, item.title]))}
    detailsBySource={detailsBySource}
    busy={busy} onOpenMember={openImportedMember} onViewLibrary={() => onViewLibrary()} onRefresh={() => void refreshBatch()}
    onResume={() => void receive(true)} onReceiveMore={() => changeSources("")} heading={displayBatch.batch_id === recoveredCompletedId ? "Import Result" : undefined} />;
  const needsDialog = Boolean(
    error
    || runtime && !runtime.configured
    || manualOpen
    || scan?.selection_issue
    || (plan || snapshots.length > 0) && !automaticIntakeKey && !automaticExistingMemberId
    || displayBatch && (
      displayBatch.status === "interrupted"
      || displayBatch.counts.failed > 0
      || displayBatch.counts.review > 0
      || displayBatch.status === "running" && !startedIntake.current
    )
    || snapshotResults.some(row => row.status === "failed")
  );
  const content = <section className="project-library" aria-label="Import projects">
    {presentation === "page" ? (topBar ? createPortal(back, topBar) : <header className="library-heading"><h1>Import Projects</h1>{back}</header>) : <header className="library-heading"><h2>Import Project</h2>{dismiss}</header>}
    {!runtime && !error && <p role="status">Loading import setup…</p>}
    {error && !runtime?.configured && <div><p role="alert">{error}</p>{!runtime && <button type="button" onClick={() => { setError(""); setSetupAttempt(value => value + 1); }}>Retry Setup</button>}</div>}
    {runtime && !runtime.configured && <div className="library-setup-problem"><p role="alert">{runtime.location_error && <>{runtime.location_error} </>}Set a valid Project default save location in Settings before importing projects.</p>{onOpenSettings && <button type="button" onClick={onOpenSettings}>Open Settings</button>}</div>}
    {runtime?.configured && !freshSuccess && <section className={`library-panel${showSourceSummary ? " library-source-panel" : ""}`}>
      {showSourceSummary ? <div className="library-source-summary" aria-label="Selected folder">
        <span title={sourcePaths[0]}>Source: {sourcePaths[0]?.split(/[\\/]/).pop()}</span>
        <button type="button" className="library-text-action" disabled={locked} onClick={() => void choose()}>Change Folder</button>
      </div> : presentation === "page" || !startOnMount ? <>
        <h2>Choose a project</h2>
        <p>Choose the project's LTR folder. ConnLab will receive it and open the project.</p>
        <div className="library-actions"><button type="button" className="primary-action" disabled={locked} title="Choose one complete project folder. Files are copied after the checks pass." onClick={() => void choose()}>Choose Project Folder</button></div>
      </> : null}
      {manualOpen && <div className="library-editor">
        <label>Source path<input value={sources} disabled={locked} onChange={event => changeSources(event.target.value)} placeholder="Full path to one project folder" /></label>
        <button type="button" disabled={locked || !sourcePaths.length} onClick={() => void review()}>Check Folder</button>
      </div>}
      {scan?.selection_issue === "needs_ltr" && !hasReview && <div className="library-editor">
        <p>No LTR was found in this folder or its project information. Enter the project's existing LTR to check it.</p>
        <label>LTR number<input value={ltrNumber} disabled={locked} onChange={event => setLtrNumber(event.target.value)} placeholder="DL-2026-09-032" /></label>
        <button type="button" disabled={locked || !/^DL-\d{4}-\d{2}-\d{3}(?:[A-Z][A-Z0-9]*)?$/i.test(ltrNumber.trim())} onClick={() => void review()}>Check Project</button>
      </div>}
      {busy && <p role="status">{busyMessage}</p>}
      {error && <div><p role="alert">{error}</p>{recoveryId && !batch && <button type="button" disabled={busy} onClick={() => void refreshBatch()}>Recover Last Batch</button>}{submission && !batch && <button type="button" disabled={busy} onClick={() => void receive(false, true)}>Retry Batch Submission</button>}{!submission && !batch && sourcePaths.length > 0 && <button type="button" disabled={locked} onClick={() => void review()}>Check Again</button>}</div>}
      {scan?.truncated && !plan && <p role="alert">Incomplete results. Choose a smaller source folder before importing projects.</p>}
      {scan && !plan && !scan.items.length && !scan.selection_issue && <p>Choose one complete project folder to check.</p>}
      {scan?.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}
    </section>}
    {(plan || snapshots.length > 0) && !displayBatch && !automaticIntakeKey && !automaticExistingMemberId && <section className="library-panel">
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
        <button type="button" className="primary-action" disabled={locked || !selected.length || Boolean(selectionProblem)} onClick={() => void receive()}>Confirm Import</button>
      </section>}
    </section>}
    {displayBatch && (displayBatch.batch_id === recoveredCompletedId
      ? <details><summary>Last Import ({displayBatch.counts.added} added; {displayBatch.counts.already_added} already added)</summary>{results}</details>
      : results)}
    {snapshotResults.some(row => row.status === "failed") && <button type="button" disabled={locked} onClick={() => { const failed = snapshotResults.filter(row => row.status === "failed").map(row => row.source_path); changeSources(failed.join("\n")); void review(failed); }}>Check Failed Projects Again</button>}
  </section>;
  return presentation === "dialog"
    ? needsDialog
      ? <div className="project-import-overlay"><div className="project-import-dialog" role="dialog" aria-modal="true" aria-label="Import project">{content}</div></div>
      : null
    : content;
}
