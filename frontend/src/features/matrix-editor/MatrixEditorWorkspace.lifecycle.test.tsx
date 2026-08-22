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
