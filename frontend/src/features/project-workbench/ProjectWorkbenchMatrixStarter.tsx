import type { ReactElement } from "react";
import type { MatrixPreviewResponse, MatrixSourceCandidate } from "../../api/client";

type ProjectWorkbenchMatrixStarterProps = {
  sourceCandidates: MatrixSourceCandidate[];
  sourceCandidateWarnings: string[];
  sourceCandidatesLoading: boolean;
  selectedSourceAssetId: string | null;
  browseHint: string | null;
  sourcePath: string;
  preview: MatrixPreviewResponse | null;
  previewing: boolean;
  creatingFromPreview: boolean;
  creatingManualDraft: boolean;
  starterError: string | null;
  onSourceCandidateSelect: (value: string | null) => void;
  onPreviewFromCandidate: () => Promise<void>;
  onSourcePathChange: (value: string) => void;
  onBrowseFallback: () => void;
  onPreviewFromPath: () => Promise<void>;
  onCreateFromPreview: () => Promise<void>;
  onCreateManualDraft: () => Promise<void>;
};

export function ProjectWorkbenchMatrixStarter({
  sourceCandidates,
  sourceCandidateWarnings,
  sourceCandidatesLoading,
  selectedSourceAssetId,
  browseHint,
  sourcePath,
  preview,
  previewing,
  creatingFromPreview,
  creatingManualDraft,
  starterError,
  onSourceCandidateSelect,
  onPreviewFromCandidate,
  onSourcePathChange,
  onBrowseFallback,
  onPreviewFromPath,
  onCreateFromPreview,
  onCreateManualDraft
}: ProjectWorkbenchMatrixStarterProps): ReactElement {
  const createFromPreviewBlocked =
    !preview || preview.blockers.length > 0 || previewing || creatingFromPreview || creatingManualDraft;

  const previewGroupCount = preview?.groups.length ?? 0;
  const previewStepCount =
    (preview?.groups ?? []).reduce((total, group) => total + group.steps.length, 0);
  const hasCandidates = sourceCandidates.length > 0;
  const selectedCandidate = sourceCandidates.find(
    (item) => item.source_asset_id === selectedSourceAssetId
  );

  return (
    <section className="matrix-starter-panel">
      <header className="matrix-starter-heading">
        <div>
          <h5>Start Matrix draft</h5>
          <p>Use project source files first, then external source fallback, then manual Matrix fallback.</p>
        </div>
      </header>

      <div className="matrix-starter-grid">
        <article className="matrix-starter-card">
          <h6>Candidate source files from this project</h6>
          <p className="fine-print">Select a received source attachment and preview before creating the draft.</p>
          {sourceCandidatesLoading ? <p className="fine-print">Loading source candidates...</p> : null}
          {!sourceCandidatesLoading && !hasCandidates ? (
            <p className="fine-print">No `.docx` source candidates are currently available for this project.</p>
          ) : null}
          {hasCandidates ? (
            <div className="matrix-source-candidate-list">
              {sourceCandidates.map((candidate) => (
                <label key={candidate.source_asset_id} className="matrix-source-candidate-row">
                  <input
                    checked={candidate.source_asset_id === selectedSourceAssetId}
                    name="matrix-source-candidate"
                    type="radio"
                    onChange={() => onSourceCandidateSelect(candidate.source_asset_id)}
                  />
                  <div>
                    <strong>{candidate.original_name}</strong>
                    <p className="fine-print">{candidate.reason}</p>
                  </div>
                  <span
                    className={
                      candidate.stored_file_available
                        ? "matrix-source-candidate-status"
                        : "matrix-source-candidate-status matrix-source-candidate-status-missing"
                    }
                  >
                    {candidate.stored_file_available ? "Available" : "Missing"}
                  </span>
                </label>
              ))}
            </div>
          ) : null}
          <div className="action-row">
            <button
              className="secondary-action"
              disabled={
                previewing ||
                creatingFromPreview ||
                creatingManualDraft ||
                !selectedCandidate ||
                !selectedCandidate.stored_file_available
              }
              type="button"
              onClick={() => void onPreviewFromCandidate()}
            >
              {previewing ? "Previewing..." : "Preview selected source"}
            </button>
            <button
              className="primary-action"
              disabled={createFromPreviewBlocked}
              type="button"
              onClick={() => void onCreateFromPreview()}
            >
              {creatingFromPreview ? "Creating..." : "Create draft from preview"}
            </button>
          </div>
          {sourceCandidateWarnings.length > 0 ? (
            <div className="message-list message-list-warning">
              <strong>Source candidate notes</strong>
              <ul>
                {sourceCandidateWarnings.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </article>

        <article className="matrix-starter-card">
          <h6>External source fallback</h6>
          <p className="fine-print">
            Use this when received project files do not contain a usable product specification.
          </p>
          <div className="action-row">
            <button
              className="secondary-action"
              disabled={previewing || creatingFromPreview || creatingManualDraft}
              type="button"
              onClick={onBrowseFallback}
            >
              Browse...
            </button>
          </div>
          {browseHint ? <p className="fine-print">{browseHint}</p> : null}
          <label className="matrix-starter-field">
            <span className="fine-print">Source .docx path</span>
            <input
              placeholder="D:\\Specifications\\product_spec.docx"
              type="text"
              value={sourcePath}
              onChange={(event) => onSourcePathChange(event.target.value)}
            />
          </label>
          <div className="action-row">
            <button
              className="secondary-action"
              disabled={previewing || creatingFromPreview || creatingManualDraft || sourcePath.trim().length === 0}
              type="button"
              onClick={() => void onPreviewFromPath()}
            >
              {previewing ? "Previewing..." : "Preview from path"}
            </button>
          </div>

          {preview ? (
            <div className="matrix-starter-preview">
              <dl className="matrix-starter-preview-grid">
                <div>
                  <dt>Source</dt>
                  <dd>{preview.source_document_name}</dd>
                </div>
                <div>
                  <dt>Capability</dt>
                  <dd>{preview.capability_status}</dd>
                </div>
                <div>
                  <dt>Selected table</dt>
                  <dd>{preview.selected_table_index ?? "-"}</dd>
                </div>
                <div>
                  <dt>Groups / steps</dt>
                  <dd>
                    {previewGroupCount} / {previewStepCount}
                  </dd>
                </div>
              </dl>
              {preview.blockers.length > 0 ? (
                <div className="message-list message-list-danger">
                  <strong>Preview blockers</strong>
                  <ul>
                    {preview.blockers.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {preview.warnings.length > 0 ? (
                <div className="message-list message-list-warning">
                  <strong>Preview warnings</strong>
                  <ul>
                    {preview.warnings.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          ) : null}
        </article>

        <article className={`matrix-starter-card${hasCandidates ? " matrix-starter-card-secondary" : ""}`}>
          <h6>Create manual Matrix</h6>
          <p className="fine-print">
            Start with explicit Group 1 identity and continue in the Matrix inspector.
          </p>
          <button
            className="primary-action"
            disabled={previewing || creatingFromPreview || creatingManualDraft}
            type="button"
            onClick={() => void onCreateManualDraft()}
          >
            {creatingManualDraft ? "Creating..." : "Create manual Matrix"}
          </button>
        </article>
      </div>

      {starterError ? <p className="error">Matrix starter failed: {starterError}</p> : null}
    </section>
  );
}
