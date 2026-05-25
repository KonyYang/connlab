import type { ReactElement } from "react";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";

type RecordStepWorkspacePanelProps = {
  selectedToken: MatrixProjectionTokenCell | null;
  statusLabel: string;
};

function displayValue(value: string): string {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : "-";
}

export function RecordStepWorkspacePanel({
  selectedToken,
  statusLabel,
}: RecordStepWorkspacePanelProps): ReactElement {
  return (
    <aside
      className="runtime-console-record-step-workspace"
      aria-label="Record Step Workspace"
    >
      <header className="runtime-console-record-step-workspace-header">
        <div>
          <p className="eyebrow">Read-only step context</p>
          <h4>Record Step Workspace</h4>
        </div>
        <span>Authority locked</span>
      </header>

      {selectedToken ? (
        <>
          <dl className="runtime-console-record-step-fields">
            <div>
              <dt>Group</dt>
              <dd>{displayValue(selectedToken.groupLabel)}</dd>
            </div>
            <div>
              <dt>Step token</dt>
              <dd>{displayValue(selectedToken.rawToken)}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{statusLabel}</dd>
            </div>
            <div>
              <dt>Sample quantity</dt>
              <dd>{displayValue(selectedToken.sampleQuantityExpression)}</dd>
            </div>
            <div>
              <dt>Test item</dt>
              <dd>{displayValue(selectedToken.testItem)}</dd>
            </div>
            <div>
              <dt>Section</dt>
              <dd>{displayValue(selectedToken.section)}</dd>
            </div>
            <div>
              <dt>Method</dt>
              <dd>{displayValue(selectedToken.method)}</dd>
            </div>
            <div>
              <dt>Condition</dt>
              <dd>{displayValue(selectedToken.condition)}</dd>
            </div>
            <div>
              <dt>Requirement</dt>
              <dd>{displayValue(selectedToken.requirement)}</dd>
            </div>
          </dl>

          <div className="runtime-console-record-step-placeholders">
            <section>
              <span>Placeholder</span>
              <h5>Record draft</h5>
              <p>Record generation is not active in this task.</p>
            </section>
            <section>
              <span>Placeholder</span>
              <h5>Evidence / data</h5>
              <p>Evidence and measured data are outside this read-only workspace task.</p>
            </section>
            <section>
              <span>Placeholder</span>
              <h5>Review</h5>
              <p>Review workflow is not active for this step yet.</p>
            </section>
          </div>
        </>
      ) : (
        <p className="runtime-console-record-step-empty">
          Select a matrix token to review record context.
        </p>
      )}
    </aside>
  );
}
