import type { ReactElement } from "react";
import type {
  FeeEvaluationPreviewHeader,
  FeeEvaluationPreviewRow,
  FeeEvaluationPreviewTotals,
} from "./feeEvaluationPreviewModel";

type FeeEvaluationPreviewTableProps = {
  header: FeeEvaluationPreviewHeader;
  rows: FeeEvaluationPreviewRow[];
  totals: FeeEvaluationPreviewTotals;
};

export function FeeEvaluationPreviewTable({
  header,
  rows,
  totals,
}: FeeEvaluationPreviewTableProps): ReactElement {
  return (
    <section className="fee-evaluation-preview-surface" aria-label="Testing Prices preview">
      <header className="fee-evaluation-preview-header">
        <div>
          <p className="eyebrow">Testing Prices preview</p>
          <h3>{rows.length} Matrix line(s)</h3>
        </div>
        <div className="fee-evaluation-preview-state">
          <span>{totals.confirmationLabel}</span>
          <strong>Total fee: {totals.testFeeTotal}</strong>
        </div>
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
                <tr
                  key={row.lineId}
                  className={
                    row.status === "pending" ? "fee-evaluation-preview-row-pending" : undefined
                  }
                >
                  <td>{row.groupLabel}</td>
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
        <div>
          <dt>Test Fee Total</dt>
          <dd>{totals.testFeeTotal}</dd>
        </div>
        <div>
          <dt>Working hours</dt>
          <dd>{totals.workingHours}</dd>
        </div>
        <div>
          <dt>Lab manpower cost</dt>
          <dd>{totals.labManpowerCost}</dd>
        </div>
        <div>
          <dt>External Cost</dt>
          <dd>{totals.externalCost}</dd>
        </div>
        <div>
          <dt>Grand Cost</dt>
          <dd>{totals.grandCost}</dd>
        </div>
        <div>
          <dt>Prepared by</dt>
          <dd>{totals.preparedBy}</dd>
        </div>
        <div>
          <dt>Approved by</dt>
          <dd>{totals.approvedBy}</dd>
        </div>
      </dl>
    </section>
  );
}
