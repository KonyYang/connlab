import { useState } from "react";

import type {
  CompleteNewProjectDuplicateResolutionInput,
  LocalLtrDuplicateConflictDetail
} from "../../api/client";

type LocalLtrDuplicateConflictPanelProps = {
  conflict: LocalLtrDuplicateConflictDetail;
  confirming?: boolean;
  onCancel: () => void;
  onOpenExisting: (projectId: string) => void;
  onConfirm: (resolution: CompleteNewProjectDuplicateResolutionInput) => void;
};

export function LocalLtrDuplicateConflictPanel({
  conflict,
  confirming = false,
  onCancel,
  onOpenExisting,
  onConfirm
}: LocalLtrDuplicateConflictPanelProps) {
  const [expanded, setExpanded] = useState(false);
  const [acknowledged, setAcknowledged] = useState(false);
  const [reason, setReason] = useState("");
  const reasonText = reason.trim();
  const confirmDisabled = confirming || !acknowledged || reasonText.length === 0;
  const identityLine = [
    conflict.ltr_number,
    conflict.existing.sample_description,
    conflict.existing.test_item
  ]
    .filter((value): value is string => Boolean(value && value.trim()))
    .join(" ");
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
          <button
            className="secondary-action"
            type="button"
            onClick={() => setExpanded((current) => !current)}
          >
            Continue with this LTR number
          </button>
        </div>
        {expanded ? (
          <div className="local-ltr-duplicate-panel__confirmation">
            <label className="local-ltr-duplicate-panel__check">
              <input
                checked={acknowledged}
                type="checkbox"
                onChange={(event) => setAcknowledged(event.target.checked)}
              />
              <span>
                I understand the old local history will be kept and this project becomes current.
              </span>
            </label>
            <label className="local-ltr-duplicate-panel__note">
              <span>Confirmation note</span>
              <textarea
                value={reason}
                rows={3}
                onChange={(event) => setReason(event.target.value)}
              />
            </label>
            <button
              className="primary-action"
              disabled={confirmDisabled}
              type="button"
              onClick={() =>
                onConfirm({
                  action: "replace_local_association",
                  token: conflict.resolution.token,
                  acknowledged: true,
                  reason: reasonText
                })
              }
            >
              {confirming ? "Confirming..." : "Confirm current local owner"}
            </button>
          </div>
        ) : null}
      </section>
    </div>
  );
}
