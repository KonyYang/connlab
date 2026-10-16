import { useEffect, useState, type ReactElement } from "react";
import { listManagedProjects, type ProjectRegistryAction, type ProjectRegistryEntry } from "../../api/projectRegistryManagement";
import { ProjectRecordIdentity } from "./ProjectRegistryManagementDialog";

export function ProjectRegistryManagementPanel({location, search, revision, onManage, onOpenProject}: {
  location: "trash" | "history"; search: string; revision: number;
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
    void listManagedProjects(location).then((result) => {if (current) setEntries(result);})
      .catch(() => {if (current) setError("Could not load retained projects. Retry to refresh this area.");})
      .finally(() => {if (current) setLoading(false);});
    return () => {current = false;};
  }, [location, revision, retry]);
  const query = search.trim().toLocaleLowerCase();
  const visible = entries.filter((entry) => [entry.display_project_id, entry.sample_description, entry.test_item,
    entry.requestor, entry.project_id].some((value) => value?.toLocaleLowerCase().includes(query)));
  return <section aria-label={location === "trash" ? "Recycle bin projects" : "Retained history projects"}>
    <p className="project-management-area-help">{location === "trash"
      ? "Deleted project records stay here until restored. Their files and business history are retained."
      : "Independent project records retained during conflict resolution. Restore them to normal management when needed."}</p>
    {loading ? <p role="status">Loading retained projects…</p> : error ? <div role="alert">{error} <button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div>
      : <>
        <p className="project-management-help">{visible.length} of {entries.length} {location === "trash" ? "recycled" : "historical"} project records</p>
        {!visible.length ? <p>No projects in this view.</p> : <div className="project-management-retained-list">{visible.map((entry) =>
          <article className="project-management-retained-row" key={entry.project_id}>
            <ProjectRecordIdentity project={entry} />
            <div className="project-management-help">{entry.reason && <p>{entry.reason}</p>}<p>Moved {entry.changed_at || "date not recorded"}</p></div>
            <div className="project-management-row-actions">
              <button type="button" className="row-action" onClick={() => onOpenProject(entry.project_id)}>View read-only details</button>
              <button type="button" className="row-action" onClick={() => onManage(entry.project_id, "restore")}>Restore</button>
              {location === "history" && <button type="button" className="row-action" onClick={() => onManage(entry.project_id, "trash")}>Delete project</button>}
            </div>
          </article>
        )}</div>}
      </>}
  </section>;
}
