import { describe, expect, it } from "vitest";
import type {
  OfficialFolderCheckPreview,
  ProjectFolderRequiredFormsPreview,
  PublicDriveUploadPreview,
  RequestMaterialPreview,
} from "../../api/client";
import {
  deriveProjectFolderTasks,
  selectCurrentProjectFolderTaskKey,
} from "./projectFolderTaskSelectors";
import type { WorkbenchVersionStatus } from "./projectWorkbenchVersionSelectors";

describe("deriveProjectFolderTasks", () => {
  it("returns the fixed Project Folder task order with operator-facing labels", () => {
    const tasks = deriveProjectFolderTasks({
      folderReady: true,
      matrixAuthorityReady: true,
      officialFolderCheckPreview: readyOfficialFolderCheckPreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
      requestMaterialError: null,
      publicDriveUploadPreview: currentPublicDriveUploadPreview,
      publicDriveUploadError: null,
      requiredFormsPreview: currentRequiredFormsPreview,
      requiredFormsError: null,
      section2SyncPreview: syncedSection2Preview,
      versionStatus: readyVersionStatus,
      confirmedFeeAuthorityStatus: "confirmed",
    });

    expect(tasks.map((task) => task.title)).toEqual([
      "Local project folder",
      "Request material",
      "Confirmed Fee authority",
      "Required forms",
      "Application Form Section 2",
      "Submitted Material",
      "Public drive upload",
    ]);
    expect(tasks.map((task) => task.title).join(" ")).not.toMatch(
      /Package|Workspace|manifest|SQLite/
    );
  });

  it("selects Request material when manual review is required", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      requestMaterialPreview: {
        ...collectedRequestMaterialPreview,
        status: "review_required",
        warnings: ["Review undecided attachments before placing them in Submitted Material."],
      },
    });

    expect(selectCurrentProjectFolderTaskKey(tasks)).toBe("request_material");
    expect(taskByTitle(tasks, "Request material").actionTarget).toBeNull();
  });

  it("keeps Confirmed Fee authority separate from generated Fee form output", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      confirmedFeeAuthorityStatus: "confirmed",
      versionStatus: {
        activeDraftVersion: 1,
        trackedDraftVersion: 1,
        hasStaleOutputs: false,
        downstream: [
          {
            key: "fee_evaluation",
            label: "Fee form",
            freshness: "missing",
            path: null,
            reason: "Fee form has not been generated.",
          },
        ],
      },
      requiredFormsPreview: {
        ...currentRequiredFormsPreview,
        status: "ready",
        items: [
          {
            key: "test_record",
            label: "Test Record",
            target_path: "D:/Projects/Submitted Material/test-record.docx",
            status: "current",
            action: "skip",
            message: "Test Record is current.",
          },
          {
            key: "fee_form",
            label: "Fee Form",
            target_path: "D:/Projects/fee.xls",
            status: "ready",
            action: "generate",
            message: "Fee Form can be generated.",
          },
          {
            key: "customer_feedback_form",
            label: "Customer Feedback Form",
            target_path: "D:/Projects/customer-feedback.xlsx",
            status: "current",
            action: "skip",
            message: "Customer Feedback Form is current.",
          },
        ],
      },
    });

    expect(taskByTitle(tasks, "Confirmed Fee authority").statusLabel).toBe("Confirmed");
    expect(taskByTitle(tasks, "Required forms").summary).toMatch(/Fee Form/);
    expect(taskByTitle(tasks, "Required forms").status).not.toBe("ready");
    expect(taskByTitle(tasks, "Required forms").actionTarget).toBe(
      "required_forms_generate"
    );
  });

  it("uses Required forms preview to show current controlled forms", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      requiredFormsPreview: currentRequiredFormsPreview,
    });

    expect(taskByTitle(tasks, "Required forms").statusLabel).toBe("Current");
    expect(taskByTitle(tasks, "Required forms").status).toBe("ready");
    expect(taskByTitle(tasks, "Required forms").summary).toMatch(/Test Record/);
    expect(taskByTitle(tasks, "Required forms").summary).toMatch(/Fee Form/);
    expect(taskByTitle(tasks, "Required forms").summary).toMatch(
      /Customer Feedback Form/
    );
  });

  it("blocks Required forms when Matrix authority is not current", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      matrixAuthorityReady: false,
      requiredFormsPreview: currentRequiredFormsPreview,
    });

    expect(taskByTitle(tasks, "Required forms").status).toBe("blocked");
    expect(taskByTitle(tasks, "Required forms").actionTarget).toBeNull();
    expect(taskByTitle(tasks, "Required forms").summary).toMatch(/Matrix/);
  });

  it("blocks Required forms when Confirmed Fee authority is missing or stale", () => {
    for (const confirmedFeeAuthorityStatus of ["missing", "stale"] as const) {
      const tasks = deriveProjectFolderTasks({
        ...readyInput(),
        confirmedFeeAuthorityStatus,
        requiredFormsPreview: currentRequiredFormsPreview,
      });

      expect(taskByTitle(tasks, "Required forms").status).toBe("blocked");
      expect(taskByTitle(tasks, "Required forms").actionTarget).toBeNull();
      expect(taskByTitle(tasks, "Required forms").summary).toMatch(/Fee/);
    }
  });

  it("blocks Required forms when the generation preview has a conflict", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      requiredFormsPreview: {
        ...currentRequiredFormsPreview,
        status: "conflict",
        blockers: ["Fee Form target was changed manually."],
        items: [
          {
            key: "fee_form",
            label: "Fee Form",
            target_path: "D:/Projects/fee.xls",
            status: "conflict",
            action: "conflict",
            message: "Fee Form target was changed manually.",
          },
        ],
      },
    });

    expect(selectCurrentProjectFolderTaskKey(tasks)).toBe("required_forms");
    expect(taskByTitle(tasks, "Required forms").status).toBe("blocked");
    expect(taskByTitle(tasks, "Required forms").actionTarget).toBeNull();
  });

  it("selects Public drive upload only after prior Project Folder tasks are ready", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      publicDriveUploadPreview: readyPublicDriveUploadPreview,
    });

    expect(selectCurrentProjectFolderTaskKey(tasks)).toBe("public_drive_upload");
    expect(taskByTitle(tasks, "Public drive upload").actionTarget).toBe(
      "public_drive_upload"
    );
  });

  it("keeps Required forms current when forms are missing even if public drive upload is ready", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      requiredFormsPreview: {
        ...currentRequiredFormsPreview,
        status: "ready",
        items: [
          {
            key: "fee_form",
            label: "Fee Form",
            target_path: "D:/Projects/fee.xls",
            status: "ready",
            action: "generate",
            message: "Fee Form can be generated.",
          },
        ],
      },
      publicDriveUploadPreview: readyPublicDriveUploadPreview,
    });

    expect(selectCurrentProjectFolderTaskKey(tasks)).toBe("required_forms");
  });

  it("keeps Section 2 current when write-back is pending even if public drive upload is ready", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      section2SyncPreview: {
        ...syncedSection2Preview,
        status: "ready",
      },
      publicDriveUploadPreview: readyPublicDriveUploadPreview,
    });

    expect(selectCurrentProjectFolderTaskKey(tasks)).toBe("section2");
  });
});

