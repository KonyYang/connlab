import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ProjectLibraryList } from "./ProjectLibraryList";
import * as api from "../../api/projectLibrary";
import { listLegacyProjects } from "../../api/legacyProjects";
vi.mock("../../api/projectLibrary", () => ({ listLibraryMembers: vi.fn(), openLibraryFolder: vi.fn() }));
vi.mock("../../api/legacyProjects", () => ({ listLegacyProjects: vi.fn() }));
beforeEach(() => {
  vi.resetAllMocks(); sessionStorage.clear();
  vi.mocked(listLegacyProjects).mockResolvedValue([]);
  vi.mocked(api.listLibraryMembers).mockResolvedValue({ items: [] });
});
const linked = { record_id: "m1", name: "Old manual folder", number: "DL-2020-01-001", number_evidence: [], folder_path: "D:/old/manual", notes: [], revision: 1, imported_at: "2026-01-01", updated_at: "2026-01-01" };

it("searches and opens both managed and linked projects from one list without losing colliding IDs", async () => {
  vi.mocked(listLegacyProjects).mockResolvedValue([linked]);
  vi.mocked(api.listLibraryMembers).mockResolvedValue({ items: [{ member_id: "m1", project_id: "p1", ltr_number: "DL-2026-09-032", title: "Managed folder", folder_path: "D:/library/managed", revision: 1, batch_id: null, snapshot_status: "missing", snapshot_created_at: null, warnings: [], can_continue: true }] });
  const onOpen = vi.fn(), onOpenLinked = vi.fn(), user = userEvent.setup();
  render(<ProjectLibraryList onOpen={onOpen} onOpenLinked={onOpenLinked} onBack={vi.fn()} onImport={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Open Managed folder" }));
  await user.click(screen.getByRole("button", { name: "Open Old manual folder" }));
  expect(onOpen).toHaveBeenCalledWith("m1");
  expect(onOpenLinked).toHaveBeenCalledWith("m1");
  await user.type(screen.getByLabelText("Search library"), "DL");
  await waitFor(() => expect(listLegacyProjects).toHaveBeenLastCalledWith("DL", expect.any(AbortSignal)));
  expect(api.listLibraryMembers).toHaveBeenLastCalledWith("DL", "", expect.any(AbortSignal));
  expect(screen.queryByRole("button", { name: "Legacy", exact: true })).toBeNull();
});

it("keeps available linked projects visible when managed records fail and supports retry", async () => {
  vi.mocked(api.listLibraryMembers).mockRejectedValueOnce(new Error("Library unavailable"));
  vi.mocked(listLegacyProjects).mockResolvedValue([linked]);
  render(<ProjectLibraryList onOpen={vi.fn()} onOpenLinked={vi.fn()} onBack={vi.fn()} onImport={vi.fn()} />);
  expect(await screen.findByRole("alert")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Open Old manual folder" })).toBeTruthy();
  await userEvent.setup().click(screen.getByRole("button", { name: "Retry" }));
  await waitFor(() => expect(screen.queryByRole("alert")).toBeNull());
});

it("keeps a receiving batch scoped to its own members", async () => {
  vi.mocked(listLegacyProjects).mockResolvedValue([linked]);
  render(<ProjectLibraryList batchId="batch-1" onOpen={vi.fn()} onOpenLinked={vi.fn()} onBack={vi.fn()} onImport={vi.fn()} />);
  await screen.findByText("0 projects");
  expect(listLegacyProjects).not.toHaveBeenCalled();
});

it("opens a new import batch without an old search and restores each list's own view", async () => {
  const props = { onOpen: vi.fn(), onOpenLinked: vi.fn(), onBack: vi.fn(), onImport: vi.fn() };
  vi.mocked(listLegacyProjects).mockResolvedValue(Array.from({ length: 21 }, (_, i) => ({ ...linked, record_id: String(i), name: `Old folder ${i + 1}` })));
  const user = userEvent.setup();
  const view = render(<ProjectLibraryList {...props} />);
  await user.type(screen.getByLabelText("Search library"), "old");
  await user.click(await screen.findByRole("button", { name: "Next" }));
  expect(screen.getByText("Page 2 of 2")).toBeTruthy();
  view.rerender(<ProjectLibraryList {...props} batchId="fresh-batch" />);
  await waitFor(() => expect(screen.getByLabelText("Search library")).toHaveProperty("value", ""));
  expect(api.listLibraryMembers).toHaveBeenLastCalledWith("", "fresh-batch", expect.any(AbortSignal));
  await user.type(screen.getByLabelText("Search library"), "new");
  view.rerender(<ProjectLibraryList {...props} />);
  await screen.findByText("21 projects");
  expect(screen.getByLabelText("Search library")).toHaveProperty("value", "old");
  expect(screen.getByText("Page 2 of 2")).toBeTruthy();
  view.rerender(<ProjectLibraryList {...props} batchId="fresh-batch" />);
  await screen.findByText("0 projects");
  expect(screen.getByLabelText("Search library")).toHaveProperty("value", "new");
});

it("offers clearing an empty search before suggesting another import", async () => {
  render(<ProjectLibraryList onOpen={vi.fn()} onOpenLinked={vi.fn()} onBack={vi.fn()} onImport={vi.fn()} />);
  const user = userEvent.setup();
  await user.type(screen.getByLabelText("Search library"), "not-found");
  await user.click(await screen.findByRole("button", { name: "Clear Search" }));
  expect(screen.getByLabelText("Search library")).toHaveProperty("value", "");
  await waitFor(() => expect(listLegacyProjects).toHaveBeenLastCalledWith("", expect.any(AbortSignal)));
});

it("paginates linked and managed results together and preserves the page after browsing", async () => {
  vi.mocked(listLegacyProjects).mockResolvedValue(Array.from({ length: 21 }, (_, i) => ({ ...linked, record_id: `linked-${i}`, name: `Folder ${i + 1}` })));
  const props = { onOpen: vi.fn(), onOpenLinked: vi.fn(), onBack: vi.fn(), onImport: vi.fn() };
  const view = render(<ProjectLibraryList {...props} />);
  await screen.findByText("21 projects");
  await userEvent.setup().click(screen.getByRole("button", { name: "Next" }));
  expect(screen.getByRole("button", { name: "Open Folder 21" })).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Open Folder 1", exact: true })).toBeNull();
  view.unmount();
  render(<ProjectLibraryList {...props} />);
  expect(await screen.findByRole("button", { name: "Open Folder 21" })).toBeTruthy();
});

it("ignores stale linked results after the shared search changes", async () => {
  let finish!: (rows: typeof linked[]) => void;
  vi.mocked(listLegacyProjects).mockReturnValueOnce(new Promise(resolve => { finish = resolve; }));
  const view = render(<ProjectLibraryList onOpen={vi.fn()} onOpenLinked={vi.fn()} onBack={vi.fn()} onImport={vi.fn()} />);
  await userEvent.setup().type(screen.getByLabelText("Search library"), "new");
  await screen.findByText("0 projects");
  await act(async () => finish([linked]));
  expect(screen.queryByText(linked.name)).toBeNull();
  view.unmount();
});
it("opens project details and retains the shared search for return navigation", async () => {
  const user = userEvent.setup(); const onOpen = vi.fn();
  vi.mocked(api.listLibraryMembers).mockResolvedValue({ items: [{ member_id: "m1", project_id: "p1", ltr_number: "DL-2026-09-032", title: "CPI-450", folder_path: "D:/library/CPI", revision: 1, batch_id: "b1", snapshot_status: "current", snapshot_created_at: "2026-10-27", warnings: [], can_continue: true }] });
  const first = render(<ProjectLibraryList onOpen={onOpen} onOpenLinked={vi.fn()} onBack={vi.fn()} onImport={vi.fn()} />);
  await user.type(screen.getByLabelText("Search library"), "CPI");
  await user.click(screen.getByRole("button", { name: "Open CPI-450" }));
  expect(onOpen).toHaveBeenCalledWith("m1");
  first.unmount();
  render(<ProjectLibraryList onOpen={onOpen} onOpenLinked={vi.fn()} onBack={vi.fn()} onImport={vi.fn()} />);
  await screen.findByRole("button", { name: "Open CPI-450" });
  expect(screen.getByLabelText("Search library")).toHaveProperty("value", "CPI");
});

it("identifies historical copies and opens their browsing details", async () => {
  const user = userEvent.setup(); const onOpen = vi.fn();
  vi.mocked(api.listLibraryMembers).mockResolvedValue({ items: [{ member_id: "history-1", project_id: "old-project", ltr_number: "DL-2026-09-032", title: "Old CPI copy", folder_path: "D:/library/history/CPI", revision: 1, batch_id: null, snapshot_status: "current", snapshot_created_at: "2026-10-27", warnings: [], can_continue: false, is_history: true }] });
  render(<ProjectLibraryList onOpen={onOpen} onOpenLinked={vi.fn()} onBack={vi.fn()} onImport={vi.fn()} />);
  expect(await screen.findByText("Historical Copy")).toBeTruthy();
  expect(screen.queryByText("Managed Project")).toBeNull();
  await user.click(screen.getByRole("button", { name: "Open Old CPI copy" }));
  expect(onOpen).toHaveBeenCalledWith("history-1");
});

it.each([false, true])("shows an unchecked snapshot without implying portability readiness for history=%s", async isHistory => {
  const user = userEvent.setup(); const onOpen = vi.fn();
  vi.mocked(api.listLibraryMembers).mockResolvedValue({ items: [{ member_id: "unchecked-1", project_id: "p1", ltr_number: "DL-2026-09-032", title: "Unchecked CPI", folder_path: "D:/library/CPI", revision: 1, batch_id: null, snapshot_status: "not_checked", snapshot_created_at: "2026-10-27", warnings: [], can_continue: !isHistory, is_history: isHistory }] });
  render(<ProjectLibraryList onOpen={onOpen} onOpenLinked={vi.fn()} onBack={vi.fn()} onImport={vi.fn()} />);
  expect(await screen.findByText("Not Checked")).toBeTruthy();
  expect(screen.queryByText("Ready to Take")).toBeNull();
  expect(screen.getByText(isHistory ? "Historical Copy" : "Managed Project")).toBeTruthy();
  await user.click(screen.getByRole("button", { name: `Open Unchecked CPI` }));
  expect(onOpen).toHaveBeenCalledWith("unchecked-1");
});
