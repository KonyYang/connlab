import type { ReactElement } from "react";
import { FeeEvaluationReviewExportPage } from "../features/fee-evaluation/FeeEvaluationReviewExportPage";
import "../workbench.css";

type ProjectFeeEvaluationPageProps = {
  projectId: string;
  onBackToWorkbench: () => void;
};

export function ProjectFeeEvaluationPage({
  projectId,
  onBackToWorkbench,
}: ProjectFeeEvaluationPageProps): ReactElement {
  return (
    <FeeEvaluationReviewExportPage
      projectId={projectId}
      onBackToWorkbench={onBackToWorkbench}
    />
  );
}
