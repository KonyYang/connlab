import { useEffect, useRef, useState } from "react";
import { inspectPortableProject, planPortableRestore, restorePortableProject, pickLibraryFolder, type PortableRestorePlan, type LibraryMember } from "../../api/projectLibrary";

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
export function PortableRestore({ onOpenMember, disabled = false }: { onOpenMember: (id: string) => void; disabled?: boolean }) {
  const [folder, setFolder] = useState("");
  const [inspection, setInspection] = useState<PortableRestorePlan | null>(null);
  const [confirmation, setConfirmation] = useState<PortableRestorePlan | null>(null);
  const [restored, setRestored] = useState<LibraryMember | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const live = useRef(true);
  useEffect(() => { live.current = true; return () => { live.current = false; }; }, []);
  function changeFolder(value: string) { setFolder(value); setInspection(null); setConfirmation(null); setRestored(null); setWarnings([]); setError(""); }
  async function run(action: () => Promise<void>) {
    if (busy) return;
    setBusy(true); setError("");
    try { await action(); } catch (cause) { if (live.current) { setError((cause as Error).message); setConfirmation(null); } }
    finally { if (live.current) setBusy(false); }
  }
  const locked = disabled || busy || Boolean(confirmation);
  return <details className="library-panel library-restore"><summary>Take Over a Portable Project</summary>
    <p>Choose the complete project folder brought from the other computer.</p>
    <label>Portable project folder<input value={folder} disabled={locked} onChange={event => changeFolder(event.target.value)} /></label>
    <div className="library-actions"><button type="button" disabled={locked} onClick={() => void run(async () => { const next = await pickLibraryFolder(); if (live.current && next) changeFolder(next); })}>Choose Portable Folder</button><button type="button" disabled={locked || !folder.trim()} onClick={() => void run(async () => { const next = await inspectPortableProject(folder.trim()); if (live.current) { setInspection(next); setRestored(null); } })}>Inspect Project</button></div>
    {busy && <p role="status">Checking portable project…</p>}{error && <p role="alert">{error}</p>}
    {inspection && <div className="library-review"><h3>{inspection.title}</h3><p>{inspection.ltr_number || "No LTR yet"}</p><p>Prepared: {inspection.created_at ? new Date(inspection.created_at).toLocaleString() : "Not available"}</p><PortableCoverage counts={inspection.record_counts} fileCount={inspection.file_count} /><details><summary>Restore Location</summary><p>{inspection.target_path}</p></details>{inspection.warnings.map((note, i) => <p key={i} role="status">{note}</p>)}{inspection.blockers.map((note, i) => <p key={i} role="alert">{note}</p>)}{inspection.status === "conflict" && !inspection.blockers.length && <p role="alert">This project conflicts with an existing record. Resolve the conflicting copies before restoring.</p>}<button type="button" className="primary-action" disabled={locked || inspection.blockers.length > 0 || !["ready", "already_added"].includes(inspection.status)} onClick={() => void run(async () => { const next = await planPortableRestore(folder.trim()); if (live.current) { setInspection(next); if (!next.blockers.length && ["ready", "already_added"].includes(next.status)) setConfirmation(next); } })}>Review Restore</button></div>}
    {confirmation && <div role="dialog" aria-modal="false" aria-labelledby="portable-confirm-title" className="library-review"><h3 id="portable-confirm-title">Confirm Restore</h3><p>Restore {confirmation.title} and its carried project data into this library?</p><div className="library-actions"><button type="button" className="primary-action" autoFocus disabled={busy} onClick={() => void run(async () => { const next = await restorePortableProject({ plan_id: confirmation.plan_id, fingerprint: confirmation.fingerprint }); if (live.current) { setRestored(next.member); setWarnings(next.warnings); setConfirmation(null); setInspection(null); } })}>Confirm Restore</button><button type="button" disabled={busy} onClick={() => setConfirmation(null)}>Cancel Restore</button></div></div>}
    {restored && <div role="status"><p>Project data recovered. Review any missing information before continuing tests.</p>{warnings.map((note, i) => <p key={i}>{note}</p>)}<button type="button" onClick={() => onOpenMember(restored.member_id)}>Open Recovered Project</button></div>}
  </details>;
}
