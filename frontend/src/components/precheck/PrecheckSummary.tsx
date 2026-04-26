import type { ReactElement } from "react";
import type { PrecheckResult } from "../../api/client";

type PrecheckSummaryProps = {
  precheck: PrecheckResult | null;
};

function countIssues(precheck: PrecheckResult | null, level: string): number {
  return precheck?.issues.filter((issue) => !issue.resolved && issue.level === level).length ?? 0;
}

export function PrecheckSummary({ precheck }: PrecheckSummaryProps): ReactElement {
  const openIssues = precheck?.issues.filter((issue) => !issue.resolved).length ?? 0;
  const resolvedIssues = precheck?.issues.filter((issue) => issue.resolved).length ?? 0;

  return (
    <div className="precheck-summary">
      <div>
        <span>{precheck?.status ?? "not run"}</span>
        <strong>Precheck status</strong>
      </div>
      <div>
        <span>{countIssues(precheck, "error")}</span>
        <strong>Errors</strong>
      </div>
      <div>
        <span>{countIssues(precheck, "warning")}</span>
        <strong>Warnings</strong>
      </div>
      <div>
        <span>{openIssues}</span>
        <strong>Open issues</strong>
      </div>
      <div>
        <span>{resolvedIssues}</span>
        <strong>Resolved</strong>
      </div>
    </div>
  );
}
