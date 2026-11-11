import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { ProjectRegistryEntry, ProjectRegistryPreview } from "../../api/projectRegistryManagement";
import { ProjectRegistryManagementDialog } from "./ProjectRegistryManagementDialog";

const entry = (id: string): ProjectRegistryEntry => ({project_id: id, display_project_id: "DL-2026-01-002",
  sample_description: `Sample ${id}`, requestor: "Lab", created_on: "2026-01-01", test_item: "LLCR",
  lifecycle_state: "closed", close_reason_label: "Completed", registry_state: "trash", registry_revision: 1,
  changed_at: "2026-01-02", reason: "Duplicate"});
const base: ProjectRegistryPreview = {project: entry("original-record"), action: "restore", token: "fresh",
  conflicts: [entry("existing-record-one"), entry("existing-record-two")], blockers: [],
  retained_data: ["Matrix and reports are retained."], warnings: []};

function setup(preview = base, stale = false, state: {busy?: boolean; loading?: boolean} = {}) {
  const onRestore = vi.fn(); const onTrash = vi.fn(); const onCancel = vi.fn(); const onRefresh = vi.fn();
  render(<ProjectRegistryManagementDialog action={preview.action} preview={preview} busy={state.busy ?? false} loading={state.loading ?? false}
    stale={stale} error={stale ? "Refresh required" : null} onRestore={onRestore} onTrash={onTrash}
    onCancel={onCancel} onRefresh={onRefresh} />);
  return {user: userEvent.setup(), onRestore, onTrash, onCancel, onRefresh};
}
describe("project management decisions", () => {
  it("shows every independent conflicting record and makes the two safe restore choices explicit", async () => {
    const {user, onRestore} = setup();
    const dialog = within(screen.getByRole("dialog"));
    expect(dialog.getByText("Sample original-record")).toBeTruthy();
    expect(dialog.getByText("Sample existing-record-one")).toBeTruthy();
    expect(dialog.getByText("Sample existing-record-two")).toBeTruthy();
    expect(dialog.getByText(/does not overwrite/)).toBeTruthy();
    await user.click(dialog.getByRole("button", {name: "Restore and retain conflicts"}));
    expect(onRestore).toHaveBeenCalledWith("active", true);
  });
  it("can retain the restored record as history without replacing any current project", async () => {
    const {user, onRestore} = setup();
    await user.click(screen.getByRole("button", {name: "Keep as retained record"}));
    expect(onRestore).toHaveBeenCalledWith("history", false);
  });
  it("does not mutate on cancel and disables restore until stale evidence has been refreshed", async () => {
    const {user, onRestore, onCancel, onRefresh} = setup(base, true);
    expect(screen.getByRole("button", {name: "Keep as retained record"})).toHaveProperty("disabled", true);
    await user.click(screen.getByRole("button", {name: "Refresh preview"}));
    expect(onRefresh).toHaveBeenCalledOnce();
    await user.click(screen.getByRole("button", {name: "Cancel"}));
    expect(onCancel).toHaveBeenCalledOnce(); expect(onRestore).not.toHaveBeenCalled();
  });
  it("shows the deletion boundary and blocks deletion during an active operation", async () => {
    const {onTrash} = setup({...base, action: "trash", conflicts: [], blockers: ["A file generation is running."]});
    expect(screen.getByText(/Files and LTR records stay unchanged/)).toBeTruthy();
    expect(screen.getByText("A file generation is running.")).toBeTruthy();
    expect(screen.getByRole("button", {name: "Move to recycle bin"})).toHaveProperty("disabled", true);
    expect(onTrash).not.toHaveBeenCalled();
  });

  it("keeps the deletion identity compact and starts with an editable existing reason", async () => {
    const {user, onTrash} = setup({...base, action: "trash", conflicts: [],
      warnings: ["Existing external files and LTR associations are retained."]});
    const dialog = within(screen.getByRole("dialog"));
    expect(dialog.getByText("DL-2026-01-002")).toBeTruthy();
    expect(dialog.getByText("Sample original-record")).toBeTruthy();
    expect(dialog.getByText("LLCR")).toBeTruthy();
    expect(dialog.queryByText(/Created 2026/)).toBeNull();
    expect(dialog.queryByText(/Record original/)).toBeNull();
    expect(dialog.queryByText("Retained project records")).toBeNull();
    expect(dialog.queryByText("Existing external files and LTR associations are retained.")).toBeNull();
    expect(dialog.getByLabelText("Deletion reason")).toHaveProperty("value", "Created by mistake");
    expect(dialog.queryByRole("option", {name: "Select a reason"})).toBeNull();
    expect(onTrash).not.toHaveBeenCalled();
    await user.click(dialog.getByRole("button", {name: "Move to recycle bin"}));
    expect(onTrash).toHaveBeenCalledWith("Created by mistake");
  });

  it("expands an optional note only on request and submits the chosen reason with trimmed notes", async () => {
    const {user, onTrash} = setup({...base, action: "trash", conflicts: []});
    expect(screen.queryByLabelText("Additional note (optional)")).toBeNull();
    await user.selectOptions(screen.getByLabelText("Deletion reason"), "Duplicate project");
    await user.click(screen.getByRole("button", {name: "Add note"}));
    const note = screen.getByLabelText("Additional note (optional)");
    expect(document.activeElement).toBe(note);
    await user.type(note, "  Duplicate intake  ");
    await user.click(screen.getByRole("button", {name: "Move to recycle bin"}));
    expect(onTrash).toHaveBeenCalledWith("Duplicate project: Duplicate intake");
  });

  it("allows Other without requiring a note and Cancel never deletes", async () => {
    const {user, onTrash, onCancel} = setup({...base, action: "trash", conflicts: []});
    await user.selectOptions(screen.getByLabelText("Deletion reason"), "Other");
    await user.click(screen.getByRole("button", {name: "Cancel"}));
    expect(onCancel).toHaveBeenCalledOnce();
    expect(onTrash).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", {name: "Move to recycle bin"}));
    expect(onTrash).toHaveBeenCalledWith("Other");
  });

  it("keeps new warnings and stale-preview safeguards visible", async () => {
    const {user, onTrash, onRefresh} = setup({...base, action: "trash", conflicts: [],
      warnings: ["Review the pending project handoff."]}, true);
    expect(screen.getByText("Review the pending project handoff.")).toBeTruthy();
    expect(screen.getByRole("button", {name: "Move to recycle bin"})).toHaveProperty("disabled", true);
    await user.click(screen.getByRole("button", {name: "Refresh preview"}));
    expect(onRefresh).toHaveBeenCalledOnce();
    expect(onTrash).not.toHaveBeenCalled();
  });

  it.each([{busy: true}, {loading: true}])("blocks confirmation while %j", async (state) => {
    const {user, onTrash, onCancel} = setup({...base, action: "trash", conflicts: []}, false, state);
    expect(screen.getByRole("button", {name: state.busy ? "Moving…" : "Move to recycle bin"})).toHaveProperty("disabled", true);
    if (state.busy) {
      expect(screen.getByLabelText("Deletion reason")).toHaveProperty("disabled", true);
      expect(screen.getByRole("button", {name: "Add note"})).toHaveProperty("disabled", true);
      expect(screen.getByRole("button", {name: "Cancel"})).toHaveProperty("disabled", true);
      await user.keyboard("{Escape}");
      expect(onCancel).not.toHaveBeenCalled();
    }
    expect(onTrash).not.toHaveBeenCalled();
  });

  it("focuses the reason rather than the deletion action and cancels with Escape", async () => {
    const {user, onTrash, onCancel} = setup({...base, action: "trash", conflicts: []});
    expect(document.activeElement).toBe(screen.getByLabelText("Deletion reason"));
    await user.keyboard("{Escape}");
    expect(onCancel).toHaveBeenCalledOnce();
    expect(onTrash).not.toHaveBeenCalled();
  });
});
