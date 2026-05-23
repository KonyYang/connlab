import { type ReactElement } from "react";
import { type MatrixImportSelectionViewModel } from "./matrixImportSelectionSelectors";

type MatrixImportSelectionModeProps = {
  viewModel: MatrixImportSelectionViewModel;
  selectedGroupKeys: string[];
  disabledReason: string;
  statusMessage: string;
  onToggleGroup: (groupKey: string) => void;
  onCancel: () => void;
  onConfirm: () => void;
};

export function MatrixImportSelectionMode({
  viewModel,
  selectedGroupKeys,
  disabledReason,
  statusMessage,
  onToggleGroup,
  onCancel,
  onConfirm,
}: MatrixImportSelectionModeProps): ReactElement {
  const visibleStatusMessage = disabledReason || statusMessage;
  return (
    <section className="matrix-editor-selection-mode" aria-label="Matrix import selection mode">
      <header className="matrix-editor-selection-mode-header">
        <div className="matrix-editor-selection-mode-meta">
          <h3>Import Selection Mode</h3>
          <p>{`Source: ${viewModel.sourceDocumentName} | Groups: ${viewModel.groups.length}, Selected: ${selectedGroupKeys.length}`}</p>
        </div>
        <div className="matrix-editor-selection-mode-actions">
          <button
            type="button"
            className="matrix-editor-import-secondary-button"
            disabled
            title="Append Matrix requires multi-source lineage and is not active in this task."
          >
            Append Matrix (Future)
          </button>
          <button type="button" className="matrix-editor-import-secondary-button" onClick={onCancel}>Cancel</button>
          <button
            type="button"
            className="matrix-editor-import-commit-button"
            disabled={disabledReason.length > 0}
            title={disabledReason}
            onClick={onConfirm}
          >
            Confirm selected groups
          </button>
        </div>
      </header>
      {visibleStatusMessage ? (
        <p className="matrix-editor-group-selection-status" aria-live="polite">{visibleStatusMessage}</p>
      ) : null}
      <div className="matrix-editor-main-table-wrap">
        <table className="matrix-editor-main-table matrix-editor-selection-table">
          <thead>
            <tr>
              <th>Test Item</th>
              {viewModel.groups.map((group) => {
                const checked = selectedGroupKeys.includes(group.groupKey);
                return (
                  <th key={group.groupKey}>
                    <label className="matrix-editor-selection-group-toggle">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => onToggleGroup(group.groupKey)}
                        aria-label={`Select ${group.groupLabel}`}
                      />
                      <span className="matrix-editor-selection-group-toggle-box" aria-hidden="true">
                        {checked ? "X" : ""}
                      </span>
                      <span>{group.groupLabel}</span>
                    </label>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {viewModel.rows.map((row) => (
              <tr key={row.rowId}>
                <td>{row.testItem}</td>
                {viewModel.groups.map((group) => (
                  <td key={`${row.rowId}-${group.groupKey}`}>{row.tokensByGroupKey[group.groupKey] || ""}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
