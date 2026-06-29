import type {
  ProjectLifecycleReadonlyErrorDetail,
  ProjectLifecycleResponse,
} from "../../api/client";

export type ProjectLifecycleReadonlyMode =
  | "active"
  | "stopped_readonly"
  | "closed_readonly";

export type ProjectLifecycleReadonlyView = {
  mode: ProjectLifecycleReadonlyMode;
  readonly: boolean;
  title: string;
  message: string;
  allowedActions: string[];
  canResume: boolean;
  canClose: boolean;
  canWriteBusinessData: boolean;
  canUseReadonlyPreview: boolean;
};

const ACTIVE_VIEW: ProjectLifecycleReadonlyView = {
  mode: "active",
  readonly: false,
  title: "Project active",
  message: "",
  allowedActions: [],
  canResume: false,
  canClose: true,
  canWriteBusinessData: true,
  canUseReadonlyPreview: true,
};

export function deriveProjectLifecycleReadonlyView(
  lifecycle: ProjectLifecycleResponse | null
): ProjectLifecycleReadonlyView {
  if (!lifecycle || lifecycle.lifecycle_state === "active") {
    return ACTIVE_VIEW;
  }
  if (lifecycle.lifecycle_state === "stopped") {
    return {
      mode: "stopped_readonly",
      readonly: true,
      title: "Project stopped",
      message:
        "This project is stopped. Activate it before making changes. Review and preview actions remain available.",
      allowedActions: lifecycle.allowed_actions,
      canResume: false,
      canClose: lifecycle.allowed_actions.includes("close"),
      canWriteBusinessData: false,
      canUseReadonlyPreview: true,
    };
  }
  if (lifecycle.close_reason_category === "completed" || lifecycle.closure_type === "completed") {
    return closedView(
      "closed_readonly",
      "Project closed: Completed",
      "This project is closed with reason Completed. Activate it before making changes.",
      lifecycle.allowed_actions
    );
  }
  if (lifecycle.close_reason_label) {
    return closedView(
      "closed_readonly",
      `Project closed: ${lifecycle.close_reason_label}`,
      "This project is closed. Activate it before making changes.",
      lifecycle.allowed_actions
    );
  }
  return closedView(
    "closed_readonly",
    "Project closed",
    "This project is closed. Activate it before making changes.",
    lifecycle.allowed_actions
  );
}

export function deriveReadonlyApiErrorMessage(
  detail: ProjectLifecycleReadonlyErrorDetail
): string {
  if (detail.lifecycle_state === "stopped") {
    return "This project is stopped. Activate it before making changes.";
  }
  if (detail.lifecycle_state === "closed") {
    return "This project is closed. Activate it before making changes.";
  }
  return detail.message.replace("readonly", "read-only");
}

function closedView(
  mode: ProjectLifecycleReadonlyMode,
  title: string,
  message: string,
  allowedActions: string[]
): ProjectLifecycleReadonlyView {
  return {
    mode,
    readonly: true,
    title,
    message,
    allowedActions,
    canResume: false,
    canClose: false,
    canWriteBusinessData: false,
    canUseReadonlyPreview: true,
  };
}
