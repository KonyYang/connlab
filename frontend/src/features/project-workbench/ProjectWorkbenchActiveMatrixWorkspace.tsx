import type { ReactElement } from "react";
import { ProjectBasicInformationSummaryCard } from "../project-basic-information/ProjectBasicInformationSummaryCard";
import { ProjectWorkbenchExecutionConsole } from "./ProjectWorkbenchExecutionConsole";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";
import type { ProjectLifecycleReadonlyView } from "../project-lifecycle/projectLifecycleReadonlyModel";
import type { PublicFolderWorkflowOperationType } from "../../api/client";
import type {
  ProjectFolderTaskActionTarget,
  ProjectFolderTaskRow,
} from "./projectFolderTaskSelectors";
import {
  ProjectFolderActionsSurface,
  type ProjectFolderHeaderAction,
} from "./ProjectFolderTaskList";
import { ProjectFileEncryptionAction } from "./ProjectFileEncryptionAction";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

type ProjectWorkbenchActiveMatrixWorkspaceProps = {
  effectiveFolderReady: boolean;
  officialWorkspaceStatus: NonNullable<ProjectRuntimeConsoleModel["officialWorkspacePreview"]>["status"] | null | undefined;
  onProjectFolderTaskAction: (actionTarget: ProjectFolderTaskActionTarget) => void;
  onProjectFolderTaskConfirm: (operation: PublicFolderWorkflowOperationType) => void;
  onProjectFolderTaskCancel: (operation: PublicFolderWorkflowOperationType) => void;
  onPublicFolderAutoSyncChange: (enabled: boolean) => void;
  projectFolderTasks: ProjectFolderTaskRow[];
  projectFolderHeaderAction: ProjectFolderHeaderAction;
  projectId: string;
  registeredLtrNumber: string | null;
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
  onProjectFolderTaskConfirm,
  onProjectFolderTaskCancel,
  onPublicFolderAutoSyncChange,
  projectFolderTasks,
  projectFolderHeaderAction,
  projectId,
  registeredLtrNumber,
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
                headerAction={projectFolderHeaderAction}
                onTaskAction={onProjectFolderTaskAction}
                onTaskConfirm={onProjectFolderTaskConfirm}
                onTaskCancel={onProjectFolderTaskCancel}
                onAutoSyncChange={onPublicFolderAutoSyncChange}
                readonlyReason={
                  lifecycleReadonlyView.readonly ? lifecycleReadonlyView.message : undefined
                }
                footerAction={
                  effectiveFolderReady ? (
                    <ProjectFileEncryptionAction
                      projectId={projectId}
                      available
                      readonlyReason={
                        lifecycleReadonlyView.readonly ? lifecycleReadonlyView.message : undefined
                      }
                    />
                  ) : null
                }
              />
              <ProjectBasicInformationSummaryCard
                projectId={projectId}
                basicInformation={basicInformation}
                registeredLtrNumber={registeredLtrNumber}
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
    task.key === "project_folder" && task.actionTarget !== "project_folder_open"
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
  projectFolderBlocker,
}: {
  activeMatrixAuthorityReady: boolean;
  confirmedFeeLatest: ProjectRuntimeConsoleModel["confirmedFeeLatest"];
  creatingFolder: boolean;
  projectFolderBlocker?: string | null;
}): {
  disabled: boolean;
  disabledReason?: string;
} {
  const hasCurrentFeeAuthority = confirmedFeeLatest?.status === "current";
  if (creatingFolder) {
    return {
      disabled: true,
      disabledReason: "Generating project folder...",
    };
  }
  if (!activeMatrixAuthorityReady) {
    return {
      disabled: true,
      disabledReason: "Confirm Matrix before generating the project folder.",
    };
  }
  if (!hasCurrentFeeAuthority) {
    return {
      disabled: true,
      disabledReason: "Update Fee before generating the project folder.",
    };
  }
  if (projectFolderBlocker) {
    return {
      disabled: true,
      disabledReason: projectFolderBlocker,
    };
  }
  return {
    disabled: false,
  };
}
