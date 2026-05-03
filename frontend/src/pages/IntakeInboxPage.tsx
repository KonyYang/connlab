import { useEffect, useMemo, useRef, useState, type ChangeEvent, type ReactElement } from "react";
import {
  getIntakeAssetPreview,
  importMsgPackage,
  selectIntakeApplicationForm,
  type IntakeAsset,
  type IntakeAssetPreview,
  type IntakePackageImport
} from "../api/client";
import { UiIcon } from "../components/common/UiIcon";
import "../intake-inbox.css";

type IntakeInboxPageProps = {
  session: IntakeSessionState;
  onSessionChange: (session: IntakeSessionState) => void;
  onOpenPackage: (packageId: string, caseId?: string | null) => void;
};

type SourceMode = "msg" | "word";

export type IntakeSessionState = {
  packageImport: IntakePackageImport | null;
  selectedAssetId: string | null;
  selectedWordAssetId: string | null;
  selectedPrecheckCaseId: string | null;
  sourceMode: SourceMode;
  directWordName: string | null;
};

export const EMPTY_INTAKE_SESSION: IntakeSessionState = {
  packageImport: null,
  selectedAssetId: null,
  selectedWordAssetId: null,
  selectedPrecheckCaseId: null,
  sourceMode: "msg",
  directWordName: null
};

