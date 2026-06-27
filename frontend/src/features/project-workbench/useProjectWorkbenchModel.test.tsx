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
  closeProjectAdministrativeLifecycle: vi.fn(),
  closeProjectCompletedLifecycle: vi.fn(),
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
  getProjectBasicInformation: vi.fn(),
  getProjectLifecycle: vi.fn(),
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
  resumeProjectLifecycle: vi.fn(),
  stopProjectLifecycle: vi.fn(),
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
    apiMocks.getProjectBasicInformation.mockResolvedValue({
      project_id: "project-1",
      status: "empty",
      draft: null,
      latest_confirmed: null,
      field_suggestions: {},
      changed_source_fields: [],
      missing_required_fields: [],
      missing_required_labels: [],
      blockers: [],
      warnings: [],
    });
    apiMocks.getProjectLifecycle.mockResolvedValue(lifecycleResponse());
    apiMocks.stopProjectLifecycle.mockResolvedValue(
      lifecycleResponse({
        lifecycle_state: "stopped",
        status: "cancelled",
        status_label: "Stopped",
        readonly: true,
        allowed_actions: ["resume", "close"],
      })
    );
    apiMocks.resumeProjectLifecycle.mockResolvedValue(lifecycleResponse());
    apiMocks.closeProjectCompletedLifecycle.mockResolvedValue(
      lifecycleResponse({
        lifecycle_state: "closed",
        closure_type: "completed",
        status: "closed",
        status_label: "Closed",
        readonly: true,
        allowed_actions: [],
      })
    );
    apiMocks.closeProjectAdministrativeLifecycle.mockResolvedValue(
      lifecycleResponse({
        lifecycle_state: "closed",
        closure_type: "administrative",
        status: "closed",
        status_label: "Closed",
        readonly: true,
        allowed_actions: [],
      })
    );
    apiMocks.listProjectLtrs.mockResolvedValue([]);
    apiMocks.listExternalResources.mockResolvedValue([]);
    apiMocks.getLatestProjectFolder.mockResolvedValue({
      project_folder_path: "D:/Projects/DL-2026-06-001",
    });
    apiMocks.getProjectOutputStatusSummary.mockResolvedValue({
      project_id: "project-1",
      active_draft_id: null,
      active_draft_version: null,
      items: [],
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
    apiMocks.writeBackProjectApplicationForm.mockResolvedValue({
      project_id: "project-1",
      target_path: "D:/Projects/DL-2026-06-001/Official/Submitted Material/request.docx",
      status: "updated",
      changed_fields: [],
      unchanged_fields: [],
      warnings: [],
      output_record_id: "application-form-output-1",
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

  it("generates project folder Required forms in separate timed batches", async () => {
    apiMocks.generateProjectFolderRequiredForms.mockImplementation(
      async (_projectId: string, request: { expected_targets: Array<{ key: string }> }) => {
        const key = request.expected_targets[0]?.key ?? "unknown";
        return {
          project_id: "project-1",
          status: "generated",
          official_project_folder_path: "D:/Projects/DL-2026-06-001/Official",
          items: [
            {
              key,
              label: key,
              target_path: `D:/Projects/DL-2026-06-001/Official/${key}`,
              status: "generated",
              source_path: `D:/Temp/${key}`,
              output_record_id: `${key}-output`,
              message: "Placed in the Official project folder.",
            },
          ],
          warnings: [],
          timings: [{ label: `${key}.generate`, elapsed_ms: 7 }],
        };
      }
    );
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));
    apiMocks.fetchProjectFolderRequiredFormsPreview
      .mockResolvedValueOnce(readyRequiredFormsPreview)
      .mockResolvedValueOnce(currentRequiredFormsPreview);

    await act(async () => {
      await result.current.onCreateOfficialWorkspace();
    });

    expect(apiMocks.generateProjectFolderRequiredForms).toHaveBeenCalledTimes(3);
    expect(
      apiMocks.generateProjectFolderRequiredForms.mock.calls.map(
        ([, request]) => request.expected_targets[0].key
      )
    ).toEqual(["customer_feedback_form", "fee_form", "test_record"]);
    expect(result.current.requiredFormsResult?.items.map((item) => item.key)).toEqual([
      "customer_feedback_form",
      "fee_form",
      "test_record",
    ]);
    expect(apiMocks.syncProjectSection2FromConfirmedMatrix).not.toHaveBeenCalled();
  });

  it("stops lifecycle in place and refreshes lifecycle plus project status", async () => {
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));
    apiMocks.getProject.mockResolvedValueOnce({
      project_id: "project-1",
      product_name: "Connector Sample",
      requestor: "Lab User",
      status: "cancelled",
    });

    await act(async () => {
      await result.current.onStopLifecycle("");
    });

    expect(apiMocks.stopProjectLifecycle).toHaveBeenCalledWith("project-1", {
      reason: null,
      operator: null,
    });
    expect(apiMocks.getProject).toHaveBeenCalledTimes(2);
    expect(result.current.project?.status).toBe("cancelled");
    expect(result.current.lifecycle?.lifecycle_state).toBe("stopped");
  });

  it("resumes lifecycle in place and refreshes legacy cancelled project status", async () => {
    apiMocks.getProject.mockResolvedValueOnce({
      project_id: "project-1",
      product_name: "Connector Sample",
      requestor: "Lab User",
      status: "cancelled",
    });
    apiMocks.getProjectLifecycle.mockResolvedValueOnce(
      lifecycleResponse({
        lifecycle_state: "stopped",
        status: "cancelled",
        status_label: "Stopped",
        readonly: true,
        allowed_actions: ["resume", "close"],
      })
    );
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(result.current.project?.status).toBe("cancelled"));
    apiMocks.getProject.mockResolvedValueOnce({
      project_id: "project-1",
      product_name: "Connector Sample",
      requestor: "Lab User",
      status: "active",
    });

    await act(async () => {
      await result.current.onResumeLifecycle("");
    });

    expect(apiMocks.resumeProjectLifecycle).toHaveBeenCalledWith("project-1", {
      reason: null,
      operator: null,
    });
    expect(result.current.project?.status).toBe("active");
    expect(result.current.lifecycle?.lifecycle_state).toBe("active");
  });

  it("closes a completed project with required note and refreshes Workbench state", async () => {
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));
    apiMocks.getProject.mockResolvedValueOnce({
      project_id: "project-1",
      product_name: "Connector Sample",
      requestor: "Lab User",
      status: "closed",
    });
    apiMocks.getProjectOutputStatusSummary.mockResolvedValueOnce({
      project_id: "project-1",
      active_draft_id: "draft-1",
      active_draft_version: 2,
      items: [],
    });

    await act(async () => {
      await result.current.onCloseCompletedLifecycle("  Outputs reviewed.  ");
    });

    expect(apiMocks.closeProjectCompletedLifecycle).toHaveBeenCalledWith("project-1", {
      close_note: "Outputs reviewed.",
      manual_completion_confirmed: true,
      output_summary_acknowledged: true,
      operator: null,
    });
    expect(apiMocks.getProject).toHaveBeenCalledTimes(2);
    expect(apiMocks.getProjectOutputStatusSummary).toHaveBeenCalledTimes(2);
    expect(result.current.project?.status).toBe("closed");
    expect(result.current.lifecycle?.lifecycle_state).toBe("closed");
    expect(result.current.lifecycle?.closure_type).toBe("completed");
  });

  it("rejects blank completed close notes before calling the close API", async () => {
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));

    await expect(
      act(async () => {
        await result.current.onCloseCompletedLifecycle("   ");
      })
    ).rejects.toThrow("Close note is required.");

    expect(apiMocks.closeProjectCompletedLifecycle).not.toHaveBeenCalled();
  });

  it("closes a project administratively with required reason and refreshes Workbench state", async () => {
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));
    apiMocks.getProject.mockResolvedValueOnce({
      project_id: "project-1",
      product_name: "Connector Sample",
      requestor: "Lab User",
      status: "closed",
    });

    await act(async () => {
      await result.current.onCloseAdministrativeLifecycle("  Duplicate request.  ");
    });

    expect(apiMocks.closeProjectAdministrativeLifecycle).toHaveBeenCalledWith(
      "project-1",
      {
        reason: "Duplicate request.",
        operator: null,
      }
    );
    expect(apiMocks.getProject).toHaveBeenCalledTimes(2);
    expect(apiMocks.getProjectOutputStatusSummary).toHaveBeenCalledTimes(2);
    expect(result.current.project?.status).toBe("closed");
    expect(result.current.lifecycle?.lifecycle_state).toBe("closed");
    expect(result.current.lifecycle?.closure_type).toBe("administrative");
  });

  it("rejects blank administrative close reasons before calling the close API", async () => {
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));

    await expect(
      act(async () => {
        await result.current.onCloseAdministrativeLifecycle("   ");
      })
    ).rejects.toThrow("Administrative close reason is required.");

    expect(apiMocks.closeProjectAdministrativeLifecycle).not.toHaveBeenCalled();
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

