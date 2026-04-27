import type { ReactElement } from "react";
import "../intake-package-detail.css";

type IntakeAssetPreview = {
  id: string;
  name: string;
  role: "Candidate" | "Selected" | "Supporting";
  score?: number;
  type: string;
  size: string;
};

const ASSETS: IntakeAssetPreview[] = [
  {
    id: "ASSET-001",
    name: "E-3718 Application Form.docx",
    role: "Candidate",
    score: 80,
    type: "Word document",
    size: "128 KB"
  },
  {
    id: "ASSET-002",
    name: "connector drawing.pdf",
    role: "Supporting",
    type: "PDF",
    size: "640 KB"
  },
  {
    id: "ASSET-003",
    name: "test request context.xlsx",
    role: "Supporting",
    type: "Spreadsheet",
    size: "84 KB"
  }
];

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
  const candidate = ASSETS.find((asset) => asset.role === "Candidate");

  return (
    <section className="intake-package-detail">
      <button className="text-button" type="button" onClick={onBack}>
        Back to intake inbox
      </button>

      <div className="package-hero">
        <div>
          <p className="eyebrow">Package detail</p>
          <h2>{packageId}</h2>
          <p>Review source metadata and choose the application form asset before draft review.</p>
        </div>
        <span className="package-state">Ready for form selection</span>
      </div>

      <div className="package-detail-grid">
        <section className="source-panel">
          <div>
            <p className="eyebrow">Source</p>
            <h3>Original request preserved</h3>
          </div>
          <dl className="metadata-list">
            <div>
              <dt>Source type</dt>
              <dd>Outlook .msg</dd>
            </div>
            <div>
              <dt>Sender</dt>
              <dd>requester@example.com</dd>
            </div>
            <div>
              <dt>Subject</dt>
              <dd>Connector qualification request</dd>
            </div>
            <div>
              <dt>Storage state</dt>
              <dd>Source and attachments staged locally</dd>
            </div>
          </dl>
        </section>

        <section className="selection-panel">
          <div>
            <p className="eyebrow">Candidate</p>
            <h3>{candidate?.name ?? "No candidate detected"}</h3>
            <p>
              Candidate scoring uses file metadata only. Word content parsing and draft review are
              handled in later tasks.
            </p>
          </div>
          <button className="primary-action" disabled type="button">
            Select application form
          </button>
          <button className="secondary-action" type="button" onClick={onOpenCaseReview}>
            Preview draft review
          </button>
          <p className="selection-note">
            Selection endpoint is not wired in this UI task. This page defines the review surface and
            action placement.
          </p>
        </section>
      </div>

      <section className="asset-panel">
        <div className="asset-toolbar">
          <div>
            <p className="eyebrow">Attachments</p>
            <h3>Asset list</h3>
          </div>
          <span>{ASSETS.length} assets</span>
        </div>

        <div className="asset-list">
          {ASSETS.map((asset) => (
            <article className="asset-row" key={asset.id}>
              <div>
                <strong>{asset.name}</strong>
                <span>{asset.type} · {asset.size}</span>
              </div>
              <div className="asset-row-meta">
                {asset.score !== undefined && <span className="score-chip">Score {asset.score}</span>}
                <span className={`asset-role asset-role-${asset.role.toLowerCase()}`}>
                  {asset.role}
                </span>
              </div>
            </article>
          ))}
        </div>
      </section>
    </section>
  );
}
