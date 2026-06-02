import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MatrixEditorWorkspace } from "./MatrixEditorWorkspace";
import { ApiRequestError } from "../../api/client";

const apiMocks = vi.hoisted(() => ({
  fetchMatrixEditorSession: vi.fn(),
  confirmMatrixEditorSession: vi.fn(),
  previewProjectTestPlanMatrixFromUpload: vi.fn(),
  commitMatrixImport: vi.fn(),
  matrixPreviewPdfUrl: vi.fn((token: string) => `/api/pdf/${token}`),
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
    confirmMatrixEditorSession: apiMocks.confirmMatrixEditorSession,
    previewProjectTestPlanMatrixFromUpload: apiMocks.previewProjectTestPlanMatrixFromUpload,
    commitMatrixImport: apiMocks.commitMatrixImport,
    matrixPreviewPdfUrl: apiMocks.matrixPreviewPdfUrl,
  };
});

vi.mock("../project-workbench/useProjectRuntimeConsoleModel", () => ({
  useProjectRuntimeConsoleModel: () => ({
    project: { product_name: "Connector A", business_unit: "BU-1", requestor: "Alice" },
    latestLtr: "LTR-0001",
    matrixAuthorityDraft: { source_document_name: "EIA-364 Qualification Matrix" },
    runtimeAuthoritySync: {
      projectionMatrixReference: "matrix-ref-1",
      authorityVersion: { confirmed_revision: 1 },
    },
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

describe("MatrixEditorWorkspace TASK_279 flow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiMocks.fetchMatrixEditorSession.mockResolvedValue(buildSessionSeed());
    apiMocks.confirmMatrixEditorSession.mockResolvedValue({
      publish_status: "published",
      message: "Matrix confirmed (v4).",
      confirmed_snapshot: null,
    });
    vi.spyOn(window, "confirm").mockReturnValue(true);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    cleanup();
  });

  it("shows Import Matrix in the header and completion actions in a sticky footer", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));
    expect(screen.getByText("spec.docx")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Import Matrix" })).toBeTruthy();
    const completionDock = screen.getByRole("contentinfo", { name: "Matrix editor completion actions" });
    expect((completionDock as HTMLElement).classList.contains("matrix-editor-completion-dock")).toBe(true);
    expect(screen.getByRole("button", { name: "Cancel" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Confirm Matrix" })).toBeTruthy();
    expect(screen.queryByText("Confirm As Active Matrix")).toBeNull();
    expect(screen.queryByText("Create Revision Draft")).toBeNull();
    expect(screen.queryByText("Confirm Revision")).toBeNull();
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
    expect(screen.queryByRole("button", { name: "Selected Groups" })).toBeNull();
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
    expect(screen.queryByText("Only digits and commas are allowed (extended tokens: 3(a), 4(1), 6#, 10*).")).toBeNull();
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
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(false);
    expect(screen.queryByText("Only digits and commas are allowed (extended tokens: 3(a), 4(1), 6#, 10*).")).toBeNull();
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

  it("sends day and schedule planning fields when confirming Matrix", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.change(await screen.findByLabelText("Row 1 day"), { target: { value: "0.5x" } });
    fireEvent.change(screen.getByLabelText("Post-test buffer"), { target: { value: "1" } });
    fireEvent.change(screen.getByLabelText("Sample received"), { target: { value: "2026-06-01" } });
    fireEvent.change(screen.getByLabelText("Planned start"), { target: { value: "2026-06-02" } });
    fireEvent.change(screen.getByLabelText("Test complete"), { target: { value: "2026-06-03" } });
    fireEvent.change(screen.getByLabelText("Estimated completion"), { target: { value: "2026-06-04" } });
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));

    await waitFor(() => expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(1));
    const request = apiMocks.confirmMatrixEditorSession.mock.calls[0][1];
    expect(request.pre_test_buffer_days).toBeNull();
    expect(request.post_test_buffer_days).toBe("1");
    expect(request.sample_received_date).toBe("2026-06-01");
    expect(request.planned_test_start_date).toBe("2026-06-02");
    expect(request.planned_test_complete_date).toBe("2026-06-03");
    expect(request.estimated_completion_date).toBe("2026-06-04");
    expect(request.rows[0].day_expression).toBe("0.5x");
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

