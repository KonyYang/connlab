import type { ReactNode } from "react";
import type { ContactMeasurementPlanWorkspace } from "../../api/client";
import { selectContactMeasurementPlanSummary } from "./contactMeasurementPlanSelectors";
import "../../contact-measurement-plan.css";

type ContactMeasurementPlanSummaryCardProps = {
  workspace: ContactMeasurementPlanWorkspace | null;
  loading: boolean;
  onOpenSetup: () => void;
  compatibilityRow: ReactNode;
};

export function ContactMeasurementPlanSummaryCard({
  workspace,
  loading,
  onOpenSetup,
  compatibilityRow,
}: ContactMeasurementPlanSummaryCardProps) {
  const view = selectContactMeasurementPlanSummary(workspace);
  const matrixRevision = workspace?.matrix_binding?.current_matrix_revision ?? "-";
  const planRevision = workspace?.revision?.revision_sequence ?? "-";
  return (
    <section className="contact-measurement-summary" aria-label="Contact Measurement Plan">
      <div className="contact-measurement-summary-header">
        <div>
          <h3>Contact Measurement Plan</h3>
          <span>{view.statusLabel}</span>
        </div>
        <button
          type="button"
          disabled={loading || !view.canOpenSetup}
          onClick={onOpenSetup}
        >
          Contact measurement setup
        </button>
      </div>
      <dl className="contact-measurement-summary-facts">
        <div>
          <dt>Coverage</dt>
          <dd>
            {workspace
              ? `${workspace.summary.included_target_count} / ${workspace.summary.total_target_count} targets`
              : "-"}
          </dd>
        </div>
        <div>
          <dt>Readings</dt>
          <dd>{`LLCR: ${view.readings.llcr}`}</dd>
          <dd>{`CR: ${view.readings.crSpecifiedCurrent}`}</dd>
        </div>
        <div>
          <dt>Revisions</dt>
          <dd>{`Plan ${planRevision}`}</dd>
          <dd>{`Matrix ${matrixRevision}`}</dd>
        </div>
      </dl>
      {view.warning ? <p className="contact-measurement-summary-warning" role="status">{view.warning}</p> : null}
      <div className="contact-measurement-compatibility-row">{compatibilityRow}</div>
    </section>
  );
}
