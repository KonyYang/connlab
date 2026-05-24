import { type ReactElement } from "react";
import {
  buildMatrixImportSelectionSummary,
  formatMatrixImportSampleQuantity,
  type MatrixImportSelectionViewModel,
} from "./matrixImportSelectionSelectors";

type MatrixImportSelectionModeProps = {
  viewModel: MatrixImportSelectionViewModel;
  selectedGroupKeys: string[];
  disabledReason: string;
  statusMessage: string;
  onToggleGroup: (groupKey: string) => void;
  onBackToCandidateSelection: () => void;
  onCancel: () => void;
  onCancelSession: () => void;
  onConfirm: () => void;
};

export function MatrixImportSelectionMode({
  viewModel,
  selectedGroupKeys,
  disabledReason,
  statusMessage,
  onToggleGroup,
  onBackToCandidateSelection,
  onCancel,
  onCancelSession,
  onConfirm,
}: MatrixImportSelectionModeProps): ReactElement {
  const visibleStatusMessage = disabledReason || statusMessage;
  const summary = buildMatrixImportSelectionSummary({
    groups: viewModel.groups,
    selectedGroupKeys,
  });
  const selectedGroupList = summary.selectedGroupLabels.length > 0
    ? summary.selectedGroupLabels.join(", ")
    : "None selected";
  const selectedStepText = summary.hasStepCounts && summary.selectedStepCount !== null
    ? `${summary.selectedStepCount}`
    : "not available";
  return (
    <section className="matrix-editor-selection-mode" aria-label="Matrix import selection mode">
      <header className="matrix-editor-selection-mode-header">
        <div className="matrix-editor-selection-mode-meta">
          <h3>Import Selection Mode</h3>
          <p>{`Source: ${viewModel.sourceDocumentName}`}</p>
          <p>{`Selected groups: ${summary.selectedGroupCount} / ${summary.totalGroupCount} | Selected steps: ${selectedStepText}`}</p>
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
          <button type="button" className="matrix-editor-import-secondary-button" onClick={onBackToCandidateSelection}>
            Back to matrix candidate selection
          </button>
          <button type="button" className="matrix-editor-import-secondary-button" onClick={onCancel}>
            Back to editor
          </button>
          <button type="button" className="matrix-editor-import-secondary-button" onClick={onCancelSession}>
            Cancel import session
          </button>
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
      <aside className="matrix-editor-selection-summary" aria-label="Selected group summary">
        <div>
          <strong>Selected groups</strong>
          <span>{selectedGroupList}</span>
        </div>
        <div>
          <strong>Selected step count</strong>
          <span>{selectedStepText}</span>
        </div>
        <div>
          <strong>Sample quantities</strong>
          <span>
            {summary.selectedSampleQuantities.length > 0
              ? summary.selectedSampleQuantities
                  .map((entry) => `${entry.groupLabel}: ${entry.sampleQuantityExpression}`)
                  .join("; ")
              : "Select at least one group to review sample quantities."}
          </span>
        </div>
        {summary.selectedGroupCount === 0 ? (
          <p className="matrix-editor-selection-blocker">Select at least one group before creating the draft.</p>
        ) : null}
      </aside>
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
                      <span className="matrix-editor-selection-group-label">
                        <span>{group.groupLabel}</span>
                        <small>{`Samples: ${formatMatrixImportSampleQuantity(group.sampleQuantityExpression)}`}</small>
                      </span>
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
