import { useEffect, useId, useRef, useState, type ReactElement, type ReactNode } from "react";
import { createPortal } from "react-dom";
import type { ProjectRegistryAction, ProjectRegistryEntry, ProjectRegistryPreview } from "../../api/projectRegistryManagement";
import "./ProjectRegistryManagementDialog.css";

export function ProjectRegistryManagementDialog({action, preview, loading, busy, error, stale,
  onCancel, onRefresh, onTrash, onRestore}: {
  action: ProjectRegistryAction; preview: ProjectRegistryPreview | null; loading: boolean; busy: boolean;
  error: string | null; stale: boolean; onCancel: () => void; onRefresh: () => void;
  onTrash: (reason: string) => void | Promise<void>;
  onRestore: (destination: "active" | "history", replaceConflicts: boolean) => void | Promise<void>;
}): ReactElement {
  const [reason, setReason] = useState("Created by mistake");
  const [note, setNote] = useState("");
  const [noteExpanded, setNoteExpanded] = useState(false);
  const noteInput = useRef<HTMLTextAreaElement>(null);
  useEffect(() => { if (noteExpanded) noteInput.current?.focus(); }, [noteExpanded]);
  const disabled = busy || loading || stale || !preview || Boolean(preview.blockers.length);
  const conflicts = preview?.conflicts ?? [];
  if (action === "trash") {
    // This fixed API reassurance is already covered by the concise retention message.
    // Keep any other server warning visible rather than treating it as boilerplate.
    const warnings = preview?.warnings.filter((warning) => warning !== "Existing external files and LTR associations are retained.") ?? [];
    return <ProjectManagementDialog title="Delete project" className="project-delete-dialog" busy={busy} onCancel={onCancel}>
      <div className="project-delete-body">
        {loading && <p role="status">Loading management preview…</p>}
        {preview && <>
          <div className="project-delete-identity">
            <strong>{preview.project.display_project_id}</strong>
            <span>{preview.project.sample_description || "Sample not recorded"}</span>
            <span>{preview.project.test_item || "Test item not recorded"}</span>
          </div>
          <p className="project-delete-help">You can restore this project from Recycle. Files and LTR records stay unchanged.</p>
          {warnings.length > 0 && <ul className="project-delete-warnings">{warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>}
          {preview.blockers.length > 0 && <div className="project-delete-error" role="alert"><ul>{preview.blockers.map((blocker) => <li key={blocker}>{blocker}</li>)}</ul></div>}
          <label className="project-delete-reason"><span>Deletion reason</span>
            <select data-dialog-initial-focus value={reason} disabled={busy} onChange={(event) => setReason(event.target.value)}>
              <option value="Created by mistake">Created by mistake</option>
              <option value="Duplicate project">Duplicate project</option><option value="Other">Other</option>
            </select>
          </label>
          {noteExpanded ? <label className="project-delete-note"><span>Additional note (optional)</span>
            <textarea ref={noteInput} rows={2} value={note} disabled={busy} onChange={(event) => setNote(event.target.value)} />
          </label> : <button className="project-delete-add-note" type="button" disabled={busy} onClick={() => setNoteExpanded(true)}>Add note</button>}
        </>}
        {error && <p className="project-delete-error" role="alert">{error}</p>}
        {(stale || error || Boolean(preview?.blockers.length)) && <button className="secondary-action ui-secondary-action" type="button" disabled={busy || loading} onClick={onRefresh}>Refresh preview</button>}
      </div>
      <div className="project-management-dialog-actions project-delete-actions">
        <button className="secondary-action ui-secondary-action" type="button" disabled={busy} onClick={onCancel}>Cancel</button>
        <button className="primary-action ui-primary-action" type="button" disabled={disabled || !reason} onClick={() => void onTrash(note.trim() ? `${reason}: ${note.trim()}` : reason)}>{busy ? "Moving…" : "Move to recycle bin"}</button>
      </div>
    </ProjectManagementDialog>;
  }
  return <ProjectManagementDialog title="Restore project" busy={busy} onCancel={onCancel}>
    {loading && <p role="status">Loading management preview…</p>}
    {preview && <>
      <ProjectRecordIdentity project={preview.project} />
      <p>Restore keeps this record's original lifecycle and all its data. It does not overwrite another project's records.</p>
      <p className="project-management-help">Public-drive files, original materials and LTR workbook records stay unchanged. LTR ownership is not transferred.</p>
      {preview.retained_data.length > 0 && <details><summary>Retained project records</summary><ul>{preview.retained_data.map((item) => <li key={item}>{item}</li>)}</ul></details>}
      {preview.warnings.length > 0 && <ul className="project-management-warnings">{preview.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>}
      {preview.blockers.length > 0 && <div role="alert"><strong>Resolve before continuing</strong><ul>{preview.blockers.map((blocker) => <li key={blocker}>{blocker}</li>)}</ul></div>}
      {conflicts.length > 0 ? <section aria-label="Conflicting current projects" className="project-management-conflicts">
        <strong>{conflicts.length} current {conflicts.length === 1 ? "project has" : "projects have"} the same identifier</strong>
        <p>Review every record below. Restoring as current moves these conflicting records into Recycle as retained records, with their data intact. You can also keep this project as a retained record in Recycle instead.</p>
        {conflicts.map((project) => <ProjectRecordIdentity key={project.project_id} project={project} />)}
      </section> : <p className="project-management-help">No current project conflicts were found in this preview.</p>}
    </>}
    {error && <p role="alert">{error}</p>}
    {(stale || error || Boolean(preview?.blockers.length)) && <button className="secondary-action ui-secondary-action" type="button" disabled={busy || loading} onClick={onRefresh}>Refresh preview</button>}
    <div className="project-management-dialog-actions">
      <button className="primary-action ui-primary-action" type="button" disabled={disabled} onClick={() => void onRestore("active", conflicts.length > 0)}>
        {conflicts.length > 0 ? "Restore and retain conflicts" : "Restore to projects"}
      </button>
      {conflicts.length > 0 && <button className="secondary-action ui-secondary-action" type="button" disabled={disabled} onClick={() => void onRestore("history", false)}>Keep as retained record</button>}
      <button className="secondary-action ui-secondary-action" type="button" disabled={busy} onClick={onCancel}>Cancel</button>
    </div>
  </ProjectManagementDialog>;
}

export function ProjectRecordIdentity({project}: {project: ProjectRegistryEntry}): ReactElement {
  return <div className="project-management-record">
    <strong>{project.display_project_id}</strong>
    <span>{project.sample_description || "Sample not recorded"}</span>
    <span>{project.test_item || "Test item not recorded"} · {project.requestor || "Requestor not recorded"}</span>
    <small>Created {project.created_on || "date not recorded"} · {project.lifecycle_state === "closed" ? `Closed${project.close_reason_label ? `: ${project.close_reason_label}` : ""}` : project.lifecycle_state === "stopped" ? "Stopped" : "Active"}</small>
    <small title={project.project_id}>Record {project.project_id.slice(0, 12)}</small>
  </div>;
}

/** Shared project management confirmation: focus, keyboard and scroll ownership. */
export function ProjectManagementDialog({ title, children, busy = false, onCancel, className = "" }: {
  title: string; children: ReactNode; busy?: boolean; onCancel: () => void; className?: string;
}): ReactElement {
  const titleId = useId();
  const container = useRef<HTMLDivElement>(null);
  const onCancelRef = useRef(onCancel);
  const busyRef = useRef(busy);
  onCancelRef.current = onCancel;
  busyRef.current = busy;
  useEffect(() => {
    const returnFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const root = container.current!;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const siblings = Array.from(document.body.children).filter((element) => element !== root.parentElement);
    const previousInert = siblings.map((element) => [element, element.hasAttribute("inert")] as const);
    siblings.forEach((element) => element.setAttribute("inert", ""));
    const focusable = () => Array.from(root.querySelectorAll<HTMLElement>(
      'button:not(:disabled), select:not(:disabled), input:not(:disabled), textarea:not(:disabled), summary, a[href], [tabindex="0"]'
    )).filter((element) => !element.closest("[hidden]") && !element.closest("details:not([open]) > :not(summary)"));
    (root.querySelector<HTMLElement>("[data-dialog-initial-focus]") ?? focusable()[0] ?? root).focus();
    function keydown(event: KeyboardEvent): void {
      if (event.key === "Escape") {
        event.preventDefault();
        if (!busyRef.current) onCancelRef.current();
      }
      if (event.key === "Tab") {
        const items = focusable();
        const first = items[0];
        const last = items[items.length - 1];
        if (!first) {event.preventDefault(); root.focus();}
        else if (event.shiftKey && (document.activeElement === first || document.activeElement === root)) {
          event.preventDefault(); last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault(); first.focus();
        }
      }
    }
    root.addEventListener("keydown", keydown);
    return () => {
      root.removeEventListener("keydown", keydown);
      document.body.style.overflow = previousOverflow;
      previousInert.forEach(([element, wasInert]) => { if (!wasInert) element.removeAttribute("inert"); });
      if (returnFocus?.isConnected) returnFocus.focus();
    };
  }, []);
  return createPortal(<div className="project-management-dialog-backdrop">
    <div ref={container} className={`project-management-dialog ${className}`.trim()} role="dialog" aria-modal="true"
      aria-labelledby={titleId} aria-busy={busy} tabIndex={-1}>
      <h2 id={titleId}>{title}</h2>{children}
    </div>
  </div>, document.body);
}
