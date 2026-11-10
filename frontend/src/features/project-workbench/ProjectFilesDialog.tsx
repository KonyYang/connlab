import { useEffect, useRef, useState } from "react";
import type { ProjectFileAction, ProjectFileKey } from "../../api/client";
import { ProjectManagementDialog } from "../projects-registry/ProjectRegistryManagementDialog";
import { useProjectFiles } from "./useProjectFiles";
import "./ProjectFilesDialog.css";

export function ProjectFilesDialog({projectId, readonly = false, onClose}: {projectId: string; readonly?: boolean; onClose: () => void}) {
  const model = useProjectFiles(projectId);
  const {preview, operation, loading, busy, running} = model;
  const [actions, setActions] = useState<Partial<Record<ProjectFileKey, ProjectFileAction>>>({});
  const [confirmReplacement, setConfirmReplacement] = useState(false);
  const closeButton = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    setActions(Object.fromEntries((preview?.items ?? []).map(item => [item.key,
      item.status === "ready" && item.default_action === "generate_missing" && item.source_token ? "generate_missing" : "skip"])));
    setConfirmReplacement(false);
  }, [preview]);
  const recovering = Boolean(operation && operation.status !== "completed" && !running);
  const locked = loading || busy || running || recovering || readonly || preview?.status !== "ready";
  useEffect(() => {
    const close = closeButton.current;
    const dialog = close?.closest('[role="dialog"]');
    const focused = document.activeElement;
    // Disabling the active control can send native focus to the document body.
    // Keep Escape and Tab inside this modal without moving a still-valid focus.
    if (close && dialog && (!dialog.contains(focused) || focused?.matches(":disabled"))) close.focus();
  }, [locked, loading, busy, running, recovering, preview, confirmReplacement]);
  const selections = (preview?.items ?? []).map(item => ({key: item.key, source_token: item.source_token, action: actions[item.key] ?? "skip" as ProjectFileAction}));
  const replacements = selections.filter(item => item.action === "replace_with_backup");
  const selected = selections.filter(item => item.action !== "skip");
  const counts = {generated: 0, replaced: 0, skipped: 0, needs_input: 0, failed: 0};
  operation?.items.forEach(item => {
    if (item.status === "failed") counts.failed++;
    else if (item.status === "needs_input") counts.needs_input++;
    else if (item.status === "completed" && item.outcome === "generated") counts.generated++;
    else if (item.status === "completed" && item.outcome === "replaced") counts.replaced++;
    else if (item.status === "skipped") counts.skipped++;
    else if (operation.status === "completed") counts.needs_input++;
  });
  const summary = operation?.summary ?? counts;
  const warnings = [...(preview?.warnings ?? []), ...(preview?.items.flatMap(item => item.warnings) ?? []), ...(operation?.warnings ?? [])];
  function change(key: ProjectFileKey, action: ProjectFileAction) {
    setActions(previous => ({...previous, [key]: action})); setConfirmReplacement(false);
  }
  return <ProjectManagementDialog title="Generate project files" onCancel={onClose} className="project-files-dialog">
    <p className="project-management-help">Select files to generate in the associated project folder. Existing files are skipped unless you choose replacement with a backup.</p>
    {loading ? <p role="status">Checking files…</p> : null}
    {model.error ? <p role="alert">{model.error}</p> : null}
    {readonly ? <p role="alert">This project is read-only. File generation is unavailable.</p> : null}
    {preview?.blockers.map((text, i) => <p role="alert" key={i}>{safeMessage(text)}</p>)}
    {operation ? <section className="project-files-progress" aria-label="File generation progress" aria-live="polite">
      <strong>{running ? "Generating files…" : recovering ? "Saved operation needs recovery" : operation.outcome === "partial" ? "Batch completed with issues" : "Batch completed"}</strong>
      <p>{summary.generated} generated · {summary.replaced} replaced · {summary.skipped} skipped · {summary.needs_input} need input · {summary.failed} failed</p>
      {operation.message ? <p>{safeMessage(operation.message)}</p> : null}
      <ul>{operation.items.map(item => <li key={item.key}><strong>{item.label}</strong>: {operationStatus(item.status, item.outcome)}{item.message ? ` — ${safeMessage(item.message)}` : ""}</li>)}</ul>
      {recovering ? <button type="button" className="secondary-action" disabled={busy || readonly || !operation.can_resume || operation.status !== "interrupted"} onClick={() => void model.resume()}>Resume saved operation</button> : null}
      {running ? <p>You can close this dialog. Generation continues in the background.</p> : null}
    </section> : null}
    {preview ? <div className="project-files-list" aria-label="Project files">
      {preview.items.map(item => {
        const action = actions[item.key] ?? "skip";
        const unavailable = locked || item.status === "blocked" || !item.source_token;
        const location = relativeLocation(item.target_path);
        return <section className="project-files-row" key={item.key}>
          <label className="project-files-choice"><input type="checkbox" aria-label={item.label} checked={action !== "skip"} disabled={unavailable}
            onChange={event => change(item.key, event.target.checked ? item.status === "exists" ? "replace_with_backup" : "generate_missing" : "skip")} />
            <span><strong>{item.label}</strong>{location ? <small>{location}</small> : null}</span></label>
          <div className="project-files-state"><span>{item.status === "ready" ? "Missing · ready" : item.status === "exists" ? "Exists · skip by default" : "Needs input"}</span>
            {item.message ? <p>{safeMessage(item.message)}</p> : null}
            {item.status === "exists" ? <label>Existing file action<select aria-label={`${item.label} existing file action`} disabled={unavailable} value={action} onChange={event => change(item.key, event.target.value as ProjectFileAction)}>
              <option value="skip">Skip existing file</option><option value="replace_with_backup">Back up and replace</option>
            </select></label> : null}
          </div>
        </section>;
      })}
    </div> : null}
    {confirmReplacement ? <section className="project-files-replacement" aria-label="Confirm replacements">
      <strong>Back up and replace {replacements.length} existing file{replacements.length === 1 ? "" : "s"}?</strong>
      <ul>{preview?.items.filter(item => replacements.some(selectedItem => selectedItem.key === item.key)).map(item => <li key={item.key}>{item.label} — {relativeLocation(item.target_path)}</li>)}</ul>
      <p>Each original is saved to History before its replacement is published. Other files remain unchanged.</p>
      <button type="button" disabled={locked} onClick={() => setConfirmReplacement(false)}>Back to selection</button>
    </section> : null}
    {operation || warnings.length ? <details><summary>Technical details and warnings</summary>
      {operation ? <p>Operation reference: {operation.operation_id}</p> : null}
      <ul>{warnings.map((text, i) => <li key={i}>{safeMessage(text)}</li>)}
        {operation?.items.filter(item => relativeLocation(item.backup_path ?? null)).map(item => <li key={`backup-${item.key}`}>{item.label} backup: {relativeLocation(item.backup_path ?? null)}</li>)}
      </ul>
    </details> : null}
    <div className="project-management-dialog-actions">
      <button ref={closeButton} type="button" className="secondary-action" onClick={onClose}>Close</button>
      <button type="button" className="secondary-action" disabled={loading || busy || running} onClick={() => void model.refresh()}>Refresh files</button>
      <button type="button" className="primary-action" disabled={locked || !selected.length} onClick={() => {
        if (replacements.length && !confirmReplacement) {setConfirmReplacement(true); return;}
        setConfirmReplacement(false); void model.submit(selections);
      }}>{confirmReplacement ? "Confirm backup and generate" : "Generate selected files"}</button>
    </div>
  </ProjectManagementDialog>;
}
function relativeLocation(value: string | null) {
  if (!value || /^[a-z]:|^[/\\]/i.test(value) || value.split(/[/\\]/).includes("..")) return null;
  return value;
}
function safeMessage(value: string) {
  // Keep diagnostic identifiers, native stacks and local paths out of the operator guidance.
  return value.replace(/(?:[a-z]:[\\/]|\\\\)[^\n]*|Traceback[\s\S]*|\[(?:Windows error|Office HRESULT|Stage:|Diagnostic ID:)[\s\S]*/gi, "").trim() || "Review file conditions and try again.";
}
function operationStatus(status: string, outcome: string | null) {
  return status === "published" ? "Output saved; registration pending" : status === "needs_input" ? "Needs input" : outcome === "generated" ? "Generated" : outcome === "replaced" ? "Replaced with backup" : status === "failed" ? "Failed" : status === "skipped" ? "Skipped" : status === "generating" ? "Generating" : status === "completed" ? "Completed" : "Pending";
}
