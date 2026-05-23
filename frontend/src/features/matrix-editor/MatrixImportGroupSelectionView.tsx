import { type ReactElement } from "react";
import { type MatrixImportSelectableGroup } from "./matrixImportSelectionSelectors";

type MatrixImportGroupSelectionViewProps = {
  groups: MatrixImportSelectableGroup[];
  selectedGroupKeys: string[];
  disabledReason: string;
  statusMessage: string;
  onToggleGroup: (groupKey: string) => void;
  onCancel: () => void;
  onConfirm: () => void;
};

export function MatrixImportGroupSelectionView({
  groups,
  selectedGroupKeys,
  disabledReason,
  statusMessage,
  onToggleGroup,
  onCancel,
  onConfirm,
}: MatrixImportGroupSelectionViewProps): ReactElement {
  const selectedCount = selectedGroupKeys.length;
  const visibleStatusMessage = disabledReason || statusMessage;
  return (
    <section className="matrix-editor-import-modal-backdrop">
      <article className="matrix-editor-import-modal matrix-editor-group-selection-modal">
        <header>
          <div className="matrix-editor-import-header-inline">
            <h3>Select Groups</h3>
            <p>{`${groups.length} groups found, ${selectedCount} selected`}</p>
          </div>
        </header>
        <div className="matrix-editor-group-selection-body">
          <table className="matrix-editor-group-selection-table">
            <thead>
              <tr>
                <th>Select</th>
                <th>Group</th>
                <th>Sample Qty</th>
                <th>Note</th>
                <th>Steps</th>
              </tr>
            </thead>
            <tbody>
              {groups.map((group) => {
                const checked = selectedGroupKeys.includes(group.groupKey);
                return (
                  <tr key={group.groupKey}>
                    <td>
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => onToggleGroup(group.groupKey)}
                        aria-label={`Select ${group.groupLabel}`}
                      />
                    </td>
                    <td>{`${group.groupLabel} (${group.groupKey})`}</td>
                    <td>{group.sampleQuantityExpression ?? "-"}</td>
                    <td>{group.sampleNote ?? "-"}</td>
                    <td>{group.stepCount}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {visibleStatusMessage ? (
            <p className="matrix-editor-group-selection-status" aria-live="polite">
              {visibleStatusMessage}
            </p>
          ) : null}
          <footer className="matrix-editor-import-controls-footer">
            <button className="matrix-editor-import-secondary-button" type="button" onClick={onCancel}>
              Cancel
            </button>
            <button
              className="matrix-editor-import-commit-button"
              type="button"
              disabled={disabledReason.length > 0}
              title={disabledReason}
              onClick={onConfirm}
            >
              Create project draft
            </button>
          </footer>
        </div>
      </article>
    </section>
  );
}
