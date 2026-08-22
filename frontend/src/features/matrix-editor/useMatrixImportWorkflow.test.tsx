import { act, cleanup, renderHook } from "@testing-library/react";
import type { ChangeEvent } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { MatrixImportCommitResponse, MatrixPreviewResponse } from "../../api/client";
import { useMatrixImportWorkflow } from "./useMatrixImportWorkflow";

const apiMocks = vi.hoisted(() => ({
  commitMatrixImport: vi.fn(),
  previewFromPath: vi.fn(),
  previewFromSourceCandidate: vi.fn(),
  previewFromUpload: vi.fn(),
}));

const sourcePickerMocks = vi.hoisted(() => ({
  choose: vi.fn(),
  hasDesktop: vi.fn(() => false),
}));

const standardVersionChoiceMocks = vi.hoisted(() => ({
  busy: false,
  chooseFile: vi.fn(),
  close: vi.fn(),
  detail: null,
  error: null,
  isOpen: false,
  open: vi.fn(),
  skip: vi.fn(),
}));

vi.mock("../../api/client", () => ({
  commitMatrixImport: apiMocks.commitMatrixImport,
  isMatrixImportStandardVersionActionRequiredError: () => false,
  isProjectLifecycleReadonlyErrorDetail: () => false,
  matrixPreviewPdfUrl: (token: string) => `/api/pdf/${token}`,
  previewProjectTestPlanMatrixFromPath: apiMocks.previewFromPath,
  previewProjectTestPlanMatrixFromSourceCandidate: apiMocks.previewFromSourceCandidate,
  previewProjectTestPlanMatrixFromUpload: apiMocks.previewFromUpload,
}));

vi.mock("../../desktop/pathPickerBridge", () => ({
  hasMatrixImportSourcePicker: sourcePickerMocks.hasDesktop,
}));

vi.mock("./useMatrixImportSourcePicker", () => ({
  useMatrixImportSourcePicker: () => sourcePickerMocks.choose,
}));

vi.mock("./useMatrixImportStandardVersionChoice", () => ({
  useMatrixImportStandardVersionChoice: () => standardVersionChoiceMocks,
}));

