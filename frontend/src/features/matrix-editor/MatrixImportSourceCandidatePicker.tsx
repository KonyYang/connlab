import type { MatrixSourceCandidate } from "../../api/client";

type MatrixImportSourceCandidatePickerProps = {
  candidates: MatrixSourceCandidate[];
  loading: boolean;
  previewBusy: boolean;
  error: string | null;
  onCancel: () => void;
  onUploadOtherFile: () => void;
  onUseCandidate: (sourceAssetId: string) => void;
};

export function MatrixImportSourceCandidatePicker({
  candidates,
  loading,
  previewBusy,
  error,
  onCancel,
  onUploadOtherFile,
  onUseCandidate,
}: MatrixImportSourceCandidatePickerProps) {
  const busy = loading || previewBusy;

  return (
    <section aria-labelledby="matrix-import-source-picker-title" className="matrix-import-source-picker-backdrop" role="dialog" aria-modal="true">
      <article className="matrix-import-source-picker">
        <header>
          <h3 id="matrix-import-source-picker-title">Choose a project source</h3>
          <p>Use a registered project file, or upload another source for review.</p>
        </header>
        <div aria-busy={busy} aria-live="polite" className="matrix-import-source-picker-body">
          {loading ? <p>Loading project sources...</p> : null}
          {error ? <p className="matrix-import-source-picker-error">{error}</p> : null}
          {!loading && candidates.length === 0 ? <p>No project candidates are available. Upload another file to continue.</p> : null}
          {candidates.length > 0 ? (
            <div className="matrix-import-source-picker-list">
              {candidates.map((candidate) => {
                const recommended = candidate.candidate_kind === "likely_spec_or_matrix";
                const available = candidate.stored_file_available;
                return (
                  <section className="matrix-import-source-picker-row" key={candidate.source_asset_id}>
                    <div>
                      <div className="matrix-import-source-picker-name-line">
                        <strong data-testid="matrix-import-source-name">{candidate.original_name}</strong>
                        {recommended ? <span className="matrix-import-source-picker-recommended">Recommended</span> : null}
                      </div>
                      <p>{candidate.extension} · {candidate.asset_type}</p>
                      <p>{candidate.reason}</p>
                      {!available ? <p className="matrix-import-source-picker-unavailable">Unavailable</p> : null}
                    </div>
                    <button type="button" disabled={!available || busy} onClick={() => onUseCandidate(candidate.source_asset_id)}>
                      Use this file: {candidate.original_name}
                    </button>
                  </section>
                );
              })}
            </div>
          ) : null}
        </div>
        <footer>
          <button type="button" disabled={busy} onClick={onCancel}>Cancel</button>
          <button type="button" disabled={busy} onClick={onUploadOtherFile}>Upload other file</button>
        </footer>
      </article>
    </section>
  );
}
