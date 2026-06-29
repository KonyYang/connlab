import type {
  ProjectCloseReasonCategory,
  ProjectLifecycleResponse,
} from "../../api/client";
import type { ProjectLifecycleReadonlyView } from "../project-lifecycle/projectLifecycleReadonlyModel";

export type WorkbenchLifecycleMode =
  | "overview"
  | "temporary_planning"
  | "registered_setup"
  | "package_preparation"
  | "execution_console";

export type WorkbenchLifecycleTone = "ready" | "blocked" | "warning" | "neutral";

export type WorkbenchLifecycleInput = {
  hasLtr: boolean;
  isCancelled: boolean;
  lifecycleReadonlyView?: ProjectLifecycleReadonlyView;
  hasActiveMatrix: boolean;
  hasCandidateMatrix: boolean;
  folderReady: boolean;
  folderTemplateReady: boolean | null;
  packageStatus: "ready" | "blocked" | null;
  packageBlockers: string[];
  packageWarnings: string[];
  requestMaterialStatus:
    | "blocked"
    | "ready"
    | "collected"
    | "review_required"
    | "partial"
    | "conflict"
    | null;
  requestMaterialBlockers: string[];
  requestMaterialWarnings: string[];
  hasRequestMaterialPreviewError: boolean;
  officialFolderCheckStatus:
    | "blocked"
    | "missing"
    | "warning"
    | "ready"
    | "conflict"
    | null;
  officialFolderCheckBlockers: string[];
  officialFolderCheckWarnings: string[];
  hasOfficialFolderCheckError: boolean;
  publicDrivePreviewStatus:
    | "blocked"
    | "ready"
    | "current"
    | "conflict"
    | "warning"
    | null;
  publicDrivePreviewBlockers: string[];
  publicDrivePreviewWarnings: string[];
  hasPublicDrivePreviewError: boolean;
  section2Status: string | null;
  hasPackagePreviewError: boolean;
};

export type WorkbenchLifecycleTab = {
  mode: WorkbenchLifecycleMode;
  label: string;
  disabled?: boolean;
  reason?: string;
};

export type WorkbenchNextAction = {
  title: string;
  reason: string;
  tone: WorkbenchLifecycleTone;
  actionLabel?: string;
  actionTarget?:
    | "matrix"
    | "fee"
    | "package"
    | "folder"
    | "settings"
    | "request_material"
    | "official_folder_repair"
    | "official_folder_refresh"
    | "public_drive_upload"
    | "public_drive_refresh"
    | null;
};

export type WorkbenchLifecycleViewModel = {
  mode: WorkbenchLifecycleMode;
  stageLabel: string;
  stageSummary: string;
  nextAction: WorkbenchNextAction;
  tabs: WorkbenchLifecycleTab[];
};

export type WorkbenchLifecycleActionPrimary = "close" | "activate" | "none";

export type WorkbenchLifecycleActionsViewModel = {
  primaryAction: WorkbenchLifecycleActionPrimary;
  canStop: boolean;
  canResume: boolean;
  canClose: boolean;
  canActivate: boolean;
  closeActionLabel: string;
  activateActionLabel: string;
  defaultCloseReasonCategory: ProjectCloseReasonCategory;
  closeReasonLabel: string | null;
  readonlyReason: string | null;
};

export type WorkbenchLifecycleActionOptions = {
  hasRegisteredProject?: boolean;
};

const ACTIVE_MATRIX_TABS: WorkbenchLifecycleTab[] = [
  { mode: "package_preparation", label: "Project Folder" },
  { mode: "execution_console", label: "Execution" },
];

