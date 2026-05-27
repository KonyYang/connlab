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
  fetchActiveConfirmedMatrixSnapshot: vi.fn(),
  previewProjectTestPlanMatrixFromUpload: vi.fn(),
  commitMatrixImport: vi.fn(),
  matrixPreviewPdfUrl: vi.fn((token: string) => token),
}));

const runtimeModelState = vi.hoisted(() => ({
  authorityVersion: { confirmed_revision: 1 } as { confirmed_revision: number } | null,
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
    matrixAuthorityDraft: {
      source_document_name: "EIA-364 Qualification Matrix",
    },
    runtimeAuthoritySync: {
      projectionMatrixReference: "matrix-ref-1",
      authorityVersion: runtimeModelState.authorityVersion,
    },
    error: null,
  }),
}));

type DraftOverrides = {
  baseConfirmedMatrixId?: string | null;
  draftId?: string;
  testItem?: string;
  section?: string | null;
};

function buildDraft(overrides: DraftOverrides = {}) {
  const testItem = overrides.testItem ?? "Visual Examination";
  const section = overrides.section ?? null;
  const baseConfirmedMatrixId =
    overrides.baseConfirmedMatrixId === undefined
      ? "confirmed-1"
      : overrides.baseConfirmedMatrixId;
  return {
    record: {
      project_matrix_draft_id: overrides.draftId ?? "draft-1",
      project_id: "P1",
      source_import_id: null,
      source_snapshot_id: "snapshot-1",
      base_confirmed_matrix_id: baseConfirmedMatrixId,
      status: "draft",
      created_at: "2026-05-23T00:00:00Z",
      updated_at: "2026-05-23T00:00:00Z",
    },
    groups: [
      {
        draft_group_id: "group-1",
        source_group_snapshot_id: "src-group-1",
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
        source_row_snapshot_id: "src-row-1",
        row_order: 1,
        test_item: testItem,
        source_section: section,
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

function buildConfirmedSnapshot(overrides: {
  cellValue?: string;
  testItem?: string;
  section?: string | null;
} = {}) {
  return {
    version: {
      confirmed_matrix_id: "confirmed-1",
      project_id: "P1",
      project_matrix_draft_id: "draft-0",
      source_import_id: "source-0",
      source_snapshot_id: "snapshot-0",
      confirmed_revision: 1,
      is_active_authority: true,
      status: "confirmed",
      confirmed_by: "operator",
      confirmed_at: "2026-05-27T00:00:00Z",
      superseded_by_confirmed_matrix_id: null,
      superseded_at: null,
      superseded_reason: null,
    },
    groups: [
      {
        confirmed_group_id: "cg-1",
        draft_group_id: "dg-1",
        source_group_snapshot_id: "sg-1",
        group_order: 1,
        group_key: "g1",
        group_label: "1",
        sample_quantity_expression: "5",
        sample_note: null,
      },
    ],
    rows: [
      {
        confirmed_row_id: "cr-1",
        draft_row_id: "dr-1",
        source_row_snapshot_id: "sr-1",
        row_order: 1,
        test_item: overrides.testItem ?? "Visual Examination",
        source_section: overrides.section ?? null,
        method: "EIA-364-18B",
        condition: "10x min magnification",
        requirement: "No detrimental condition",
      },
    ],
    cells: [
      {
        confirmed_cell_id: "cc-1",
        confirmed_row_id: "cr-1",
        confirmed_group_id: "cg-1",
        draft_row_id: "dr-1",
        draft_group_id: "dg-1",
        cell_value: overrides.cellValue ?? "1",
      },
    ],
  };
}

describe("MatrixEditorWorkspace single draft publish flow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    runtimeModelState.authorityVersion = { confirmed_revision: 1 };
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
    apiMocks.getProjectMatrixDraft.mockResolvedValue(buildDraft());
    apiMocks.saveProjectMatrixDraft.mockResolvedValue(
      buildDraft({ testItem: "Visual Examination Updated" })
    );
    apiMocks.confirmProjectMatrixRevisionDraft.mockResolvedValue({
      version: { confirmed_revision: 2 },
      groups: [],
      rows: [],
      cells: [],
    });
    apiMocks.confirmProjectMatrixDraft.mockResolvedValue({
      version: { confirmed_revision: 1 },
      groups: [],
      rows: [],
      cells: [],
    });
    apiMocks.fetchActiveConfirmedMatrixSnapshot.mockResolvedValue(
      buildConfirmedSnapshot()
    );
    apiMocks.createMatrixRevisionDraft.mockResolvedValue(buildDraft());
    apiMocks.previewProjectTestPlanMatrixFromUpload.mockResolvedValue({
      project_id: "P1",
      source_document_path: "D:/samples/matrix.docx",
      source_document_name: "matrix.docx",
      source_format: "docx",
      capability_status: "supported",
      generated_at: "2026-05-27T00:00:00Z",
      selected_table_index: 0,
      selected_page_number: 1,
      selected_page_table_index: 1,
      candidate_tables: [],
      preview_pdf_token: "pdf-token-1",
      rows: [
        {
          source_row_index: 1,
          test_item: "Visual Examination",
          source_section: "1.1",
          group_tokens: { "1": "1" },
          is_sample_row: false,
        },
      ],
      groups: [
        {
          group_key: "g1",
          group_label: "1",
          source_table_index: 0,
          extraction_status: "ok",
          sample_size: 5,
          sample_quantity_expression: "5",
          sample_note: null,
          steps: [],
        },
      ],
      warnings: [],
      blockers: [],
    });
    vi.spyOn(window, "confirm").mockReturnValue(true);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    cleanup();
  });

  it("hides revision/draft concept actions and keeps one publish button", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    expect(screen.getByRole("button", { name: "Back to Workbench" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Confirm As Active Matrix" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Create Revision Draft" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Confirm Revision" })).toBeNull();
    expect(screen.queryByText("Draft Actions")).toBeNull();
    expect(screen.queryByText("Authority Actions")).toBeNull();
    expect(screen.queryByText("Current State")).toBeNull();
  });

  it("flushes unsaved edits before publish and uses revision confirm API", async () => {
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    let resolveSave: ((value: ReturnType<typeof buildDraft>) => void) | undefined;
    apiMocks.saveProjectMatrixDraft.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveSave = resolve as (value: ReturnType<typeof buildDraft>) => void;
        })
    );

    fireEvent.change(screen.getByLabelText("Row 1 test item"), {
      target: { value: "Visual Examination Updated" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Confirm As Active Matrix" }));
    expect(apiMocks.confirmProjectMatrixRevisionDraft).toHaveBeenCalledTimes(0);
    await waitFor(() => {
      expect(apiMocks.saveProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    if (resolveSave) {
      resolveSave(buildDraft({ testItem: "Visual Examination Updated" }));
    }

    await waitFor(() => {
      expect(apiMocks.confirmProjectMatrixRevisionDraft).toHaveBeenCalledTimes(1);
      expect(apiMocks.confirmProjectMatrixDraft).toHaveBeenCalledTimes(0);
      expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    });
  });

  it("uses first-authority confirm API when draft has no base confirmed id", async () => {
    runtimeModelState.authorityVersion = null;
    apiMocks.fetchActiveConfirmedMatrixSnapshot.mockRejectedValueOnce(
      new Error("Active confirmed matrix not found.")
    );
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
    apiMocks.getProjectMatrixDraft.mockResolvedValueOnce(
      buildDraft({ baseConfirmedMatrixId: null })
    );
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByRole("button", { name: "Confirm As Active Matrix" }));

    await waitFor(() => {
      expect(apiMocks.confirmProjectMatrixDraft).toHaveBeenCalledTimes(1);
      expect(apiMocks.confirmProjectMatrixRevisionDraft).toHaveBeenCalledTimes(0);
      expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    });
  });

  it("prefers the active-authority revision draft over a newer non-revision draft", async () => {
    runtimeModelState.authorityVersion = null;
    apiMocks.listProjectMatrixDrafts.mockResolvedValueOnce([
      {
        project_matrix_draft_id: "draft-legacy",
        project_id: "P1",
        source_import_id: null,
        source_snapshot_id: "snapshot-legacy",
        base_confirmed_matrix_id: null,
        status: "draft",
        created_at: "2026-05-23T00:00:00Z",
        updated_at: "2026-05-23T00:00:00Z",
      },
      {
        project_matrix_draft_id: "revision-draft-1",
        project_id: "P1",
        source_import_id: null,
        source_snapshot_id: "snapshot-revision",
        base_confirmed_matrix_id: "confirmed-1",
        status: "draft",
        created_at: "2026-05-23T00:00:00Z",
        updated_at: "2026-05-23T00:00:00Z",
      },
    ]);
    apiMocks.getProjectMatrixDraft.mockResolvedValueOnce(
      buildDraft({
        draftId: "revision-draft-1",
        testItem: "Visual Examination Updated",
      })
    );
    apiMocks.saveProjectMatrixDraft.mockResolvedValueOnce(
      buildDraft({
        draftId: "revision-draft-1",
        testItem: "Visual Examination Updated",
      })
    );
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledWith(
        "P1",
        "revision-draft-1"
      );
      expect(apiMocks.fetchActiveConfirmedMatrixSnapshot).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByRole("button", { name: "Confirm As Active Matrix" }));

    await waitFor(() => {
      expect(apiMocks.createMatrixRevisionDraft).toHaveBeenCalledTimes(0);
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
      expect(apiMocks.saveProjectMatrixDraft).toHaveBeenCalledTimes(0);
      expect(apiMocks.confirmProjectMatrixRevisionDraft).toHaveBeenCalledWith(
        "P1",
        "revision-draft-1",
        { confirmed_by: "connlab-operator" }
      );
      expect(apiMocks.confirmProjectMatrixDraft).toHaveBeenCalledTimes(0);
      expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    });
  });

  it("blocks no-change publish after lazy revision draft creation", async () => {
    apiMocks.listProjectMatrixDrafts.mockResolvedValueOnce([]);
    apiMocks.createMatrixRevisionDraft.mockResolvedValueOnce(buildDraft());

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.listProjectMatrixDrafts).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByRole("button", { name: "Confirm As Active Matrix" }));

    await waitFor(() => {
      expect(apiMocks.createMatrixRevisionDraft).toHaveBeenCalledTimes(1);
      expect(apiMocks.confirmProjectMatrixRevisionDraft).toHaveBeenCalledTimes(0);
      expect(apiMocks.confirmProjectMatrixDraft).toHaveBeenCalledTimes(0);
      expect(screen.getByText("No Matrix changes to publish.")).toBeTruthy();
    });
  });

  it("blocks no-change publish for loaded persisted revision draft", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
      expect(apiMocks.fetchActiveConfirmedMatrixSnapshot).toHaveBeenCalledTimes(1);
    });

    const publishButton = screen.getByRole("button", { name: "Confirm As Active Matrix" });
    expect((publishButton as HTMLButtonElement).disabled).toBe(true);
    expect((publishButton as HTMLButtonElement).getAttribute("title")).toBe(
      "No Matrix changes to publish."
    );
    expect(apiMocks.confirmProjectMatrixRevisionDraft).toHaveBeenCalledTimes(0);
    expect(apiMocks.confirmProjectMatrixDraft).toHaveBeenCalledTimes(0);
  });

  it("supports first publish from editor-only state by creating persisted draft via commit", async () => {
    runtimeModelState.authorityVersion = null;
    apiMocks.listProjectMatrixDrafts.mockResolvedValueOnce([]);
    apiMocks.saveProjectMatrixDraft.mockResolvedValueOnce(
      buildDraft({ baseConfirmedMatrixId: null })
    );
    apiMocks.commitMatrixImport.mockResolvedValueOnce({
      source_import_id: "source-1",
      source_snapshot_id: "snapshot-1",
      selected_group_keys_committed: ["g1"],
      commit_status: "created",
      project_matrix_draft: buildDraft({ baseConfirmedMatrixId: null }),
    });
    apiMocks.fetchActiveConfirmedMatrixSnapshot.mockRejectedValueOnce(
      new Error("Active confirmed matrix not found.")
    );

    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);

    await waitFor(() => {
      expect(apiMocks.listProjectMatrixDrafts).toHaveBeenCalledTimes(1);
    });

    fireEvent.click(screen.getByRole("button", { name: "Confirm As Active Matrix" }));

    await waitFor(() => {
      expect(apiMocks.commitMatrixImport).toHaveBeenCalledTimes(1);
      expect(apiMocks.saveProjectMatrixDraft).toHaveBeenCalledTimes(1);
      expect(apiMocks.confirmProjectMatrixDraft).toHaveBeenCalledTimes(1);
      expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    });

    const saveCall = apiMocks.saveProjectMatrixDraft.mock.calls[0];
    expect(saveCall?.[0]).toBe("P1");
    expect(saveCall?.[1]).toBe("draft-1");
    expect(saveCall?.[2]?.rows?.[0]?.method).toBe("EIA-364-18B");
    expect(saveCall?.[2]?.rows?.[0]?.condition).toBe("10x min magnification");
    expect(saveCall?.[2]?.rows?.[0]?.requirement).toBe("No detrimental condition");
  });

  it("keeps import candidate dialog and selection mode workflow available", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement | null;
    expect(fileInput).not.toBeNull();
    if (!fileInput) {
      return;
    }

    fireEvent.change(fileInput, {
      target: {
        files: [new File(["matrix"], "matrix.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })],
      },
    });

    await waitFor(() => {
      expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(1);
      expect(screen.getByRole("heading", { name: "Import Matrix" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
      expect(screen.getByText("Selected groups")).toBeTruthy();
    });
  });

  it("keeps reparse + cancel import session controls available in selection mode", async () => {
    apiMocks.previewProjectTestPlanMatrixFromUpload
      .mockResolvedValueOnce({
        project_id: "P1",
        source_document_path: "D:/samples/matrix.docx",
        source_document_name: "matrix.docx",
        source_format: "docx",
        capability_status: "supported",
        generated_at: "2026-05-27T00:00:00Z",
        selected_table_index: 0,
        selected_page_number: 1,
        selected_page_table_index: 1,
        candidate_tables: [],
        preview_pdf_token: "pdf-token-1",
        rows: [],
        groups: [],
        warnings: [],
        blockers: [],
      })
      .mockResolvedValueOnce({
        project_id: "P1",
        source_document_path: "D:/samples/matrix.docx",
        source_document_name: "matrix.docx",
        source_format: "docx",
        capability_status: "supported",
        generated_at: "2026-05-27T00:00:00Z",
        selected_table_index: 0,
        selected_page_number: 2,
        selected_page_table_index: 1,
        candidate_tables: [],
        preview_pdf_token: "pdf-token-2",
        rows: [],
        groups: [],
        warnings: [],
        blockers: [],
      });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    await waitFor(() => {
      expect(apiMocks.getProjectMatrixDraft).toHaveBeenCalledTimes(1);
    });

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement | null;
    expect(fileInput).not.toBeNull();
    if (!fileInput) {
      return;
    }
    fireEvent.change(fileInput, {
      target: {
        files: [new File(["matrix"], "matrix.docx", { type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document" })],
      },
    });

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Matrix" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
      expect(screen.getByText("No valid matrix found from reparse.")).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Back to matrix candidate selection" }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Matrix" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Reparse" }));
    await waitFor(() => {
      expect(apiMocks.previewProjectTestPlanMatrixFromUpload).toHaveBeenCalledTimes(2);
    });

    fireEvent.click(screen.getByRole("button", { name: "Replace" }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Import Selection Mode" })).toBeTruthy();
    });

    fireEvent.click(screen.getByRole("button", { name: "Cancel import session" }));
    await waitFor(() => {
      expect(screen.queryByRole("heading", { name: "Import Selection Mode" })).toBeNull();
      expect(screen.queryByRole("heading", { name: "Import Matrix" })).toBeNull();
    });
  });
});
