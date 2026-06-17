import type { ReactElement } from "react";
import type { OfficialWorkspacePreview } from "../../api/client";

type OfficialWorkspaceActionPanelProps = {
  preview: OfficialWorkspacePreview | null;
  loading: boolean;
  creating: boolean;
  error: string | null;
  onCreate: () => Promise<void>;
};

export function OfficialWorkspaceActionPanel({
  preview,
  loading,
  creating,
  error,
  onCreate,
}: OfficialWorkspaceActionPanelProps): ReactElement {
  const blocked =
    preview?.status === "blocked" ||
    preview?.status === "exists" ||
    preview?.status === "inconsistent";
  const settingsBlocked =
    blocked &&
    (preview?.blockers ?? []).some((blocker) =>
      /project default save location|template folder|workspace root|template path|configured|settings/i.test(blocker)
    );
  const reason = blocked
    ? formatWorkspaceBlocker(preview?.blockers[0], settingsBlocked)
    : "Create the formal project folder from the standard template.";
  const nextActionTitle = settingsBlocked
    ? "Project folder template is not ready"
    : blocked
      ? "Resolve project folder blocker"
      : "Create official project folder locally";
  const nextActionDescription = settingsBlocked
    ? "Ask the ConnLab administrator to confirm the installed template before creating the folder."
    : blocked
      ? "Review the blocker before creating the local project folder."
      : "ConnLab will copy the template and prepare the standard folders.";
  const pathSummaryTitle = formatWorkspacePathSummaryTitle(preview?.status ?? null);

  return (
    <section className="runtime-console-mode-stack" aria-label="Local project folder">
      <section className={`runtime-console-folder-primary ${blocked ? "status-blocked" : "status-ready"}`}>
        <div className="runtime-console-folder-task-heading">
          <p className="eyebrow">Next step</p>
          <h3>{nextActionTitle}</h3>
          <p>{reason}</p>
          <p>{nextActionDescription}</p>
          {blocked ? (
            <p className="runtime-console-action-unavailable">
              {settingsBlocked
                ? "Creation is unavailable until the ConnLab project template is ready."
                : "Creation is unavailable until this blocker is resolved."}
            </p>
          ) : (
            <button
              type="button"
              disabled={loading || creating}
              onClick={() => void onCreate()}
            >
              {creating ? "Creating..." : "Create project folder"}
            </button>
          )}
        </div>
      </section>

      {error ? <p className="runtime-console-error">{error}</p> : null}

      <details className="runtime-console-diagnostics">
        <summary>{pathSummaryTitle}</summary>
        <dl>
          <div>
            <dt>Local DL folder</dt>
            <dd>{preview?.local_workspace_path ?? "Available after the local DL folder is created."}</dd>
          </div>
          <div>
            <dt>Official project folder</dt>
            <dd>{preview?.official_project_folder_path ?? "Available after the official folder is created."}</dd>
          </div>
          <div>
            <dt>Source Book</dt>
            <dd>{preview?.source_book_path ?? "Available after the local DL folder is created."}</dd>
          </div>
        </dl>
      </details>
    </section>
  );
}

function formatWorkspacePathSummaryTitle(
  status: OfficialWorkspacePreview["status"] | null
): string {
  if (status === "completed") {
    return "Created project folder paths";
  }
  if (status === "exists" || status === "inconsistent") {
    return "Project folder check paths";
  }
  return "Planned project folder paths";
}

function formatWorkspaceBlocker(
  blocker: string | undefined,
  settingsBlocked: boolean
): string {
  if (!blocker) {
    return "Resolve project folder blockers before continuing.";
  }
  if (settingsBlocked) {
    return "ConnLab project folder template is not ready.";
  }
  return blocker;
}