export function deriveProjectWorkbenchLifecycle(
  input: WorkbenchLifecycleInput,
  requestedMode: WorkbenchLifecycleMode | null = null
): WorkbenchLifecycleViewModel {
  if (input.lifecycleReadonlyView?.readonly) {
    const baseLifecycle = deriveProjectWorkbenchLifecycle(
      {
        ...input,
        isCancelled: false,
        lifecycleReadonlyView: undefined,
      },
      requestedMode
    );
    return {
      ...baseLifecycle,
      mode: input.hasActiveMatrix ? baseLifecycle.mode : "overview",
      stageLabel: input.lifecycleReadonlyView.title,
      stageSummary: input.lifecycleReadonlyView.message,
      nextAction: {
        title: "Read-only project",
        reason: input.lifecycleReadonlyView.message,
        tone: "neutral",
      },
      tabs: baseLifecycle.tabs,
    };
  }

  if (input.isCancelled) {
    return {
      mode: "overview",
      stageLabel: "Stopped project",
      stageSummary: "This project is stopped and retained for review. Planning and promotion actions are not available.",
      nextAction: {
        title: "No action",
        reason: "Stopped projects are retained for review only.",
        tone: "neutral",
      },
      tabs: [],
    };
  }

  if (!input.hasLtr) {
    return {
      mode: "temporary_planning",
      stageLabel: "Temporary planning",
      stageSummary: "No DL number is registered yet. Use this space to shape Matrix scope and fee expectations before formal setup.",
      nextAction: {
        title: "Plan Matrix and fee before DL registration",
        reason: "Formal package preparation starts after the project has a DL number and active Matrix authority.",
        tone: "neutral",
        actionLabel: "Open Matrix",
        actionTarget: "matrix",
      },
      tabs: [{ mode: "temporary_planning", label: "Planning" }],
    };
  }

  if (!input.hasActiveMatrix) {
    return {
      mode: "registered_setup",
      stageLabel: "Matrix authority setup",
      stageSummary: "DL registration is available. Publish the active Matrix authority before preparing derived outputs.",
      nextAction: {
        title: input.hasCandidateMatrix
          ? "Confirm Matrix authority"
          : "Create Matrix authority",
        reason: "Test Record, Fee Evaluation, Section 2 sync, and package readiness all derive from the active Matrix.",
        tone: input.hasCandidateMatrix ? "warning" : "blocked",
        actionLabel: "Open Matrix",
        actionTarget: "matrix",
      },
      tabs: [{ mode: "registered_setup", label: "Matrix setup" }],
    };
  }

  const mode =
    requestedMode === "execution_console" ||
    requestedMode === "package_preparation"
      ? requestedMode
      : "package_preparation";

  if (mode === "execution_console") {
    return {
      mode,
      stageLabel: "Execution console",
      stageSummary: "Use the active Matrix as the execution map and inspect step-level method, condition, and requirement details.",
      nextAction: buildExecutionNextAction(input),
      tabs: ACTIVE_MATRIX_TABS,
    };
  }

  return {
    mode: "package_preparation",
    stageLabel: "Project Folder preparation",
    stageSummary: "Finish the project folder files.",
    nextAction: buildProjectFolderNextAction(input),
    tabs: ACTIVE_MATRIX_TABS,
  };
}

export function deriveProjectWorkbenchLifecycleActions(
  lifecycle: ProjectLifecycleResponse | null,
  readonlyView?: ProjectLifecycleReadonlyView,
  options: WorkbenchLifecycleActionOptions = {}
): WorkbenchLifecycleActionsViewModel {
  const readonlyReason = readonlyView?.readonly ? readonlyView.message : null;
  const allowedActions = lifecycle?.allowed_actions ?? [];
  const canStop = false;
  const canResume = false;
  const canClose =
    lifecycle?.lifecycle_state === "active" &&
    !lifecycle.readonly &&
    allowedActions.includes("close");
  const canActivate =
    (lifecycle?.lifecycle_state === "stopped" ||
      lifecycle?.lifecycle_state === "closed") &&
    allowedActions.includes("activate");

  return {
    primaryAction: canClose ? "close" : canActivate ? "activate" : "none",
    canStop,
    canResume,
    canClose,
    canActivate,
    closeActionLabel: "Close project",
    activateActionLabel: "Activate project",
    defaultCloseReasonCategory: options.hasRegisteredProject ? "completed" : "other",
    closeReasonLabel: lifecycle?.close_reason_label ?? null,
    readonlyReason,
  };
}

