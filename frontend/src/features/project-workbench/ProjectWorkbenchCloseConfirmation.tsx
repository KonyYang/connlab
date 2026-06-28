import { useState, type ReactElement } from "react";
import type { ProjectOutputStatusItem, ProjectOutputStatusSummary } from "../../api/client";
import type {
  WorkbenchLifecycleActionsViewModel,
  WorkbenchLifecycleClosePath,
} from "./projectWorkbenchLifecycleSelectors";

type ProjectWorkbenchCloseConfirmationProps = {
  compact?: boolean;
  lifecycleActions: WorkbenchLifecycleActionsViewModel;
  lifecycleBusy: boolean;
  outputStatusSummary: ProjectOutputStatusSummary | null;
  projectIdentity: string;
  projectReference: string | null;
  onCloseCompletedProject: (closeNote: string) => void | Promise<void>;
  onCloseAdministrativeProject: (reason: string) => void | Promise<void>;
};

export function ProjectWorkbenchCloseConfirmation({
  compact = false,
  lifecycleActions,
  lifecycleBusy,
  outputStatusSummary,
  projectIdentity,
  projectReference,
  onCloseCompletedProject,
  onCloseAdministrativeProject,
}: ProjectWorkbenchCloseConfirmationProps): ReactElement | null {
  const [pendingClosePath, setPendingClosePath] =
    useState<WorkbenchLifecycleClosePath | null>(null);
  const [closeNote, setCloseNote] = useState("");
  const [administrativeReason, setAdministrativeReason] = useState("");
  const [manualCompletionConfirmed, setManualCompletionConfirmed] = useState(false);
  const [outputSummaryAcknowledged, setOutputSummaryAcknowledged] = useState(false);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  if (!lifecycleActions.canClose) {
    return null;
  }

  function resetConfirmation(): void {
    setPendingClosePath(null);
    setCloseNote("");
    setAdministrativeReason("");
    setManualCompletionConfirmed(false);
    setOutputSummaryAcknowledged(false);
    setValidationMessage(null);
  }

  async function handleCompletedClose(): Promise<void> {
    const normalizedCloseNote = closeNote.trim();
    if (!normalizedCloseNote) {
      setValidationMessage("Close note is required.");
      return;
    }
    if (!manualCompletionConfirmed) {
      setValidationMessage("Manual completion confirmation is required.");
      return;
    }
    if (!outputSummaryAcknowledged) {
      setValidationMessage("Output status acknowledgement is required.");
      return;
    }
    await onCloseCompletedProject(normalizedCloseNote);
    resetConfirmation();
  }

  async function handleAdministrativeClose(): Promise<void> {
    const normalizedReason = administrativeReason.trim();
    if (!normalizedReason) {
      setValidationMessage("Administrative close reason is required.");
      return;
    }
    await onCloseAdministrativeProject(normalizedReason);
    resetConfirmation();
  }

  return (
    <section
      className={`runtime-console-close-actions${compact ? " is-compact" : ""}`}
      aria-label="Project close actions"
    >
      {compact ? null : (
        <div className="runtime-console-close-actions-heading">
          <strong>Archive project</strong>
          <p>
            Close archives this project as read-only. Use completed close only after
            reviewing available output status.
          </p>
        </div>
      )}
      <div className="runtime-console-lifecycle-actions">
        {lifecycleActions.canCloseCompleted ? (
          <button
            type="button"
            disabled={lifecycleBusy}
            className="runtime-console-close-action"
            onClick={() => {
              setPendingClosePath("completed");
              setValidationMessage(null);
            }}
          >
            {lifecycleActions.completedCloseLabel}
          </button>
        ) : null}
        {lifecycleActions.canCloseAdministrative ? (
          <button
            type="button"
            disabled={lifecycleBusy}
            className="runtime-console-close-action is-administrative"
            onClick={() => {
              setPendingClosePath("administrative");
              setValidationMessage(null);
            }}
          >
            {lifecycleActions.administrativeCloseLabel}
          </button>
        ) : null}
      </div>
      {pendingClosePath === "completed" ? (
        <div className="runtime-console-lifecycle-confirmation">
          <strong>Confirm completed close</strong>
          <p>
            This is a manual archive confirmation for {projectReference ?? projectIdentity}.
            ConnLab has not verified testing from structured step records in this phase.
          </p>
          <OutputStatusSummaryPanel outputStatusSummary={outputStatusSummary} />
          <label>
            <span>Close note</span>
            <textarea
              value={closeNote}
              onChange={(event) => setCloseNote(event.target.value)}
              rows={3}
            />
          </label>
          <label className="runtime-console-lifecycle-check">
            <input
              type="checkbox"
              checked={manualCompletionConfirmed}
              onChange={(event) => setManualCompletionConfirmed(event.target.checked)}
            />
            <span>I manually confirm this project is ready to archive as completed.</span>
          </label>
          <label className="runtime-console-lifecycle-check">
            <input
              type="checkbox"
              checked={outputSummaryAcknowledged}
              onChange={(event) => setOutputSummaryAcknowledged(event.target.checked)}
            />
            <span>I reviewed the available output status summary.</span>
          </label>
          <CloseValidationMessage message={validationMessage} />
          <div className="runtime-console-lifecycle-confirm-actions">
            <button
              type="button"
              disabled={lifecycleBusy}
              onClick={() => void handleCompletedClose()}
            >
              Confirm completed close
            </button>
            <button type="button" disabled={lifecycleBusy} onClick={resetConfirmation}>
              Cancel
            </button>
          </div>
        </div>
      ) : null}
      {pendingClosePath === "administrative" ? (
        <div className="runtime-console-lifecycle-confirmation">
          <strong>Confirm administrative close</strong>
          <p>
            Administrative close archives the project without marking testing complete.
            Use this for temporary, duplicate, or non-completion closure.
          </p>
          <label>
            <span>Administrative reason</span>
            <textarea
              value={administrativeReason}
              onChange={(event) => setAdministrativeReason(event.target.value)}
              rows={3}
            />
          </label>
          <CloseValidationMessage message={validationMessage} />
          <div className="runtime-console-lifecycle-confirm-actions">
            <button
              type="button"
              disabled={lifecycleBusy}
              onClick={() => void handleAdministrativeClose()}
            >
              Confirm administrative close
            </button>
            <button type="button" disabled={lifecycleBusy} onClick={resetConfirmation}>
              Cancel
            </button>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function OutputStatusSummaryPanel({
  outputStatusSummary,
}: {
  outputStatusSummary: ProjectOutputStatusSummary | null;
}): ReactElement {
  if (!outputStatusSummary) {
    return (
      <div className="runtime-console-output-status-summary">
        <strong>Output status summary</strong>
        <p>Output status is not available. Review current Workbench outputs before closing.</p>
      </div>
    );
  }

  return (
    <div className="runtime-console-output-status-summary">
      <strong>Output status summary</strong>
      {outputStatusSummary.items.length > 0 ? (
        <ul>
          {outputStatusSummary.items.map((item) => (
            <li key={`${item.output_kind}-${item.output_path ?? item.reason}`}>
              <span>{formatOutputKind(item.output_kind)}</span>
              <strong>{formatOutputStatus(item.status)}</strong>
              <p>{item.reason}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>No output status items are currently reported.</p>
      )}
    </div>
  );
}

function CloseValidationMessage({
  message,
}: {
  message: string | null;
}): ReactElement | null {
  if (!message) {
    return null;
  }
  return (
    <p className="runtime-console-error" role="alert">
      {message}
    </p>
  );
}

function formatOutputKind(kind: ProjectOutputStatusItem["output_kind"]): string {
  const labels: Record<ProjectOutputStatusItem["output_kind"], string> = {
    section2_write_back: "Section 2 write-back",
    test_record_form: "Test Record",
    fee_evaluation: "Fee Evaluation",
    customer_feedback_form: "Customer Feedback",
    approval_package: "Approval Package",
  };
  return labels[kind];
}

function formatOutputStatus(status: ProjectOutputStatusItem["status"]): string {
  const labels: Record<ProjectOutputStatusItem["status"], string> = {
    missing: "Missing",
    current: "Current",
    stale: "Needs refresh",
    manual: "Manual",
    failed: "Failed",
  };
  return labels[status];
}
