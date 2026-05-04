import type { ReactElement } from "react";

import type { IntakeAsset, IntakeAssetPreview } from "../../api/client";
import { intakeAssetDownloadUrl } from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import {
  assetKindFromPreview,
  assetKindLabelFromPreview,
} from "./intakeSelectors";

type AttachmentPreviewPanelProps = {
  directWordName: string | null;
  error: string | null;
  loading: boolean;
  preview: IntakeAssetPreview | null;
  selectedAsset: IntakeAsset | null;
};

export function AttachmentPreviewPanel({
  error,
  loading,
  preview,
  selectedAsset,
}: AttachmentPreviewPanelProps): ReactElement {
  return (
    <section className="attachment-details-panel attachment-details-panel-compact">
      <div className="document-preview">
        <AttachmentPreview asset={selectedAsset} error={error} loading={loading} preview={preview} />
      </div>
    </section>
  );
}

function AttachmentPreviewActions({ assetId, originalName }: { assetId: string; originalName: string }): ReactElement {
  return (
    <div className="details-actions">
      <a
        className="secondary-action ui-secondary-action"
        href={intakeAssetDownloadUrl(assetId)}
        download={originalName}
      >
        Download
      </a>
    </div>
  );
}

function PreviewHeader({ asset }: { asset: IntakeAsset }): ReactElement {
  return (
    <div className="docx-preview-title docx-preview-title-with-actions">
      <span className="file-chip file-chip-file">FILE</span>
      <div>
        <span>{asset.original_name}</span>
      </div>
      <AttachmentPreviewActions assetId={asset.asset_id} originalName={asset.original_name} />
    </div>
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
      <div className="preview-loading-outer">
        <PreviewHeader asset={asset} />
        <div className="preview-empty preview-loading">
          <UiIcon name="refresh" />
          <strong>Loading preview</strong>
          <span>Reading the selected attachment from the intake package.</span>
        </div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="preview-error-outer">
        <PreviewHeader asset={asset} />
        <div className="preview-empty preview-error-state">
          <UiIcon name="help" />
          <strong>Preview unavailable</strong>
          <span>{error}</span>
        </div>
      </div>
    );
  }
  if (!preview) {
    return (
      <div className="preview-no-preview-outer">
        <PreviewHeader asset={asset} />
        <div className="preview-empty">
          <UiIcon name="projects" />
          <strong>No preview loaded</strong>
          <span>Select another attachment or import the email package again.</span>
        </div>
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
    return <MetadataOnlyPreview preview={preview} />;
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
      <div className="docx-preview-title docx-preview-title-with-actions">
        <span className="file-chip file-chip-image">IMG</span>
        <div>
          <strong className="ui-preview-title">{preview.title}</strong>
          <span>{preview.metadata.original_name}</span>
        </div>
        <AttachmentPreviewActions assetId={preview.metadata.asset_id} originalName={preview.metadata.original_name} />
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
      <div className="docx-preview-title docx-preview-title-with-actions">
        <span className={`file-chip file-chip-${assetKindFromPreview(preview)}`}>{assetKindLabelFromPreview(preview)}</span>
        <div>
          <strong className="ui-preview-title">{preview.title}</strong>
          <span>{preview.metadata.original_name}</span>
        </div>
        <AttachmentPreviewActions assetId={preview.metadata.asset_id} originalName={preview.metadata.original_name} />
      </div>
      <p>{preview.message ?? "Attachment metadata is available. Structured rendering is not implemented for this file type."}</p>
    </div>
  );
}

const FORM_VERSION_LABELS = new Set(["Form No.", "Revision"]);

function businessPreviewFields(preview: IntakeAssetPreview): IntakeAssetPreview["fields"] {
  return preview.fields.filter((field) => !FORM_VERSION_LABELS.has(field.label));
}

function formVersionText(preview: IntakeAssetPreview): string | null {
  const formNo = preview.fields.find((field) => field.label === "Form No.")?.value.trim();
  const revision = preview.fields.find((field) => field.label === "Revision")?.value.trim();

  if (formNo && revision) {
    return `${formNo} / Rev ${revision}`;
  }
  if (formNo) {
    return formNo;
  }
  if (revision) {
    return `Rev ${revision}`;
  }
  return null;
}

function DocxApplicationPreview({
  preview,
}: {
  preview: IntakeAssetPreview;
}): ReactElement {
  const sampleTable = preview.tables.find((table) => table.title === "Test Sample Information");
  const requestedTestingTable = preview.tables.find(
    (table) => table.title === "Description of Requested Testing" || table.title === "Requested Testing",
  );
  const additionalInformationTable = preview.tables.find((table) => table.title === "Additional Information");
  const otherTables = preview.tables.filter(
    (table) =>
      table.title !== "Test Sample Information" &&
      table.title !== "Description of Requested Testing" &&
      table.title !== "Requested Testing" &&
      table.title !== "Additional Information",
  );
  const fields = businessPreviewFields(preview);
  const versionText = formVersionText(preview);
  return (
    <div className="docx-structured-preview">
      <div className="docx-preview-title docx-preview-title-with-actions">
        <span className="file-chip file-chip-word">W</span>
        <div>
          <strong className="ui-preview-title">{preview.title}</strong>
          <span>{preview.metadata.original_name}</span>
        </div>
        <AttachmentPreviewActions assetId={preview.metadata.asset_id} originalName={preview.metadata.original_name} />
      </div>
      {preview.warnings.length > 0 ? (
        <div className="preview-warning-list">
          {preview.warnings.map((warning) => <span key={warning}>{warning}</span>)}
        </div>
      ) : null}
      {fields.length > 0 ? (
        <dl className="docx-field-grid">
          {fields.map((field) => (
            <div key={`${field.label}-${field.value}`}>
              <dt>{field.label}</dt>
              <dd>{field.value}</dd>
            </div>
          ))}
          {versionText ? (
            <div>
              <dt>Form No./Revision</dt>
              <dd>{versionText}</dd>
            </div>
          ) : null}
        </dl>
      ) : null}
      {sampleTable ? <PreviewTableSection table={sampleTable} compact /> : null}
      <RequestedTestingPreviewSection
        additionalInformationTable={additionalInformationTable}
        requestedTestingTable={requestedTestingTable}
      />
      {otherTables.map((table) => <PreviewTableSection key={table.title} table={table} />)}
    </div>
  );
}

function RequestedTestingPreviewSection({
  requestedTestingTable,
  additionalInformationTable,
}: {
  requestedTestingTable?: IntakeAssetPreview["tables"][number];
  additionalInformationTable?: IntakeAssetPreview["tables"][number];
}): ReactElement {
  const additionalInformation = additionalInformationTable?.rows
    .map((row) => row.filter(Boolean).join(" "))
    .filter(Boolean)
    .join("\n");

  return (
    <div className="attachment-requested-testing-stack">
      {requestedTestingTable ? <PreviewTableSection table={requestedTestingTable} /> : null}
      <section className="attachment-additional-information-section">
        <h4 className="ui-section-title">Additional Information</h4>
        <div className="attachment-additional-information-block">
          {additionalInformation || "No additional information extracted from the selected application form."}
        </div>
      </section>
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
      <h4 className="ui-section-title">{table.title}</h4>
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