export function IntakeInboxPage({
  session,
  onSessionChange,
  onOpenPackage
}: IntakeInboxPageProps): ReactElement {
  const msgInputRef = useRef<HTMLInputElement | null>(null);
  const wordInputRef = useRef<HTMLInputElement | null>(null);
  const [importing, setImporting] = useState(false);
  const [preparingPrecheck, setPreparingPrecheck] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [preview, setPreview] = useState<IntakeAssetPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const { packageImport, selectedAssetId, selectedWordAssetId, sourceMode, directWordName } = session;

  const selectedAsset = useMemo(
    () => packageImport?.assets.find((asset) => asset.asset_id === selectedAssetId) ?? null,
    [packageImport, selectedAssetId]
  );
  const selectedApplicationForm = useMemo(
    () => packageImport?.assets.find((asset) => asset.asset_id === selectedWordAssetId) ?? null,
    [packageImport, selectedWordAssetId]
  );

  useEffect(() => {
    if (!selectedAssetId) {
      setPreview(null);
      setPreviewError(null);
      setPreviewLoading(false);
      return;
    }
    let cancelled = false;
    setPreviewLoading(true);
    setPreviewError(null);
    getIntakeAssetPreview(selectedAssetId)
      .then((result) => {
        if (!cancelled) {
          setPreview(result);
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setPreview(null);
          setPreviewError(error instanceof Error ? error.message : "Attachment preview failed.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setPreviewLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [selectedAssetId]);

  async function handleMsgFileChange(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    setImporting(true);
    setImportError(null);
    try {
      const imported = await importMsgPackage(file);
      const firstWord = imported.assets.find(isWordAsset) ?? null;
      onSessionChange({
        packageImport: imported,
        selectedAssetId: firstWord?.asset_id ?? imported.assets[0]?.asset_id ?? null,
        selectedWordAssetId: firstWord?.asset_id ?? null,
        selectedPrecheckCaseId: null,
        sourceMode: "msg",
        directWordName: null
      });
    } catch (error) {
      onSessionChange(EMPTY_INTAKE_SESSION);
      setImportError(error instanceof Error ? error.message : "Import failed.");
    } finally {
      setImporting(false);
    }
  }

  function handleDirectWordChange(event: ChangeEvent<HTMLInputElement>): void {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    onSessionChange({
      packageImport: null,
      selectedAssetId: null,
      selectedWordAssetId: null,
      selectedPrecheckCaseId: null,
      sourceMode: "word",
      directWordName: file.name
    });
    setImportError("Direct application form import is visible here but not wired to backend in this task.");
  }

  async function handleContinueToPrecheck(): Promise<void> {
    if (!packageImport || !selectedApplicationForm) {
      return;
    }
    setPreparingPrecheck(true);
    setImportError(null);
    try {
      const selection = await selectIntakeApplicationForm(
        packageImport.package_id,
        selectedApplicationForm.asset_id
      );
      onSessionChange({
        ...session,
        selectedPrecheckCaseId: selection.case_id,
        selectedWordAssetId: selection.selected_form_asset_id,
        selectedAssetId: selection.selected_form_asset_id
      });
      onOpenPackage(packageImport.package_id, selection.case_id);
    } catch (error) {
      setImportError(error instanceof Error ? error.message : "Unable to prepare Precheck review case.");
    } finally {
      setPreparingPrecheck(false);
    }
  }

  return (
    <section className="intake-workflow">
      <div className="new-project-heading">
        <div>
          <h2>New Project</h2>
          <p>Create a project from email or application form.</p>
        </div>
      </div>

      <NewProjectStepper />

      <div className="intake-step-grid">
        <aside className="intake-left-stack">
          <section className="intake-panel">
            <h3>Import source</h3>
            <div className="import-source-actions">
              <input
                ref={msgInputRef}
                accept=".msg"
                className="file-input-hidden"
                type="file"
                onChange={(event) => void handleMsgFileChange(event)}
              />
              <input
                ref={wordInputRef}
                accept=".doc,.docx"
                className="file-input-hidden"
                type="file"
                onChange={handleDirectWordChange}
              />
              <button
                className={sourceMode === "msg" ? "source-button source-button-active" : "source-button"}
                disabled={importing}
                type="button"
                onClick={() => msgInputRef.current?.click()}
              >
                <UiIcon name="package" />
                {importing ? "Importing email..." : "Import email package"}
              </button>
              <button
                className={sourceMode === "word" ? "source-button source-button-active" : "source-button"}
                type="button"
                onClick={() => wordInputRef.current?.click()}
              >
                <UiIcon name="folder" />
                Upload application form
              </button>
            </div>
            {importError ? <p className="intake-error">{importError}</p> : null}
          </section>

          <section className="intake-panel">
            <h3>Email information</h3>
            <dl className="email-info-list">
              <div>
                <dt>Sender</dt>
                <dd>{senderText(packageImport)}</dd>
              </div>
              <div>
                <dt>Subject</dt>
                <dd>{packageImport?.subject || directWordName || "No email imported"}</dd>
              </div>
              <div>
                <dt>Received</dt>
                <dd>{packageImport ? "Imported now" : "Waiting for package"}</dd>
              </div>
              <div>
                <dt>Source file</dt>
                <dd>{packageImport?.source_original_name || directWordName || "Not selected"}</dd>
              </div>
            </dl>
          </section>

          <section className="intake-panel intake-attachments-panel">
            <div className="attachments-heading">
              <h3>Attachments ({packageImport?.assets.length ?? 0})</h3>
              <span>Choose one Word document as the application form.</span>
            </div>
            {packageImport ? (
              <div className="attachment-list" role="list">
                {packageImport.assets.map((asset) => {
                  const word = isWordAsset(asset);
                  const selected = asset.asset_id === selectedAssetId;
                  return (
                    <button
                      className={selected ? "attachment-row attachment-row-active" : "attachment-row"}
                      key={asset.asset_id}
                      type="button"
                      onClick={() => onSessionChange({ ...session, selectedAssetId: asset.asset_id })}
                    >
                      <span className="attachment-selector">
                        {word ? (
                          <input
                            aria-label={`Use ${asset.original_name} as application form`}
                            checked={asset.asset_id === selectedWordAssetId}
                            name="application-form-asset"
                            type="radio"
                            onChange={() => {
                              onSessionChange({
                                ...session,
                                selectedAssetId: asset.asset_id,
                                selectedWordAssetId: asset.asset_id,
                                selectedPrecheckCaseId: null
                              });
                            }}
                            onClick={(event) => event.stopPropagation()}
                          />
                        ) : (
                          <span className="attachment-spacer" />
                        )}
                      </span>
                      <span className={`file-chip file-chip-${assetKind(asset)}`}>{assetKindLabel(asset)}</span>
                      <span className="attachment-name">{asset.original_name}</span>
                      <span className="attachment-type">{assetTypeText(asset)}</span>
                      <span className="attachment-size">{formatBytes(asset.size_bytes)}</span>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="attachment-empty">
                <UiIcon name="package" />
                <strong>No email package imported</strong>
                <span>Import one Outlook `.msg` file to list its attachments.</span>
              </div>
            )}
            <p className="attachment-guidance">
              Select a Word (.docx) file as the application form before continuing.
            </p>
          </section>
        </aside>

        <section className="attachment-details-panel">
          <div className="attachment-details-heading">
            <div className={`detail-file-icon detail-file-icon-${selectedAsset ? assetKind(selectedAsset) : "empty"}`}>
              {selectedAsset ? assetKindLabel(selectedAsset) : "--"}
            </div>
            <div>
              <h3>Attachment details</h3>
              <strong>{selectedAsset?.original_name ?? directWordName ?? "Select an attachment"}</strong>
              <span>{selectedAsset ? assetTypeText(selectedAsset) : "Attachment metadata and preview appear here."}</span>
            </div>
            <div className="details-actions">
              <button className="secondary-action" disabled type="button">
                Download
              </button>
              <button className="toolbar-button toolbar-icon-button" disabled type="button">
                <UiIcon name="columns" />
              </button>
            </div>
          </div>

          <dl className="attachment-meta-grid">
            <div>
              <dt>Preview</dt>
              <dd>{previewStatusText(selectedAsset, preview, previewLoading, previewError)}</dd>
            </div>
            <div>
              <dt>File size</dt>
              <dd>{selectedAsset ? formatBytes(selectedAsset.size_bytes) : "No file selected"}</dd>
            </div>
            <div>
              <dt>Role</dt>
              <dd>{selectedAsset?.asset_role ?? "Waiting"}</dd>
            </div>
          </dl>

          <div className="document-preview">
            <AttachmentPreview
              asset={selectedAsset}
              error={previewError}
              loading={previewLoading}
              preview={preview}
            />
          </div>
        </section>
      </div>

      <div className="step-footer">
        <button className="secondary-action" disabled type="button">Back</button>
        <span>Step 1 of 4</span>
        <button
          className="primary-action continue-action"
          disabled={!packageImport || !selectedApplicationForm || preparingPrecheck}
          type="button"
          onClick={() => void handleContinueToPrecheck()}
        >
          {preparingPrecheck ? "Preparing Precheck..." : "Continue to Precheck"}
          <span aria-hidden="true">&gt;</span>
        </button>
      </div>
    </section>
  );
}

function AttachmentPreview({
  asset,
  error,
  loading,
  preview
}: {
  asset: IntakeAsset | null;
  error: string | null;
  loading: boolean;
  preview: IntakeAssetPreview | null;
}): ReactElement {
  if (!asset) {
    return (
      <div className="preview-empty">
        <UiIcon name="projects" />
        <strong>Attachment details</strong>
        <span>Select an attachment from the left list to inspect it here.</span>
      </div>
    );
  }
  if (loading) {
    return (
      <div className="preview-empty preview-loading">
        <UiIcon name="refresh" />
        <strong>Loading preview</strong>
        <span>Reading the selected attachment from the intake package.</span>
      </div>
    );
  }
  if (error) {
    return (
      <div className="preview-empty preview-error-state">
        <UiIcon name="help" />
        <strong>Preview unavailable</strong>
        <span>{error}</span>
      </div>
    );
  }
  if (!preview) {
    return (
      <div className="preview-empty">
        <UiIcon name="projects" />
        <strong>No preview loaded</strong>
        <span>Select another attachment or import the email package again.</span>
      </div>
    );
  }
  if (preview.kind !== "docx_application_form") {
    return (
      <div className="preview-empty unsupported-preview">
        <UiIcon name="package" />
        <strong>{preview.title}</strong>
        <span>{preview.message ?? "Structured preview is not available for this attachment type."}</span>
      </div>
    );
  }
  return <DocxApplicationPreview preview={preview} />;
}

function DocxApplicationPreview({
  preview
}: {
  preview: IntakeAssetPreview;
}): ReactElement {
  const sampleTable = preview.tables.find((table) => table.title === "Test Sample Information");
  const otherTables = preview.tables.filter((table) => table.title !== "Test Sample Information");
  return (
    <div className="docx-structured-preview">
      <div className="docx-preview-title">
        <span className="file-chip file-chip-word">W</span>
        <div>
          <strong>{preview.title}</strong>
          <span>{preview.metadata.original_name}</span>
        </div>
      </div>
      {preview.warnings.length > 0 ? (
        <div className="preview-warning-list">
          {preview.warnings.map((warning) => <span key={warning}>{warning}</span>)}
        </div>
      ) : null}
      <dl className="docx-field-grid">
        {preview.fields.map((field) => (
          <div key={`${field.label}-${field.value}`}>
            <dt>{field.label}</dt>
            <dd>{field.value}</dd>
          </div>
        ))}
      </dl>
      {sampleTable ? <PreviewTableSection table={sampleTable} compact /> : null}
      {otherTables.map((table) => <PreviewTableSection key={table.title} table={table} />)}
    </div>
  );
}

function PreviewTableSection({
  compact,
  table
}: {
  compact?: boolean;
  table: IntakeAssetPreview["tables"][number];
}): ReactElement {
  return (
    <section className={compact ? "preview-table-section preview-table-section-compact" : "preview-table-section"}>
      <h4>{table.title}</h4>
      <div className="preview-table-scroll">
        <table>
          <thead>
            <tr>{table.headers.map((header) => <th key={header}>{header}</th>)}</tr>
          </thead>
          <tbody>
            {table.rows.map((row, rowIndex) => (
              <tr key={`${table.title}-${rowIndex}`}>
                {table.headers.map((header, index) => <td key={`${header}-${index}`}>{row[index] || ""}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function NewProjectStepper(): ReactElement {
  const steps = ["Intake", "Precheck", "LTR", "Folder"];
  return (
    <ol className="new-project-stepper" aria-label="New project steps">
      {steps.map((step, index) => (
        <li className={index === 0 ? "stepper-item stepper-item-active" : "stepper-item"} key={step}>
          <span>{index + 1}</span>
          <strong>{step}</strong>
        </li>
      ))}
    </ol>
  );
}

function senderText(item: IntakePackageImport | null): string {
  if (!item) {
    return "No email imported";
  }
  const sender = [item.sender_name, item.sender_email].filter(Boolean).join(" ");
  return sender || "Unknown sender";
}

function isWordAsset(asset: IntakeAsset | null): boolean {
  if (!asset) {
    return false;
  }
  return [".doc", ".docx"].includes(asset.extension.toLowerCase());
}

function assetKind(asset: IntakeAsset): string {
  const extension = asset.extension.toLowerCase();
  if (extension === ".doc" || extension === ".docx") {
    return "word";
  }
  if (extension === ".pdf") {
    return "pdf";
  }
  if ([".png", ".jpg", ".jpeg", ".tif", ".tiff"].includes(extension)) {
    return "image";
  }
  return "file";
}

function assetKindLabel(asset: IntakeAsset): string {
  const kind = assetKind(asset);
  if (kind === "word") {
    return "W";
  }
  if (kind === "pdf") {
    return "PDF";
  }
  if (kind === "image") {
    return "IMG";
  }
  return "FILE";
}

function assetTypeText(asset: IntakeAsset): string {
  if (isWordAsset(asset)) {
    return "Word Document";
  }
  if (asset.extension.toLowerCase() === ".pdf") {
    return "PDF Document";
  }
  return `${asset.extension.replace(".", "").toUpperCase()} Attachment`;
}

function previewStatusText(
  asset: IntakeAsset | null,
  preview: IntakeAssetPreview | null,
  loading: boolean,
  error: string | null
): string {
  if (!asset) {
    return "Waiting";
  }
  if (loading) {
    return "Loading";
  }
  if (error) {
    return "Preview error";
  }
  if (preview?.kind === "docx_application_form") {
    return "Structured Word preview";
  }
  if (preview?.kind === "unsupported") {
    return "Metadata only";
  }
  return "Ready";
}

function formatBytes(value: number): string {
  if (value >= 1024 * 1024) {
    return `${(value / 1024 / 1024).toFixed(1)} MB`;
  }
  if (value >= 1024) {
    return `${Math.round(value / 1024)} KB`;
  }
  return `${value} B`;
}
