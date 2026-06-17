import type { ReactElement } from "react";
import { ProjectFolderTaskList } from "./ProjectFolderTaskList";
import { ProjectWorkbenchExecutionConsole } from "./ProjectWorkbenchExecutionConsole";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import type {
  ProjectFolderTaskActionTarget,
  ProjectFolderTaskKey,
  ProjectFolderTaskRow,
} from "./projectFolderTaskSelectors";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

type ProjectWorkbenchActiveMatrixWorkspaceProps = {
  activeMatrixAuthorityReady: boolean;
  confirmedFeeLatest: ProjectRuntimeConsoleModel["confirmedFeeLatest"];
  creatingFolder: boolean;
  effectiveFolderReady: boolean;
  feeEvaluationOutputStatus: ProjectRuntimeConsoleModel["versionStatus"]["downstream"][number] | null;
  officialWorkspaceStatus: NonNullable<ProjectRuntimeConsoleModel["officialWorkspacePreview"]>["status"] | null | undefined;
  onFolderCommand: () => void;
  onOpenFeeEvaluation: () => void;
  onOpenMatrixEditor: () => void;
  onProjectFolderTaskAction: (actionTarget: ProjectFolderTaskActionTarget) => void;
  onSelectProjectFolderTask: (taskKey: ProjectFolderTaskKey) => void;
  projectFolderTasks: ProjectFolderTaskRow[];
  projectId: string;
  projectIdentity: string;
  projectSubtitle: string;
  requestMaterialPreview: ProjectRuntimeConsoleModel["requestMaterialPreview"];
  requestMaterialError: ProjectRuntimeConsoleModel["requestMaterialError"];
  requestMaterialLoading: boolean;
  requiredFormsPreview: ProjectRuntimeConsoleModel["requiredFormsPreview"];
  requiredFormsError: ProjectRuntimeConsoleModel["requiredFormsError"];
  requiredFormsLoading: boolean;
  publicDriveUploadPreview: ProjectRuntimeConsoleModel["publicDriveUploadPreview"];
  publicDriveUploadError: ProjectRuntimeConsoleModel["publicDriveUploadError"];
  publicDriveUploadLoading: boolean;
  currentProjectFolderTaskKey: ProjectFolderTaskKey;
  selectedProjectFolderTaskKey: ProjectFolderTaskKey;
  runtimeProjectionSnapshot: ProjectRuntimeConsoleModel["runtimeProjectionSnapshot"];
  selectedProjectionToken: MatrixProjectionTokenCell | null;
  setSelectedProjectionToken: (token: MatrixProjectionTokenCell | null) => void;
};

export function ProjectWorkbenchActiveMatrixWorkspace({
  activeMatrixAuthorityReady,
  confirmedFeeLatest,
  creatingFolder,
  effectiveFolderReady,
  feeEvaluationOutputStatus,
  officialWorkspaceStatus,
  onFolderCommand,
  onOpenFeeEvaluation,
  onOpenMatrixEditor,
  onProjectFolderTaskAction,
  onSelectProjectFolderTask,
  projectFolderTasks,
  projectId,
  projectIdentity,
  projectSubtitle,
  requestMaterialPreview,
  requestMaterialError,
  requestMaterialLoading,
  requiredFormsPreview,
  requiredFormsError,
  requiredFormsLoading,
  publicDriveUploadPreview,
  publicDriveUploadError,
  publicDriveUploadLoading,
  currentProjectFolderTaskKey,
  selectedProjectFolderTaskKey,
  runtimeProjectionSnapshot,
  selectedProjectionToken,
  setSelectedProjectionToken,
}: ProjectWorkbenchActiveMatrixWorkspaceProps): ReactElement {
  const canGenerateFolder =
    officialWorkspaceStatus === "ready" || officialWorkspaceStatus === "adoptable";
  const visibleProjectFolderTasks =
    !effectiveFolderReady && !canGenerateFolder
      ? withoutUnavailableFolderAction(projectFolderTasks)
      : projectFolderTasks;
  const currentFolderTask =
    visibleProjectFolderTasks.find((task) => task.key === currentProjectFolderTaskKey) ??
    visibleProjectFolderTasks[0];
  const folderCommand = deriveFolderCommand({
    creatingFolder,
    effectiveFolderReady,
    officialWorkspaceStatus,
    currentFolderTask,
  });

  return (
    <section className="runtime-console-active-matrix" aria-label="Test Execution Workspace">
      <section className="runtime-console-commandbar" aria-label="Project commands">
        <div className="runtime-console-commandbar-identity">
          <strong>{projectIdentity}</strong>
          <span>{projectSubtitle}</span>
        </div>
        <div className="runtime-console-commandbar-status" aria-label="Project status">
          <StatusChip tone="ready" label={activeMatrixAuthorityReady ? "Matrix confirmed" : "Matrix missing"} />
          <StatusChip
            tone={confirmedFeeLatest?.status === "current" ? "ready" : "warning"}
            label={formatFeeAuthorityLabel(confirmedFeeLatest)}
          />
          <StatusChip
            tone={effectiveFolderReady ? "ready" : "warning"}
            label={effectiveFolderReady ? "Folder generated" : "Folder not generated"}
          />
        </div>
        <div className="runtime-console-commandbar-actions">
          <button type="button" onClick={onOpenMatrixEditor}>
            Open Matrix
          </button>
          <button type="button" onClick={onOpenFeeEvaluation}>
            Open Fee
          </button>
          <button
            type="button"
            className="is-primary"
            disabled={folderCommand.disabled}
            title={folderCommand.disabledReason}
            onClick={onFolderCommand}
          >
            {folderCommand.label}
          </button>
          <button
            type="button"
            disabled
            title="Activity history is a planned future surface."
          >
            History
          </button>
        </div>
      </section>

      <header className="runtime-console-workspace-heading">
        <div>
          <h3>Test Execution Workspace</h3>
          <p>
            Use the confirmed Matrix as the main testing map. Folder generation and updates
            stay in the command bar and inspector.
          </p>
        </div>
      </header>

      <section className="runtime-console-workbench-canvas">
        <ProjectWorkbenchExecutionConsole
          feeEvaluationOutputStatus={feeEvaluationOutputStatus}
          activeMatrixAuthorityReady={activeMatrixAuthorityReady}
          onOpenFeeEvaluation={onOpenFeeEvaluation}
          onOpenMatrixEditor={onOpenMatrixEditor}
          projectId={projectId}
          runtimeProjectionSnapshot={runtimeProjectionSnapshot}
          selectedProjectionToken={selectedProjectionToken}
          setSelectedProjectionToken={setSelectedProjectionToken}
          sideColumnAfter={
            <section className="runtime-console-folder-inspector" aria-label="Folder Action">
            <p className="eyebrow">Folder Action</p>
            <h3>{currentFolderTask.title}</h3>
            <strong className={`runtime-console-folder-inspector-status status-${currentFolderTask.status}`}>
              {currentFolderTask.statusLabel}
            </strong>
            <p>{currentFolderTask.summary}</p>
            <FolderTaskMessages task={currentFolderTask} />
            {currentFolderTask.actionLabel && currentFolderTask.actionTarget ? (
              <button
                type="button"
                onClick={() => onProjectFolderTaskAction(currentFolderTask.actionTarget ?? null)}
              >
                {currentFolderTask.actionLabel}
              </button>
            ) : null}
          </section>
          }
        />
      </section>

      <details className="runtime-console-folder-bottom-details">
        <summary>Project folder details</summary>
        <ProjectFolderTaskList
          tasks={visibleProjectFolderTasks}
          currentTaskKey={currentProjectFolderTaskKey}
          selectedTaskKey={selectedProjectFolderTaskKey}
          onSelectTask={onSelectProjectFolderTask}
          onTaskAction={onProjectFolderTaskAction}
          requestMaterialPreview={requestMaterialPreview}
          requestMaterialError={requestMaterialError}
          requestMaterialLoading={requestMaterialLoading}
          requiredFormsPreview={requiredFormsPreview}
          requiredFormsError={requiredFormsError}
          requiredFormsLoading={requiredFormsLoading}
          publicDriveUploadPreview={publicDriveUploadPreview}
          publicDriveUploadError={publicDriveUploadError}
          publicDriveUploadLoading={publicDriveUploadLoading}
        />
      </details>
    </section>
  );
}

