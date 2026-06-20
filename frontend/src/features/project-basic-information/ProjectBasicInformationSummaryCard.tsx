import { useState, type ReactElement } from "react";
import type { ProjectBasicInformationResponse } from "../../api/client";
import {
  selectBasicInformationMissingLabels,
  selectBasicInformationStatusLabel,
  selectChangedSourceFieldLabels,
  selectConfirmedViewItems,
  selectWorkbenchSummaryItems,
} from "./basicInformationSelectors";

type ProjectBasicInformationSummaryCardProps = {
  basicInformation: ProjectBasicInformationResponse | null;
  loading: boolean;
  error: string | null;
};

export function ProjectBasicInformationSummaryCard({
  basicInformation,
  loading,
  error,
}: ProjectBasicInformationSummaryCardProps): ReactElement {
  const [expanded, setExpanded] = useState(false);
  const statusLabel = selectBasicInformationStatusLabel(basicInformation);
  const missingLabels = selectBasicInformationMissingLabels(basicInformation);
  const changedLabels = selectChangedSourceFieldLabels(basicInformation);
  const summaryItems = selectWorkbenchSummaryItems(basicInformation);
  const confirmedItems = selectConfirmedViewItems(basicInformation);
  const hasConfirmed = Boolean(basicInformation?.latest_confirmed);

  return (
    <section className="runtime-console-basic-information" aria-label="Project Basic Information">
      <div className="runtime-console-card-header">
        <p className="eyebrow">Project Basic Information</p>
        <strong className={`runtime-console-basic-information-status status-${basicInformation?.status ?? "none"}`}>
          {loading ? "Loading" : statusLabel}
        </strong>
      </div>
      {error ? <p className="runtime-console-basic-information-error">{error}</p> : null}
      {!loading && !error && !hasConfirmed ? (
        <>
          <p>Confirm from Basic Information</p>
          {missingLabels.length > 0 ? (
            <div className="runtime-console-basic-information-muted">
              <span>Missing</span>
              <ul>
                {missingLabels.map((label) => (
                  <li key={label}>{label}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </>
      ) : null}
      {!loading && !error && basicInformation?.status === "needs_review" ? (
        <>
          <p className="runtime-console-basic-information-warning">
            {changedLabels.length} source field{changedLabels.length === 1 ? "" : "s"} changed
          </p>
          <p>Confirm from Basic Information</p>
        </>
      ) : null}
      {!loading && !error && hasConfirmed ? (
        <>
          <dl className="runtime-console-basic-information-list">
            {summaryItems.map((item) => (
              <div key={item.key}>
                <dt>{item.label}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
          <button type="button" onClick={() => setExpanded((value) => !value)}>
            {expanded ? "Hide" : "View"}
          </button>
          {expanded ? (
            <div className="runtime-console-basic-information-expanded">
              <strong>All confirmed fields</strong>
              <dl className="runtime-console-basic-information-list">
                {confirmedItems.map((item) => (
                  <div key={item.key}>
                    <dt>{item.label}</dt>
                    <dd>{item.value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
