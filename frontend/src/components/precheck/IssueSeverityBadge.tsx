import type { ReactElement } from "react";

type IssueSeverityBadgeProps = {
  resolved: boolean;
  severity: string;
};

function labelFor(severity: string, resolved: boolean): string {
  if (resolved) {
    return "Resolved";
  }
  if (severity.toLowerCase() === "error") {
    return "Error";
  }
  if (severity.toLowerCase() === "warning") {
    return "Warning";
  }
  return severity || "Review";
}

export function IssueSeverityBadge({
  resolved,
  severity
}: IssueSeverityBadgeProps): ReactElement {
  const normalized = resolved ? "resolved" : severity.toLowerCase() || "review";

  return (
    <span className={`issue-severity issue-severity-${normalized}`}>
      {labelFor(severity, resolved)}
    </span>
  );
}
