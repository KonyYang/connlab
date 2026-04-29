import { useDeferredValue, useEffect, useState, type FormEvent, type ReactElement } from "react";
import {
  createProject,
  listProjects,
  type Project,
  type ProjectCreateInput
} from "../api/client";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { ProjectStatusBadge } from "../components/project/ProjectStatusBadge";
import "../project-dashboard.css";

type ProjectListPageProps = {
  onOpenProject: (projectId: string) => void;
};

const EMPTY_PROJECT: ProjectCreateInput = {
  project_no: "",
  product_name: "",
  requestor: "",
  business_unit: ""
};

export function ProjectListPage({ onOpenProject }: ProjectListPageProps): ReactElement {
  const [projects, setProjects] = useState<Project[]>([]);
  const [form, setForm] = useState<ProjectCreateInput>(EMPTY_PROJECT);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const deferredSearch = useDeferredValue(search);

  const query = deferredSearch.trim().toLowerCase();
  const filteredProjects = query
    ? projects.filter((project) =>
        [
          project.project_no,
          project.product_name,
          project.requestor,
          project.business_unit ?? "",
          project.status
        ]
          .join(" ")
          .toLowerCase()
          .includes(query)
      )
    : projects;

  useEffect(() => {
    void refreshProjects();
  }, []);

  async function refreshProjects(): Promise<void> {
    setLoading(true);
    try {
      setProjects(await listProjects());
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function submitProject(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSaving(true);
    try {
      const project = await createProject(form);
      setForm(EMPTY_PROJECT);
      setProjects((current) => [project, ...current]);
      setError(null);
      onOpenProject(project.project_id);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="project-dashboard">
      <div className="section-heading dashboard-heading">
        <div>
          <p className="eyebrow">Projects</p>
          <h2>Project registry</h2>
          <p className="section-summary">
            Track active connector lab requests and open the next workflow step.
          </p>
        </div>
        <div className="dashboard-count">
          <strong>{projects.length}</strong>
          <span>stored projects</span>
        </div>
      </div>

      <div className="dashboard-layout">
        <aside className="new-project-panel">
          <div>
            <p className="eyebrow">New project</p>
            <h3>Register request</h3>
            <p>Create the project shell before importing application material.</p>
          </div>
          <form className="compact-form" onSubmit={submitProject}>
            <label>
              Project No. (optional)
              <input
                value={form.project_no ?? ""}
                onChange={(event) => setForm({ ...form, project_no: event.target.value })}
              />
            </label>
            <label>
              Product Name
              <input
                required
                value={form.product_name}
                onChange={(event) => setForm({ ...form, product_name: event.target.value })}
              />
            </label>
            <label>
              Requestor
              <input
                required
                value={form.requestor}
                onChange={(event) => setForm({ ...form, requestor: event.target.value })}
              />
            </label>
            <label>
              Business Unit
              <input
                value={form.business_unit ?? ""}
                onChange={(event) => setForm({ ...form, business_unit: event.target.value })}
              />
            </label>
            <button className="primary-action" disabled={saving} type="submit">
              {saving ? "Creating..." : "Create project"}
            </button>
          </form>
        </aside>

        <div className="project-register-panel">
          <div className="register-toolbar">
            <div>
              <h3>Active work queue</h3>
              <p>Search by DL, project reference, product, requestor, business unit, or status.</p>
            </div>
            <label className="search-field">
              Search projects
              <input
                placeholder="DL, product, requestor..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </label>
          </div>

          {loading && <LoadingState label="Loading project registry..." />}
          {error && <ErrorMessage message={error} />}
          {!loading && !error && projects.length === 0 && (
            <EmptyState
              title="No projects yet"
              message="Create the first project record to start the MVP workflow."
            />
          )}
          {!loading && !error && projects.length > 0 && filteredProjects.length === 0 && (
            <EmptyState
              title="No matching projects"
              message="Adjust the search text to return to the full project registry."
            />
          )}
          {!loading && !error && filteredProjects.length > 0 && (
            <div className="project-table-wrap">
              <table className="project-table">
                <thead>
                  <tr>
                    <th>Project Ref.</th>
                    <th>Product</th>
                    <th>Requestor</th>
                    <th>Business Unit</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProjects.map((project) => (
                    <tr key={project.project_id}>
                      <td className="project-no">{project.project_no || "Not set"}</td>
                      <td>{project.product_name}</td>
                      <td>{project.requestor}</td>
                      <td>{project.business_unit || "Not set"}</td>
                      <td><ProjectStatusBadge status={project.status} /></td>
                      <td>
                        <button
                          className="row-action"
                          type="button"
                          onClick={() => onOpenProject(project.project_id)}
                        >
                          Open
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
