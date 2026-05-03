import type { FormEvent, ReactElement } from "react";
import type {
  EvidencePlacementPlan,
  EvidencePlacementResult,
  FolderGeneration,
  FolderPlan,
  FolderPlanItem,
  FolderRequest
} from "../../api/client";
import { lifecycleBlockReason } from "./lifecycleGuards";

type FolderActionPanelProps = {
  evidencePlan: EvidencePlacementPlan | null;
  evidenceResult: EvidencePlacementResult | null;
  folderGeneration: FolderGeneration | null;
  folderInput: FolderRequest;
  folderPlan: FolderPlan | null;
  placingEvidence: boolean;
  onGenerate: () => Promise<void>;
  onPlaceEvidence: () => Promise<void>;
  onPreview: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  onPreviewEvidence: () => Promise<void>;
  previewingEvidence: boolean;
  projectStatus?: string | null;
  setFolderInput: (value: FolderRequest) => void;
};

function leafName(path: string): string {
  return path.split(/[\\/]/).filter(Boolean).at(-1) ?? path;
}

function itemLabel(item: FolderPlanItem): string {
  const prefix = item.item_type === "directory" ? "Folder" : "File";
  return `${prefix}: ${leafName(item.target_path)}`;
}

export function FolderActionPanel({
  evidencePlan,
  evidenceResult,
  folderGeneration,
  folderInput,
  folderPlan,
  placingEvidence,
  onGenerate,
  onPlaceEvidence,
  onPreview,
  onPreviewEvidence,
  previewingEvidence,
  projectStatus,
  setFolderInput
}: FolderActionPanelProps): ReactElement {
  const folderPreviewBlockReason = lifecycleBlockReason(projectStatus, "folder_preview");
  const folderGenerateBlockReason = lifecycleBlockReason(projectStatus, "folder_generate");
  const evidencePlaceBlockReason = lifecycleBlockReason(projectStatus, "evidence_place");

  return (
    <div className="action-panel-body">
      <div className="operator-panel">
        <div>
          <p className="eyebrow">Folder preparation</p>
          <h4>{folderGeneration ? "Folder generated" : folderPlan ? "Preview ready" : "Preview project folder"}</h4>
          <p>Preview folder and file actions first. Generation stays disabled when conflicts exist.</p>
        </div>
        <form className="card-form folder-preview-panel" onSubmit={onPreview}>
          <input
            required
            placeholder="Template path"
            value={folderInput.template_path}
            onChange={(event) => setFolderInput({ ...folderInput, template_path: event.target.value })}
          />
          <input
            required
            placeholder="Target root"
            value={folderInput.target_root}
            onChange={(event) => setFolderInput({ ...folderInput, target_root: event.target.value })}
          />
          <input
            placeholder="LTR Number"
            value={folderInput.dl_number ?? ""}
            onChange={(event) => setFolderInput({ ...folderInput, dl_number: event.target.value })}
          />
          {folderPreviewBlockReason && <p className="blocking-copy">{folderPreviewBlockReason}</p>}
          <button
            className="primary-action"
            disabled={Boolean(folderPreviewBlockReason)}
            type="submit"
          >
            Preview folder
          </button>
        </form>
      </div>

      {folderPlan && (
        <div className={`folder-preview-card ${folderPlan.conflict ? "folder-preview-conflict" : ""}`}>
          <div className="folder-preview-heading">
            <div>
              <span>{folderPlan.conflict ? "Conflict detected" : "Clear to generate"}</span>
              <strong>{leafName(folderPlan.project_folder_path)}</strong>
            </div>
            <button
              className="primary-action"
              disabled={folderPlan.conflict || Boolean(folderGenerateBlockReason)}
              type="button"
              onClick={() => void onGenerate()}
            >
              Generate folder
            </button>
          </div>
          <ul className="folder-tree-preview">
            {folderPlan.items.map((item) => (
              <li className={item.conflict ? "folder-tree-conflict" : ""} key={item.target_path} title={item.target_path}>
                {itemLabel(item)}
                {item.conflict && <span>conflict</span>}
              </li>
            ))}
          </ul>
          {folderGenerateBlockReason && <p className="blocking-copy">{folderGenerateBlockReason}</p>}
        </div>
      )}

      {folderGeneration && (
        <div className="latest-ltr-card">
          <span>Generated</span>
          <strong>{leafName(folderGeneration.project_folder_path)}</strong>
          <p>{folderGeneration.generated_paths.length} paths created.</p>
        </div>
      )}

      <section className="evidence-placement-panel">
        <div className="evidence-placement-heading">
          <div>
            <p className="eyebrow">Evidence placement</p>
            <h4>{evidencePlan ? "Evidence preview ready" : "Preview evidence copy"}</h4>
            <p>
              Source email, selected application form, attachments, specifications, LTR evidence,
              and correction evidence are copied only after a clear preview.
            </p>
          </div>
          <button
            className="secondary-action"
            disabled={previewingEvidence}
            type="button"
            onClick={() => void onPreviewEvidence()}
          >
            {previewingEvidence ? "Previewing..." : "Preview evidence"}
          </button>
        </div>

        {evidencePlan && (
          <div className={`evidence-plan-card ${evidencePlan.conflict ? "evidence-plan-conflict" : ""}`}>
            <div className="folder-preview-heading">
              <div>
                <span>{evidencePlan.conflict ? "Conflicts block copy" : "No-overwrite copy ready"}</span>
                <strong>{leafName(evidencePlan.evidence_root_path)}</strong>
              </div>
              <button
                className="primary-action"
                disabled={placingEvidence || evidencePlan.conflict || Boolean(evidencePlaceBlockReason)}
                type="button"
                onClick={() => void onPlaceEvidence()}
              >
                {placingEvidence ? "Placing..." : "Place evidence"}
              </button>
            </div>
            {(evidencePlan.conflicts.length > 0 || evidencePlan.warnings.length > 0) && (
              <ul className="message-list">
                {[...evidencePlan.conflicts, ...evidencePlan.warnings].map((message) => (
                  <li key={message}>{message}</li>
                ))}
              </ul>
            )}
            <ul className="evidence-item-list">
              {evidencePlan.items.map((item) => (
                <li className={item.conflict ? "evidence-item-conflict" : ""} key={item.asset_id}>
                  <div>
                    <strong>{categoryLabel(item.category)}</strong>
                    <span>{leafName(item.source_path)} to {leafName(item.target_path)}</span>
                  </div>
                  <em>{itemStatus(item)}</em>
                </li>
              ))}
            </ul>
            {evidencePlaceBlockReason && <p className="blocking-copy">{evidencePlaceBlockReason}</p>}
          </div>
        )}

        {evidenceResult && (
          <div className="latest-ltr-card">
            <span>Evidence placed</span>
            <strong>{evidenceResult.copied_paths.length} files copied</strong>
            <p>No existing target files were overwritten.</p>
          </div>
        )}
      </section>
    </div>
  );
}

function categoryLabel(category: string): string {
  const labels: Record<string, string> = {
    application_form: "Application form",
    correction: "Correction evidence",
    email: "Source email",
    ltr_evidence: "LTR evidence",
    photo: "Photo",
    specification: "Specification",
    supporting_attachment: "Supporting attachment"
  };
  return labels[category] ?? category;
}

function itemStatus(item: { conflict: boolean; duplicate_target: boolean; missing_source: boolean; target_exists: boolean }): string {
  if (item.missing_source) {
    return "missing source";
  }
  if (item.target_exists) {
    return "target exists";
  }
  if (item.duplicate_target) {
    return "duplicate target";
  }
  return item.conflict ? "conflict" : "ready";
}
