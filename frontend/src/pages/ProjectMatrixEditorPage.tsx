import type { ReactElement } from "react";
import { MatrixEditorWorkspace } from "../features/matrix-editor/MatrixEditorWorkspace";

type ProjectMatrixEditorPageProps = {
  projectId: string;
  onBackToWorkbench: () => void;
};

export function ProjectMatrixEditorPage({
  projectId,
  onBackToWorkbench,
}: ProjectMatrixEditorPageProps): ReactElement {
  return (
    <MatrixEditorWorkspace
      projectId={projectId}
      onBackToWorkbench={onBackToWorkbench}
    />
  );
}

