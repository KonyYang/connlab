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
      <h3>Source document & template check</h3>
      <div className="template-check-grid">
        <div className="source-doc-card">
          <span className="word-file-icon">W</span>
          <div>
            <strong>{activeCase.selected_asset_name ?? review.source_original_name}</strong>
            <span>source context: {formatSourceType(review.source_type)}</span>
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
              <strong>Template version mismatch detected</strong>
              <span>Current: In Library: E_3778_Rev-H</span>
              <span>Source: E_3778_Rev-H</span>
            </div>
          </div>
          <button className="secondary-button" disabled type="button">
            <UiIcon name="refresh" />
            Update to latest template
          </button>
        </div>
      </div>
    </section>
  );
}

function FieldBadge({ label, value }: { label: string; value: string }): ReactElement {
  return <dl><dt>{label}</dt><dd>{value}</dd></dl>;
}
