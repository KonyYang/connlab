import type { ReactElement } from "react";
import { ProjectBasicInformationSummaryCard } from "../project-basic-information/ProjectBasicInformationSummaryCard";
import { ProjectWorkbenchExecutionConsole } from "./ProjectWorkbenchExecutionConsole";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import type { ProjectLifecycleReadonlyView } from "../project-lifecycle/projectLifecycleReadonlyModel";
import type {
  ProjectFolderTaskActionTarget,
  ProjectFolderTaskRow,
} from "./projectFolderTaskSelectors";
import { ProjectFolderActionsSurface } from "./ProjectFolderTaskList";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

type ProjectWorkbenchActiveMatrixWorkspaceProps = {
  effectiveFolderReady: boolean;
  officialWorkspaceStatus: NonNullable<ProjectRuntimeConsoleModel["officialWorkspacePreview"]>["status"] | null | undefined;
  onProjectFolderTaskAction: (actionTarget: ProjectFolderTaskActionTarget) => void;
  projectFolderTasks: ProjectFolderTaskRow[];
  projectId: string;
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
              <ProjectFolderActionsSurface
                tasks={visibleProjectFolderTasks}
                onTaskAction={onProjectFolderTaskAction}
                readonlyReason={
                  lifecycleReadonlyView.readonly ? lifecycleReadonlyView.message : undefined
                }
              />
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
    task.key === "project_folder"
      ? {
          ...task,
          actionLabel: undefined,
          actionTarget: undefined,
          summary:
            "Project folder access is unavailable until the template and target path are ready.",
        }
      : task
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
      : "Create project folder";
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
