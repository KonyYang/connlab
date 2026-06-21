import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useProjectWorkbenchModel } from "./useProjectWorkbenchModel";

const MockApiRequestError = vi.hoisted(
  () =>
    class MockApiRequestError extends Error {
      status: number;

      constructor(status: number, message: string) {
        super(message);
        this.status = status;
      }
    }
);

const apiMocks = vi.hoisted(() => ({
  collectRequestMaterial: vi.fn(),
  confirmProjectTestPlanMatrixDraft: vi.fn(),
  createProjectTestPlanDraft: vi.fn(),
  executeApprovalPackage: vi.fn(),
  fetchActiveConfirmedMatrixSnapshot: vi.fn(),
  fetchConfirmedMatrixRuntimeProjectionSnapshot: vi.fn(),
  fetchOfficialFolderCheck: vi.fn(),
  fetchOfficialWorkspacePreview: vi.fn(),
  fetchProjectBasicInformation: vi.fn(),
  fetchProjectFolderRequiredFormsPreview: vi.fn(),
  fetchProjectPackagePreview: vi.fn(),
  fetchProjectSection2SyncPreview: vi.fn(),
  fetchPublicDriveUploadPreview: vi.fn(),
  fetchRequestMaterialPreview: vi.fn(),
  generateProjectFolderRequiredForms: vi.fn(),
  getConfirmedFeeLatest: vi.fn(),
  getLatestProjectFolder: vi.fn(),
  getProject: vi.fn(),
  getProjectOutputStatusSummary: vi.fn(),
  getProjectTestPlanDraft: vi.fn(),
  getRuntimeProjectionReadOnlySnapshot: vi.fn(),
  listExternalResources: vi.fn(),
  listProjectLtrs: vi.fn(),
  listProjectTestPlanDrafts: vi.fn(),
  listProjectTestPlanSourceCandidates: vi.fn(),
  placeEvidence: vi.fn(),
  previewApprovalPackage: vi.fn(),
  previewEvidencePlacement: vi.fn(),
  previewProjectTestPlanMatrixFromPath: vi.fn(),
  previewProjectTestPlanMatrixFromSourceCandidate: vi.fn(),
  repairOfficialFolderStructure: vi.fn(),
  syncProjectSection2FromConfirmedMatrix: vi.fn(),
  updateProjectTestPlanMatrixDraft: vi.fn(),
  uploadPublicDriveProjectFolder: vi.fn(),
  validateProjectTestPlanMatrixDraft: vi.fn(),
  writeBackProjectApplicationForm: vi.fn(),
  createOfficialWorkspace: vi.fn(),
}));

vi.mock("../../api/client", () => ({
  ApiRequestError: MockApiRequestError,
  ...apiMocks,
}));

