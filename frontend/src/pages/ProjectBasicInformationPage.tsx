import type { ReactElement } from "react";
import {
  ProjectBasicInformationWorkspace,
} from "../features/project-basic-information/ProjectBasicInformationWorkspace";
import type { BackToWorkbenchOptions } from "../features/project-basic-information/useProjectBasicInformationModel";
import type { ProjectBasicInformationInitialValuesMode } from "../features/project-basic-information/useProjectBasicInformationModel";
import "../workbench.css";

type ProjectBasicInformationPageProps = {
  projectId: string;
  initialValuesMode?: ProjectBasicInformationInitialValuesMode;
  onBackToWorkbench: (options: BackToWorkbenchOptions) => void;
};

export function ProjectBasicInformationPage({
  projectId,
  initialValuesMode = "draft",
  onBackToWorkbench,
}: ProjectBasicInformationPageProps): ReactElement {
  return (
    <ProjectBasicInformationWorkspace
      projectId={projectId}
      initialValuesMode={initialValuesMode}
      onBackToWorkbench={onBackToWorkbench}
    />
  );
}
