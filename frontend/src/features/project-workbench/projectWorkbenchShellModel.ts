import type { ProjectLifecycleResponse } from "../../api/client";
import type { ProjectLifecycleReadonlyView } from "../project-lifecycle/projectLifecycleReadonlyModel";

export type ProjectWorkbenchShellPrimaryWorkspace =
  | "temporary_planning"
  | "matrix_setup"
  | "active_matrix"
  | "readonly_archive";

export type ProjectWorkbenchShellStatus =
  | "ready"
  | "warning"
  | "blocked"
  | "neutral";

export type ProjectWorkbenchShellOutputEntry = {
  key:
    | "basic_information"
    | "project_folder"
    | "required_forms"
    | "fee_evaluation"
    | "ltr_public_drive";
  label: string;
  status: ProjectWorkbenchShellStatus;
  statusLabel: string;
  summary: string;
};

export type ProjectWorkbenchShellHistoryEntry = {
  label: string;
  value: string;
};

export type ProjectWorkbenchShellModelInput = {
  projectIdentity: string;
  hasRegisteredProject: boolean;
  latestLtr: string | null;
  hasActiveMatrix: boolean;
  hasCandidateMatrix: boolean;
  folderReady: boolean;
  basicInformationStatus: "confirmed" | "draft" | "missing" | "unknown";
  packageStatus: string | null;
  requiredFormsStatus: string | null;
  confirmedFeeStatus: string | null;
  publicDriveStatus: string | null;
  lifecycle: ProjectLifecycleResponse | null;
  lifecycleReadonlyView: ProjectLifecycleReadonlyView;
};

export type ProjectWorkbenchShellModel = {
  projectIdentity: string;
  lifecycleLabel: string;
  formalIdentityLabel: string;
  matrixAuthorityLabel: string;
  timestampLine: string | null;
  reasonLine: string | null;
  readonly: boolean;
  bannerTitle: string;
  bannerMessage: string;
  primaryWorkspace: ProjectWorkbenchShellPrimaryWorkspace;
  primaryWorkspaceLabel: string;
  primaryWorkspaceSummary: string;
  primaryActionLabel: string;
  allowedLifecycleActions: string[];
  outputEntries: ProjectWorkbenchShellOutputEntry[];
  historyEntries: ProjectWorkbenchShellHistoryEntry[];
};

export function deriveProjectWorkbenchShellModel(
  input: ProjectWorkbenchShellModelInput
): ProjectWorkbenchShellModel {
  const primaryWorkspace = derivePrimaryWorkspace(input);
  return {
    projectIdentity: input.projectIdentity,
    lifecycleLabel: deriveLifecycleLabel(input.lifecycle, input.lifecycleReadonlyView),
    formalIdentityLabel: input.hasRegisteredProject
      ? "Registered project"
      : "Temporary planning",
    matrixAuthorityLabel: deriveMatrixAuthorityLabel(input),
    timestampLine: deriveTimestampLine(input.lifecycle),
    reasonLine: deriveReasonLine(input.lifecycle),
    readonly: input.lifecycleReadonlyView.readonly,
    bannerTitle: input.lifecycleReadonlyView.readonly
      ? input.lifecycleReadonlyView.title
      : "Project active",
    bannerMessage: input.lifecycleReadonlyView.readonly
      ? input.lifecycleReadonlyView.message
      : "Continue from the current Matrix authority and supporting output status.",
    primaryWorkspace,
    primaryWorkspaceLabel: derivePrimaryWorkspaceLabel(primaryWorkspace),
    primaryWorkspaceSummary: derivePrimaryWorkspaceSummary(primaryWorkspace, input),
    primaryActionLabel: input.lifecycleReadonlyView.readonly
      ? input.lifecycle?.lifecycle_state === "closed"
        ? "Read-only archive"
        : "Read-only project"
      : derivePrimaryActionLabel(primaryWorkspace),
    allowedLifecycleActions: input.lifecycleReadonlyView.readonly
      ? []
      : ["stop", "close"],
    outputEntries: deriveOutputEntries(input),
    historyEntries: deriveHistoryEntries(input),
  };
}

function deriveLifecycleLabel(
  lifecycle: ProjectLifecycleResponse | null,
  readonlyView: ProjectLifecycleReadonlyView
): string {
  if (!lifecycle || lifecycle.lifecycle_state === "active") {
    return "Active";
  }
  if (lifecycle.lifecycle_state === "stopped") {
    return "Stopped";
  }
  if (readonlyView.mode === "closed_completed_readonly") {
    return "Closed: Completed";
  }
  if (readonlyView.mode === "closed_administrative_readonly") {
    return "Closed: Administrative";
  }
  return "Closed";
}

function deriveMatrixAuthorityLabel(input: ProjectWorkbenchShellModelInput): string {
  if (input.hasActiveMatrix) {
    return "Active Matrix";
  }
  if (input.hasCandidateMatrix) {
    return "Candidate Matrix";
  }
  return "No Matrix";
}

function derivePrimaryWorkspace(
  input: ProjectWorkbenchShellModelInput
): ProjectWorkbenchShellPrimaryWorkspace {
  if (input.lifecycle?.lifecycle_state === "closed") {
    return "readonly_archive";
  }
  if (input.hasActiveMatrix) {
    return "active_matrix";
  }
  if (!input.hasRegisteredProject) {
    return "temporary_planning";
  }
  return "matrix_setup";
}

function derivePrimaryWorkspaceLabel(
  workspace: ProjectWorkbenchShellPrimaryWorkspace
): string {
  if (workspace === "active_matrix") {
    return "Active Matrix workspace";
  }
  if (workspace === "matrix_setup") {
    return "Matrix authority setup";
  }
  if (workspace === "readonly_archive") {
    return "Read-only archive";
  }
  return "Temporary planning";
}

