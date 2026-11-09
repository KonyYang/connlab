import { useState } from "react";
import type { PublicProjectFolderBindingPreview } from "../../api/client";
import { ProjectManagementDialog } from "../projects-registry/ProjectRegistryManagementDialog";

export function ProjectPublicFolderBindingDialog({preview, busy, error, onConfirm, onCancel}: {
  preview: PublicProjectFolderBindingPreview; busy: boolean; error: string | null;
  onConfirm: (candidateId: string) => void | Promise<void>; onCancel: () => void;
}) {
  const [candidate, setCandidate] = useState(preview.candidates.length === 1
    ? preview.candidates[0].candidate_id : preview.can_create && !preview.candidates.length ? "create" : "");
  return <ProjectManagementDialog title="Public project folder" busy={busy} onCancel={onCancel} className="project-folder-binding-dialog">
    <strong>{preview.full_ltr_number}</strong>
    <p className="project-management-help">Confirm the public folder for this project before syncing.</p>
    <div className="project-folder-binding-choices">
      {preview.candidates.map(item => <label key={item.candidate_id}>
        <input type="radio" name="public-folder-candidate" value={item.candidate_id} checked={candidate === item.candidate_id} disabled={busy} onChange={() => setCandidate(item.candidate_id)} />
        <span>{item.path}</span>
      </label>)}
      {preview.can_create && preview.proposed_path ? <label>
        <input type="radio" name="public-folder-candidate" value="create" checked={candidate === "create"} disabled={busy} onChange={() => setCandidate("create")} />
        <span>{preview.proposed_path}</span>
      </label> : null}
    </div>
    {error ? <p role="alert">{error}</p> : null}
    {preview.blockers.map(blocker => <p key={blocker} role="alert">{blocker}</p>)}
    <div className="project-management-dialog-actions">
      <button className="secondary-action ui-secondary-action" type="button" disabled={busy} onClick={onCancel}>Cancel</button>
      <button className="primary-action ui-primary-action" type="button" disabled={busy || !candidate || preview.status === "blocked" || Boolean(preview.blockers.length)} onClick={() => void onConfirm(candidate)}>
        {candidate === "create" ? "Create project folder" : "Use this folder"}
      </button>
    </div>
  </ProjectManagementDialog>;
}
