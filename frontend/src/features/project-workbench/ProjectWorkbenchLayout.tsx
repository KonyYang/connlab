import type { ReactElement } from "react";
import { ApprovalPackagePanel } from "../../components/workflow/ApprovalPackagePanel";
import { ProjectLookupPanel } from "../../components/project/ProjectLookupPanel";
import { ProjectSummaryPanel } from "../../components/project/ProjectSummaryPanel";
import type { Project } from "../../api/client";
import { ProjectFolderCreationPanel } from "./ProjectFolderCreationPanel";
import { ProjectWorkbenchEvidencePanel } from "./ProjectWorkbenchEvidencePanel";
import { ProjectWorkbenchMatrixReviewPanel } from "./ProjectWorkbenchMatrixReviewPanel";
import type { ProjectWorkbenchModel } from "./useProjectWorkbenchModel";

type ProjectWorkbenchLayoutProps = {
  model: ProjectWorkbenchModel;
  project: Project;
  onBack: () => void;
};

export function ProjectWorkbenchLayout({
  model,
  project,
  onBack
}: ProjectWorkbenchLayoutProps): ReactElement {
  const {
    approvalInput,
    approvalPreview,
    approvalResult,
    baselineItems,
    executingApprovalPackage,
    evidencePlan,
    evidenceResult,
    folderReady,
    folderResources,
    latestLtr,
    matrixDraft,
    matrixDraftError,
    matrixDraftLoading,
    placingEvidence,
    previewingApprovalPackage,
    previewingEvidence,
    setApprovalInput,
    onExecuteApprovalPackage,
    onFolderCreated,
    onPlaceEvidence,
    onPreviewApprovalPackage,
    onPreviewEvidence
  } = model;

  return (
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
            Project folder is not recorded for this project. Create it here after LTR registration.
          </p>
        ) : null}
      </section>
      <ProjectFolderCreationPanel
        configuredOutputRoot={folderResources.outputRoot}
        configuredTemplate={folderResources.template}
        folderReady={folderReady}
        latestLtrNumber={latestLtr}
        onFolderCreated={onFolderCreated}
        projectId={project.project_id}
        projectStatus={project.status}
      />
      <ProjectWorkbenchMatrixReviewPanel
        draft={matrixDraft}
        error={matrixDraftError}
        loading={matrixDraftLoading}
      />
      <ProjectLookupPanel projectId={project.project_id} />
      <ApprovalPackagePanel
        executing={executingApprovalPackage}
        folderReady={folderReady}
        input={approvalInput}
        onExecute={onExecuteApprovalPackage}
        onInputChange={setApprovalInput}
        onPreview={onPreviewApprovalPackage}
        preview={approvalPreview}
        previewing={previewingApprovalPackage}
        result={approvalResult}
      />
      <ProjectWorkbenchEvidencePanel
        evidencePlan={evidencePlan}
        evidenceResult={evidenceResult}
        folderReady={folderReady}
        onPlaceEvidence={onPlaceEvidence}
        onPreviewEvidence={onPreviewEvidence}
        placingEvidence={placingEvidence}
        previewingEvidence={previewingEvidence}
      />
    </>
  );
}
