import { useEffect, useRef, useState } from "react";
import { inspectPortableProject, planPortableRestore, restorePortableProject, pickLibraryFolder, type PortableRestorePlan, type PortableResolution, type PortableRestoreResult } from "../../api/projectLibrary";

function coverageCategory(name: string): string {
  if (name.includes("fee")) return "Fees";
  if (name.includes("matrix") || name.startsWith("measurement_plan") || name.startsWith("contact_point")) return "Matrix";
  if (name.startsWith("result_dataset")) return "Test Results";
  if (name.includes("report") || name === "project_output_records") return "Reports";
  if (name.startsWith("intake_") || name === "file_assets" || name.includes("request_material") || name.startsWith("source_")) return "Source Materials";
  if (name.includes("schedule")) return "Schedule";
  if (name.startsWith("ltr_") || name.includes("lifecycle") || name.includes("registry")) return "Project History";
  if (name === "projects" || name.startsWith("project_") || name === "application_forms" || name === "sample_infos" || name.startsWith("precheck_")) return "Project Information";
  return "Other Retained Data";
}
export function PortableCoverage({ counts, fileCount, label = "Saved Snapshot Data" }: { counts: Record<string, number>; fileCount: number; label?: string }) {
  const records = Object.entries(counts).filter(([, count]) => count > 0);
  const categories = records.reduce<Record<string, number>>((result, [name, count]) => {
    const category = coverageCategory(name); result[category] = (result[category] ?? 0) + count; return result;
  }, {});
  return <details open><summary>{label} · {fileCount} files</summary><dl className="library-facts">{Object.entries(categories).map(([name, count]) => <div key={name}><dt>{name}</dt><dd>{count} records</dd></div>)}</dl>{!records.length && <p>No structured project records available.</p>}<details><summary>Snapshot Diagnostics</summary><dl className="library-facts">{records.map(([name, count]) => <div key={name}><dt>{name}</dt><dd>{count}</dd></div>)}</dl></details></details>;
}
const resolutionLabels: Record<PortableResolution, string> = { replace_working_copy: "Replace Working Copy", keep_as_history: "Keep as History" };
function RestoreProtection({ plan }: { plan: PortableRestorePlan }) {
  return <div className="library-review">
    <p>Source snapshot: {plan.created_at ? new Date(plan.created_at).toLocaleString() : "Not available"}</p>
    {plan.source_signature && <p>Source data version: <code title={plan.source_signature}>{plan.source_signature.slice(0, 12)}</code></p>}
    {plan.target_revision !== null && <p>Current library revision: {plan.target_revision}</p>}
    <details><summary>Restore Location</summary><p>{plan.target_path}</p></details>
    {plan.backup_path && <><p>Recovery point location:</p><p>{plan.backup_path}</p></>}
    {plan.resolution === "replace_working_copy" && <p>A complete recovery point of the current working copy will be saved before replacement.</p>}
    {plan.resolution === "keep_as_history" && <p>The current LTR owner stays unchanged. This complete copy will be retained as history for browsing.</p>}
  </div>;
}
export function PortableRestore({ onOpenMember, disabled = false }: { onOpenMember: (id: string) => void; disabled?: boolean }) {
  const [folder, setFolder] = useState("");
  const [inspection, setInspection] = useState<PortableRestorePlan | null>(null);
  const [resolution, setResolution] = useState<PortableResolution | "">("");
  const [confirmation, setConfirmation] = useState<PortableRestorePlan | null>(null);
  const [restored, setRestored] = useState<PortableRestoreResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const live = useRef(true);
  useEffect(() => { live.current = true; return () => { live.current = false; }; }, []);
  function changeFolder(value: string) { setFolder(value); setInspection(null); setResolution(""); setConfirmation(null); setRestored(null); setError(""); }
  async function run(action: () => Promise<void>) {
    if (busy) return;
    setBusy(true); setError("");
    try { await action(); } catch (cause) { if (live.current) { setError((cause as Error).message); setConfirmation(null); } }
    finally { if (live.current) setBusy(false); }
  }
  async function reviewRestore() {
    const selected = resolution || undefined;
    const next = await planPortableRestore(folder.trim(), selected);
    if (!live.current) return;
    setInspection(next);
    if (next.blockers.length || !["ready", "already_added"].includes(next.status)) return;
    if ((next.resolution || undefined) !== selected) {
      setResolution(""); setError("The available restore choices changed. Review this project again."); return;
    }
    setConfirmation(next);
  }
  const locked = disabled || busy || Boolean(confirmation);
  const options = inspection && !inspection.blockers.length ? (inspection.resolution_options ?? []).filter(option => option in resolutionLabels) : [];
  const canReview = inspection && !inspection.blockers.length && (["ready", "already_added"].includes(inspection.status) || (inspection.status === "conflict" && Boolean(resolution) && options.includes(resolution as PortableResolution)));
  return <section className="library-panel library-restore" aria-label="Restore Project Data"><h3>Restore Project Data</h3>
    <p>Restore test data saved by ConnLab. Choose the complete project folder brought from the other computer, including its saved snapshot.</p>
    <label>Portable project folder<input value={folder} disabled={locked} onChange={event => changeFolder(event.target.value)} /></label>
    <div className="library-actions"><button type="button" disabled={locked} onClick={() => void run(async () => { const next = await pickLibraryFolder(); if (live.current && next) changeFolder(next); })}>Choose Portable Folder</button><button type="button" disabled={locked || !folder.trim()} onClick={() => void run(async () => { const next = await inspectPortableProject(folder.trim()); if (live.current) { setInspection(next); setResolution(""); setRestored(null); } })}>Inspect Project</button></div>
    {busy && <p role="status">Checking portable project…</p>}{error && <p role="alert">{error} Review the restore plan again before continuing.</p>}
    {inspection && !confirmation && <div className="library-review"><h3>{inspection.title}</h3><p>{inspection.ltr_number || "No LTR yet"}</p><RestoreProtection plan={inspection} /><PortableCoverage counts={inspection.record_counts} fileCount={inspection.file_count} />
      {inspection.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}{inspection.blockers.map((note, i) => <p key={i} role="alert">{note}</p>)}
      {inspection.status === "conflict" && <p role="alert">{options.length ? "Choose how to handle this copy. No project data is changed until you confirm the reviewed plan." : "This project conflicts with an existing record. Resolve the conflicting copies before restoring."}</p>}
      {options.length > 0 && <fieldset className="library-resolution" disabled={locked}><legend>Conflict Handling</legend>{options.map(option => <label key={option}><input type="radio" name="portable-resolution" checked={resolution === option} onChange={() => setResolution(option)} />{resolutionLabels[option]}</label>)}<p>Each copy stays complete. Individual fields are not merged.</p></fieldset>}
      <button type="button" className="primary-action" disabled={locked || !canReview} onClick={() => void run(reviewRestore)}>Review Restore</button>
    </div>}
    {confirmation && <div role="dialog" aria-modal="false" aria-labelledby="portable-confirm-title" className="library-review"><h3 id="portable-confirm-title">Confirm Restore</h3><p>{confirmation.resolution ? resolutionLabels[confirmation.resolution] : "Restore Project"}: {confirmation.title}</p><RestoreProtection plan={confirmation} /><PortableCoverage counts={confirmation.record_counts} fileCount={confirmation.file_count} />{confirmation.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}<div className="library-actions"><button type="button" className="primary-action" autoFocus disabled={busy} onClick={() => void run(async () => { const next = await restorePortableProject({ plan_id: confirmation.plan_id, fingerprint: confirmation.fingerprint, ...(confirmation.resolution ? { resolution: confirmation.resolution } : {}) }); if (live.current) { setRestored(next); setConfirmation(null); setInspection(null); setResolution(""); } })}>Confirm Restore</button><button type="button" disabled={busy} onClick={() => setConfirmation(null)}>Cancel Restore</button></div></div>}
    {restored && <div role="status"><p>{restored.status === "history_kept" ? "Historical copy saved. The current LTR owner is unchanged." : "Project data recovered. Review any missing information before continuing tests."}</p>{restored.warnings.map((note, i) => <p key={i}>{note}</p>)}<div className="library-actions"><button type="button" onClick={() => onOpenMember(restored.member.member_id)}>{restored.status === "history_kept" ? "Open History Project" : "Open Recovered Project"}</button>{restored.backup_member_id && <button type="button" onClick={() => onOpenMember(restored.backup_member_id!)}>Open Recovery Point</button>}</div></div>}
  </section>;
}
