import type {
  OfficialFolderCheckPreview,
  ProjectFolderRequiredFormsPreview,
  PublicFolderWorkflowContext,
  PublicFolderWorkflowOperationType,
  PublicFolderWorkflowPreview,
  PublicFolderWorkflowResult,
  RequestMaterialPreview,
} from "../../api/client";
import type { WorkbenchVersionStatus } from "./projectWorkbenchVersionSelectors";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

export type ProjectFolderTaskKey =
  | "project_folder"
  | "public_working_copy"
  | "approval_package"
  | "approved_folder";

export type ProjectFolderTaskStatus = "neutral" | "blocked";

export type ProjectFolderTaskIconName = "folder" | "refresh" | "package" | "copy";

export type ProjectFolderTaskActionTarget =
  | "folder"
  | "project_folder_open"
  | "request_material"
  | "fee"
  | "required_forms_generate"
  | "required_forms_refresh"
  | "official_folder_repair"
  | "official_folder_refresh"
  | "public_folder_workflow_sync"
  | "public_folder_workflow_submit"
  | "public_folder_workflow_pull"
  | null;

export type ProjectFolderWorkflowOperationMap<T> = Record<
  PublicFolderWorkflowOperationType,
  T
>;

export type ProjectFolderTaskAutoSyncControl = {
  checked: boolean;
  disabled: boolean;
  busy: boolean;
  blocker?: string | null;
};

export type ProjectFolderTaskRow = {
  key: ProjectFolderTaskKey;
  title: string;
  iconName: ProjectFolderTaskIconName;
  statusLabel: string;
  status: ProjectFolderTaskStatus;
  summary: string;
  context: string;
  actionLabel?: string;
  actionTarget?: ProjectFolderTaskActionTarget;
  blockers: string[];
  warnings: string[];
  operation?: PublicFolderWorkflowOperationType;
  autoSync?: ProjectFolderTaskAutoSyncControl;
  confirming?: boolean;
  confirmLabel?: string;
  cancelLabel?: string;
  detailMessages?: string[];
};

export type ProjectFolderTaskSelectorInput = {
  folderReady: boolean;
  matrixAuthorityReady: boolean;
  officialFolderCheckPreview: OfficialFolderCheckPreview | null;
  requestMaterialPreview: RequestMaterialPreview | null;
  requestMaterialError: string | null;
  publicFolderWorkflowContext: PublicFolderWorkflowContext | null;
  publicFolderWorkflowContextLoading: boolean;
  publicFolderWorkflowContextError: string | null;
  publicFolderWorkflowPreviews: ProjectFolderWorkflowOperationMap<
    PublicFolderWorkflowPreview | null
  >;
  publicFolderWorkflowResults: ProjectFolderWorkflowOperationMap<
    PublicFolderWorkflowResult | null
  >;
  publicFolderWorkflowBusyOperation: PublicFolderWorkflowOperationType | null;
  publicFolderWorkflowConfirmingOperation: PublicFolderWorkflowOperationType | null;
  publicFolderWorkflowError: string | null;
  publicFolderWorkflowMessage: string | null;
  publicFolderWorkflowAutoSyncBusy: boolean;
  requiredFormsPreview: ProjectFolderRequiredFormsPreview | null;
  requiredFormsError: string | null;
  section2SyncPreview: ProjectRuntimeConsoleModel["section2SyncPreview"];
  versionStatus: WorkbenchVersionStatus;
  confirmedFeeAuthorityStatus: "missing" | "confirmed" | "stale" | "unknown";
  lifecycleReadonlyReason?: string | null;
};

