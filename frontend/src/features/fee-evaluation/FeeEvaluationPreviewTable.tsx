import type { ReactElement } from "react";
import type {
  FeeEvaluationEditableField,
  FeeEvaluationPreviewHeader,
  FeeEvaluationPreviewRow,
  FeeEvaluationPreviewTotals,
  FeeEvaluationCostRisk,
  FeeEvaluationUpdateBlocker,
} from "./feeEvaluationPreviewModel";
import { FEE_UNIT_TYPE_OPTIONS } from "./feeEvaluationPreviewModel";

type FeeEvaluationPreviewTableProps = {
  costPreviewValues: FeeEvaluationCostPreviewValues;
  costRisk: FeeEvaluationCostRisk;
  confirmFeeActionState: ConfirmFeeActionState;
  grandCostLabel: string;
  labManpowerCostLabel: string;
  groupFilter: string;
  header: FeeEvaluationPreviewHeader;
  identityLine: string;
  downloadState: FeeFileDownloadState;
  draftPreviewNotice: string | null;
  readOnly?: boolean;
  onCostPreviewChange: (field: keyof FeeEvaluationCostPreviewValues, value: string) => void;
  onGenerateFeeFile: () => void;
  onGroupFilterChange: (value: string) => void;
  onRowEditChange: (
    lineId: string,
    field: FeeEvaluationEditableField,
    value: string
  ) => void;
  saveState: FeePricingDraftSaveState;
  suppressedSaveMessage?: string | null;
  scopeFeeLabel: string;
  groupOptions: string[];
  rows: FeeEvaluationPreviewRow[];
  totals: FeeEvaluationPreviewTotals;
  updateFeeBlockersByRowId?: Record<string, FeeEvaluationUpdateBlocker>;
};

export type FeeEvaluationCostPreviewValues = {
  conditionConfirmationSpendTime: string;
  externalCost: string;
  externalCostNote: string;
  labManpowerHourlyRate: string;
};

type FeeFileDownloadState =
  | { kind: "idle" }
  | { kind: "running" }
  | {
      kind: "success";
      fileName: string | null;
      delivery?: "download" | "official";
    }
  | { kind: "error"; message: string; manualCleanupWarning?: string | null };

type FeePricingDraftSaveState =
  | { kind: "loading" }
  | { kind: "idle"; message: string | null }
  | { kind: "dirty" }
  | { kind: "saving" }
  | { kind: "saved"; message: string }
  | { kind: "stale"; message: string }
  | { kind: "error"; message: string };

type ConfirmFeeActionState =
  | { kind: "idle" }
  | { kind: "confirming" }
  | { kind: "success"; message: string }
  | { kind: "error"; message: string };

