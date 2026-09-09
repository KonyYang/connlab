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

function setup(preview = base, stale = false) {
  const onRestore = vi.fn(); const onTrash = vi.fn(); const onCancel = vi.fn(); const onRefresh = vi.fn();
  render(<ProjectRegistryManagementDialog action={preview.action} preview={preview} busy={false} loading={false}
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
    await user.click(dialog.getByRole("button", {name: "Restore as current; retain existing projects in history"}));
    expect(onRestore).toHaveBeenCalledWith("active", true);
  });
  it("can retain the restored record as history without replacing any current project", async () => {
    const {user, onRestore} = setup();
    await user.click(screen.getByRole("button", {name: "Restore to history only"}));
    expect(onRestore).toHaveBeenCalledWith("history", false);
  });
  it("does not mutate on cancel and disables restore until stale evidence has been refreshed", async () => {
    const {user, onRestore, onCancel, onRefresh} = setup(base, true);
    expect(screen.getByRole("button", {name: "Restore to history only"})).toHaveProperty("disabled", true);
    await user.click(screen.getByRole("button", {name: "Refresh preview"}));
    expect(onRefresh).toHaveBeenCalledOnce();
    await user.click(screen.getByRole("button", {name: "Cancel"}));
    expect(onCancel).toHaveBeenCalledOnce(); expect(onRestore).not.toHaveBeenCalled();
  });
  it("shows the deletion boundary and blocks deletion during an active operation", async () => {
    const {onTrash} = setup({...base, action: "trash", conflicts: [], blockers: ["A file generation is running."]});
    expect(screen.getByText(/Public-drive files, original materials and LTR workbook records/)).toBeTruthy();
    expect(screen.getByText("A file generation is running.")).toBeTruthy();
    expect(screen.getByRole("button", {name: "Move to recycle bin"})).toHaveProperty("disabled", true);
    expect(onTrash).not.toHaveBeenCalled();
  });
});
