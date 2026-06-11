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
  actionTarget?: "matrix" | "fee" | "package" | "folder" | "settings" | null;
};

export type WorkbenchLifecycleViewModel = {
  mode: WorkbenchLifecycleMode;
  stageLabel: string;
  stageSummary: string;
  nextAction: WorkbenchNextAction;
  tabs: WorkbenchLifecycleTab[];
};

const ACTIVE_MATRIX_TABS: WorkbenchLifecycleTab[] = [
  { mode: "overview", label: "Overview" },
  { mode: "package_preparation", label: "Package" },
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
    requestedMode === "overview" ||
    requestedMode === "execution_console" ||
    requestedMode === "package_preparation"
      ? requestedMode
      : "package_preparation";

  if (mode === "overview") {
    return {
      mode,
      stageLabel: "Project overview",
      stageSummary: "Review lifecycle state, current blockers, and the next controlled action before opening a work surface.",
      nextAction: buildPackageNextAction(input),
      tabs: ACTIVE_MATRIX_TABS,
    };
  }

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
    stageLabel: "Package preparation",
    stageSummary: "Prepare the folder, Section 2 dates, confirmed fee, Customer Feedback template, and package readiness from the active Matrix.",
    nextAction: buildPackageNextAction(input),
    tabs: ACTIVE_MATRIX_TABS,
  };
}

function buildPackageNextAction(input: WorkbenchLifecycleInput): WorkbenchNextAction {
  if (input.hasPackagePreviewError) {
    return {
      title: "Refresh package readiness",
      reason: "Package readiness could not be loaded. Refresh the preview before preparing outputs.",
      tone: "blocked",
      actionLabel: "Refresh preview",
      actionTarget: "package",
    };
  }

  if (!input.folderReady && input.folderTemplateReady === false) {
    return {
      title: "Enable project folder template",
      reason: "Project folder template is inactive in Settings.",
      tone: "blocked",
      actionLabel: "Open Settings",
      actionTarget: "settings",
    };
  }

  if (input.packageStatus === "blocked") {
    return {
      title: "Resolve package blockers",
      reason:
        input.packageBlockers[0] ??
        "Package readiness has blockers that must be resolved before execution.",
      tone: "blocked",
      actionLabel: selectPackageBlockerAction(input),
      actionTarget: selectPackageBlockerTarget(input),
    };
  }

  if (!input.folderReady) {
    return {
      title: "Create project folder",
      reason: "The latest project folder is required before final package files can be placed.",
      tone: "warning",
      actionLabel: "Review folder setup",
      actionTarget: "folder",
    };
  }

  if (input.packageWarnings.length > 0) {
    return {
      title: "Review package warnings",
      reason: input.packageWarnings[0],
      tone: "warning",
      actionLabel: "Refresh preview",
      actionTarget: "package",
    };
  }

  if (input.packageStatus === "ready") {
    return {
      title: "Review package readiness",
      reason: "Required package inputs are ready. Package execution remains a separate approved task.",
      tone: "ready",
      actionLabel: "Refresh preview",
      actionTarget: "package",
    };
  }

  return {
    title: "Check package readiness",
    reason: "Refresh readiness before preparing Test Record, Fee Form, and Customer Feedback outputs.",
    tone: "neutral",
    actionLabel: "Refresh preview",
    actionTarget: "package",
  };
}

function buildExecutionNextAction(input: WorkbenchLifecycleInput): WorkbenchNextAction {
  if (input.packageStatus === "blocked" && input.packageBlockers.length > 0) {
    return {
      title: "Use Matrix as the execution map",
      reason: `Execution view is available, but package preparation still has a blocker: ${input.packageBlockers[0]}`,
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
