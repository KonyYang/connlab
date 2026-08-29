import type { ReactElement } from "react";
import type { MatrixImportDialogView } from "./useMatrixImportWorkflow";

type MatrixImportDialogProps = {
  dialog: MatrixImportDialogView;
  readOnly: boolean;
};

export function MatrixImportDialog({
  dialog,
  readOnly,
}: MatrixImportDialogProps): ReactElement {
  const isXlsx = dialog.preview?.source_format.toLowerCase() === ".xlsx";
  const groupCount = dialog.preview?.groups.length ?? 0;
  const rowCount = dialog.preview?.rows.length ?? 0;
  return (
    <section className="matrix-editor-import-modal-backdrop">
      <article
        className="matrix-editor-import-modal"
        onClick={(event) => event.stopPropagation()}
      >
        <header>
          <div className="matrix-editor-import-header-inline">
            <h3>Import Matrix</h3>
            <p title={dialog.fileName}>{dialog.fileName}</p>
          </div>
        </header>
        <div className={`matrix-editor-import-modal-body${isXlsx ? " is-xlsx" : ""}`}>
          {isXlsx ? (
            <section className="matrix-editor-import-xlsx-summary" aria-label="Workbook summary">
              <h4>ConnLab Matrix workbook</h4>
              <p>
                {groupCount} Group{groupCount === 1 ? "" : "s"} · {rowCount} test row
                {rowCount === 1 ? "" : "s"}
              </p>
              {dialog.preview?.warnings.length ? (
                <ul>
                  {dialog.preview.warnings.map((warning, index) => (
                    <li key={`${index}-${warning}`}>{warning}</li>
                  ))}
                </ul>
              ) : (
                <p>Workbook details match the visible Matrix table.</p>
              )}
            </section>
          ) : (
            <div className="matrix-editor-import-pdf-pane">
              {dialog.previewPdfSrc ? (
                <iframe title="Source PDF Preview" src={dialog.previewPdfSrc} />
              ) : (
                <div className="matrix-editor-step-empty">PDF preview unavailable.</div>
              )}
            </div>
          )}
          <div className="matrix-editor-import-controls-pane">
            {!isXlsx ? (
              <>
                <div className="matrix-editor-import-controls-row">
                  <label>
                    <span>Page</span>
                    <input
                      disabled={readOnly || dialog.actionBusy}
                      value={dialog.locatorPage}
                      onChange={(event) => dialog.updateLocator({ page: event.target.value })}
                    />
                  </label>
                  <label>
                    <span>Table on page</span>
                    <input
                      disabled={readOnly || dialog.actionBusy}
                      value={dialog.locatorTableOnPage}
                      onChange={(event) =>
                        dialog.updateLocator({ tableOnPage: event.target.value })
                      }
                    />
                  </label>
                </div>
                <label>
                  <span>Table Title / Content Keyword</span>
                  <input
                    disabled={readOnly || dialog.actionBusy}
                    value={dialog.locatorKeyword}
                    onChange={(event) => dialog.updateLocator({ keyword: event.target.value })}
                  />
                </label>
                {dialog.importingPreview ? <p>Reparsing...</p> : null}
              </>
            ) : null}
            {dialog.lookupMessage ? (
              <p
                className={
                  dialog.lookupTone === "success"
                    ? "matrix-editor-import-status-success"
                    : dialog.lookupTone === "error"
                      ? "matrix-editor-import-status-error"
                      : ""
                }
              >
                {dialog.lookupMessage}
              </p>
            ) : null}
            {dialog.error ? <p className="error">{dialog.error}</p> : null}
            <footer className="matrix-editor-import-controls-footer">
              <button
                className="matrix-editor-import-secondary-button"
                type="button"
                disabled={dialog.actionBusy}
                onClick={dialog.close}
              >
                Cancel
              </button>
              <button
                className="matrix-editor-import-commit-button"
                type="button"
                disabled={
                  readOnly ||
                  dialog.actionBusy ||
                  !dialog.preview ||
                  dialog.preview.groups.length === 0
                }
                onClick={() => void dialog.replace()}
              >
                Replace
              </button>
              <button className="matrix-editor-import-commit-button" type="button" disabled>
                Append
              </button>
            </footer>
          </div>
        </div>
      </article>
    </section>
  );
}
