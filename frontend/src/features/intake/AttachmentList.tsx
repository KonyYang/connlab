import type { ReactElement } from "react";

import { UiIcon } from "../../components/common/UiIcon";
import type { IntakeAttachmentViewModel } from "./intakeSelectors";

type AttachmentListProps = {
  attachments: IntakeAttachmentViewModel[];
  importingAssetId?: string | null;
  onImport?: (attachment: IntakeAttachmentViewModel) => void;
  onOpen?: (attachment: IntakeAttachmentViewModel) => void;
  onSelect: (attachment: IntakeAttachmentViewModel) => void;
  packageLoaded: boolean;
};

export function AttachmentList({
  attachments,
  importingAssetId,
  onImport,
  onOpen,
  onSelect,
  packageLoaded,
}: AttachmentListProps): ReactElement {
  return (
    <section className="intake-panel intake-attachments-panel">
      <div className="attachments-heading">
        <h3 className="ui-panel-title">Attachments ({attachments.length})</h3>
      </div>
      {packageLoaded ? (
        <div className="attachment-list" role="list">
          {attachments.map((attachment) => (
            <div
              className={attachment.selected ? "attachment-row attachment-row-active" : "attachment-row"}
              key={attachment.asset.asset_id}
              onDoubleClick={() => onOpen?.(attachment)}
            >
              <button
                className="attachment-select-button"
                type="button"
                onClick={() => onSelect(attachment)}
              >
                <span className={`file-chip file-chip-${attachment.kind}`}>{attachment.label}</span>
                <span className="attachment-name">
                  <span className="attachment-title">{attachment.asset.original_name}</span>
                </span>
              </button>
              {attachment.word && onImport ? (
                <button
                  className="attachment-import-button ui-compact-action"
                  disabled={importingAssetId === attachment.asset.asset_id}
                  type="button"
                  onClick={() => onImport?.(attachment)}
                >
                  {importingAssetId === attachment.asset.asset_id ? "Importing" : "Import"}
                </button>
              ) : null}
            </div>
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
