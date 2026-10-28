import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { listManagedProjects, type ProjectRegistryEntry } from "../../api/projectRegistryManagement";
import { ProjectRegistryManagementPanel } from "./ProjectRegistryManagementPanel";

vi.mock("../../api/projectRegistryManagement", () => ({ listManagedProjects: vi.fn() }));
const deleted: ProjectRegistryEntry = { project_id: "deleted-A", display_project_id: "DL-2026-01-002", sample_description: "Deleted sample", test_item: "LLCR", requestor: "Lab", created_on: "2026-01-01", lifecycle_state: "active", close_reason_label: null, registry_state: "trash", registry_revision: 1, changed_at: "2026-01-02", reason: "Created by mistake" };
const retained: ProjectRegistryEntry = { ...deleted, project_id: "retained-B", sample_description: "Retained sample", registry_state: "history", reason: "Retained while restoring another project." };
const props = () => ({ search: "", revision: 0, onManage: vi.fn(), onOpenProject: vi.fn() });
beforeEach(() => { vi.resetAllMocks(); });

it("keeps available records on a partial failure and adds the missing source on Retry", async () => {
  let failed = true;
  vi.mocked(listManagedProjects).mockImplementation(async location => {
    if (location === "trash") return [deleted];
    if (failed) throw new Error("Unavailable");
    return [retained];
  });
  render(<ProjectRegistryManagementPanel {...props()} />);
  expect(await screen.findByText("Deleted sample")).toBeTruthy();
  expect(screen.getByRole("alert")).toBeTruthy();
  expect(screen.queryByText("No projects in this view.")).toBeNull();
  failed = false;
  await userEvent.setup().click(screen.getByRole("button", { name: "Retry" }));
  expect(await screen.findByText("Retained sample")).toBeTruthy();
  expect(screen.getAllByRole("article")).toHaveLength(2);
  expect(screen.queryByRole("alert")).toBeNull();
});

it("keeps same-number identities independent and searches their retention reasons", async () => {
  vi.mocked(listManagedProjects).mockImplementation(async location => location === "trash" ? [deleted] : [retained]);
  const callbacks = props(), user = userEvent.setup();
  const { rerender } = render(<ProjectRegistryManagementPanel {...callbacks} />);
  await screen.findByText("Retained sample");
  expect(screen.getAllByRole("article")).toHaveLength(2);
  rerender(<ProjectRegistryManagementPanel {...callbacks} search="retained after conflict" />);
  expect(screen.queryByText("Deleted sample")).toBeNull();
  const row = screen.getByRole("article");
  await user.click(within(row).getByRole("button", { name: "View read-only details" }));
  await user.click(within(row).getByRole("button", { name: "Restore", exact: true }));
  expect(callbacks.onOpenProject).toHaveBeenCalledWith("retained-B");
  expect(callbacks.onManage).toHaveBeenCalledWith("retained-B", "restore");
  rerender(<ProjectRegistryManagementPanel {...callbacks} search="Created by mistake" />);
  expect(screen.getByText("Deleted sample")).toBeTruthy();
  expect(screen.queryByText("Retained sample")).toBeNull();
});

it("shows the latest revision once if a record moves between the two reads", async () => {
  vi.mocked(listManagedProjects).mockImplementation(async location => location === "trash" ? [deleted] : [{ ...deleted, registry_state: "history", registry_revision: 2 }]);
  render(<ProjectRegistryManagementPanel {...props()} />);
  expect(await screen.findByText("Retained after conflict")).toBeTruthy();
  expect(screen.getAllByRole("article")).toHaveLength(1);
  expect(screen.queryByText("Deleted", { exact: true })).toBeNull();
});

it("ignores an old response after a restore has refreshed the list", async () => {
  let resolveOld!: (value: ProjectRegistryEntry[]) => void;
  vi.mocked(listManagedProjects).mockReturnValueOnce(new Promise(resolve => { resolveOld = resolve; })).mockResolvedValueOnce([]).mockResolvedValue([]);
  const callbacks = props(), { rerender } = render(<ProjectRegistryManagementPanel {...callbacks} />);
  rerender(<ProjectRegistryManagementPanel {...callbacks} revision={1} />);
  await screen.findByText("No projects in this view.");
  await act(async () => resolveOld([deleted]));
  expect(screen.queryByText("Deleted sample")).toBeNull();
});
