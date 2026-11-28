import { useEffect, useMemo, useRef, type ReactElement } from "react";
import type { LlcrImportPreview } from "../../api/client";
import { LlcrReadings } from "./LlcrReadings";
import {
  formatLlcrSummary,
  validateLlcrConfirmation,
  type LlcrDecisionDrafts,
  type LlcrOutcome,
} from "./reportWorkspaceModel";

type LlcrImportPreviewDialogProps = {
  preview: LlcrImportPreview;
  drafts: LlcrDecisionDrafts;
  confirming: boolean;
  canceling: boolean;
  onDraftChange: (resultId: string, outcome: LlcrOutcome, overrideReason: string) => void;
  onCancel: () => void;
  onConfirm: () => void;
};

export function LlcrImportPreviewDialog({
  preview,
  drafts,
  confirming,
  canceling,
  onDraftChange,
  onCancel,
  onConfirm,
}: LlcrImportPreviewDialogProps): ReactElement {
  const busy = confirming || canceling;
  const dialog = useRef<HTMLElement>(null);
  useEffect(() => {
    const trigger = document.activeElement;
    dialog.current?.focus();
    return () => { if (trigger instanceof HTMLElement && trigger.isConnected) trigger.focus(); };
  }, []);
  const validationErrors = useMemo(
    () => validateLlcrConfirmation(preview, drafts),
    [drafts, preview]
  );

  return (
    <div className="report-workspace-dialog-backdrop">
      <section
        aria-labelledby="llcr-preview-title"
        aria-modal="true"
        className="report-workspace-dialog llcr-preview"
        role="dialog"
        ref={dialog}
        tabIndex={-1}
        onKeyDown={event => {
          if (event.key === "Escape" && !busy) onCancel();
          if (event.key !== "Tab") return;
          const controls = event.currentTarget.querySelectorAll<HTMLElement>("button:enabled, select:enabled, input:enabled, [tabindex='0']");
          const first = controls[0], last = controls[controls.length - 1];
          if (!first) { event.preventDefault(); return; }
          if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog.current)) {
            event.preventDefault(); last.focus();
          } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault(); first.focus();
          }
        }}
      >
        <header className="report-workspace-dialog-header">
          <div>
            <h2 id="llcr-preview-title">LLCR import preview</h2>
            <p>
              {preview.source.file_name} · {preview.sample_count} samples · {preview.test_point_count} test points
            </p>
          </div>
          <button disabled={busy} onClick={onCancel} type="button">Close</button>
        </header>

        {preview.diagnostics.length > 0 ? (
          <div className="report-workspace-diagnostics" aria-label="Import diagnostics">
            {preview.diagnostics.map((diagnostic, index) => (
              <p className={diagnostic.severity === "blocked" || diagnostic.severity === "error" ? "error" : "warning"} key={`${diagnostic.code}-${index}`}>
                {diagnostic.message}
              </p>
            ))}
          </div>
        ) : null}

        {preview.readings?.length ? <LlcrReadings readings={preview.readings} /> : null}
        {preview.entries.length > 0 && (
          <div className="llcr-review-outcomes" aria-label="Report outcomes">
            {preview.entries.map((entry) => {
              const draft = drafts[entry.result_id];
              const changed = Boolean(draft && draft.outcome !== entry.provisional_outcome);
              return (
                <div key={entry.result_id} className="llcr-review-target">
                  <div>
                    <strong>{entry.report_target}</strong> · {entry.stage_label}
                    <p>Min / Max / Avg · <span>{formatLlcrSummary(entry)}</span></p>
                    <p>Requirement · {entry.requirement}</p>
                  </div>
                  <label>
                    Final outcome
                    <select
                      aria-label={`Final outcome for ${entry.report_target}`}
                      disabled={busy}
                      onChange={(event) => onDraftChange(
                        entry.result_id,
                        event.target.value as LlcrOutcome,
                        draft?.overrideReason ?? ""
                      )}
                      value={draft?.outcome ?? entry.provisional_outcome}
                    >
                      <option value="pass">Pass</option>
                      <option value="fail">Fail</option>
                      <option value="not_determined">Not determined</option>
                    </select>
                  </label>
                  {changed ? (
                    <label className="report-workspace-override-reason">
                      Override reason
                      <input
                        aria-label={`Override reason for ${entry.report_target}`}
                        disabled={busy}
                        onChange={(event) => onDraftChange(
                          entry.result_id,
                          draft?.outcome ?? entry.provisional_outcome,
                          event.target.value
                        )}
                        value={draft?.overrideReason ?? ""}
                      />
                    </label>
                  ) : null}
                </div>
              );
            })}
          </div>
        )}

        {validationErrors.length > 0 ? (
          <ul className="report-workspace-confirm-errors">
            {validationErrors.map((message) => <li key={message}>{message}</li>)}
          </ul>
        ) : null}

        <footer className="report-workspace-dialog-actions">
          <button disabled={busy} onClick={onCancel} type="button">
            {canceling ? "Cancelling..." : "Cancel"}
          </button>
          <button
            className="primary-action"
            disabled={busy || validationErrors.length > 0}
            onClick={onConfirm}
            type="button"
          >
            {confirming ? "Confirming..." : "Confirm LLCR Dataset"}
          </button>
        </footer>
      </section>
    </div>
  );
}
