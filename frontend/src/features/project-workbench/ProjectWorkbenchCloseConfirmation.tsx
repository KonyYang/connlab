import { useState, type ReactElement } from "react";
import type {
  ProjectCloseReasonCategory,
  ProjectOutputStatusItem,
  ProjectOutputStatusSummary,
} from "../../api/client";
import type { WorkbenchLifecycleActionsViewModel } from "./projectWorkbenchLifecycleSelectors";

const CLOSE_REASON_OPTIONS: Array<{
  value: ProjectCloseReasonCategory;
  label: string;
}> = [
  { value: "completed", label: "Completed" },
  { value: "failed", label: "Failed" },
  { value: "cancelled", label: "Cancelled" },
  { value: "cannot_test", label: "Cannot test" },
  { value: "duplicate", label: "Duplicate" },
  { value: "other", label: "Other" },
];

type ProjectWorkbenchCloseConfirmationProps = {
  compact?: boolean;
  lifecycleActions: WorkbenchLifecycleActionsViewModel;
  lifecycleBusy: boolean;
  outputStatusSummary: ProjectOutputStatusSummary | null;
  projectIdentity: string;
  projectReference: string | null;
  onCloseProject: (
    reasonCategory: ProjectCloseReasonCategory,
    note: string
  ) => void | Promise<void>;
};

export function ProjectWorkbenchCloseConfirmation({
  compact = false,
  lifecycleActions,
  lifecycleBusy,
  outputStatusSummary,
  projectIdentity,
  projectReference,
  onCloseProject,
}: ProjectWorkbenchCloseConfirmationProps): ReactElement | null {
  const [confirming, setConfirming] = useState(false);
  const [reasonCategory, setReasonCategory] = useState<ProjectCloseReasonCategory>(
    lifecycleActions.defaultCloseReasonCategory
  );
  const [note, setNote] = useState("");
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  if (!lifecycleActions.canClose) {
    return null;
  }

  const normalizedNote = note.trim();
  const canSubmit = Boolean(normalizedNote) && !lifecycleBusy;

  function resetConfirmation(): void {
    setConfirming(false);
    setReasonCategory(lifecycleActions.defaultCloseReasonCategory);
    setNote("");
    setValidationMessage(null);
  }

  async function handleCloseProject(): Promise<void> {
    if (!normalizedNote) {
      setValidationMessage("Close note is required.");
      return;
    }
    await onCloseProject(reasonCategory, normalizedNote);
    resetConfirmation();
  }

  return (
    <section
      className={`runtime-console-close-actions${compact ? " is-compact" : ""}`}
      aria-label="Project close action"
    >
      {compact ? null : (
        <div className="runtime-console-close-actions-heading">
          <strong>Close project</strong>
          <p>
            Close records a business reason and keeps the project traceable for later
            activation if work needs to continue.
          </p>
        </div>
      )}
      <div className="runtime-console-lifecycle-actions">
        <button
          type="button"
          disabled={lifecycleBusy}
          className="runtime-console-close-action"
          onClick={() => {
            setConfirming(true);
            setValidationMessage(null);
          }}
        >
          {lifecycleActions.closeActionLabel}
        </button>
      </div>
      {confirming ? (
        <div className="runtime-console-lifecycle-confirmation">
          <strong>Confirm close project</strong>
          <p>
            This records why {projectReference ?? projectIdentity} is closing. It does
            not erase the project history, and the project can be activated later when
            business work should continue.
          </p>
          <OutputStatusSummaryPanel outputStatusSummary={outputStatusSummary} />
          <label>
            <span>Close reason</span>
            <select
              value={reasonCategory}
              onChange={(event) =>
                setReasonCategory(event.target.value as ProjectCloseReasonCategory)
              }
            >
              {CLOSE_REASON_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Close note</span>
            <textarea
              value={note}
              onChange={(event) => setNote(event.target.value)}
              rows={3}
            />
          </label>
          <CloseValidationMessage message={validationMessage} />
          <div className="runtime-console-lifecycle-confirm-actions">
            <button
              type="button"
              disabled={!canSubmit}
              onClick={() => void handleCloseProject()}
            >
              Confirm close project
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
    test_status: "Test Status",
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
