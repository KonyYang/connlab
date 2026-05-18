import type { ReactElement } from "react";
import type { WorkbenchVersionStatus } from "./projectWorkbenchVersionSelectors";

type ProjectWorkbenchDocumentStatusPanelProps = {
  status: WorkbenchVersionStatus;
};

export function ProjectWorkbenchDocumentStatusPanel({
  status
}: ProjectWorkbenchDocumentStatusPanelProps): ReactElement {
  return (
    <section className="workbench-document-status-panel">
      <header className="workbench-document-status-heading">
        <div>
          <h4>Derived outputs</h4>
          <p>Output sync visibility against current Matrix authority.</p>
        </div>
        <strong>
          Draft v{status.activeDraftVersion ?? "-"}
          {status.trackedDraftVersion ? ` / tracked v${status.trackedDraftVersion}` : ""}
        </strong>
      </header>
      {status.hasStaleOutputs ? (
        <p className="blocking-copy">
          Some derived outputs are stale after authority changes. Refresh output generation or
          preview before final package placement.
        </p>
      ) : null}
      <ul className="workbench-document-status-list">
        {status.downstream.map((item) => (
          <li key={item.key}>
            <div>
              <strong>{item.label}</strong>
              <span>{item.reason}</span>
              {item.path ? <code>{item.path}</code> : null}
            </div>
            <em className={`workbench-status-badge workbench-status-${item.freshness}`}>
              {item.freshness}
            </em>
          </li>
        ))}
      </ul>
    </section>
  );
}
