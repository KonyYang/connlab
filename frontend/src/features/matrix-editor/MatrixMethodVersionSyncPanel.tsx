import { useEffect, useRef, type KeyboardEvent, type ReactElement } from "react";
import type { MatrixMethodVersionSyncPreview } from "../../api/client";

type MatrixMethodVersionSyncPanelProps = {
  preview: MatrixMethodVersionSyncPreview | null;
  selectedRowIds: Set<string>;
  busy: "preview" | "apply" | null;
  error: string | null;
  message: string | null;
  disabled: boolean;
  disabledReason?: string;
  onPreview: () => void;
  onToggle: (rowId: string, checked: boolean) => void;
  onApply: () => void;
  onClose: () => void;
};

export function MatrixMethodVersionSyncPanel({
  preview,
  selectedRowIds,
  busy,
  error,
  message,
  disabled,
  disabledReason,
  onPreview,
  onToggle,
  onApply,
  onClose,
}: MatrixMethodVersionSyncPanelProps): ReactElement {
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLElement>(null);
  const selectableCount = preview?.rows.filter((row) => row.selectable).length ?? 0;

  useEffect(() => {
    closeButtonRef.current?.focus();
  }, []);

  useEffect(() => {
    if (busy !== null) dialogRef.current?.focus();
  }, [busy]);

  const onDialogKeyDown = (event: KeyboardEvent<HTMLElement>): void => {
    if (event.key === "Escape" && busy === null) {
      event.preventDefault();
      onClose();
      return;
    }
    if (event.key !== "Tab") return;
    const focusable = Array.from(
      dialogRef.current?.querySelectorAll<HTMLElement>("button:not(:disabled), input:not(:disabled)") ?? []
    );
    const first = focusable[0];
    const last = focusable.at(-1);
    if (!first || !last) {
      event.preventDefault();
      return;
    }
    if (!focusable.includes(document.activeElement as HTMLElement)) {
      event.preventDefault();
      (event.shiftKey ? last : first).focus();
      return;
    }
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first?.focus();
    }
  };

  return (
    <section className="matrix-method-sync-backdrop">
      <article
        className="matrix-method-sync"
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="matrix-method-sync-title"
        aria-describedby="matrix-method-sync-description"
        tabIndex={-1}
        onKeyDown={onDialogKeyDown}
      >
        <header className="matrix-method-sync-header">
          <div>
            <h3 id="matrix-method-sync-title">Standard Method versions</h3>
            <span id="matrix-method-sync-description">
              {disabled ? disabledReason || "Save the Matrix draft before checking Method versions." :
                preview ? `${selectableCount} update(s) available` : "Check the configured Standard record"}
            </span>
          </div>
          <button type="button" disabled={disabled || busy !== null} onClick={onPreview}>
            {busy === "preview" ? "Checking..." : "Check versions"}
          </button>
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
        <footer className="matrix-method-sync-actions">
          <span>Updates change the saved draft; Confirm Matrix is still required.</span>
          <div>
            <button type="button" ref={closeButtonRef} disabled={busy !== null} onClick={onClose}>Close</button>
            <button
              className="ui-primary-action"
              type="button"
              disabled={disabled || busy !== null || selectedRowIds.size === 0}
              onClick={onApply}
            >
              {busy === "apply" ? "Applying..." : "Apply selected"}
            </button>
          </div>
        </footer>
      </article>
    </section>
  );
}
