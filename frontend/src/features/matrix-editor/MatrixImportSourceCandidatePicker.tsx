import type { MatrixResolvedDirectoryCandidate } from "../../api/client";

type MatrixImportSourceCandidatePickerProps = {
  candidates: MatrixResolvedDirectoryCandidate[];
  sourceTitle: string;
  loading: boolean;
  previewBusy: boolean;
  error: string | null;
  onCancel: () => void;
  onUploadOtherFile: () => void;
  onUseCandidate: (sourceAssetId: string) => void;
};

export function MatrixImportSourceCandidatePicker({
  candidates,
  sourceTitle,
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
          <h3 id="matrix-import-source-picker-title">{sourceTitle}</h3>
          <p>Select a file from this folder, or upload another file.</p>
        </header>
        <div aria-busy={busy} aria-live="polite" className="matrix-import-source-picker-body">
          {loading ? <p>Loading project sources...</p> : null}
          {error ? <p className="matrix-import-source-picker-error">{error}</p> : null}
          {!loading && candidates.length === 0 ? <p>No project candidates are available. Upload another file to continue.</p> : null}
          {candidates.length > 0 ? (
            <div className="matrix-import-source-picker-list">
              {candidates.map((candidate) => {
                return (
                  <section className="matrix-import-source-picker-row" key={candidate.candidate_id}>
                    <div>
                      <div className="matrix-import-source-picker-name-line">
                        <strong data-testid="matrix-import-source-name">{candidate.file_name}</strong>
                      </div>
                    </div>
                    <button type="button" disabled={busy} onClick={() => onUseCandidate(candidate.candidate_id)}>
                      Select {candidate.file_name}
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
