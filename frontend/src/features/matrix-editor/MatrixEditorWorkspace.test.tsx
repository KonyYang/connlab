import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MatrixEditorWorkspace } from "./MatrixEditorWorkspace";

const apiMocks = vi.hoisted(() => ({
  listProjectMatrixDrafts: vi.fn(),
  getProjectMatrixDraft: vi.fn(),
  saveProjectMatrixDraft: vi.fn(),
  confirmProjectMatrixDraft: vi.fn(),
  createMatrixRevisionDraft: vi.fn(),
  confirmProjectMatrixRevisionDraft: vi.fn(),
  previewProjectTestPlanMatrixFromUpload: vi.fn(),
  commitMatrixImport: vi.fn(),
  matrixPreviewPdfUrl: vi.fn((token: string) => token),
}));

vi.mock("../../api/client", () => apiMocks);

vi.mock("../project-workbench/useProjectRuntimeConsoleModel", () => ({
  useProjectRuntimeConsoleModel: () => ({
    project: {
      product_name: "Connector A",
      business_unit: "BU-1",
      requestor: "Alice",
    },
    latestLtr: "LTR-0001",
    runtimeAuthoritySync: {
      projectionMatrixReference: "matrix-ref-1",
    },
    error: null,
  }),
}));

type DraftOverrides = {
  testItem?: string;
  updatedAt?: string;
};

function buildRevisionDraft(overrides: DraftOverrides = {}) {
  const testItem = overrides.testItem ?? "Visual Examination";
  return {
    record: {
      project_matrix_draft_id: "draft-1",
      project_id: "P1",
      source_import_id: null,
      source_snapshot_id: "snapshot-1",
      base_confirmed_matrix_id: "confirmed-1",
      status: "draft",
      created_at: "2026-05-23T00:00:00Z",
      updated_at: overrides.updatedAt ?? "2026-05-23T00:00:00Z",
    },
    groups: [
      {
        draft_group_id: "group-1",
        source_group_snapshot_id: "src-group-1",
        group_order: 1,
        group_key: "g1",
        group_label: "A",
        is_selected: true,
        sample_quantity_expression: "5",
        sample_note: null,
      },
    ],
    rows: [
      {
        draft_row_id: "row-1",
        source_row_snapshot_id: "src-row-1",
        row_order: 1,
        test_item: testItem,
        source_section: "6.1",
        method: "EIA-364-18B",
        condition: "10x min magnification",
        requirement: "No detrimental condition",
        is_sample_row: false,
      },
    ],
    cells: [
      {
        draft_cell_id: "cell-1",
        draft_row_id: "row-1",
        draft_group_id: "group-1",
        cell_value: "1",
      },
    ],
  };
}

