import type { ReactElement } from "react";
import type { MatrixMethodVersionSyncPreview } from "../../api/client";

type MatrixMethodVersionSyncPanelProps = {
  preview: MatrixMethodVersionSyncPreview | null;
  selectedRowIds: Set<string>;
  busy: "preview" | "apply" | null;
  error: string | null;
  message: string | null;
  disabled: boolean;
  onPreview: () => void;
  onToggle: (rowId: string, checked: boolean) => void;
  onApply: () => void;
};

export function MatrixMethodVersionSyncPanel({
  preview,
  selectedRowIds,
  busy,
  error,
  message,
  disabled,
  onPreview,
  onToggle,
  onApply,
}: MatrixMethodVersionSyncPanelProps): ReactElement {
  const selectableCount = preview?.rows.filter((row) => row.selectable).length ?? 0;
  return (
    <section className="matrix-method-sync" aria-labelledby="matrix-method-sync-title">
      <header className="matrix-method-sync-header">
        <div>
          <h3 id="matrix-method-sync-title">Standard Method versions</h3>
          <span>{preview ? `${selectableCount} update(s) available` : "Check the configured Standard record"}</span>
        </div>
        <div className="matrix-method-sync-actions">
          <button type="button" disabled={disabled || busy !== null} onClick={onPreview}>
            {busy === "preview" ? "Checking..." : "Check versions"}
          </button>
          <button
            className="ui-primary-action"
            type="button"
            disabled={disabled || busy !== null || selectedRowIds.size === 0}
            onClick={onApply}
          >
            {busy === "apply" ? "Applying..." : "Apply selected"}
          </button>
        </div>
      </header>
      {preview ? (
        <div className="matrix-method-sync-table-wrap">
          <table className="matrix-method-sync-table">
            <thead><tr><th>Use</th><th>Test item</th><th>Current</th><th>Catalog</th><th>Status</th></tr></thead>
            <tbody>
              {preview.rows.map((row) => (
                <tr className="matrix-method-sync-row" key={row.draft_row_id}>
                  <td className="matrix-method-sync-select" data-label="Use">
                    <input
                      aria-label={`Select ${row.test_item} Method update`}
                      type="checkbox"
                      checked={selectedRowIds.has(row.draft_row_id)}
                      disabled={!row.selectable || busy !== null || disabled}
                      onChange={(event) => onToggle(row.draft_row_id, event.target.checked)}
                    />
                  </td>
                  <td className="matrix-method-sync-item" data-label="Test item">{row.test_item}</td>
                  <td className="matrix-method-sync-current" data-label="Current">
                    {row.current_method || "-"}
                  </td>
                  <td className="matrix-method-sync-proposed" data-label="Proposed">
                    {row.proposed_method || row.matched_standard_code || "-"}
                  </td>
                  <td className="matrix-method-sync-status" data-label="Status">
                    {row.status.replaceAll("_", " ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      {error ? <p className="matrix-method-sync-error" role="alert">{error}</p> : null}
      {message ? <p className="matrix-method-sync-message" role="status">{message}</p> : null}
    </section>
  );
}
