import type { ReactElement } from "react";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { ProjectWorkbenchLayout } from "../features/project-workbench/ProjectWorkbenchLayout";
import { useProjectWorkbenchModel } from "../features/project-workbench/useProjectWorkbenchModel";
import { selectProjectRuntimeConsoleModel } from "../features/project-workbench/useProjectRuntimeConsoleModel";
import "../workbench.css";

type ProjectWorkbenchPageProps = {
  projectId: string;
  onBack: () => void;
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
  onOpenBasicInformation: () => void;
  onOpenReportWorkspace: () => void;
  onOpenSettings: () => void;
};

export function ProjectWorkbenchPage({
  projectId,
  onBack,
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
  onOpenBasicInformation,
  onOpenReportWorkspace,
  onOpenSettings
}: ProjectWorkbenchPageProps): ReactElement {
  const model = useProjectWorkbenchModel(projectId);
  const runtimeModel = selectProjectRuntimeConsoleModel(model);

  if (!model.project && !model.error) {
    return <section className="workbench-page" aria-busy="true" />;
  }

  return (
    <section className="workbench-page">
      {model.error && <ErrorMessage message={model.error} />}
      {model.project && (
        <ProjectWorkbenchLayout
          runtimeModel={runtimeModel}
          onBack={onBack}
          onOpenMatrixEditor={onOpenMatrixEditor}
          onOpenFeeEvaluation={onOpenFeeEvaluation}
          onOpenBasicInformation={onOpenBasicInformation}
          onOpenReportWorkspace={onOpenReportWorkspace}
          onOpenSettings={onOpenSettings}
          project={model.project}
        />
      )}
    </section>
  );
}
