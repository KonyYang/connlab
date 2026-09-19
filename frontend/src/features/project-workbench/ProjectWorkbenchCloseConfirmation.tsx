import { useRef, useState, type ReactElement } from "react";
import type { ProjectCloseReasonCategory, ProjectOutputStatusItem, ProjectOutputStatusSummary } from "../../api/client";
import { ProjectManagementDialog } from "../projects-registry/ProjectRegistryManagementDialog";
import type { WorkbenchLifecycleActionsViewModel } from "./projectWorkbenchLifecycleSelectors";
import "../../project-dashboard.css";

const CLOSE_REASON_OPTIONS: Array<{value: ProjectCloseReasonCategory; label: string}> = [
  { value: "completed", label: "Completed" },
  { value: "cancelled", label: "Cancelled" },
  { value: "cannot_test", label: "Cannot continue testing" },
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
  compact = false, lifecycleActions, lifecycleBusy, outputStatusSummary, projectIdentity,
  projectReference, onCloseProject, initiallyOpen = false, onDismiss,
}: ProjectWorkbenchCloseConfirmationProps): ReactElement | null {
  const [confirming, setConfirming] = useState(initiallyOpen);
  const [reasonCategory, setReasonCategory] = useState<ProjectCloseReasonCategory | "">("");
  const [note, setNote] = useState("");
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const submitLock = useRef(false);
  if (!lifecycleActions.canClose) return null;
  const busy = lifecycleBusy || submitting;
  const canSubmit = Boolean(reasonCategory) && (reasonCategory !== "other" || Boolean(note.trim())) && !busy;
  function resetConfirmation(): void {
    setConfirming(false); setReasonCategory(""); setNote(""); setValidationMessage(null); onDismiss?.();
  }
  async function handleCloseProject(): Promise<void> {
    if (!canSubmit || !reasonCategory || submitLock.current) return;
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
    {confirming && <ProjectManagementDialog title={`Close project ${projectReference ?? projectIdentity}`} busy={busy} onCancel={resetConfirmation}>
      <p>Closing makes this project read-only and keeps all its records. Reopen it when work needs to continue.</p>
      <label><span>Close reason</span><select data-dialog-initial-focus value={reasonCategory} disabled={busy}
        onChange={(event) => setReasonCategory(event.target.value as ProjectCloseReasonCategory | "")}>
        <option value="">Select a reason</option>
        {CLOSE_REASON_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
      </select></label>
      <label><span>Additional note ({reasonCategory === "other" ? "required" : "optional"})</span>
        <textarea value={note} disabled={busy} onChange={(event) => setNote(event.target.value)} rows={2} />
      </label>
      {reasonCategory === "other" && !note.trim() && <p className="project-management-help">Explain the reason when choosing Other.</p>}
      <OutputStatusSummaryPanel outputStatusSummary={outputStatusSummary} />
      {validationMessage && <p className="runtime-console-error" role="alert">{validationMessage}</p>}
      <div className="project-management-dialog-actions">
        <button className="primary-action ui-primary-action" type="button" disabled={!canSubmit} onClick={() => void handleCloseProject()}>{submitting ? "Closing…" : "Close project"}</button>
        <button className="secondary-action ui-secondary-action" type="button" disabled={busy} onClick={resetConfirmation}>Cancel</button>
      </div>
    </ProjectManagementDialog>}
  </section>;
}

function OutputStatusSummaryPanel({outputStatusSummary}: {outputStatusSummary: ProjectOutputStatusSummary | null}): ReactElement {
  if (!outputStatusSummary) return <p className="project-management-help">Output status is currently unavailable. You can still close the project after reviewing your records.</p>;
  const exceptions = outputStatusSummary.items.filter((item) => item.status !== "current");
  if (!exceptions.length) return <p className="project-management-help">{outputStatusSummary.items.length ? "Recorded outputs are current." : "No output status is recorded. Review your records before closing."}</p>;
  return <div className="project-management-output-summary">
    <p>{exceptions.length} {exceptions.length === 1 ? "output needs" : "outputs need"} review</p>
    <details><summary>View output details</summary><ul>{exceptions.map((item) =>
      <li key={item.output_kind}><strong>{formatOutputKind(item.output_kind)}: {formatOutputStatus(item.status)}</strong><p>{item.reason}</p></li>
    )}</ul></details>
  </div>;
}
function formatOutputKind(kind: ProjectOutputStatusItem["output_kind"]): string {
  return ({section2_write_back: "Section 2 write-back", test_record_form: "Test Record", test_status: "Test Status",
    fee_evaluation: "Fee Evaluation", customer_feedback_form: "Customer Feedback", approval_package: "Approval Package"})[kind];
}
function formatOutputStatus(status: ProjectOutputStatusItem["status"]): string {
  return ({missing: "Not generated", current: "Current", stale: "Needs refresh", manual: "Manually maintained", failed: "Failed"})[status];
}
