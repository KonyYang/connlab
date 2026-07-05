import { useState, type FormEvent } from "react";

import type {
  CompleteNewProjectDuplicateResolutionInput,
  LocalLtrDuplicateConflictDetail
} from "../../api/client";

type LocalLtrDuplicateConflictPanelProps = {
  conflict: LocalLtrDuplicateConflictDetail;
  confirming?: boolean;
  onCancel: () => void;
  onOpenExisting: (projectId: string) => void;
  onConfirm: (resolution: CompleteNewProjectDuplicateResolutionInput) => Promise<void> | void;
};

export function LocalLtrDuplicateConflictPanel({
  conflict,
  confirming = false,
  onCancel,
  onOpenExisting,
  onConfirm
}: LocalLtrDuplicateConflictPanelProps) {
  const [reason, setReason] = useState("");
  const [localSubmitting, setLocalSubmitting] = useState(false);
  const reasonText = reason.trim();
  const isConfirming = confirming || localSubmitting;
  const confirmDisabled = isConfirming || reasonText.length === 0;
  const identityLine = [
    conflict.ltr_number,
    conflict.existing.sample_description,
    conflict.existing.test_item
  ]
    .filter((value): value is string => Boolean(value && value.trim()))
    .join(" ");

  async function handleConfirmRequest(): Promise<void> {
    if (confirmDisabled) {
      return;
    }
    setLocalSubmitting(true);
    try {
      await onConfirm({
        action: "replace_local_association",
        token: conflict.resolution.token,
        acknowledged: true,
        reason: reasonText
      });
    } finally {
      setLocalSubmitting(false);
    }
  }

  function handleConfirm(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    void handleConfirmRequest();
  }

  return (
    <div className="local-ltr-duplicate-modal" role="presentation">
      <section
        aria-label="Local LTR duplicate confirmation"
        aria-modal="true"
        className="local-ltr-duplicate-panel"
        role="alertdialog"
      >
        <p className="local-ltr-duplicate-panel__identity">{identityLine || conflict.ltr_number}</p>
        <div className="local-ltr-duplicate-panel__actions">
          <button
            className="primary-action"
            type="button"
            onClick={() => onOpenExisting(conflict.existing.project_id)}
          >
            Open existing project
          </button>
          <button className="secondary-action" type="button" onClick={onCancel}>
            Cancel
          </button>
        </div>
        <form className="local-ltr-duplicate-panel__confirmation" onSubmit={handleConfirm}>
          <label className="local-ltr-duplicate-panel__note">
            <span>Confirmation note</span>
            <textarea
              value={reason}
              rows={3}
              onChange={(event) => setReason(event.target.value)}
            />
          </label>
          <button
            className="secondary-action"
            disabled={confirmDisabled}
            type="submit"
          >
            {isConfirming ? "Replacing..." : "Replace local owner"}
          </button>
        </form>
      </section>
    </div>
  );
}