export function deriveProjectFolderTasks(
  input: ProjectFolderTaskSelectorInput
): ProjectFolderTaskRow[] {
  const basicInformationBlocker = findBasicInformationRequiredFormsBlocker(input);
  const contextBlocker = selectContextBlocker(input);
  const localProjectFolderPath =
    input.publicFolderWorkflowContext?.local_official_folder_path?.trim() ?? "";
  const projectFolderOpenAvailable = Boolean(localProjectFolderPath);
  return [
    {
      key: "project_folder",
      title: "Project folder",
      iconName: "folder",
      statusLabel: "Open",
      status: projectFolderOpenAvailable ? "neutral" : "blocked",
      summary: "Folder access.",
      context: projectFolderOpenAvailable
        ? "Local folder available."
        : "Project folder is not available yet.",
      actionLabel: "Open",
      actionTarget: projectFolderOpenAvailable ? "project_folder_open" : null,
      blockers: projectFolderOpenAvailable
        ? []
        : ["Project folder is not available yet."],
      warnings: basicInformationBlocker ? [basicInformationBlocker] : [],
    },
    deriveWorkflowTask(input, contextBlocker, "sync"),
    deriveWorkflowTask(input, contextBlocker, "submit"),
    deriveWorkflowTask(input, contextBlocker, "pull"),
  ];
}

export function selectCurrentProjectFolderTaskKey(
  tasks: ProjectFolderTaskRow[]
): ProjectFolderTaskKey {
  return tasks[0]?.key ?? "project_folder";
}

export function selectProjectFolderOneClickBlocker(
  tasks: ProjectFolderTaskRow[],
  folderReady: boolean
): string | null {
  if (!folderReady) {
    return null;
  }
  for (const task of tasks) {
    const blocker = [...task.blockers, ...task.warnings].find(
      isBasicInformationRequiredFormsBlocker
    );
    if (blocker) {
      return blocker;
    }
  }
  return null;
}

function findBasicInformationRequiredFormsBlocker(
  input: ProjectFolderTaskSelectorInput
): string | null {
  const blockers = [
    ...(input.requiredFormsPreview?.blockers ?? []),
    ...(input.requiredFormsError ? [input.requiredFormsError] : []),
  ];
  return blockers.find(isBasicInformationRequiredFormsBlocker) ?? null;
}

function isBasicInformationRequiredFormsBlocker(message: string): boolean {
  return (
    message.includes("Basic Information") &&
    (message.includes("Confirm") || message.includes("confirm"))
  );
}

function deriveWorkflowTask(
  input: ProjectFolderTaskSelectorInput,
  contextBlocker: string | null,
  operation: PublicFolderWorkflowOperationType
): ProjectFolderTaskRow {
  const preview = input.publicFolderWorkflowPreviews?.[operation] ?? null;
  const result = input.publicFolderWorkflowResults?.[operation] ?? null;
  const issue = selectPreviewIssue(preview);
  const busy = input.publicFolderWorkflowBusyOperation === operation;
  const confirming = input.publicFolderWorkflowConfirmingOperation === operation;
  const readonlyReason = input.lifecycleReadonlyReason ?? null;
  const blocker = readonlyReason ?? contextBlocker ?? issue;
  const definition = workflowDefinition(operation);
  const canRun = !blocker && Boolean(input.publicFolderWorkflowContext) && !busy;
  const detailMessages = [
    ...(preview ? selectPreviewDetailMessages(preview) : []),
    ...(result ? selectResultDetailMessages(result) : []),
    ...selectOperationFeedback(input, operation),
  ];

  return {
    key: definition.key,
    title: definition.title,
    iconName: definition.iconName,
    statusLabel: definition.statusLabel,
    status: blocker ? "blocked" : "neutral",
    summary: definition.summary,
    context: workflowContextCopy(input, operation),
    actionLabel: busy ? definition.busyLabel : definition.actionLabel,
    actionTarget: canRun ? definition.actionTarget : null,
    blockers: blocker ? [blocker] : [],
    warnings: [...(input.publicFolderWorkflowContext?.warnings ?? []), ...(preview?.warnings ?? [])],
    operation,
    autoSync:
      operation === "sync"
        ? {
            checked: input.publicFolderWorkflowContext?.auto_sync_enabled ?? false,
            disabled: Boolean(readonlyReason || contextBlocker || input.publicFolderWorkflowAutoSyncBusy),
            busy: input.publicFolderWorkflowAutoSyncBusy,
            blocker: readonlyReason ?? contextBlocker,
          }
        : undefined,
    confirming,
    confirmLabel: definition.confirmLabel,
    cancelLabel: "Cancel",
    detailMessages,
  };
}

