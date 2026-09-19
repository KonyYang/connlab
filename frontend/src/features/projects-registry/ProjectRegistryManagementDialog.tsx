import { useEffect, useId, useRef, useState, type ReactElement, type ReactNode } from "react";
import { createPortal } from "react-dom";
import type { ProjectRegistryAction, ProjectRegistryEntry, ProjectRegistryPreview } from "../../api/projectRegistryManagement";

export function ProjectRegistryManagementDialog({action, preview, loading, busy, error, stale,
  onCancel, onRefresh, onTrash, onRestore}: {
  action: ProjectRegistryAction; preview: ProjectRegistryPreview | null; loading: boolean; busy: boolean;
  error: string | null; stale: boolean; onCancel: () => void; onRefresh: () => void;
  onTrash: (reason: string) => void | Promise<void>;
  onRestore: (destination: "active" | "history", replaceConflicts: boolean) => void | Promise<void>;
}): ReactElement {
  const [reason, setReason] = useState("");
  const [note, setNote] = useState("");
  const disabled = busy || loading || stale || !preview || Boolean(preview.blockers.length);
  const conflicts = preview?.conflicts ?? [];
  return <ProjectManagementDialog title={action === "trash" ? "Delete project" : "Restore project"} busy={busy} onCancel={onCancel}>
    {loading && <p role="status">Loading management preview…</p>}
    {preview && <>
      <ProjectRecordIdentity project={preview.project} />
      <p>{action === "trash"
        ? "This moves the record to the recycle bin and removes it from normal lists, counts and work queues. You can restore it later."
        : "Restore keeps this record's original lifecycle and all its data. It does not overwrite another project's records."}</p>
      <p className="project-management-help">Public-drive files, original materials and LTR workbook records stay unchanged. LTR ownership is not transferred.</p>
      {preview.retained_data.length > 0 && <details><summary>Retained project records</summary><ul>{preview.retained_data.map((item) => <li key={item}>{item}</li>)}</ul></details>}
      {preview.warnings.length > 0 && <ul className="project-management-warnings">{preview.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>}
      {preview.blockers.length > 0 && <div role="alert"><strong>Resolve before continuing</strong><ul>{preview.blockers.map((blocker) => <li key={blocker}>{blocker}</li>)}</ul></div>}
      {action === "trash" ? <>
        <label><span>Deletion reason</span><select data-dialog-initial-focus value={reason} disabled={busy} onChange={(event) => setReason(event.target.value)}>
          <option value="">Select a reason</option><option value="Created by mistake">Created by mistake</option>
          <option value="Duplicate project">Duplicate project</option><option value="Other">Other</option>
        </select></label>
        <label><span>Additional note (optional)</span><textarea rows={2} value={note} disabled={busy} onChange={(event) => setNote(event.target.value)} /></label>
      </> : conflicts.length > 0 ? <section aria-label="Conflicting current projects" className="project-management-conflicts">
        <strong>{conflicts.length} current {conflicts.length === 1 ? "project has" : "projects have"} the same identifier</strong>
        <p>Review every record below. Restoring as current moves all these records into retained history, with their data intact.</p>
        {conflicts.map((project) => <ProjectRecordIdentity key={project.project_id} project={project} />)}
      </section> : <p className="project-management-help">No current project conflicts were found in this preview.</p>}
    </>}
    {error && <p role="alert">{error}</p>}
    {(stale || error || Boolean(preview?.blockers.length)) && <button className="secondary-action ui-secondary-action" type="button" disabled={busy || loading} onClick={onRefresh}>Refresh preview</button>}
    <div className="project-management-dialog-actions">
      {action === "trash" ? <button className="primary-action ui-primary-action" type="button" disabled={disabled || !reason} onClick={() => void onTrash(note.trim() ? `${reason}: ${note.trim()}` : reason)}>Move to recycle bin</button>
        : <>
          <button className="primary-action ui-primary-action" type="button" disabled={disabled} onClick={() => void onRestore("active", conflicts.length > 0)}>
            {conflicts.length > 0 ? "Restore as current; retain existing projects in history" : "Restore to projects"}
          </button>
          {conflicts.length > 0 && <button className="secondary-action ui-secondary-action" type="button" disabled={disabled} onClick={() => void onRestore("history", false)}>Restore to history only</button>}
        </>}
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
export function ProjectManagementDialog({ title, children, busy = false, onCancel }: {
  title: string; children: ReactNode; busy?: boolean; onCancel: () => void;
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
    <div ref={container} className="project-management-dialog" role="dialog" aria-modal="true"
      aria-labelledby={titleId} aria-busy={busy} tabIndex={-1}>
      <h2 id={titleId}>{title}</h2>{children}
    </div>
  </div>, document.body);
}
