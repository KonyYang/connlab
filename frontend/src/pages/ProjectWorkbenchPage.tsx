import { useEffect, useMemo, useState, type ReactElement } from "react";
import {
  getProject,
  listProjectLtrs,
  placeEvidence,
  previewEvidencePlacement,
  type EvidencePlacementPlan,
  type EvidencePlacementResult,
  type LtrRecord,
  type Project
} from "../api/client";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { ProjectLookupPanel } from "../components/project/ProjectLookupPanel";
import { ProjectSummaryPanel } from "../components/project/ProjectSummaryPanel";
import "../workbench.css";

type ProjectWorkbenchPageProps = {
  projectId: string;
  onBack: () => void;
};

export function ProjectWorkbenchPage({
  projectId,
  onBack
}: ProjectWorkbenchPageProps): ReactElement {
  const [project, setProject] = useState<Project | null>(null);
  const [ltrs, setLtrs] = useState<LtrRecord[]>([]);
  const [evidencePlan, setEvidencePlan] = useState<EvidencePlacementPlan | null>(null);
  const [evidenceResult, setEvidenceResult] = useState<EvidencePlacementResult | null>(null);
  const [previewingEvidence, setPreviewingEvidence] = useState(false);
  const [placingEvidence, setPlacingEvidence] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadWorkbench();
  }, [projectId]);

  const folderReady = project?.status === "folder_created";
  const latestLtr = ltrs[0]?.ltr_number ?? null;
  const baselineItems = useMemo(
    () => [
      {
        title: "Created project",
        value: project ? "Yes" : "Loading",
      },
      {
        title: "LTR Number registered",
        value: latestLtr ? `Yes (${latestLtr})` : "No",
      },
      {
        title: "Project folder",
        value: folderReady ? "Created" : "Not recorded",
      },
      {
        title: "Source materials",
        value: folderReady
          ? "Evidence placement available"
          : "Available after folder creation",
      },
    ],
    [folderReady, latestLtr, project]
  );

  async function loadWorkbench(): Promise<void> {
    try {
      setProject(await getProject(projectId));
      setLtrs(await listProjectLtrs(projectId));
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function previewEvidenceNow(): Promise<void> {
    setPreviewingEvidence(true);
    try {
      const plan = await previewEvidencePlacement(projectId);
      setEvidencePlan(plan);
      setEvidenceResult(null);
      setMessage(plan.conflict ? "Evidence preview has conflicts." : "Evidence preview is clear.");
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPreviewingEvidence(false);
    }
  }

  async function placeEvidenceNow(): Promise<void> {
    setPlacingEvidence(true);
    try {
      const result = await placeEvidence(projectId);
      setEvidenceResult(result);
      setEvidencePlan(result.plan);
      setMessage(`Evidence placed: ${result.copied_paths.length} files copied.`);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPlacingEvidence(false);
    }
  }

  if (!project && !error) {
    return <LoadingState label="Loading project workbench..." />;
  }

  return (
    <section className="workbench-page">
      {error && <ErrorMessage message={error} />}
      {message && <p className="success">{message}</p>}
      {project && (
        <>
          <ProjectSummaryPanel project={project} onBack={onBack} />
          <section className="project-workbench-status">
            <header>
              <h3>Project workbench boundary</h3>
              <p>
                New Project is used for creation. This page is for confirmed project status and
                source material management.
              </p>
            </header>
            <dl className="project-workbench-status-grid">
              {baselineItems.map((item) => (
                <div key={item.title}>
                  <dt>{item.title}</dt>
                  <dd>{item.value}</dd>
                </div>
              ))}
            </dl>
            {!folderReady ? (
              <p className="blocking-copy">
                Project folder is not recorded for this project. Complete New Project folder
                creation or use a future recovery task.
              </p>
            ) : null}
          </section>
          <ProjectLookupPanel projectId={project.project_id} />
          <section className="evidence-placement-panel">
            <div className="evidence-placement-heading">
              <div>
                <h4>Evidence placement</h4>
                <p>
                  Preview and place source materials into the project folder after project creation.
                </p>
              </div>
              <div className="action-row">
                <button
                  className="secondary-action"
                  disabled={!folderReady || previewingEvidence || placingEvidence}
                  type="button"
                  onClick={() => void previewEvidenceNow()}
                >
                  {previewingEvidence ? "Previewing..." : "Preview evidence placement"}
                </button>
                <button
                  className="primary-action"
                  disabled={!folderReady || placingEvidence || !evidencePlan}
                  type="button"
                  onClick={() => void placeEvidenceNow()}
                >
                  {placingEvidence ? "Placing..." : "Place evidence"}
                </button>
              </div>
            </div>

            {evidencePlan && (
              <div
                className={
                  evidencePlan.conflict
                    ? "evidence-plan-card evidence-plan-conflict"
                    : "evidence-plan-card"
                }
              >
                <strong>
                  {evidencePlan.conflict
                    ? "Evidence placement has conflicts"
                    : "Evidence placement preview is ready"}
                </strong>
                <p className="fine-print">
                  Project folder: <code>{evidencePlan.project_folder_path}</code>
                </p>
                <ul className="evidence-item-list">
                  {evidencePlan.items.map((item) => (
                    <li
                      className={item.conflict ? "evidence-item-conflict" : undefined}
                      key={`${item.asset_id}-${item.target_path}`}
                    >
                      <div>
                        <strong>{assetLabel(item.source_path, item.asset_id)}</strong>
                        <span>
                          {item.category} {"->"} {item.target_path}
                        </span>
                      </div>
                      <em>{item.conflict ? "Conflict" : "Ready"}</em>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {evidenceResult && (
              <div className="message-list message-list-warning">
                <strong>Evidence placement result</strong>
                <ul>
                  <li>Copied files: {evidenceResult.copied_paths.length}</li>
                  <li>Skipped files: {evidenceResult.plan.conflicts.length}</li>
                </ul>
              </div>
            )}
          </section>
        </>
      )}
    </section>
  );
}

function assetLabel(sourcePath: string, assetId: string): string {
  const normalized = sourcePath.replace(/\\/g, "/");
  const lastSegment = normalized.split("/").pop();
  return lastSegment && lastSegment.trim() ? lastSegment : assetId;
}
