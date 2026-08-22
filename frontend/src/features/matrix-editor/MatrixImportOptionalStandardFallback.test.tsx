import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError, type MatrixImportCommitResponse, type MatrixPreviewResponse } from "../../api/client";
import { MatrixEditorWorkspace } from "./MatrixEditorWorkspace";

const apiMocks = vi.hoisted(() => ({
  commitMatrixImport: vi.fn(),
  fetchMatrixEditorSession: vi.fn(),
  previewProjectTestPlanMatrixFromUpload: vi.fn(),
  saveMatrixEditorSessionDraft: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/client")>()),
  commitMatrixImport: apiMocks.commitMatrixImport,
  fetchMatrixEditorSession: apiMocks.fetchMatrixEditorSession,
  previewProjectTestPlanMatrixFromUpload: apiMocks.previewProjectTestPlanMatrixFromUpload,
  saveMatrixEditorSessionDraft: apiMocks.saveMatrixEditorSessionDraft,
  matrixPreviewPdfUrl: (token: string) => `/api/pdf/${token}`,
}));

vi.mock("../project-workbench/useProjectRuntimeConsoleModel", () => ({
  useProjectRuntimeConsoleModel: () => ({
    project: { project_id: "P1", product_name: "Connector", requestor: "Alice" },
    latestLtr: "LTR-0001",
    matrixAuthorityDraft: { source_document_name: "source.docx" },
    runtimeAuthoritySync: {
      projectionMatrixReference: "matrix-ref-1",
      authorityVersion: { confirmed_revision: 1 },
    },
    lifecycle: {
      project_id: "P1",
      lifecycle_state: "active",
      closure_type: null,
      status: "active",
      readonly: false,
      allowed_actions: ["stop"],
      warnings: [],
    },
    error: null,
  }),
}));
vi.mock("./MatrixSchedulePlanningCard", () => ({ MatrixSchedulePlanningCard: () => null }));
vi.mock("./MatrixEditorXlsxExportButton", () => ({ MatrixEditorXlsxExportButton: () => null }));
vi.mock("./useMatrixEditorXlsxExport", () => ({
  useMatrixEditorXlsxExport: () => ({ busy: false, error: null, message: null, exportSnapshot: vi.fn() }),
}));
vi.mock("./MatrixMethodVersionSyncPanel", () => ({ MatrixMethodVersionSyncPanel: () => null }));
vi.mock("./useMatrixMethodVersionSync", () => ({
  useMatrixMethodVersionSync: () => ({
    preview: null,
    selectedRowIds: [],
    busy: false,
    error: null,
    message: null,
    previewMethods: vi.fn(),
    toggleRow: vi.fn(),
    applySelected: vi.fn(),
  }),
}));
vi.mock("../contact-measurement-plan/ContactMeasurementPlanSummaryCard", () => ({
  ContactMeasurementPlanSummaryCard: () => null,
}));
vi.mock("../contact-measurement-plan/useProjectPointProfileSummaryModel", () => ({
  useProjectPointProfileSummaryModel: () => ({ summary: null, loading: false }),
}));

const actionDetail = {
  code: "matrix_import_standard_version_action_required",
  reason_code: "standard_version_not_configured",
  message: "Standard version file unavailable.",
};
const warningMessage =
  "Standard version file unavailable. Original Method values were kept. " +
  "You can update them later in Standard Method versions.";

describe("Matrix Import optional Standard version fallback", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiMocks.fetchMatrixEditorSession.mockResolvedValue(sessionSeed());
    apiMocks.saveMatrixEditorSessionDraft.mockResolvedValue({
      editor_draft_id: "draft-fallback",
      saved_payload_signature: "saved",
    });
  });

  afterEach(() => cleanup());

  it("turns typed action-required into a choice and Skip applies the preserved draft", async () => {
    const preview = importPreview();
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValue(preview);
    apiMocks.commitMatrixImport
      .mockRejectedValueOnce(
        new ApiRequestError(actionDetail.message, 409, actionDetail)
      )
      .mockResolvedValueOnce(fallbackResponse(preview));
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={vi.fn()} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, {
      target: { files: [new File(["docx"], "source.docx")] },
    });
    fireEvent.click(await screen.findByRole("button", { name: "Replace" }));

    const dialog = await screen.findByRole("dialog", {
      name: "Standard version file unavailable",
    });
    expect(dialog).toBeTruthy();
    expect(screen.queryByText("Failed to import Matrix.")).toBeNull();
    await userEvent.click(screen.getByRole("button", { name: "Skip for now" }));

    await waitFor(() => expect(apiMocks.commitMatrixImport).toHaveBeenCalledTimes(2));
    expect(apiMocks.commitMatrixImport.mock.calls[0][1]).toMatchObject({
      standard_version_unavailable_action: "prompt_if_unavailable",
    });
    expect(apiMocks.commitMatrixImport.mock.calls[1][1]).toMatchObject({
      standard_version_unavailable_action: "preserve_imported_methods",
    });
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(screen.queryByRole("button", { name: "Replace" })).toBeNull();
    const warning = await screen.findByRole("status");
    expect(warning.textContent).toContain(warningMessage);
    expect(warning.classList.contains("matrix-editor-import-status-warning")).toBe(true);
    expect(screen.getByDisplayValue("Original · Method 原值")).toBeTruthy();
  });

  it("keeps integrity failures on the fail-closed path without offering Skip", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValue(importPreview());
    apiMocks.commitMatrixImport.mockRejectedValue(
      new ApiRequestError("Standard workbook is corrupt.", 422, "Standard workbook is corrupt.")
    );
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={vi.fn()} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, {
      target: { files: [new File(["docx"], "source.docx")] },
    });
    fireEvent.click(await screen.findByRole("button", { name: "Replace" }));

    expect(await screen.findByText("Standard workbook is corrupt.")).toBeTruthy();
    expect(screen.queryByRole("dialog", { name: "Standard version file unavailable" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Skip for now" })).toBeNull();
  });
});