export function FeeEvaluationPreviewTable({
  costPreviewValues,
  costRisk,
  confirmFeeActionState,
  grandCostLabel,
  labManpowerCostLabel,
  groupFilter,
  header,
  identityLine,
  downloadState,
  draftPreviewNotice,
  readOnly = false,
  onCostPreviewChange,
  onGenerateFeeFile,
  onGroupFilterChange,
  onRowEditChange,
  saveState,
  suppressedSaveMessage = null,
  scopeFeeLabel,
  groupOptions,
  rows,
  totals,
  updateFeeBlockersByRowId = {},
}: FeeEvaluationPreviewTableProps): ReactElement {
  return (
    <section className="fee-evaluation-preview-surface" aria-label="Testing Prices preview">
      <header className="fee-evaluation-preview-header">
        <div>
          <p className="eyebrow fee-evaluation-preview-title" title={identityLine}>
            {identityLine}
          </p>
        </div>
        <div className="fee-evaluation-preview-controls">
          <div className="fee-evaluation-preview-group-card">
            <label>
              <span className="fee-evaluation-sr-only">Preview group</span>
              <select
                value={groupFilter}
                disabled={readOnly}
                onChange={(event) => onGroupFilterChange(event.currentTarget.value)}
              >
                <option value="all">All Group</option>
                {groupOptions.map((group) => (
                  <option key={group} value={group}>
                    {group}
                  </option>
                ))}
              </select>
            </label>
            <div className="fee-evaluation-preview-scope-fee" aria-label="Selected group fee">
              <span>Total Testing Fee</span>
              <strong>{scopeFeeLabel}</strong>
            </div>
          </div>
          <button
            className="fee-evaluation-file-button"
            type="button"
            onClick={onGenerateFeeFile}
            disabled={downloadState.kind === "running"}
            title="Downloads a draft until the current Fee is confirmed; otherwise saves the official Fee Form."
          >
            {downloadState.kind === "running" ? "Generating..." : "Fee Form"}
          </button>
        </div>
        <FeeFileDownloadStatus
          state={downloadState}
          notice={draftPreviewNotice}
        />
        <FeePricingDraftSaveStatus
          state={saveState}
          suppressedMessage={suppressedSaveMessage}
        />
      </header>

      {confirmFeeActionState.kind === "error" ? (
        <p className="fee-evaluation-confirm-error" role="alert">
          {confirmFeeActionState.message}
        </p>
      ) : null}
      {confirmFeeActionState.kind === "success" ? (
        <p className="fee-evaluation-confirm-success" role="status">
          {confirmFeeActionState.message}
        </p>
      ) : null}

      <dl className="fee-evaluation-preview-totals" aria-label="Testing Prices totals">
        <div className="fee-evaluation-preview-cost-entry">
          <dt>
            <label htmlFor="fee-evaluation-condition-confirmation-spend-time">
              Condition confirmation
            </label>
          </dt>
          <dd>
            <input
              id="fee-evaluation-condition-confirmation-spend-time"
              aria-label="Condition confirmation spend time"
              inputMode="decimal"
              disabled={readOnly}
              placeholder="Spend Time"
              value={costPreviewValues.conditionConfirmationSpendTime}
              onChange={(event) =>
                onCostPreviewChange(
                  "conditionConfirmationSpendTime",
                  event.currentTarget.value
                )
              }
            />
          </dd>
        </div>
        <div className="fee-evaluation-preview-cost-entry fee-evaluation-preview-rate-entry">
          <dt>
            <label htmlFor="fee-evaluation-lab-manpower-hourly-rate">
              Working hours
            </label>
          </dt>
          <dd>
            <strong className="fee-evaluation-preview-cost-result">
              {totals.workingHours}
            </strong>
            <span aria-hidden="true" className="fee-evaluation-preview-formula-mark">
              *
            </span>
            <input
              id="fee-evaluation-lab-manpower-hourly-rate"
              aria-label="Lab manpower hourly rate"
              inputMode="decimal"
              disabled={readOnly}
              placeholder="200"
              value={costPreviewValues.labManpowerHourlyRate}
              onChange={(event) =>
                onCostPreviewChange("labManpowerHourlyRate", event.currentTarget.value)
              }
            />
            <span aria-hidden="true" className="fee-evaluation-preview-formula-mark">
              =
            </span>
            <span className="fee-evaluation-preview-formula-label">
              Lab manpower cost
            </span>
            <strong className="fee-evaluation-preview-cost-result">
              {labManpowerCostLabel}
            </strong>
          </dd>
        </div>
        <div className="fee-evaluation-preview-cost-entry fee-evaluation-preview-external-entry">
          <dt>
            <label htmlFor="fee-evaluation-external-cost">External Cost</label>
          </dt>
          <dd>
            <input
              id="fee-evaluation-external-cost"
              aria-label="External Cost preview"
              inputMode="decimal"
              disabled={readOnly}
              placeholder={totals.externalCost}
              value={costPreviewValues.externalCost}
              onChange={(event) =>
                onCostPreviewChange("externalCost", event.currentTarget.value)
              }
            />
            <input
              id="fee-evaluation-external-cost-note"
              aria-label="External Cost note"
              disabled={readOnly}
              placeholder="Cost note"
              value={costPreviewValues.externalCostNote}
              onChange={(event) =>
                onCostPreviewChange("externalCostNote", event.currentTarget.value)
              }
            />
          </dd>
        </div>
        <div>
          <dt>Grand Cost</dt>
          <dd>{grandCostLabel}</dd>
        </div>
      </dl>
      {costRisk.severity === "loss_warning" && costRisk.message ? (
        <p className="fee-evaluation-preview-cost-warning" role="alert">
          {costRisk.message}
        </p>
      ) : null}

      <dl className="fee-evaluation-preview-header-band" aria-label="Testing Prices header">
        <div>
          <dt>LTR Number</dt>
          <dd>{header.ltrNumber}</dd>
        </div>
        <div>
          <dt>Test description</dt>
          <dd>{header.testDescription}</dd>
        </div>
        <div>
          <dt>Requestor</dt>
          <dd>{header.requestor}</dd>
        </div>
        <div>
          <dt>Site</dt>
          <dd>{header.site}</dd>
        </div>
      </dl>

      {rows.length === 0 ? (
        <p className="fee-evaluation-empty">No Matrix fee rows are available for preview.</p>
      ) : (
        <div className="fee-evaluation-preview-table-wrap">
          <table
            className="fee-evaluation-preview-table"
            aria-label="Testing Prices preview rows"
          >
            <thead>
              <tr>
                <th>Group</th>
                <th>Step</th>
                <th>Man-hour</th>
                <th>Description</th>
                <th>Unit Price</th>
                <th>Unit Type</th>
                <th>Units</th>
                <th>Base Fee</th>
                <th>Discount</th>
                <th>Testing Fee</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr
                  key={row.lineId}
                  className={previewRowClassName(
                    row,
                    Boolean(updateFeeBlockersByRowId[row.lineId])
                  )}
                >
                  <td>{row.groupLabel}</td>
                  <td>{row.stepToken}</td>
                  <td>
                    <EditablePreviewInput
                      ariaLabel={`Spend Time for group ${row.groupLabel || "manual"} step ${row.stepToken}`}
                      disabled={readOnly}
                      fieldState={previewFieldState(row, "spendTime")}
                      value={row.spendTime}
                      onChange={(value) =>
                        onRowEditChange(row.lineId, "spendTime", value)
                      }
                    />
                  </td>
                  <td>
                    <strong>{row.description}</strong>
                    <ReviewCue
                      row={row}
                      updateBlocker={updateFeeBlockersByRowId[row.lineId]}
                    />
                  </td>
                  <td>
                    <EditablePreviewInput
                      ariaLabel={`Unit Price for ${row.description}`}
                      disabled={readOnly}
                      fieldState={previewFieldState(row, "unitPrice")}
                      value={row.unitPrice}
                      onChange={(value) =>
                        onRowEditChange(row.lineId, "unitPrice", value)
                      }
                    />
                  </td>
                  <td>
                    <EditableUnitTypeSelect
                      disabled={readOnly}
                      fieldState={previewFieldState(row, "unitType")}
                      value={row.unitType}
                      onChange={(value) =>
                        onRowEditChange(row.lineId, "unitType", value)
                      }
                    />
                  </td>
                  <td>
                    <EditablePreviewInput
                      ariaLabel={`Units for ${row.description}`}
                      disabled={readOnly}
                      fieldState={previewFieldState(row, "units")}
                      value={row.units}
                      onChange={(value) => onRowEditChange(row.lineId, "units", value)}
                    />
                  </td>
                  <td>
                    <EditablePreviewInput
                      ariaLabel={`Base Fee for ${row.description}`}
                      disabled={readOnly}
                      fieldState={previewFieldState(row, "baseFee")}
                      value={row.baseFee}
                      onChange={(value) =>
                        onRowEditChange(row.lineId, "baseFee", value)
                      }
                    />
                  </td>
                  <td>
                    <EditablePreviewInput
                      ariaLabel={`Discount for ${row.description}`}
                      disabled={readOnly}
                      fieldState={previewFieldState(row, "discount")}
                      value={row.discount}
                      onChange={(value) =>
                        onRowEditChange(row.lineId, "discount", value)
                      }
                    />
                  </td>
                  <td>{row.testingFee}</td>
                  <td>
                    <EditablePreviewInput
                      ariaLabel={`Notes for ${row.description}`}
                      disabled={readOnly}
                      inputMode="text"
                      placeholder=""
                      value={row.notes}
                      onChange={(value) => onRowEditChange(row.lineId, "notes", value)}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </section>
  );
}

function FeePricingDraftSaveStatus({
  state,
  suppressedMessage,
}: {
  state: FeePricingDraftSaveState;
  suppressedMessage?: string | null;
}): ReactElement | null {
  if (state.kind !== "stale" && state.kind !== "error") {
    return null;
  }
  if (suppressedMessage && state.message === suppressedMessage) {
    return null;
  }
  if (state.kind === "stale") {
    return (
      <p className="fee-evaluation-save-notice" role="status">
        {state.message}
      </p>
    );
  }
  return (
    <p className="fee-evaluation-save-error" role="alert">
      {state.message}
    </p>
  );
}

function previewRowClassName(
  row: FeeEvaluationPreviewRow,
  hasUpdateBlocker = false
): string {
  const classNames = [`fee-evaluation-preview-group-${row.groupTone}`];
  if (row.status === "pending") {
    classNames.push("fee-evaluation-preview-row-pending");
  }
  if (row.rowKind === "manual_trailing") {
    classNames.push("fee-evaluation-preview-row-manual");
  }
  if (hasUpdateBlocker) {
    classNames.push("fee-evaluation-preview-row-blocked");
  }
  return classNames.join(" ");
}

function ReviewCue({
  row,
  updateBlocker,
}: {
  row: FeeEvaluationPreviewRow;
  updateBlocker?: FeeEvaluationUpdateBlocker;
}): ReactElement | null {
  const metadata = row.fieldMetadata.find((entry) => entry.state !== "auto_filled");
  const message = updateBlocker?.rowMessage ?? metadata?.message ?? row.reviewReason;
  if (!message) {
    return null;
  }
  return <span className="fee-evaluation-review-cue">Review: {message}</span>;
}

function previewFieldState(
  row: FeeEvaluationPreviewRow,
  field: NonNullable<FeeEvaluationPreviewRow["fieldMetadata"]>[number]["field"]
): string | null {
  const state = row.fieldMetadata.find((entry) => entry.field === field)?.state;
  return state && state !== "auto_filled" ? state : null;
}

function EditablePreviewInput({
  ariaLabel,
  disabled = false,
  fieldState,
  inputMode = "decimal",
  onChange,
  placeholder = "Pending",
  value,
}: {
  ariaLabel: string;
  disabled?: boolean;
  fieldState?: string | null;
  inputMode?: "decimal" | "text";
  onChange: (value: string) => void;
  placeholder?: string;
  value: string;
}): ReactElement {
  const className = [
    "fee-evaluation-preview-cell-input",
    fieldState ? `fee-evaluation-preview-cell-${fieldState}` : "",
  ]
    .filter(Boolean)
    .join(" ");
  return (
    <input
      aria-label={ariaLabel}
      className={className}
      disabled={disabled}
      inputMode={inputMode}
      placeholder={placeholder}
      value={editableInputValue(value)}
      onChange={(event) => onChange(event.currentTarget.value)}
    />
  );
}

function EditableUnitTypeSelect({
  disabled = false,
  fieldState,
  onChange,
  value,
}: {
  disabled?: boolean;
  fieldState?: string | null;
  onChange: (value: string) => void;
  value: string;
}): ReactElement {
  const normalizedValue = value.trim() || "Pending";
  const hasStandardValue = FEE_UNIT_TYPE_OPTIONS.some(
    (option) => option === normalizedValue
  );
  return (
    <select
      aria-label="Unit Type"
      className={[
        "fee-evaluation-preview-cell-select",
        fieldState ? `fee-evaluation-preview-cell-${fieldState}` : "",
      ]
        .filter(Boolean)
        .join(" ")}
      disabled={disabled}
      value={normalizedValue}
      onChange={(event) => onChange(event.currentTarget.value)}
    >
      {!hasStandardValue ? (
        <option value={normalizedValue}>{normalizedValue}</option>
      ) : null}
      {FEE_UNIT_TYPE_OPTIONS.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  );
}

function editableInputValue(value: string): string {
  return value.trim().toLowerCase() === "pending" ? "" : value;
}

function FeeFileDownloadStatus({
  notice,
  state,
}: {
  notice: string | null;
  state: FeeFileDownloadState;
}): ReactElement | null {
  if (state.kind === "success") {
    return (
      <p className="fee-evaluation-download-status" role="status">
        {(state.fileName ?? "Fee file") +
          (state.delivery === "official" ? " saved to the project folder." : " downloaded.")}
      </p>
    );
  }
  if (state.kind === "error") {
    return (
      <div className="fee-evaluation-download-error" role="alert">
        <p>{state.message}</p>
        {state.manualCleanupWarning ? <p>{state.manualCleanupWarning}</p> : null}
      </div>
    );
  }
  if (notice) {
    return <p className="fee-evaluation-download-status">{notice}</p>;
  }
  return null;
}
