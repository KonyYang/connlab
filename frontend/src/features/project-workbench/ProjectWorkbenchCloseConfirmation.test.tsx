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
  it("keeps output checks out of the confirmation and still closes with the selected reason", async () => {
    const onCloseProject = vi.fn();
    render(<ProjectWorkbenchCloseConfirmation lifecycleActions={lifecycleActions}
      lifecycleBusy={false} onCloseProject={onCloseProject} projectIdentity="Connector A"
      projectReference="DL-2026-01-002" initiallyOpen outputStatusSummary={{project_id: "A", active_draft_id: null,
        active_draft_version: null, items: [{output_kind: "ir_dwv_record_form", status: "stale",
          reason: "Matrix test points have changed.", output_path: null, source: null,
          draft_id: null, draft_version: null, updated_at: null}]}} />);
    const user = userEvent.setup();
    const dialog = within(screen.getByRole("dialog"));
    expect(dialog.queryByText("View output details")).toBeNull();
    expect(dialog.queryByText("Matrix test points have changed.")).toBeNull();
    await user.click(dialog.getByRole("radio", {name: "Completed"}));
    await user.click(dialog.getByRole("button", {name: "Close project"}));
    expect(onCloseProject).toHaveBeenCalledWith("completed", "");
  });

  it("shows four explicit reasons without a default or a mandatory optional-note field", async () => {
    const onCloseProject = vi.fn();
    const user = setup(onCloseProject);
    await user.click(screen.getByRole("button", {name: "Close project"}));
    const dialog = within(screen.getByRole("dialog", {name: "Close project"}));
    expect(dialog.getByText("DL-2026-01-002")).toBeTruthy();
    const reasons = within(dialog.getByRole("group", {name: "Close reason"}));
    expect(reasons.getAllByRole("radio")).toHaveLength(4);
    expect(reasons.getAllByRole("radio").every((radio) => !(radio as HTMLInputElement).checked)).toBe(true);
    expect(dialog.getByRole("button", {name: "Close project"})).toHaveProperty("disabled", true);
    expect(dialog.queryByRole("textbox")).toBeNull();
    expect(dialog.queryByText(/output needs review/)).toBeNull();
    await user.click(reasons.getByRole("radio", {name: "Completed"}));
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
    await user.click(dialog.getByRole("radio", {name: "Other"}));
    expect(dialog.getByRole("button", {name: "Close project"})).toHaveProperty("disabled", true);
    await user.type(dialog.getByLabelText(/Additional note/), "Scope changed");
    await user.dblClick(dialog.getByRole("button", {name: "Close project"}));
    expect(onCloseProject).toHaveBeenCalledTimes(1);
    await user.keyboard("{Escape}");
    expect(screen.getByRole("dialog")).toBeTruthy();
    expect(dialog.getByRole("radio", {name: "Other"}).matches(":disabled")).toBe(true);
    reject(new Error("Project changed. Review and retry."));
    expect(await dialog.findByRole("alert")).toHaveProperty("textContent", "Project changed. Review and retry.");
    expect(dialog.getByLabelText(/Additional note/)).toHaveProperty("value", "Scope changed");
  });

  it("rejects a blank Other explanation and keeps a written note visible when changing reason", async () => {
    const onCloseProject = vi.fn();
    const user = setup(onCloseProject);
    await user.click(screen.getByRole("button", {name: "Close project"}));
    const dialog = within(screen.getByRole("dialog"));
    await user.click(dialog.getByRole("radio", {name: "Other"}));
    await user.type(dialog.getByRole("textbox"), "   ");
    expect(dialog.getByRole("button", {name: "Close project"})).toHaveProperty("disabled", true);
    await user.clear(dialog.getByRole("textbox"));
    await user.type(dialog.getByRole("textbox"), "  Request withdrawn  ");
    await user.click(dialog.getByRole("radio", {name: "Cancelled"}));
    expect(dialog.getByRole("textbox", {name: "Additional note (optional)"})).toHaveProperty("value", "  Request withdrawn  ");
    await user.click(dialog.getByRole("button", {name: "Close project"}));
    expect(onCloseProject).toHaveBeenCalledWith("cancelled", "Request withdrawn");
  });

  it("allows an optional note for normal reasons and discards the form on cancellation", async () => {
    const onCloseProject = vi.fn();
    const user = setup(onCloseProject);
    const trigger = screen.getByRole("button", {name: "Close project"});
    await user.click(trigger);
    let dialog = within(screen.getByRole("dialog"));
    await user.click(dialog.getByRole("radio", {name: "Cancelled"}));
    await user.click(dialog.getByRole("button", {name: "Add note"}));
    expect(document.activeElement).toBe(dialog.getByRole("textbox", {name: /Additional note/}));
    await user.type(dialog.getByRole("textbox"), "Request withdrawn");
    await user.click(dialog.getByRole("button", {name: "Cancel"}));
    expect(onCloseProject).not.toHaveBeenCalled();
    await user.click(trigger);
    dialog = within(screen.getByRole("dialog"));
    expect(dialog.queryByRole("textbox")).toBeNull();
    expect(dialog.getAllByRole("radio").every((radio) => !(radio as HTMLInputElement).checked)).toBe(true);
    await user.click(dialog.getByRole("radio", {name: "Unable to continue"}));
    await user.click(dialog.getByRole("button", {name: "Add note"}));
    await user.type(dialog.getByRole("textbox"), "Samples unavailable");
    await user.click(dialog.getByRole("button", {name: "Close project"}));
    expect(onCloseProject).toHaveBeenCalledWith("cannot_test", "Samples unavailable");
  });

  it("returns keyboard focus after Escape and traps tabbing inside the confirmation", async () => {
    const user = setup();
    const trigger = screen.getByRole("button", {name: "Close project"});
    await user.click(trigger);
    const dialog = within(screen.getByRole("dialog"));
    expect(document.activeElement).toBe(dialog.getByRole("radio", {name: "Completed"}));
    await user.click(dialog.getByRole("radio", {name: "Cancelled"}));
    await user.tab({shift: true});
    expect(document.activeElement).toBe(dialog.getByRole("button", {name: "Close project"}));
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(trigger);
  });
});
