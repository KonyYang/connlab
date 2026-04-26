import { useEffect, useState, type FormEvent, type ReactElement } from "react";
import {
  createProject,
  listProjects,
  type Project,
  type ProjectCreateInput
} from "../api/client";

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
    <section className="panel">
      <div className="section-heading">
        <p className="eyebrow">Projects</p>
        <h2>Start or resume MVP workflow</h2>
      </div>

      <form className="workflow-form" onSubmit={submitProject}>
        <label>
          Project No.
          <input
            required
            value={form.project_no}
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

      {loading && <p>Loading projects...</p>}
      {error && <p className="error">Workflow error: {error}</p>}
      {!loading && !error && projects.length === 0 && <p>No projects found.</p>}
      <div className="project-grid">
        {projects.map((project) => (
          <button
            className="project-card"
            key={project.project_id}
            type="button"
            onClick={() => onOpenProject(project.project_id)}
          >
            <span>{project.project_no}</span>
            <strong>{project.product_name}</strong>
            <small>{project.status}</small>
          </button>
        ))}
      </div>
    </section>
  );
}
