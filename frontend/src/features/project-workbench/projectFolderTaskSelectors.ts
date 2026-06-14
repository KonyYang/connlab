import type {
  OfficialFolderCheckPreview,
  ProjectFolderRequiredFormsPreview,
  PublicDriveUploadPreview,
  RequestMaterialPreview,
} from "../../api/client";
import type { WorkbenchVersionStatus } from "./projectWorkbenchVersionSelectors";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

export type ProjectFolderTaskKey =
  | "local_project_folder"
  | "request_material"
  | "confirmed_fee_authority"
  | "required_forms"
  | "section2"
  | "submitted_material"
  | "public_drive_upload";

export type ProjectFolderTaskStatus = "ready" | "blocked" | "warning" | "neutral";

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
  statusLabel: string;
  status: ProjectFolderTaskStatus;
  summary: string;
  actionLabel?: string;
  actionTarget?: ProjectFolderTaskActionTarget;
  detailKind:
    | "folder"
    | "request_material"
    | "fee_authority"
    | "required_forms"
    | "section2"
    | "submitted_material"
    | "public_drive";
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
  return [
    deriveLocalProjectFolderTask(input),
    deriveRequestMaterialTask(input),
    deriveConfirmedFeeAuthorityTask(input),
    deriveRequiredFormsTask(input),
    deriveSection2Task(input),
    deriveSubmittedMaterialTask(input),
    derivePublicDriveUploadTask(input),
  ];
}

export function selectCurrentProjectFolderTaskKey(
  tasks: ProjectFolderTaskRow[]
): ProjectFolderTaskKey {
  const needsAttention = tasks.find((task) => task.status !== "ready");
  return needsAttention?.key ?? "public_drive_upload";
}

function deriveLocalProjectFolderTask(
  input: ProjectFolderTaskSelectorInput
): ProjectFolderTaskRow {
  const checkStatus = input.officialFolderCheckPreview?.status ?? null;
  if (!input.folderReady) {
    return {
      key: "local_project_folder",
      title: "Local project folder",
      statusLabel: "Not created",
      status: "blocked",
      summary: "Create the local DL folder and Official project folder before preparation.",
      actionLabel: "Create local project folder",
      actionTarget: "folder",
      detailKind: "folder",
      blockers: ["The local project folder has not been created."],
      warnings: [],
    };
  }
  if (checkStatus === "missing") {
    return {
      key: "local_project_folder",
      title: "Local project folder",
      statusLabel: "Needs repair",
      status: "blocked",
      summary: "Required local project folders are missing.",
      actionLabel: "Repair folder structure",
      actionTarget: "official_folder_repair",
      detailKind: "folder",
      blockers: input.officialFolderCheckPreview?.blockers ?? [],
      warnings: input.officialFolderCheckPreview?.warnings ?? [],
    };
  }
  if (checkStatus === "conflict") {
    return {
      key: "local_project_folder",
      title: "Local project folder",
      statusLabel: "Conflict",
      status: "blocked",
      summary: "Review the local folder conflict before continuing.",
      detailKind: "folder",
      blockers: input.officialFolderCheckPreview?.blockers ?? [],
      warnings: input.officialFolderCheckPreview?.warnings ?? [],
    };
  }
  return {
    key: "local_project_folder",
    title: "Local project folder",
    statusLabel: "Created",
    status: "ready",
    summary: "The local DL folder and Official project folder are available.",
    detailKind: "folder",
    blockers: [],
    warnings: input.officialFolderCheckPreview?.warnings ?? [],
  };
}

function deriveRequestMaterialTask(
  input: ProjectFolderTaskSelectorInput
): ProjectFolderTaskRow {
  const status = input.requestMaterialPreview?.status ?? null;
  const blockers = [
    ...(input.requestMaterialPreview?.blockers ?? []),
    ...(input.requestMaterialError ? [input.requestMaterialError] : []),
  ];
  const warnings = input.requestMaterialPreview?.warnings ?? [];
  if (status === "collected") {
    return baseTask("request_material", "Request material", "Collected", "ready", {
      summary: "Original request files and controlled Submitted Material copies are recorded.",
      detailKind: "request_material",
      blockers,
      warnings,
    });
  }
  if (status === "ready" || status === "partial") {
    return baseTask(
      "request_material",
      "Request material",
      status === "ready" ? "Ready to collect" : "Partial",
      "warning",
      {
        summary:
          status === "ready"
            ? "Request files can be copied into Source Book and Submitted Material."
            : "Some request material can be collected, with remaining gaps still visible.",
        actionLabel: "Collect request material",
        actionTarget: "request_material",
        detailKind: "request_material",
        blockers,
        warnings,
      }
    );
  }
  if (status === "review_required") {
    return baseTask("request_material", "Request material", "Needs review", "warning", {
      summary: "Review undecided attachments before placing them in Submitted Material.",
      detailKind: "request_material",
      blockers,
      warnings,
    });
  }
  if (status === "blocked" || status === "conflict") {
    return baseTask("request_material", "Request material", "Needs review", "blocked", {
      summary: "Resolve the request material blocker before collecting files.",
      detailKind: "request_material",
      blockers,
      warnings,
    });
  }
  return baseTask("request_material", "Request material", "Not checked", "neutral", {
    summary: "Refresh request material after the local project folder is available.",
    detailKind: "request_material",
    blockers,
    warnings,
  });
}

