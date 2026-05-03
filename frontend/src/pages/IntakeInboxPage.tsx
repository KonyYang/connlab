import { useEffect, useMemo, useRef, useState, type ChangeEvent, type ReactElement } from "react";
import {
  getIntakeAssetPreview,
  importDirectWordApplicationForm,
  importMsgPackage,
  selectIntakeApplicationForm,
  type IntakeAsset,
  type IntakeAssetPreview,
  type IntakePackageImport
} from "../api/client";
import { UiIcon } from "../components/common/UiIcon";
import {
  EMPTY_INTAKE_SESSION,
  type IntakeSessionState
} from "../features/intake/intakeSession";
import "../intake-inbox.css";

type IntakeInboxPageProps = {
  session: IntakeSessionState;
  onSessionChange: (session: IntakeSessionState) => void;
  onOpenPackage: (packageId: string, caseId?: string | null) => void;
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

  async function handleDirectWordChange(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    setImporting(true);
    setImportError(null);
    try {
      const imported = await importDirectWordApplicationForm(file);
      const firstWord = imported.assets.find(isWordAsset) ?? imported.assets[0] ?? null;
      onSessionChange({
        packageImport: imported,
        selectedAssetId: firstWord?.asset_id ?? null,
        selectedWordAssetId: firstWord?.asset_id ?? null,
        selectedPrecheckCaseId: null,
        sourceMode: "word",
        directWordName: file.name
      });
    } catch (error) {
      onSessionChange(EMPTY_INTAKE_SESSION);
      setImportError(error instanceof Error ? error.message : "Direct application form import failed.");
    } finally {
      setImporting(false);
    }
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
          <p>Step 1 of 4: Intake</p>
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
                onChange={(event) => void handleDirectWordChange(event)}
              />
              <button
                className={sourceMode === "msg" ? "source-button source-button-active" : "source-button"}
                disabled={importing}
                type="button"
                onClick={() => msgInputRef.current?.click()}
              >
                <UiIcon name="outlook" />
                {importing ? "Importing from Outlook..." : "Import from Outlook"}
              </button>
              <button
                className={sourceMode === "word" ? "source-button source-button-active" : "source-button"}
                type="button"
                onClick={() => wordInputRef.current?.click()}
              >
                <UiIcon name="upload" />
                {importing && sourceMode === "word" ? "Uploading application form..." : "Upload application form"}
              </button>
            </div>
            {importError ? <p className="intake-error">{importError}</p> : null}
          </section>

          <section className="intake-panel">
            <h3>Email information</h3>
            <dl className="email-info-list">
              <div>
                <dt>From</dt>
                <dd>{senderEmailText(packageImport)}</dd>
              </div>
              <div>
                <dt>Subject</dt>
                <dd>{packageImport?.subject || directWordName || "No subject"}</dd>
              </div>
              <div>
                <dt>Date</dt>
                <dd>{mailDateText(packageImport)}</dd>
              </div>
            </dl>
          </section>

          <section className="intake-panel intake-attachments-panel">
            <div className="attachments-heading">
              <h3>Attachments ({packageImport?.assets.length ?? 0})</h3>
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
                      onClick={() => {
                        onSessionChange({
                          ...session,
                          selectedAssetId: asset.asset_id,
                          selectedWordAssetId: word ? asset.asset_id : selectedWordAssetId,
                          selectedPrecheckCaseId: word ? null : session.selectedPrecheckCaseId
                        });
                      }}
                    >
                      <span className={`file-chip file-chip-${assetKind(asset)}`}>{assetKindLabel(asset)}</span>
                      <span className="attachment-name">
                        <strong>{asset.original_name}</strong>
                        <small>{attachmentRoleText(asset)}</small>
                      </span>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="attachment-empty">
                <UiIcon name="package" />
                <strong>No source imported</strong>
                <span>Import a .msg package or upload an application form.</span>
              </div>
            )}
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
        <span className="step-footer-guidance">
          {selectedApplicationForm
            ? `Application form: ${selectedApplicationForm.original_name}`
            : "Select a Word (.docx) file before continuing."}
        </span>
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
  if (preview.kind === "image") {
    return <ImageAttachmentPreview preview={preview} />;
  }
  if (preview.kind === "metadata_only" || preview.kind === "unsupported") {
    return <MetadataOnlyPreview preview={preview} />;
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

function ImageAttachmentPreview({
  preview
}: {
  preview: IntakeAssetPreview;
}): ReactElement {
  if (!preview.image_data_url) {
    return <MetadataOnlyPreview preview={preview} />;
  }
  return (
    <div className="image-attachment-preview">
      <div className="docx-preview-title">
        <span className="file-chip file-chip-image">IMG</span>
        <div>
          <strong>{preview.title}</strong>
          <span>{preview.metadata.original_name}</span>
        </div>
      </div>
      <div className="image-preview-frame">
        <img alt={preview.metadata.original_name} src={preview.image_data_url} />
      </div>
    </div>
  );
}

function MetadataOnlyPreview({
  preview
}: {
  preview: IntakeAssetPreview;
}): ReactElement {
  return (
    <div className="metadata-only-preview">
      <div className="docx-preview-title">
        <span className={`file-chip file-chip-${assetKindFromPreview(preview)}`}>{assetKindLabelFromPreview(preview)}</span>
        <div>
          <strong>{preview.title}</strong>
          <span>{preview.metadata.original_name}</span>
        </div>
      </div>
      <p>{preview.message ?? "Attachment metadata is available. Structured rendering is not implemented for this file type."}</p>
      <dl className="metadata-preview-grid">
        {preview.fields.map((field) => (
          <div key={`${field.label}-${field.value}`}>
            <dt>{field.label}</dt>
            <dd>{field.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
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

function senderEmailText(item: IntakePackageImport | null): string {
  if (!item) {
    return "No email imported";
  }
  return item.sender_email || "No sender email";
}

function mailDateText(item: IntakePackageImport | null): string {
  if (!item) {
    return "Waiting for source";
  }
  if (!item.received_at) {
    return "Direct upload";
  }
  const date = new Date(item.received_at);
  if (Number.isNaN(date.getTime())) {
    return item.received_at;
  }
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  });
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

function assetKindFromPreview(preview: IntakeAssetPreview): string {
  return assetKind({
    asset_id: preview.metadata.asset_id,
    original_name: preview.metadata.original_name,
    extension: preview.metadata.extension,
    mime_type: preview.metadata.mime_type,
    size_bytes: preview.metadata.size_bytes,
    asset_role: preview.metadata.asset_role
  });
}

function assetKindLabelFromPreview(preview: IntakeAssetPreview): string {
  const kind = assetKindFromPreview(preview);
  if (kind === "word") {
    return "W";
  }
  if (kind === "pdf") {
    return "PDF";
  }
  if (kind === "image") {
    return "IMG";
  }
  return preview.metadata.extension.replace(".", "").toUpperCase() || "FILE";
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

function attachmentRoleText(asset: IntakeAsset): string {
  if (isWordAsset(asset)) {
    return "Application form candidate";
  }
  if (asset.asset_role && asset.asset_role !== "source_email") {
    return asset.asset_role.replaceAll("_", " ");
  }
  return "Supporting attachment";
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
  if (preview?.kind === "image") {
    return "Image preview";
  }
  if (preview?.kind === "metadata_only" || preview?.kind === "unsupported") {
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