function buildProjectFolderNextAction(input: WorkbenchLifecycleInput): WorkbenchNextAction {
  if (!input.folderReady && input.folderTemplateReady === false) {
    return {
      title: "Enable project folder template",
      reason: "Project folder template is inactive in Settings.",
      tone: "blocked",
      actionLabel: "Open Settings",
      actionTarget: "settings",
    };
  }

  if (!input.folderReady) {
    return {
      title: "Create project folder",
      reason: "Create the official project folder before collecting request material.",
      tone: "warning",
      actionLabel: "Review folder setup",
      actionTarget: "folder",
    };
  }

  if (input.hasRequestMaterialPreviewError) {
    return {
      title: "Refresh request material",
      reason: "Request material could not be loaded. Refresh before copying source files.",
      tone: "blocked",
      actionLabel: "Refresh request material",
      actionTarget: "request_material",
    };
  }

  if (input.requestMaterialStatus === "blocked" || input.requestMaterialStatus === "conflict") {
    return {
      title: "Review request material",
      reason:
        input.requestMaterialBlockers[0] ??
        "Request material needs review before ConnLab can copy source files.",
      tone: "blocked",
    };
  }

  if (input.requestMaterialStatus === "review_required") {
    return {
      title: "Review request material",
      reason:
        input.requestMaterialWarnings[0] ??
        "Available request files are collected. Review undecided attachments before placing them in Submitted Material.",
      tone: "warning",
    };
  }

  if (input.hasOfficialFolderCheckError) {
    return {
      title: "Refresh project folder check",
      reason: "Project Folder check could not be loaded.",
      tone: "blocked",
      actionLabel: "Refresh project folder check",
      actionTarget: "official_folder_refresh",
    };
  }

  if (input.officialFolderCheckStatus === "conflict") {
    return {
      title: "Review folder structure conflict",
      reason:
        input.officialFolderCheckBlockers[0] ??
        "A required project folder path exists with the wrong type.",
      tone: "blocked",
    };
  }

  if (input.officialFolderCheckStatus === "missing") {
    return {
      title: "Repair folder structure",
      reason:
        input.officialFolderCheckBlockers[0] ??
        "Required local project folders are missing.",
      tone: "warning",
      actionLabel: "Repair folder structure",
      actionTarget: "official_folder_repair",
    };
  }

  if (input.officialFolderCheckStatus === "warning") {
    return {
      title: "Review project folder warnings",
      reason:
        input.officialFolderCheckWarnings[0] ??
        "Project Folder check has warnings that should be reviewed.",
      tone: "warning",
      actionLabel: "Refresh project folder check",
      actionTarget: "official_folder_refresh",
    };
  }

  if (
    input.requestMaterialStatus === null ||
    input.requestMaterialStatus === "ready" ||
    input.requestMaterialStatus === "partial"
  ) {
    return {
      title: "Collect request material",
      reason:
        input.requestMaterialWarnings[0] ??
        "Copy original request files into Source Book and controlled copies into the official project folder.",
      tone: input.requestMaterialStatus === "partial" ? "warning" : "neutral",
      actionLabel: "Collect request material",
      actionTarget: "request_material",
    };
  }

  if (input.hasPackagePreviewError) {
    return {
      title: "Refresh project folder checks",
      reason: "Project folder output checks could not be loaded.",
      tone: "blocked",
      actionLabel: "Refresh checks",
      actionTarget: "package",
    };
  }

  if (input.packageStatus === "blocked") {
    return {
      title: "Resolve project folder blockers",
      reason:
        input.packageBlockers[0] ??
        "Project folder checks have blockers that must be resolved before continuing.",
      tone: "blocked",
      actionLabel: selectPackageBlockerAction(input),
      actionTarget: selectPackageBlockerTarget(input),
    };
  }

  if (input.packageWarnings.length > 0) {
    return {
      title: "Review project folder warnings",
      reason: input.packageWarnings[0],
      tone: "warning",
      actionLabel: "Refresh checks",
      actionTarget: "package",
    };
  }

  if (input.packageStatus === "ready") {
    return buildPublicDriveNextAction(input);
  }

  return {
    title: "Check project folder readiness",
    reason: "Refresh checks before preparing generated forms and submitted material.",
    tone: "neutral",
    actionLabel: "Refresh checks",
    actionTarget: "package",
  };
}