function taskByTitle(
  tasks: ReturnType<typeof deriveProjectFolderTasks>,
  title: string
): ReturnType<typeof deriveProjectFolderTasks>[number] {
  const task = tasks.find((item) => item.title === title);
  if (!task) {
    throw new Error(`Missing task ${title}`);
  }
  return task;
}

function readyInput() {
  return {
    folderReady: true,
    matrixAuthorityReady: true,
    officialFolderCheckPreview: readyOfficialFolderCheckPreview,
    requestMaterialPreview: collectedRequestMaterialPreview,
    requestMaterialError: null,
    publicDriveUploadPreview: currentPublicDriveUploadPreview,
    publicDriveUploadError: null,
    requiredFormsPreview: currentRequiredFormsPreview,
    requiredFormsError: null,
    section2SyncPreview: syncedSection2Preview,
    versionStatus: readyVersionStatus,
    confirmedFeeAuthorityStatus: "confirmed" as const,
  };
}

const readyVersionStatus: WorkbenchVersionStatus = {
  activeDraftVersion: 1,
  trackedDraftVersion: 1,
  hasStaleOutputs: false,
  downstream: [
    {
      key: "test_record",
      label: "Test Record",
      freshness: "current",
      path: "D:/Projects/test-record.docx",
      reason: "Test Record is current.",
    },
    {
      key: "fee_evaluation",
      label: "Fee form",
      freshness: "current",
      path: "D:/Projects/fee.xlsx",
      reason: "Fee form is current.",
    },
  ],
};

