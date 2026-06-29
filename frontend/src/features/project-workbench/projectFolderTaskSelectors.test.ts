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
    expect(selectCurrentProjectFolderTaskKey(tasks)).toBe("project_folder");
  });

  it("keeps backend-dependent operations as non-executing placeholders", () => {
    const tasks = deriveProjectFolderTasks(readyInput());

    expect(tasks.every((task) => task.actionTarget === null)).toBe(true);
    expect(tasks.map((task) => task.blockers[0])).toEqual([
      "Project folder open is not connected yet.",
      "Sync workflow is not connected yet.",
      "Submit workflow is not connected yet.",
      "Pull workflow is not connected yet.",
    ]);
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
    });

    expect(tasks[0].title).toBe("Project folder");
    expect(tasks[0].blockers[0]).toBe("Project folder is not available yet.");
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
