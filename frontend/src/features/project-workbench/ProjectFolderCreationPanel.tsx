import { useEffect, useMemo, useState, type FormEvent, type ReactElement } from "react";
import {
  ApiRequestError,
  type ExternalResource,
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
  configuredOutputRoot: ExternalResource | null;
  configuredTemplate: ExternalResource | null;
  folderReady: boolean;
  latestLtrNumber: string | null;
  onFolderCreated: (generation: FolderGeneration) => Promise<void>;
  projectId: string;
  projectStatus: string | null;
};

export function ProjectFolderCreationPanel({
  configuredOutputRoot,
  configuredTemplate,
  folderReady,
  latestLtrNumber,
  onFolderCreated,
  projectId,
  projectStatus
}: ProjectFolderCreationPanelProps): ReactElement {
  const [folderPlan, setFolderPlan] = useState<FolderPlan | null>(null);
  const [folderGeneration, setFolderGeneration] = useState<FolderGeneration | null>(null);
  const [folderRecord, setFolderRecord] = useState<ProjectFolderRecord | null>(null);
  const [previewing, setPreviewing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    if (!configuredTemplate) {
      return "Configure Project folder template in Settings before previewing the project folder.";
    }
    if (!configuredTemplate.active) {
      return "Project folder template is inactive in Settings. Enable it before previewing the project folder.";
    }
    if (configuredTemplate.validation_status !== "valid") {
      if (configuredTemplate.validation_failure_reason) {
        return `Project folder template is not valid: ${configuredTemplate.validation_failure_reason}`;
      }
      return "Project folder template must be validated in Settings before previewing the project folder.";
    }
    if (!configuredOutputRoot) {
      return "Configure Project output root in Settings before previewing the project folder.";
    }
    if (!configuredOutputRoot.active) {
      return "Project output root is inactive in Settings. Enable it before previewing the project folder.";
    }
    if (configuredOutputRoot.validation_status !== "valid") {
      if (configuredOutputRoot.validation_failure_reason) {
        return `Project output root is not valid: ${configuredOutputRoot.validation_failure_reason}`;
      }
      return "Project output root must be validated in Settings before previewing the project folder.";
    }
    return null;
  }, [configuredOutputRoot, configuredTemplate, latestLtrNumber, projectStatus]);

  const folderRequest = useMemo(() => {
    if (!configuredTemplate || !configuredOutputRoot) {
      return null;
    }
    return cleanInput(configuredTemplate.path, configuredOutputRoot.path, latestLtrNumber);
  }, [configuredOutputRoot, configuredTemplate, latestLtrNumber]);

  const canPreview = !actionBlockedReason && Boolean(folderRequest);

  async function previewFolderNow(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!folderRequest) {
      return;
    }
    setPreviewing(true);
    try {
      setFolderPlan(await previewFolder(projectId, folderRequest));
      setFolderGeneration(null);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPreviewing(false);
    }
  }

  async function generateFolderNow(): Promise<void> {
    if (!folderRequest) {
      return;
    }
    setGenerating(true);
    try {
      const generation = await generateFolder(projectId, folderRequest);
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
        <div className="configured-resource-grid">
          <article className="configured-resource-card">
            <span>Project folder template</span>
            <code>{configuredTemplate?.path ?? "Not configured"}</code>
            <strong>{resourceStateLabel(configuredTemplate)}</strong>
          </article>
          <article className="configured-resource-card">
            <span>Project output root</span>
            <code>{configuredOutputRoot?.path ?? "Not configured"}</code>
            <strong>{resourceStateLabel(configuredOutputRoot)}</strong>
          </article>
          <article className="configured-resource-card">
            <span>LTR number</span>
            <code>{latestLtrNumber ?? "Not available"}</code>
            <strong>{latestLtrNumber ? "Ready" : "Missing"}</strong>
          </article>
        </div>
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

function cleanInput(
  templatePath: string,
  targetRoot: string,
  latestLtrNumber: string | null
): FolderRequest {
  const dlNumber = latestLtrNumber || undefined;
  return {
    template_path: templatePath.trim(),
    target_root: targetRoot.trim(),
    dl_number: dlNumber
  };
}

function resourceStateLabel(resource: ExternalResource | null): string {
  if (!resource) {
    return "Not configured";
  }
  if (!resource.active) {
    return "Inactive";
  }
  if (resource.validation_status === "valid") {
    return "Valid";
  }
  if (resource.validation_status === "invalid") {
    return "Invalid";
  }
  return "Not checked";
}

function leafName(path: string): string {
  return path.split(/[\\/]/).filter(Boolean).at(-1) ?? path;
}

function itemLabel(item: FolderPlanItem): string {
  const prefix = item.item_type === "directory" ? "Folder" : "File";
  return `${prefix}: ${leafName(item.target_path)}`;
}
