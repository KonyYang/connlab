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

  it("disables confirm when unsaved and re-enables after save", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const confirmButton = screen.getByRole("button", { name: "Confirm Revision" });
    const createRevisionButton = screen.getByRole("button", { name: "Create Revision Draft" });
    expect(confirmButton.hasAttribute("disabled")).toBe(false);
    expect(createRevisionButton.hasAttribute("disabled")).toBe(false);

    const rowItem = screen.getByLabelText("Row 1 test item");
    fireEvent.change(rowItem, { target: { value: "Visual Examination Updated" } });

    await waitFor(() => {
      expect(confirmButton.hasAttribute("disabled")).toBe(true);
      expect(confirmButton.getAttribute("title")).toBe("Save changes before confirming revision.");
      expect(createRevisionButton.hasAttribute("disabled")).toBe(true);
      expect(createRevisionButton.getAttribute("title")).toBe("Save changes before creating revision draft.");
    });

    const saveButton = screen.getByRole("button", { name: "Save Draft" });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(apiMocks.saveProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(confirmButton.hasAttribute("disabled")).toBe(false);
      expect(createRevisionButton.hasAttribute("disabled")).toBe(false);
    });
  });

  it("disables confirm after successful confirmation", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByRole("button", { name: "Confirm Revision" }));

    await waitFor(() => {
      expect(apiMocks.confirmProjectMatrixRevisionDraft).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(screen.getByText("Current Active Matrix Authority")).toBeTruthy();
      const confirmAsActiveButton = screen.getByRole("button", { name: "Confirm As Active Matrix" });
      expect(confirmAsActiveButton.hasAttribute("disabled")).toBe(true);
      expect(confirmAsActiveButton.getAttribute("title")).toBe("This matrix is already active.");
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
    expect(screen.getByRole("button", { name: "Save Draft" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Discard Draft Changes" })).toBeTruthy();
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

    const createButton = screen.getByRole("button", { name: "Confirm selected groups" });
    fireEvent.click(screen.getByLabelText("Select Group A"));
    fireEvent.click(screen.getByLabelText("Select Group B"));
    await waitFor(() => {
      expect(createButton.hasAttribute("disabled")).toBe(true);
      expect(createButton.getAttribute("title")).toBe("Select at least one group.");
    });
    expect(screen.getByText("Select at least one group.")).toBeTruthy();

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
      expect(screen.getByText("No matrix detected. Continue from default editor and add groups manually.")).toBeTruthy();
    });
    expect(screen.queryByText("Group A")).toBeNull();
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
