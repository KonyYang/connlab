import { describe, expect, it } from "vitest";
import type { ProjectFolderRequiredFormsPreview } from "../../api/client";
import {
  deriveProjectFolderTasks,
  selectCurrentProjectFolderTaskKey,
  selectProjectFolderOneClickBlocker,
} from "./projectFolderTaskSelectors";
import type { WorkbenchVersionStatus } from "./projectWorkbenchVersionSelectors";

describe("deriveProjectFolderTasks", () => {
  it("returns the quiet four-operation Folder Actions model", () => {
    const tasks = deriveProjectFolderTasks(readyInput());

    expect(tasks.map((task) => task.title)).toEqual([
      "Project folder",
      "Public working copy",
      "Approval package",
      "Approved folder",
    ]);
    expect(tasks.map((task) => task.actionLabel)).toEqual([
      "Open",
      "Sync now",
      "Submit",
      "Pull",
    ]);
    expect(tasks.map((task) => task.iconName)).toEqual([
      "folder",
      "cloud-sync",
      "folder-move",
      "download",
    ]);
    expect(tasks.map((task) => task.context)).toEqual([
      "D:/Test Project/DL-2026-06-001",
      "D:/PublicProject/Open/2026/DL-2026-06-001",
      "Preview required before moving the package.",
      "D:/PublicProject/Closed/2026/DL-2026-06-001 · keep local history",
    ]);
    expect(selectCurrentProjectFolderTaskKey(tasks)).toBe("project_folder");
  });

  it("wires workflow operations as preview-first actions", () => {
    const tasks = deriveProjectFolderTasks(readyInput());

    expect(tasks.map((task) => task.actionTarget)).toEqual([
      "project_folder_open",
      "public_folder_workflow_sync",
      "public_folder_workflow_submit",
      "public_folder_workflow_pull",
    ]);
    expect(tasks[1].autoSync).toMatchObject({
      checked: true,
      disabled: false,
    });
  });

  it("does not expose old readiness or public upload vocabulary", () => {
    const text = JSON.stringify(deriveProjectFolderTasks(readyInput()));

    expect(text).not.toMatch(
      /Request material|Source Book|Public drive upload|Ready to upload|Already current|Upload to public drive|Refresh public-drive preview|Partial|Waiting|Not current/
    );
  });

  it("keeps the Basic Information folder blocker available for one-click folder commands", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      requiredFormsPreview: basicInformationBlockedRequiredFormsPreview,
    });

    expect(selectProjectFolderOneClickBlocker(tasks, true)).toBe(
      "Confirm Basic Information before generating Project Folder outputs."
    );
    expect(selectProjectFolderOneClickBlocker(tasks, false)).toBeNull();
  });

  it("uses a short unavailable blocker before the folder exists", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      folderReady: false,
      publicFolderWorkflowContext: {
        ...readyInput().publicFolderWorkflowContext,
        local_official_folder_path: null,
      },
    });

    expect(tasks[0].title).toBe("Project folder");
    expect(tasks[0].context).toBe("Project folder is not available yet.");
    expect(tasks[0].blockers[0]).toBe("Project folder is not available yet.");
    expect(tasks.slice(1).map((task) => task.actionTarget)).toEqual([null, null, null]);
    expect(tasks.slice(1).flatMap((task) => task.blockers)).toEqual([
      "Project folder is not available yet.",
      "Project folder is not available yet.",
      "Project folder is not available yet.",
    ]);
    expect(tasks[1].autoSync).toMatchObject({
      disabled: true,
      blocker: "Project folder is not available yet.",
    });
  });

  it("does not require legacy folderReady for project folder Open", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      folderReady: false,
    });

    expect(tasks[0]).toMatchObject({
      title: "Project folder",
      context: "D:/Test Project/DL-2026-06-001",
      actionLabel: "Open",
      actionTarget: "project_folder_open",
      blockers: [],
    });
  });

  it("disables project folder Open when workflow context has no local path", () => {
    const tasks = deriveProjectFolderTasks({
      ...readyInput(),
      publicFolderWorkflowContext: {
        ...readyInput().publicFolderWorkflowContext,
        local_official_folder_path: null,
      },
    });

    expect(tasks[0]).toMatchObject({
      title: "Project folder",
      context: "Project folder is not available yet.",
      actionTarget: null,
      blockers: ["Project folder is not available yet."],
    });
  });
});

function readyInput() {
  return {
    folderReady: true,
    matrixAuthorityReady: true,
    officialFolderCheckPreview: null,
    requestMaterialPreview: null,
    requestMaterialError: null,
    publicDriveUploadPreview: null,
    publicDriveUploadError: null,
    publicFolderWorkflowContext: {
      project_id: "project-1",
      auto_sync_enabled: true,
      sync_locked: false,
      submitted_at: null,
      public_root: "D:/PublicProject",
      public_root_class: "open",
      public_folder_year: 2026,
      year_source: "project",
      year_evidence: "created_on",
      local_official_folder_path: "D:/Test Project/DL-2026-06-001",
      public_open_path: "D:/PublicProject/Open/2026/DL-2026-06-001",
      public_closed_path: "D:/PublicProject/Closed/2026/DL-2026-06-001",
      blockers: [],
      warnings: [],
    },
    publicFolderWorkflowContextLoading: false,
    publicFolderWorkflowContextError: null,
    publicFolderWorkflowPreviews: { sync: null, submit: null, pull: null },
    publicFolderWorkflowResults: { sync: null, submit: null, pull: null },
    publicFolderWorkflowBusyOperation: null,
    publicFolderWorkflowConfirmingOperation: null,
    publicFolderWorkflowError: null,
    publicFolderWorkflowMessage: null,
    publicFolderWorkflowAutoSyncBusy: false,
    requiredFormsPreview: currentRequiredFormsPreview,
    requiredFormsError: null,
    section2SyncPreview: null,
    versionStatus: readyVersionStatus,
    confirmedFeeAuthorityStatus: "confirmed" as const,
  };
}

const readyVersionStatus: WorkbenchVersionStatus = {
  activeDraftVersion: 1,
  trackedDraftVersion: 1,
  hasStaleOutputs: false,
  downstream: [],
};

const currentRequiredFormsPreview: ProjectFolderRequiredFormsPreview = {
  project_id: "project-1",
  status: "current",
  official_project_folder_path: null,
  confirmed_matrix_id: "matrix-1",
  confirmed_revision: 1,
  confirmed_fee_id: "fee-1",
  confirmed_fee_revision: 1,
  confirmed_fee_pricing_draft_edit_id: "pricing-1",
  confirmed_basic_information_version: 1,
  confirmed_basic_information_source_signature_hash: "basic-hash",
  customer_feedback_template_path: "D:/Source/Template/Customer Feedback.xlsx",
  items: [],
  blockers: [],
  warnings: [],
};

const basicInformationBlockedRequiredFormsPreview: ProjectFolderRequiredFormsPreview = {
  ...currentRequiredFormsPreview,
  status: "blocked",
  confirmed_matrix_id: null,
  confirmed_revision: null,
  confirmed_fee_id: null,
  confirmed_fee_revision: null,
  confirmed_fee_pricing_draft_edit_id: null,
  confirmed_basic_information_version: null,
  confirmed_basic_information_source_signature_hash: null,
  customer_feedback_template_path: null,
  blockers: ["Confirm Basic Information before generating Project Folder outputs."],
};