function workflowDefinition(operation: PublicFolderWorkflowOperationType): {
  key: ProjectFolderTaskKey;
  title: string;
  iconName: ProjectFolderTaskIconName;
  statusLabel: string;
  summary: string;
  actionLabel: string;
  busyLabel: string;
  confirmLabel: string;
  actionTarget: ProjectFolderTaskActionTarget;
} {
  if (operation === "sync") {
    return {
      key: "public_working_copy",
      title: "Public working copy",
      iconName: "refresh",
      statusLabel: "Sync",
      summary: "Keep the lab working copy aligned.",
      actionLabel: "Sync now",
      busyLabel: "Checking...",
      confirmLabel: "Confirm sync",
      actionTarget: "public_folder_workflow_sync",
    };
  }
  if (operation === "submit") {
    return {
      key: "approval_package",
      title: "Approval package",
      iconName: "package",
      statusLabel: "Submit",
      summary: "Submit controlled output.",
      actionLabel: "Submit",
      busyLabel: "Checking...",
      confirmLabel: "Confirm submit",
      actionTarget: "public_folder_workflow_submit",
    };
  }
  return {
    key: "approved_folder",
    title: "Approved folder",
    iconName: "copy",
    statusLabel: "Pull",
    summary: "Bring approved public results back.",
    actionLabel: "Pull",
    busyLabel: "Checking...",
    confirmLabel: "Confirm pull",
    actionTarget: "public_folder_workflow_pull",
  };
}

function workflowContextCopy(
  input: ProjectFolderTaskSelectorInput,
  operation: PublicFolderWorkflowOperationType
): string {
  const context = input.publicFolderWorkflowContext;
  if (!context) {
    return input.publicFolderWorkflowContextLoading
      ? "Loading workflow state."
      : "Workflow state is unavailable.";
  }
  if (operation === "sync") {
    if (context.sync_locked) {
      return "Submitted package is locked.";
    }
    return context.public_open_path
      ? "Public Open working copy."
      : "Public Open location will be prepared after preview.";
  }
  if (operation === "submit") {
    if (context.sync_locked) {
      return "Approval package has already been submitted.";
    }
    return "Preview moves Open output to Closed after confirmation.";
  }
  return context.public_closed_path
    ? "Closed output can be pulled without overwriting local history."
    : "Closed output is available after approval package submission.";
}

function selectContextBlocker(input: ProjectFolderTaskSelectorInput): string | null {
  if (input.publicFolderWorkflowContextError) {
    return input.publicFolderWorkflowContextError;
  }
  const context = input.publicFolderWorkflowContext;
  if (!context) {
    return input.publicFolderWorkflowContextLoading
      ? "Workflow state is loading."
      : "Public folder workflow is unavailable.";
  }
  return context.blockers[0] ?? null;
}

function selectPreviewIssue(
  preview: PublicFolderWorkflowPreview | null
): string | null {
  if (!preview) {
    return null;
  }
  return preview.blockers[0] ?? preview.conflicts[0] ?? null;
}

function selectPreviewDetailMessages(preview: PublicFolderWorkflowPreview): string[] {
  if (preview.status === "ready") {
    return ["Preview can be confirmed."];
  }
  return [
    ...preview.blockers.slice(0, 1),
    ...preview.conflicts.slice(0, 1),
    ...preview.warnings.slice(0, 1),
  ];
}

function selectResultDetailMessages(result: PublicFolderWorkflowResult): string[] {
  if (result.status === "completed") {
    return [`${operationLabel(result.operation_type)} completed.`];
  }
  return result.errors.slice(0, 1);
}

function selectOperationFeedback(
  input: ProjectFolderTaskSelectorInput,
  operation: PublicFolderWorkflowOperationType
): string[] {
  if (input.publicFolderWorkflowBusyOperation === operation) {
    return ["Working..."];
  }
  if (input.publicFolderWorkflowConfirmingOperation === operation) {
    return ["Confirm after reviewing the preview."];
  }
  if (input.publicFolderWorkflowError) {
    return [input.publicFolderWorkflowError];
  }
  if (input.publicFolderWorkflowMessage) {
    return [input.publicFolderWorkflowMessage];
  }
  return [];
}

function operationLabel(operation: PublicFolderWorkflowOperationType): string {
  if (operation === "sync") {
    return "Sync";
  }
  if (operation === "submit") {
    return "Submit";
  }
  return "Pull";
}