function buildPublicDriveNextAction(input: WorkbenchLifecycleInput): WorkbenchNextAction {
  if (input.hasPublicDrivePreviewError) {
    return {
      title: "Refresh public-drive preview",
      reason: "Public-drive upload preview could not be loaded.",
      tone: "blocked",
      actionLabel: "Refresh public-drive preview",
      actionTarget: "public_drive_refresh",
    };
  }

  if (input.publicDrivePreviewStatus === "conflict") {
    return {
      title: "Review public-drive conflict",
      reason:
        input.publicDrivePreviewBlockers[0] ??
        "Resolve public-drive conflicts before upload.",
      tone: "blocked",
    };
  }

  if (input.publicDrivePreviewStatus === "blocked") {
    return {
      title: "Public-drive upload is not ready",
      reason:
        input.publicDrivePreviewBlockers[0] ??
        "Review the public-drive upload blocker before submitting the Project Folder.",
      tone: "blocked",
    };
  }

  if (input.publicDrivePreviewStatus === "ready") {
    return {
      title: "Upload Project Folder to public drive",
      reason: "Preview is ready. Upload the local Project Folder to the configured public location.",
      tone: "ready",
      actionLabel: "Upload to public drive",
      actionTarget: "public_drive_upload",
    };
  }

  if (input.publicDrivePreviewStatus === "warning") {
    return {
      title: "Review public-drive upload warnings",
      reason:
        input.publicDrivePreviewWarnings[0] ??
        "Public-drive preview has warnings that should be reviewed before upload.",
      tone: "warning",
      actionLabel: "Upload to public drive",
      actionTarget: "public_drive_upload",
    };
  }

  if (input.publicDrivePreviewStatus === "current") {
    return {
      title: "Public-drive folder is current",
      reason: "The public Project Folder already matches the local Project Folder.",
      tone: "ready",
      actionLabel: "Refresh public-drive preview",
      actionTarget: "public_drive_refresh",
    };
  }

  return {
    title: "Preview public-drive upload",
    reason: "Review public-drive add, update, already-current, and conflict items before upload.",
    tone: "neutral",
    actionLabel: "Preview public-drive upload",
    actionTarget: "public_drive_refresh",
  };
}

function buildExecutionNextAction(input: WorkbenchLifecycleInput): WorkbenchNextAction {
  if (input.packageStatus === "blocked" && input.packageBlockers.length > 0) {
    return {
      title: "Use Matrix as the execution map",
      reason: `Execution view is available, but Project Folder preparation still has a blocker: ${input.packageBlockers[0]}`,
      tone: "warning",
      actionLabel: "Open Matrix",
      actionTarget: "matrix",
    };
  }

  return {
    title: "Use Matrix as the execution map",
    reason: "Select a Matrix step to inspect method, condition, requirement, and lifecycle projection.",
    tone: input.packageStatus === "ready" ? "ready" : "neutral",
    actionLabel: "Open Matrix",
    actionTarget: "matrix",
  };
}

function selectPackageBlockerAction(input: WorkbenchLifecycleInput): string {
  const firstBlocker = (input.packageBlockers[0] ?? "").toLowerCase();
  if (firstBlocker.includes("fee")) {
    return "Open Fee Evaluation";
  }
  if (firstBlocker.includes("template") || firstBlocker.includes("settings")) {
    return "Open Settings";
  }
  if (firstBlocker.includes("folder")) {
    return "Review folder setup";
  }
  return "Refresh preview";
}

function selectPackageBlockerTarget(
  input: WorkbenchLifecycleInput
): WorkbenchNextAction["actionTarget"] {
  const firstBlocker = (input.packageBlockers[0] ?? "").toLowerCase();
  if (firstBlocker.includes("fee")) {
    return "fee";
  }
  if (firstBlocker.includes("template") || firstBlocker.includes("settings")) {
    return "settings";
  }
  if (firstBlocker.includes("folder")) {
    return "folder";
  }
  return "package";
}
