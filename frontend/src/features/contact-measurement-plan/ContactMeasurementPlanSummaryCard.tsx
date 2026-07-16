import type { ProjectPointProfileSummary } from "../../api/client";
import "../../contact-measurement-plan.css";

type ContactMeasurementPlanSummaryCardProps = {
  summary: ProjectPointProfileSummary | null;
  loading: boolean;
  onOpenSetup: () => void;
};

export function ContactMeasurementPlanSummaryCard({ summary, loading, onOpenSetup }: ContactMeasurementPlanSummaryCardProps) {
  const confirmed = summary?.confirmed_revision ?? null;
  return <section className="contact-measurement-summary" aria-label="Test points">
    <div className="contact-measurement-summary-header">
      <div><h3>Test points</h3><span>{confirmed ? `Confirmed revision ${confirmed.revision_sequence}` : "Not confirmed"}</span></div>
      <button type="button" disabled={loading} onClick={onOpenSetup}>Setup</button>
    </div>
    {confirmed ? <><p>{`${confirmed.points_per_sample} points / sample`}</p><ul className="contact-measurement-summary-categories">{confirmed.categories.filter((category) => category.included).map((category) => <li key={category.category_id}>{`${category.record_prefix}: ${category.count_per_sample}`}</li>)}</ul></> : <p>Confirm a project point profile to make it available to Matrix summary.</p>}
  </section>;
}
