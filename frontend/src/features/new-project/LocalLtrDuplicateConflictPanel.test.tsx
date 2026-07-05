import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { LocalLtrDuplicateConflictPanel } from "./LocalLtrDuplicateConflictPanel";
import type { LocalLtrDuplicateConflictDetail } from "../../api/client";

describe("LocalLtrDuplicateConflictPanel", () => {
  it("shows existing local owner summary and requires a second confirmation", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();
    const onOpenExisting = vi.fn();
    const onConfirm = vi.fn();

    render(
      <LocalLtrDuplicateConflictPanel
        conflict={conflict}
        confirming={false}
        onCancel={onCancel}
        onConfirm={onConfirm}
        onOpenExisting={onOpenExisting}
      />
    );

    expect(screen.getByRole("alertdialog")).toBeTruthy();
    expect(
      screen.getByText("DL-2026-05-777 Existing sample assembly Qualification Testing")
    ).toBeTruthy();
    expect(screen.queryByText("Local LTR conflict")).toBeNull();
    expect(screen.queryByText("LTR number already exists locally")).toBeNull();
    expect(screen.queryByText("OLD-PROJECT")).toBeNull();
    expect(screen.queryByText("Project folder")).toBeNull();

    expect(screen.queryByText("I understand the old local history will be kept and this project becomes current.")).toBeNull();

    const replaceButton = screen.getByRole("button", { name: "Replace local owner" });
    const confirmationNote = screen.getByLabelText("Confirmation note");
    expect(replaceButton).toHaveProperty("disabled", true);

    await user.click(replaceButton);
    expect(onConfirm).not.toHaveBeenCalled();

    await user.type(confirmationNote, "Confirmed by lab coordinator");
    expect(replaceButton).toHaveProperty("disabled", false);
    await user.click(replaceButton);

    expect(onConfirm).toHaveBeenCalledWith({
      action: "replace_local_association",
      token: "token-1",
      acknowledged: true,
      reason: "Confirmed by lab coordinator",
    });
  });

  it("exposes safe open existing and cancel actions", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();
    const onOpenExisting = vi.fn();

    render(
      <LocalLtrDuplicateConflictPanel
        conflict={conflict}
        confirming={false}
        onCancel={onCancel}
        onConfirm={vi.fn()}
        onOpenExisting={onOpenExisting}
      />
    );

    await user.click(screen.getByRole("button", { name: "Open existing project" }));
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onOpenExisting).toHaveBeenCalledWith("P-OLD");
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("shows a local replacing state while the confirmation request is pending", async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn(
      () =>
        new Promise<void>(() => {
          // Keep the request pending so the button state is observable.
        })
    );

    render(
      <LocalLtrDuplicateConflictPanel
        conflict={conflict}
        confirming={false}
        onCancel={vi.fn()}
        onConfirm={onConfirm}
        onOpenExisting={vi.fn()}
      />
    );

    await user.type(screen.getByLabelText("Confirmation note"), "Confirmed");
    await user.click(screen.getByRole("button", { name: "Replace local owner" }));

    expect(screen.getByRole("button", { name: "Replacing..." })).toHaveProperty(
      "disabled",
      true
    );
  });
});

const conflict: LocalLtrDuplicateConflictDetail = {
  code: "LOCAL_LTR_DUPLICATE",
  message: "This LTR number already has a local ConnLab owner.",
  ltr_number: "DL-2026-05-777",
  existing: {
    ltr_id: "LTR-OLD",
    project_id: "P-OLD",
    display_project_id: "OLD-PROJECT",
    project_name: "Existing Connector",
    product_name: "Existing Connector",
    sample_description: "Existing sample assembly",
    test_item: "Qualification Testing",
    requester: "Alice",
    registered_on: "2026-05-07",
    recent_activity_at: "2026-05-07",
    project_status: "ltr_registered",
    lifecycle_state: "active",
    has_local_folder: true,
    local_folder_path: "D:\\Test Project\\DL-2026-05-777",
    has_matrix: false,
    has_outputs: false,
  },
  current: {
    case_id: "CASE-NEW",
    project_id: "P-NEW",
    project_name: "Current Connector",
    requester: "Bob",
  },
  resolution: {
    token: "token-1",
    expires_at: "2026-07-02T12:00:00Z",
    allowed_actions: ["open_existing", "cancel", "replace_local_association"],
    requires_second_confirmation: true,
  },
};
