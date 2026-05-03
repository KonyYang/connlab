import type { ReactElement } from "react";

import { UiIcon } from "../../components/common/UiIcon";
import type { IntakeAttachmentViewModel } from "./intakeSelectors";

type AttachmentListProps = {
  attachments: IntakeAttachmentViewModel[];
  packageLoaded: boolean;
  onSelect: (attachment: IntakeAttachmentViewModel) => void;
};

export function AttachmentList({
  attachments,
  onSelect,
  packageLoaded,
}: AttachmentListProps): ReactElement {
  return (
    <section className="intake-panel intake-attachments-panel">
      <div className="attachments-heading">
        <h3>Attachments ({attachments.length})</h3>
      </div>
      {packageLoaded ? (
        <div className="attachment-list" role="list">
          {attachments.map((attachment) => (
            <button
              className={attachment.selected ? "attachment-row attachment-row-active" : "attachment-row"}
              key={attachment.asset.asset_id}
              type="button"
              onClick={() => onSelect(attachment)}
            >
              <span className={`file-chip file-chip-${attachment.kind}`}>{attachment.label}</span>
              <span className="attachment-name">
                <strong>{attachment.asset.original_name}</strong>
                <small>{attachment.roleText}</small>
              </span>
            </button>
          ))}
        </div>
      ) : (
        <div className="attachment-empty">
          <UiIcon name="package" />
          <strong>No source imported</strong>
          <span>Import a .msg package or upload an application form.</span>
        </div>
      )}
    </section>
  );
}
