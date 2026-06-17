import type { ReactElement } from "react";
import type {
  ProjectFolderRequiredFormsPreview,
  PublicDriveUploadPreview,
  RequestMaterialPreview,
} from "../../api/client";
import type {
  ProjectFolderTaskActionTarget,
  ProjectFolderTaskKey,
  ProjectFolderTaskRow,
} from "./projectFolderTaskSelectors";

export function ProjectFolderTaskList({
  tasks,
  currentTaskKey,
  selectedTaskKey,
  onSelectTask,
  onTaskAction,
  requestMaterialPreview,
  requestMaterialError,
  requestMaterialLoading,
  requiredFormsPreview,
  requiredFormsError,
  requiredFormsLoading,
  publicDriveUploadPreview,
  publicDriveUploadError,
  publicDriveUploadLoading,
}: {
  tasks: ProjectFolderTaskRow[];
  currentTaskKey: ProjectFolderTaskKey;
  selectedTaskKey: ProjectFolderTaskKey;
  onSelectTask: (taskKey: ProjectFolderTaskKey) => void;
  onTaskAction: (actionTarget: ProjectFolderTaskActionTarget) => void;
  requestMaterialPreview: RequestMaterialPreview | null;
  requestMaterialError: string | null;
  requestMaterialLoading: boolean;
  requiredFormsPreview: ProjectFolderRequiredFormsPreview | null;
  requiredFormsError: string | null;
  requiredFormsLoading: boolean;
  publicDriveUploadPreview: PublicDriveUploadPreview | null;
  publicDriveUploadError: string | null;
  publicDriveUploadLoading: boolean;
}): ReactElement {
  const selectedTask = tasks.find((task) => task.key === selectedTaskKey) ?? tasks[0];
  const currentTask = tasks.find((task) => task.key === currentTaskKey) ?? selectedTask;
  const detailTask = selectedTask.key === currentTask.key ? currentTask : selectedTask;

  return (
    <section className="runtime-console-project-folder-flow">
      <section className="runtime-console-folder-primary" aria-label="Current Project Folder action">
        <div className="runtime-console-folder-task-heading">
          <p className="eyebrow">Next step</p>
          <h3>{currentTask.title}</h3>
          <p>{currentTask.summary}</p>
          {currentTask.actionLabel && currentTask.actionTarget ? (
            <button
              type="button"
              onClick={() => onTaskAction(currentTask.actionTarget ?? null)}
            >
              {currentTask.actionLabel}
            </button>
          ) : (
            <p className="runtime-console-muted-action">{currentTask.statusLabel}</p>
          )}
        </div>
        <TaskMessages task={currentTask} />
      </section>

      <section className="runtime-console-project-folder-steps" aria-label="Project Folder progress">
        {tasks.map((task) => {
          const isSelected = task.key === detailTask.key;
          const isCurrent = task.key === currentTaskKey;
          return (
            <button
              key={task.key}
              type="button"
              className={`runtime-console-folder-task-row status-${task.status}${
                isSelected ? " is-selected" : ""
              }`}
              aria-current={isCurrent ? "step" : undefined}
              aria-pressed={isSelected}
              onClick={() => onSelectTask(task.key)}
            >
              <span className={`runtime-console-state-dot runtime-console-state-${task.status}`} />
              <span>
                <strong>{task.title}</strong>
                <small>{task.statusLabel}</small>
              </span>
              {isCurrent ? <em>Now</em> : null}
            </button>
          );
        })}
      </section>

      <details className="runtime-console-folder-detail-panel">
        <summary>{detailTask.key === currentTask.key ? "Show details" : `Show ${detailTask.title} details`}</summary>

        <div
          className="runtime-console-current-folder-task"
          aria-label="Selected Project Folder task"
        >
          <div className="runtime-console-folder-task-heading">
            <p className="eyebrow">{detailTask.statusLabel}</p>
            <h3>{detailTask.title}</h3>
            <p>{detailTask.summary}</p>
            {detailTask.actionLabel && detailTask.actionTarget && detailTask.key !== currentTask.key ? (
              <button
                type="button"
                onClick={() => onTaskAction(detailTask.actionTarget ?? null)}
              >
                {detailTask.actionLabel}
              </button>
            ) : null}
          </div>

          <TaskMessages task={detailTask} />

        {detailTask.detailKind === "request_material" ? (
          <RequestMaterialDetail
            preview={requestMaterialPreview}
            error={requestMaterialError}
            loading={requestMaterialLoading}
          />
        ) : null}

        {detailTask.detailKind === "public_drive" ? (
          <PublicDriveUploadDetail
            preview={publicDriveUploadPreview}
            error={publicDriveUploadError}
            loading={publicDriveUploadLoading}
          />
        ) : null}

        {detailTask.detailKind === "required_forms" ? (
          <RequiredFormsDetail
            preview={requiredFormsPreview}
            error={requiredFormsError}
            loading={requiredFormsLoading}
          />
        ) : null}

        {detailTask.detailKind !== "request_material" &&
        detailTask.detailKind !== "public_drive" &&
        detailTask.detailKind !== "required_forms" ? (
          <GenericTaskDetail task={detailTask} />
        ) : null}
        </div>
      </details>
    </section>
  );
}

