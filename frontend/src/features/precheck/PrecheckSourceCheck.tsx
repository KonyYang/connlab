import type { ReactElement } from "react";

import type { IntakeCaseReview, IntakeCaseReviewItem } from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import { fallbackValue, formatSourceType } from "./precheckReviewSelectors";

type PrecheckSourceCheckProps = {
  review: IntakeCaseReview;
  activeCase: IntakeCaseReviewItem;
};

export function PrecheckSourceCheck({
  review,
  activeCase
}: PrecheckSourceCheckProps): ReactElement {
  return (
    <section className="precheck-card source-template-check">
      <h3 className="ui-panel-title">Source traceability</h3>
      <div className="template-check-grid">
        <div className="source-doc-card">
          <span className="word-file-icon">W</span>
          <div>
            <strong>{activeCase.selected_asset_name ?? review.source_original_name}</strong>
            <span>Imported source: {formatSourceType(review.source_type)}</span>
          </div>
          <UiIcon name="clock" />
        </div>
        <div className="metadata-card">
          <FieldBadge label="Form No." value={fallbackValue("form_no", activeCase.fields) || "E-7818"} />
          <FieldBadge label="Revision" value={fallbackValue("revision", activeCase.fields) || "H"} />
          <FieldBadge label="Reference doc." value={fallbackValue("reference_doc", activeCase.fields) || "QS-03-008"} />
        </div>
        <div className="template-warning-card">
          <div className="template-warning-copy">
            <UiIcon name="help" />
            <div>
              <strong>Confirmed application data is edited below</strong>
              <span>The source file remains attached for traceability.</span>
              <span>Project creation uses the corrected Precheck values.</span>
            </div>
          </div>
          <button className="secondary-button ui-secondary-action" disabled type="button">
            <UiIcon name="clock" />
            Source locked after Precheck entry
          </button>
        </div>
      </div>
    </section>
  );
}

function FieldBadge({ label, value }: { label: string; value: string }): ReactElement {
  return <dl><dt>{label}</dt><dd>{value}</dd></dl>;
}
