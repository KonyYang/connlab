import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ProjectLibraryList } from "./ProjectLibraryList";
import * as api from "../../api/projectLibrary";
vi.mock("../../api/projectLibrary", () => ({ listLibraryMembers: vi.fn(), openLibraryFolder: vi.fn() }));
beforeEach(() => { vi.resetAllMocks(); sessionStorage.clear(); });
it("searches library records, opens original files directly, and retains the search for return navigation", async () => {
  const user = userEvent.setup(); const onOpen = vi.fn();
  vi.mocked(api.listLibraryMembers).mockResolvedValue({ items: [{ member_id: "m1", project_id: "p1", ltr_number: "DL-2026-09-032", title: "CPI-450", folder_path: "D:/library/CPI", revision: 1, batch_id: "b1", snapshot_status: "current", snapshot_created_at: "2026-10-27", warnings: [], can_continue: true }] });
  vi.mocked(api.openLibraryFolder).mockResolvedValue({ status: "opened", message: "Folder opened." });
  const first = render(<ProjectLibraryList onOpen={onOpen} onBack={vi.fn()} onImport={vi.fn()} />);
  await user.type(screen.getByLabelText("Search library"), "CPI");
  await user.click(await screen.findByRole("button", { name: "Open Folder CPI-450" }));
  expect(await screen.findByText("Folder opened.")).toBeTruthy();
  await user.click(screen.getByRole("button", { name: "Manage CPI-450" }));
  expect(onOpen).toHaveBeenCalledWith("m1");
  first.unmount();
  render(<ProjectLibraryList onOpen={onOpen} onBack={vi.fn()} onImport={vi.fn()} />);
  await screen.findByRole("button", { name: "Manage CPI-450" });
  expect(screen.getByLabelText("Search library")).toHaveProperty("value", "CPI");
});

it("identifies historical copies and opens their browsing details", async () => {
  const user = userEvent.setup(); const onOpen = vi.fn();
  vi.mocked(api.listLibraryMembers).mockResolvedValue({ items: [{ member_id: "history-1", project_id: "old-project", ltr_number: "DL-2026-09-032", title: "Old CPI copy", folder_path: "D:/library/history/CPI", revision: 1, batch_id: null, snapshot_status: "current", snapshot_created_at: "2026-10-27", warnings: [], can_continue: false, is_history: true }] });
  render(<ProjectLibraryList onOpen={onOpen} onBack={vi.fn()} onImport={vi.fn()} />);
  expect(await screen.findByText("Historical Copy")).toBeTruthy();
  expect(screen.queryByText("Managed Project")).toBeNull();
  await user.click(screen.getByRole("button", { name: "Browse History Old CPI copy" }));
  expect(onOpen).toHaveBeenCalledWith("history-1");
});

it.each([false, true])("shows an unchecked snapshot without implying portability readiness for history=%s", async isHistory => {
  const user = userEvent.setup(); const onOpen = vi.fn();
  vi.mocked(api.listLibraryMembers).mockResolvedValue({ items: [{ member_id: "unchecked-1", project_id: "p1", ltr_number: "DL-2026-09-032", title: "Unchecked CPI", folder_path: "D:/library/CPI", revision: 1, batch_id: null, snapshot_status: "not_checked", snapshot_created_at: "2026-10-27", warnings: [], can_continue: !isHistory, is_history: isHistory }] });
  render(<ProjectLibraryList onOpen={onOpen} onBack={vi.fn()} onImport={vi.fn()} />);
  expect(await screen.findByText("Not Checked")).toBeTruthy();
  expect(screen.queryByText("Ready to Take")).toBeNull();
  expect(screen.getByText(isHistory ? "Historical Copy" : "Managed Project")).toBeTruthy();
  await user.click(screen.getByRole("button", { name: `${isHistory ? "Browse History" : "Manage"} Unchecked CPI` }));
  expect(onOpen).toHaveBeenCalledWith("unchecked-1");
});
