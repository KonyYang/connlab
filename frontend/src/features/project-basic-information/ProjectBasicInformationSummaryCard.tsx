import { useState, type ReactElement } from "react";
import {
  commitLtrWorkbookBasicInformationSync,
  openLtrWorkbookBasicInformationSyncReadonly,
  previewLtrWorkbookBasicInformationSync,
  type LtrWorkbookBasicInformationSyncCommit,
  type LtrWorkbookBasicInformationSyncPreview,
  type ProjectBasicInformationResponse,
} from "../../api/client";
import {
  selectBasicInformationMissingLabels,
  selectBasicInformationStatusLabel,
  selectChangedSourceFieldLabels,
} from "./basicInformationSelectors";

type ProjectBasicInformationSummaryCardProps = {
  projectId: string;
  basicInformation: ProjectBasicInformationResponse | null;
  registeredLtrNumber?: string | null;
  loading: boolean;
  error: string | null;
};

export function ProjectBasicInformationSummaryCard({
  projectId,
  basicInformation,
  registeredLtrNumber = null,
  loading,
  error,
}: ProjectBasicInformationSummaryCardProps): ReactElement {
  const [ltrPreview, setLtrPreview] =
    useState<LtrWorkbookBasicInformationSyncPreview | null>(null);
  const [ltrPreviewLoading, setLtrPreviewLoading] = useState(false);
  const [ltrCommitLoading, setLtrCommitLoading] = useState(false);
  const [ltrOpenLoading, setLtrOpenLoading] = useState(false);
  const [ltrSyncError, setLtrSyncError] = useState<string | null>(null);
  const [ltrSyncResult, setLtrSyncResult] =
    useState<LtrWorkbookBasicInformationSyncCommit | null>(null);
  const statusLabel = selectBasicInformationStatusLabel(basicInformation);
  const missingLabels = selectBasicInformationMissingLabels(basicInformation);
  const changedLabels = selectChangedSourceFieldLabels(basicInformation);
  const hasConfirmed = Boolean(basicInformation?.latest_confirmed);
  const hasRegisteredLtr = Boolean(registeredLtrNumber);
  const canUpdateLtr = basicInformation?.status === "confirmed" && hasConfirmed;
  const canPreviewLtr = canUpdateLtr || hasRegisteredLtr;
  const showStatusBadge = loading || basicInformation?.status !== "confirmed";
  const hasLtrPreviewChanges = Boolean(
    ltrPreview?.comparison_values.some((value) => value.changed)
  );
  const canCommitLtrPreview =
    ltrPreview?.status === "ready" &&
    ltrPreview.confirmed_basic_information_version !== null &&
    ltrPreview.confirmed_basic_information_source_signature_hash !== null &&
    hasLtrPreviewChanges;

  async function handlePreviewLtrSync(): Promise<void> {
    if (!canPreviewLtr) {
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

  async function handleOpenLtrWorkbookReadonly(): Promise<void> {
    if (ltrPreview?.status !== "ready" || !ltrPreview.workbook_path) {
      return;
    }
    setLtrOpenLoading(true);
    setLtrSyncError(null);
    try {
      await openLtrWorkbookBasicInformationSyncReadonly(projectId);
    } catch (openError) {
      setLtrSyncError(toLtrSyncOperatorMessage(openError));
    } finally {
      setLtrOpenLoading(false);
    }
  }

  return (
    <section className="runtime-console-basic-information" aria-label="LTR Information">
      {showStatusBadge ? (
        <div className="runtime-console-card-header">
          <strong className={`runtime-console-basic-information-status status-${basicInformation?.status ?? "none"}`}>
            {loading ? "Loading" : statusLabel}
          </strong>
        </div>
      ) : null}
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
      {!loading && !error ? (
        <div className="runtime-console-basic-information-actions">
          <button
            type="button"
            onClick={handlePreviewLtrSync}
            disabled={!canPreviewLtr || ltrPreviewLoading || ltrCommitLoading}
            title={
              canPreviewLtr
                ? "Preview the public-drive LTR workbook update."
                : "Registered LTR is required before previewing LTR."
            }
          >
            {ltrPreviewLoading ? "Previewing..." : "LTR update preview"}
          </button>
        </div>
      ) : null}
      {!loading && !error ? (
        <LtrWorkbookSyncPanel
          preview={ltrPreview}
          previewLoading={ltrPreviewLoading}
          commitLoading={ltrCommitLoading}
          openLoading={ltrOpenLoading}
          error={ltrSyncError}
          result={ltrSyncResult}
          canCommit={canCommitLtrPreview}
          onCommit={handleCommitLtrSync}
          onOpenWorkbook={handleOpenLtrWorkbookReadonly}
          onCancel={() => {
            setLtrPreview(null);
            setLtrSyncError(null);
          }}
        />
      ) : null}
    </section>
  );
}

type LtrWorkbookSyncPanelProps = {
  preview: LtrWorkbookBasicInformationSyncPreview | null;
  previewLoading: boolean;
  commitLoading: boolean;
  openLoading: boolean;
  error: string | null;
  result: LtrWorkbookBasicInformationSyncCommit | null;
  canCommit: boolean;
  onCommit: () => void;
  onOpenWorkbook: () => void;
  onCancel: () => void;
};

function LtrWorkbookSyncPanel({
  preview,
  previewLoading,
  commitLoading,
  openLoading,
  error,
  result,
  canCommit,
  onCommit,
  onOpenWorkbook,
  onCancel,
}: LtrWorkbookSyncPanelProps): ReactElement | null {
  if (!previewLoading && !error && !preview && !result) {
    return null;
  }

  const isBlocked = preview?.status !== "ready";
  const hasChanges = Boolean(preview?.comparison_values.some((value) => value.changed));
  const canOpenWorkbook = preview?.status === "ready" && Boolean(preview.workbook_path);

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
          <div className="runtime-console-ltr-sync-heading">
            <span>{preview.ltr_number}</span>
          </div>
          <dl className="runtime-console-ltr-sync-context">
            <div>
              <dt>
                <button
                  type="button"
                  className="runtime-console-ltr-sync-workbook-button"
                  onClick={onOpenWorkbook}
                  disabled={!canOpenWorkbook || openLoading || commitLoading}
                  title="Open the LTR workbook read-only and select this DL row."
                >
                  {openLoading ? "Opening read-only..." : "Open read-only workbook"}
                </button>
              </dt>
              <dd>{preview.workbook_path ?? "-"}</dd>
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
              <table className="runtime-console-ltr-sync-comparison">
                <thead>
                  <tr>
                    <th scope="col">Field</th>
                    <th scope="col">LTR workbook</th>
                    <th scope="col">LTR of Basic Info</th>
                  </tr>
                </thead>
                <tbody>
                  {preview.comparison_values.map((value) => (
                    <tr
                      key={value.field_name}
                      className={value.changed ? "is-changed" : undefined}
                    >
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

  if (message.includes("excel automation is not available")) {
    return "Excel automation is not available on this workstation.";
  }
  if (
    message.includes("read-only prompt") ||
    message.includes("password") ||
    message.includes("could not open") ||
    message.includes("unable to open")
  ) {
    return (
      "Excel could not open the LTR workbook read-only. Confirm any Excel read-only prompt, " +
      "then retry. Check the setup workbook path and password if it still fails."
    );
  }
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
    message.includes("already open") ||
    message.includes("unable to verify") ||
    message.includes("excel automation") ||
    message.includes("permission denied") ||
    message.includes("being used") ||
    message.includes("access is denied")
  ) {
    return "The LTR workbook cannot be opened safely. Close Excel copies of the workbook and retry.";
  }
  if (message.includes("not found") || message.includes("registered ltr row")) {
    return "The registered LTR row was not found in the configured workbook.";
  }
  if (message.includes("already up to date")) {
    return "LTR workbook is already up to date.";
  }
  return "Unable to update the LTR workbook. Check the setup path and try again.";
}