function deriveConfirmedFeeAuthorityTask(
  input: ProjectFolderTaskSelectorInput
): ProjectFolderTaskRow {
  if (input.confirmedFeeAuthorityStatus === "confirmed") {
    return baseTask(
      "confirmed_fee_authority",
      "Confirmed Fee authority",
      "Confirmed",
      "ready",
      {
        summary: "The business fee authority is confirmed for the active Matrix.",
        detailKind: "fee_authority",
      }
    );
  }
  if (input.confirmedFeeAuthorityStatus === "stale") {
    return baseTask(
      "confirmed_fee_authority",
      "Confirmed Fee authority",
      "Stale",
      "blocked",
      {
        summary: "Confirmed Fee authority is stale for the active Matrix.",
        actionLabel: "Open Fee Evaluation",
        actionTarget: "fee",
        detailKind: "fee_authority",
      }
    );
  }
  return baseTask(
    "confirmed_fee_authority",
    "Confirmed Fee authority",
    input.confirmedFeeAuthorityStatus === "unknown" ? "Not checked" : "Missing",
    input.confirmedFeeAuthorityStatus === "unknown" ? "neutral" : "blocked",
    {
      summary: "Confirm Fee authority before treating generated Fee forms as controlled.",
      actionLabel: "Open Fee Evaluation",
      actionTarget: "fee",
      detailKind: "fee_authority",
    }
  );
}

function deriveRequiredFormsTask(
  input: ProjectFolderTaskSelectorInput
): ProjectFolderTaskRow {
  const preview = input.requiredFormsPreview;
  const blockers = [
    ...(preview?.blockers ?? []),
    ...(input.requiredFormsError ? [input.requiredFormsError] : []),
  ];
  const warnings = preview?.warnings ?? [];

  if (!input.matrixAuthorityReady) {
    return baseTask("required_forms", "Required forms", "Blocked", "blocked", {
      summary: "Confirm Matrix authority before generating Required forms.",
      detailKind: "required_forms",
      blockers: ["Confirmed Matrix authority is required before Required forms."],
      warnings,
    });
  }

  if (input.confirmedFeeAuthorityStatus !== "confirmed") {
    return baseTask("required_forms", "Required forms", "Blocked", "blocked", {
      summary: "Confirm Fee authority before generating Required forms.",
      detailKind: "required_forms",
      blockers: ["Current Confirmed Fee authority is required before Required forms."],
      warnings,
    });
  }

  if (preview?.status === "conflict" || preview?.status === "blocked") {
    return baseTask(
      "required_forms",
      "Required forms",
      preview.status === "conflict" ? "Conflict" : "Blocked",
      "blocked",
      {
        summary:
          preview.items.find((item) => item.status === "conflict" || item.status === "blocked")
            ?.message ?? "Resolve Required forms blockers before generating controlled files.",
        detailKind: "required_forms",
        blockers,
        warnings,
      }
    );
  }

  if (preview?.status === "current") {
    return baseTask("required_forms", "Required forms", "Current", "ready", {
      summary: `${formatRequiredFormsList(preview)} are current.`,
      detailKind: "required_forms",
      blockers,
      warnings,
    });
  }

  if (preview?.status === "ready") {
    const readyItems = preview.items.filter((item) =>
      item.action === "generate" || item.action === "update"
    );
    return baseTask("required_forms", "Required forms", "Ready to generate", "warning", {
      summary:
        readyItems.length > 0
          ? `${formatRequiredFormsList({ ...preview, items: readyItems })} need controlled generation.`
          : "Required forms preview is ready for review.",
      actionLabel: "Generate required forms",
      actionTarget: "required_forms_generate",
      detailKind: "required_forms",
      blockers,
      warnings,
    });
  }

  if (input.requiredFormsError) {
    return baseTask("required_forms", "Required forms", "Not checked", "neutral", {
      summary: "Refresh Required forms before generating controlled output files.",
      actionLabel: "Refresh required forms",
      actionTarget: "required_forms_refresh",
      detailKind: "required_forms",
      blockers,
      warnings,
    });
  }

  const outputs = input.versionStatus.downstream.filter((item) =>
    item.key === "test_record" || item.key === "fee_evaluation"
  );
  const missingOrStale = outputs.filter((item) =>
    item.freshness === "missing" || item.freshness === "stale" || item.freshness === "failed"
  );
  if (outputs.length === 0) {
    return baseTask("required_forms", "Required forms", "Deferred", "warning", {
      summary: "Required form output status is not available yet.",
      detailKind: "required_forms",
    });
  }
  if (missingOrStale.length > 0) {
    return baseTask("required_forms", "Required forms", "Missing files", "warning", {
      summary: `${missingOrStale.map((item) => item.label).join(", ")} need generated output review.`,
      detailKind: "required_forms",
      warnings: missingOrStale.map((item) => item.reason),
    });
  }
  return baseTask("required_forms", "Required forms", "Ready", "ready", {
    summary: "Required generated form outputs are current.",
    detailKind: "required_forms",
  });
}

