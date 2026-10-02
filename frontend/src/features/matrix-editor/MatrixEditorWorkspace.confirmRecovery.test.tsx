import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import {
  apiMocks,
  buildSessionSeed,
  createDeferred,
  installMatrixEditorWorkspaceTestLifecycle,
} from "./MatrixEditorWorkspace.testSupport";
import { ApiRequestError } from "../../api/client";
import { MatrixEditorWorkspace } from "./MatrixEditorWorkspace";

installMatrixEditorWorkspaceTestLifecycle();

const pairs = "P1&P2, S1&Housing";

function missingDraftError() {
  const message = "Saved Matrix draft is no longer available. Reload the latest Matrix.";
  return new ApiRequestError(message, 409, {
    code: "matrix_editor_draft_conflict",
    message,
  });
}

async function openChangedMatrix(onBack = vi.fn()) {
  render(<MatrixEditorWorkspace projectId="P1" onBackToWorkbench={onBack} />);
  fireEvent.change(await screen.findByRole("textbox", { name: "IR / DWV test points" }), {
    target: { value: pairs },
  });
  await waitFor(() => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalled(), {
    timeout: 1600,
  });
  await waitFor(() => expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(false));
  return onBack;
}

describe("Matrix confirmation draft recovery", () => {
  it("recreates a missing draft with the current inputs and confirms its new tokens", async () => {
    apiMocks.confirmMatrixEditorSession.mockRejectedValueOnce(missingDraftError());
    apiMocks.saveMatrixEditorSessionDraft.mockResolvedValueOnce({
      editor_draft_id: "draft-before-deletion", saved_payload_signature: "old-signature",
      active_confirmed_matrix_id: "confirmed-1", active_confirmed_revision: 3,
      draft_status: "current", draft_updated_at: "2026-10-02T01:00:00Z",
    }).mockResolvedValueOnce({
      editor_draft_id: "recovered-draft", saved_payload_signature: "recovered-signature",
      active_confirmed_matrix_id: "confirmed-1", active_confirmed_revision: 3,
      draft_status: "current", draft_updated_at: "2026-10-02T01:01:00Z",
    });
    const onBack = await openChangedMatrix();
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    await waitFor(() => expect(onBack).toHaveBeenCalled());
    expect(apiMocks.confirmMatrixEditorSession.mock.lastCall?.[1]).toEqual(expect.objectContaining({
      expected_editor_draft_id: "recovered-draft",
      expected_saved_payload_signature: "recovered-signature",
      expected_active_confirmed_matrix_id: "confirmed-1",
      point_profile: expect.objectContaining({ electrical_point_pairs: pairs }),
    }));
    expect(apiMocks.saveMatrixEditorSessionDraft.mock.lastCall?.[1].point_profile)
      .toEqual(expect.objectContaining({ electrical_point_pairs: pairs }));
  });

  it("retains inputs without saving over a newer Matrix authority", async () => {
    apiMocks.confirmMatrixEditorSession.mockRejectedValueOnce(missingDraftError());
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce(buildSessionSeed())
      .mockResolvedValueOnce({ ...buildSessionSeed(), active_confirmed_matrix_id: "confirmed-2",
        active_confirmed_revision: 4 });
    const onBack = await openChangedMatrix();
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    await screen.findByText(/Matrix authority changed.*Your edits remain here/);
    expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1);
    expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(1);
    expect((screen.getByRole("textbox", { name: "IR / DWV test points" }) as HTMLTextAreaElement).value).toBe(pairs);
    expect(onBack).not.toHaveBeenCalled();
  });

  it("does not replace a draft that is now available on the server", async () => {
    apiMocks.confirmMatrixEditorSession.mockRejectedValueOnce(missingDraftError());
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce(buildSessionSeed()).mockResolvedValueOnce({
      ...buildSessionSeed(), editor_draft_id: "another-draft", saved_payload_signature: "another-signature",
    });
    const onBack = await openChangedMatrix();
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    await screen.findByText(/A saved Matrix draft is already available/);
    expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1);
    expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(1);
    expect(onBack).not.toHaveBeenCalled();
  });

  it("keeps inputs and permits retry after the recovery save fails", async () => {
    apiMocks.confirmMatrixEditorSession.mockRejectedValueOnce(missingDraftError());
    const onBack = await openChangedMatrix();
    apiMocks.saveMatrixEditorSessionDraft.mockRejectedValueOnce(new Error("Connection interrupted"));
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    await screen.findByText(/Your edits remain here.*Connection interrupted/);
    expect(onBack).not.toHaveBeenCalled();
    expect((screen.getByRole("textbox", { name: "IR / DWV test points" }) as HTMLTextAreaElement).value).toBe(pairs);
    expect((screen.getByRole("button", { name: "Confirm Matrix" }) as HTMLButtonElement).disabled).toBe(false);
    apiMocks.confirmMatrixEditorSession.mockRejectedValueOnce(missingDraftError());
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    await waitFor(() => expect(onBack).toHaveBeenCalled());
    expect(apiMocks.confirmMatrixEditorSession.mock.lastCall?.[1].expected_editor_draft_id).toBe("editor-draft-1");
  });

  it("stops if inputs change during recovery and disables repeated confirmation", async () => {
    apiMocks.confirmMatrixEditorSession.mockRejectedValueOnce(missingDraftError());
    const onBack = await openChangedMatrix();
    const recoverySave = createDeferred<Awaited<ReturnType<typeof apiMocks.saveMatrixEditorSessionDraft>>>();
    apiMocks.saveMatrixEditorSessionDraft.mockReturnValueOnce(recoverySave.promise);
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    await waitFor(() => expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(2));
    const busyButton = screen.getByRole("button", { name: "Confirming..." }) as HTMLButtonElement;
    expect(busyButton.disabled).toBe(true);
    fireEvent.click(busyButton);
    fireEvent.change(screen.getByLabelText("Row 1 requirement"), { target: { value: "New requirement" } });
    recoverySave.resolve({ editor_draft_id: "recovered-draft", saved_payload_signature: "recovered-signature",
      active_confirmed_matrix_id: "confirmed-1", active_confirmed_revision: 3,
      draft_status: "current", draft_updated_at: "2026-10-02T01:01:00Z" });
    await screen.findByText(/Matrix edits changed while saving/);
    expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(1);
    expect((screen.getByLabelText("Row 1 requirement") as HTMLTextAreaElement).value).toBe("New requirement");
    expect(onBack).not.toHaveBeenCalled();
  });

  it("does not save or retry confirmation when the session check is unavailable", async () => {
    apiMocks.confirmMatrixEditorSession.mockRejectedValueOnce(missingDraftError());
    apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce(buildSessionSeed())
      .mockRejectedValueOnce(new Error("Latest Matrix check unavailable"));
    const onBack = await openChangedMatrix();
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    await screen.findByText(/Your edits remain here.*Latest Matrix check unavailable/);
    expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(1);
    expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(1);
    expect(onBack).not.toHaveBeenCalled();
  });

  it("limits automatic confirmation recovery to one attempt", async () => {
    apiMocks.confirmMatrixEditorSession.mockRejectedValue(missingDraftError());
    const onBack = await openChangedMatrix();
    fireEvent.click(screen.getByRole("button", { name: "Confirm Matrix" }));
    await screen.findByText(/Matrix confirmation could not complete/);
    expect(apiMocks.saveMatrixEditorSessionDraft).toHaveBeenCalledTimes(2);
    expect(apiMocks.confirmMatrixEditorSession).toHaveBeenCalledTimes(2);
    expect((screen.getByRole("textbox", { name: "IR / DWV test points" }) as HTMLTextAreaElement).value).toBe(pairs);
    expect(onBack).not.toHaveBeenCalled();
  });
});
