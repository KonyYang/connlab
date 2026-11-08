import { useEffect, useRef, useState, type ReactElement } from "react";
import type { ProjectCloseReasonCategory, ProjectOutputStatusSummary } from "../../api/client";
import { ProjectManagementDialog } from "../projects-registry/ProjectRegistryManagementDialog";
import type { WorkbenchLifecycleActionsViewModel } from "./projectWorkbenchLifecycleSelectors";
import "../../project-dashboard.css";
import "./ProjectWorkbenchCloseConfirmation.css";

const CLOSE_REASON_OPTIONS: Array<{value: ProjectCloseReasonCategory; label: string}> = [
  { value: "completed", label: "Completed" },
  { value: "cancelled", label: "Cancelled" },
  { value: "cannot_test", label: "Unable to continue" },
  { value: "other", label: "Other" },
];

type ProjectWorkbenchCloseConfirmationProps = {
  compact?: boolean;
  lifecycleActions: WorkbenchLifecycleActionsViewModel;
  lifecycleBusy: boolean;
  outputStatusSummary: ProjectOutputStatusSummary | null;
  projectIdentity: string;
  projectReference: string | null;
  onCloseProject: (reasonCategory: ProjectCloseReasonCategory, note: string) => void | Promise<void>;
  initiallyOpen?: boolean;
  onDismiss?: () => void;
};

export function ProjectWorkbenchCloseConfirmation({
  compact = false, lifecycleActions, lifecycleBusy, projectIdentity,
  projectReference, onCloseProject, initiallyOpen = false, onDismiss,
}: ProjectWorkbenchCloseConfirmationProps): ReactElement | null {
  const [confirming, setConfirming] = useState(initiallyOpen);
  const [reasonCategory, setReasonCategory] = useState<ProjectCloseReasonCategory>("completed");
  const [note, setNote] = useState("");
  const [noteExpanded, setNoteExpanded] = useState(false);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const submitLock = useRef(false);
  const noteInput = useRef<HTMLTextAreaElement>(null);
  useEffect(() => { if (noteExpanded) noteInput.current?.focus(); }, [noteExpanded]);
  if (!lifecycleActions.canClose) return null;
  const busy = lifecycleBusy || submitting;
  const showNote = noteExpanded || Boolean(note);
  function resetConfirmation(): void {
    setConfirming(false); setReasonCategory("completed"); setNote(""); setNoteExpanded(false); setValidationMessage(null); onDismiss?.();
  }
  async function handleCloseProject(): Promise<void> {
    if (busy || submitLock.current) return;
    submitLock.current = true; setSubmitting(true); setValidationMessage(null);
    try {
      await onCloseProject(reasonCategory, note.trim());
      resetConfirmation();
    } catch (error) {
      setValidationMessage(error instanceof Error ? error.message : "Could not close this project. Review and retry.");
    } finally {submitLock.current = false; setSubmitting(false);}
  }
  return <section className={`runtime-console-close-actions${compact ? " is-compact" : ""}`} aria-label="Project close action">
    {!initiallyOpen && <button type="button" className="runtime-console-close-action ui-primary-action" disabled={busy}
      onClick={() => setConfirming(true)}>Close project</button>}
    {confirming && <ProjectManagementDialog title="Close project" className="project-close-dialog" busy={busy} onCancel={resetConfirmation}>
      <p className="project-close-identity">{projectReference ?? projectIdentity}</p>
      <div className="project-close-body">
        <p className="project-close-description">Records will be kept. Reopen the project to edit again.</p>
        <label className="project-close-reason"><span>Close reason</span>
          <select data-dialog-initial-focus value={reasonCategory} disabled={busy}
            onChange={(event) => setReasonCategory(event.target.value as ProjectCloseReasonCategory)}>
            {CLOSE_REASON_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        {showNote ? <label className="project-close-note"><span>Additional note (optional)</span>
          <textarea ref={noteInput} value={note} disabled={busy}
            onChange={(event) => setNote(event.target.value)} rows={3} />
        </label> : <button className="project-close-add-note" type="button" disabled={busy} onClick={() => setNoteExpanded(true)}>Add note</button>}
        {validationMessage && <p className="project-close-error" role="alert">{validationMessage}</p>}
      </div>
      <div className="project-management-dialog-actions project-close-actions">
        <button className="secondary-action ui-secondary-action" type="button" disabled={busy} onClick={resetConfirmation}>Cancel</button>
        <button className="primary-action ui-primary-action" type="button" disabled={busy} onClick={() => void handleCloseProject()}>{submitting ? "Closing…" : "Close project"}</button>
      </div>
    </ProjectManagementDialog>}
  </section>;
}
