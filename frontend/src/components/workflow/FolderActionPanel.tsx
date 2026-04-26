import type { FormEvent, ReactElement } from "react";
import type { FolderGeneration, FolderPlan, FolderPlanItem, FolderRequest } from "../../api/client";

type FolderActionPanelProps = {
  folderGeneration: FolderGeneration | null;
  folderInput: FolderRequest;
  folderPlan: FolderPlan | null;
  onGenerate: () => Promise<void>;
  onPreview: (event: FormEvent<HTMLFormElement>) => Promise<void>;
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
  folderGeneration,
  folderInput,
  folderPlan,
  onGenerate,
  onPreview,
  setFolderInput
}: FolderActionPanelProps): ReactElement {
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
            placeholder="DL number"
            value={folderInput.dl_number ?? ""}
            onChange={(event) => setFolderInput({ ...folderInput, dl_number: event.target.value })}
          />
          <button className="primary-action" type="submit">Preview folder</button>
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
              disabled={folderPlan.conflict}
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
        </div>
      )}

      {folderGeneration && (
        <div className="latest-ltr-card">
          <span>Generated</span>
          <strong>{leafName(folderGeneration.project_folder_path)}</strong>
          <p>{folderGeneration.generated_paths.length} paths created.</p>
        </div>
      )}
    </div>
  );
}