function derivePrimaryWorkspaceSummary(
  workspace: ProjectWorkbenchShellPrimaryWorkspace,
  input: ProjectWorkbenchShellModelInput
): string {
  if (workspace === "active_matrix") {
    return input.lifecycleReadonlyView.readonly
      ? "Matrix remains visible for review; lifecycle state prevents editing."
      : "Use the active Matrix as the authority map for current lab work.";
  }
  if (workspace === "matrix_setup") {
    return input.lifecycleReadonlyView.readonly
      ? "Matrix setup context remains visible for review."
      : "Register or confirm the Matrix authority before downstream outputs.";
  }
  if (workspace === "readonly_archive") {
    return "This project is archived for review from current stored data.";
  }
  return "Shape Matrix and fee planning before formal LTR registration.";
}

function derivePrimaryActionLabel(
  workspace: ProjectWorkbenchShellPrimaryWorkspace
): string {
  if (workspace === "active_matrix") {
    return "Work from Matrix";
  }
  if (workspace === "matrix_setup") {
    return "Confirm Matrix authority";
  }
  if (workspace === "readonly_archive") {
    return "Read-only archive";
  }
  return "Plan Matrix";
}

function deriveTimestampLine(lifecycle: ProjectLifecycleResponse | null): string | null {
  if (!lifecycle) {
    return null;
  }
  if (lifecycle.closed_at) {
    return `Closed: ${lifecycle.closed_at}`;
  }
  if (lifecycle.stopped_at) {
    return `Stopped: ${lifecycle.stopped_at}`;
  }
  return null;
}

function deriveReasonLine(lifecycle: ProjectLifecycleResponse | null): string | null {
  const reason = lifecycle?.closed_reason ?? lifecycle?.stopped_reason;
  return reason ? `Reason: ${reason}` : null;
}

function deriveOutputEntries(
  input: ProjectWorkbenchShellModelInput
): ProjectWorkbenchShellOutputEntry[] {
  return [
    {
      key: "basic_information",
      label: "Basic Information",
      ...deriveBasicInformationOutput(input.basicInformationStatus),
    },
    {
      key: "project_folder",
      label: "Project Folder",
      status: input.folderReady ? "ready" : statusFromPreview(input.packageStatus),
      statusLabel: input.folderReady ? "Ready" : labelFromPreview(input.packageStatus),
      summary: input.folderReady
        ? "Local project folder is available."
        : "Folder status follows the current package preview.",
    },
    {
      key: "required_forms",
      label: "Required Forms",
      status: statusFromPreview(input.requiredFormsStatus),
      statusLabel: labelFromPreview(input.requiredFormsStatus),
      summary: "Required form generation follows current output readiness.",
    },
    {
      key: "fee_evaluation",
      label: "Fee Evaluation",
      status: input.confirmedFeeStatus === "current" ? "ready" : "warning",
      statusLabel:
        input.confirmedFeeStatus === "current"
          ? "Current"
          : labelFromPreview(input.confirmedFeeStatus),
      summary: "Fee status is derived from the current confirmed Fee authority.",
    },
    {
      key: "ltr_public_drive",
      label: "LTR/Public Drive",
      status: input.latestLtr ? statusFromPreview(input.publicDriveStatus) : "neutral",
      statusLabel: input.latestLtr
        ? labelFromPreview(input.publicDriveStatus)
        : "Not registered",
      summary: input.latestLtr
        ? "LTR identity is available for current read and preview surfaces."
        : "LTR registration has not been assigned yet.",
    },
  ];
}

function deriveBasicInformationOutput(
  status: ProjectWorkbenchShellModelInput["basicInformationStatus"]
): Omit<ProjectWorkbenchShellOutputEntry, "key" | "label"> {
  if (status === "confirmed") {
    return {
      status: "ready",
      statusLabel: "Confirmed",
      summary: "Confirmed Basic Information is available.",
    };
  }
  if (status === "draft") {
    return {
      status: "warning",
      statusLabel: "Draft",
      summary: "Basic Information still needs confirmation.",
    };
  }
  return {
    status: "neutral",
    statusLabel: "Missing",
    summary: "Basic Information is not confirmed yet.",
  };
}

function statusFromPreview(value: string | null): ProjectWorkbenchShellStatus {
  if (value === "ready" || value === "completed" || value === "current") {
    return "ready";
  }
  if (value === "blocked" || value === "missing") {
    return "blocked";
  }
  if (value === "warning" || value === "stale" || value === "exists") {
    return "warning";
  }
  return "neutral";
}

function labelFromPreview(value: string | null): string {
  if (!value) {
    return "Not checked";
  }
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function deriveHistoryEntries(
  input: ProjectWorkbenchShellModelInput
): ProjectWorkbenchShellHistoryEntry[] {
  return [
    input.lifecycle?.closed_at
      ? { label: "Lifecycle timestamp", value: input.lifecycle.closed_at }
      : null,
    input.lifecycle?.stopped_at
      ? { label: "Lifecycle timestamp", value: input.lifecycle.stopped_at }
      : null,
    input.lifecycle?.closed_reason
      ? { label: "Lifecycle reason", value: input.lifecycle.closed_reason }
      : null,
    input.lifecycle?.stopped_reason
      ? { label: "Lifecycle reason", value: input.lifecycle.stopped_reason }
      : null,
    input.hasActiveMatrix
      ? { label: "Matrix authority", value: "Active Matrix is the current authority." }
      : null,
  ].filter((entry): entry is ProjectWorkbenchShellHistoryEntry => Boolean(entry));
}
