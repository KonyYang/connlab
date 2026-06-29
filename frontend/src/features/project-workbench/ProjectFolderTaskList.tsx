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
  onTaskAction,
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
  return <ProjectFolderActionsSurface tasks={tasks} onTaskAction={onTaskAction} />;
}

export function ProjectFolderActionsSurface({
  tasks,
  onTaskAction,
  readonlyReason,
}: {
  tasks: ProjectFolderTaskRow[];
  onTaskAction?: (actionTarget: ProjectFolderTaskActionTarget) => void;
  readonlyReason?: string;
}): ReactElement {
  return (
    <section className="runtime-console-folder-actions" aria-label="Folder Actions">
      <header className="runtime-console-folder-actions-header">
        <p className="eyebrow">Folder Actions</p>
      </header>
      <div className="runtime-console-folder-operation-grid">
        {tasks.map((task) => (
          <FolderOperation
            key={task.key}
            task={task}
            onTaskAction={onTaskAction}
            readonlyReason={readonlyReason}
          />
        ))}
      </div>
    </section>
  );
}

function FolderOperation({
  task,
  onTaskAction,
  readonlyReason,
}: {
  task: ProjectFolderTaskRow;
  onTaskAction?: (actionTarget: ProjectFolderTaskActionTarget) => void;
  readonlyReason?: string;
}): ReactElement {
  const blocker = readonlyReason ?? task.blockers[0] ?? null;
  const disabled = Boolean(readonlyReason || !task.actionTarget);
  return (
    <article className="runtime-console-folder-operation">
      <div className="runtime-console-folder-operation-copy">
        <h3>{task.title}</h3>
        <p>{task.summary}</p>
      </div>
      <div className="runtime-console-folder-operation-controls">
        {task.key === "public_working_copy" ? (
          <label className="runtime-console-folder-auto-sync">
            <input type="checkbox" disabled aria-label="Auto sync public working copy" />
            <span>Auto sync</span>
          </label>
        ) : null}
        {task.actionLabel ? (
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
      {blocker ? <p className="runtime-console-folder-operation-blocker">{blocker}</p> : null}
    </article>
  );
}
