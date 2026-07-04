import { useEffect, useRef, type KeyboardEvent, type ReactElement } from "react";

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
  const dialogRef = useRef<HTMLElement | null>(null);
  const confirmButtonRef = useRef<HTMLButtonElement | null>(null);
  const closeButtonRef = useRef<HTMLButtonElement | null>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const metaId = "specified-ltr-preview-meta";
  const messageId = "specified-ltr-preview-message";

  useEffect(() => {
    previousFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const focusTimer = window.setTimeout(() => {
      const nextFocus = canConfirm ? confirmButtonRef.current : closeButtonRef.current;
      nextFocus?.focus();
    }, 0);

    return () => {
      window.clearTimeout(focusTimer);
      if (previousFocusRef.current?.isConnected) {
        previousFocusRef.current.focus();
      }
    };
  }, [canConfirm]);

  const handleDialogKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key === "Escape" && !confirming) {
      event.preventDefault();
      onCancel();
      return;
    }

    if (event.key !== "Tab" || !dialogRef.current) {
      return;
    }

    const focusableElements = getFocusableElements(dialogRef.current);
    if (focusableElements.length === 0) {
      event.preventDefault();
      dialogRef.current.focus();
      return;
    }

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    const activeElement = document.activeElement;

    if (event.shiftKey && activeElement === firstElement) {
      event.preventDefault();
      lastElement.focus();
      return;
    }

    if (!event.shiftKey && activeElement === lastElement) {
      event.preventDefault();
      firstElement.focus();
    }
  };

  return (
    <div className="specified-ltr-preview-modal" role="presentation">
      <div className="specified-ltr-preview-backdrop" aria-hidden="true" />
      <section
        aria-describedby={preview.status === "found" ? metaId : messageId}
        aria-labelledby="specified-ltr-preview-title"
        aria-modal="true"
        className="specified-ltr-preview-panel"
        ref={dialogRef}
        role={preview.status === "found" ? "dialog" : "alertdialog"}
        tabIndex={-1}
        onKeyDown={handleDialogKeyDown}
      >
        <div className="specified-ltr-preview-heading">
          <div>
            <h3 id="specified-ltr-preview-title">{preview.ltr_number}</h3>
          </div>
        </div>

        <div className="specified-ltr-preview-meta" id={metaId}>
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
          <p className="specified-ltr-preview-message" id={messageId} role="alert">
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
              ref={confirmButtonRef}
              type="button"
              onClick={onConfirm}
            >
              {confirming ? "Applying LTR number..." : "Use this LTR number"}
            </button>
          ) : null}
          <button
            className="secondary-action"
            disabled={confirming}
            ref={closeButtonRef}
            type="button"
            onClick={onCancel}
          >
            {closeLabel}
          </button>
        </div>
      </section>
    </div>
  );
}

function formatPreviewValue(value: unknown, isBlank: boolean): string {
  if (isBlank || value == null) {
    return "Blank";
  }
  return String(value);
}

function getFocusableElements(root: HTMLElement): HTMLElement[] {
  return Array.from(
    root.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  ).filter((element) => !element.hasAttribute("disabled"));
}