const currentRequiredFormsPreview: ProjectFolderRequiredFormsPreview = {
  project_id: "project-1",
  status: "current",
  official_project_folder_path:
    "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  confirmed_matrix_id: "matrix-1",
  confirmed_revision: 1,
  confirmed_fee_id: "fee-1",
  confirmed_fee_revision: 1,
  confirmed_fee_pricing_draft_edit_id: "pricing-1",
  customer_feedback_template_path: "D:/Source/Template/Customer Feedback.xlsx",
  items: [
    {
      key: "test_record",
      label: "Test Record",
      target_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/DL-2026-06-001_Test_Record.docx",
      status: "current",
      action: "skip",
      message: "Test Record is current.",
    },
    {
      key: "fee_form",
      label: "Fee Form",
      target_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/DL-2026-06-001_Fee_Form.xls",
      status: "current",
      action: "skip",
      message: "Fee Form is current.",
    },
    {
      key: "customer_feedback_form",
      label: "Customer Feedback Form",
      target_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/DL-2026-06-001_Customer_Feedback_Form.xlsx",
      status: "current",
      action: "skip",
      message: "Customer Feedback Form is current.",
    },
  ],
  blockers: [],
  warnings: [],
};

const syncedSection2Preview = {
  project_id: "project-1",
  application_form_id: "application-1",
  confirmed_matrix_id: "CM1",
  confirmed_revision: 1,
  fields: [],
  status: "synced" as const,
};

const collectedRequestMaterialPreview: RequestMaterialPreview = {
  project_id: "project-1",
  local_workspace_path: "D:/Projects/DL-2026-06-001",
  source_book_path: "D:/Projects/DL-2026-06-001/Source Book",
  official_project_folder_path:
    "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  status: "collected",
  items: [
    {
      source_asset_id: "asset-1",
      source_asset_type: "application_form",
      source_role: "selected_application_form",
      source_name: "application.docx",
      source_path: "D:/Intake/application.docx",
      dedupe_key: "path:d:/intake/application.docx",
      target_area: "submitted_material",
      target_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/application.docx",
      action: "none",
      status: "copied",
      message: "Copied.",
      review_required: false,
      size_bytes: 100,
      sha256: "a".repeat(64),
    },
  ],
  blockers: [],
  warnings: [],
};

const readyOfficialFolderCheckPreview: OfficialFolderCheckPreview = {
  project_id: "project-1",
  status: "ready",
  local_workspace_path: "D:/Projects/DL-2026-06-001",
  official_project_folder_path:
    "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  required_folders: [],
  required_files: [
    {
      key: "submitted_material",
      label: "Submitted Material",
      kind: "file",
      status: "ready",
      path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/application.docx",
      message: "Confirmed collected files are present.",
      repairable: false,
    },
  ],
  blockers: [],
  warnings: [],
  next_action: "none",
};

const currentPublicDriveUploadPreview: PublicDriveUploadPreview = {
  project_id: "project-1",
  status: "current",
  local_official_folder_path:
    "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  public_project_folder_path:
    "D:/PublicProjects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  items: [],
  blockers: [],
  warnings: [],
  counts: {
    add: 0,
    update: 0,
    skip: 2,
    conflict: 0,
    deferred: 0,
  },
  next_action: "none",
};

const readyPublicDriveUploadPreview: PublicDriveUploadPreview = {
  ...currentPublicDriveUploadPreview,
  status: "ready",
  items: [
    {
      kind: "file",
      relative_path: "Submitted Material/application.docx",
      local_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/application.docx",
      public_path:
        "D:/PublicProjects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/application.docx",
      action: "add",
      status: "ready",
      message: "Ready to add.",
    },
  ],
  counts: {
    add: 1,
    update: 0,
    skip: 0,
    conflict: 0,
    deferred: 0,
  },
  next_action: "upload",
};
