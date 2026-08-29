import type { ReactElement } from "react";
import { ReportWorkspace } from "../features/report-workspace/ReportWorkspace";
import "../workbench.css";

type ProjectReportWorkspacePageProps = {
  projectId: string;
  onBackToWorkbench: () => void;
};

export function ProjectReportWorkspacePage({
  projectId,
  onBackToWorkbench,
}: ProjectReportWorkspacePageProps): ReactElement {
  return <ReportWorkspace onBack={onBackToWorkbench} projectId={projectId} />;
}
