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
import { ApiRequestError } from "../../api/client";
import { MatrixEditorWorkspace } from "./MatrixEditorWorkspace";

installMatrixEditorWorkspaceTestLifecycle();

describe("MatrixEditorWorkspace save, cancel, and confirm lifecycle", () => {
  it("saves step-local text, restores it on reopen, and retains it when confirmation fails", async () => {
    const seed = buildSessionSeed();
    seed.source_preview_payload.rows[0].group_tokens = { "1": "1,2", g1: "1,2" };
    seed.editor_draft.cells[0].cell_value = "1,2";
    apiMocks.fetchMatrixEditorSession.mockResolvedValue(seed);
    const onBack = vi.fn();
    const first = render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBack} />);
    fireEvent.change(await screen.findByLabelText("Step 1 description"), {
      target: { value: "Only this step" },
    });
    fireEvent.change(screen.getByLabelText("Step 1 requirement"), {
      target: { value: "Local requirement" },
    });
    expect(screen.getByLabelText("Step 2 description")).toHaveProperty("value", "Visual Examination");
    expect(screen.getByLabelText("Row 1 test item")).toHaveProperty("value", "Visual Examination");
    await waitFor(() => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 });
    const saved = apiMocks.saveMatrixEditorSessionDraft.mock.calls[0][1];
    expect(saved.step_text_overrides).toEqual([{
      draft_group_id: "group-1", draft_row_id: "row-1", step_sequence: 1,
      step_suffix_note: "", description: "Only this step", requirement: "Local requirement",
    }]);
    expect(apiMocks.confirmMatrixEditorSession).not.toHaveBeenCalled();
    first.unmount();
    apiMocks.fetchMatrixEditorSession.mockResolvedValue({ ...seed,
      editor_draft_id: "editor-draft-1", saved_payload_signature: "saved-signature-1",
      editor_draft: { ...seed.editor_draft, step_text_overrides: saved.step_text_overrides },
    });
    apiMocks.confirmMatrixEditorSession.mockRejectedValueOnce(new Error("Confirmation unavailable. Please retry."));
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBack} />);
    expect(await screen.findByLabelText("Step 1 description")).toHaveProperty("value", "Only this step");
    expect(screen.getByLabelText("Step 1 requirement")).toHaveProperty("value", "Local requirement");
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    expect(await screen.findByText("Confirmation unavailable. Please retry.")).toBeTruthy();
    expect(onBack).not.toHaveBeenCalled();
    expect(screen.getByLabelText("Step 1 description")).toHaveProperty("value", "Only this step");
    expect(apiMocks.confirmMatrixEditorSession.mock.calls[0][1].step_text_overrides)
      .toEqual(saved.step_text_overrides);
  });

  it("keeps explicit blank step text local to one group and one repeated LLCR step", async () => {
    const seed = buildSessionSeed();
    seed.editor_draft.rows[0].test_item = "Contact Resistance (Low Level)";
    seed.editor_draft.rows[0].requirement = "Initial <= 0.25 mΩ; R<= 0.17 mΩ";
    seed.editor_draft.groups.push({ ...seed.editor_draft.groups[0],
      draft_group_id: "group-2", source_group_snapshot_id: "sg-2", group_order: 2,
      group_key: "g2", group_label: "2",
    });
    seed.editor_draft.cells = [
      { draft_row_id: "row-1", draft_group_id: "group-1", cell_value: "1(a),2" },
      { draft_row_id: "row-1", draft_group_id: "group-2", cell_value: "1(a),2" },
    ];
    apiMocks.fetchMatrixEditorSession.mockResolvedValue({ ...seed, source_preview_payload: null });
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={vi.fn()} />);
    fireEvent.change(await screen.findByLabelText("Step 1 description"), { target: { value: "" } });
    fireEvent.change(screen.getByLabelText("Step 1 requirement"), { target: { value: "" } });
    expect(screen.getByLabelText("Step 1 description")).toHaveProperty("value", "");
    expect(screen.getByLabelText("Step 1 requirement")).toHaveProperty("value", "");
    expect(screen.getByLabelText("Step 2 description")).toHaveProperty("value", "Final LLCR");
    fireEvent.click(screen.getByLabelText("Include group 2").closest("th")!);
    expect(screen.getByLabelText("Step 1 description")).toHaveProperty("value", "Initial LLCR");
    expect(screen.getByLabelText("Step 1 requirement")).toHaveProperty("value", "<= 0.25 mΩ");
    await waitFor(() => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 });
    expect(apiMocks.saveMatrixEditorSessionDraft.mock.calls[0][1].step_text_overrides).toEqual([{
      draft_group_id: "group-1", draft_row_id: "row-1", step_sequence: 1,
      step_suffix_note: "(a)", description: "", requirement: "",
    }]);
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
    expect(apiMocks.previewProjectTestPlanMatrixFromSourceCandidate).not.toHaveBeenCalled();
    expect(apiMocks.previewProjectTestPlanMatrixFromUpload).not.toHaveBeenCalled();
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

  it("returns to Workbench when the server canonicalizes an edited Matrix to no changes", async () => {
    apiMocks.confirmMatrixEditorSession.mockResolvedValueOnce({
      publish_status: "no_change",
      message: "No Matrix changes to confirm.",
      confirmed_snapshot: null,
    });
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);
    fireEvent.change(await screen.findByLabelText("Row 1 method"), {
      target: { value: "Updated method before canonical no-change" },
    });
    await waitFor(
      () => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 }
    );
    fireEvent.click(await screen.findByRole("button", { name: "Confirm Matrix" }));
    await waitFor(() => {
      expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(1);
      expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    });
  });

  it("keeps edits visible and reports failure when stale confirmation cannot be recovered", async () => {
    apiMocks.confirmMatrixEditorSession
      .mockRejectedValueOnce(new ApiRequestError("stale", 409, { code: "active_matrix_changed" }))
      .mockRejectedValueOnce(new Error("Confirmation unavailable. Please retry."));
    apiMocks.fetchMatrixEditorSession
      .mockResolvedValueOnce(buildSessionSeed())
      .mockResolvedValueOnce({ ...buildSessionSeed(), active_confirmed_matrix_id: "confirmed-2",
        active_confirmed_revision: 4 });
    const onBackToWorkbench = vi.fn();
    render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBackToWorkbench} />);
    fireEvent.change(await screen.findByLabelText("Row 1 method"), {
      target: { value: "Unsaved confirmation must stay visible" },
    });
    await waitFor(() => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 });
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    expect(await screen.findByText("Confirmation unavailable. Please retry.")).toBeTruthy();
    expect(onBackToWorkbench).not.toHaveBeenCalled();
    expect((screen.getByLabelText("Row 1 method") as HTMLTextAreaElement).value)
      .toBe("Unsaved confirmation must stay visible");
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
    fireEvent.change(await screen.findByLabelText("Row 1 method"), {
      target: { value: "Updated method before stale confirm" },
    });
    await waitFor(
      () => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 }
    );
    fireEvent.click(await screen.findByRole("button", { name: "Confirm Matrix" }));
    await waitFor(() => {
      expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(2);
      expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    });
  });
});
