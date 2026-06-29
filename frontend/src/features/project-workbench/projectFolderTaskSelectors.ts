import type {
  OfficialFolderCheckPreview,
  ProjectFolderRequiredFormsPreview,
  PublicDriveUploadPreview,
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
  | "request_material"
  | "fee"
  | "required_forms_generate"
  | "required_forms_refresh"
  | "official_folder_repair"
  | "official_folder_refresh"
  | "public_drive_upload"
  | "public_drive_refresh"
  | null;

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
};

export type ProjectFolderTaskSelectorInput = {
  folderReady: boolean;
  matrixAuthorityReady: boolean;
  officialFolderCheckPreview: OfficialFolderCheckPreview | null;
  requestMaterialPreview: RequestMaterialPreview | null;
  requestMaterialError: string | null;
  publicDriveUploadPreview: PublicDriveUploadPreview | null;
  publicDriveUploadError: string | null;
  requiredFormsPreview: ProjectFolderRequiredFormsPreview | null;
  requiredFormsError: string | null;
  section2SyncPreview: ProjectRuntimeConsoleModel["section2SyncPreview"];
  versionStatus: WorkbenchVersionStatus;
  confirmedFeeAuthorityStatus: "missing" | "confirmed" | "stale" | "unknown";
};

export function deriveProjectFolderTasks(
  input: ProjectFolderTaskSelectorInput
): ProjectFolderTaskRow[] {
  const basicInformationBlocker = findBasicInformationRequiredFormsBlocker(input);
  return [
    {
      key: "project_folder",
      title: "Project folder",
      iconName: "folder",
      statusLabel: "Open",
      status: "neutral",
      summary: "Folder access.",
      context: input.folderReady
        ? "Open is not connected yet."
        : "Folder setup is not available yet.",
      actionLabel: "Open",
      actionTarget: null,
      blockers: [
        input.folderReady
          ? "Project folder open is not connected yet."
          : "Project folder is not available yet.",
        ...(basicInformationBlocker ? [basicInformationBlocker] : []),
      ],
      warnings: [],
    },
    {
      key: "public_working_copy",
      title: "Public working copy",
      iconName: "refresh",
      statusLabel: "Sync",
      status: "neutral",
      summary: "Keep the lab working copy aligned.",
      context: "Sync workflow placeholder.",
      actionLabel: "Sync now",
      actionTarget: null,
      blockers: ["Sync workflow is not connected yet."],
      warnings: [],
    },
    {
      key: "approval_package",
      title: "Approval package",
      iconName: "package",
      statusLabel: "Submit",
      status: "neutral",
      summary: "Submit controlled output.",
      context: "Moves Open package to Closed after confirmation.",
      actionLabel: "Submit",
      actionTarget: null,
      blockers: ["Submit workflow is not connected yet."],
      warnings: [],
    },
    {
      key: "approved_folder",
      title: "Approved folder",
      iconName: "copy",
      statusLabel: "Pull",
      status: "neutral",
      summary: "Bring approved public results back.",
      context: "Closed package · keep local history.",
      actionLabel: "Pull",
      actionTarget: null,
      blockers: ["Pull workflow is not connected yet."],
      warnings: [],
    },
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
    const blocker = task.blockers.find(isBasicInformationRequiredFormsBlocker);
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
