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
  const blocker = readonlyReason ?? task.blockers[0] ?? null;
  const disabled = Boolean(readonlyReason || !task.actionTarget);
  return (
    <article className="runtime-console-folder-operation">
      <span className="runtime-console-folder-operation-icon">
        <UiIcon name={task.iconName} />
      </span>
      <div className="runtime-console-folder-operation-copy">
        <h3>{task.title}</h3>
        <p>{task.summary}</p>
        <small>{task.context}</small>
        {task.detailMessages && task.detailMessages.length > 0 ? (
          <ul className="runtime-console-folder-operation-details">
            {task.detailMessages.slice(0, 2).map((message) => (
              <li key={message}>{message}</li>
            ))}
          </ul>
        ) : null}
      </div>
      <div className="runtime-console-folder-operation-controls">
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
          </label>
        ) : null}
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
        ) : task.actionLabel ? (
          <button
            type="button"
            disabled={disabled}
            title={blocker ?? undefined}
            onClick={() => {
              if (task.actionTarget) {
                onTaskAction?.(task.actionTarget);
              }
            }}
          >
            {task.actionLabel}
          </button>
        ) : null}
      </div>
    </article>
  );
}

function selectPanelBlocker(tasks: ProjectFolderTaskRow[]): string | null {
  const directBlocker = tasks.flatMap((task) => task.blockers)[0];
  return directBlocker ?? null;
}
