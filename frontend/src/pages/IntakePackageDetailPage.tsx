import { useEffect, useMemo, useState, type ReactElement } from "react";
import {
  getIntakePackageDetail,
  reviewIntakePackageExceptions,
  type ExceptionWorkflowReview,
  type IntakeAsset,
  type IntakePackageDetail
} from "../api/client";
import "../intake-package-detail.css";

type IntakePackageDetailPageProps = {
  packageId: string;
  onBack: () => void;
  onOpenCaseReview: () => void;
};

export function IntakePackageDetailPage({
  packageId,
  onBack,
  onOpenCaseReview
}: IntakePackageDetailPageProps): ReactElement {
  const [detail, setDetail] = useState<IntakePackageDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [exceptionReview, setExceptionReview] =
    useState<ExceptionWorkflowReview | null>(null);
  const [reviewing, setReviewing] = useState(false);
  const [reviewError, setReviewError] = useState<string | null>(null);

  useEffect(() => {
    void loadDetail();
  }, [packageId]);

  const candidates = useMemo(() => detail?.candidate_assets ?? [], [detail]);
  const noFormCandidate = candidates.length === 0;
  const multiFormCandidate = candidates.length > 1;
  const packageState = exceptionReview?.package_status ?? detail?.package_status ?? "loading";

  async function loadDetail(): Promise<void> {
    setLoading(true);
    setLoadError(null);
    try {
      setDetail(await getIntakePackageDetail(packageId));
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : "Package detail load failed.");
    } finally {
      setLoading(false);
    }
  }

  async function reviewExceptions(): Promise<void> {
    setReviewing(true);
    setReviewError(null);
    try {
      const review = await reviewIntakePackageExceptions(packageId);
      setExceptionReview(review);
      await loadDetail();
    } catch (error) {
      setReviewError(error instanceof Error ? error.message : "Exception review failed.");
    } finally {
      setReviewing(false);
    }
  }

  return (
    <section className="intake-package-detail">
      <button className="text-button" type="button" onClick={onBack}>
        Back to intake inbox
      </button>

      <div className="package-hero">
        <div>
          <p className="eyebrow">Package detail</p>
          <h2>{packageId}</h2>
          <p>Review preserved source material and create review cases before project creation.</p>
        </div>
        <span className="package-state">{formatStatus(packageState)}</span>
      </div>

      {loading && <p className="exception-note">Loading package source and assets...</p>}
      {loadError && <p className="exception-note exception-note-danger">{loadError}</p>}

      {detail && (
        <>
          <div className="package-detail-grid">
            <section className="source-panel">
              <div>
                <p className="eyebrow">Source</p>
                <h3>Original request preserved</h3>
              </div>
              <dl className="metadata-list">
                <div>
                  <dt>Source type</dt>
                  <dd>{formatSourceType(detail.source_type)}</dd>
                </div>
                <div>
                  <dt>Sender</dt>
                  <dd>{detail.sender_email || detail.sender_name || "Not captured"}</dd>
                </div>
                <div>
                  <dt>Subject</dt>
                  <dd>{detail.subject || detail.source_original_name}</dd>
                </div>
                <div>
                  <dt>Storage state</dt>
                  <dd>{detail.source_stored ? "Source and attachments staged locally" : "Source file missing"}</dd>
                </div>
              </dl>
            </section>

            <section className="selection-panel">
              <div>
                <p className="eyebrow">Candidate</p>
                <h3>{candidateHeading(candidates)}</h3>
                <p>
                  Candidate forms come from stored attachment metadata. Each candidate becomes its
                  own project confirmation review before project creation.
                </p>
              </div>
              <button
                className="primary-action"
                disabled={reviewing || noFormCandidate}
                type="button"
                onClick={() => void reviewExceptions()}
              >
                {reviewing ? "Reviewing..." : "Create review cases"}
              </button>
              <button
                className="secondary-action"
                disabled={detail.case_count === 0}
                type="button"
                onClick={onOpenCaseReview}
              >
                Open case review
              </button>
              <p className="selection-note">
                {selectionNote(detail, noFormCandidate, multiFormCandidate)}
              </p>
              {noFormCandidate && (
                <p className="exception-note exception-note-danger">
                  No application form candidate was found. Request the application form or import
                  the Word form directly in the later direct-intake path.
                </p>
              )}
              {reviewError && <p className="exception-note exception-note-danger">{reviewError}</p>}
            </section>
          </div>

          <section className="asset-panel">
            <div className="asset-toolbar">
              <div>
                <p className="eyebrow">Attachments</p>
                <h3>Stored asset list</h3>
              </div>
              <span>{detail.asset_count} assets</span>
            </div>

            <div className="asset-list">
              {detail.assets.map((asset) => (
                <article className="asset-row" key={asset.asset_id}>
                  <div className="asset-row-main">
                    <div>
                      <strong>{asset.original_name}</strong>
                      <span>{assetTypeLabel(asset)} · {formatSize(asset.size_bytes)}</span>
                    </div>
                  </div>
                  <div className="asset-row-meta">
                    {asset.candidate_score !== null && asset.candidate_score !== undefined && (
                      <span className="score-chip">Score {asset.candidate_score}</span>
                    )}
                    <span className={`asset-role asset-role-${roleClass(asset.asset_role)}`}>
                      {formatRole(asset.asset_role)}
                    </span>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="exception-review-panel">
            <div className="exception-review-header">
              <div>
                <p className="eyebrow">Exception review</p>
                <h3>Application form outcomes</h3>
              </div>
              <span>{detail.candidate_count} candidate forms</span>
            </div>

            <div className="exception-outcome-grid">
              <article className="exception-outcome">
                <strong>No-form package</strong>
                <p>Shown when stored assets do not include a candidate application form.</p>
              </article>
              <article className="exception-outcome">
                <strong>Multiple forms</strong>
                <p>Each candidate form becomes a separate project request for independent review.</p>
              </article>
              <article className="exception-outcome">
                <strong>Created cases</strong>
                <p>{detail.case_count} cases are currently linked to this package.</p>
              </article>
            </div>

            {(exceptionReview || detail.cases.length > 0) && (
              <div className="exception-result">
                <dl className="metadata-list">
                  <div>
                    <dt>Package status</dt>
                    <dd>{formatStatus(exceptionReview?.package_status ?? detail.package_status)}</dd>
                  </div>
                  <div>
                    <dt>Created cases</dt>
                    <dd>{exceptionReview?.case_ids.length ?? detail.case_count}</dd>
                  </div>
                </dl>
                {exceptionReview && exceptionReview.issues.length > 0 && (
                  <ul className="exception-issue-list">
                    {exceptionReview.issues.map((issue) => (
                      <li key={`${issue.kind}-${issue.asset_id ?? issue.case_id ?? issue.message}`}>
                        <strong>{formatStatus(issue.kind)}</strong>
                        <span>{issue.message}</span>
                        <em>{issue.operator_action}</em>
                      </li>
                    ))}
                  </ul>
                )}
                <div className="case-link-list">
                  {(exceptionReview?.case_ids ?? detail.cases.map((item) => item.case_id)).map(
                    (caseId) => (
                      <button
                        className="secondary-action"
                        key={caseId}
                        type="button"
                        onClick={onOpenCaseReview}
                      >
                        Review {caseId}
                      </button>
                    )
                  )}
                </div>
              </div>
            )}
          </section>
        </>
      )}
    </section>
  );
}

function candidateHeading(candidates: IntakeAsset[]): string {
  if (candidates.length === 0) {
    return "No application form candidate";
  }
  if (candidates.length === 1) {
    return candidates[0].original_name;
  }
  return `${candidates.length} application form candidates`;
}

function selectionNote(
  detail: IntakePackageDetail,
  noFormCandidate: boolean,
  multiFormCandidate: boolean
): string {
  if (noFormCandidate) {
    return "The package stays in follow-up until a form is provided.";
  }
  if (multiFormCandidate) {
    return "Multiple forms are present. Review creates one case for each candidate form.";
  }
  if (detail.case_count > 0) {
    return "One candidate form already has a review case.";
  }
  return "One candidate form will create one review case.";
}

function formatSourceType(value: string): string {
  return value === "outlook_msg" ? "Outlook .msg" : formatStatus(value);
}

function formatRole(value: string): string {
  return formatStatus(value.replace("application_form", "form"));
}

function formatStatus(value: string): string {
  return value
    .split("_")
    .filter(Boolean)
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

function roleClass(value: string): string {
  if (value.includes("candidate")) {
    return "candidate";
  }
  if (value.includes("selected")) {
    return "selected";
  }
  if (value.includes("email")) {
    return "source";
  }
  return "supporting";
}

function assetTypeLabel(asset: IntakeAsset): string {
  if (asset.asset_role === "email_source") {
    return "Source email";
  }
  if (asset.extension) {
    return asset.extension.replace(".", "").toUpperCase();
  }
  return asset.mime_type || "Stored file";
}

function formatSize(sizeBytes: number): string {
  if (sizeBytes < 1024) {
    return `${sizeBytes} B`;
  }
  if (sizeBytes < 1024 * 1024) {
    return `${Math.round(sizeBytes / 1024)} KB`;
  }
  return `${(sizeBytes / (1024 * 1024)).toFixed(1)} MB`;
}
