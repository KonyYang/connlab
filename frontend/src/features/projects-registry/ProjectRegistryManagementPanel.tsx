import { useEffect, useState, type ReactElement } from "react";
import { listManagedProjects, type ProjectRegistryAction, type ProjectRegistryEntry } from "../../api/projectRegistryManagement";
import { ProjectRecordIdentity } from "./ProjectRegistryManagementDialog";

const reasonLabel = (entry: ProjectRegistryEntry) => entry.registry_state === "trash" ? "Deleted" : "Retained after conflict";

export function ProjectRegistryManagementPanel({search, revision, onManage, onOpenProject}: {
  search: string; revision: number;
  onManage: (projectId: string, action: ProjectRegistryAction) => void;
  onOpenProject: (projectId: string) => void;
}): ReactElement {
  const [entries, setEntries] = useState<ProjectRegistryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let current = true;
    setLoading(true); setEntries([]); setError(null);
    void Promise.allSettled([listManagedProjects("trash"), listManagedProjects("history")]).then(results => {
      if (!current) return;
      const records = new Map<string, ProjectRegistryEntry>();
      for (const result of results) {
        if (result.status !== "fulfilled") continue;
        for (const entry of result.value) {
          if (entry.registry_state === "active") continue;
          const previous = records.get(entry.project_id);
          // The record may move between the two reads. Prefer its latest revision, never a matching LTR.
          if (!previous || entry.registry_revision > previous.registry_revision) records.set(entry.project_id, entry);
        }
      }
      setEntries([...records.values()].sort((a, b) => (b.changed_at ?? "").localeCompare(a.changed_at ?? "") || a.project_id.localeCompare(b.project_id)));
      setError(results.some(result => result.status === "rejected") ? "Some records could not be loaded. Retry to show the complete Recycle list." : null);
      setLoading(false);
    });
    return () => {current = false;};
  }, [revision, retry]);
  const query = search.trim().toLocaleLowerCase();
  const visible = entries.filter(entry => [entry.display_project_id, entry.sample_description, entry.test_item,
    entry.requestor, entry.project_id, entry.reason, reasonLabel(entry)].some(value => value?.toLocaleLowerCase().includes(query)));
  return <section aria-label="Recycle bin projects">
    <p className="project-management-area-help">Deleted and conflict-retained project records stay here until restored. Their files and data are retained.</p>
    {loading ? <p role="status">Loading Recycle records…</p> : <>
      {error && <div role="alert">{error} <button type="button" onClick={() => setRetry(value => value + 1)}>Retry</button></div>}
      <p className="project-management-help">{visible.length} of {entries.length} records in Recycle</p>
      {!visible.length ? !error && <p>No projects in this view.</p> : <div className="project-management-retained-list">{visible.map(entry =>
        <article className="project-management-retained-row" key={entry.project_id}>
          <ProjectRecordIdentity project={entry} />
          <div className="project-management-help"><strong>{reasonLabel(entry)}</strong>{entry.reason && <p>{entry.reason}</p>}<p>Moved {entry.changed_at || "date not recorded"}</p></div>
          <div className="project-management-row-actions">
            <button type="button" className="row-action" onClick={() => onOpenProject(entry.project_id)}>View read-only details</button>
            <button type="button" className="row-action" onClick={() => onManage(entry.project_id, "restore")}>Restore</button>
          </div>
        </article>
      )}</div>}
    </>}
  </section>;
}