function TaskMessages({ task }: { task: ProjectFolderTaskRow }): ReactElement | null {
  const messages = [...task.blockers, ...task.warnings];
  if (messages.length === 0) {
    return null;
  }
  return (
    <ul className="runtime-console-blocker-list">
      {messages.map((message) => (
        <li key={message}>{message}</li>
      ))}
    </ul>
  );
}

function RequestMaterialDetail({
  preview,
  error,
  loading,
}: {
  preview: RequestMaterialPreview | null;
  error: string | null;
  loading: boolean;
}): ReactElement {
  const copiedCount =
    preview?.items.filter((item) =>
      item.status === "copied" || item.status === "already_present"
    ).length ?? 0;
  const reviewCount = preview?.items.filter((item) => item.review_required).length ?? 0;
  return (
    <div className="runtime-console-folder-task-detail">
      <dl className="runtime-console-compact-metrics">
        <div>
          <dt>Files checked</dt>
          <dd>{loading ? "Loading" : preview?.items.length ?? 0}</dd>
        </div>
        <div>
          <dt>Already collected</dt>
          <dd>{copiedCount}</dd>
        </div>
        <div>
          <dt>Needs review</dt>
          <dd>{reviewCount}</dd>
        </div>
      </dl>
      <PathLine label="Official project folder" value={preview?.official_project_folder_path} />
      <PathLine label="Source Book" value={preview?.source_book_path} />
      {error ? <p className="runtime-console-error">{error}</p> : null}
    </div>
  );
}

