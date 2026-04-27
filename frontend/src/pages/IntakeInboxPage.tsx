import type { ReactElement } from "react";
import "../intake-inbox.css";

type IntakePackageRow = {
  id: string;
  source: string;
  received: string;
  sender: string;
  subject: string;
  assets: number;
  state: "Needs candidate review" | "Ready for form selection" | "Draft pending";
};

const SAMPLE_PACKAGES: IntakePackageRow[] = [
  {
    id: "PKG-LOCAL-001",
    source: "Outlook .msg",
    received: "Today",
    sender: "requester@example.com",
    subject: "Connector qualification request",
    assets: 4,
    state: "Ready for form selection"
  },
  {
    id: "PKG-LOCAL-002",
    source: "Direct Word",
    received: "Waiting",
    sender: "Manual import",
    subject: "Application form review",
    assets: 1,
    state: "Needs candidate review"
  }
];

type IntakeInboxPageProps = {
  onOpenPackage: (packageId: string) => void;
};

export function IntakeInboxPage({ onOpenPackage }: IntakeInboxPageProps): ReactElement {
  return (
    <section className="intake-inbox">
      <div className="intake-page-heading">
        <div>
          <p className="eyebrow">Intake</p>
          <h2>Request material inbox</h2>
          <p>
            Stage Outlook packages and direct Word forms before creating a formal
            project record.
          </p>
        </div>
        <span className="queue-badge">Phase 6A preview</span>
      </div>

      <div className="intake-grid">
        <aside className="intake-import-panel" aria-label="Import request material">
          <div>
            <p className="eyebrow">Import source</p>
            <h3>Bring request material into review</h3>
            <p>
              Preserve the original email or document first. Candidate detection,
              form selection, and draft review happen after import.
            </p>
          </div>

          <div className="import-actions">
            <button className="primary-action" disabled type="button">
              Import .msg package
            </button>
            <button className="secondary-action" disabled type="button">
              Import Word form
            </button>
          </div>

          <p className="intake-note">
            Import endpoints are not wired in this UI task. This panel establishes
            the entry point without pretending the full flow is active.
          </p>
        </aside>

        <div className="intake-queue-panel">
          <div className="queue-toolbar">
            <div>
              <h3>Review queue</h3>
              <p>Packages wait here until a user confirms the application form.</p>
            </div>
            <div className="queue-summary">
              <strong>{SAMPLE_PACKAGES.length}</strong>
              <span>visible packages</span>
            </div>
          </div>

          <div className="intake-table-wrap">
            <table className="intake-table">
              <thead>
                <tr>
                  <th>Package</th>
                  <th>Source</th>
                  <th>Sender</th>
                  <th>Subject</th>
                  <th>Assets</th>
                  <th>State</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {SAMPLE_PACKAGES.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.id}</strong>
                      <span>{item.received}</span>
                    </td>
                    <td>{item.source}</td>
                    <td>{item.sender}</td>
                    <td>{item.subject}</td>
                    <td>{item.assets}</td>
                    <td>
                      <span className="state-chip">{item.state}</span>
                    </td>
                    <td>
                      <button className="row-action" type="button" onClick={() => onOpenPackage(item.id)}>
                        Review
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="intake-boundary-panel">
        <div>
          <p className="eyebrow">Current boundary</p>
          <h3>Human confirmation remains required</h3>
        </div>
        <ol>
          <li>Store the original package and attachments.</li>
          <li>Detect likely application forms from attachment metadata.</li>
          <li>Select one form and create a draft for later review.</li>
        </ol>
      </div>
    </section>
  );
}
