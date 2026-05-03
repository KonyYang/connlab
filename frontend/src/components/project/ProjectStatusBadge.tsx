import type { ReactElement } from "react";

type ProjectStatusBadgeProps = {
  status: string;
};

const STATUS_LABELS: Record<string, string> = {
  draft: "Draft",
  intake_received: "Pending LTR Number",
  confirmed: "Pending LTR Number",
  precheck_pending: "Precheck pending",
  precheck_passed: "Precheck passed",
  precheck_failed: "Precheck failed",
  ltr_registered: "LTR Number registered",
  folder_created: "Folder created"
};

function statusTone(status: string): string {
  if (status.includes("failed") || status.includes("blocked")) {
    return "danger";
  }
  if (status.includes("folder") || status.includes("passed")) {
    return "success";
  }
  if (status.includes("ltr") || status.includes("precheck")) {
    return "ready";
  }
  return "neutral";
}

export function ProjectStatusBadge({ status }: ProjectStatusBadgeProps): ReactElement {
  const normalized = status.trim().toLowerCase();
  const label = STATUS_LABELS[normalized] ?? status.replaceAll("_", " ");

  return (
    <span className={`status-badge status-badge-${statusTone(normalized)}`}>
      {label}
    </span>
  );
}
