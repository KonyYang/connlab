import type { ReactElement } from "react";
import type { Project } from "../../api/client";
import { ProjectStatusBadge } from "./ProjectStatusBadge";

type ProjectSummaryPanelProps = {
  project: Project;
  onBack: () => void;
};

export function ProjectSummaryPanel({
  project,
  onBack
}: ProjectSummaryPanelProps): ReactElement {
  return (
    <section className="project-summary-panel">
      <button className="text-button" type="button" onClick={onBack}>
        Back to projects
      </button>
      <div className="project-summary-grid">
        <div>
          <p className="eyebrow">Workbench</p>
          <h2>{project.product_name}</h2>
          <p className="section-summary">Project workflow for intake, precheck, LTR, and folder preparation.</p>
        </div>
        <dl className="project-summary-facts">
          <div>
            <dt>Project No.</dt>
            <dd>{project.project_no}</dd>
          </div>
          <div>
            <dt>Requestor</dt>
            <dd>{project.requestor}</dd>
          </div>
          <div>
            <dt>Business Unit</dt>
            <dd>{project.business_unit || "Not set"}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd><ProjectStatusBadge status={project.status} /></dd>
          </div>
        </dl>
      </div>
    </section>
  );
}
