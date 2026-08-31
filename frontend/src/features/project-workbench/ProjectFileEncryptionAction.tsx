import { useState, type ReactElement } from "react";
import {
  executeProjectFileEncryption,
  previewProjectFileEncryption,
  type ProjectFileEncryptionPreview,
  type ProjectFileEncryptionResult,
} from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";

export function ProjectFileEncryptionAction({
  projectId,
  available,
  readonlyReason,
}: {
  projectId: string;
  available: boolean;
  readonlyReason?: string;
}): ReactElement {
  const [preview, setPreview] = useState<ProjectFileEncryptionPreview | null>(null);
  const [result, setResult] = useState<ProjectFileEncryptionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const disabledReason = readonlyReason ??
    (!available ? "Create the local project folder before encrypting project files." : null);

  async function openPreview(): Promise<void> {
    if (disabledReason) {
      return;
    }
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const response = await previewProjectFileEncryption(projectId);
      setPreview(response.status === "ready" || response.status === "conflict" ? response : null);
      if (response.status === "blocked") {
        setError(response.blockers[0] ?? "Project files cannot be encrypted yet.");
      } else if (response.status === "empty") {
        setError("No supported unencrypted files were found in the two controlled layers.");
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function execute(conflictAction: "overwrite" | "skip"): Promise<void> {
    if (!preview) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const response = await executeProjectFileEncryption(projectId, {
        expected_plan_token: preview.plan_token,
        conflict_action: conflictAction,
      });
      setResult(response);
      setPreview(null);
      if (response.failed_count > 0) {
        const firstFailure = response.items.find((item) => item.status === "failed");
        setError(
          firstFailure
            ? `${firstFailure.file_name}: ${firstFailure.message}`
            : `${response.failed_count} file${response.failed_count === 1 ? "" : "s"} failed and remained unchanged.`
        );
      }
    } catch (err) {
      setError((err as Error).message);
      setPreview(null);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <article className="project-file-encryption-action">
        <span className="runtime-console-folder-operation-icon" aria-hidden="true">
          <UiIcon name="file" />
        </span>
        <div className="runtime-console-folder-operation-copy">
          <div className="runtime-console-folder-operation-title">
            <h3>Encrypt project files</h3>
          </div>
          <p>Protect supported current-layer Office files with controlled project passwords.</p>
          <small>Subfolders and macro-enabled files are never processed.</small>
          {result ? (
            <small className={result.failed_count ? "is-danger" : "is-success"} role="status">
              Encrypted {result.encrypted_count}; skipped {result.skipped_count}; failed {result.failed_count}.
            </small>
          ) : null}
          {error ? <small className="is-danger" role="alert">{error}</small> : null}
        </div>
        <div className="runtime-console-folder-operation-controls">
          <button
            type="button"
            disabled={busy || Boolean(disabledReason)}
            title={disabledReason ?? undefined}
            onClick={() => void openPreview()}
          >
            {busy ? "Working..." : "Preview"}
          </button>
        </div>
      </article>
      {preview ? (
        <ProjectFileEncryptionDialog
          preview={preview}
          busy={busy}
          onCancel={() => setPreview(null)}
          onExecute={execute}
        />
      ) : null}
    </>
  );
}

function ProjectFileEncryptionDialog({
  preview,
  busy,
  onCancel,
  onExecute,
}: {
  preview: ProjectFileEncryptionPreview;
  busy: boolean;
  onCancel: () => void;
  onExecute: (action: "overwrite" | "skip") => Promise<void>;
}): ReactElement {
  const visibleItems = preview.items.slice(0, 8);
  const extraCount = preview.items.length - visibleItems.length;
  return (
    <div className="runtime-console-modal-backdrop">
      <section
        aria-label="Encrypt project files preview"
        aria-modal="true"
        className="runtime-console-conflict-dialog project-file-encryption-dialog"
        role="dialog"
      >
        <header>
          <h2>Encrypt project files</h2>
          <p>
            Review {preview.items.length} file{preview.items.length === 1 ? "" : "s"} before any changes are made.
          </p>
        </header>
        <ul className="project-file-encryption-preview-list">
          {visibleItems.map((item) => (
            <li key={`${item.location}:${item.file_name}`}>
              <span>{item.file_name}</span>
              <small>{item.location === "official_root" ? "Project folder" : "Test results"}</small>
              {item.conflict ? <strong>Secured file exists</strong> : null}
            </li>
          ))}
        </ul>
        {extraCount > 0 ? <p>+{extraCount} more files</p> : null}
        <p className="project-file-encryption-dialog-note">
          Test results originals move to History only after the encrypted copy is verified.
        </p>
        <div className="runtime-console-conflict-actions">
          {preview.conflict_count > 0 ? (
            <>
              <button type="button" disabled={busy} onClick={() => void onExecute("overwrite")}>
                Overwrite all
              </button>
              <button type="button" disabled={busy} onClick={() => void onExecute("skip")}>
                Skip all
              </button>
            </>
          ) : (
            <button type="button" disabled={busy} onClick={() => void onExecute("overwrite")}>
              Encrypt files
            </button>
          )}
          <button type="button" disabled={busy} onClick={onCancel}>Cancel</button>
        </div>
      </section>
    </div>
  );
}
