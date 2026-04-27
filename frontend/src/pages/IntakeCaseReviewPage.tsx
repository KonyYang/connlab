import type { ReactElement } from "react";
import "../intake-case-review.css";

type DraftField = {
  field: string;
  extracted: string;
  confidence: "High" | "Needs review" | "Missing";
  override?: string;
};

const DRAFT_FIELDS: DraftField[] = [
  {
    field: "Project No.",
    extracted: "P-2026-041",
    confidence: "High"
  },
  {
    field: "Requester",
    extracted: "White",
    confidence: "High"
  },
  {
    field: "Product Name",
    extracted: "Connector sample",
    confidence: "Needs review",
    override: "Pending manual confirmation"
  },
  {
    field: "Requested Testing",
    extracted: "See attachment",
    confidence: "Needs review",
    override: "Requires supporting attachment check"
  },
  {
    field: "Sample Quantity",
    extracted: "Not parsed",
    confidence: "Missing"
  }
];

type IntakeCaseReviewPageProps = {
  packageId: string;
  onBack: () => void;
};

export function IntakeCaseReviewPage({
  packageId,
  onBack
}: IntakeCaseReviewPageProps): ReactElement {
  return (
    <section className="intake-case-review">
      <button className="text-button" type="button" onClick={onBack}>
        Back to package detail
      </button>

      <div className="case-review-hero">
        <div>
          <p className="eyebrow">Case review</p>
          <h2>{packageId} draft</h2>
          <p>Review extracted values and manual notes before a project can be created.</p>
        </div>
        <span className="review-state">Needs human review</span>
      </div>

      <div className="case-review-grid">
        <aside className="selected-form-panel">
          <div>
            <p className="eyebrow">Selected form</p>
            <h3>E-3718 Application Form.docx</h3>
            <p>Word content parsing is intentionally represented as draft data here.</p>
          </div>
          <dl>
            <div>
              <dt>Case state</dt>
              <dd>Needs review</dd>
            </div>
            <div>
              <dt>Parser status</dt>
              <dd>Draft placeholder</dd>
            </div>
            <div>
              <dt>Source package</dt>
              <dd>{packageId}</dd>
            </div>
          </dl>
        </aside>

        <section className="draft-field-panel">
          <div className="draft-toolbar">
            <div>
              <p className="eyebrow">Draft fields</p>
              <h3>Review extracted application data</h3>
            </div>
            <span>{DRAFT_FIELDS.length} fields</span>
          </div>

          <div className="draft-field-list">
            {DRAFT_FIELDS.map((item) => (
              <article className="draft-field-row" key={item.field}>
                <div>
                  <strong>{item.field}</strong>
                  <span>{item.extracted}</span>
                </div>
                <div className="draft-field-review">
                  <span className={`confidence-chip confidence-${item.confidence.toLowerCase().replace(" ", "-")}`}>
                    {item.confidence}
                  </span>
                  <input
                    aria-label={`${item.field} manual override`}
                    disabled
                    placeholder={item.override ?? "Manual override"}
                  />
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>

      <section className="confirmation-panel">
        <div>
          <p className="eyebrow">Confirmation gate</p>
          <h3>Project creation is still blocked</h3>
          <p>
            The next backend task will decide how confirmed draft data becomes Project,
            ApplicationForm, SampleInfo, and FileAsset records.
          </p>
        </div>
        <button className="primary-action" disabled type="button">
          Confirm into project
        </button>
      </section>
    </section>
  );
}
