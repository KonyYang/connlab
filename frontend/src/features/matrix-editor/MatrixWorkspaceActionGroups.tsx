import { type ReactElement } from "react";
import { MATRIX_WORKSPACE_ACTION_COPY } from "./matrixWorkspaceClarityModel";

type MatrixActionButtonProps = {
  label: string;
  busyLabel?: string;
  consequence: string;
  disabled: boolean;
  disabledReason: string;
  isBusy?: boolean;
  primary?: boolean;
  onClick: () => void;
};

function MatrixActionButton({
  label,
  busyLabel,
  consequence,
  disabled,
  disabledReason,
  isBusy = false,
  primary = false,
  onClick,
}: MatrixActionButtonProps): ReactElement {
  return (
    <div className="matrix-workspace-action-item">
      <button
        className={primary ? "matrix-editor-primary-action" : undefined}
        type="button"
        disabled={disabled}
        title={disabled ? disabledReason : consequence}
        onClick={onClick}
      >
        {isBusy && busyLabel ? busyLabel : label}
      </button>
      <p>{consequence}</p>
    </div>
  );
}

type MatrixWorkspaceActionGroupsProps = {
  revertDraftVisible: boolean;
  revertDraftDisabled: boolean;
  revertDraftDisabledReason: string;
  changeSelectedGroupsDisabled: boolean;
  changeSelectedGroupsDisabledReason: string;
  confirmAsActiveDisabled: boolean;
  confirmAsActiveDisabledReason: string;
  confirmAsActiveBusy: boolean;
  createRevisionDisabled: boolean;
  createRevisionDisabledReason: string;
  createRevisionBusy: boolean;
  confirmRevisionDisabled: boolean;
  confirmRevisionDisabledReason: string;
  confirmRevisionBusy: boolean;
  showConfirmAsActive: boolean;
  showConfirmRevision: boolean;
  onRevertDraftChanges: () => void;
  onChangeSelectedGroups: () => void;
  onChangeSourceMatrix: () => void;
  onConfirmAsActiveMatrix: () => void;
  onCreateRevisionDraft: () => void;
  onConfirmRevision: () => void;
};

export function MatrixWorkspaceActionGroups({
  revertDraftVisible,
  revertDraftDisabled,
  revertDraftDisabledReason,
  changeSelectedGroupsDisabled,
  changeSelectedGroupsDisabledReason,
  confirmAsActiveDisabled,
  confirmAsActiveDisabledReason,
  confirmAsActiveBusy,
  createRevisionDisabled,
  createRevisionDisabledReason,
  createRevisionBusy,
  confirmRevisionDisabled,
  confirmRevisionDisabledReason,
  confirmRevisionBusy,
  showConfirmAsActive,
  showConfirmRevision,
  onRevertDraftChanges,
  onChangeSelectedGroups,
  onChangeSourceMatrix,
  onConfirmAsActiveMatrix,
  onCreateRevisionDraft,
  onConfirmRevision,
}: MatrixWorkspaceActionGroupsProps): ReactElement {
  return (
    <section className="matrix-workspace-action-groups" aria-label="Matrix workspace actions">
      <div className="matrix-workspace-action-group" aria-label="Draft Actions">
        <h3>Draft Actions</h3>
        <MatrixActionButton
          label="Change Selected Groups"
          consequence={MATRIX_WORKSPACE_ACTION_COPY.changeSelectedGroups}
          disabled={changeSelectedGroupsDisabled}
          disabledReason={changeSelectedGroupsDisabledReason}
          onClick={onChangeSelectedGroups}
        />
        <MatrixActionButton
          label="Change Source Matrix"
          consequence={MATRIX_WORKSPACE_ACTION_COPY.changeSourceMatrix}
          disabled={false}
          disabledReason=""
          onClick={onChangeSourceMatrix}
        />
        {revertDraftVisible ? (
          <MatrixActionButton
            label="Revert to last saved draft"
            consequence={MATRIX_WORKSPACE_ACTION_COPY.revertDraftChanges}
            disabled={revertDraftDisabled}
            disabledReason={revertDraftDisabledReason}
            onClick={onRevertDraftChanges}
          />
        ) : null}
      </div>

      <div className="matrix-workspace-action-group" aria-label="Authority Actions">
        <h3>Authority Actions</h3>
        {showConfirmAsActive ? (
          <MatrixActionButton
            label="Confirm As Active Matrix"
            busyLabel="Confirming..."
            consequence={MATRIX_WORKSPACE_ACTION_COPY.confirmAsActiveMatrix}
            disabled={confirmAsActiveDisabled}
            disabledReason={confirmAsActiveDisabledReason}
            isBusy={confirmAsActiveBusy}
            primary
            onClick={onConfirmAsActiveMatrix}
          />
        ) : null}
        <MatrixActionButton
          label="Create Revision Draft"
          busyLabel="Creating..."
          consequence={MATRIX_WORKSPACE_ACTION_COPY.createRevisionDraft}
          disabled={createRevisionDisabled}
          disabledReason={createRevisionDisabledReason}
          isBusy={createRevisionBusy}
          onClick={onCreateRevisionDraft}
        />
        {showConfirmRevision ? (
          <MatrixActionButton
            label="Confirm Revision"
            busyLabel="Confirming..."
            consequence={MATRIX_WORKSPACE_ACTION_COPY.confirmRevision}
            disabled={confirmRevisionDisabled}
            disabledReason={confirmRevisionDisabledReason}
            isBusy={confirmRevisionBusy}
            primary
            onClick={onConfirmRevision}
          />
        ) : null}
      </div>
    </section>
  );
}
