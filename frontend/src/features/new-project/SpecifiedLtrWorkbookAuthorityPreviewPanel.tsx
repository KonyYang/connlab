import type { ReactElement } from "react";

import type { SpecifiedLtrWorkbookAuthorityPreview } from "../../api/client";

type SpecifiedLtrWorkbookAuthorityPreviewPanelProps = {
  confirming: boolean;
  preview: SpecifiedLtrWorkbookAuthorityPreview;
  onCancel: () => void;
  onConfirm: () => void;
};

export function SpecifiedLtrWorkbookAuthorityPreviewPanel({
  confirming,
  preview,
  onCancel,
  onConfirm
}: SpecifiedLtrWorkbookAuthorityPreviewPanelProps): ReactElement {
  const canConfirm = preview.status === "found" && Boolean(preview.preview_ack);
  const closeLabel = preview.status === "found" ? "Cancel" : "Close";

  return (
    <section
      aria-labelledby="specified-ltr-preview-title"
      className="specified-ltr-preview-panel"
      role={preview.status === "found" ? "dialog" : "alertdialog"}
    >
      <div className="specified-ltr-preview-heading">
        <div>
          <p className="ui-section-kicker">LTR workbook authority</p>
          <h3 id="specified-ltr-preview-title">Confirm LTR workbook row</h3>
        </div>
        <span className={`specified-ltr-preview-status is-${preview.status}`}>
          {preview.status === "found" ? "Found" : preview.status === "not_found" ? "Not found" : "Blocked"}
        </span>
      </div>

      <div className="specified-ltr-preview-meta">
        <span>{preview.ltr_number}</span>
        {preview.sheet_name && preview.row_number ? (
          <span>
            {preview.sheet_name} row {preview.row_number}
          </span>
        ) : null}
        {preview.workbook_path ? <span>{preview.workbook_path}</span> : null}
      </div>

      {preview.status === "found" ? (
        <div className="specified-ltr-preview-table" role="table" aria-label="LTR workbook row">
          {preview.row_values.map((value) => (
            <div className="specified-ltr-preview-row" role="row" key={value.field_name}>
              <span role="rowheader">{value.label}</span>
              <span role="cell">{formatPreviewValue(value.value, value.is_blank)}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="specified-ltr-preview-message" role="alert">
          {preview.message}
        </p>
      )}

      {preview.blockers.length > 0 ? (
        <ul className="specified-ltr-preview-blockers">
          {preview.blockers.map((blocker) => (
            <li key={blocker}>{blocker}</li>
          ))}
        </ul>
      ) : null}

      <div className="specified-ltr-preview-actions">
        {canConfirm ? (
          <button
            className="new-project-primary-action ui-primary-action"
            disabled={confirming}
            type="button"
            onClick={onConfirm}
          >
            {confirming ? "Applying LTR number..." : "Use this LTR number"}
          </button>
        ) : null}
        <button
          className="secondary-action"
          disabled={confirming}
          type="button"
          onClick={onCancel}
        >
          {closeLabel}
        </button>
      </div>
    </section>
  );
}

function formatPreviewValue(value: unknown, isBlank: boolean): string {
  if (isBlank || value == null) {
    return "Blank";
  }
  return String(value);
}
