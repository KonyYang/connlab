import { useEffect, useState, type ReactElement } from "react";
import { getProject, getProjectBasicInformation, listProjectLtrs } from "../api/client";
import { buildProjectIdentityLine } from "../features/projectIdentity";
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
  const [identity, setIdentity] = useState<{ projectId: string; label: string } | null>(null);

  useEffect(() => {
    let active = true;
    // Labels must not block report operations when an optional context lookup is unavailable.
    void Promise.allSettled([
      getProject(projectId),
      listProjectLtrs(projectId),
      getProjectBasicInformation(projectId),
    ]).then(([projectResult, ltrResult, basicResult]) => {
      if (!active) return;
      const project = projectResult.status === "fulfilled" ? projectResult.value : null;
      const latestLtr = ltrResult.status === "fulfilled" ? ltrResult.value.at(-1)?.ltr_number : null;
      const confirmed = basicResult.status === "fulfilled" ? basicResult.value.latest_confirmed?.values : null;
      const product = confirmed?.product_description?.trim();
      const testItem = confirmed?.test_item?.trim();
      const label = buildProjectIdentityLine({
        project: project ? {
          ...project,
          sample_description: product || project.sample_description,
          test_item: testItem || project.test_item,
        } : null,
        latestLtr,
        projectId,
        productFallback: product,
        testItemFallback: testItem,
      });
      setIdentity({ projectId, label });
    });
    return () => { active = false; };
  }, [projectId]);

  return <ReportWorkspace
    identityLabel={identity?.projectId === projectId ? identity.label : "Connector Project"}
    onBack={onBackToWorkbench}
    projectId={projectId}
  />;
}
