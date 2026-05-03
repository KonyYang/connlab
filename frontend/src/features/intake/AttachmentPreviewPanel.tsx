import type { ReactElement } from "react";

import type { IntakeAsset, IntakeAssetPreview } from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import {
  assetKind,
  assetKindFromPreview,
  assetKindLabel,
  assetKindLabelFromPreview,
  assetTypeText,
  formatBytes,
  previewStatusText,
} from "./intakeSelectors";

type AttachmentPreviewPanelProps = {
  directWordName: string | null;
  error: string | null;
  loading: boolean;
  preview: IntakeAssetPreview | null;
  selectedAsset: IntakeAsset | null;
};

export function AttachmentPreviewPanel({
  directWordName,
  error,
  loading,
  preview,
  selectedAsset,
}: AttachmentPreviewPanelProps): ReactElement {
  return (
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
          <dd>{previewStatusText(selectedAsset, preview, loading, error)}</dd>
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
        <AttachmentPreview asset={selectedAsset} error={error} loading={loading} preview={preview} />
      </div>
    </section>
  );
}

function AttachmentPreview({
  asset,
  error,
  loading,
  preview,
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
  preview,
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
  preview,
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
  preview,
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
  table,
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