describe("MatrixEditorWorkspace revision confirm guard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    apiMocks.matrixPreviewPdfUrl.mockImplementation((token: string) => `/api/pdf/${token}`);
    apiMocks.listProjectMatrixDrafts.mockResolvedValue([
      {
        project_matrix_draft_id: "draft-1",
        project_id: "P1",
        source_import_id: null,
        source_snapshot_id: "snapshot-1",
        base_confirmed_matrix_id: "confirmed-1",
        status: "draft",
        created_at: "2026-05-23T00:00:00Z",
        updated_at: "2026-05-23T00:00:00Z",
      },
    ]);
    apiMocks.getProjectMatrixDraft.mockResolvedValue(buildRevisionDraft());
    apiMocks.saveProjectMatrixDraft.mockResolvedValue(
      buildRevisionDraft({
        testItem: "Visual Examination Updated",
        updatedAt: "2026-05-23T00:01:00Z",
      })
    );
    apiMocks.confirmProjectMatrixRevisionDraft.mockResolvedValue({
      version: {
        confirmed_matrix_id: "confirmed-2",
        project_id: "P1",
        project_matrix_draft_id: "draft-1",
        source_import_id: "source-1",
        source_snapshot_id: "snapshot-1",
        confirmed_revision: 2,
        is_active_authority: true,
        status: "active",
        confirmed_by: "connlab-operator",
        confirmed_at: "2026-05-23T00:02:00Z",
        superseded_by_confirmed_matrix_id: null,
        superseded_at: null,
        superseded_reason: null,
      },
      groups: [],
      rows: [],
      cells: [],
    });
    apiMocks.confirmProjectMatrixDraft.mockResolvedValue({
      version: {
        confirmed_matrix_id: "confirmed-1",
        project_id: "P1",
        project_matrix_draft_id: "draft-1",
        source_import_id: "source-1",
        source_snapshot_id: "snapshot-1",
        confirmed_revision: 1,
        is_active_authority: true,
        status: "active",
        confirmed_by: "connlab-operator",
        confirmed_at: "2026-05-23T00:02:00Z",
        superseded_by_confirmed_matrix_id: null,
        superseded_at: null,
        superseded_reason: null,
      },
      groups: [],
      rows: [],
      cells: [],
    });
    vi.spyOn(window, "confirm").mockReturnValue(true);
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValue({
      project_id: "P1",
      source_document_path: "C:/specs/spec.docx",
      source_document_name: "spec.docx",
      source_format: ".docx",
      capability_status: "ok",
      generated_at: "2026-05-23T00:00:00Z",
      selected_table_index: 0,
      selected_page_number: 2,
      selected_page_table_index: 1,
      candidate_tables: [],
      preview_pdf_token: null,
      rows: [
        {
          source_row_index: 1,
          test_item: "Visual Examination",
          source_section: "6.1",
          group_tokens: { "Group A": "1", "Group B": "2" },
          is_sample_row: false,
        },
      ],
      groups: [
        {
          group_key: "g1",
          group_label: "Group A",
          source_table_index: 0,
          extraction_status: "ok",
          sample_quantity_expression: "5",
          sample_note: null,
          steps: [],
        },
        {
          group_key: "g2",
          group_label: "Group B",
          source_table_index: 0,
          extraction_status: "ok",
          sample_quantity_expression: "3",
          sample_note: null,
          steps: [],
        },
      ],
      warnings: [],
      blockers: [],
    });
    apiMocks.commitMatrixImport.mockResolvedValue({
      source_import_id: "smi-1",
      source_snapshot_id: "sms-1",
      selected_group_keys_committed: ["g1"],
      commit_status: "created",
      project_matrix_draft: buildRevisionDraft(),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    cleanup();
  });

  it("auto-saves unsaved edits and re-enables confirm after save", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const confirmButton = screen.getByRole("button", { name: "Confirm Revision" });
    const createRevisionButton = screen.getByRole("button", { name: "Create Revision Draft" });
    expect(confirmButton.hasAttribute("disabled")).toBe(false);
    expect(createRevisionButton.hasAttribute("disabled")).toBe(false);

    const rowItem = screen.getByLabelText("Row 1 test item");
    let resolveSave: ((value: ReturnType<typeof buildRevisionDraft>) => void) | undefined;
    apiMocks.saveProjectMatrixDraft.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveSave = resolve as (value: ReturnType<typeof buildRevisionDraft>) => void;
        })
    );
    fireEvent.change(rowItem, { target: { value: "Visual Examination Updated" } });

    await waitFor(() => {
      expect(confirmButton.hasAttribute("disabled")).toBe(true);
      expect(confirmButton.getAttribute("title")).toBeTruthy();
      expect(createRevisionButton.hasAttribute("disabled")).toBe(true);
      expect(createRevisionButton.getAttribute("title")).toBeTruthy();
    });
    expect(screen.getByRole("button", { name: "Revert to last saved draft" })).toBeTruthy();

    await waitFor(() => {
      expect(apiMocks.saveProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });
    expect(screen.queryByRole("button", { name: "Save Draft" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Discard Draft Changes" })).toBeNull();

    await waitFor(() => {
      expect(typeof resolveSave).toBe("function");
    });
    if (typeof resolveSave !== "function") {
      throw new Error("Missing deferred save resolver in auto-save test.");
    }
    resolveSave(
      buildRevisionDraft({
        testItem: "Visual Examination Updated",
        updatedAt: "2026-05-23T00:01:00Z",
      })
    );

    await waitFor(() => {
      expect(confirmButton.hasAttribute("disabled")).toBe(false);
      expect(createRevisionButton.hasAttribute("disabled")).toBe(false);
    });
  });

  it("shows save failure status and blocks confirm when auto-save rejects", async () => {
    apiMocks.saveProjectMatrixDraft.mockRejectedValueOnce(new Error("save failed"));
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const confirmButton = screen.getByRole("button", { name: "Confirm Revision" });
    fireEvent.change(screen.getByLabelText("Row 1 test item"), {
      target: { value: "Visual Examination Reject Case" },
    });

    await waitFor(() => {
      expect(apiMocks.saveProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(screen.getAllByText("Save failed. Retry before confirming.").length).toBeGreaterThan(0);
      expect(confirmButton.hasAttribute("disabled")).toBe(true);
      expect(screen.getByRole("button", { name: "Revert to last saved draft" })).toBeTruthy();
    });
  });

  it("confirms revision and hides initial confirm action", async () => {
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByRole("button", { name: "Confirm Revision" }));

    await waitFor(() => {
      expect(apiMocks.confirmProjectMatrixRevisionDraft).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
      expect(screen.getByText("Current Active Matrix Authority")).toBeTruthy();
      expect(screen.queryByRole("button", { name: "Confirm As Active Matrix" })).toBeNull();
      expect(screen.getByRole("button", { name: "Create Revision Draft" })).toBeTruthy();
    });
  });

  it("returns to revision draft state when editing after confirmation", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByRole("button", { name: "Confirm Revision" }));

    await waitFor(() => {
      expect(screen.getByText("Current Active Matrix Authority")).toBeTruthy();
    });

    fireEvent.change(screen.getByLabelText("Row 1 test item"), {
      target: { value: "Visual Examination Edited After Confirm" },
    });

    await waitFor(() => {
      expect(screen.getByText("Editing Revision Draft")).toBeTruthy();
      expect(screen.getByText("Changes are not active until confirmed")).toBeTruthy();
    });
  });

  it("shows revision draft state and separates draft and authority actions", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    expect(screen.getByLabelText("Matrix workspace state").textContent).toContain("Editing Revision Draft");
    expect(screen.getByText("Changes are not active until confirmed")).toBeTruthy();
    expect(screen.getByLabelText("Draft Actions")).toBeTruthy();
    expect(screen.getByLabelText("Authority Actions")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Save Draft" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Discard Draft Changes" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Revert to last saved draft" })).toBeNull();
    expect(screen.getByRole("button", { name: "Change Selected Groups" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Change Source Matrix" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Create Revision Draft" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Confirm Revision" })).toBeTruthy();
    expect(screen.getByText("Adjust execution groups for this matrix configuration. This is not a new source import.")).toBeTruthy();
  });

  it("confirms a normal draft as active authority", async () => {
    apiMocks.listProjectMatrixDrafts.mockResolvedValueOnce([
      {
        project_matrix_draft_id: "draft-1",
        project_id: "P1",
        source_import_id: null,
        source_snapshot_id: "snapshot-1",
        base_confirmed_matrix_id: null,
        status: "draft",
        created_at: "2026-05-23T00:00:00Z",
        updated_at: "2026-05-23T00:00:00Z",
      },
    ]);
    apiMocks.getProjectMatrixDraft.mockResolvedValueOnce({
      ...buildRevisionDraft(),
      record: {
        ...buildRevisionDraft().record,
        base_confirmed_matrix_id: null,
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText("Editing Draft")).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Confirm As Active Matrix" }));

    await waitFor(() => {
      expect(apiMocks.confirmProjectMatrixDraft).toHaveBeenCalledTimes(1);
      expect(screen.getByText("Current Active Matrix Authority")).toBeTruthy();
      expect(screen.getByText("Used by Project Workbench and Test Record generation")).toBeTruthy();
      expect(screen.getByText("Active matrix confirmed (v1).")).toBeTruthy();
    });
  });

  it("asks for confirmation before changing source matrix", async () => {
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValueOnce(false).mockReturnValueOnce(true);
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByRole("button", { name: "Change Source Matrix" }));
    expect(confirmSpy).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Change Source Matrix" }));
    expect(confirmSpy).toHaveBeenCalledTimes(2);
  });

  it("enters inline import selection mode and requires at least one group before commit", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    const file = new File(["dummy"], "spec.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(1);
      expect(screen.getByRole("button", { name: "Replace" })).toBeTruthy();
      expect(screen.getByRole("button", { name: "Append" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
    });
    expect(screen.getByText("Test Item")).toBeTruthy();
    expect(screen.queryByText("Section")).toBeNull();
    expect(screen.queryByText("Method")).toBeNull();
    expect(screen.queryByText("Condition")).toBeNull();
    expect(screen.queryByText("Requirement")).toBeNull();
    expect(screen.queryByRole("button", { name: "Save Draft" })).toBeNull();
    expect(screen.queryByLabelText("Draft Actions")).toBeNull();
    expect(screen.queryByLabelText("Authority Actions")).toBeNull();
    expect(screen.getByLabelText("Matrix workspace state").textContent).toContain("Editing Revision Draft");
    expect(screen.getAllByRole("button", { name: "Append Matrix (Future)" }).every((button) => button.hasAttribute("disabled"))).toBe(true);
    const groupARow = screen.getByText("Group A").closest("tr");
    const groupBRow = screen.getByText("Group B").closest("tr");
    expect(groupARow?.textContent?.includes("Qty:")).toBe(false);
    expect(groupBRow?.textContent?.includes("Qty:")).toBe(false);
    expect(screen.getByText("Visual Examination")).toBeTruthy();
    expect(screen.getByText("Selected groups: 2 / 2 | Selected steps: 0")).toBeTruthy();
    expect(screen.getByLabelText("Selected group summary")).toBeTruthy();
    expect(screen.getByText("Group A: 5; Group B: 3")).toBeTruthy();
    expect(screen.getAllByText("Samples: 5").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Samples: 3").length).toBeGreaterThan(0);

    const createButton = screen.getByRole("button", { name: "Confirm selected groups" });
    fireEvent.click(screen.getByLabelText("Select Group B"));
    expect(screen.getByText("Selected groups: 1 / 2 | Selected steps: 0")).toBeTruthy();
    expect(screen.getByText("Group A: 5")).toBeTruthy();
    expect(screen.queryByText("Group A: 5; Group B: 3")).toBeNull();
    fireEvent.click(screen.getByLabelText("Select Group B"));
    fireEvent.click(screen.getByLabelText("Select Group A"));
    fireEvent.click(screen.getByLabelText("Select Group B"));
    await waitFor(() => {
      expect(createButton.hasAttribute("disabled")).toBe(true);
      expect(createButton.getAttribute("title")).toBe("Select at least one group.");
    });
    expect(screen.getByText("Select at least one group.")).toBeTruthy();
    expect(screen.getByText("Select at least one group before creating the draft.")).toBeTruthy();

    fireEvent.click(screen.getByLabelText("Select Group A"));
    await waitFor(() => {
      expect(createButton.hasAttribute("disabled")).toBe(false);
    });

    fireEvent.click(createButton);
    await waitFor(() => {
      expect(apiMocks.commitMatrixImport).toHaveBeenCalledTimes(1);
    });
    const [calledProjectId, payload] = apiMocks.commitMatrixImport.mock.calls[0];
    expect(calledProjectId).toBe("P1");
    expect(payload.selected_group_keys).toEqual(["g1"]);
    expect(payload.selected_group_keys.includes("g2")).toBe(false);
    expect(screen.queryByRole("heading", { name: "Import Selection Mode" })).toBeNull();
  });

  it("shows selected step totals when preview groups include step arrays", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValueOnce({
      project_id: "P1",
      source_document_path: "C:/specs/spec.docx",
      source_document_name: "spec.docx",
      source_format: ".docx",
      capability_status: "ok",
      generated_at: "2026-05-23T00:00:00Z",
      selected_table_index: 0,
      selected_page_number: 2,
      selected_page_table_index: 1,
      candidate_tables: [],
      preview_pdf_token: "pdf-token-test-268",
      rows: [
        {
          source_row_index: 1,
          test_item: "Visual Examination",
          source_section: "6.1",
          group_tokens: { "Group A": "1", "Group B": "2" },
          is_sample_row: false,
        },
      ],
      groups: [
        {
          group_key: "g1",
          group_label: "Group A",
          source_table_index: 0,
          extraction_status: "ok",
          sample_quantity_expression: "5",
          sample_note: null,
          steps: [
            { sequence: 1, raw_token: "1", test_item: "Step 1" },
            { sequence: 2, raw_token: "2", test_item: "Step 2" },
          ],
        },
        {
          group_key: "g2",
          group_label: "Group B",
          source_table_index: 0,
          extraction_status: "ok",
          sample_quantity_expression: "3",
          sample_note: null,
          steps: [
            { sequence: 3, raw_token: "3", test_item: "Step 3" },
          ],
        },
      ],
      warnings: [],
      blockers: [],
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    const file = new File(["dummy"], "spec.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Replace" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));
    await waitFor(() => {
      expect(screen.getByText("Selected groups: 2 / 2 | Selected steps: 3")).toBeTruthy();
      expect(screen.getByText("Group A: 5; Group B: 3")).toBeTruthy();
    });
  });

  it("returns from group selection to matrix candidate preview without losing source context", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValueOnce({
      project_id: "P1",
      source_document_path: "C:/specs/spec.docx",
      source_document_name: "spec.docx",
      source_format: ".docx",
      capability_status: "ok",
      generated_at: "2026-05-23T00:00:00Z",
      selected_table_index: 0,
      selected_page_number: 2,
      selected_page_table_index: 1,
      candidate_tables: [],
      preview_pdf_token: "pdf-token-test-267",
      rows: [
        {
          source_row_index: 1,
          test_item: "Visual Examination",
          source_section: "6.1",
          group_tokens: { "Group A": "1", "Group B": "2" },
          is_sample_row: false,
        },
      ],
      groups: [
        {
          group_key: "g1",
          group_label: "Group A",
          source_table_index: 0,
          extraction_status: "ok",
          sample_quantity_expression: "5",
          sample_note: null,
          steps: [],
        },
        {
          group_key: "g2",
          group_label: "Group B",
          source_table_index: 0,
          extraction_status: "ok",
          sample_quantity_expression: "3",
          sample_note: null,
          steps: [],
        },
      ],
      warnings: [],
      blockers: [],
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    const file = new File(["dummy"], "spec.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Replace" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Back to matrix candidate selection" }));
    await waitFor(() => {
      expect(screen.getByTitle("Word PDF Preview")).toBeTruthy();
      expect(screen.getByLabelText("Page")).toBeTruthy();
      expect(screen.getByLabelText("Table on page")).toBeTruthy();
      expect(screen.getByRole("button", { name: "Reparse" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));
    await waitFor(() => {
      expect(screen.getByLabelText("Select Group A")).toBeTruthy();
    });
  });

  it("reopens selection mode from draft actions without re-uploading source", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    const file = new File(["dummy"], "spec.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(1);
      expect(screen.getByRole("button", { name: "Replace" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Confirm selected groups" }));
    await waitFor(() => {
      expect(apiMocks.commitMatrixImport).toHaveBeenCalledTimes(1);
      expect(screen.queryByRole("heading", { name: "Import Selection Mode" })).toBeNull();
    });

    fireEvent.click(screen.getByRole("button", { name: "Change Selected Groups" }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
    });
    expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(1);
  });

  it("cancels import session and still allows group selection from current draft", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    const file = new File(["dummy"], "spec.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Replace" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Cancel import session" }));
    await waitFor(() => {
      expect(screen.queryByRole("heading", { name: "Import Selection Mode" })).toBeNull();
    });

    const changeSelectedGroupsButton = screen.getByRole("button", { name: "Change Selected Groups" });
    expect(changeSelectedGroupsButton.hasAttribute("disabled")).toBe(false);
    fireEvent.click(changeSelectedGroupsButton);
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
      expect(screen.getByText("Source: Current persisted draft")).toBeTruthy();
    });
  });

  it("clears stale preview after reparse failure and guides manual setup", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload
      .mockResolvedValueOnce({
        project_id: "P1",
        source_document_path: "C:/specs/spec.docx",
        source_document_name: "spec.docx",
        source_format: ".docx",
        capability_status: "ok",
        generated_at: "2026-05-23T00:00:00Z",
        selected_table_index: 0,
        selected_page_number: 2,
        selected_page_table_index: 1,
        candidate_tables: [],
        preview_pdf_token: null,
        rows: [
          {
            source_row_index: 1,
            test_item: "Visual Examination",
            source_section: "6.1",
            group_tokens: { "Group A": "1" },
            is_sample_row: false,
          },
        ],
        groups: [
          {
            group_key: "g1",
            group_label: "Group A",
            source_table_index: 0,
            extraction_status: "ok",
            sample_quantity_expression: "5",
            sample_note: null,
            steps: [],
          },
        ],
        warnings: [],
        blockers: [],
      })
      .mockRejectedValueOnce(new Error("Reparse failed."));

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    const file = new File(["dummy"], "spec.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(1);
      expect(screen.getByRole("button", { name: "Reparse" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Reparse" }));
    await waitFor(() => {
      expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(2);
      expect(screen.getByText("No matching matrix found. Adjust page/table and reparse.")).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
      expect(screen.getByText("Source: Current persisted draft")).toBeTruthy();
    });
    expect(screen.getByText("A")).toBeTruthy();
  });

  it("keeps the PDF preview on the requested page when reparse finds no matching matrix", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload
      .mockResolvedValueOnce({
        project_id: "P1",
        source_document_path: "C:/specs/spec.docx",
        source_document_name: "spec.docx",
        source_format: ".docx",
        capability_status: "ok",
        generated_at: "2026-05-23T00:00:00Z",
        selected_table_index: 0,
        selected_page_number: 2,
        selected_page_table_index: 1,
        candidate_tables: [],
        preview_pdf_token: "pdf-token-1",
        rows: [
          {
            source_row_index: 1,
            test_item: "Visual Examination",
            source_section: "6.1",
            group_tokens: { "Group A": "1" },
            is_sample_row: false,
          },
        ],
        groups: [
          {
            group_key: "g1",
            group_label: "Group A",
            source_table_index: 0,
            extraction_status: "ok",
            sample_quantity_expression: "5",
            sample_note: null,
            steps: [],
          },
        ],
        warnings: [],
        blockers: [],
      })
      .mockResolvedValueOnce({
        project_id: "P1",
        source_document_path: "C:/specs/spec.docx",
        source_document_name: "spec.docx",
        source_format: ".docx",
        capability_status: "ok",
        generated_at: "2026-05-23T00:01:00Z",
        selected_table_index: null,
        selected_page_number: 2,
        selected_page_table_index: null,
        candidate_tables: [],
        preview_pdf_token: "pdf-token-1",
        rows: [],
        groups: [],
        warnings: [],
        blockers: ["Selected table is not a valid Matrix table."],
      });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    const file = new File(["dummy"], "spec.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByTitle("Word PDF Preview").getAttribute("src")).toBe(
        "/api/pdf/pdf-token-1#page=2&zoom=page-width&pagemode=thumbs"
      );
    });

    fireEvent.change(screen.getByLabelText("Page"), { target: { value: "9" } });
    fireEvent.click(screen.getByRole("button", { name: "Reparse" }));

    await waitFor(() => {
      expect(screen.getByText("No matching matrix found at requested page/table. Reparse or edit manually.")).toBeTruthy();
      expect(screen.getByTitle("Word PDF Preview").getAttribute("src")).toBe(
        "/api/pdf/pdf-token-1#page=9&zoom=page-width&pagemode=thumbs"
      );
    });
  });
});
