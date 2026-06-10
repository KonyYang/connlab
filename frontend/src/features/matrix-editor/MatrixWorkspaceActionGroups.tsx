import { type ReactElement } from "react";

type MatrixWorkspaceActionGroupsProps = {
  publishDisabled: boolean;
  publishBusy: boolean;
  testRecordDisabled: boolean;
  testRecordBusy: boolean;
  onCancel: () => void;
  onChangeSourceMatrix: () => void;
  onGenerateTestRecord: () => void;
  onPublishActiveMatrix: () => void;
};

export function MatrixWorkspaceActionGroups({
  publishDisabled,
  publishBusy,
  testRecordDisabled,
  testRecordBusy,
  onCancel,
  onChangeSourceMatrix,
  onGenerateTestRecord,
  onPublishActiveMatrix,
}: MatrixWorkspaceActionGroupsProps): ReactElement {
  return (
    <section className="matrix-workspace-toolbar" aria-label="Matrix workspace actions">
      <div className="matrix-workspace-toolbar-edit-actions">
        <button type="button" onClick={onChangeSourceMatrix}>
          Import Matrix
        </button>
        <button
          type="button"
          disabled={testRecordDisabled}
          onClick={onGenerateTestRecord}
        >
          {testRecordBusy ? "Generating..." : "Test record"}
        </button>
      </div>
      <div className="matrix-workspace-toolbar-completion-actions">
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
        <button
          className="matrix-editor-primary-action"
          type="button"
          disabled={publishDisabled}
          onClick={onPublishActiveMatrix}
        >
          {publishBusy ? "Confirming..." : "Confirm Matrix"}
        </button>
      </div>
    </section>
  );
}
