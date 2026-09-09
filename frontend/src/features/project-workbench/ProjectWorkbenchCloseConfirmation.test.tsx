import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProjectWorkbenchCloseConfirmation } from "./ProjectWorkbenchCloseConfirmation";
import { deriveProjectWorkbenchLifecycleActions } from "./projectWorkbenchLifecycleSelectors";

const lifecycleActions = deriveProjectWorkbenchLifecycleActions({
  project_id: "A", lifecycle_state: "active", closure_type: null, status_label: "Active",
  readonly: false, allowed_actions: ["close"], status: "active", warnings: [],
});

function setup(onCloseProject = vi.fn()) {
  render(<ProjectWorkbenchCloseConfirmation lifecycleActions={lifecycleActions}
    lifecycleBusy={false} onCloseProject={onCloseProject} projectIdentity="Connector A"
    projectReference="DL-2026-01-002" outputStatusSummary={{project_id: "A", active_draft_id: null,
      active_draft_version: null, items: [{output_kind: "approval_package", status: "missing",
        reason: "Approval package has not been placed.", output_path: null, source: null,
        draft_id: null, draft_version: null, updated_at: null}]}} />);
  return userEvent.setup();
}

describe("ProjectWorkbenchCloseConfirmation", () => {
  it("requires a selected reason, permits Completed without a note and summarizes output exceptions", async () => {
    const onCloseProject = vi.fn();
    const user = setup(onCloseProject);
    await user.click(screen.getByRole("button", {name: "Close project"}));
    const dialog = within(screen.getByRole("dialog", {name: "Close project DL-2026-01-002"}));
    expect(dialog.getByLabelText("Close reason")).toHaveProperty("value", "");
    expect(dialog.getByRole("button", {name: "Close project"})).toHaveProperty("disabled", true);
    expect(dialog.queryByRole("option", {name: "Failed"})).toBeNull();
    expect(dialog.queryByRole("option", {name: "Duplicate"})).toBeNull();
    expect(dialog.getByText("1 output needs review")).toBeTruthy();
    expect(dialog.getByText("View output details").closest("details")).toHaveProperty("open", false);
    await user.selectOptions(dialog.getByLabelText("Close reason"), "completed");
    await user.click(dialog.getByRole("button", {name: "Close project"}));
    expect(onCloseProject).toHaveBeenCalledWith("completed", "");
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
  });

  it("requires explanation only for Other, preserves failed input and blocks duplicate submission", async () => {
    let reject!: (error: Error) => void;
    const onCloseProject = vi.fn(() => new Promise<void>((_resolve, rejectFn) => {reject = rejectFn;}));
    const user = setup(onCloseProject);
    await user.click(screen.getByRole("button", {name: "Close project"}));
    const dialog = within(screen.getByRole("dialog"));
    await user.selectOptions(dialog.getByLabelText("Close reason"), "other");
    expect(dialog.getByRole("button", {name: "Close project"})).toHaveProperty("disabled", true);
    await user.type(dialog.getByLabelText(/Additional note/), "Scope changed");
    await user.dblClick(dialog.getByRole("button", {name: "Close project"}));
    expect(onCloseProject).toHaveBeenCalledTimes(1);
    reject(new Error("Project changed. Review and retry."));
    expect(await dialog.findByRole("alert")).toHaveProperty("textContent", "Project changed. Review and retry.");
    expect(dialog.getByLabelText(/Additional note/)).toHaveProperty("value", "Scope changed");
  });

  it("returns keyboard focus after Escape and traps tabbing inside the confirmation", async () => {
    const user = setup();
    const trigger = screen.getByRole("button", {name: "Close project"});
    await user.click(trigger);
    const dialog = within(screen.getByRole("dialog"));
    expect(document.activeElement).toBe(dialog.getByLabelText("Close reason"));
    await user.tab({shift: true});
    expect(document.activeElement).toBe(dialog.getByRole("button", {name: "Cancel"}));
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(trigger);
  });
});
