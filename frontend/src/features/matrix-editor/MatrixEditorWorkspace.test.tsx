import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MatrixEditorWorkspace } from "./MatrixEditorWorkspace";

const apiMocks = vi.hoisted(() => ({
  listProjectMatrixDrafts: vi.fn(),
  getProjectMatrixDraft: vi.fn(),
  saveProjectMatrixDraft: vi.fn(),
  createMatrixRevisionDraft: vi.fn(),
  confirmProjectMatrixRevisionDraft: vi.fn(),
  previewProjectTestPlanMatrixFromUpload: vi.fn(),
  matrixPreviewPdfUrl: vi.fn(() => ""),
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
  });

  afterEach(() => {
    cleanup();
  });

  it("disables confirm when unsaved and re-enables after save", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const confirmButton = screen.getByRole("button", { name: "Confirm revision" });
    const createRevisionButton = screen.getByRole("button", { name: "Create revision draft" });
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

    const saveButton = screen.getByRole("button", { name: "Save" });
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

    const confirmButton = screen.getByRole("button", { name: "Confirm revision" });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(apiMocks.confirmProjectMatrixRevisionDraft).toHaveBeenCalledTimes(1);
    });

    await waitFor(() => {
      expect(confirmButton.hasAttribute("disabled")).toBe(true);
      expect(confirmButton.getAttribute("title")).toBe("Revision already confirmed.");
    });
  });
});