function importPreview(): MatrixPreviewResponse {
  return {
    project_id: "P1",
    source_document_path: "D:/source.docx",
    source_document_name: "source.docx",
    source_format: ".docx",
    capability_status: "supported",
    generated_at: "2026-08-01T00:00:00Z",
    selected_table_index: 0,
    selected_page_number: 1,
    selected_page_table_index: 1,
    candidate_tables: [],
    preview_pdf_token: null,
    rows: [
      {
        source_row_index: 1,
        test_item: "Visual",
        source_section: "1.1",
        method: "Original · Method 原值",
        condition: "10x",
        requirement: "No damage",
        group_tokens: { g1: "1" },
        is_sample_row: false,
      },
    ],
    groups: [
      {
        group_key: "g1",
        group_label: "1",
        source_table_index: 0,
        extraction_status: "loaded",
        sample_size: null,
        sample_quantity_expression: "5",
        sample_note: null,
        steps: [],
      },
    ],
    warnings: [],
    blockers: [],
  };
}

function sessionSeed() {
  const preview = importPreview();
  return {
    project_id: "P1",
    active_confirmed_matrix_id: "confirmed-1",
    active_confirmed_revision: 1,
    active_source_import_id: "source-old",
    active_source_snapshot_id: "snapshot-old",
    editor_draft_id: null,
    draft_status: "missing",
    loaded_source: "authority",
    stale_draft_present: false,
    draft_updated_at: null,
    saved_payload_signature: null,
    source_status: "available",
    source_unavailable_message: null,
    pre_test_buffer_days: null,
    post_test_buffer_days: null,
    sample_received_date: null,
    planned_test_start_date: null,
    planned_test_complete_date: null,
    estimated_completion_date: null,
    source_preview_payload: preview,
    editor_draft: {
      groups: [], rows: [], cells: [],
    },
  };
}

function fallbackResponse(preview: MatrixPreviewResponse): MatrixImportCommitResponse {
  return {
    source_import_id: "import-fallback",
    source_snapshot_id: "snapshot-fallback",
    selected_group_keys_committed: ["g1"],
    commit_status: "created",
    project_matrix_draft: {
      record: {
        project_matrix_draft_id: "draft-fallback",
        project_id: "P1",
        source_import_id: "import-fallback",
        source_snapshot_id: "snapshot-fallback",
        base_confirmed_matrix_id: null,
        status: "draft",
        created_at: "2026-08-01T00:00:00Z",
        updated_at: "2026-08-01T00:00:00Z",
      },
      groups: [{
        draft_group_id: "group-1", source_group_snapshot_id: "source-group-1",
        group_order: 1, group_key: "g1", group_label: "1", is_selected: true,
        sample_quantity_expression: "5", sample_note: null,
      }],
      rows: [{
        draft_row_id: "row-1", source_row_snapshot_id: "source-row-1", row_order: 1,
        test_item: "Visual", source_section: "1.1", method: "Original · Method 原值",
        condition: "10x", requirement: "No damage", day_expression: null,
        is_sample_row: false,
      }],
      cells: [{
        draft_cell_id: "cell-1", draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1",
      }],
    },
    method_authority_sync: {
      status: "source_preserved",
      updated_count: 0,
      current_count: 0,
      review_count: 0,
      standard_resource_id: null,
      effective_worksheet_name: null,
      catalog_fingerprint: null,
      context_fingerprint: "fallback-context",
      rows: [],
      warning: { code: "standard_version_unavailable", message: warningMessage },
    },
  };
}
