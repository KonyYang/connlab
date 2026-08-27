import { afterEach, beforeEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";
import {
  type MatrixImportCommitResponse,
  type MatrixPreviewResponse,
} from "../../api/client";

const apiMocks = vi.hoisted(() => ({
  fetchMatrixEditorSession: vi.fn(),
  createMatrixRevisionDraft: vi.fn(),
  saveMatrixEditorSessionDraft: vi.fn(),
  discardMatrixEditorSessionDraft: vi.fn(),
  confirmMatrixEditorSession: vi.fn(),
  generateMatrixEditorTestRecordDraftDownload: vi.fn(),
  generateMatrixEditorTestStatusDraftDownload: vi.fn(),
  generateMatrixEditorLlcrCrRecordDraftDownload: vi.fn(),
  previewProjectTestPlanMatrixFromUpload: vi.fn(),
  previewProjectTestPlanMatrixFromPath: vi.fn(),
  previewProjectTestPlanMatrixFromSourceCandidate: vi.fn(),
  commitMatrixImport: vi.fn(),
  previewLlcrCrRecordWorkbook: vi.fn(),
  generateLlcrCrRecordWorkbook: vi.fn(),
  downloadLlcrCrRecordWorkbook: vi.fn(),
  fetchContactMeasurementPlanWorkspace: vi.fn(),
  openContactMeasurementPlanRevision: vi.fn(),
  patchContactMeasurementPlanTarget: vi.fn(),
  saveContactMeasurementPlanRevision: vi.fn(),
  confirmContactMeasurementPlanRevision: vi.fn(),
  refreshContactMeasurementPlanImpacts: vi.fn(),
  acceptCompatibleContactMeasurementPlanSuggestions: vi.fn(),
  rebindContactMeasurementPlanTarget: vi.fn(),
  fetchProjectPointProfileWorkspace: vi.fn(),
  fetchProjectPointProfileSummary: vi.fn(),
  saveProjectPointProfileDraft: vi.fn(),
  confirmProjectPointProfile: vi.fn(),
  matrixPreviewPdfUrl: vi.fn((token: string) => `/api/pdf/${token}`),
}));

const sourcePickerMocks = vi.hoisted(() => ({
  hasDesktop: vi.fn(() => false),
  choose: vi.fn(),
}));

vi.mock("../../desktop/pathPickerBridge", () => ({
  hasMatrixImportSourcePicker: sourcePickerMocks.hasDesktop,
}));

vi.mock("./useMatrixImportSourcePicker", () => ({
  useMatrixImportSourcePicker: () => sourcePickerMocks.choose,
}));

const runtimeModelState = vi.hoisted(() => ({
  lifecycle: {
    project_id: "P1",
    lifecycle_state: "active",
    closure_type: null as string | null,
    status: "active",
    previous_project_status: null,
    stopped_at: null,
    closed_at: null,
    updated_at: "2026-06-27T09:00:00Z",
    allowed_actions: ["stop"],
    readonly: false,
    warnings: [],
  },
}));

vi.mock("../../api/client", () => {
  class MockApiRequestError extends Error {
    status: number;
    detail: unknown;
    constructor(message: string, status: number, detail: unknown) {
      super(message);
      this.name = "ApiRequestError";
      this.status = status;
      this.detail = detail;
    }
  }
  return {
    ApiRequestError: MockApiRequestError,
    fetchMatrixEditorSession: apiMocks.fetchMatrixEditorSession,
    createMatrixRevisionDraft: apiMocks.createMatrixRevisionDraft,
    saveMatrixEditorSessionDraft: apiMocks.saveMatrixEditorSessionDraft,
    discardMatrixEditorSessionDraft: apiMocks.discardMatrixEditorSessionDraft,
    confirmMatrixEditorSession: apiMocks.confirmMatrixEditorSession,
    generateMatrixEditorTestRecordDraftDownload: apiMocks.generateMatrixEditorTestRecordDraftDownload,
    generateMatrixEditorTestStatusDraftDownload: apiMocks.generateMatrixEditorTestStatusDraftDownload,
    generateMatrixEditorLlcrCrRecordDraftDownload: apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload,
    previewProjectTestPlanMatrixFromUpload: apiMocks.previewProjectTestPlanMatrixFromUpload,
    previewProjectTestPlanMatrixFromPath: apiMocks.previewProjectTestPlanMatrixFromPath,
    previewProjectTestPlanMatrixFromSourceCandidate: apiMocks.previewProjectTestPlanMatrixFromSourceCandidate,
    commitMatrixImport: apiMocks.commitMatrixImport,
    previewLlcrCrRecordWorkbook: apiMocks.previewLlcrCrRecordWorkbook,
    generateLlcrCrRecordWorkbook: apiMocks.generateLlcrCrRecordWorkbook,
    downloadLlcrCrRecordWorkbook: apiMocks.downloadLlcrCrRecordWorkbook,
    fetchContactMeasurementPlanWorkspace: apiMocks.fetchContactMeasurementPlanWorkspace,
    openContactMeasurementPlanRevision: apiMocks.openContactMeasurementPlanRevision,
    patchContactMeasurementPlanTarget: apiMocks.patchContactMeasurementPlanTarget,
    saveContactMeasurementPlanRevision: apiMocks.saveContactMeasurementPlanRevision,
    confirmContactMeasurementPlanRevision: apiMocks.confirmContactMeasurementPlanRevision,
    refreshContactMeasurementPlanImpacts: apiMocks.refreshContactMeasurementPlanImpacts,
    acceptCompatibleContactMeasurementPlanSuggestions: apiMocks.acceptCompatibleContactMeasurementPlanSuggestions,
    rebindContactMeasurementPlanTarget: apiMocks.rebindContactMeasurementPlanTarget,
    fetchProjectPointProfileWorkspace: apiMocks.fetchProjectPointProfileWorkspace,
    fetchProjectPointProfileSummary: apiMocks.fetchProjectPointProfileSummary,
    saveProjectPointProfileDraft: apiMocks.saveProjectPointProfileDraft,
    confirmProjectPointProfile: apiMocks.confirmProjectPointProfile,
    matrixPreviewPdfUrl: apiMocks.matrixPreviewPdfUrl,
    isProjectLifecycleReadonlyErrorDetail: (detail: unknown) =>
      Boolean(detail) &&
      typeof detail === "object" &&
      (detail as { code?: unknown }).code === "project_lifecycle_readonly",
  };
});

vi.mock("../project-workbench/useProjectRuntimeConsoleModel", () => ({
  useProjectRuntimeConsoleModel: () => ({
    project: {
      product_name: "Connector A",
      sample_description: "Coolpower HDF 3.40mm pin",
      test_item: "Qualification Testing",
      business_unit: "BU-1",
      requestor: "Alice",
    },
    latestLtr: "LTR-0001",
    matrixAuthorityDraft: { source_document_name: "EIA-364 Qualification Matrix" },
    runtimeAuthoritySync: {
      projectionMatrixReference: "matrix-ref-1",
      authorityVersion: { confirmed_revision: 1 },
    },
    lifecycle: runtimeModelState.lifecycle,
    error: null,
  }),
}));

export function buildSessionSeed() {
  return {
    project_id: "P1",
    active_confirmed_matrix_id: "confirmed-1",
    active_confirmed_revision: 3,
    active_source_import_id: "source-a",
    active_source_snapshot_id: "snapshot-a",
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
    source_preview_payload: {
      project_id: "P1",
      source_document_path: "D:/spec.docx",
      source_document_name: "spec.docx",
      source_format: ".docx",
      capability_status: "supported",
      generated_at: "2026-05-28T00:00:00Z",
      selected_table_index: 0,
      selected_page_number: 1,
      selected_page_table_index: 1,
      candidate_tables: [],
      preview_pdf_token: null,
      rows: [
        {
          source_row_index: 1,
          test_item: "Visual Examination",
          source_section: "1.1",
          group_tokens: { "1": "1", g1: "1" },
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
    },
    editor_draft: {
      groups: [
        {
          draft_group_id: "group-1",
          source_group_snapshot_id: "sg-1",
          group_order: 1,
          group_key: "g1",
          group_label: "1",
          is_selected: true,
          sample_quantity_expression: "5",
          sample_note: null,
        },
      ],
      rows: [
        {
          draft_row_id: "row-1",
          source_row_snapshot_id: "sr-1",
          row_order: 1,
          test_item: "Visual Examination",
          source_section: "1.1",
          method: "EIA-364-18B",
          condition: "10x min magnification",
          requirement: "No detrimental condition",
          day_expression: null,
          is_sample_row: false,
        },
      ],
      cells: [{ draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1" }],
    },
  };
}

export function buildImportPreview(
  overrides: Partial<MatrixPreviewResponse> = {},
): MatrixPreviewResponse {
  const seed = buildSessionSeed();
  const base = seed.source_preview_payload as MatrixPreviewResponse;
  return {
    ...base,
    groups: base.groups.map((group) => ({ ...group })),
    rows: base.rows.map((row) => ({ ...row })),
    blockers: [],
    warnings: [],
    ...overrides,
  };
}

export function buildCommitResponse(
  preview: MatrixPreviewResponse,
  sampleQuantityExpression = "7",
): MatrixImportCommitResponse {
  return {
    source_import_id: "import-test",
    source_snapshot_id: "snapshot-test",
    selected_group_keys_committed: preview.groups.map((group) => group.group_key),
    commit_status: "created",
    method_authority_sync: {
      status: "review_required",
      updated_count: 1,
      current_count: 0,
      review_count: 2,
      standard_resource_id: "standard-1",
      effective_worksheet_name: "认可标准",
      catalog_fingerprint: "catalog-fingerprint",
      context_fingerprint: "context-fingerprint",
      rows: [],
    },
    project_matrix_draft: {
      record: {
        project_matrix_draft_id: "draft-test",
        project_id: "P1",
        base_confirmed_matrix_id: null,
        status: "draft",
        source_import_id: "import-test",
        source_snapshot_id: "snapshot-test",
        created_at: "2026-05-28T00:00:00Z",
        updated_at: "2026-05-28T00:00:00Z",
      },
      groups: preview.groups.map((group, index) => ({
        draft_group_id: `group-${index + 1}`,
        source_group_snapshot_id: `sg-${index + 1}`,
        group_order: index + 1,
        group_key: group.group_key,
        group_label: group.group_label,
        is_selected: true,
        sample_quantity_expression: sampleQuantityExpression,
        sample_note: null,
      })),
      rows: preview.rows.map((row, index) => ({
        draft_row_id: `row-${index + 1}`,
        source_row_snapshot_id: `sr-${index + 1}`,
        row_order: index + 1,
        test_item: row.test_item,
        source_section: row.source_section ?? null,
        method: row.method ?? null,
        condition: row.condition ?? null,
        requirement: row.requirement ?? null,
        is_sample_row: row.is_sample_row,
      })),
      cells: [
        {
          draft_cell_id: "cell-test",
          draft_row_id: "row-1",
          draft_group_id: "group-1",
          cell_value: preview.groups[0]?.group_label ?? "1",
        },
      ],
    },
  };
}

export function createDeferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((promiseResolve, promiseReject) => {
    resolve = promiseResolve;
    reject = promiseReject;
  });
  return { promise, resolve, reject };
}

export function installMatrixEditorWorkspaceTestLifecycle(): void {
  beforeEach(() => {
    vi.clearAllMocks();
    sourcePickerMocks.hasDesktop.mockReturnValue(false);
    sourcePickerMocks.choose.mockResolvedValue({ kind: "browser" });
    apiMocks.fetchContactMeasurementPlanWorkspace.mockResolvedValue({
      status: "not_started",
      project_id: "P1",
      active_confirmed_revision_id: null,
      editable_revision_id: null,
      editable_revision_state: null,
      editable_revision_fingerprint: null,
      revision: null,
      matrix_binding: null,
      targets: [],
      impacts: [],
      summary: {
        included_target_count: 0,
        total_target_count: 0,
        needs_review_count: 0,
        readings_by_kind: { llcr: null, cr_specified_current: null },
      },
      diagnostics: [],
    });
    apiMocks.fetchProjectPointProfileWorkspace.mockResolvedValue({
      status: "not_started",
      project_id: "P1",
      editable_revision: null,
      confirmed_revision: null,
      has_unconfirmed_draft: false,
      legacy_suggestion: null,
    });
    apiMocks.fetchProjectPointProfileSummary.mockResolvedValue({
      status: "not_started", project_id: "P1", confirmed_revision: null,
      points_per_sample: null, has_unconfirmed_draft: false, diagnostics: [],
    });
    runtimeModelState.lifecycle = {
      project_id: "P1",
      lifecycle_state: "active",
      closure_type: null as string | null,
      status: "active",
      previous_project_status: null,
      stopped_at: null,
      closed_at: null,
      updated_at: "2026-06-27T09:00:00Z",
      allowed_actions: ["stop"],
      readonly: false,
      warnings: [],
    };
    apiMocks.fetchMatrixEditorSession.mockResolvedValue(buildSessionSeed());
    apiMocks.createMatrixRevisionDraft.mockResolvedValue({});
    apiMocks.previewLlcrCrRecordWorkbook.mockResolvedValue({
      status: "ready",
      row_count: 1,
      sections: [{ group_label: "1", source_step: "1", record_type: "llcr" }],
      diagnostics: [],
      preview_fingerprint: "confirmed-preview",
    });
    apiMocks.saveMatrixEditorSessionDraft.mockResolvedValue({
      editor_draft_id: "editor-draft-1",
      draft_status: "current",
      draft_updated_at: "2026-06-14T00:00:00Z",
      saved_payload_signature: "saved-signature-1",
      active_confirmed_matrix_id: "confirmed-1",
      active_confirmed_revision: 3,
    });
    apiMocks.discardMatrixEditorSessionDraft.mockResolvedValue({
      discarded: true,
      active_confirmed_matrix_id: "confirmed-1",
      active_confirmed_revision: 3,
    });
    apiMocks.confirmMatrixEditorSession.mockResolvedValue({
      publish_status: "published",
      message: "Matrix confirmed (v4).",
      confirmed_snapshot: null,
    });
    apiMocks.generateMatrixEditorTestRecordDraftDownload.mockResolvedValue({
      blob: new Blob(["docx"], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      }),
      fileName: "DL-2026 Test Record Preview - Unconfirmed Matrix draft.docx",
    });
    apiMocks.generateMatrixEditorTestStatusDraftDownload.mockResolvedValue({
      blob: new Blob(["test-status"]),
      fileName: "DL-2026-08-001 test status.xlsx",
    });
    apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload.mockResolvedValue({
      blob: new Blob(["xlsx"], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      }),
      fileName: "P1_LLCR_Record_Preview_Unconfirmed_Matrix_draft.xlsx",
    });
    if (!window.URL.createObjectURL) {
      Object.defineProperty(window.URL, "createObjectURL", {
        configurable: true,
        value: vi.fn(),
      });
    }
    if (!window.URL.revokeObjectURL) {
      Object.defineProperty(window.URL, "revokeObjectURL", {
        configurable: true,
        value: vi.fn(),
      });
    }
    vi.spyOn(window.URL, "createObjectURL").mockReturnValue("blob:test-record-preview");
    vi.spyOn(window.URL, "revokeObjectURL").mockImplementation(() => {});
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
    vi.spyOn(window, "confirm").mockReturnValue(true);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    cleanup();
  });
}

export {
  apiMocks,
  runtimeModelState,
  sourcePickerMocks,
};
export type { MatrixImportCommitResponse, MatrixPreviewResponse } from "../../api/client";
