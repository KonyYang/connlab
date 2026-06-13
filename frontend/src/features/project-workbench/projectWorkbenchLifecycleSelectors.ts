export type WorkbenchLifecycleMode =
  | "overview"
  | "temporary_planning"
  | "registered_setup"
  | "package_preparation"
  | "execution_console";

export type WorkbenchLifecycleTone = "ready" | "blocked" | "warning" | "neutral";

export type WorkbenchLifecycleInput = {
  hasLtr: boolean;
  hasActiveMatrix: boolean;
  hasCandidateMatrix: boolean;
  folderReady: boolean;
  folderTemplateReady: boolean | null;
  packageStatus: "ready" | "blocked" | null;
  packageBlockers: string[];
  packageWarnings: string[];
  requestMaterialStatus: "blocked" | "ready" | "collected" | "partial" | "conflict" | null;
  requestMaterialBlockers: string[];
  requestMaterialWarnings: string[];
  hasRequestMaterialPreviewError: boolean;
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
  actionTarget?: "matrix" | "fee" | "package" | "folder" | "settings" | "request_material" | null;
};

export type WorkbenchLifecycleViewModel = {
  mode: WorkbenchLifecycleMode;
  stageLabel: string;
  stageSummary: string;
  nextAction: WorkbenchNextAction;
  tabs: WorkbenchLifecycleTab[];
};

const ACTIVE_MATRIX_TABS: WorkbenchLifecycleTab[] = [
  { mode: "package_preparation", label: "Project Folder" },
  { mode: "execution_console", label: "Execution" },
];

export function deriveProjectWorkbenchLifecycle(
  input: WorkbenchLifecycleInput,
  requestedMode: WorkbenchLifecycleMode | null = null
): WorkbenchLifecycleViewModel {
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
    stageSummary: "Prepare local project files before public-drive submission.",
    nextAction: buildProjectFolderNextAction(input),
    tabs: ACTIVE_MATRIX_TABS,
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
      title: "Create local project folder",
      reason: "The official project folder is required before request material can be collected.",
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
    return {
      title: "Project Folder is ready for the next preparation step",
      reason: "Request material is collected. Continue with approved form and fee tasks when available.",
      tone: "ready",
      actionLabel: "Refresh checks",
      actionTarget: "package",
    };
  }

  return {
    title: "Check project folder readiness",
    reason: "Refresh checks before preparing generated forms and submitted material.",
    tone: "neutral",
    actionLabel: "Refresh checks",
    actionTarget: "package",
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
