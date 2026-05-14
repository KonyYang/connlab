import type { ReactElement } from "react";
import { ApprovalPackagePanel } from "../../components/workflow/ApprovalPackagePanel";
import { ProjectLookupPanel } from "../../components/project/ProjectLookupPanel";
import { ProjectSummaryPanel } from "../../components/project/ProjectSummaryPanel";
import type { Project } from "../../api/client";
import { ProjectFolderCreationPanel } from "./ProjectFolderCreationPanel";
import { ProjectWorkbenchEvidencePanel } from "./ProjectWorkbenchEvidencePanel";
import { ProjectWorkbenchDocumentStatusPanel } from "./ProjectWorkbenchDocumentStatusPanel";
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
    approvalInputSources,
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
    matrixAuthorityDraft,
    matrixCandidateDraft,
    matrixDraftEditableGroups,
    matrixDraftError,
    matrixDraftLoading,
    matrixSaving,
    matrixValidating,
    matrixConfirming,
    matrixValidation,
    matrixSourceCandidates,
    matrixSourceCandidateWarnings,
    matrixSourceCandidatesLoading,
    matrixSelectedSourceAssetId,
    matrixStarterBrowseHint,
    matrixStarterSourcePath,
    matrixStarterPreview,
    matrixStarterPreviewing,
    matrixStarterCreatingFromPreview,
    matrixStarterCreatingManual,
    matrixStarterError,
    versionStatus,
    placingEvidence,
    previewingApprovalPackage,
    previewingEvidence,
    setApprovalInput,
    setMatrixStarterSourcePath,
    setMatrixSelectedSourceAssetId,
    setMatrixDraftEditableGroups,
    onPreviewMatrixStarterFromCandidate,
    onPreviewMatrixStarterFromPath,
    onBrowseMatrixStarterFallback,
    onCreateMatrixDraftFromPreview,
    onCreateManualMatrixDraft,
    onSaveMatrixDraft,
    onValidateMatrixDraft,
    onConfirmMatrixDraft,
    onExecuteApprovalPackage,
    onFolderCreated,
    onPlaceEvidence,
    onPreviewApprovalPackage,
    onPreviewEvidence
  } = model;

  return (
    <>
      <ProjectSummaryPanel project={project} onBack={onBack} />
      <section className="project-workbench-matrix-primary">
        <header className="project-workbench-matrix-header">
          <div>
            <p className="eyebrow">Matrix authority workspace</p>
            <h3>Project planning center</h3>
            <p>Confirmed Matrix authority and candidate editing remain the primary work surface.</p>
          </div>
          <dl className="project-workbench-mini-grid">
            {baselineItems.map((item) => (
              <div key={item.title}>
                <dt>{item.title}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
        </header>
        <ProjectWorkbenchMatrixReviewPanel
          draft={matrixDraft}
          authorityDraft={matrixAuthorityDraft}
          candidateDraft={matrixCandidateDraft}
          editableGroups={matrixDraftEditableGroups}
          error={matrixDraftError}
          loading={matrixDraftLoading}
          saving={matrixSaving}
          validating={matrixValidating}
          confirming={matrixConfirming}
          validation={matrixValidation}
          sourceCandidates={matrixSourceCandidates}
          sourceCandidateWarnings={matrixSourceCandidateWarnings}
          sourceCandidatesLoading={matrixSourceCandidatesLoading}
          selectedSourceAssetId={matrixSelectedSourceAssetId}
          starterBrowseHint={matrixStarterBrowseHint}
          starterSourcePath={matrixStarterSourcePath}
          starterPreview={matrixStarterPreview}
          starterPreviewing={matrixStarterPreviewing}
          starterCreatingFromPreview={matrixStarterCreatingFromPreview}
          starterCreatingManual={matrixStarterCreatingManual}
          starterError={matrixStarterError}
          onSourceCandidateSelect={setMatrixSelectedSourceAssetId}
          onPreviewStarterFromCandidate={onPreviewMatrixStarterFromCandidate}
          onStarterSourcePathChange={setMatrixStarterSourcePath}
          onBrowseStarterFallback={onBrowseMatrixStarterFallback}
          onPreviewStarterFromPath={onPreviewMatrixStarterFromPath}
          onCreateDraftFromPreview={onCreateMatrixDraftFromPreview}
          onCreateManualDraft={onCreateManualMatrixDraft}
          onEditableGroupsChange={setMatrixDraftEditableGroups}
          onSaveDraft={onSaveMatrixDraft}
          onValidateDraft={onValidateMatrixDraft}
          onConfirmDraft={onConfirmMatrixDraft}
          versionStatus={versionStatus}
        />
        <ProjectWorkbenchDocumentStatusPanel status={versionStatus} />
      </section>

      <section className="project-workbench-supporting">
        <section className="project-workbench-status">
          <header>
            <h3>Project workbench boundary</h3>
            <p>
              New Project is used for creation. This page is for confirmed project status and
              source material management.
            </p>
          </header>
          {!folderReady ? (
            <p className="blocking-copy">
              Project folder is not recorded for this project. Create it here after LTR registration.
            </p>
          ) : null}
        </section>

        <details className="workbench-supporting-panel">
          <summary>Project folder workspace</summary>
          <ProjectFolderCreationPanel
            configuredOutputRoot={folderResources.outputRoot}
            configuredTemplate={folderResources.template}
            folderReady={folderReady}
            latestLtrNumber={latestLtr}
            onFolderCreated={onFolderCreated}
            projectId={project.project_id}
            projectStatus={project.status}
          />
        </details>

        <details className="workbench-supporting-panel">
          <summary>Approval package workspace</summary>
          <ApprovalPackagePanel
            executing={executingApprovalPackage}
            folderReady={folderReady}
            input={approvalInput}
            inputSources={approvalInputSources}
            onExecute={onExecuteApprovalPackage}
            onInputChange={setApprovalInput}
            onPreview={onPreviewApprovalPackage}
            preview={approvalPreview}
            previewing={previewingApprovalPackage}
            result={approvalResult}
          />
        </details>

        <details className="workbench-supporting-panel">
          <summary>Evidence placement workspace</summary>
          <ProjectWorkbenchEvidencePanel
            evidencePlan={evidencePlan}
            evidenceResult={evidenceResult}
            folderReady={folderReady}
            onPlaceEvidence={onPlaceEvidence}
            onPreviewEvidence={onPreviewEvidence}
            placingEvidence={placingEvidence}
            previewingEvidence={previewingEvidence}
          />
        </details>

        <details className="workbench-supporting-panel">
          <summary>Read-only lookup workspace</summary>
          <ProjectLookupPanel projectId={project.project_id} />
        </details>
      </section>
    </>
  );
}
