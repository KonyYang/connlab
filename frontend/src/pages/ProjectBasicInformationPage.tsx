import type { ReactElement } from "react";
import {
  ProjectBasicInformationWorkspace,
} from "../features/project-basic-information/ProjectBasicInformationWorkspace";
import type { BackToWorkbenchOptions } from "../features/project-basic-information/useProjectBasicInformationModel";
import "../workbench.css";

type ProjectBasicInformationPageProps = {
  projectId: string;
  onBackToWorkbench: (options: BackToWorkbenchOptions) => void;
};

export function ProjectBasicInformationPage({
  projectId,
  onBackToWorkbench,
}: ProjectBasicInformationPageProps): ReactElement {
  return (
    <ProjectBasicInformationWorkspace
      projectId={projectId}
      onBackToWorkbench={onBackToWorkbench}
    />
  );
}
