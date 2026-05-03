import type { ReactElement } from "react";

import type { DraftPrecheckIssue } from "../../api/client";
import { UiIcon } from "../../components/common/UiIcon";

export function PrecheckIssueSummary({
  issues
}: {
  issues: DraftPrecheckIssue[];
}): ReactElement {
  const errors = issues.filter((issue) => issue.level === "error");
  const warnings = issues.filter((issue) => issue.level === "warning");
  if (issues.length === 0) {
    return <div className="precheck-issue-summary precheck-issue-summary-pass"><UiIcon name="help" /><strong>SECTION 1 precheck passed.</strong><span>No Project creation blockers detected.</span></div>;
  }
  return (
    <div className="precheck-issue-summary">
      <UiIcon name="help" />
      <div>
        <strong>{errors.length} blocker{errors.length === 1 ? "" : "s"} and {warnings.length} warning{warnings.length === 1 ? "" : "s"} before Project creation</strong>
        <span>Lab Test Request Number must be blank. SECTION 2 lab fields are excluded from this pre-project check.</span>
        <ul>
          {issues.slice(0, 6).map((issue) => (
            <li className={`precheck-issue-${issue.level}`} key={`${issue.field_key}-${issue.message}`}>{issue.message}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
