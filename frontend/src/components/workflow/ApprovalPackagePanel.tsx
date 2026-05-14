import type { ChangeEvent, ReactElement } from "react";
import type {
  ApprovalPackageRequest,
  ApprovalPackageResponse
} from "../../api/client";
import type { ApprovalInputSources } from "../../features/project-workbench/useProjectWorkbenchModel";

type ApprovalPackagePanelProps = {
  folderReady: boolean;
  input: ApprovalPackageRequest;
  inputSources: ApprovalInputSources;
  preview: ApprovalPackageResponse | null;
  result: ApprovalPackageResponse | null;
  previewing: boolean;
  executing: boolean;
  onPreview: () => Promise<void>;
  onExecute: () => Promise<void>;
  onInputChange: (next: ApprovalPackageRequest) => void;
};

export function ApprovalPackagePanel({
  folderReady,
  input,
  inputSources,
  preview,
  result,
  previewing,
  executing,
  onPreview,
  onExecute,
  onInputChange
}: ApprovalPackagePanelProps): ReactElement {
  const executeBlocked = !preview || preview.blockers.length > 0 || executing;

  return (
    <section className="evidence-placement-panel">
      <div className="evidence-placement-heading">
        <div>
          <h4>Approval package</h4>
          <p>Preview and place required approval files into the project folder.</p>
        </div>
        <div className="action-row">
          <button
            className="secondary-action"
            disabled={!folderReady || previewing || executing}
            type="button"
            onClick={() => void onPreview()}
          >
            {previewing ? "Previewing..." : "Preview approval package"}
          </button>
          <button
            className="primary-action"
            disabled={!folderReady || executeBlocked}
            type="button"
            onClick={() => void onExecute()}
          >
            {executing ? "Placing..." : "Place approval package"}
          </button>
        </div>
      </div>

      <div className="folder-preview-panel">
        <div className="form-grid-two">
          <label className="approval-input-field">
            <span className="fine-print">
              Project folder path ({inputSources.project_folder_path})
            </span>
            <input
              required
              placeholder="Project folder path"
              value={input.project_folder_path}
              onChange={(event) => updateField(event, input, onInputChange, "project_folder_path")}
            />
          </label>
          <label className="approval-input-field">
            <span className="fine-print">
              Completed application form ({inputSources.completed_application_form_path})
            </span>
            <input
              required
              placeholder="Completed application form path"
              value={input.completed_application_form_path}
              onChange={(event) =>
                updateField(event, input, onInputChange, "completed_application_form_path")
              }
            />
          </label>
          <label className="approval-input-field">
            <span className="fine-print">
              Test record output ({inputSources.test_record_output_path})
            </span>
            <input
              required
              placeholder="Test record output path"
              value={input.test_record_output_path}
              onChange={(event) => updateField(event, input, onInputChange, "test_record_output_path")}
            />
          </label>
          <label className="approval-input-field">
            <span className="fine-print">
              Fee evaluation output ({inputSources.fee_evaluation_output_path})
            </span>
            <input
              placeholder="Fee evaluation output path (optional)"
              value={input.fee_evaluation_output_path ?? ""}
              onChange={(event) => {
                const value = event.target.value.trim();
                onInputChange({
                  ...input,
                  fee_evaluation_output_path: value ? value : null
                });
              }}
            />
          </label>
        </div>
        <p className="fine-print">
          Evidence source paths ({inputSources.evidence_source_paths}) are auto-filled from Source
          Archive when available.
        </p>
        <textarea
          className="approval-evidence-input"
          placeholder="Evidence source paths (optional, one path per line)"
          rows={4}
          value={input.evidence_source_paths.join("\n")}
          onChange={(event) =>
            onInputChange({
              ...input,
              evidence_source_paths: splitLines(event.target.value)
            })
          }
        />
        <label className="checkbox-row">
          <input
            checked={input.overwrite}
            type="checkbox"
            onChange={(event) => onInputChange({ ...input, overwrite: event.target.checked })}
          />
          Allow overwrite when target file already exists
        </label>
      </div>

      {preview && (
        <div className={`evidence-plan-card ${preview.blockers.length > 0 ? "evidence-plan-conflict" : ""}`}>
          <div className="folder-preview-heading">
            <div>
              <span>{preview.blockers.length > 0 ? "Blocked by conflicts" : "Ready to place"}</span>
              <strong>{preview.project_folder_path}</strong>
            </div>
          </div>
          {(preview.blockers.length > 0 || preview.warnings.length > 0) && (
            <div className="message-list message-list-warning">
              <ul>
                {[...preview.blockers, ...preview.warnings].map((message) => (
                  <li key={message}>{message}</li>
                ))}
              </ul>
            </div>
          )}
          <ul className="evidence-item-list">
            {preview.items.map((item) => (
              <li key={`${item.source_path}-${item.target_path}`}>
                <div>
                  <strong>{item.classification}</strong>
                  <span>{item.target_relative_path}</span>
                </div>
                <em>{item.status}</em>
              </li>
            ))}
          </ul>
        </div>
      )}

      {result && (
        <div className="latest-ltr-card">
          <span>Approval package placed</span>
          <strong>{result.items.filter((item) => item.status === "copied").length} copied</strong>
          <p>{result.items.length} items processed in execute mode.</p>
        </div>
      )}
    </section>
  );
}

function updateField(
  event: ChangeEvent<HTMLInputElement>,
  input: ApprovalPackageRequest,
  onInputChange: (next: ApprovalPackageRequest) => void,
  key: "project_folder_path" | "completed_application_form_path" | "test_record_output_path"
): void {
  onInputChange({
    ...input,
    [key]: event.target.value
  });
}

function splitLines(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}
