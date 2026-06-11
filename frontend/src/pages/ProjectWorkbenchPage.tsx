import type { ReactElement } from "react";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { ProjectWorkbenchLayout } from "../features/project-workbench/ProjectWorkbenchLayout";
import { useProjectWorkbenchModel } from "../features/project-workbench/useProjectWorkbenchModel";
import { selectProjectRuntimeConsoleModel } from "../features/project-workbench/useProjectRuntimeConsoleModel";
import "../workbench.css";

type ProjectWorkbenchPageProps = {
  projectId: string;
  onBack: () => void;
  onOpenMatrixEditor: () => void;
  onOpenFeeEvaluation: () => void;
  onOpenSettings: () => void;
};

export function ProjectWorkbenchPage({
  projectId,
  onBack,
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
  onOpenSettings
}: ProjectWorkbenchPageProps): ReactElement {
  const model = useProjectWorkbenchModel(projectId);
  const runtimeModel = selectProjectRuntimeConsoleModel(model);

  if (!model.project && !model.error) {
    return <LoadingState label="Loading project workbench..." />;
  }

  return (
    <section className="workbench-page">
      {model.error && <ErrorMessage message={model.error} />}
      {model.message && <p className="success">{model.message}</p>}
      {model.project && (
        <ProjectWorkbenchLayout
          runtimeModel={runtimeModel}
          onBack={onBack}
          onOpenMatrixEditor={onOpenMatrixEditor}
          onOpenFeeEvaluation={onOpenFeeEvaluation}
          onOpenSettings={onOpenSettings}
          project={model.project}
        />
      )}
    </section>
  );
}