const requiredFormsPreviewContext = {
  project_id: "project-1",
  status: "ready",
  official_project_folder_path: "D:/Projects/DL-2026-06-001/Official",
  confirmed_matrix_id: "CM1",
  confirmed_revision: 1,
  confirmed_fee_id: "CF1",
  confirmed_fee_revision: 1,
  confirmed_fee_pricing_draft_edit_id: "PD1",
  confirmed_basic_information_version: 2,
  confirmed_basic_information_source_signature_hash: "basic-info-hash",
  customer_feedback_template_path: "D:/Template/E-4243 Customer Feedback Form.xlsx",
  blockers: [],
  warnings: [],
};

function lifecycleResponse(overrides = {}) {
  return {
    project_id: "project-1",
    lifecycle_state: "active",
    closure_type: null,
    status_label: "Active",
    readonly: false,
    allowed_actions: ["stop", "close"],
    status: "active",
    stopped_at: null,
    stopped_reason: null,
    closed_at: null,
    closed_reason: null,
    completion_summary: null,
    warnings: [],
    ...overrides,
  };
}

const readyRequiredFormsPreview = {
  ...requiredFormsPreviewContext,
  items: [
    {
      key: "test_record",
      label: "Test Record",
      target_path: "D:/Projects/DL-2026-06-001/Official/Submitted Material/DL Test Record.docx",
      status: "ready",
      action: "generate",
      message: "Ready to generate.",
      output_kind: "test_record_form",
      existing_sha256: null,
    },
    {
      key: "fee_form",
      label: "Fee Form",
      target_path: "D:/Projects/DL-2026-06-001/Official/DL Fee Form.xls",
      status: "ready",
      action: "generate",
      message: "Ready to generate.",
      output_kind: "fee_evaluation",
      existing_sha256: null,
    },
    {
      key: "customer_feedback_form",
      label: "Customer Feedback Form",
      target_path: "D:/Projects/DL-2026-06-001/Official/DL Customer Feedback Form.xlsx",
      status: "ready",
      action: "generate",
      message: "Ready to generate.",
      output_kind: "customer_feedback_form",
      existing_sha256: null,
    },
  ],
};

const currentRequiredFormsPreview = {
  ...requiredFormsPreviewContext,
  status: "current",
  items: readyRequiredFormsPreview.items.map((item) => ({
    ...item,
    status: "current",
    action: "skip",
    message: "Current.",
  })),
};
