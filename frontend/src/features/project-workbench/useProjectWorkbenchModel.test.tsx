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
  activateProjectLifecycle: vi.fn(),
  collectRequestMaterial: vi.fn(),
  closeProjectLifecycle: vi.fn(),
  closeProjectAdministrativeLifecycle: vi.fn(),
  closeProjectCompletedLifecycle: vi.fn(),
  confirmProjectTestPlanMatrixDraft: vi.fn(),
  createProjectTestPlanDraft: vi.fn(),
  executePublicFolderWorkflowPull: vi.fn(),
  executePublicFolderWorkflowSubmit: vi.fn(),
  executePublicFolderWorkflowSync: vi.fn(),
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
  getPublicFolderWorkflowContext: vi.fn(),
  getRuntimeProjectionReadOnlySnapshot: vi.fn(),
  listExternalResources: vi.fn(),
  listProjectLtrs: vi.fn(),
  listProjectTestPlanDrafts: vi.fn(),
  listProjectTestPlanSourceCandidates: vi.fn(),
  openLocalProjectFolder: vi.fn(),
  placeEvidence: vi.fn(),
  previewApprovalPackage: vi.fn(),
  previewEvidencePlacement: vi.fn(),
  previewProjectTestPlanMatrixFromPath: vi.fn(),
  previewProjectTestPlanMatrixFromSourceCandidate: vi.fn(),
  previewPublicFolderWorkflowPull: vi.fn(),
  previewPublicFolderWorkflowSubmit: vi.fn(),
  previewPublicFolderWorkflowSync: vi.fn(),
  repairOfficialFolderStructure: vi.fn(),
  resumeProjectLifecycle: vi.fn(),
  stopProjectLifecycle: vi.fn(),
  syncProjectSection2FromConfirmedMatrix: vi.fn(),
  setPublicFolderWorkflowAutoSync: vi.fn(),
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
    apiMocks.activateProjectLifecycle.mockResolvedValue(lifecycleResponse());
    apiMocks.closeProjectLifecycle.mockResolvedValue(
      lifecycleResponse({
        lifecycle_state: "closed",
        closure_type: null,
        close_reason_category: "failed",
        close_reason_label: "Failed",
        status: "closed",
        status_label: "Closed",
        readonly: true,
        allowed_actions: ["activate"],
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
      authority_context: {
        matrix_source: "missing",
        confirmed_fee_status: "missing",
      },
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
    apiMocks.getPublicFolderWorkflowContext.mockResolvedValue(
      publicFolderWorkflowContext()
    );
    apiMocks.setPublicFolderWorkflowAutoSync.mockResolvedValue({
      project_id: "project-1",
      auto_sync_enabled: true,
      sync_locked: false,
      submitted_at: null,
      submit_operation_id: null,
      last_sync_operation_id: null,
      last_pull_operation_id: null,
      created_at: "2026-06-30T00:00:00Z",
      updated_at: "2026-06-30T00:00:00Z",
    });
    apiMocks.previewPublicFolderWorkflowSync.mockResolvedValue(
      publicFolderWorkflowPreview("sync")
    );
    apiMocks.previewPublicFolderWorkflowSubmit.mockResolvedValue(
      publicFolderWorkflowPreview("submit")
    );
    apiMocks.previewPublicFolderWorkflowPull.mockResolvedValue(
      publicFolderWorkflowPreview("pull")
    );
    apiMocks.executePublicFolderWorkflowSync.mockResolvedValue(
      publicFolderWorkflowResult("sync")
    );
    apiMocks.executePublicFolderWorkflowSubmit.mockResolvedValue(
      publicFolderWorkflowResult("submit")
    );
    apiMocks.executePublicFolderWorkflowPull.mockResolvedValue(
      publicFolderWorkflowResult("pull")
    );
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

  it("loads and saves backend-owned public folder Auto sync state", async () => {
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() =>
      expect(result.current.publicFolderWorkflowContext?.auto_sync_enabled).toBe(false)
    );

    await act(async () => {
      await result.current.onSetPublicFolderWorkflowAutoSync(true);
    });

    expect(apiMocks.setPublicFolderWorkflowAutoSync).toHaveBeenCalledWith(
      "project-1",
      true
    );
    expect(result.current.publicFolderWorkflowMessage).toBe("Auto sync enabled.");
  });

  it("uses preview-first Submit before executing with the preview hash", async () => {
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));

    await act(async () => {
      await result.current.onPreviewPublicFolderWorkflowOperation("submit");
    });

    expect(apiMocks.previewPublicFolderWorkflowSubmit).toHaveBeenCalledWith("project-1");
    expect(result.current.publicFolderWorkflowConfirmingOperation).toBe("submit");
    expect(apiMocks.executePublicFolderWorkflowSubmit).not.toHaveBeenCalled();

    await act(async () => {
      await result.current.onConfirmPublicFolderWorkflowOperation("submit");
    });

    expect(apiMocks.executePublicFolderWorkflowSubmit).toHaveBeenCalledWith(
      "project-1",
      {
        preview_hash: "submit-preview-hash",
        confirmed: true,
        confirm_directory_creation: true,
        operator: null,
      }
    );
    expect(result.current.publicFolderWorkflowConfirmingOperation).toBeNull();
    expect(result.current.publicFolderWorkflowMessage).toBe("Submit completed.");
  });

  it("does not execute when a workflow preview reports conflicts", async () => {
    apiMocks.previewPublicFolderWorkflowSubmit.mockResolvedValueOnce(
      publicFolderWorkflowPreview("submit", {
        status: "conflict",
        conflicts: ["Unmanaged public files require review."],
      })
    );
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));

    await act(async () => {
      await result.current.onPreviewPublicFolderWorkflowOperation("submit");
    });

    expect(result.current.publicFolderWorkflowConfirmingOperation).toBeNull();
    expect(result.current.publicFolderWorkflowMessage).toBe(
      "Unmanaged public files require review."
    );
    expect(apiMocks.executePublicFolderWorkflowSubmit).not.toHaveBeenCalled();
  });

  it("opens the backend-resolved local project folder", async () => {
    apiMocks.openLocalProjectFolder.mockResolvedValueOnce({
      project_id: "project-1",
      status: "opened",
      message: "Project folder opened.",
      local_official_folder_path: "D:/Projects/DL-2026-06-001/Official",
    });
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));

    await act(async () => {
      await result.current.onOpenLocalProjectFolder();
    });

    expect(apiMocks.openLocalProjectFolder).toHaveBeenCalledWith("project-1");
    expect(result.current.publicFolderWorkflowMessage).toBe("Project folder opened.");
    expect(result.current.publicFolderWorkflowError).toBeNull();
  });

  it("refreshes Folder Actions after creating the project folder", async () => {
    apiMocks.getPublicFolderWorkflowContext
      .mockResolvedValueOnce(
        publicFolderWorkflowContext({ local_official_folder_path: null })
      )
      .mockResolvedValue(publicFolderWorkflowContext());
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() =>
      expect(result.current.publicFolderWorkflowContext?.local_official_folder_path).toBeNull()
    );

    await act(async () => {
      await result.current.onCreateOfficialWorkspace();
    });

    expect(apiMocks.getPublicFolderWorkflowContext).toHaveBeenCalledTimes(2);
    expect(result.current.publicFolderWorkflowContext?.local_official_folder_path).toBe(
      "D:/Projects/DL-2026-06-001/Official"
    );
  });

  it("shows the local folder path fallback when the open bridge is blocked", async () => {
    apiMocks.openLocalProjectFolder.mockResolvedValueOnce({
      project_id: "project-1",
      status: "blocked",
      message: "Project folder is not available yet.",
      local_official_folder_path: "D:/Projects/DL-2026-06-001/Official",
    });
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));

    await act(async () => {
      await result.current.onOpenLocalProjectFolder();
    });

    expect(result.current.publicFolderWorkflowMessage).toBe(
      "Project folder is not available yet. D:/Projects/DL-2026-06-001/Official"
    );
    expect(result.current.publicFolderWorkflowError).toBeNull();
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

    expect(apiMocks.generateProjectFolderRequiredForms).toHaveBeenCalledTimes(4);
    expect(
      apiMocks.generateProjectFolderRequiredForms.mock.calls.map(
        ([, request]) => request.expected_targets[0].key
      )
    ).toEqual(["customer_feedback_form", "fee_form", "test_record", "test_status"]);
    expect(result.current.requiredFormsResult?.items.map((item) => item.key)).toEqual([
      "customer_feedback_form",
      "fee_form",
      "test_record",
      "test_status",
    ]);
    expect(apiMocks.syncProjectSection2FromConfirmedMatrix).not.toHaveBeenCalled();
  });

  it("activates lifecycle in place and refreshes project status", async () => {
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
        allowed_actions: ["activate", "resume", "close"],
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
      await result.current.onActivateLifecycle("  Business work continues.  ");
    });

    expect(apiMocks.activateProjectLifecycle).toHaveBeenCalledWith("project-1", {
      reason: "Business work continues.",
      operator: null,
    });
    expect(result.current.project?.status).toBe("active");
    expect(result.current.lifecycle?.lifecycle_state).toBe("active");
  });

  it("closes a project with unified business reason and refreshes Workbench state", async () => {
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
      await result.current.onCloseLifecycle("failed", "  Testing cannot continue.  ");
    });

    expect(apiMocks.closeProjectLifecycle).toHaveBeenCalledWith("project-1", {
      reason_category: "failed",
      note: "Testing cannot continue.",
      operator: null,
    });
    expect(apiMocks.closeProjectCompletedLifecycle).not.toHaveBeenCalled();
    expect(apiMocks.closeProjectAdministrativeLifecycle).not.toHaveBeenCalled();
    expect(apiMocks.getProject).toHaveBeenCalledTimes(2);
    expect(apiMocks.getProjectOutputStatusSummary).toHaveBeenCalledTimes(2);
    expect(result.current.project?.status).toBe("closed");
    expect(result.current.lifecycle?.lifecycle_state).toBe("closed");
    expect(result.current.lifecycle?.close_reason_category).toBe("failed");
  });

  it("rejects blank close notes before calling the close API", async () => {
    const { result } = renderHook(() => useProjectWorkbenchModel("project-1"));

    await waitFor(() => expect(apiMocks.getProject).toHaveBeenCalledTimes(1));

    await expect(
      act(async () => {
        await result.current.onCloseLifecycle("other", "   ");
      })
    ).rejects.toThrow("Close note is required.");

    expect(apiMocks.closeProjectLifecycle).not.toHaveBeenCalled();
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

function publicFolderWorkflowContext(overrides = {}) {
  return {
    project_id: "project-1",
    auto_sync_enabled: false,
    sync_locked: false,
    submitted_at: null,
    public_root: "D:/PublicProject",
    public_root_class: "open",
    public_folder_year: 2026,
    year_source: "project_created_on",
    year_evidence: "2026-06-30",
    local_official_folder_path: "D:/Projects/DL-2026-06-001/Official",
    public_open_path: "D:/PublicProject/Open/2026/DL-2026-06-001",
    public_closed_path: "D:/PublicProject/Closed/2026/DL-2026-06-001",
    blockers: [],
    warnings: [],
    ...overrides,
  };
}

function publicFolderWorkflowPreview(operation: "sync" | "submit" | "pull", overrides = {}) {
  return {
    project_id: "project-1",
    operation_type: operation,
    status: "ready",
    local_official_folder_path: "D:/Projects/DL-2026-06-001/Official",
    public_root: "D:/PublicProject",
    public_root_class: "open",
    public_folder_year: 2026,
    year_source: "project_created_on",
    year_evidence: "2026-06-30",
    public_open_path: "D:/PublicProject/Open/2026/DL-2026-06-001",
    public_closed_path: "D:/PublicProject/Closed/2026/DL-2026-06-001",
    target_path:
      operation === "pull"
        ? "D:/Projects/DL-2026-06-001/Official"
        : "D:/PublicProject/Open/2026/DL-2026-06-001",
    items: [],
    blockers: [],
    warnings: [],
    conflicts: [],
    required_confirmations:
      operation === "submit" ? ["create_missing_public_directories"] : [],
    counts: {},
    preview_hash: `${operation}-preview-hash`,
    next_action: operation,
    auto_sync_enabled: false,
    sync_locked: false,
    ...overrides,
  };
}

function publicFolderWorkflowResult(operation: "sync" | "submit" | "pull") {
  return {
    project_id: "project-1",
    operation_id: "operation-12",
    operation_type: operation,
    status: "completed",
    counts: {},
    errors: [],
    preview: publicFolderWorkflowPreview(operation),
  };
}

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
      key: "test_status",
      label: "Test Status",
      target_path: "D:/Projects/DL-2026-06-001/Official/Submitted Material/DL test status.xlsx",
      status: "ready",
      action: "generate",
      message: "Ready to generate.",
      output_kind: "test_status",
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
