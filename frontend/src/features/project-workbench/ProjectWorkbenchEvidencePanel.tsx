import type { ReactElement } from "react";
import type {
  EvidencePlacementPlan,
  EvidencePlacementResult
} from "../../api/client";

type ProjectWorkbenchEvidencePanelProps = {
  folderReady: boolean;
  evidencePlan: EvidencePlacementPlan | null;
  evidenceResult: EvidencePlacementResult | null;
  previewingEvidence: boolean;
  placingEvidence: boolean;
  onPreviewEvidence: () => Promise<void>;
  onPlaceEvidence: () => Promise<void>;
};

export function ProjectWorkbenchEvidencePanel({
  folderReady,
  evidencePlan,
  evidenceResult,
  previewingEvidence,
  placingEvidence,
  onPreviewEvidence,
  onPlaceEvidence
}: ProjectWorkbenchEvidencePanelProps): ReactElement {
  return (
    <section className="evidence-placement-panel">
      <div className="evidence-placement-heading">
        <div>
          <h4>Evidence placement</h4>
          <p>
            Preview and place source materials into the project folder after project creation.
          </p>
        </div>
        <div className="action-row">
          <button
            className="secondary-action"
            disabled={!folderReady || previewingEvidence || placingEvidence}
            type="button"
            onClick={() => void onPreviewEvidence()}
          >
            {previewingEvidence ? "Previewing..." : "Preview evidence placement"}
          </button>
          <button
            className="primary-action"
            disabled={!folderReady || placingEvidence || !evidencePlan}
            type="button"
            onClick={() => void onPlaceEvidence()}
          >
            {placingEvidence ? "Placing..." : "Place evidence"}
          </button>
        </div>
      </div>

      {evidencePlan && (
        <div
          className={
            evidencePlan.conflict
              ? "evidence-plan-card evidence-plan-conflict"
              : "evidence-plan-card"
          }
        >
          <strong>
            {evidencePlan.conflict
              ? "Evidence placement has conflicts"
              : "Evidence placement preview is ready"}
          </strong>
          <p className="fine-print">
            Project folder: <code>{evidencePlan.project_folder_path}</code>
          </p>
          <ul className="evidence-item-list">
            {evidencePlan.items.map((item) => (
              <li
                className={item.conflict ? "evidence-item-conflict" : undefined}
                key={`${item.asset_id}-${item.target_path}`}
              >
                <div>
                  <strong>{assetLabel(item.source_path, item.asset_id)}</strong>
                  <span>
                    {item.category} {"->"} {item.target_path}
                  </span>
                </div>
                <em>{item.conflict ? "Conflict" : "Ready"}</em>
              </li>
            ))}
          </ul>
        </div>
      )}

      {evidenceResult && (
        <div className="message-list message-list-warning">
          <strong>Evidence placement result</strong>
          <ul>
            <li>Copied files: {evidenceResult.copied_paths.length}</li>
            <li>Skipped files: {evidenceResult.plan.conflicts.length}</li>
          </ul>
        </div>
      )}
    </section>
  );
}

function assetLabel(sourcePath: string, assetId: string): string {
  const normalized = sourcePath.replace(/\\/g, "/");
  const lastSegment = normalized.split("/").pop();
  return lastSegment && lastSegment.trim() ? lastSegment : assetId;
}
