import type {
  ProjectLifecycleReadonlyErrorDetail,
  ProjectLifecycleResponse,
} from "../../api/client";

export type ProjectLifecycleReadonlyMode =
  | "active"
  | "stopped_readonly"
  | "closed_completed_readonly"
  | "closed_administrative_readonly"
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
        "This project is paused. Review and preview actions remain available; editing resumes after the project is resumed.",
      allowedActions: lifecycle.allowed_actions,
      canResume: lifecycle.allowed_actions.includes("resume"),
      canClose: lifecycle.allowed_actions.includes("close"),
      canWriteBusinessData: false,
      canUseReadonlyPreview: true,
    };
  }
  if (lifecycle.closure_type === "completed") {
    return closedView(
      "closed_completed_readonly",
      "Project closed as completed",
      "This project is archived as completed. Project data is read-only.",
      lifecycle.allowed_actions
    );
  }
  if (lifecycle.closure_type === "administrative") {
    return closedView(
      "closed_administrative_readonly",
      "Project closed administratively",
      "This project is archived administratively. Project data is read-only.",
      lifecycle.allowed_actions
    );
  }
  return closedView(
    "closed_readonly",
    "Project closed",
    "This project is archived. Project data is read-only.",
    lifecycle.allowed_actions
  );
}

export function deriveReadonlyApiErrorMessage(
  detail: ProjectLifecycleReadonlyErrorDetail
): string {
  if (detail.lifecycle_state === "stopped") {
    return "This project is stopped. Resume it before making changes.";
  }
  if (detail.closure_type === "completed") {
    return "This project is closed as completed and is read-only.";
  }
  if (detail.closure_type === "administrative") {
    return "This project is closed administratively and is read-only.";
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
