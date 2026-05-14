import type { ReactElement } from "react";
import type {
  MatrixSourceCandidate,
  MatrixPreviewResponse,
  MatrixValidationSummary,
  ProjectTestPlanDraft,
  ProjectTestPlanDraftGroup
} from "../../api/client";
import type { WorkbenchVersionStatus } from "./projectWorkbenchVersionSelectors";
import { ProjectWorkbenchMatrixAuthorityBar } from "./ProjectWorkbenchMatrixAuthorityBar";
import { ProjectWorkbenchMatrixInspector } from "./ProjectWorkbenchMatrixInspector";
import { ProjectWorkbenchMatrixOverview } from "./ProjectWorkbenchMatrixOverview";
import { ProjectWorkbenchMatrixStarter } from "./ProjectWorkbenchMatrixStarter";
import { buildMatrixSummary } from "./projectWorkbenchMatrixHelpers";

type ProjectWorkbenchMatrixReviewPanelProps = {
  draft: ProjectTestPlanDraft | null;
  authorityDraft: ProjectTestPlanDraft | null;
  candidateDraft: ProjectTestPlanDraft | null;
  editableGroups: ProjectTestPlanDraftGroup[];
  error: string | null;
  loading: boolean;
  saving: boolean;
  validating: boolean;
  confirming: boolean;
  validation: MatrixValidationSummary | null;
  sourceCandidates: MatrixSourceCandidate[];
  sourceCandidateWarnings: string[];
  sourceCandidatesLoading: boolean;
  selectedSourceAssetId: string | null;
  starterBrowseHint: string | null;
  starterSourcePath: string;
  starterPreview: MatrixPreviewResponse | null;
  starterPreviewing: boolean;
  starterCreatingFromPreview: boolean;
  starterCreatingManual: boolean;
  starterError: string | null;
  onSourceCandidateSelect: (value: string | null) => void;
  onPreviewStarterFromCandidate: () => Promise<void>;
  onStarterSourcePathChange: (value: string) => void;
  onBrowseStarterFallback: () => void;
  onPreviewStarterFromPath: () => Promise<void>;
  onCreateDraftFromPreview: () => Promise<void>;
  onCreateManualDraft: () => Promise<void>;
  onEditableGroupsChange: (groups: ProjectTestPlanDraftGroup[]) => void;
  onSaveDraft: () => Promise<void>;
  onValidateDraft: () => Promise<void>;
  onConfirmDraft: () => Promise<void>;
  versionStatus: WorkbenchVersionStatus;
};

export function ProjectWorkbenchMatrixReviewPanel({
  draft,
  authorityDraft,
  candidateDraft,
  editableGroups,
  error,
  loading,
  saving,
  validating,
  confirming,
  validation,
  sourceCandidates,
  sourceCandidateWarnings,
  sourceCandidatesLoading,
  selectedSourceAssetId,
  starterBrowseHint,
  starterSourcePath,
  starterPreview,
  starterPreviewing,
  starterCreatingFromPreview,
  starterCreatingManual,
  starterError,
  onSourceCandidateSelect,
  onPreviewStarterFromCandidate,
  onStarterSourcePathChange,
  onBrowseStarterFallback,
  onPreviewStarterFromPath,
  onCreateDraftFromPreview,
  onCreateManualDraft,
  onEditableGroupsChange,
  onSaveDraft,
  onValidateDraft,
  onConfirmDraft,
  versionStatus
}: ProjectWorkbenchMatrixReviewPanelProps): ReactElement {
  const summary = buildMatrixSummary(draft?.payload.groups, draft?.payload.warnings?.length ?? 0);
  const canEdit = draft !== null && draft.status !== "superseded";
  const hasBlockers = (validation?.blockers.length ?? 0) > 0;

  return (
    <section className="matrix-review-panel">
      <header className="matrix-review-heading">
        <div>
          <h4>Matrix review</h4>
          <p>Use the Project test-plan draft as the primary authority workspace before downstream documents.</p>
        </div>
        {draft ? <strong>Draft v{draft.version}</strong> : null}
      </header>

      <ProjectWorkbenchMatrixAuthorityBar
        authorityDraft={authorityDraft}
        candidateDraft={candidateDraft}
        hasBlockers={hasBlockers}
      />

      {loading ? <p className="fine-print">Loading Matrix draft...</p> : null}
      {!loading && error ? <p className="error">Unable to load Matrix draft: {error}</p> : null}
      {!loading && !error && !draft ? (
        <ProjectWorkbenchMatrixStarter
          sourceCandidates={sourceCandidates}
          sourceCandidateWarnings={sourceCandidateWarnings}
          sourceCandidatesLoading={sourceCandidatesLoading}
          selectedSourceAssetId={selectedSourceAssetId}
          browseHint={starterBrowseHint}
          sourcePath={starterSourcePath}
          preview={starterPreview}
          previewing={starterPreviewing}
          creatingFromPreview={starterCreatingFromPreview}
          creatingManualDraft={starterCreatingManual}
          starterError={starterError}
          onSourceCandidateSelect={onSourceCandidateSelect}
          onPreviewFromCandidate={onPreviewStarterFromCandidate}
          onSourcePathChange={onStarterSourcePathChange}
          onBrowseFallback={onBrowseStarterFallback}
          onPreviewFromPath={onPreviewStarterFromPath}
          onCreateFromPreview={onCreateDraftFromPreview}
          onCreateManualDraft={onCreateManualDraft}
        />
      ) : null}

      {draft && versionStatus.hasStaleOutputs ? (
        <div className="message-list message-list-warning">
          <strong>Downstream outputs are stale</strong>
          <ul>
            <li>Active draft version is newer than the latest downstream output linkage in this session.</li>
          </ul>
        </div>
      ) : null}

      {draft ? (
        <>
          <dl className="matrix-review-summary">
            <div>
              <dt>Source document</dt>
              <dd>{draft.source_document_name}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{draft.status}</dd>
            </div>
            <div>
              <dt>Groups</dt>
              <dd>{summary.groupCount}</dd>
            </div>
            <div>
              <dt>Steps</dt>
              <dd>{summary.stepCount}</dd>
            </div>
            <div>
              <dt>Warnings</dt>
              <dd>{summary.warningCount}</dd>
            </div>
            <div>
              <dt>Validation blockers</dt>
              <dd>{validation?.blockers.length ?? draft.payload.blockers?.length ?? 0}</dd>
            </div>
          </dl>

          <div className="matrix-workspace">
            <ProjectWorkbenchMatrixOverview draft={draft} />
            {canEdit ? (
              <ProjectWorkbenchMatrixInspector
                editableGroups={editableGroups}
                validating={validating}
                saving={saving}
                confirming={confirming}
                hasBlockers={hasBlockers}
                onEditableGroupsChange={onEditableGroupsChange}
                onValidateDraft={onValidateDraft}
                onSaveDraft={onSaveDraft}
                onConfirmDraft={onConfirmDraft}
              />
            ) : null}
          </div>

          {validation && validation.blockers.length > 0 ? (
            <div className="message-list message-list-danger">
              <strong>Validation blockers</strong>
              <ul>
                {validation.blockers.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {validation && validation.warnings.length > 0 ? (
            <div className="message-list message-list-warning">
              <strong>Validation warnings</strong>
              <ul>
                {validation.warnings.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}

          {(draft.payload.warnings ?? []).length > 0 ? (
            <div className="message-list message-list-warning">
              <strong>Draft warnings</strong>
              <ul>
                {(draft.payload.warnings ?? []).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
