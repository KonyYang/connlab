import type { ReactElement } from "react";
import type {
  FeeEvaluationPreviewHeader,
  FeeEvaluationPreviewRow,
  FeeEvaluationPreviewTotals,
  FeeEvaluationCostRisk,
} from "./feeEvaluationPreviewModel";

type FeeEvaluationPreviewTableProps = {
  costPreviewValues: FeeEvaluationCostPreviewValues;
  costRisk: FeeEvaluationCostRisk;
  groupFilter: string;
  header: FeeEvaluationPreviewHeader;
  downloadState: FeeFileDownloadState;
  generateDisabledReason: string | null;
  onBackToWorkbench: () => void;
  onCostPreviewChange: (field: keyof FeeEvaluationCostPreviewValues, value: string) => void;
  onGenerateFeeFile: () => void;
  onGroupFilterChange: (value: string) => void;
  scopeFeeLabel: string;
  groupOptions: string[];
  rows: FeeEvaluationPreviewRow[];
  totals: FeeEvaluationPreviewTotals;
};

export type FeeEvaluationCostPreviewValues = {
  conditionConfirmationSpendTime: string;
  externalCost: string;
  grandCost: string;
  labManpowerCost: string;
};

type FeeFileDownloadState =
  | { kind: "idle" }
  | { kind: "running" }
  | { kind: "success"; fileName: string | null }
  | { kind: "error"; message: string; manualCleanupWarning?: string | null };

export function FeeEvaluationPreviewTable({
  costPreviewValues,
  costRisk,
  groupFilter,
  header,
  downloadState,
  generateDisabledReason,
  onBackToWorkbench,
  onCostPreviewChange,
  onGenerateFeeFile,
  onGroupFilterChange,
  scopeFeeLabel,
  groupOptions,
  rows,
  totals,
}: FeeEvaluationPreviewTableProps): ReactElement {
  const grandCostLabel = calculateGrandCostLabel(rows, costPreviewValues.externalCost, totals.grandCost);

  return (
    <section className="fee-evaluation-preview-surface" aria-label="Testing Prices preview">
      <header className="fee-evaluation-preview-header">
        <div>
          <p className="eyebrow">Fee Evaluation</p>
        </div>
        <div className="fee-evaluation-preview-controls">
          <button
            className="fee-evaluation-back-button fee-evaluation-preview-back"
            type="button"
            onClick={onBackToWorkbench}
          >
            Back to Workbench
          </button>
          <div className="fee-evaluation-preview-group-card">
            <label>
              <span className="fee-evaluation-sr-only">Preview group</span>
              <select
                value={groupFilter}
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
              <strong>{scopeFeeLabel}</strong>
            </div>
          </div>
          <button
            className="fee-evaluation-file-button"
            type="button"
            onClick={onGenerateFeeFile}
            disabled={Boolean(generateDisabledReason) || downloadState.kind === "running"}
          >
            {downloadState.kind === "running" ? "Generating..." : "Fee Form"}
          </button>
        </div>
        <FeeFileDownloadStatus
          state={downloadState}
          disabledReason={generateDisabledReason}
        />
      </header>

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
                <th>Spend Time</th>
                <th>Description</th>
                <th>Unit Price</th>
                <th>Unit Type</th>
                <th>Units</th>
                <th>Base Fee</th>
                <th>Discount</th>
                <th>Testing Fee</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.lineId} className={previewRowClassName(row)}>
                  <td>{row.groupLabel}</td>
                  <td>{row.stepToken}</td>
                  <td>{row.spendTime}</td>
                  <td>
                    <strong>{row.description}</strong>
                    {row.reviewReason ? <span>{row.reviewReason}</span> : null}
                  </td>
                  <td>{row.unitPrice}</td>
                  <td>{row.unitType}</td>
                  <td>{row.units}</td>
                  <td>{row.baseFee}</td>
                  <td>{row.discount}</td>
                  <td>{row.testingFee}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

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
        <div>
          <dt>Working hours</dt>
          <dd>{totals.workingHours}</dd>
        </div>
        <div className="fee-evaluation-preview-cost-entry">
          <dt>
            <label htmlFor="fee-evaluation-lab-manpower-cost">Lab manpower cost</label>
          </dt>
          <dd>
            <input
              id="fee-evaluation-lab-manpower-cost"
              aria-label="Lab manpower cost preview"
              inputMode="decimal"
              placeholder={totals.labManpowerCost}
              value={costPreviewValues.labManpowerCost}
              onChange={(event) =>
                onCostPreviewChange("labManpowerCost", event.currentTarget.value)
              }
            />
          </dd>
        </div>
        <div className="fee-evaluation-preview-cost-entry">
          <dt>
            <label htmlFor="fee-evaluation-external-cost">External Cost</label>
          </dt>
          <dd>
            <input
              id="fee-evaluation-external-cost"
              aria-label="External Cost preview"
              inputMode="decimal"
              placeholder={totals.externalCost}
              value={costPreviewValues.externalCost}
              onChange={(event) =>
                onCostPreviewChange("externalCost", event.currentTarget.value)
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
    </section>
  );
}

function previewRowClassName(row: FeeEvaluationPreviewRow): string {
  const classNames = [`fee-evaluation-preview-group-${row.groupTone}`];
  if (row.status === "pending") {
    classNames.push("fee-evaluation-preview-row-pending");
  }
  if (row.rowKind === "manual_trailing") {
    classNames.push("fee-evaluation-preview-row-manual");
  }
  return classNames.join(" ");
}

function calculateGrandCostLabel(
  rows: FeeEvaluationPreviewRow[],
  externalCost: string,
  pendingLabel: string
): string {
  if (rows.length === 0) {
    return pendingLabel;
  }

  let total = 0;
  for (const row of rows) {
    const testingFee = parsePreviewNumber(row.testingFee);
    if (testingFee === null) {
      return pendingLabel;
    }
    total += testingFee;
  }

  const external = externalCost.trim().length > 0 ? parsePreviewNumber(externalCost) : 0;
  if (external === null) {
    return pendingLabel;
  }

  return String(total + external);
}

function parsePreviewNumber(value: string): number | null {
  const normalized = value.replace(/[$,]/g, "").trim();
  if (normalized.length === 0) {
    return null;
  }
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function FeeFileDownloadStatus({
  disabledReason,
  state,
}: {
  disabledReason: string | null;
  state: FeeFileDownloadState;
}): ReactElement | null {
  if (state.kind === "success") {
    return (
      <p className="fee-evaluation-download-status" role="status">
        {(state.fileName ?? "Fee file") + " downloaded."}
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
  if (disabledReason) {
    return <p className="fee-evaluation-download-status">{disabledReason}</p>;
  }
  return null;
}
