import { type ReactElement } from "react";

type MatrixWorkspaceActionGroupsProps = {
  changeSelectedGroupsDisabled: boolean;
  changeSelectedGroupsDisabledReason: string;
  publishDisabled: boolean;
  publishDisabledReason: string;
  publishBusy: boolean;
  onChangeSelectedGroups: () => void;
  onChangeSourceMatrix: () => void;
  onPublishActiveMatrix: () => void;
};

export function MatrixWorkspaceActionGroups({
  changeSelectedGroupsDisabled,
  changeSelectedGroupsDisabledReason,
  publishDisabled,
  publishDisabledReason,
  publishBusy,
  onChangeSelectedGroups,
  onChangeSourceMatrix,
  onPublishActiveMatrix,
}: MatrixWorkspaceActionGroupsProps): ReactElement {
  return (
    <section className="matrix-workspace-toolbar" aria-label="Matrix workspace actions">
      <button
        type="button"
        disabled={changeSelectedGroupsDisabled}
        title={changeSelectedGroupsDisabled ? changeSelectedGroupsDisabledReason : ""}
        onClick={onChangeSelectedGroups}
      >
        Change Selected Groups
      </button>
      <button type="button" onClick={onChangeSourceMatrix}>
        Change Source Matrix
      </button>
      <button
        className="matrix-editor-primary-action"
        type="button"
        disabled={publishDisabled}
        title={publishDisabled ? publishDisabledReason : ""}
        onClick={onPublishActiveMatrix}
      >
        {publishBusy ? "Confirming..." : "Confirm As Active Matrix"}
      </button>
    </section>
  );
}