function withoutUnavailableFolderAction(
  tasks: ProjectFolderTaskRow[]
): ProjectFolderTaskRow[] {
  return tasks.map((task) =>
    task.key === "local_project_folder"
      ? {
          ...task,
          actionLabel: undefined,
          actionTarget: undefined,
          summary:
            "Project folder generation is unavailable until the template and target path are ready.",
        }
      : task
  );
}

function StatusChip({
  label,
  tone,
}: {
  label: string;
  tone: "ready" | "warning";
}): ReactElement {
  return <span className={`runtime-console-status-chip status-${tone}`}>{label}</span>;
}

function FolderTaskMessages({ task }: { task: ProjectFolderTaskRow }): ReactElement | null {
  const messages = [...task.blockers, ...task.warnings].slice(0, 2);
  if (messages.length === 0) {
    return null;
  }
  return (
    <ul className="runtime-console-inspector-messages">
      {messages.map((message) => (
        <li key={message}>{message}</li>
      ))}
    </ul>
  );
}

function formatFeeAuthorityLabel(
  confirmedFeeLatest: ProjectRuntimeConsoleModel["confirmedFeeLatest"]
): string {
  if (confirmedFeeLatest?.status === "current") {
    const revision = confirmedFeeLatest.confirmed_fee?.confirmed_fee_revision;
    return revision ? `Fee v${revision} confirmed` : "Fee confirmed";
  }
  if (confirmedFeeLatest?.status === "stale") {
    return "Fee needs update";
  }
  return "Fee not confirmed";
}

function deriveFolderCommand({
  creatingFolder,
  currentFolderTask,
  effectiveFolderReady,
  officialWorkspaceStatus,
}: {
  creatingFolder: boolean;
  currentFolderTask: ProjectFolderTaskRow;
  effectiveFolderReady: boolean;
  officialWorkspaceStatus: NonNullable<ProjectRuntimeConsoleModel["officialWorkspacePreview"]>["status"] | null | undefined;
}): {
  disabled: boolean;
  disabledReason?: string;
  label: string;
} {
  if (!effectiveFolderReady) {
    const canGenerate =
      officialWorkspaceStatus === "ready" || officialWorkspaceStatus === "adoptable";
    return {
      disabled: creatingFolder || !canGenerate,
      disabledReason: canGenerate
        ? undefined
        : "Project folder template or target path is not ready.",
      label: creatingFolder ? "Generating..." : "Generate folder",
    };
  }
  if (currentFolderTask.actionLabel && currentFolderTask.actionTarget) {
    return {
      disabled: false,
      label: currentFolderTask.actionLabel,
    };
  }
  return {
    disabled: true,
    disabledReason: "Project folder actions are current.",
    label: "Folder ready",
  };
}
