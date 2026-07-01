import type { ReactElement } from "react";
import type {
  ProjectFolderRequiredFormsPreview,
  PublicFolderWorkflowOperationType,
  PublicDriveUploadPreview,
  RequestMaterialPreview,
} from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";
import type {
  ProjectFolderTaskActionTarget,
  ProjectFolderTaskKey,
  ProjectFolderTaskRow,
} from "./projectFolderTaskSelectors";

export function ProjectFolderTaskList({
  tasks,
  onTaskAction,
  onTaskConfirm,
  onTaskCancel,
  onAutoSyncChange,
}: {
  tasks: ProjectFolderTaskRow[];
  currentTaskKey: ProjectFolderTaskKey;
  selectedTaskKey: ProjectFolderTaskKey;
  onSelectTask: (taskKey: ProjectFolderTaskKey) => void;
  onTaskAction: (actionTarget: ProjectFolderTaskActionTarget) => void;
  onTaskConfirm?: (operation: PublicFolderWorkflowOperationType) => void;
  onTaskCancel?: (operation: PublicFolderWorkflowOperationType) => void;
  onAutoSyncChange?: (enabled: boolean) => void;
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
  return (
    <ProjectFolderActionsSurface
      tasks={tasks}
      onTaskAction={onTaskAction}
      onTaskConfirm={onTaskConfirm}
      onTaskCancel={onTaskCancel}
      onAutoSyncChange={onAutoSyncChange}
    />
  );
}

export function ProjectFolderActionsSurface({
  tasks,
  onTaskAction,
  onTaskConfirm,
  onTaskCancel,
  onAutoSyncChange,
  readonlyReason,
}: {
  tasks: ProjectFolderTaskRow[];
  onTaskAction?: (actionTarget: ProjectFolderTaskActionTarget) => void;
  onTaskConfirm?: (operation: PublicFolderWorkflowOperationType) => void;
  onTaskCancel?: (operation: PublicFolderWorkflowOperationType) => void;
  onAutoSyncChange?: (enabled: boolean) => void;
  readonlyReason?: string;
}): ReactElement {
  const panelBlocker = readonlyReason ?? selectPanelBlocker(tasks);
  return (
    <section className="runtime-console-folder-actions" aria-label="Folder Actions">
      <header className="runtime-console-folder-actions-header">
        <p className="eyebrow">Folder Actions</p>
      </header>
      <div className="runtime-console-folder-operation-list">
        {tasks.map((task) => (
          <FolderOperation
            key={task.key}
            task={task}
            onTaskAction={onTaskAction}
            onTaskConfirm={onTaskConfirm}
            onTaskCancel={onTaskCancel}
            onAutoSyncChange={onAutoSyncChange}
            readonlyReason={readonlyReason}
          />
        ))}
      </div>
      {panelBlocker ? (
        <p className="runtime-console-folder-actions-blocker">{panelBlocker}</p>
      ) : null}
    </section>
  );
}

function FolderOperation({
  task,
  onTaskAction,
  onTaskConfirm,
  onTaskCancel,
  onAutoSyncChange,
  readonlyReason,
}: {
  task: ProjectFolderTaskRow;
  onTaskAction?: (actionTarget: ProjectFolderTaskActionTarget) => void;
  onTaskConfirm?: (operation: PublicFolderWorkflowOperationType) => void;
  onTaskCancel?: (operation: PublicFolderWorkflowOperationType) => void;
  onAutoSyncChange?: (enabled: boolean) => void;
  readonlyReason?: string;
}): ReactElement {
  const readonlyBlocksAction = Boolean(
    readonlyReason && task.actionTarget !== "project_folder_open"
  );
  const blocker = readonlyBlocksAction ? readonlyReason ?? null : task.blockers[0] ?? null;
  const disabled = Boolean(readonlyBlocksAction || !task.actionTarget);
  function activateTaskAction(): void {
    if (!disabled && task.actionTarget) {
      onTaskAction?.(task.actionTarget);
    }
  }

  return (
    <article className="runtime-console-folder-operation">
      {task.actionLabel ? (
        <button
          className="runtime-console-folder-operation-icon runtime-console-folder-operation-icon-button"
          type="button"
          aria-label={task.actionLabel}
          disabled={disabled}
          title={blocker ?? undefined}
          onClick={activateTaskAction}
        >
          <UiIcon name={task.iconName} />
        </button>
      ) : (
        <span className="runtime-console-folder-operation-icon" aria-hidden="true">
          <UiIcon name={task.iconName} />
        </span>
      )}
      <div className="runtime-console-folder-operation-copy">
        <div className="runtime-console-folder-operation-title">
          <h3>{task.title}</h3>
          {task.autoSync ? (
            <label className="runtime-console-folder-auto-sync">
              <input
                type="checkbox"
                checked={task.autoSync.checked}
                disabled={readonlyReason ? true : task.autoSync.disabled}
                aria-label="Auto sync public working copy"
                title={task.autoSync.blocker ?? undefined}
                onChange={(event) => onAutoSyncChange?.(event.currentTarget.checked)}
              />
              <span>Auto sync</span>
              <span className="runtime-console-folder-auto-sync-track" aria-hidden="true" />
            </label>
          ) : null}
        </div>
        {task.summary ? <p>{task.summary}</p> : null}
        {task.context ? <small>{task.context}</small> : null}
        {task.detailMessages && task.detailMessages.length > 0 ? (
          <ul className="runtime-console-folder-operation-details">
            {task.detailMessages.slice(0, 2).map((message) => (
              <li key={message}>{message}</li>
            ))}
          </ul>
        ) : null}
      </div>
      <div className="runtime-console-folder-operation-controls">
        {task.confirming && task.operation ? (
          <div className="runtime-console-folder-operation-confirmation">
            <button
              type="button"
              onClick={() => onTaskConfirm?.(task.operation as PublicFolderWorkflowOperationType)}
            >
              {task.confirmLabel ?? "Confirm"}
            </button>
            <button
              type="button"
              onClick={() => onTaskCancel?.(task.operation as PublicFolderWorkflowOperationType)}
            >
              {task.cancelLabel ?? "Cancel"}
            </button>
          </div>
        ) : null}
      </div>
    </article>
  );
}

function selectPanelBlocker(tasks: ProjectFolderTaskRow[]): string | null {
  const directBlocker = tasks.flatMap((task) => task.blockers)[0];
  return directBlocker ?? null;
}
