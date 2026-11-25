import { useEffect, useRef, useState } from "react";
import { ApiRequestError, pickExternalResourcePath } from "../../api/client";
import {
  abandonFolderResolution, applyFolderResolution, previewFolderResolution, resumeFolderResolution,
  type FolderResolutionChoice, type FolderResolutionPreview,
} from "../../api/projectFolderResolution";
import { ProjectManagementDialog } from "../projects-registry/ProjectRegistryManagementDialog";

export function ProjectFolderResolutionDialog({projectId, registeredPath, pendingOperation, onCancel, onRecheck, onResolved}: {
  projectId: string; registeredPath: string; pendingOperation: string | null;
  onCancel: () => void; onRecheck: () => Promise<void>; onResolved: () => void;
}) {
  const [choice, setChoice] = useState<FolderResolutionChoice>({strategy: "relink", path: null});
  const [preview, setPreview] = useState<FolderResolutionPreview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [checking, setChecking] = useState(false);
  const [interrupted, setInterrupted] = useState<string | null>(null);
  const operation = pendingOperation ?? interrupted;
  const alive = useRef(true);
  const locked = useRef(false);
  const requestId = useRef("");
  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; };
  }, []);

  useEffect(() => {
    let active = true;
    if (operation || (choice.strategy === "relink" && !choice.path)) {
      setChecking(false);
      return;
    }
    setChecking(true);
    previewFolderResolution(projectId, choice).then(value => {
      if (active && value.project_id === projectId && value.strategy === choice.strategy) setPreview(value);
    }).catch(reason => {
      if (active) setError(reason instanceof Error ? reason.message : "Could not check the selected folder.");
    }).finally(() => { if (active) setChecking(false); });
    return () => { active = false; };
  }, [choice, operation, projectId]);

  function select(next: FolderResolutionChoice) {
    setPreview(null);
    setError(null);
    requestId.current = "";
    setChoice(next);
  }

  async function browse() {
    if (locked.current) return;
    locked.current = true;
    setBusy(true);
    try {
      const {path} = await pickExternalResourcePath("project_output_root");
      if (path && alive.current) select({...choice, path});
    } catch (reason) {
      if (alive.current) setError(reason instanceof Error ? reason.message : "Could not open the folder picker.");
    } finally {
      locked.current = false;
      if (alive.current) setBusy(false);
    }
  }

  async function confirm(keepPrevious = false) {
    if (locked.current || (keepPrevious ? !operation : !operation && !preview)) return;
    locked.current = true;
    setBusy(true);
    setError(null);
    try {
      if (keepPrevious && operation) {
        await abandonFolderResolution(projectId, operation);
        if (alive.current) onResolved();
        return;
      }
      requestId.current ||= crypto.randomUUID();
      const result = operation ? await resumeFolderResolution(projectId, operation)
        : await applyFolderResolution(projectId, choice, preview!.expected_context, requestId.current);
      if (!alive.current) return;
      if (result.directory_available && result.status === "completed") {
        onResolved();
      } else {
        setError([result.message, ...result.issues].filter(Boolean).join(" ") || "Folder setup is incomplete. Resume to continue.");
        setInterrupted(result.operation_id);
        await onRecheck();
      }
    } catch (reason) {
      if (!alive.current) return;
      setError(reason instanceof Error ? reason.message : "Could not finish the folder change. Retry to check this operation.");
      if (reason instanceof ApiRequestError && reason.status === 409) setPreview(null);
      await onRecheck();
    } finally {
      locked.current = false;
      if (alive.current) setBusy(false);
    }
  }

  const relink = choice.strategy === "relink";
  return <ProjectManagementDialog title="Resolve project folder" busy={busy} onCancel={onCancel} className="project-folder-binding-dialog">
    <div className="project-management-record"><strong>Registered folder</strong><span className="project-basic-folder-path">{preview?.old_path ?? registeredPath}</span></div>
    {operation ? <p>Resume the unfinished change or keep the previous registered location. Files already created stay in place.</p> : <>
      <div className="project-folder-binding-choices" role="radiogroup" aria-label="Folder action">
        <label><input type="radio" name="folder-resolution" checked={relink} disabled={busy} onChange={() => select({strategy: "relink", path: null})} />Link existing project folder</label>
        <label><input type="radio" name="folder-resolution" checked={!relink} disabled={busy} onChange={() => select({strategy: "recreate", path: null})} />Create a new working folder</label>
      </div>
      <p className="project-management-help">{relink
        ? "Choose the moved project folder. ConnLab will check its project identity."
        : "Creates the basic folder structure. Recover original documents and manually edited files from your backup."}</p>
      <button className="secondary-action ui-secondary-action" type="button" disabled={busy} onClick={() => void browse()}>
        {relink ? "Choose project folder…" : "Choose another parent folder…"}
      </button>
      {!relink && choice.path && <button type="button" className="secondary-action ui-secondary-action" disabled={busy} onClick={() => select({strategy: "recreate", path: null})}>Use default location</button>}
      {checking && <p role="status">Checking folder…</p>}
      {preview && <div className="project-management-record"><strong>{relink ? "Link to" : "Create in"}</strong><span className="project-basic-folder-path">{preview.target_path}</span></div>}
    </>}
    {error && <p role="alert" className="project-delete-error">{error}</p>}
    {error && !operation && !preview && (choice.path || !relink) && <button className="secondary-action ui-secondary-action" type="button" disabled={busy || checking} onClick={() => select({...choice})}>Refresh preview</button>}
    <div className="project-management-dialog-actions">
      <button className="secondary-action ui-secondary-action" type="button" disabled={busy} onClick={onCancel}>Cancel</button>
      {operation && <button className="secondary-action ui-secondary-action" type="button" disabled={busy} onClick={() => void confirm(true)}>Keep previous location</button>}
      <button className="primary-action ui-primary-action" type="button" disabled={busy || (!operation && !preview)} onClick={() => void confirm()}>
        {operation ? "Resume folder change" : relink ? "Link folder" : "Create working folder"}
      </button>
    </div>
  </ProjectManagementDialog>;
}
