import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import {
  apiMocks,
  buildCommitResponse,
  buildImportPreview,
  buildSessionSeed,
  createDeferred,
  installMatrixEditorWorkspaceTestLifecycle,
  runtimeModelState,
  sourcePickerMocks,
  type MatrixPreviewResponse,
} from "./MatrixEditorWorkspace.testSupport";
import { MatrixEditorWorkspace } from "./MatrixEditorWorkspace";

installMatrixEditorWorkspaceTestLifecycle();

describe("MatrixEditorWorkspace import flow", () => {
  it("opens the browser project source chooser without native confirmation", async () => {
    const inputClickSpy = vi
      .spyOn(HTMLInputElement.prototype, "click")
      .mockImplementation(() => {});

    sourcePickerMocks.choose.mockResolvedValue({ kind: "browser", sourceTitle: "Project source files", candidates: [], warnings: [], error: null });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));

    expect(window.confirm).not.toHaveBeenCalled();
    expect(inputClickSpy).not.toHaveBeenCalled();
    expect(await screen.findByRole("heading", { name: "Project source files" })).toBeTruthy();
    const input = document.querySelector("input[type=\"file\"]") as HTMLInputElement;
    expect(input.getAttribute("accept")).toBe(".pdf,.doc,.docx");
  });

  it("shows the browser source folder loading state while candidates are fetched", async () => {
    const pendingChoice = createDeferred<{
      kind: "browser";
      sourceTitle: string;
      candidates: [];
      warnings: [];
      error: null;
    }>();
    sourcePickerMocks.choose.mockReturnValueOnce(pendingChoice.promise);
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));

    expect(await screen.findByRole("heading", { name: "Project source files" })).toBeTruthy();
    expect(screen.getByText("Loading project sources...")).toBeTruthy();
    await act(async () => {
      pendingChoice.resolve({
        kind: "browser",
        sourceTitle: "Email attachment files",
        candidates: [],
        warnings: [],
        error: null,
      });
      await pendingChoice.promise;
    });
    expect(await screen.findByRole("heading", { name: "Email attachment files" })).toBeTruthy();
    expect(screen.queryByText("Loading project sources...")).toBeNull();
  });

  it("previews a browser project candidate only after explicit selection", async () => {
    sourcePickerMocks.choose.mockResolvedValue({
      kind: "browser",
      sourceTitle: "Submitted Material files",
      candidates: [{ candidate_id: "source-1", file_name: "matrix.docx" }],
      warnings: [],
      error: null,
    });
    apiMocks.previewProjectTestPlanMatrixFromSourceCandidate.mockResolvedValue(buildImportPreview());
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    expect(await screen.findByRole("heading", { name: "Submitted Material files" })).toBeTruthy();
    expect(apiMocks.previewProjectTestPlanMatrixFromSourceCandidate).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Select matrix.docx" }));
    await waitFor(() => expect(apiMocks.previewProjectTestPlanMatrixFromSourceCandidate).toHaveBeenCalledWith("P1", "source-1", "resolved_directory"));
    expect(await screen.findByRole("button", { name: "Replace" })).toBeTruthy();
  });

  it("shows the blocking Matrix search dialog while a browser project candidate is previewed", async () => {
    const deferredPreview = createDeferred<MatrixPreviewResponse>();
    sourcePickerMocks.choose.mockResolvedValue({
      kind: "browser",
      sourceTitle: "Submitted Material files",
      candidates: [{ candidate_id: "source-1", file_name: "matrix.docx" }],
      warnings: [],
      error: null,
    });
    apiMocks.previewProjectTestPlanMatrixFromSourceCandidate.mockReturnValueOnce(deferredPreview.promise);

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    expect(await screen.findByRole("heading", { name: "Submitted Material files" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Select matrix.docx" }));

    expect(
      await screen.findByRole("alertdialog", { name: "Searching for Matrix" })
    ).toBeTruthy();
    expect(
      screen.getByText("ConnLab is reading the source document and preparing the preview.")
    ).toBeTruthy();

    await act(async () => {
      deferredPreview.resolve(buildImportPreview({ source_document_name: "matrix.docx", preview_pdf_token: "source-pdf" }));
      await deferredPreview.promise;
    });

    await waitFor(() =>
      expect(screen.queryByRole("alertdialog", { name: "Searching for Matrix" })).toBeNull()
    );
    expect(await screen.findByRole("button", { name: "Replace" })).toBeTruthy();
    await waitFor(() =>
      expect(apiMocks.previewProjectTestPlanMatrixFromSourceCandidate).toHaveBeenCalledWith("P1", "source-1", "resolved_directory")
    );
  });

  it("cancels the browser source chooser without previewing or uploading", async () => {
    sourcePickerMocks.choose.mockResolvedValue({
      kind: "browser",
      sourceTitle: "Submitted Material files",
      candidates: [{ candidate_id: "source-1", file_name: "matrix.docx" }],
      warnings: [],
      error: null,
    });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    fireEvent.click(await screen.findByRole("button", { name: "Import Matrix" }));
    fireEvent.click(within(await screen.findByRole("dialog")).getByRole("button", { name: "Cancel" }));

    expect(screen.queryByRole("heading", { name: "Submitted Material files" })).toBeNull();
    expect(apiMocks.previewProjectTestPlanMatrixFromSourceCandidate).not.toHaveBeenCalled();
    expect(apiMocks.previewProjectTestPlanMatrixFromUpload).not.toHaveBeenCalled();
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
    await screen.findByRole("button", { name: "Import Matrix" });

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

  it("restores an imported source replacement draft after returning from Setup", async () => {
    const replacementPreview = buildImportPreview({
      source_document_name: "replacement.docx",
      source_document_path: "replacement.docx",
      groups: [
        {
          group_key: "g2",
          group_label: "H",
          source_table_index: 0,
          extraction_status: "loaded",
          sample_size: null,
          sample_quantity_expression: "3",
          sample_note: null,
          steps: [],
        },
      ],
      rows: [
        {
          source_row_index: 1,
          test_item: "Imported replacement row",
          source_section: "5.5",
          method: "IEC 60512-1-1",
          condition: "10x min magnification",
          requirement: "No detrimental condition",
          group_tokens: { g2: "1", H: "1" },
          is_sample_row: false,
        },
      ],
    });
    const committed = buildCommitResponse(replacementPreview, "3");
    committed.project_matrix_draft.cells[0].cell_value = "1";
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_source_import_id: committed.source_import_id,
      editor_source_snapshot_id: committed.source_snapshot_id,
      editor_draft_id: committed.project_matrix_draft.record.project_matrix_draft_id,
      draft_status: "current",
      loaded_source: "draft",
      saved_payload_signature: "replacement-signature",
      source_preview_payload: replacementPreview,
      editor_draft: {
        groups: committed.project_matrix_draft.groups,
        rows: committed.project_matrix_draft.rows.map((row) => ({
          ...row,
          day_expression: null,
        })),
        cells: committed.project_matrix_draft.cells.map((cell) => ({
          draft_row_id: cell.draft_row_id,
          draft_group_id: cell.draft_group_id,
          cell_value: cell.cell_value,
        })),
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByText("replacement.docx")).toBeTruthy();
    expect((screen.getByLabelText("Row 1 test item") as HTMLInputElement).value).toBe(
      "Imported replacement row"
    );
    expect(screen.getByRole("columnheader", { name: "Include group H H" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    await waitFor(() => expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(1));
    expect(apiMocks.confirmMatrixEditorSession.mock.calls[0][1]).toMatchObject({
      source_import_id: committed.source_import_id,
      source_snapshot_id: committed.source_snapshot_id,
      expected_editor_draft_id: committed.project_matrix_draft.record.project_matrix_draft_id,
      expected_saved_payload_signature: "replacement-signature",
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

});
