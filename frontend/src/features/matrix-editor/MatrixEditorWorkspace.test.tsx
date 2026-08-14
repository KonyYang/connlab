import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MatrixEditorWorkspace } from "./MatrixEditorWorkspace";
import {
  ApiRequestError,
  type MatrixImportCommitResponse,
  type MatrixPreviewResponse,
} from "../../api/client";

const apiMocks = vi.hoisted(() => ({
  fetchMatrixEditorSession: vi.fn(),
  fetchMatrixStepQuantities: vi.fn(),
  createMatrixRevisionDraft: vi.fn(),
  saveMatrixEditorSessionDraft: vi.fn(),
  saveMatrixStepQuantities: vi.fn(),
  discardMatrixEditorSessionDraft: vi.fn(),
  confirmMatrixEditorSession: vi.fn(),
  generateMatrixEditorTestRecordDraftDownload: vi.fn(),
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
    fetchMatrixStepQuantities: apiMocks.fetchMatrixStepQuantities,
    createMatrixRevisionDraft: apiMocks.createMatrixRevisionDraft,
    saveMatrixEditorSessionDraft: apiMocks.saveMatrixEditorSessionDraft,
    saveMatrixStepQuantities: apiMocks.saveMatrixStepQuantities,
    discardMatrixEditorSessionDraft: apiMocks.discardMatrixEditorSessionDraft,
    confirmMatrixEditorSession: apiMocks.confirmMatrixEditorSession,
    generateMatrixEditorTestRecordDraftDownload: apiMocks.generateMatrixEditorTestRecordDraftDownload,
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

function buildSessionSeed() {
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

function buildImportPreview(
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

function buildCommitResponse(
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

function createDeferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((promiseResolve, promiseReject) => {
    resolve = promiseResolve;
    reject = promiseReject;
  });
  return { promise, resolve, reject };
}

describe("MatrixEditorWorkspace TASK_279 flow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sourcePickerMocks.hasDesktop.mockReturnValue(false);
    sourcePickerMocks.choose.mockResolvedValue({ kind: "browser" });
    apiMocks.fetchMatrixStepQuantities.mockResolvedValue({
      project_id: "P1",
      project_matrix_draft_id: "draft-test",
      items: [
        {
          draft_group_id: "group-1",
          draft_row_id: "row-1",
          step_sequence: 1,
          step_suffix_note: null,
          raw_token: "1",
          test_item: "Visual Examination",
          test_points_per_sample: "3",
          readings_per_point: "2",
          contact_points_per_sample: "4",
          total_readings: "6",
          source: "basic_information_confirmed",
          review_required: false,
          review_reason: null,
        },
      ],
    });
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
    apiMocks.saveMatrixStepQuantities.mockImplementation(async (_projectId, draftId, input) => ({
      project_id: "P1",
      project_matrix_draft_id: draftId,
      items: input.items.map((item: any) => ({
        ...item,
        test_item: "Visual Examination",
        total_readings: "20",
        review_required: Boolean(item.review_required),
        review_reason: item.review_reason ?? null,
      })),
    }));
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

  it("shows Matrix-only header actions and completion actions in a sticky footer", async () => {
    render(
      <MatrixEditorWorkspace
        projectId="P1"
        onBackToWorkbench={() => {}}
      />
    );
    expect(screen.queryByText("Loading matrix editor...")).toBeNull();
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));
    const identityLine = screen.getByText("LTR-0001 Coolpower HDF 3.40mm pin Qualification Testing");
    expect(identityLine.getAttribute("title")).toBe("LTR-0001 Coolpower HDF 3.40mm pin Qualification Testing");
    expect(screen.queryByText("LTR-0001 | Connector A | EIA-364 Qualification Matrix")).toBeNull();
    expect(screen.getByText("spec.docx")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Import Matrix" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Test record" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Fee Evaluation" })).toBeNull();
    const completionDock = screen.getByRole("contentinfo", { name: "Matrix editor completion actions" });
    expect((completionDock as HTMLElement).classList.contains("matrix-editor-completion-dock")).toBe(true);
    expect(screen.getByRole("button", { name: "Cancel" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Confirm Matrix" })).toBeTruthy();
    expect(screen.queryByText("Confirm As Active Matrix")).toBeNull();
    expect(screen.queryByText("Create Revision Draft")).toBeNull();
    expect(screen.queryByText("Confirm Revision")).toBeNull();
    expect(screen.getByRole("button", { name: "Setup" })).toBeTruthy();
  });

  it("keeps the Matrix summary free of specialized workbook controls", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByRole("button", { name: "Setup" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Open editable Matrix draft" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Preview specialized record" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Generate workbook" })).toBeNull();
  });

  it("loads and saves Matrix Step quantity setup for the selected group", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft_id: "draft-test",
      saved_payload_signature: "saved-signature",
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByText("Step quantity setup")).toBeTruthy();
    await waitFor(() =>
      expect(apiMocks.fetchMatrixStepQuantities).toHaveBeenCalledWith("P1", "draft-test")
    );
    const points = (await screen.findByLabelText(
      "Step 1 test points per sample"
    )) as HTMLInputElement;
    fireEvent.change(points, { target: { value: "5" } });
    fireEvent.click(screen.getByRole("button", { name: "Save quantities" }));

    await waitFor(() => expect(apiMocks.saveMatrixStepQuantities).toHaveBeenCalledTimes(1));
    expect(apiMocks.saveMatrixStepQuantities.mock.calls[0][0]).toBe("P1");
    expect(apiMocks.saveMatrixStepQuantities.mock.calls[0][1]).toBe("draft-test");
    expect(apiMocks.saveMatrixStepQuantities.mock.calls[0][2].items[0]).toMatchObject({
      test_points_per_sample: "5",
      source: "matrix_step_override",
    });
  });

  it("applies Matrix Step quantity defaults only to blank fields", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft_id: "draft-test",
      saved_payload_signature: "saved-signature",
    });
    apiMocks.fetchMatrixStepQuantities.mockResolvedValueOnce({
      project_id: "P1",
      project_matrix_draft_id: "draft-test",
      items: [
        {
          draft_group_id: "group-1",
          draft_row_id: "row-1",
          step_sequence: 1,
          step_suffix_note: null,
          raw_token: "1",
          test_item: "Visual Examination",
          test_points_per_sample: "",
          readings_per_point: null,
          contact_points_per_sample: "",
          total_readings: null,
          source: "manual_required",
          review_required: true,
          review_reason: "Confirm Step quantity values.",
        },
        {
          draft_group_id: "group-1",
          draft_row_id: "row-2",
          step_sequence: 2,
          step_suffix_note: null,
          raw_token: "2",
          test_item: "Visual Examination",
          test_points_per_sample: "9",
          readings_per_point: "8",
          contact_points_per_sample: "7",
          total_readings: "72",
          source: "matrix_step_override",
          review_required: false,
          review_reason: null,
        },
      ],
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByText("Defaults for this group")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Default test points per sample"), {
      target: { value: "3" },
    });
    fireEvent.change(screen.getByLabelText("Default readings per point"), {
      target: { value: "2" },
    });
    fireEvent.change(screen.getByLabelText("Default contact points per sample"), {
      target: { value: "1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Apply to blank Step quantities" }));

    expect(screen.getByLabelText("Step 1 test points per sample")).toHaveProperty("value", "3");
    expect(screen.getByLabelText("Step 1 readings per point")).toHaveProperty("value", "2");
    expect(screen.getByLabelText("Step 1 contact points per sample")).toHaveProperty("value", "1");
    expect(screen.getByLabelText("Step 2 test points per sample")).toHaveProperty("value", "9");
    expect(screen.getByLabelText("Step 2 readings per point")).toHaveProperty("value", "8");
    expect(screen.getByLabelText("Step 2 contact points per sample")).toHaveProperty("value", "7");
    expect(screen.getByText("Defaults applied to blank Step quantities.")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Save quantities" }));
    await waitFor(() => expect(apiMocks.saveMatrixStepQuantities).toHaveBeenCalledTimes(1));
    expect(apiMocks.saveMatrixStepQuantities.mock.calls[0][2].items).toMatchObject([
      {
        step_sequence: 1,
        test_points_per_sample: "3",
        readings_per_point: "2",
        contact_points_per_sample: "1",
        source: "matrix_step_override",
      },
      {
        step_sequence: 2,
        test_points_per_sample: "9",
        readings_per_point: "8",
        contact_points_per_sample: "7",
        source: "matrix_step_override",
      },
    ]);
  });

  it("replaces the legacy contact editor with the dedicated setup entry", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft_id: "draft-test",
      saved_payload_signature: "saved-signature",
    });
    apiMocks.fetchMatrixStepQuantities.mockResolvedValueOnce({
      project_id: "P1",
      project_matrix_draft_id: "draft-test",
      items: [
        {
          draft_group_id: "group-1",
          draft_row_id: "llcr-row",
          step_sequence: 1,
          step_suffix_note: null,
          raw_token: "1",
          test_item: "LLCR",
          test_points_per_sample: null,
          readings_per_point: null,
          contact_points_per_sample: null,
          total_readings: null,
          source: "manual_required",
          review_required: true,
          review_reason: "Confirm Step quantity values.",
        },
        {
          draft_group_id: "group-1",
          draft_row_id: "visual-row",
          step_sequence: 2,
          step_suffix_note: null,
          raw_token: "2",
          test_item: "Visual Examination",
          test_points_per_sample: null,
          readings_per_point: null,
          contact_points_per_sample: null,
          total_readings: null,
          source: "manual_required",
          review_required: true,
          review_reason: "Confirm Step quantity values.",
        },
      ],
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByRole("heading", { name: "Test points" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Setup" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Save contact plan" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Apply to blank contact targets" })).toBeNull();
  });

  it("keeps persisted legacy contact profiles out of the compact Matrix summary", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft_id: "draft-contact-plan",
      saved_payload_signature: "saved-signature",
    });
    apiMocks.fetchMatrixStepQuantities.mockResolvedValueOnce({
      project_id: "P1",
      project_matrix_draft_id: "draft-contact-plan",
      items: [
        {
          draft_group_id: "group-1",
          draft_row_id: "llcr-row",
          step_sequence: 1,
          step_suffix_note: null,
          raw_token: "1",
          test_item: "LLCR",
          test_points_per_sample: "33",
          readings_per_point: "1",
          contact_points_per_sample: "33",
          total_readings: "33",
          source: "matrix_contact_plan",
          review_required: false,
          review_reason: null,
          contact_plan: {
            contact_kind: "llcr",
            coverage_status: "eligible",
            included: true,
            exclusion_reason: null,
            is_override: false,
            readings_per_sample: "33",
            families: [
              {
                family_id: "high_power_pin",
                family_label: "High Power Pin",
                count_per_sample: "4",
                record_label: "High Power Pin contact",
                record_prefix: "HP",
                included: true,
                is_custom: false,
              },
            ],
          },
        },
      ],
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByRole("heading", { name: "Test points" })).toBeTruthy();
    expect(screen.queryByLabelText("LLCR High Power Pin count per sample")).toBeNull();
    expect(screen.getByRole("button", { name: "Setup" })).toBeTruthy();
  });

  it("does not render persisted overrides as editable Matrix summary inputs", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft_id: "draft-contact-plan",
      saved_payload_signature: "saved-signature",
    });
    apiMocks.fetchMatrixStepQuantities.mockResolvedValueOnce({
      project_id: "P1",
      project_matrix_draft_id: "draft-contact-plan",
      items: [
        {
          draft_group_id: "group-1",
          draft_row_id: "llcr-normal",
          step_sequence: 1,
          step_suffix_note: null,
          raw_token: "1",
          test_item: "LLCR",
          test_points_per_sample: "4",
          readings_per_point: "1",
          contact_points_per_sample: "4",
          total_readings: "4",
          source: "matrix_contact_plan",
          review_required: false,
          review_reason: null,
          contact_plan: {
            contact_kind: "llcr",
            coverage_status: "eligible",
            included: true,
            exclusion_reason: null,
            is_override: false,
            readings_per_sample: "4",
            families: [
              {
                family_id: "high_power_pin",
                family_label: "High Power Pin",
                count_per_sample: "4",
                record_label: "High Power Pin contact",
                record_prefix: "HP",
                included: true,
                is_custom: false,
              },
            ],
          },
        },
        {
          draft_group_id: "group-1",
          draft_row_id: "llcr-override",
          step_sequence: 2,
          step_suffix_note: null,
          raw_token: "2",
          test_item: "LLCR",
          test_points_per_sample: "7",
          readings_per_point: "1",
          contact_points_per_sample: "7",
          total_readings: "7",
          source: "matrix_step_override",
          review_required: false,
          review_reason: null,
          contact_plan: {
            contact_kind: "llcr",
            coverage_status: "manual_override",
            included: true,
            exclusion_reason: null,
            is_override: true,
            readings_per_sample: "7",
            families: [
              {
                family_id: "high_power_pin",
                family_label: "High Power Pin",
                count_per_sample: "7",
                record_label: "High Power Pin contact",
                record_prefix: "HP",
                included: true,
                is_custom: false,
              },
            ],
          },
        },
      ],
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByRole("heading", { name: "Test points" })).toBeTruthy();
    expect(screen.queryByLabelText("LLCR High Power Pin count per sample")).toBeNull();
    expect(screen.getByRole("button", { name: "Setup" })).toBeTruthy();
  });

  it("opens the browser project source chooser without native confirmation", async () => {
    const inputClickSpy = vi
      .spyOn(HTMLInputElement.prototype, "click")
      .mockImplementation(() => {});

    sourcePickerMocks.choose.mockResolvedValue({ kind: "browser", candidates: [], warnings: [], error: null });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));

    expect(window.confirm).not.toHaveBeenCalled();
    expect(inputClickSpy).not.toHaveBeenCalled();
    expect(await screen.findByRole("heading", { name: "Choose a project source" })).toBeTruthy();
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    expect(input.getAttribute("accept")).toBe(".pdf,.doc,.docx");
  });

  it("previews a browser project candidate only after explicit selection", async () => {
    sourcePickerMocks.choose.mockResolvedValue({
      kind: "browser",
      candidates: [{ source_asset_id: "source-1", original_name: "matrix.docx", extension: ".docx", asset_type: "attachment", candidate_kind: "likely_spec_or_matrix", reason: "Matrix keywords found.", stored_file_available: true }],
      warnings: [],
      error: null,
    });
    apiMocks.previewProjectTestPlanMatrixFromSourceCandidate.mockResolvedValue(buildImportPreview());
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    expect(await screen.findByRole("heading", { name: "Choose a project source" })).toBeTruthy();
    expect(apiMocks.previewProjectTestPlanMatrixFromSourceCandidate).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Use this file: matrix.docx" }));
    await waitFor(() => expect(apiMocks.previewProjectTestPlanMatrixFromSourceCandidate).toHaveBeenCalledWith("P1", "source-1"));
    expect(await screen.findByRole("button", { name: "Replace" })).toBeTruthy();
  });

  it("previews a desktop local path and preserves locator values on reparse", async () => {
    sourcePickerMocks.hasDesktop.mockReturnValue(true);
    sourcePickerMocks.choose.mockResolvedValue({
      kind: "selected",
      path: "D:/project/Submitted Material/spec.pdf",
    });
    apiMocks.previewProjectTestPlanMatrixFromPath
      .mockResolvedValueOnce(buildImportPreview({ selected_page_number: 2, selected_page_table_index: 1 }))
      .mockResolvedValueOnce(buildImportPreview({ selected_page_number: 7, selected_page_table_index: 3 }));

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    expect(await screen.findByRole("button", { name: "Replace" })).toBeTruthy();

    fireEvent.change(screen.getByLabelText("Page"), { target: { value: "7" } });
    fireEvent.change(screen.getByLabelText("Table on page"), { target: { value: "3" } });
    fireEvent.change(screen.getByLabelText("Table Title / Content Keyword"), {
      target: { value: "qualification matrix" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Replace" }));

    await waitFor(() => expect(apiMocks.previewProjectTestPlanMatrixFromPath).toHaveBeenCalledTimes(2));
    expect(apiMocks.previewProjectTestPlanMatrixFromPath.mock.calls[1][0]).toEqual({
      source_path: "D:/project/Submitted Material/spec.pdf",
      project_id: "P1",
      page_number: 7,
      page_table_index: 3,
      table_text_query: "qualification matrix",
    });
  });

  it("does not mutate import state when the desktop picker is cancelled", async () => {
    sourcePickerMocks.hasDesktop.mockReturnValue(true);
    sourcePickerMocks.choose.mockResolvedValue({ kind: "cancelled" });
    const inputClickSpy = vi.spyOn(HTMLInputElement.prototype, "click").mockImplementation(() => {});

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));

    await waitFor(() => expect(sourcePickerMocks.choose).toHaveBeenCalledTimes(1));
    expect(inputClickSpy).not.toHaveBeenCalled();
    expect(apiMocks.previewProjectTestPlanMatrixFromPath).not.toHaveBeenCalled();
    expect(apiMocks.previewProjectTestPlanMatrixFromUpload).not.toHaveBeenCalled();
    expect(screen.queryByRole("button", { name: "Replace" })).toBeNull();
  });

  it("shows a blocking Matrix search dialog while the selected Word document is parsed", async () => {
    const deferredPreview = createDeferred<MatrixPreviewResponse>();
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockReturnValueOnce(deferredPreview.promise);

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    fireEvent.change(input, {
      target: {
        files: [
          new File(["docx"], "slow_spec.docx", {
            type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          }),
        ],
      },
    });

    expect(
      await screen.findByRole("alertdialog", { name: "Searching for Matrix" })
    ).toBeTruthy();
    expect(
      screen.getByText("ConnLab is reading the source document and preparing the preview.")
    ).toBeTruthy();

    await act(async () => {
      deferredPreview.resolve(
        buildImportPreview({
          source_document_name: "slow_spec.docx",
          preview_pdf_token: "pdf-token-slow",
        })
      );
      await deferredPreview.promise;
    });

    await waitFor(() =>
      expect(screen.queryByRole("alertdialog", { name: "Searching for Matrix" })).toBeNull()
    );
    expect(await screen.findByRole("button", { name: "Replace" })).toBeTruthy();
  });

  it("opens the import panel with the failure when initial Matrix search fails", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockRejectedValueOnce(new Error("Word parser failed"));

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    fireEvent.change(input, {
      target: {
        files: [
          new File(["docx"], "broken_spec.docx", {
            type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          }),
        ],
      },
    });

    expect(
      await screen.findByRole("alertdialog", { name: "Searching for Matrix" })
    ).toBeTruthy();
    await waitFor(() =>
      expect(screen.queryByRole("alertdialog", { name: "Searching for Matrix" })).toBeNull()
    );
    expect(await screen.findByText("Word parser failed")).toBeTruthy();
    expect(screen.getByText("PDF preview unavailable.")).toBeTruthy();
  });

  it("downloads a Test Record preview from current unsaved Matrix Editor state", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));

    fireEvent.change(screen.getByLabelText("Row 1 method"), {
      target: { value: "Updated unsaved UI method" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Test record" }));

    await waitFor(() =>
      expect(apiMocks.generateMatrixEditorTestRecordDraftDownload).toHaveBeenCalledTimes(1)
    );
    const [projectId, payload] = apiMocks.generateMatrixEditorTestRecordDraftDownload.mock.calls[0];
    expect(projectId).toBe("P1");
    expect(payload.source).toBe("matrix_editor_current_ui_state");
    expect(payload.groups).toEqual([
      {
        group_key: "g1",
        group_label: "1",
        sample_quantity_expression: "5",
      },
    ]);
    expect(payload.rows[0]).toMatchObject({
      test_item: "Visual Examination",
      method: "Updated unsaved UI method",
      condition: "10x min magnification",
      requirement: "No detrimental condition",
      group_values: { g1: "1" },
    });
    expect(screen.getByText("Downloaded unconfirmed Test Record preview.")).toBeTruthy();
  });

  it("keeps Append disabled in import modal", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValueOnce({
      ...buildSessionSeed().source_preview_payload,
      source_document_name: "spec_b.docx",
      preview_pdf_token: "pdf-token-b",
      groups: [
        {
          group_key: "g1",
          group_label: "1",
          source_table_index: 0,
          extraction_status: "loaded",
          sample_size: null,
          sample_quantity_expression: "7",
          sample_note: null,
          steps: [],
        },
      ],
    });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    fireEvent.change(input, {
      target: {
        files: [new File(["docx"], "spec_b.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })],
      },
    });
    const append = await screen.findByRole("button", { name: "Append" });
    expect((append as HTMLButtonElement).disabled).toBe(true);
  });

  it("keeps the committed source document name when import preview is cancelled", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValueOnce({
      ...buildSessionSeed().source_preview_payload,
      source_document_name: "spec_b.docx",
      source_document_path: "D:/spec_b.docx",
      preview_pdf_token: "pdf-token-b",
      groups: [
        {
          group_key: "g1",
          group_label: "1",
          source_table_index: 0,
          extraction_status: "loaded",
          sample_size: null,
          sample_quantity_expression: "7",
          sample_note: null,
          steps: [],
        },
      ],
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await screen.findByText("spec.docx");
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    fireEvent.change(input, {
      target: {
        files: [new File(["docx"], "spec_b.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })],
      },
    });

    await screen.findByRole("button", { name: "Replace" });
    expect(screen.getByText("spec.docx")).toBeTruthy();
    fireEvent.click(screen.getAllByRole("button", { name: "Cancel" })[0]);
    await waitFor(() => expect(screen.queryByRole("button", { name: "Replace" })).toBeNull());
    expect(screen.getByText("spec.docx")).toBeTruthy();
    expect(screen.queryByText("spec_b.docx")).toBeNull();
  });

  it("allows pdf, legacy doc, and docx files from the import selector", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));

    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    expect(input.getAttribute("accept")).toBe(".pdf,.doc,.docx");
  });

  it("imports by Replace directly and does not enter group-selection mode", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValueOnce({
      ...buildSessionSeed().source_preview_payload,
      source_document_name: "spec_b.docx",
      source_document_path: "D:/spec_b.docx",
      preview_pdf_token: "pdf-token-b",
      groups: [
        {
          group_key: "g1",
          group_label: "1",
          source_table_index: 0,
          extraction_status: "loaded",
          sample_size: null,
          sample_quantity_expression: "7",
          sample_note: null,
          steps: [],
        },
      ],
    });
    apiMocks.commitMatrixImport.mockResolvedValueOnce({
      source_import_id: "source-b",
      source_snapshot_id: "snapshot-b",
      selected_group_keys_committed: ["g1"],
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
          project_matrix_draft_id: "draft-b",
          project_id: "P1",
          source_import_id: "source-b",
          source_snapshot_id: "snapshot-b",
          base_confirmed_matrix_id: null,
          status: "draft",
          created_at: "2026-05-28T00:00:00Z",
          updated_at: "2026-05-28T00:00:00Z",
        },
        groups: [
          {
            draft_group_id: "group-b1",
            source_group_snapshot_id: "sg-b1",
            group_order: 1,
            group_key: "g1",
            group_label: "1",
            is_selected: true,
            sample_quantity_expression: "7",
            sample_note: null,
          },
        ],
        rows: [
          {
            draft_row_id: "row-b1",
            source_row_snapshot_id: "sr-b1",
            row_order: 1,
            test_item: "Visual Examination",
            source_section: "1.1",
            method: "EIA-364-18B",
            condition: "10x min magnification",
            requirement: "No detrimental condition",
            is_sample_row: false,
          },
        ],
        cells: [{ draft_cell_id: "cell-b1", draft_row_id: "row-b1", draft_group_id: "group-b1", cell_value: "1" }],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    fireEvent.change(input, {
      target: {
        files: [new File(["docx"], "spec_b.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })],
      },
    });
    fireEvent.click((await screen.findAllByRole("button", { name: "Replace" }))[0]);
    await waitFor(() => expect(apiMocks.commitMatrixImport).toHaveBeenCalledTimes(1));
    expect(screen.getByText("spec_b.docx")).toBeTruthy();
    expect(screen.getByText("Matrix replaced. 1 Method updated; 2 rows need review.")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Selected Groups" })).toBeNull();
  });

  it("auto-reparses stale Replace with the current locator before committing", async () => {
    const firstPreview = buildImportPreview({
      source_document_name: "stale.docx",
      source_document_path: "D:/stale.docx",
      preview_pdf_token: "pdf-token-stale",
    });
    const refreshedPreview = buildImportPreview({
      source_document_name: "fresh.docx",
      source_document_path: "D:/fresh.docx",
      selected_page_number: 2,
      selected_page_table_index: 1,
      preview_pdf_token: "pdf-token-fresh",
      groups: [
        {
          group_key: "g2",
          group_label: "2",
          source_table_index: 0,
          extraction_status: "loaded",
          sample_size: null,
          sample_quantity_expression: "9",
          sample_note: null,
          steps: [],
        },
      ],
    });
    apiMocks.previewProjectTestPlanMatrixFromUpload
      .mockResolvedValueOnce(firstPreview)
      .mockResolvedValueOnce(refreshedPreview);
    apiMocks.commitMatrixImport.mockResolvedValueOnce(buildCommitResponse(refreshedPreview, "9"));

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    fireEvent.change(input, {
      target: {
        files: [new File(["docx"], "stale.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })],
      },
    });
    fireEvent.change(await screen.findByLabelText("Page"), { target: { value: "2" } });
    fireEvent.click(await screen.findByRole("button", { name: "Replace" }));

    await waitFor(() => expect(apiMocks.commitMatrixImport).toHaveBeenCalledTimes(1));
    expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(2);
    expect(apiMocks.previewProjectTestPlanMatrixFromUpload.mock.calls[1][2]).toEqual({
      pageNumber: 2,
      pageTableIndex: 1,
      tableTextQuery: null,
    });
    expect(apiMocks.commitMatrixImport.mock.calls[0][1]).toMatchObject({
      source_document_name: "fresh.docx",
      preview_payload: refreshedPreview,
      selected_group_keys: ["g2"],
    });
  });

  it("keeps stale Replace open and does not commit when auto-reparse fails", async () => {
    const firstPreview = buildImportPreview({ preview_pdf_token: "pdf-token-stale" });
    apiMocks.previewProjectTestPlanMatrixFromUpload
      .mockResolvedValueOnce(firstPreview)
      .mockRejectedValueOnce(new Error("Preview failed"));

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    fireEvent.change(input, {
      target: {
        files: [new File(["docx"], "stale.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })],
      },
    });
    fireEvent.change(await screen.findByLabelText("Table Title / Content Keyword"), { target: { value: "Visual" } });
    fireEvent.click(await screen.findByRole("button", { name: "Replace" }));

    await screen.findByText("Preview failed");
    expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(2);
    expect(apiMocks.commitMatrixImport).not.toHaveBeenCalled();
    expect((screen.getByRole("button", { name: "Replace" }) as HTMLButtonElement).disabled).toBe(false);
  });

  it("shows a precise preview blocker before locator mismatch fallback", async () => {
    const firstPreview = buildImportPreview({ preview_pdf_token: "pdf-token-stale" });
    const blockedPreview = buildImportPreview({
      selected_table_index: null,
      selected_page_number: null,
      selected_page_table_index: null,
      groups: [],
      blockers: ["Selected table 6 is not a valid Matrix table."],
    });
    apiMocks.previewProjectTestPlanMatrixFromUpload
      .mockResolvedValueOnce(firstPreview)
      .mockResolvedValueOnce(blockedPreview);

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    fireEvent.change(input, {
      target: {
        files: [new File(["docx"], "split-header.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })],
      },
    });
    fireEvent.change(await screen.findByLabelText("Page"), { target: { value: "10" } });
    fireEvent.change(await screen.findByLabelText("Table Title / Content Keyword"), { target: { value: "TEST GROUP" } });
    fireEvent.click(await screen.findByRole("button", { name: "Replace" }));

    expect(await screen.findByText("Selected table 6 is not a valid Matrix table.")).toBeTruthy();
    expect(screen.queryByText("Requested page/table did not match a matrix.")).toBeNull();
    expect(apiMocks.commitMatrixImport).not.toHaveBeenCalled();
  });

  it("does not reparse or commit stale Replace when the locator is invalid", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValueOnce(
      buildImportPreview({ preview_pdf_token: "pdf-token-stale" }),
    );

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    fireEvent.change(input, {
      target: {
        files: [new File(["docx"], "stale.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })],
      },
    });
    fireEvent.change(await screen.findByLabelText("Page"), { target: { value: "abc" } });
    fireEvent.click(await screen.findByRole("button", { name: "Replace" }));

    await screen.findByText("Page must be a positive integer.");
    expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(1);
    expect(apiMocks.commitMatrixImport).not.toHaveBeenCalled();
  });

  it("disables locator inputs and import actions while stale Replace is reparsing", async () => {
    const firstPreview = buildImportPreview({ preview_pdf_token: "pdf-token-stale" });
    const deferredPreview = createDeferred<MatrixPreviewResponse>();
    apiMocks.previewProjectTestPlanMatrixFromUpload
      .mockResolvedValueOnce(firstPreview)
      .mockReturnValueOnce(deferredPreview.promise);

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    fireEvent.change(input, {
      target: {
        files: [new File(["docx"], "stale.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })],
      },
    });
    fireEvent.change(await screen.findByLabelText("Page"), { target: { value: "2" } });
    fireEvent.click(await screen.findByRole("button", { name: "Replace" }));

    await waitFor(() => expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(2));
    expect((screen.getByLabelText("Page") as HTMLInputElement).disabled).toBe(true);
    expect((screen.getByLabelText("Table on page") as HTMLInputElement).disabled).toBe(true);
    expect((screen.getByLabelText("Table Title / Content Keyword") as HTMLInputElement).disabled).toBe(true);
    expect(screen.getByText("Reparsing...")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Replace" }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByRole("button", { name: "Append" }) as HTMLButtonElement).disabled).toBe(true);

    await act(async () => {
      deferredPreview.resolve(buildImportPreview({ selected_page_number: 2, selected_page_table_index: 1 }));
      await deferredPreview.promise;
    });
  });

  it("prefills Method Condition and Requirement from source preview rows", async () => {
    const seed = buildSessionSeed();
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...seed,
      source_preview_payload: {
        ...seed.source_preview_payload,
        rows: [
          {
            ...seed.source_preview_payload.rows[0],
            test_item: "Contact Resistance (Low Level)",
            source_section: "6.1",
            method: "EIA-364-23D",
            condition: "20mV max, 100mA max",
            requirement: "Initial <= 0.25 milliohms",
          },
        ],
      },
      editor_draft: {
        ...seed.editor_draft,
        rows: [],
        cells: [],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByDisplayValue("EIA-364-23D")).toBeTruthy();
    expect(screen.getByDisplayValue("20mV max, 100mA max")).toBeTruthy();
    const requirement = screen.getByLabelText("Row 1 requirement") as HTMLInputElement;
    expect(requirement.value).toBe("Initial <= 0.25 milliohms");
    fireEvent.change(requirement, { target: { value: "Initial <= 0.30 milliohms" } });
    expect(requirement.value).toBe("Initial <= 0.30 milliohms");
  });

  it("keeps MCR source review metadata out of the main editing table", async () => {
    const seed = buildSessionSeed();
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...seed,
      source_preview_payload: {
        ...seed.source_preview_payload,
        rows: [
          {
            ...seed.source_preview_payload.rows[0],
            test_item: "Visual Examination",
            method: "EIA-364-18B",
            condition: "10x min magnification",
            requirement: "No detrimental condition",
            detail_extraction_status: "matched",
            detail_extraction_notes: ["template-fallback-method"],
          },
          {
            source_row_index: 2,
            test_item: "Temperature rise",
            source_section: "6.2",
            method: "EIA-364-70",
            condition: "Method 2, 13.5A",
            requirement: "≤ 30 ℃",
            detail_extraction_status: "matched",
            detail_extraction_notes: [],
            group_tokens: { "1": "2", g1: "2" },
            is_sample_row: false,
          },
          {
            source_row_index: 3,
            test_item: "Custom test",
            source_section: "6.3",
            method: "",
            condition: "",
            requirement: "",
            detail_extraction_status: "missing",
            detail_extraction_notes: ["unresolved"],
            group_tokens: { "1": "3", g1: "3" },
            is_sample_row: false,
          },
        ],
      },
      editor_draft: {
        ...seed.editor_draft,
        rows: [],
        cells: [],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await screen.findByDisplayValue("EIA-364-18B");
    expect(screen.queryByText("Template")).toBeNull();
    expect(screen.queryByText("Spec")).toBeNull();
    expect(screen.queryByText("Needs review")).toBeNull();
    expect(screen.queryByLabelText("Row 1 method review status")).toBeNull();

    const methodInput = screen.getByLabelText("Row 1 method");
    fireEvent.change(methodInput, { target: { value: "EIA-364-18C" } });
    expect((methodInput as HTMLTextAreaElement).value).toBe("EIA-364-18C");
    expect(screen.queryByText("Edited")).toBeNull();
  });

  it("supports inline include toggles and selected-only filter", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft: {
        ...buildSessionSeed().editor_draft,
        groups: [
          buildSessionSeed().editor_draft.groups[0],
          {
            draft_group_id: "group-2",
            source_group_snapshot_id: "sg-2",
            group_order: 2,
            group_key: "g2",
            group_label: "2",
            is_selected: true,
            sample_quantity_expression: "6",
            sample_note: null,
          },
        ],
        cells: [
          { draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1" },
          { draft_row_id: "row-1", draft_group_id: "group-2", cell_value: "2" },
        ],
      },
    });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    const includeChecks = await screen.findAllByRole("checkbox", { name: /^Include group/ });
    fireEvent.click(includeChecks[1]);
    fireEvent.click(screen.getByRole("checkbox", { name: "Show selected groups only" }));
    expect(screen.getByText("Show selected groups only")).toBeTruthy();
    expect(screen.queryByLabelText("Row 1 2")).toBeNull();
    expect(screen.getByLabelText("Row 1 1")).toBeTruthy();
  });

  it("splits LLCR multi-step requirement into initial and delta-r forms", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft: {
        ...buildSessionSeed().editor_draft,
        rows: [
          {
            draft_row_id: "row-1",
            source_row_snapshot_id: "sr-1",
            row_order: 1,
            test_item: "Contact Resistance (Low Level)",
            source_section: "6.1",
            method: "EIA-364-23D",
            condition: "20mV max, 100mA max",
            requirement: "Initial <= 0.25 m惟; R<= 0.17 m惟",
            is_sample_row: false,
          },
          {
            draft_row_id: "row-2",
            source_row_snapshot_id: "sr-2",
            row_order: 2,
            test_item: "Contact Resistance (Low Level)",
            source_section: "6.1",
            method: "EIA-364-23D",
            condition: "20mV max, 100mA max",
            requirement: "Initial <= 0.25 m惟; R<= 0.17 m惟",
            is_sample_row: false,
          },
        ],
        cells: [
          { draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1" },
          { draft_row_id: "row-2", draft_group_id: "group-1", cell_value: "2" },
        ],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    const firstStepRequirement = await screen.findByLabelText("Step 1 requirement");
    const secondStepRequirement = await screen.findByLabelText("Step 2 requirement");
    expect((firstStepRequirement as HTMLTextAreaElement).value).toBe("<= 0.25 m惟");
    expect((secondStepRequirement as HTMLTextAreaElement).value).toBe("ΔR <= 0.17 m惟");
  });

  it("restores unchecked source groups after re-entering from Workbench", async () => {
    const seed = buildSessionSeed();
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...seed,
      source_preview_payload: {
        ...seed.source_preview_payload,
        rows: [
          {
            ...seed.source_preview_payload.rows[0],
            group_tokens: { "1": "1", g1: "1", "2": "2", g2: "2" },
          },
        ],
        groups: [
          seed.source_preview_payload.groups[0],
          {
            group_key: "g2",
            group_label: "2",
            source_table_index: 0,
            extraction_status: "loaded",
            sample_size: null,
            sample_quantity_expression: "6",
            sample_note: null,
            steps: [],
          },
        ],
      },
      editor_draft: {
        ...seed.editor_draft,
        groups: [seed.editor_draft.groups[0]],
        cells: [{ draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1" }],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByLabelText("Row 1 1")).toBeTruthy();
    expect(screen.getByLabelText("Row 1 2")).toBeTruthy();
    const includeGroup2 = screen.getByRole("checkbox", { name: "Include group 2" }) as HTMLInputElement;
    expect(includeGroup2.checked).toBe(false);
  });

  it("normalizes Group prefix in source-backed group labels", async () => {
    const seed = buildSessionSeed();
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...seed,
      source_preview_payload: {
        ...seed.source_preview_payload,
        rows: [
          {
            ...seed.source_preview_payload.rows[0],
            group_tokens: { "Group 8a": "8", g8a: "8" },
          },
        ],
        groups: [
          {
            group_key: "g8a",
            group_label: "Group 8a",
            source_table_index: 0,
            extraction_status: "loaded",
            sample_size: null,
            sample_quantity_expression: "6",
            sample_note: null,
            steps: [],
          },
        ],
      },
      editor_draft: {
        ...seed.editor_draft,
        groups: [
          {
            draft_group_id: "group-8a",
            source_group_snapshot_id: "sg-8a",
            group_order: 1,
            group_key: "g8a",
            group_label: "Group 8a",
            is_selected: true,
            sample_quantity_expression: "6",
            sample_note: null,
          },
        ],
        cells: [{ draft_row_id: "row-1", draft_group_id: "group-8a", cell_value: "8" }],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    expect(await screen.findByRole("checkbox", { name: "Include group 8a" })).toBeTruthy();
    expect(screen.queryByRole("checkbox", { name: "Include group Group 8a" })).toBeNull();
  });

  it("allows numeric parenthetical step note tokens and shows their note", async () => {
    const seed = buildSessionSeed();
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...seed,
      source_preview_payload: {
        ...seed.source_preview_payload,
        rows: [
          {
            ...seed.source_preview_payload.rows[0],
            group_tokens: { "1": "1,2,3,4(1)", g1: "1,2,3,4(1)" },
          },
        ],
        groups: [
          {
            ...seed.source_preview_payload.groups[0],
            steps: [
              {
                sequence: 4,
                raw_token: "4(1)",
                suffix_note: "(1)",
                test_item: "Vibration",
                source_section: "8.8",
                source_note: "(1) Circuit continuity monitoring is performed during conditioning.",
                source_note_origin: "step",
                source_item_section_note: null,
                source_table_index: 8,
                source_row_index: 18,
                duration_status: "deferred",
                warnings: [],
              },
            ],
          },
        ],
      },
      editor_draft: {
        ...seed.editor_draft,
        cells: [{ draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1,2,3,4(1)" }],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect((await screen.findByLabelText("Row 1 1") as HTMLInputElement).value).toBe("1,2,3,4(1)");
    expect(screen.getByText("4(1) Circuit continuity monitoring is performed during conditioning.")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(false);
  });

  it("accepts full-width numeric note tokens and ignores invalid tokens in unselected groups", async () => {
    const seed = buildSessionSeed();
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...seed,
      editor_draft: {
        ...seed.editor_draft,
        groups: [
          seed.editor_draft.groups[0],
          {
            draft_group_id: "group-2",
            source_group_snapshot_id: "sg-2",
            group_order: 2,
            group_key: "g2",
            group_label: "2",
            is_selected: false,
            sample_quantity_expression: "6",
            sample_note: null,
          },
        ],
        cells: [
          { draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1,2,3,4\uFF081\uFF09" },
          { draft_row_id: "row-1", draft_group_id: "group-2", cell_value: "A" },
        ],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect((await screen.findByLabelText("Row 1 1") as HTMLInputElement).value).toBe("1,2,3,4\uFF081\uFF09");
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(false);
    expect(screen.queryByText(/Only digits,/)).toBeNull();
  });

  it("treats Chinese commas, ideographic commas, PDF comma mojibake, and spaces as step separators", async () => {
    const seed = buildSessionSeed();
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...seed,
      editor_draft: {
        ...seed.editor_draft,
        cells: [{ draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1、8 2Ўў3,4\uFF081\uFF09 5 6 7" }],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect((await screen.findByLabelText("Row 1 1") as HTMLInputElement).value).toBe("1、8 2Ўў3,4\uFF081\uFF09 5 6 7");
    expect(screen.getByText("Group 1: 8 steps")).toBeTruthy();
    expect(screen.getByLabelText("Step 4 description")).toBeTruthy();
    expect(screen.getByLabelText("Step 8 description")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(false);
    expect(screen.queryByText(/Only digits,/)).toBeNull();
  });

  it("lets source instruction rows be marked as non-test rows so their text does not block confirm", async () => {
    const seed = buildSessionSeed();
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...seed,
      editor_draft: {
        ...seed.editor_draft,
        rows: [
          seed.editor_draft.rows[0],
          {
            draft_row_id: "row-2",
            source_row_snapshot_id: "sr-2",
            row_order: 2,
            test_item: "鏍峰搧鐘舵€佸拰閫夋嫨璇存槑",
            source_section: null,
            method: null,
            condition: null,
            requirement: null,
            is_sample_row: false,
          },
        ],
        cells: [
          { draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1" },
          { draft_row_id: "row-2", draft_group_id: "group-1", cell_value: "connector sample note" },
        ],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    const instructionRowButton = await screen.findByRole("button", { name: "Select row 2" });
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.contextMenu(instructionRowButton);
    fireEvent.click(screen.getByRole("button", { name: "Mark as Information" }));

    expect(screen.queryByRole("button", { name: "Select row 2" })).toBeNull();
    const sampleRowButton = screen.getByRole("button", { name: "Select sample/instruction row 2" });
    expect(sampleRowButton).toBeTruthy();
    expect(screen.getByLabelText("Row 2 method").className).not.toContain("is-empty-required");
    expect(screen.getByLabelText("Row 2 condition").className).not.toContain("is-empty-required");
    expect(screen.getByLabelText("Row 2 requirement").className).not.toContain("is-empty-required");
    fireEvent.contextMenu(sampleRowButton);
    expect(screen.getByRole("button", { name: "Mark as Test Item" })).toBeTruthy();
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(true);
    await waitFor(
      () => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 }
    );
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(false);
    expect(screen.queryByText(/Only digits,/)).toBeNull();
  });

  it("hides inline group checkboxes while selected-only filtering is active", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByRole("checkbox", { name: "Include group 1" })).toBeTruthy();
    fireEvent.click(screen.getByRole("checkbox", { name: "Show selected groups only" }));

    expect(screen.queryByRole("checkbox", { name: "Include group 1" })).toBeNull();
    expect(screen.getByRole("checkbox", { name: "Show selected groups only" })).toBeTruthy();
  });

  it("uses Exclude group for source groups and keeps the source group visible", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    const includeGroup1 = await screen.findByRole("checkbox", { name: "Include group 1" });
    fireEvent.contextMenu(includeGroup1.closest("th") as HTMLElement);

    expect(screen.queryByRole("button", { name: "Delete group" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Exclude group" }));

    const updatedIncludeGroup1 = screen.getByRole("checkbox", { name: "Include group 1" }) as HTMLInputElement;
    expect(updatedIncludeGroup1.checked).toBe(false);
    expect(screen.getByLabelText("Row 1 1")).toBeTruthy();
  });

  it("allows deleting manually inserted groups from the editor table", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    const includeGroup1 = await screen.findByRole("checkbox", { name: "Include group 1" });
    fireEvent.contextMenu(includeGroup1.closest("th") as HTMLElement);
    fireEvent.click(screen.getByRole("button", { name: "Insert right" }));
    expect(document.querySelectorAll(".matrix-editor-group-band")).toHaveLength(2);

    const manualGroupHeader = document.querySelectorAll(".matrix-editor-group-band")[1] as HTMLElement;
    fireEvent.contextMenu(manualGroupHeader);
    expect(screen.queryByRole("button", { name: "Exclude group" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Delete group" }));

    expect(document.querySelectorAll(".matrix-editor-group-band")).toHaveLength(1);
  });

  it("disables deleting source rows but allows deleting manually inserted rows", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    const sourceRowButton = await screen.findByRole("button", { name: "Select row 1" });
    fireEvent.contextMenu(sourceRowButton);
    expect((screen.getByRole("button", { name: "Delete row" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByRole("button", { name: "Insert below" }));

    const manualRowButton = await screen.findByRole("button", { name: "Select row 2" });
    fireEvent.contextMenu(manualRowButton);
    const deleteRowButton = screen.getByRole("button", { name: "Delete row" }) as HTMLButtonElement;
    expect(deleteRowButton.disabled).toBe(false);
    fireEvent.click(deleteRowButton);

    expect(screen.queryByRole("button", { name: "Select row 2" })).toBeNull();
  });

  it("shows a blocking status when sample guard blocks confirm", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    const sample = await screen.findByLabelText("Samples 1");
    fireEvent.change(sample, { target: { value: "sample only" } });
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("Sample quantity is required for selected groups.").length).toBe(1);
    expect(document.querySelector(".matrix-editor-save-status")?.textContent ?? "").not.toContain(
      "Sample quantity is required for selected groups."
    );
    await waitFor(() => expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(0));
  });

  it("keeps closed projects read-only and blocks Matrix confirmation", async () => {
    runtimeModelState.lifecycle = {
      ...runtimeModelState.lifecycle,
      lifecycle_state: "closed",
      closure_type: "completed",
      status: "closed",
      allowed_actions: [],
      readonly: true,
    };

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={vi.fn()} />);

    expect(await screen.findByText("Project closed: Completed")).toBeTruthy();
    expect(screen.getByLabelText("Row 1 test item")).toHaveProperty(
      "disabled",
      true
    );
    const confirmButton = screen.getByRole("button", { name: "Confirm Matrix" });
    expect(screen.getByRole("button", { name: "Import Matrix" })).toHaveProperty(
      "disabled",
      true
    );
    expect(sourcePickerMocks.choose).not.toHaveBeenCalled();
    expect(confirmButton).toHaveProperty("disabled", true);
    fireEvent.click(confirmButton);
    expect(apiMocks.confirmMatrixEditorSession).not.toHaveBeenCalled();
    expect(apiMocks.saveMatrixEditorSessionDraft).not.toHaveBeenCalled();
  });

  it("keeps transient autosave progress out of the Matrix grid layout", async () => {
    apiMocks.saveMatrixEditorSessionDraft.mockImplementationOnce(
      () => new Promise(() => {})
    );
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.change(await screen.findByLabelText("Row 1 method"), {
      target: { value: "Updated method before confirm" },
    });

    await waitFor(
      () => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 }
    );
    expect(screen.queryByText("Preparing confirm...")).toBeNull();
    expect(document.querySelector(".matrix-editor-save-status")?.textContent ?? "").not.toContain(
      "Preparing confirm..."
    );
  });

  it("does not autosave before the first Matrix authority exists", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      active_confirmed_matrix_id: null,
      active_confirmed_revision: null,
      active_source_import_id: null,
      active_source_snapshot_id: null,
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.change(await screen.findByLabelText("Row 1 method"), {
      target: { value: "Updated first authority method" },
    });

    await new Promise((resolve) => window.setTimeout(resolve, 1000));
    expect(apiMocks.saveMatrixEditorSessionDraft).not.toHaveBeenCalled();
    expect(document.querySelector(".matrix-editor-save-status")?.textContent ?? "").not.toContain(
      "Save failed. Retry before confirming."
    );
    expect(screen.getByRole("button", { name: "Confirm Matrix" })).toHaveProperty(
      "disabled",
      false
    );
  });

  it("sends day and schedule planning fields when confirming Matrix", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.change(await screen.findByLabelText("Row 1 day"), { target: { value: "0.5x" } });
    fireEvent.change(screen.getByLabelText("Post-test buffer"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Sample received"), { target: { value: "2026-06-01" } });
    fireEvent.change(screen.getByLabelText("Planned start"), { target: { value: "2026-06-02" } });
    fireEvent.change(screen.getByLabelText("Test complete"), { target: { value: "2026-06-03" } });
    fireEvent.change(screen.getByLabelText("Estimated completion"), { target: { value: "2026-06-04" } });
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(true);
    await waitFor(
      () => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 }
    );
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));

    await waitFor(() => expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(1));
    const saveRequest = apiMocks.saveMatrixEditorSessionDraft.mock.calls[0][1];
    expect(saveRequest.rows[0].day_expression).toBe("0.5x");
    const request = apiMocks.confirmMatrixEditorSession.mock.calls[0][1];
    expect(request.expected_editor_draft_id).toBe("editor-draft-1");
    expect(request.expected_saved_payload_signature).toBe("saved-signature-1");
    expect(request.pre_test_buffer_days).toBeNull();
    expect(request.post_test_buffer_days).toBe("1");
    expect(request.sample_received_date).toBe("2026-06-01");
    expect(request.planned_test_start_date).toBe("2026-06-02");
    expect(request.planned_test_complete_date).toBe("2026-06-03");
    expect(request.estimated_completion_date).toBe("2026-06-04");
    expect(request.rows[0].day_expression).toBe("0.5x");
  });

  it("waits for in-flight autosave before discarding on Cancel", async () => {
    const resolveSaveRef: {
      current:
        | ((value: {
            editor_draft_id: string;
            draft_status: "current";
            draft_updated_at: string;
            saved_payload_signature: string;
            active_confirmed_matrix_id: string;
            active_confirmed_revision: number;
          }) => void)
        | null;
    } = { current: null };
    apiMocks.saveMatrixEditorSessionDraft.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveSaveRef.current = resolve;
        })
    );
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

    fireEvent.change(await screen.findByLabelText("Row 1 method"), {
      target: { value: "Updated method before cancel" },
    });
    await waitFor(
      () => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 }
    );
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onBackToWorkbench).toHaveBeenCalledTimes(0);

    resolveSaveRef.current?.({
      editor_draft_id: "editor-draft-cancel",
      draft_status: "current",
      draft_updated_at: "2026-06-14T00:00:00Z",
      saved_payload_signature: "cancel-signature",
      active_confirmed_matrix_id: "confirmed-1",
      active_confirmed_revision: 3,
    });

    await waitFor(() => {
      expect(apiMocks.discardMatrixEditorSessionDraft).toHaveBeenCalledWith("P1", {
        expected_editor_draft_id: "editor-draft-cancel",
        expected_saved_payload_signature: "cancel-signature",
      });
      expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    });
  });

  it("does not hang Cancel when the in-flight autosave never finishes", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft_id: "editor-draft-existing",
      draft_status: "current",
      loaded_source: "draft",
      draft_updated_at: "2026-06-14T00:00:00Z",
      saved_payload_signature: "existing-signature",
    });
    apiMocks.saveMatrixEditorSessionDraft.mockImplementationOnce(
      () => new Promise(() => {})
    );
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

    fireEvent.change(await screen.findByLabelText("Row 1 method"), {
      target: { value: "Updated method before hanging cancel" },
    });
    await waitFor(
      () => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 }
    );
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    await waitFor(
      () => {
        expect(apiMocks.discardMatrixEditorSessionDraft).toHaveBeenCalledWith("P1", {
          expected_editor_draft_id: "editor-draft-existing",
          expected_saved_payload_signature: "existing-signature",
        });
        expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
      },
      { timeout: 2500 }
    );
    expect(apiMocks.saveMatrixEditorSessionDraft.mock.calls[0][2]?.signal.aborted).toBe(true);
  });

  it("stays in Matrix Editor and surfaces an error when Cancel discard fails", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft_id: "editor-draft-existing",
      draft_status: "current",
      loaded_source: "draft",
      draft_updated_at: "2026-06-14T00:00:00Z",
      saved_payload_signature: "existing-signature",
    });
    apiMocks.discardMatrixEditorSessionDraft.mockRejectedValueOnce(
      new Error("Matrix draft changed before cancel.")
    );
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

    fireEvent.click(await screen.findByRole("button", { name: "Cancel" }));

    await waitFor(() => {
      expect(apiMocks.discardMatrixEditorSessionDraft).toHaveBeenCalledWith("P1", {
        expected_editor_draft_id: "editor-draft-existing",
        expected_saved_payload_signature: "existing-signature",
      });
      expect(onBackToWorkbench).toHaveBeenCalledTimes(0);
    });
    expect(screen.getByText("Matrix draft changed before cancel.")).toBeTruthy();
  });

  it("blocks confirm when schedule planning dates are insufficient", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.change(await screen.findByLabelText("Row 1 day"), { target: { value: "3" } });
    fireEvent.change(screen.getByLabelText("Sample received"), { target: { value: "2026-06-01" } });
    fireEvent.change(screen.getByLabelText("Planned start"), { target: { value: "2026-06-01" } });
    fireEvent.change(screen.getByLabelText("Test complete"), { target: { value: "2026-06-02" } });
    fireEvent.change(screen.getByLabelText("Estimated completion"), { target: { value: "2026-06-02" } });

    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("Test complete is earlier than planned start plus critical group days.").length).toBeGreaterThan(0);
    await waitFor(() => expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(0));
  });

  it("returns to Workbench when confirm has no Matrix changes", async () => {
    apiMocks.confirmMatrixEditorSession.mockResolvedValueOnce({
      publish_status: "no_change",
      message: "No Matrix changes to confirm.",
      confirmed_snapshot: null,
    });
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);
    fireEvent.click(await screen.findByRole("button", { name: "Confirm Matrix" }));
    await waitFor(() => {
      expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(1);
      expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    });
  });

  it("rebases stale confirm and returns to workbench", async () => {
    apiMocks.confirmMatrixEditorSession
      .mockRejectedValueOnce(new ApiRequestError("stale", 409, { code: "active_matrix_changed", message: "stale" }))
      .mockResolvedValueOnce({ publish_status: "published", message: "Matrix confirmed (v5).", confirmed_snapshot: null });
    apiMocks.fetchMatrixEditorSession
      .mockResolvedValueOnce(buildSessionSeed())
      .mockResolvedValueOnce({
        ...buildSessionSeed(),
        active_confirmed_matrix_id: "confirmed-2",
        active_confirmed_revision: 4,
      });
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);
    fireEvent.click(await screen.findByRole("button", { name: "Confirm Matrix" }));
    await waitFor(() => {
      expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(2);
      expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    });
  });
});

