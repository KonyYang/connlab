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
  onBrowseProjectFiles?: (memberId: string) => void;
};

export function ProjectWorkbenchPage({
  projectId,
  onBack,
  onOpenMatrixEditor,
  onOpenFeeEvaluation,
  onOpenBasicInformation,
  onOpenReportWorkspace,
  onOpenSettings,
  onBrowseProjectFiles
}: ProjectWorkbenchPageProps): ReactElement {
  const model = useProjectWorkbenchModel(projectId);
  const runtimeModel = selectProjectRuntimeConsoleModel(model);

  if (!model.project && !model.error) {
    return <section className="workbench-page" aria-busy="true" />;
  }

  return (
    <section className="workbench-page">
      {model.error && <ErrorMessage message={model.error} />}
      {model.project && <>
        {model.project.library_member_id && onBrowseProjectFiles && <aside className="runtime-console-workflow-alert" aria-label="Project files and setup">
          <strong>Project files</strong>
          {model.basicInformationLoading || model.activeConfirmedMatrixLoading ? <span>Checking project setup…</span> : <>
            {model.basicInformation?.status !== "confirmed" && <span>Review Basic Information before testing.</span>}
            {!model.activeConfirmedMatrixSnapshot && <span>No confirmed Matrix. Review or create the Matrix before testing.</span>}
          </>}
          <button type="button" onClick={() => onBrowseProjectFiles(model.project!.library_member_id!)}>Browse Files</button>
        </aside>}
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
      </>}
    </section>
  );
}