function buildPreview(overrides: Partial<MatrixPreviewResponse> = {}): MatrixPreviewResponse {
  return {
    project_id: "P1",
    source_document_path: "D:/source.docx",
    source_document_name: "source.docx",
    source_format: ".docx",
    capability_status: "supported",
    generated_at: "2026-08-22T00:00:00Z",
    selected_table_index: 0,
    selected_page_number: 1,
    selected_page_table_index: 1,
    candidate_tables: [],
    preview_pdf_token: "preview-token",
    rows: [
      {
        source_row_index: 1,
        test_item: "Visual Examination",
        source_section: "1.1",
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
    ...overrides,
  };
}

function buildCommitResponse(preview: MatrixPreviewResponse): MatrixImportCommitResponse {
  return {
    source_import_id: "import-1",
    source_snapshot_id: "snapshot-1",
    selected_group_keys_committed: preview.groups.map((group) => group.group_key),
    commit_status: "created",
    method_authority_sync: {
      status: "synchronized",
      updated_count: 1,
      current_count: 1,
      review_count: 0,
      standard_resource_id: "standard-1",
      effective_worksheet_name: "认可标准",
      catalog_fingerprint: "catalog-1",
      context_fingerprint: "context-1",
      rows: [],
    },
    project_matrix_draft: {
      record: {
        project_matrix_draft_id: "draft-1",
        project_id: "P1",
        base_confirmed_matrix_id: null,
        status: "draft",
        source_import_id: "import-1",
        source_snapshot_id: "snapshot-1",
        created_at: "2026-08-22T00:00:00Z",
        updated_at: "2026-08-22T00:00:00Z",
      },
      groups: [
        {
          draft_group_id: "group-1",
          source_group_snapshot_id: "source-group-1",
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
          source_row_snapshot_id: "source-row-1",
          row_order: 1,
          test_item: "Visual Examination",
          source_section: "1.1",
          method: null,
          condition: null,
          requirement: null,
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
    },
  };
}

function uploadEvent(file: File): ChangeEvent<HTMLInputElement> {
  return {
    target: { files: [file], value: "C:/fakepath/source.docx" },
  } as unknown as ChangeEvent<HTMLInputElement>;
}

describe("useMatrixImportWorkflow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sourcePickerMocks.hasDesktop.mockReturnValue(false);
    sourcePickerMocks.choose.mockResolvedValue({ kind: "browser", candidates: [] });
  });

  afterEach(() => cleanup());

  it("reparses a stale locator before committing the refreshed preview", async () => {
    const firstPreview = buildPreview();
    const refreshedPreview = buildPreview({
      source_document_name: "refreshed.docx",
      selected_page_number: 2,
    });
    apiMocks.previewFromUpload
      .mockResolvedValueOnce(firstPreview)
      .mockResolvedValueOnce(refreshedPreview);
    apiMocks.commitMatrixImport.mockResolvedValue(buildCommitResponse(refreshedPreview));
    const onCommitted = vi.fn();
    const { result } = renderHook(() =>
      useMatrixImportWorkflow({ projectId: "P1", readonlyMessage: null, onCommitted }),
    );

    await act(async () => {
      await result.current.onFileChange(
        uploadEvent(new File(["docx"], "source.docx", { type: "application/docx" })),
      );
    });
    act(() => result.current.dialog?.updateLocator({ page: "2" }));
    await act(async () => result.current.dialog?.replace());

    expect(apiMocks.previewFromUpload).toHaveBeenCalledTimes(2);
    expect(apiMocks.previewFromUpload.mock.calls[1][2]).toEqual({
      pageNumber: 2,
      pageTableIndex: 1,
      tableTextQuery: null,
    });
    expect(apiMocks.commitMatrixImport).toHaveBeenCalledWith(
      "P1",
      expect.objectContaining({ preview_payload: refreshedPreview }),
    );
    expect(onCommitted).toHaveBeenCalledWith({
      preview: refreshedPreview,
      response: expect.objectContaining({ source_import_id: "import-1" }),
    });
  });

  it("rejects an invalid locator without reparsing or committing", async () => {
    apiMocks.previewFromUpload.mockResolvedValue(buildPreview());
    const { result } = renderHook(() =>
      useMatrixImportWorkflow({ projectId: "P1", readonlyMessage: null, onCommitted: vi.fn() }),
    );

    await act(async () => {
      await result.current.onFileChange(
        uploadEvent(new File(["docx"], "source.docx", { type: "application/docx" })),
      );
    });
    act(() => result.current.dialog?.updateLocator({ page: "abc" }));
    await act(async () => result.current.dialog?.replace());

    expect(result.current.dialog?.error).toBe("Page must be a positive integer.");
    expect(apiMocks.previewFromUpload).toHaveBeenCalledTimes(1);
    expect(apiMocks.commitMatrixImport).not.toHaveBeenCalled();
  });

  it("keeps the initial upload no-match guidance focused on adjusting the locator", async () => {
    apiMocks.previewFromUpload.mockResolvedValue(buildPreview({ groups: [] }));
    const { result } = renderHook(() =>
      useMatrixImportWorkflow({ projectId: "P1", readonlyMessage: null, onCommitted: vi.fn() }),
    );

    await act(async () => {
      await result.current.onFileChange(
        uploadEvent(new File(["docx"], "source.docx", { type: "application/docx" })),
      );
    });

    expect(result.current.dialog?.lookupMessage).toBe(
      "No matching matrix found. Adjust the locator, then Replace.",
    );
  });

  it("keeps the precise preview blocker when stale reparse finds no usable matrix", async () => {
    apiMocks.previewFromUpload
      .mockResolvedValueOnce(buildPreview())
      .mockResolvedValueOnce(
        buildPreview({
          blockers: ["Selected table 6 is not a valid Matrix table."],
          groups: [],
          selected_page_number: null,
          selected_page_table_index: null,
        }),
      );
    const { result } = renderHook(() =>
      useMatrixImportWorkflow({ projectId: "P1", readonlyMessage: null, onCommitted: vi.fn() }),
    );

    await act(async () => {
      await result.current.onFileChange(
        uploadEvent(new File(["docx"], "source.docx", { type: "application/docx" })),
      );
    });
    act(() => result.current.dialog?.updateLocator({ page: "10" }));
    await act(async () => result.current.dialog?.replace());

    expect(result.current.dialog?.error).toBe(
      "Selected table 6 is not a valid Matrix table.",
    );
    expect(apiMocks.commitMatrixImport).not.toHaveBeenCalled();
  });
});
