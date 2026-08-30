import type { ReactNode } from "react";
import type { ProjectPointProfileSummary } from "../../api/client";
import "../../contact-measurement-plan.css";

type ContactMeasurementPlanSummaryCardProps = {
  summary: ProjectPointProfileSummary | null;
  loading: boolean;
  onOpenSetup: () => void;
  recordActions?: {
    llcr: ReactNode;
    cr: ReactNode;
  };
};

export function ContactMeasurementPlanSummaryCard({
  summary,
  loading,
  onOpenSetup,
  recordActions,
}: ContactMeasurementPlanSummaryCardProps) {
  const confirmed = summary?.confirmed_revision ?? null;
  const crCoverage = confirmed?.cr_coverage ?? null;
  const crSummary = crCoverage?.mode === "follow_llcr"
    ? `Same as LLCR · ${crCoverage.points_per_sample} points / sample`
    : crCoverage
      ? `${crCoverage.selected_category_ids.length} ${crCoverage.selected_category_ids.length === 1 ? "category" : "categories"} · ${crCoverage.points_per_sample} points / sample`
      : "Not set";
  return <section className="contact-measurement-summary" aria-label="Test points" aria-busy={loading}>
    <div className="contact-measurement-summary-header">
      <div><h3>Test points</h3></div>
      <button type="button" disabled={loading} onClick={onOpenSetup}>Setup</button>
    </div>
    {!confirmed ? <p>Test point summary is not available.</p> : null}
    {confirmed || recordActions ? <dl className="contact-measurement-summary-points">
      <div>
        <dt>LLCR</dt>
        <dd>{confirmed ? `${confirmed.points_per_sample} points / sample · ΔR ${confirmed.delta_r_enabled ? "on" : "off"}` : "Not set"}</dd>
        {recordActions ? <div className="contact-measurement-summary-record-action">{recordActions.llcr}</div> : null}
      </div>
      <div>
        <dt>CR</dt>
        <dd>{crSummary}</dd>
        {recordActions ? <div className="contact-measurement-summary-record-action">{recordActions.cr}</div> : null}
      </div>
      <div><dt>IR</dt><dd>Not set</dd></div>
      <div><dt>DWV</dt><dd>Not set</dd></div>
    </dl> : null}
  </section>;
}
