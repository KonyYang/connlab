import type { ReactElement } from "react";
import type { PrecheckIssue } from "../../api/client";
import { IssueSeverityBadge } from "./IssueSeverityBadge";

type PrecheckIssueCardProps = {
  issue: PrecheckIssue;
  onResolve: (issueId: string) => void;
};

function displayName(value?: string | null): string {
  if (!value) {
    return "General review";
  }
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function issueTitle(issue: PrecheckIssue): string {
  const target = displayName(issue.field_name || issue.category);
  return issue.resolved ? `${target} resolved` : `${target} needs review`;
}

function expectedValue(issue: PrecheckIssue): string {
  const message = issue.message.toLowerCase();
  if (message.includes("empty") || message.includes("missing") || message.includes("required")) {
    return "A completed value in the submitted application form.";
  }
  if (message.includes("see attachment")) {
    return "A specific testing request or a registered supporting attachment.";
  }
  if (message.includes("too vague")) {
    return "A clear test request that the lab can act on.";
  }
  return "A value that matches the application form requirement.";
}

function suggestedAction(issue: PrecheckIssue): string {
  if (issue.resolved) {
    return "No further action is needed for this issue.";
  }
  if (issue.field_name) {
    return `Review and correct the ${displayName(issue.field_name)} field, then rerun precheck if needed.`;
  }
  return "Review the application form section, update the source information, then rerun precheck if needed.";
}

export function PrecheckIssueCard({
  issue,
  onResolve
}: PrecheckIssueCardProps): ReactElement {
  return (
    <article className={`precheck-issue-card ${issue.resolved ? "precheck-issue-resolved" : ""}`}>
      <div className="precheck-issue-heading">
        <div>
          <h4>{issueTitle(issue)}</h4>
          <p>{displayName(issue.category)}</p>
        </div>
        <IssueSeverityBadge resolved={issue.resolved} severity={issue.level} />
      </div>

      <dl className="precheck-issue-details">
        <div>
          <dt>Field or category</dt>
          <dd>{displayName(issue.field_name || issue.category)}</dd>
        </div>
        <div>
          <dt>What is wrong</dt>
          <dd>{issue.message}</dd>
        </div>
        <div>
          <dt>Expected value</dt>
          <dd>{expectedValue(issue)}</dd>
        </div>
        <div>
          <dt>Suggested action</dt>
          <dd>{suggestedAction(issue)}</dd>
        </div>
      </dl>

      {!issue.resolved && (
        <button className="row-action" type="button" onClick={() => onResolve(issue.issue_id)}>
          Mark reviewed
        </button>
      )}
    </article>
  );
}