function RequiredFormsDetail({
  preview,
  error,
  loading,
}: {
  preview: ProjectFolderRequiredFormsPreview | null;
  error: string | null;
  loading: boolean;
}): ReactElement {
  const items = preview?.items ?? [];
  const readyCount = items.filter((item) =>
    item.action === "generate" || item.action === "update"
  ).length;
  const currentCount = items.filter((item) => item.action === "skip").length;
  const conflictCount = items.filter((item) => item.action === "conflict").length;
  return (
    <div className="runtime-console-folder-task-detail">
      <dl className="runtime-console-compact-metrics">
        <div>
          <dt>Forms ready to generate</dt>
          <dd>{loading ? "Loading" : readyCount}</dd>
        </div>
        <div>
          <dt>Already current</dt>
          <dd>{currentCount}</dd>
        </div>
        <div>
          <dt>Conflict</dt>
          <dd>{conflictCount}</dd>
        </div>
      </dl>
      <PathLine label="Official project folder" value={preview?.official_project_folder_path} />
      {error ? <p className="runtime-console-error">{error}</p> : null}
      <details className="runtime-console-public-drive-items" open={items.length > 0}>
        <summary>Required form targets</summary>
        {items.length > 0 ? (
          <ul>
            {items.map((item) => (
              <li key={item.key}>
                <span>{formatRequiredFormAction(item.action)}</span>
                <strong>{item.label}</strong>
                <em>{displayProjectFolderRelativePath(preview, item.target_path)}</em>
                <p>{item.message}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No Required forms preview is available yet.</p>
        )}
      </details>
    </div>
  );
}

function PublicDriveUploadDetail({
  preview,
  error,
  loading,
}: {
  preview: PublicDriveUploadPreview | null;
  error: string | null;
  loading: boolean;
}): ReactElement {
  const counts = preview?.counts ?? {};
  const items = preview?.items ?? [];
  return (
    <div className="runtime-console-folder-task-detail">
      <dl className="runtime-console-compact-metrics">
        <div>
          <dt>Add</dt>
          <dd>{loading ? "Loading" : counts.add ?? 0}</dd>
        </div>
        <div>
          <dt>Update</dt>
          <dd>{counts.update ?? 0}</dd>
        </div>
        <div>
          <dt>Already current</dt>
          <dd>{counts.skip ?? 0}</dd>
        </div>
        <div>
          <dt>Conflict</dt>
          <dd>{counts.conflict ?? 0}</dd>
        </div>
      </dl>
      <PathLine label="Public folder" value={preview?.public_project_folder_path} />
      {error ? <p className="runtime-console-error">{error}</p> : null}
      <details className="runtime-console-public-drive-items" open={items.length > 0}>
        <summary>Upload preview items</summary>
        {items.length > 0 ? (
          <ul>
            {items.map((item) => (
              <li key={`${item.kind}:${item.relative_path}`}>
                <span>{formatUploadAction(item.action)}</span>
                <strong>{item.relative_path}</strong>
                <em>{item.kind === "directory" ? "Folder" : "File"}</em>
                <p>{item.message}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No upload items are available yet.</p>
        )}
      </details>
    </div>
  );
}

function formatRequiredFormAction(action: string): string {
  if (action === "generate") {
    return "Generate";
  }
  if (action === "update") {
    return "Update";
  }
  if (action === "skip") {
    return "Current";
  }
  if (action === "conflict") {
    return "Conflict";
  }
  if (action === "blocked") {
    return "Blocked";
  }
  return action;
}

function displayProjectFolderRelativePath(
  preview: ProjectFolderRequiredFormsPreview | null,
  targetPath: string | null
): string {
  if (!targetPath) {
    return "Target not available";
  }
  const root = preview?.official_project_folder_path;
  const normalizedTarget = targetPath.replaceAll("\\", "/");
  if (!root) {
    return normalizedTarget;
  }
  const normalizedRoot = root.replaceAll("\\", "/").replace(/\/+$/, "");
  if (normalizedTarget.startsWith(`${normalizedRoot}/`)) {
    return normalizedTarget.slice(normalizedRoot.length + 1);
  }
  return normalizedTarget;
}

function GenericTaskDetail({ task }: { task: ProjectFolderTaskRow }): ReactElement {
  return (
    <div className="runtime-console-folder-task-detail">
      <p>{task.summary}</p>
    </div>
  );
}

function PathLine({
  label,
  value,
}: {
  label: string;
  value: string | null | undefined;
}): ReactElement {
  return (
    <div className="runtime-console-path-line">
      <span>{label}</span>
      <strong>{value ?? "Not checked"}</strong>
    </div>
  );
}

function formatUploadAction(action: string): string {
  if (action === "add") {
    return "Add";
  }
  if (action === "update") {
    return "Update";
  }
  if (action === "skip") {
    return "Skip";
  }
  if (action === "conflict") {
    return "Conflict";
  }
  if (action === "deferred") {
    return "Deferred";
  }
  return action;
}
