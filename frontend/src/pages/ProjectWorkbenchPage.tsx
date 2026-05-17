import type { ReactElement } from "react";
import { ErrorMessage } from "../components/common/ErrorMessage";
import { LoadingState } from "../components/common/LoadingState";
import { ProjectWorkbenchLayout } from "../features/project-workbench/ProjectWorkbenchLayout";
import { useProjectWorkbenchModel } from "../features/project-workbench/useProjectWorkbenchModel";
import "../workbench.css";

type ProjectWorkbenchPageProps = {
  projectId: string;
  onBack: () => void;
  onOpenMatrixEditor: () => void;
};

export function ProjectWorkbenchPage({
  projectId,
  onBack,
  onOpenMatrixEditor
}: ProjectWorkbenchPageProps): ReactElement {
  const model = useProjectWorkbenchModel(projectId);

  if (!model.project && !model.error) {
    return <LoadingState label="Loading project workbench..." />;
  }

  return (
    <section className="workbench-page">
      {model.error && <ErrorMessage message={model.error} />}
      {model.message && <p className="success">{model.message}</p>}
      {model.project && (
        <ProjectWorkbenchLayout
          model={model}
          onBack={onBack}
          onOpenMatrixEditor={onOpenMatrixEditor}
          project={model.project}
        />
      )}
    </section>
  );
}
