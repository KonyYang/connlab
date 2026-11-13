import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ReferenceLibraryPage } from "./ReferenceLibraryPage";
import * as api from "../api/referenceLibrary";
vi.mock("../api/referenceLibrary", () => ({ searchReferenceLibrary: vi.fn(), openReferenceFile: vi.fn() }));
const project = { key: "project:p1", project_id: "p1", member_id: null, number: "DL-2026-08-079", title: "PwrBlade", test_item: "温升", source: "connlab", available: true, folder_path: "D:/isolated" };
beforeEach(() => {
  sessionStorage.clear(); vi.resetAllMocks();
  vi.mocked(api.searchReferenceLibrary).mockResolvedValue({ projects: [project], files: [], total: 0, warnings: [] });
  vi.mocked(api.openReferenceFile).mockResolvedValue({ status: "opened", message: "File opened." });
});
it("searches files, shows context, opens and refreshes without starting intake", async () => {
  const user = userEvent.setup();
  render(<ReferenceLibraryPage onOpenProject={vi.fn()} onOpenMember={vi.fn()} />);
  await screen.findByText("PwrBlade");
  vi.mocked(api.searchReferenceLibrary).mockResolvedValue({ projects: [project], total: 1, warnings: [], files: [{ key: project.key, title: project.title, number: project.number, name: "温升记录.xlsx", relative_path: "Records/温升记录.xlsx", directory: "Records", kind: "record" }] });
  await act(async () => { await user.type(screen.getByLabelText("Search project materials"), "PwrBlade 温升"); });
  await act(async () => { await user.click(screen.getByRole("button", { name: "Search", exact: true })); });
  await screen.findByRole("button", { name: "温升记录.xlsx" });
  expect(screen.getByText("Records")).toBeTruthy();
  await act(async () => { await user.click(screen.getByRole("button", { name: "温升记录.xlsx" })); });
  expect(api.openReferenceFile).toHaveBeenCalledWith(project.key, "Records/温升记录.xlsx", false);
  await act(async () => { await user.click(screen.getByRole("button", { name: "Refresh" })); });
  await waitFor(() => expect(api.searchReferenceLibrary).toHaveBeenCalledTimes(3));
});
it("filters by material type without keywords and reaches linked location details", async () => {
  const user = userEvent.setup();
  const linked = vi.fn();
  vi.mocked(api.searchReferenceLibrary).mockResolvedValue({ projects: [{ ...project, key: "linked:old", project_id: null, available: false }], files: [], total: 0, warnings: [] });
  render(<ReferenceLibraryPage onOpenProject={vi.fn()} onOpenMember={vi.fn()} onOpenLinked={linked} />);
  const details = await screen.findByRole("button", { name: "Details / Locate folder" });
  await act(async () => { await user.click(details); });
  expect(linked).toHaveBeenCalledWith("old");
  await act(async () => { await user.selectOptions(screen.getByLabelText("Material type"), "report"); });
  expect(await screen.findByText("0 matching files")).toBeTruthy();
  expect(api.searchReferenceLibrary).toHaveBeenLastCalledWith("", "all", "report", "", 0, expect.any(AbortSignal));
});
it("retains missing projects and shows incomplete search and opening failures", async () => {
  vi.mocked(api.searchReferenceLibrary).mockResolvedValue({ projects: [{ ...project, available: false }], files: [], total: 0, warnings: ["Search incomplete: location unavailable"] });
  render(<ReferenceLibraryPage onOpenProject={vi.fn()} onOpenMember={vi.fn()} />);
  await screen.findByText("PwrBlade");
  expect(screen.getByText("Material location unavailable")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Open folder" }).hasAttribute("disabled")).toBe(true);
  expect(screen.getByText("Search incomplete: location unavailable")).toBeTruthy();
});