function formatRequiredFormsList(preview: Pick<ProjectFolderRequiredFormsPreview, "items">): string {
  return preview.items.map((item) => item.label).join(", ");
}

function deriveSection2Task(input: ProjectFolderTaskSelectorInput): ProjectFolderTaskRow {
  const status = input.section2SyncPreview?.status ?? null;
  if (status === "synced" || status === "up_to_date") {
    return baseTask("section2", "Application Form Section 2", "Written", "ready", {
      summary: "Application Form Section 2 is aligned with current project dates.",
      detailKind: "section2",
    });
  }
  if (status === "ready" || status === "partial") {
    return baseTask("section2", "Application Form Section 2", "Preview ready", "warning", {
      summary: "Review and write Application Form Section 2 dates through the approved flow.",
      detailKind: "section2",
    });
  }
  if (status === "blocked") {
    return baseTask("section2", "Application Form Section 2", "Blocked", "blocked", {
      summary: "Resolve Section 2 blockers before write-back.",
      detailKind: "section2",
    });
  }
  return baseTask("section2", "Application Form Section 2", "Not updated", "neutral", {
    summary: "Section 2 write-back status is not checked yet.",
    detailKind: "section2",
  });
}

function deriveSubmittedMaterialTask(
  input: ProjectFolderTaskSelectorInput
): ProjectFolderTaskRow {
  const item = input.officialFolderCheckPreview?.required_files.find(
    (file) => file.key === "submitted_material"
  );
  if (!item) {
    return baseTask("submitted_material", "Submitted Material", "Not checked", "neutral", {
      summary: "Submitted Material readiness is not checked yet.",
      actionLabel: "Check Submitted Material",
      actionTarget: "official_folder_refresh",
      detailKind: "submitted_material",
    });
  }
  if (item.status === "ready") {
    return baseTask("submitted_material", "Submitted Material", "Ready", "ready", {
      summary: item.message,
      detailKind: "submitted_material",
    });
  }
  return baseTask(
    "submitted_material",
    "Submitted Material",
    item.status === "warning" || item.status === "deferred" ? "Needs review" : "Missing files",
    item.status === "missing" ? "blocked" : "warning",
    {
      summary: item.message,
      actionLabel: "Check Submitted Material",
      actionTarget: "official_folder_refresh",
      detailKind: "submitted_material",
      blockers: item.status === "missing" ? [item.message] : [],
      warnings: item.status === "warning" || item.status === "deferred" ? [item.message] : [],
    }
  );
}

function derivePublicDriveUploadTask(
  input: ProjectFolderTaskSelectorInput
): ProjectFolderTaskRow {
  const status = input.publicDriveUploadPreview?.status ?? null;
  const blockers = [
    ...(input.publicDriveUploadPreview?.blockers ?? []),
    ...(input.publicDriveUploadError ? [input.publicDriveUploadError] : []),
  ];
  const warnings = input.publicDriveUploadPreview?.warnings ?? [];
  if (status === "current") {
    return baseTask("public_drive_upload", "Public drive upload", "Already current", "ready", {
      summary: "The public Project Folder matches the local Official project folder.",
      detailKind: "public_drive",
      blockers,
      warnings,
    });
  }
  if (status === "ready" || status === "warning") {
    return baseTask(
      "public_drive_upload",
      "Public drive upload",
      status === "ready" ? "Ready to upload" : "Warning",
      "warning",
      {
        summary: "Review public-drive target changes before uploading.",
        actionLabel: "Upload to public drive",
        actionTarget: "public_drive_upload",
        detailKind: "public_drive",
        blockers,
        warnings,
      }
    );
  }
  if (status === "conflict" || status === "blocked") {
    return baseTask(
      "public_drive_upload",
      "Public drive upload",
      status === "conflict" ? "Conflict" : "Blocked",
      "blocked",
      {
        summary: "Resolve public-drive blockers before upload.",
        detailKind: "public_drive",
        blockers,
        warnings,
      }
    );
  }
  return baseTask("public_drive_upload", "Public drive upload", "Not checked", "neutral", {
    summary: "Refresh public-drive preview when the Project Folder is ready.",
    actionLabel: "Refresh public-drive preview",
    actionTarget: "public_drive_refresh",
    detailKind: "public_drive",
    blockers,
    warnings,
  });
}

function baseTask(
  key: ProjectFolderTaskKey,
  title: string,
  statusLabel: string,
  status: ProjectFolderTaskStatus,
  options: {
    summary: string;
    detailKind: ProjectFolderTaskRow["detailKind"];
    actionLabel?: string;
    actionTarget?: ProjectFolderTaskActionTarget;
    blockers?: string[];
    warnings?: string[];
  }
): ProjectFolderTaskRow {
  return {
    key,
    title,
    statusLabel,
    status,
    summary: options.summary,
    actionLabel: options.actionLabel,
    actionTarget: options.actionTarget ?? null,
    detailKind: options.detailKind,
    blockers: options.blockers ?? [],
    warnings: options.warnings ?? [],
  };
}
