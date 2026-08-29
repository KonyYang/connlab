import { useMemo, type ReactElement } from "react";
import type { LlcrImportPreview } from "../../api/client";
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
  const validationErrors = useMemo(
    () => validateLlcrConfirmation(preview, drafts),
    [drafts, preview]
  );

  return (
    <div className="report-workspace-dialog-backdrop">
      <section
        aria-labelledby="llcr-preview-title"
        aria-modal="true"
        className="report-workspace-dialog"
        role="dialog"
      >
        <header className="report-workspace-dialog-header">
          <div>
            <p className="report-workspace-eyebrow">Non-authoritative preview</p>
            <h2 id="llcr-preview-title">LLCR import preview</h2>
            <p>
              {preview.source.file_name} · {preview.sample_count} samples · {preview.test_point_count} test points
            </p>
          </div>
          <button disabled={busy} onClick={onCancel} type="button">Close</button>
        </header>

        <dl className="report-workspace-preview-facts">
          <div><dt>Matrix authority</dt><dd>Revision {preview.confirmed_matrix_revision}</dd></div>
          <div><dt>Detected sheets</dt><dd>{preview.detected_sheets.join(", ")}</dd></div>
          <div><dt>Parser profile</dt><dd>{preview.parser_profile_version}</dd></div>
          <div><dt>Result targets</dt><dd>{preview.result_count}</dd></div>
        </dl>

        {preview.diagnostics.length > 0 ? (
          <div className="report-workspace-diagnostics" aria-label="Import diagnostics">
            {preview.diagnostics.map((diagnostic, index) => (
              <p className={diagnostic.severity === "blocked" || diagnostic.severity === "error" ? "error" : "warning"} key={`${diagnostic.code}-${index}`}>
                <strong>{diagnostic.code}</strong>: {diagnostic.message}
              </p>
            ))}
          </div>
        ) : null}

        <div className="report-workspace-table-wrap">
          <table className="report-workspace-table">
            <thead>
              <tr>
                <th>Report target</th>
                <th>Stage</th>
                <th>Min / Max / Avg</th>
                <th>Requirement</th>
                <th>Provisional</th>
                <th>Final confirmation</th>
              </tr>
            </thead>
            <tbody>
              {preview.entries.map((entry) => {
                const draft = drafts[entry.result_id];
                const changed = Boolean(draft && draft.outcome !== entry.provisional_outcome);
                return (
                  <tr key={entry.result_id}>
                    <td><strong>{entry.report_target}</strong><small>{entry.source_range}</small></td>
                    <td>{entry.stage_label}</td>
                    <td>{formatLlcrSummary(entry)}</td>
                    <td>{entry.requirement}</td>
                    <td><span className={`report-workspace-outcome ${entry.provisional_outcome}`}>{outcomeLabel(entry.provisional_outcome)}</span></td>
                    <td>
                      <label>
                        <span className="sr-only">Final outcome for {entry.report_target}</span>
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
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

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
            {confirming ? "Confirming..." : "Confirm LLCR dataset"}
          </button>
        </footer>
      </section>
    </div>
  );
}

function outcomeLabel(outcome: LlcrOutcome): string {
  if (outcome === "not_determined") {
    return "Not determined";
  }
  return outcome === "pass" ? "Pass" : "Fail";
}
