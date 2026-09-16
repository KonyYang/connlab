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

describe("MatrixEditorWorkspace editing behavior", () => {
  it("confirms schedule before Matrix authority even with invalid Matrix edits and no received date", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({ ...buildSessionSeed(),
      active_confirmed_matrix_id: null, active_confirmed_revision: null });
    apiMocks.fetchProjectSchedule.mockResolvedValue({ status: "not_started", project_id: "P1",
      sample_received_date: "", critical_group_id: null, critical_group_days: "0",
      suggestion: {post_test_buffer_days: "", test_start_date: "", test_complete_date: "", estimated_completion_date: ""},
      confirmed_revision: null });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    const start = await screen.findByLabelText("Planned start");
    fireEvent.change(screen.getByLabelText("Row 1 day"), {target: {value: "invalid"}});
    fireEvent.change(start, {target: {value: "2026-09-09"}});
    const confirm = screen.getByRole("button", {name: "Confirm schedule"}) as HTMLButtonElement;
    expect(confirm.disabled).toBe(false);
    fireEvent.click(confirm);
    await waitFor(() => expect(apiMocks.confirmProjectSchedule).toHaveBeenCalled());
    expect(apiMocks.confirmMatrixEditorSession).not.toHaveBeenCalled();
  });
  it("confirms Project Schedule independently without activating Confirm Matrix", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    const plannedStart = await screen.findByLabelText("Planned start");
    const confirmMatrix = screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement;
    expect(confirmMatrix.disabled).toBe(true);
    expect(screen.queryByLabelText("Sample received")).toBeNull();

    fireEvent.change(plannedStart, { target: { value: "2026-06-03" } });

    expect(confirmMatrix.disabled).toBe(true);
    const confirmSchedule = screen.getByRole("button", { name: "Confirm schedule" }) as HTMLButtonElement;
    expect(confirmSchedule.disabled).toBe(false);
    fireEvent.click(confirmSchedule);
    await waitFor(() => expect(apiMocks.confirmProjectSchedule).toHaveBeenCalledWith(
      "P1",
      expect.objectContaining({
        test_start_date: "2026-06-03",
        test_complete_date: "2026-06-03",
        estimated_completion_date: "2026-06-03",
      })
    ));
    expect(apiMocks.saveMatrixEditorSessionDraft).not.toHaveBeenCalled();
    expect(apiMocks.confirmMatrixEditorSession).not.toHaveBeenCalled();
  });

  it("exports the current unsaved Matrix and keeps its snapshot while preview is pending", async () => {
    const preview = createDeferred();
    apiMocks.previewMatrixEditorLiveXlsxPublication.mockReturnValueOnce(preview.promise);
    apiMocks.exportMatrixEditorLiveXlsx.mockResolvedValueOnce({ blob: new Blob(["xlsx"]), fileName: "Matrix.xlsx" });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    const method = await screen.findByLabelText("Row 1 method");
    fireEvent.change(method, { target: { value: "Unsaved export method" } });
    fireEvent.change(screen.getByLabelText("Samples 1"), { target: { value: "7" } });
    expect(apiMocks.previewMatrixEditorLiveXlsxPublication).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Export Matrix" }));
    expect(apiMocks.previewMatrixEditorLiveXlsxPublication).toHaveBeenCalledWith("P1", expect.objectContaining({
      groups: [expect.objectContaining({ sample_size: "7" })],
      rows: [expect.objectContaining({ test_method: "Unsaved export method" })],
    }));
    fireEvent.change(method, { target: { value: "Next edit" } });
    await act(async () => preview.resolve({
      mode: "download",
      status: "ready",
      authority_status: "unconfirmed",
      existing_file: false,
      existing_modified_at: null,
      blockers: [],
      preview_token: "matrix-download-token",
    }));
    const dialog = await screen.findByRole("alertdialog", {
      name: "Download Matrix draft preview?",
    });
    expect(apiMocks.exportMatrixEditorLiveXlsx).not.toHaveBeenCalled();
    fireEvent.click(within(dialog).getByRole("button", { name: "Download draft preview" }));
    await waitFor(() => expect(apiMocks.exportMatrixEditorLiveXlsx).toHaveBeenCalledWith("P1", expect.objectContaining({
      preview_token: "matrix-download-token",
      rows: [expect.objectContaining({ test_method: "Unsaved export method" })],
    })));
    expect((method as HTMLTextAreaElement).value).toBe("Next edit");
  });

  it("explains a confirmed Matrix preview when the project folder is unavailable", async () => {
    apiMocks.previewMatrixEditorLiveXlsxPublication.mockResolvedValueOnce({
      mode: "download",
      status: "ready",
      authority_status: "confirmed",
      existing_file: false,
      existing_modified_at: null,
      blockers: [],
      preview_token: "confirmed-matrix-download",
    });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));

    fireEvent.click(screen.getByRole("button", { name: "Export Matrix" }));

    const dialog = await screen.findByRole("alertdialog", {
      name: "Download Matrix preview?",
    });
    expect(within(dialog).getByText(/no available project folder/i)).toBeTruthy();
    expect(apiMocks.exportMatrixEditorLiveXlsx).not.toHaveBeenCalled();
    fireEvent.click(within(dialog).getByRole("button", { name: "Cancel" }));
    expect(screen.queryByRole("alertdialog")).toBeNull();
    expect(apiMocks.exportMatrixEditorLiveXlsx).not.toHaveBeenCalled();
  });

  it("uses one conflict dialog before replacing an existing official Matrix workbook", async () => {
    apiMocks.previewMatrixEditorLiveXlsxPublication.mockResolvedValueOnce({
      mode: "official",
      status: "conflict",
      authority_status: "confirmed",
      existing_file: true,
      existing_modified_at: "2026-09-16T10:30:00+08:00",
      blockers: [],
      preview_token: "matrix-conflict-token",
    });
    apiMocks.publishMatrixEditorLiveXlsx.mockResolvedValueOnce({
      file_name: "DL-001 Matrix.xlsx",
      archive_path: "D:/Projects/DL-001/History/Matrix/old.xlsx",
    });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));

    fireEvent.click(screen.getByRole("button", { name: "Export Matrix" }));

    const dialog = await screen.findByRole("alertdialog", {
      name: "Replace existing Matrix workbook?",
    });
    expect(screen.getAllByRole("alertdialog")).toHaveLength(1);
    expect(apiMocks.publishMatrixEditorLiveXlsx).not.toHaveBeenCalled();
    fireEvent.click(within(dialog).getByRole("button", { name: "Archive old file" }));
    await waitFor(() =>
      expect(apiMocks.publishMatrixEditorLiveXlsx).toHaveBeenCalledWith(
        "P1",
        expect.objectContaining({
          preview_token: "matrix-conflict-token",
          conflict_action: "archive",
        })
      )
    );
  });

  it("exports unique stable identities after inserting a group between source groups", async () => {
    const seed = buildSessionSeed();
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...seed,
      source_preview_payload: {
        ...seed.source_preview_payload,
        groups: [
          seed.source_preview_payload.groups[0],
          {
            ...seed.source_preview_payload.groups[0],
            group_key: "g2",
            group_label: "2",
            sample_quantity_expression: "6",
          },
        ],
        rows: [{
          ...seed.source_preview_payload.rows[0],
          group_tokens: { "1": "1", g1: "1", "2": "1", g2: "1" },
        }],
      },
      editor_draft: {
        ...seed.editor_draft,
        groups: [
          seed.editor_draft.groups[0],
          {
            ...seed.editor_draft.groups[0],
            draft_group_id: "group-2",
            source_group_snapshot_id: "sg-2",
            group_order: 2,
            group_key: "g2",
            group_label: "2",
            sample_quantity_expression: "6",
          },
        ],
        cells: [
          seed.editor_draft.cells[0],
          { draft_row_id: "row-1", draft_group_id: "group-2", cell_value: "1" },
        ],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await screen.findByRole("checkbox", { name: "Include group 1" });
    fireEvent.contextMenu(document.querySelectorAll(".matrix-editor-group-band")[0] as HTMLElement);
    fireEvent.click(screen.getByRole("button", { name: "Insert right" }));
    fireEvent.change(document.querySelector("#group-name-group-3") as HTMLInputElement, {
      target: { value: "Inserted" },
    });
    fireEvent.change(screen.getByLabelText("Samples Inserted"), { target: { value: "1" } });
    fireEvent.click(screen.getByRole("button", { name: "Export Matrix" }));

    await waitFor(() => expect(apiMocks.previewMatrixEditorLiveXlsxPublication).toHaveBeenCalled());
    expect(
      apiMocks.previewMatrixEditorLiveXlsxPublication.mock.calls[0][1].groups.map(
        (group: { group_key: string }) => group.group_key,
      ),
    ).toEqual(["g1", "manual_group_1", "g2"]);
  });

  it("keeps unique stable identities when duplicating and moving groups", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    const sourceHeader = (await screen.findByRole("checkbox", { name: "Include group 1" }))
      .closest("th") as HTMLElement;
    fireEvent.contextMenu(sourceHeader);
    fireEvent.click(screen.getByRole("button", { name: "Duplicate group" }));

    fireEvent.contextMenu(document.querySelectorAll(".matrix-editor-group-band")[0] as HTMLElement);
    fireEvent.click(screen.getByRole("button", { name: "Move right" }));
    fireEvent.click(screen.getByRole("button", { name: "Export Matrix" }));

    await waitFor(() => expect(apiMocks.previewMatrixEditorLiveXlsxPublication).toHaveBeenCalled());
    expect(
      apiMocks.previewMatrixEditorLiveXlsxPublication.mock.calls[0][1].groups.map(
        (group: { group_key: string }) => group.group_key,
      ),
    ).toEqual(["manual_group_1", "g1"]);
  });

  it("surfaces legacy duplicate group keys without autosaving or exporting them", async () => {
    const seed = buildSessionSeed();
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...seed,
      editor_draft: {
        ...seed.editor_draft,
        groups: [
          seed.editor_draft.groups[0],
          {
            ...seed.editor_draft.groups[0],
            draft_group_id: "manual-group",
            source_group_snapshot_id: null,
            group_order: 2,
            group_key: "g1",
            group_label: "Manual",
          },
        ],
        cells: [
          seed.editor_draft.cells[0],
          { draft_row_id: "row-1", draft_group_id: "manual-group", cell_value: "2" },
        ],
      },
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect((await screen.findByLabelText("Row 1 Manual") as HTMLInputElement).value).toBe("2");
    const identityMessage = /Matrix group identity conflict: g1/;
    expect(screen.getByRole("region", { name: "Matrix input errors" }).textContent).toMatch(identityMessage);
    const exportButton = screen.getByRole("button", { name: "Export Matrix" }) as HTMLButtonElement;
    expect(exportButton.disabled).toBe(true);
    expect(exportButton.title).toMatch(identityMessage);
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(true);

    fireEvent.change(screen.getByLabelText("Row 1 method"), { target: { value: "Do not save" } });
    await new Promise((resolve) => window.setTimeout(resolve, 900));
    expect(apiMocks.saveMatrixEditorSessionDraft).not.toHaveBeenCalled();
    expect(apiMocks.previewMatrixEditorLiveXlsxPublication).not.toHaveBeenCalled();
  });

  it("collapses step details without losing edited text and locates invalid cells", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await screen.findByLabelText("Step 1 description");
    fireEvent.change(screen.getByLabelText("Step 1 description"), { target: { value: "Keep my draft" } });
    fireEvent.click(screen.getByRole("button", { name: "Hide step details" }));
    expect(screen.queryByRole("complementary", { name: "Group Step Workspace" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Show step details" }));
    expect((screen.getByLabelText("Step 1 description") as HTMLTextAreaElement).value).toBe("Keep my draft");

    fireEvent.change(screen.getByLabelText("Row 1 1"), { target: { value: "invalid" } });
    const issues = screen.getByRole("region", { name: "Matrix input errors" });
    fireEvent.click(within(issues).getByRole("button", { name: /Row 1 1/ }));
    expect(document.activeElement).toBe(screen.getByLabelText("Row 1 1"));
    expect(screen.getByLabelText("Row 1 1").getAttribute("aria-invalid")).toBe("true");
    fireEvent.change(screen.getByLabelText("Row 1 1"), { target: { value: "1" } });
    expect(screen.queryByRole("region", { name: "Matrix input errors" })).toBeNull();
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
    expect(screen.getByRole("button", { name: "Test Status" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Fee Evaluation" })).toBeNull();
    const completionDock = screen.getByRole("contentinfo", { name: "Matrix editor completion actions" });
    expect((completionDock as HTMLElement).classList.contains("matrix-editor-completion-dock")).toBe(true);
    expect(screen.getByRole("button", { name: "Cancel" })).toBeTruthy();
    const confirmMatrix = screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement;
    expect(confirmMatrix.disabled).toBe(true);
    expect(confirmMatrix.title).toBe("No Matrix changes to confirm.");
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

  it("does not expose the retired Matrix Step quantity setup", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft_id: "draft-test",
      saved_payload_signature: "saved-signature",
    });

    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByRole("button", { name: "Confirm Matrix" })).toBeTruthy();
    expect(screen.queryByRole("region", { name: "Step quantity setup" })).toBeNull();
  });

  it("replaces the legacy contact editor with the dedicated setup entry", async () => {
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce({
      ...buildSessionSeed(),
      editor_draft_id: "draft-test",
      saved_payload_signature: "saved-signature",
    });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);

    expect(await screen.findByRole("heading", { name: "Test points" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Setup" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Save contact plan" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Apply to blank contact targets" })).toBeNull();
  });

  it("confirms before downloading a Test Record from current unconfirmed Matrix state", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));

    fireEvent.change(screen.getByLabelText("Row 1 method"), {
      target: { value: "Updated unsaved UI method" },
    });
    fireEvent.change(screen.getByLabelText("Step 1 description"), {
      target: { value: "Draft-only step description" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Test record" }));

    const dialog = await screen.findByRole("alertdialog", {
      name: "Download Test Record draft preview?",
    });
    expect(
      within(dialog).getByText(/unconfirmed draft/i)
    ).toBeTruthy();
    expect(apiMocks.generateMatrixEditorTestRecordDraftDownload).not.toHaveBeenCalled();
    fireEvent.click(within(dialog).getByRole("button", { name: "Download draft preview" }));

    await waitFor(() =>
      expect(apiMocks.generateMatrixEditorTestRecordDraftDownload).toHaveBeenCalledTimes(1)
    );
    const [projectId, payload] = apiMocks.generateMatrixEditorTestRecordDraftDownload.mock.calls[0];
    expect(projectId).toBe("P1");
    expect(payload.source).toBe("matrix_editor_current_ui_state");
    expect(payload.preview_token).toBe("download-preview-token");
    expect(payload.step_text_overrides).toEqual([{
      group_key: "g1", row_order: 1, step_sequence: 1, step_suffix_note: "",
      description: "Draft-only step description", requirement: null,
    }]);
    expect(payload.groups).toEqual([
      {
        group_key: "g1",
        group_label: "1",
        sample_quantity_expression: "5",
        sample_note: null,
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

  it("confirms a preview download when Matrix is confirmed but no project folder is available", async () => {
    apiMocks.previewMatrixEditorTestRecordPublication.mockResolvedValueOnce({
      project_id: "P1",
      mode: "download",
      status: "ready",
      authority_status: "confirmed",
      target_path: null,
      existing_file: false,
      existing_modified_at: null,
      blockers: [],
      preview_token: "confirmed-download-token",
    });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));

    fireEvent.click(screen.getByRole("button", { name: "Test record" }));

    const dialog = await screen.findByRole("alertdialog", {
      name: "Download Test Record preview?",
    });
    expect(within(dialog).getByText(/no available project folder/i)).toBeTruthy();
    fireEvent.click(within(dialog).getByRole("button", { name: "Download preview" }));
    await waitFor(() =>
      expect(apiMocks.generateMatrixEditorTestRecordDraftDownload).toHaveBeenCalledWith(
        "P1",
        expect.objectContaining({ preview_token: "confirmed-download-token" })
      )
    );
  });

  it("cancels the Test Record preview confirmation without creating a file or state change", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));

    fireEvent.click(screen.getByRole("button", { name: "Test record" }));
    const dialog = await screen.findByRole("alertdialog", {
      name: "Download Test Record draft preview?",
    });
    fireEvent.click(within(dialog).getByRole("button", { name: "Cancel" }));

    expect(apiMocks.generateMatrixEditorTestRecordDraftDownload).not.toHaveBeenCalled();
    expect(apiMocks.publishMatrixEditorTestRecord).not.toHaveBeenCalled();
    expect(screen.queryByRole("alertdialog")).toBeNull();
  });

  it("saves Test Record directly to Submitted Material when the official folder exists", async () => {
    apiMocks.previewMatrixEditorTestRecordPublication.mockResolvedValueOnce({
      project_id: "P1",
      mode: "official",
      status: "ready",
      authority_status: "confirmed",
      target_path: "D:/Projects/DL-001/Submitted Material/DL-001 Test Record.docx",
      existing_file: false,
      existing_modified_at: null,
      blockers: [],
      preview_token: "official-ready-token",
    });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));

    fireEvent.click(screen.getByRole("button", { name: "Test record" }));

    await waitFor(() =>
      expect(apiMocks.publishMatrixEditorTestRecord).toHaveBeenCalledWith(
        "P1",
        expect.objectContaining({
          source: "matrix_editor_current_ui_state",
          preview_token: "official-ready-token",
          conflict_action: "none",
        })
      )
    );
    expect(screen.queryByRole("alertdialog")).toBeNull();
    expect(apiMocks.generateMatrixEditorTestRecordDraftDownload).not.toHaveBeenCalled();
    expect(screen.getByText("Saved DL-001 Test Record.docx to Submitted Material.")).toBeTruthy();
  });

  it("asks how to handle an existing Test Record and archives it only after choice", async () => {
    apiMocks.previewMatrixEditorTestRecordPublication.mockResolvedValueOnce({
      project_id: "P1",
      mode: "official",
      status: "conflict",
      authority_status: "confirmed",
      target_path: "D:/Projects/DL-001/Submitted Material/DL-001 Test Record.docx",
      existing_file: true,
      existing_modified_at: "2026-08-28T12:00:00+08:00",
      blockers: [],
      preview_token: "official-conflict-token",
    });
    apiMocks.publishMatrixEditorTestRecord.mockResolvedValueOnce({
      project_id: "P1",
      target_path: "D:/Projects/DL-001/Submitted Material/DL-001 Test Record.docx",
      archive_path: "D:/Projects/DL-001/History/Test Record/DL-001 Test Record_20260828-120000.docx",
      file_name: "DL-001 Test Record.docx",
    });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));

    fireEvent.click(screen.getByRole("button", { name: "Test record" }));
    const dialog = await screen.findByRole("alertdialog", {
      name: "Replace existing Test Record?",
    });
    expect(screen.getAllByRole("alertdialog")).toHaveLength(1);
    expect(within(dialog).getByRole("button", { name: "Archive old file" })).toBeTruthy();
    expect(
      within(dialog).getByRole("button", { name: "Move old file to Recycle Bin" })
    ).toBeTruthy();
    fireEvent.click(within(dialog).getByRole("button", { name: "Archive old file" }));

    await waitFor(() =>
      expect(apiMocks.publishMatrixEditorTestRecord).toHaveBeenCalledWith(
        "P1",
        expect.objectContaining({
          preview_token: "official-conflict-token",
          conflict_action: "archive",
        })
      )
    );
    expect(screen.queryByRole("alertdialog")).toBeNull();
    expect(
      screen.getByText("Saved DL-001 Test Record.docx; archived the previous file in History.")
    ).toBeTruthy();
  });

  it("downloads a Test Status workbook from current unsaved Matrix Editor state", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));

    fireEvent.change(screen.getByLabelText("Samples 1"), {
      target: { value: "5+5(d)" },
    });
    fireEvent.change(screen.getByLabelText("Row 1 1"), {
      target: { value: "1,8" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Test Status" }));

    await waitFor(() =>
      expect(apiMocks.generateMatrixEditorTestStatusDraftDownload).toHaveBeenCalledTimes(1)
    );
    expect(apiMocks.generateMatrixEditorTestStatusDraftDownload).toHaveBeenCalledWith(
      "P1",
      expect.objectContaining({
        source: "matrix_editor_current_ui_state",
        project_reference: "LTR-0001",
        groups: [expect.objectContaining({ sample_quantity_expression: "5+5(d)" })],
        rows: [expect.objectContaining({ group_values: { g1: "1,8" } })],
      })
    );
    expect(screen.getByText("Downloaded Test Status draft.")).toBeTruthy();
  });

  it("downloads an LLCR preview from the current unsaved Matrix Editor state", async () => {
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />);
    await waitFor(() => expect(apiMocks.fetchMatrixEditorSession).toHaveBeenCalledTimes(1));

    const testPoints = screen.getByRole("region", { name: "Test points" });
    const llcrRow = within(testPoints).getByText("LLCR").closest("div");
    expect(llcrRow).toBeTruthy();
    expect(within(llcrRow as HTMLElement).getByRole("button", { name: "Download LLCR" })).toBeTruthy();
    expect(screen.queryByRole("region", { name: "LLCR and CR tables" })).toBeNull();

    fireEvent.change(screen.getByLabelText("Samples 1"), {
      target: { value: "7" },
    });
    fireEvent.change(screen.getByLabelText("Row 1 method"), {
      target: { value: "Unsaved LLCR method" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Download LLCR" }));

    await waitFor(() =>
      expect(apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload).toHaveBeenCalledTimes(1)
    );
    expect(apiMocks.generateMatrixEditorLlcrCrRecordDraftDownload).toHaveBeenCalledWith(
      "P1",
      expect.objectContaining({
        source: "matrix_editor_current_ui_state",
        record_type: "llcr",
        groups: [{
          group_key: "g1",
          group_label: "1",
          sample_quantity_expression: "7",
          sample_note: null,
        }],
        rows: [expect.objectContaining({ method: "Unsaved LLCR method" })],
      }),
    );
  });

  it("loads imported Method Condition and Requirement from the saved draft", async () => {
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
        rows: [{ ...seed.editor_draft.rows[0], test_item: "Contact Resistance (Low Level)",
          source_section: "6.1", method: "EIA-364-23D", condition: "20mV max, 100mA max",
          requirement: "Initial <= 0.25 milliohms" }],
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
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(true);
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
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(true);
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
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(true);
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

});
