import { useMemo, useState, type ReactElement } from "react";
import type { EvidencePlacementPlan, EvidencePlacementResult } from "../../api/client";

type ProjectWorkbenchMaterialDropPanelProps = {
  folderReady: boolean;
  evidencePlan: EvidencePlacementPlan | null;
  evidenceResult: EvidencePlacementResult | null;
  previewingEvidence: boolean;
  placingEvidence: boolean;
  onPreviewEvidence: () => Promise<void>;
  onPlaceEvidence: () => Promise<void>;
};

export function ProjectWorkbenchMaterialDropPanel({
  folderReady,
  evidencePlan,
  evidenceResult,
  previewingEvidence,
  placingEvidence,
  onPreviewEvidence,
  onPlaceEvidence
}: ProjectWorkbenchMaterialDropPanelProps): ReactElement {
  const [pathInput, setPathInput] = useState("");
  const pathCount = useMemo(
    () => pathInput.split(/\r?\n/).map((item) => item.trim()).filter(Boolean).length,
    [pathInput]
  );

  return (
    <section className="material-drop-panel" aria-label="Other materials">
      <header className="material-drop-heading">
        <div>
          <h4>Other materials</h4>
          <p>Lightweight support intake with preview-first placement.</p>
        </div>
        <span className="material-drop-mode">Runtime support</span>
      </header>

      <div className="material-drop-dropzone" role="note" aria-label="Drop zone limitation">
        <strong>Drop files here (desktop workspace)</strong>
        <p>
          Browser mode does not expose trusted local absolute paths for drag/drop. Use desktop workspace drop
          or paste source paths below for preview.
        </p>
      </div>

      <label className="material-drop-paths">
        Source paths (fallback)
        <textarea
          value={pathInput}
          onChange={(event) => setPathInput(event.target.value)}
          placeholder="Paste one source path per line"
        />
      </label>

      <div className="material-drop-actions">
        <button disabled={!folderReady || previewingEvidence} type="button" onClick={() => void onPreviewEvidence()}>
          {previewingEvidence ? "Previewing..." : "Preview placement"}
        </button>
        <button
          disabled={!folderReady || !evidencePlan || evidencePlan.conflict || placingEvidence}
          type="button"
          onClick={() => void onPlaceEvidence()}
        >
          {placingEvidence ? "Placing..." : "Confirm placement"}
        </button>
      </div>

      <dl className="material-drop-summary">
        <div>
          <dt>Input paths</dt>
          <dd>{pathCount}</dd>
        </div>
        <div>
          <dt>Preview items</dt>
          <dd>{evidencePlan?.items.length ?? 0}</dd>
        </div>
        <div>
          <dt>Placed files</dt>
          <dd>{evidenceResult?.copied_paths.length ?? 0}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>
            {evidenceResult
              ? "Placed"
              : evidencePlan?.conflict
                ? "Preview conflict"
                : evidencePlan
                  ? "Preview ready"
                  : "Not started"}
          </dd>
        </div>
      </dl>

      {evidencePlan?.conflicts.length ? (
        <ul className="material-drop-warning-list">
          {evidencePlan.conflicts.slice(0, 4).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
