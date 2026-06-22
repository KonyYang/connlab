import { useState, type ReactElement } from "react";
import {
  commitLtrWorkbookBasicInformationSync,
  previewLtrWorkbookBasicInformationSync,
  type LtrWorkbookBasicInformationSyncCommit,
  type LtrWorkbookBasicInformationSyncPreview,
  type ProjectBasicInformationResponse,
} from "../../api/client";
import {
  selectBasicInformationMissingLabels,
  selectBasicInformationStatusLabel,
  selectChangedSourceFieldLabels,
  selectConfirmedViewItems,
  selectWorkbenchSummaryItems,
} from "./basicInformationSelectors";

type ProjectBasicInformationSummaryCardProps = {
  projectId: string;
  basicInformation: ProjectBasicInformationResponse | null;
  loading: boolean;
  error: string | null;
};

export function ProjectBasicInformationSummaryCard({
  projectId,
  basicInformation,
  loading,
  error,
}: ProjectBasicInformationSummaryCardProps): ReactElement {
  const [expanded, setExpanded] = useState(false);
  const [ltrPreview, setLtrPreview] =
    useState<LtrWorkbookBasicInformationSyncPreview | null>(null);
  const [ltrPreviewLoading, setLtrPreviewLoading] = useState(false);
  const [ltrCommitLoading, setLtrCommitLoading] = useState(false);
  const [ltrSyncError, setLtrSyncError] = useState<string | null>(null);
  const [ltrSyncResult, setLtrSyncResult] =
    useState<LtrWorkbookBasicInformationSyncCommit | null>(null);
  const statusLabel = selectBasicInformationStatusLabel(basicInformation);
  const missingLabels = selectBasicInformationMissingLabels(basicInformation);
  const changedLabels = selectChangedSourceFieldLabels(basicInformation);
  const summaryItems = selectWorkbenchSummaryItems(basicInformation);
  const confirmedItems = selectConfirmedViewItems(basicInformation);
  const hasConfirmed = Boolean(basicInformation?.latest_confirmed);
  const canUpdateLtr = basicInformation?.status === "confirmed" && hasConfirmed;
  const showStatusBadge = loading || basicInformation?.status !== "confirmed";
  const canCommitLtrPreview =
    ltrPreview?.status === "ready" &&
    ltrPreview.confirmed_basic_information_version !== null &&
    ltrPreview.confirmed_basic_information_source_signature_hash !== null;

  async function handlePreviewLtrSync(): Promise<void> {
    if (!canUpdateLtr) {
      return;
    }
    setLtrPreviewLoading(true);
    setLtrSyncError(null);
    setLtrSyncResult(null);
    try {
      const preview = await previewLtrWorkbookBasicInformationSync(projectId);
      setLtrPreview(preview);
    } catch (previewError) {
      setLtrPreview(null);
      setLtrSyncError(toLtrSyncOperatorMessage(previewError));
    } finally {
      setLtrPreviewLoading(false);
    }
  }

  async function handleCommitLtrSync(): Promise<void> {
    if (!canCommitLtrPreview || !ltrPreview) {
      return;
    }
    const expectedVersion = ltrPreview.confirmed_basic_information_version;
    const expectedSourceHash = ltrPreview.confirmed_basic_information_source_signature_hash;
    if (expectedVersion === null || expectedSourceHash === null) {
      return;
    }
    setLtrCommitLoading(true);
    setLtrSyncError(null);
    setLtrSyncResult(null);
    try {
      const result = await commitLtrWorkbookBasicInformationSync(projectId, {
        operator_confirmed: true,
        preview_acknowledged: true,
        expected_confirmed_basic_information_version: expectedVersion,
        expected_confirmed_basic_information_source_signature_hash: expectedSourceHash,
      });
      setLtrSyncResult(result);
      setLtrPreview(null);
    } catch (commitError) {
      setLtrSyncError(toLtrSyncOperatorMessage(commitError));
    } finally {
      setLtrCommitLoading(false);
    }
  }

  return (
    <section className="runtime-console-basic-information" aria-label="Project Basic Information">
      <div className="runtime-console-card-header">
        <p className="eyebrow">Basic Information</p>
        {showStatusBadge ? (
          <strong className={`runtime-console-basic-information-status status-${basicInformation?.status ?? "none"}`}>
            {loading ? "Loading" : statusLabel}
          </strong>
        ) : null}
      </div>
      {error ? <p className="runtime-console-basic-information-error">{error}</p> : null}
      {!loading && !error && !hasConfirmed ? (
        <>
          <p>Confirm from Basic Information</p>
          {missingLabels.length > 0 ? (
            <div className="runtime-console-basic-information-muted">
              <span>Missing</span>
              <ul>
                {missingLabels.map((label) => (
                  <li key={label}>{label}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </>
      ) : null}
      {!loading && !error && basicInformation?.status === "needs_review" ? (
        <>
          <p className="runtime-console-basic-information-warning">
            {changedLabels.length} source field{changedLabels.length === 1 ? "" : "s"} changed
          </p>
          <p>Confirm from Basic Information</p>
        </>
      ) : null}
      {!loading && !error && hasConfirmed ? (
        <>
          <dl className="runtime-console-basic-information-list is-summary">
            {summaryItems.map((item) => (
              <div key={item.key}>
                <dt>{item.label}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
        </>
      ) : null}
      {!loading && !error ? (
        <div className="runtime-console-basic-information-actions">
          {hasConfirmed ? (
            <button type="button" onClick={() => setExpanded((value) => !value)}>
              {expanded ? "Hide" : "View"}
            </button>
          ) : null}
          <button
            type="button"
            onClick={handlePreviewLtrSync}
            disabled={!canUpdateLtr || ltrPreviewLoading || ltrCommitLoading}
            title={
              canUpdateLtr
                ? "Preview the public-drive LTR workbook update."
                : "Confirm Basic Information before updating LTR."
            }
          >
            {ltrPreviewLoading ? "Previewing..." : "Update LTR"}
          </button>
        </div>
      ) : null}
      {!loading && !error ? (
        <LtrWorkbookSyncPanel
          preview={ltrPreview}
          previewLoading={ltrPreviewLoading}
          commitLoading={ltrCommitLoading}
          error={ltrSyncError}
          result={ltrSyncResult}
          canCommit={canCommitLtrPreview}
          onCommit={handleCommitLtrSync}
          onCancel={() => {
            setLtrPreview(null);
            setLtrSyncError(null);
          }}
        />
      ) : null}
      {!loading && !error && hasConfirmed && expanded ? (
        <div className="runtime-console-basic-information-expanded">
          <strong>All confirmed fields</strong>
          <dl className="runtime-console-basic-information-list">
            {confirmedItems.map((item) => (
              <div key={item.key}>
                <dt>{item.label}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      ) : null}
    </section>
  );
}

type LtrWorkbookSyncPanelProps = {
  preview: LtrWorkbookBasicInformationSyncPreview | null;
  previewLoading: boolean;
  commitLoading: boolean;
  error: string | null;
  result: LtrWorkbookBasicInformationSyncCommit | null;
  canCommit: boolean;
  onCommit: () => void;
  onCancel: () => void;
};

function LtrWorkbookSyncPanel({
  preview,
  previewLoading,
  commitLoading,
  error,
  result,
  canCommit,
  onCommit,
  onCancel,
}: LtrWorkbookSyncPanelProps): ReactElement | null {
  if (!previewLoading && !error && !preview && !result) {
    return null;
  }

  const targetLabel =
    preview?.target_sheet && preview.target_row
      ? `${preview.target_sheet} row ${preview.target_row}`
      : "-";
  const isBlocked = preview?.status !== "ready";

  return (
    <div className="runtime-console-ltr-sync-panel" aria-live="polite">
      {previewLoading ? <p>Loading LTR workbook preview...</p> : null}
      {error ? (
        <p className="runtime-console-ltr-sync-error" role="alert">
          {error}
        </p>
      ) : null}
      {result ? (
        <div className="runtime-console-ltr-sync-result">
          <p>
            LTR workbook updated: {result.sheet_name} row {result.row_number}. Backup retained
            automatically.
          </p>
        </div>
      ) : null}
      {preview && !previewLoading ? (
        <>
          <strong>
            {isBlocked ? "LTR workbook update is blocked" : "LTR workbook update preview"}
          </strong>
          <dl className="runtime-console-ltr-sync-context">
            <div>
              <dt>Workbook</dt>
              <dd>{preview.workbook_path ?? "-"}</dd>
            </div>
            <div>
              <dt>Target row</dt>
              <dd>{targetLabel}</dd>
            </div>
            <div>
              <dt>LTR</dt>
              <dd>{preview.ltr_number}</dd>
            </div>
          </dl>
          {preview.blockers.length > 0 ? (
            <ul className="runtime-console-ltr-sync-list is-blocked">
              {preview.blockers.map((blocker) => (
                <li key={blocker}>{blocker}</li>
              ))}
            </ul>
          ) : null}
          {preview.warnings.length > 0 ? (
            <ul className="runtime-console-ltr-sync-list">
              {preview.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          ) : null}
          {!isBlocked ? (
            <>
              <p className="runtime-console-ltr-sync-note">
                Review the current LTR workbook row before updating it.
              </p>
              <table className="runtime-console-ltr-sync-comparison">
                <thead>
                  <tr>
                    <th scope="col">Field</th>
                    <th scope="col">Current LTR workbook</th>
                    <th scope="col">Value to write</th>
                  </tr>
                </thead>
                <tbody>
                  {preview.comparison_values.map((value) => (
                    <tr key={value.field_name}>
                      <th scope="row">{value.label}</th>
                      <td>{formatPreviewValue(value.current_value)}</td>
                      <td>{formatPreviewValue(value.pending_value)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          ) : null}
          <div className="runtime-console-ltr-sync-actions">
            {!isBlocked ? (
              <button
                type="button"
                onClick={onCommit}
                disabled={!canCommit || commitLoading}
              >
                {commitLoading ? "Updating..." : "Confirm update"}
              </button>
            ) : null}
            <button type="button" onClick={onCancel} disabled={commitLoading}>
              Close preview
            </button>
          </div>
        </>
      ) : null}
    </div>
  );
}

function formatPreviewValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return JSON.stringify(value);
}

function toLtrSyncOperatorMessage(error: unknown): string {
  const rawMessage = error instanceof Error ? error.message : String(error);
  const message = rawMessage.toLowerCase();

  if (
    message.includes("changed after preview") ||
    message.includes("stale") ||
    message.includes("source signature") ||
    message.includes("version")
  ) {
    return "Basic Information changed after preview. Refresh before updating LTR.";
  }
  if (
    message.includes("locked") ||
    message.includes("permission denied") ||
    message.includes("being used") ||
    message.includes("access is denied")
  ) {
    return "The LTR workbook appears to be open or locked. Close it and retry.";
  }
  if (message.includes("not found") || message.includes("registered ltr row")) {
    return "The registered LTR row was not found in the configured workbook.";
  }
  return "Unable to update the LTR workbook. Check the setup path and try again.";
}
