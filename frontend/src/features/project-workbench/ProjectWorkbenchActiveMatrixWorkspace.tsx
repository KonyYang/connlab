import type { ReactElement } from "react";
import { ProjectBasicInformationSummaryCard } from "../project-basic-information/ProjectBasicInformationSummaryCard";
import { ProjectWorkbenchExecutionConsole } from "./ProjectWorkbenchExecutionConsole";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import type { ProjectLifecycleReadonlyView } from "../project-lifecycle/projectLifecycleReadonlyModel";
import type {
  ProjectFolderTaskActionTarget,
  ProjectFolderTaskKey,
  ProjectFolderTaskRow,
} from "./projectFolderTaskSelectors";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

type ProjectWorkbenchActiveMatrixWorkspaceProps = {
  effectiveFolderReady: boolean;
  officialWorkspaceStatus: NonNullable<ProjectRuntimeConsoleModel["officialWorkspacePreview"]>["status"] | null | undefined;
  onProjectFolderTaskAction: (actionTarget: ProjectFolderTaskActionTarget) => void;
  projectFolderTasks: ProjectFolderTaskRow[];
  projectId: string;
  currentProjectFolderTaskKey: ProjectFolderTaskKey;
  basicInformation: ProjectRuntimeConsoleModel["basicInformation"];
  basicInformationLoading: ProjectRuntimeConsoleModel["basicInformationLoading"];
  basicInformationError: ProjectRuntimeConsoleModel["basicInformationError"];
  lifecycleReadonlyView: ProjectLifecycleReadonlyView;
  runtimeProjectionSnapshot: ProjectRuntimeConsoleModel["runtimeProjectionSnapshot"];
  selectedProjectionToken: MatrixProjectionTokenCell | null;
  setSelectedProjectionToken: (token: MatrixProjectionTokenCell | null) => void;
};

export function ProjectWorkbenchActiveMatrixWorkspace({
  effectiveFolderReady,
  officialWorkspaceStatus,
  onProjectFolderTaskAction,
  projectFolderTasks,
  projectId,
  currentProjectFolderTaskKey,
  basicInformation,
  basicInformationLoading,
  basicInformationError,
  lifecycleReadonlyView,
  runtimeProjectionSnapshot,
  selectedProjectionToken,
  setSelectedProjectionToken,
}: ProjectWorkbenchActiveMatrixWorkspaceProps): ReactElement {
  const canGenerateFolder =
    officialWorkspaceStatus === "ready" ||
    officialWorkspaceStatus === "adoptable" ||
    officialWorkspaceStatus === "exists";
  const visibleProjectFolderTasks =
    !effectiveFolderReady && !canGenerateFolder
      ? withoutUnavailableFolderAction(projectFolderTasks)
      : projectFolderTasks;
  const currentFolderTask =
    visibleProjectFolderTasks.find((task) => task.key === currentProjectFolderTaskKey) ??
    visibleProjectFolderTasks[0];
  return (
    <section className="runtime-console-active-matrix" aria-label="Test Execution Workspace">
      <section className="runtime-console-workbench-canvas">
        <ProjectWorkbenchExecutionConsole
          projectId={projectId}
          runtimeProjectionSnapshot={runtimeProjectionSnapshot}
          selectedProjectionToken={selectedProjectionToken}
          setSelectedProjectionToken={setSelectedProjectionToken}
          sideColumnAfter={
            <>
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
                    disabled={lifecycleReadonlyView.readonly}
                    title={lifecycleReadonlyView.readonly ? lifecycleReadonlyView.message : undefined}
                    type="button"
                    onClick={() => {
                      if (currentFolderTask.actionTarget) {
                        onProjectFolderTaskAction(currentFolderTask.actionTarget);
                      }
                    }}
                  >
                    {currentFolderTask.actionLabel}
                  </button>
                ) : null}
              </section>
              <ProjectBasicInformationSummaryCard
                projectId={projectId}
                basicInformation={basicInformation}
                loading={basicInformationLoading}
                error={basicInformationError}
              />
            </>
          }
        />
      </section>
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

export function deriveActiveMatrixFolderCommand({
  activeMatrixAuthorityReady,
  confirmedFeeLatest,
  creatingFolder,
  effectiveFolderReady,
  officialWorkspaceStatus,
  projectFolderBlocker,
}: {
  activeMatrixAuthorityReady: boolean;
  confirmedFeeLatest: ProjectRuntimeConsoleModel["confirmedFeeLatest"];
  creatingFolder: boolean;
  effectiveFolderReady: boolean;
  officialWorkspaceStatus: NonNullable<ProjectRuntimeConsoleModel["officialWorkspacePreview"]>["status"] | null | undefined;
  projectFolderBlocker?: string | null;
}): {
  disabled: boolean;
  disabledReason?: string;
  label: string;
} {
  const hasCurrentFeeAuthority = confirmedFeeLatest?.status === "current";
  const label =
    effectiveFolderReady || officialWorkspaceStatus === "completed"
      ? "Update project folder"
      : "Generate project folder";
  if (creatingFolder) {
    return {
      disabled: true,
      disabledReason: "Generating project folder...",
      label: "Generating...",
    };
  }
  if (!activeMatrixAuthorityReady) {
    return {
      disabled: true,
      disabledReason: "Confirm Matrix before generating the project folder.",
      label,
    };
  }
  if (!hasCurrentFeeAuthority) {
    return {
      disabled: true,
      disabledReason: "Update Fee before generating the project folder.",
      label,
    };
  }
  if (
    (effectiveFolderReady || officialWorkspaceStatus === "completed") &&
    projectFolderBlocker
  ) {
    return {
      disabled: true,
      disabledReason: projectFolderBlocker,
      label,
    };
  }
  return {
    disabled: false,
    label,
  };
}
