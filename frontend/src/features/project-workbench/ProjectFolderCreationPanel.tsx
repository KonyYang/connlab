import { useEffect, useMemo, useState, type FormEvent, type ReactElement } from "react";
import {
  ApiRequestError,
  generateFolder,
  getLatestProjectFolder,
  previewFolder,
  type FolderGeneration,
  type FolderPlan,
  type FolderPlanItem,
  type FolderRequest,
  type ProjectFolderRecord
} from "../../api/client";

type ProjectFolderCreationPanelProps = {
  folderReady: boolean;
  latestLtrNumber: string | null;
  onFolderCreated: (generation: FolderGeneration) => Promise<void>;
  projectId: string;
  projectStatus: string | null;
};

export function ProjectFolderCreationPanel({
  folderReady,
  latestLtrNumber,
  onFolderCreated,
  projectId,
  projectStatus
}: ProjectFolderCreationPanelProps): ReactElement {
  const [folderInput, setFolderInput] = useState<FolderRequest>({
    template_path: "",
    target_root: "",
    dl_number: latestLtrNumber ?? ""
  });
  const [folderPlan, setFolderPlan] = useState<FolderPlan | null>(null);
  const [folderGeneration, setFolderGeneration] = useState<FolderGeneration | null>(null);
  const [folderRecord, setFolderRecord] = useState<ProjectFolderRecord | null>(null);
  const [previewing, setPreviewing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!folderInput.dl_number && latestLtrNumber) {
      setFolderInput((current) => ({ ...current, dl_number: latestLtrNumber }));
    }
  }, [folderInput.dl_number, latestLtrNumber]);

  useEffect(() => {
    if (!folderReady) {
      setFolderRecord(null);
      return;
    }
    let active = true;
    void getLatestProjectFolder(projectId)
      .then((record) => {
        if (active) {
          setFolderRecord(record);
          setError(null);
        }
      })
      .catch((err) => {
        if (active && !(err instanceof ApiRequestError && err.status === 404)) {
          setError((err as Error).message);
        }
      });
    return () => {
      active = false;
    };
  }, [folderReady, projectId]);

  const actionBlockedReason = useMemo(() => {
    if (!latestLtrNumber) {
      return "Apply an LTR number before creating the project folder.";
    }
    if (projectStatus !== "ltr_registered") {
      return "Folder creation is available only after LTR registration.";
    }
    return null;
  }, [latestLtrNumber, projectStatus]);

  const canPreview =
    !actionBlockedReason &&
    folderInput.template_path.trim().length > 0 &&
    folderInput.target_root.trim().length > 0;

  async function previewFolderNow(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setPreviewing(true);
    try {
      setFolderPlan(await previewFolder(projectId, cleanInput(folderInput, latestLtrNumber)));
      setFolderGeneration(null);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPreviewing(false);
    }
  }

  async function generateFolderNow(): Promise<void> {
    setGenerating(true);
    try {
      const generation = await generateFolder(projectId, cleanInput(folderInput, latestLtrNumber));
      setFolderGeneration(generation);
      setFolderPlan(null);
      setError(null);
      await onFolderCreated(generation);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setGenerating(false);
    }
  }

  if (folderReady || folderGeneration) {
    const path = folderGeneration?.project_folder_path ?? folderRecord?.project_folder_path ?? null;
    return (
      <section className="project-folder-workbench-panel">
        <div>
          <p className="eyebrow">Project folder</p>
          <h4>Folder created</h4>
          <p>Source material placement is available for this project.</p>
        </div>
        {path && (
          <div className="project-folder-path-card">
            <span>Recorded path</span>
            <code>{path}</code>
          </div>
        )}
        {error && <p className="blocking-copy">{error}</p>}
      </section>
    );
  }

  return (
    <section className="project-folder-workbench-panel">
      <div className="project-folder-workbench-heading">
        <div>
          <p className="eyebrow">Project folder</p>
          <h4>Create project folder</h4>
          <p>Preview the target folder before writing files. Conflicts block creation.</p>
        </div>
        {latestLtrNumber && <span className="status-chip">LTR {latestLtrNumber}</span>}
      </div>

      <form className="project-folder-form" onSubmit={(event) => void previewFolderNow(event)}>
        <label>
          Template path
          <input
            required
            placeholder="Project folder template path"
            value={folderInput.template_path}
            onChange={(event) => {
              setFolderInput({ ...folderInput, template_path: event.target.value });
              setFolderPlan(null);
            }}
          />
        </label>
        <label>
          Target root
          <input
            required
            placeholder="Project folder target root"
            value={folderInput.target_root}
            onChange={(event) => {
              setFolderInput({ ...folderInput, target_root: event.target.value });
              setFolderPlan(null);
            }}
          />
        </label>
        <label>
          LTR number
          <input
            value={folderInput.dl_number ?? ""}
            onChange={(event) => {
              setFolderInput({ ...folderInput, dl_number: event.target.value });
              setFolderPlan(null);
            }}
          />
        </label>
        <button className="primary-action" disabled={!canPreview || previewing || generating} type="submit">
          {previewing ? "Previewing..." : "Preview folder"}
        </button>
      </form>

      {actionBlockedReason && <p className="blocking-copy">{actionBlockedReason}</p>}
      {error && <p className="blocking-copy">{error}</p>}

      {folderPlan && (
        <div className={`folder-preview-card ${folderPlan.conflict ? "folder-preview-conflict" : ""}`}>
          <div className="folder-preview-heading">
            <div>
              <span>{folderPlan.conflict ? "Conflict detected" : "Clear to create"}</span>
              <strong>{leafName(folderPlan.project_folder_path)}</strong>
              <p className="fine-print">
                Target path: <code>{folderPlan.project_folder_path}</code>
              </p>
            </div>
            <button
              className="primary-action"
              disabled={folderPlan.conflict || generating}
              type="button"
              onClick={() => void generateFolderNow()}
            >
              {generating ? "Creating..." : "Create folder"}
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
    </section>
  );
}

function cleanInput(input: FolderRequest, latestLtrNumber: string | null): FolderRequest {
  const dlNumber = input.dl_number?.trim() || latestLtrNumber || undefined;
  return {
    template_path: input.template_path.trim(),
    target_root: input.target_root.trim(),
    dl_number: dlNumber
  };
}

function leafName(path: string): string {
  return path.split(/[\\/]/).filter(Boolean).at(-1) ?? path;
}

function itemLabel(item: FolderPlanItem): string {
  const prefix = item.item_type === "directory" ? "Folder" : "File";
  return `${prefix}: ${leafName(item.target_path)}`;
}