describe("useProjectWorkbenchModel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiMocks.getProject.mockResolvedValue({
      project_id: "project-1",
      product_name: "Connector Sample",
      requestor: "Lab User",
      status: "active",
    });
    apiMocks.listProjectLtrs.mockResolvedValue([]);
    apiMocks.listExternalResources.mockResolvedValue([]);
    apiMocks.getLatestProjectFolder.mockResolvedValue({
      project_folder_path: "D:/Projects/DL-2026-06-001",
    });
    apiMocks.getProjectOutputStatusSummary.mockResolvedValue({
      project_id: "project-1",
      items: [],
      has_stale_outputs: false,
    });
    apiMocks.getConfirmedFeeLatest.mockResolvedValue({
      status: "current",
      current_confirmed_matrix_id: "CM1",
      current_confirmed_revision: 1,
      current_fee_rule_version_id: "fee-rule-1",
      fee_review_required_count: 0,
      confirmed_fee: null,
    });
    apiMocks.fetchActiveConfirmedMatrixSnapshot.mockResolvedValue(null);
    apiMocks.getProjectTestPlanDraft.mockRejectedValue(
      new MockApiRequestError(404, "No Matrix draft")
    );
    apiMocks.listProjectTestPlanDrafts.mockResolvedValue({ drafts: [] });
    apiMocks.fetchProjectSection2SyncPreview.mockResolvedValue({
      project_id: "project-1",
      status: "blocked",
      blockers: [],
      warnings: [],
    });
    apiMocks.fetchProjectPackagePreview.mockResolvedValue({
      project_id: "project-1",
      status: "ready",
      project_folder: { status: "ready", path: "D:/Projects", message: "Ready." },
      authority_context: {},
      required_items: [],
      optional_items: [],
      blockers: [],
      warnings: [],
    });
    apiMocks.fetchOfficialWorkspacePreview.mockResolvedValue({
      project_id: "project-1",
      dl_number: "DL-2026-06-001",
      status: "completed",
      local_workspace_root: "D:/Projects",
      local_workspace_path: "D:/Projects/DL-2026-06-001",
      source_book_path: "D:/Projects/DL-2026-06-001/Source Book",
      template_path: "D:/Template",
      official_project_folder_path: "D:/Projects/DL-2026-06-001/Official",
      manifest_path: "D:/Projects/DL-2026-06-001/.connlab/manifest.json",
      template_root_mode: "template_root",
      blockers: [],
      warnings: [],
      planned_paths: [],
    });
    apiMocks.fetchRequestMaterialPreview.mockResolvedValue({
      project_id: "project-1",
      status: "collected",
      local_workspace_path: "D:/Projects/DL-2026-06-001",
      source_book_path: "D:/Projects/DL-2026-06-001/Source Book",
      official_project_folder_path: "D:/Projects/DL-2026-06-001/Official",
      items: [],
      blockers: [],
      warnings: [],
    });
    apiMocks.fetchProjectFolderRequiredFormsPreview.mockResolvedValue(
      blockedRequiredFormsPreview
    );
    apiMocks.fetchOfficialFolderCheck.mockResolvedValue({
      project_id: "project-1",
      status: "ready",
      local_workspace_path: "D:/Projects/DL-2026-06-001",
      official_project_folder_path: "D:/Projects/DL-2026-06-001/Official",
      required_folders: [],
      required_files: [],
      blockers: [],
      warnings: [],
      next_action: "none",
    });
    apiMocks.fetchPublicDriveUploadPreview.mockResolvedValue({
      project_id: "project-1",
      status: "ready",
      public_project_folder_path: "D:/Public/DL-2026-06-001",
      counts: {},
      items: [],
      blockers: [],
      warnings: [],
    });
    apiMocks.fetchProjectBasicInformation.mockResolvedValue({
      project_id: "project-1",
      status: "unconfirmed",
      draft: { values: {} },
      latest_confirmed: null,
      field_suggestions: {},
      changed_source_fields: [],
      missing_required_fields: ["project_leader"],
      missing_required_labels: ["Project Leader"],
      blockers: [],
      warnings: [],
    });
    apiMocks.listProjectTestPlanSourceCandidates.mockResolvedValue({
      candidates: [],
      warnings: [],
    });
    apiMocks.createOfficialWorkspace.mockResolvedValue({
      project_id: "project-1",
      status: "completed",
      local_workspace_path: "D:/Projects/DL-2026-06-001",
      official_project_folder_path: "D:/Projects/DL-2026-06-001/Official",
      manifest_path: "D:/Projects/DL-2026-06-001/.connlab/manifest.json",
      copied_paths: [],
      skipped_paths: [],
      warnings: [],
    });
    apiMocks.collectRequestMaterial.mockResolvedValue({
      project_id: "project-1",
      status: "collected",
      local_workspace_path: "D:/Projects/DL-2026-06-001",
      source_book_path: "D:/Projects/DL-2026-06-001/Source Book",
      official_project_folder_path: "D:/Projects/DL-2026-06-001/Official",
      items: [],
      blockers: [],
      warnings: [],
      collection_id: "collection-1",
      copied_paths: [],
      already_present_paths: [],
      skipped_paths: [],
      missing_source_paths: [],
      conflict_paths: [],
    });
  });

  it("stops the one-click project folder chain when Required forms preview is blocked", async () => {
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));
    const section2CallsBefore = apiMocks.fetchProjectSection2SyncPreview.mock.calls.length;
    const packageCallsBefore = apiMocks.fetchProjectPackagePreview.mock.calls.length;
    const publicDriveCallsBefore = apiMocks.fetchPublicDriveUploadPreview.mock.calls.length;

    await act(async () => {
      await result.current.onCreateOfficialWorkspace();
    });

    await waitFor(() =>
      expect(result.current.message).toBe(
        "Project folder update blocked: Confirm Basic Information before generating Project Folder outputs."
      )
    );
    expect(result.current.requiredFormsError).toBe(
      "Confirm Basic Information before generating Project Folder outputs."
    );
    expect(apiMocks.generateProjectFolderRequiredForms).not.toHaveBeenCalled();
    expect(apiMocks.writeBackProjectApplicationForm).not.toHaveBeenCalled();
    expect(apiMocks.fetchProjectSection2SyncPreview).toHaveBeenCalledTimes(
      section2CallsBefore
    );
    expect(apiMocks.fetchProjectPackagePreview).toHaveBeenCalledTimes(
      packageCallsBefore
    );
    expect(apiMocks.fetchPublicDriveUploadPreview).toHaveBeenCalledTimes(
      publicDriveCallsBefore
    );
  });
});

const blockedRequiredFormsPreview = {
  project_id: "project-1",
  status: "blocked",
  official_project_folder_path: null,
  confirmed_matrix_id: null,
  confirmed_revision: null,
  confirmed_fee_id: null,
  confirmed_fee_revision: null,
  confirmed_fee_pricing_draft_edit_id: null,
  confirmed_basic_information_version: null,
  confirmed_basic_information_source_signature_hash: null,
  customer_feedback_template_path: null,
  items: [],
  blockers: ["Confirm Basic Information before generating Project Folder outputs."],
  warnings: [],
};
