import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ProjectLibraryImport } from "./ProjectLibraryImport";
import * as api from "../../api/projectLibrary";

vi.mock("../../api/projectLibrary", () => ({
  getLibraryRuntime: vi.fn(), getLibraryMember: vi.fn(), scanLibrarySources: vi.fn(), planLibraryIntake: vi.fn(),
  startLibraryBatch: vi.fn(), getLibraryBatch: vi.fn(), resumeLibraryBatch: vi.fn(), pickLibraryFolder: vi.fn(),
  inspectPortableProject: vi.fn(), planPortableRestore: vi.fn(), restorePortableProject: vi.fn(), listLibraryMembers: vi.fn(),
}));
const path = "D:/old/DL-2026-09-032 Connector";
const candidate = { source_path: path, title: "Connector", ltr_number: "DL-2026-09-032", kind: "project" as const, warnings: [], child_folders: [] };
const item = { ...candidate, target_path: "D:/managed/DL-2026-09-032", status: "ready" as const, can_keep_separate: false };
beforeEach(() => {
  vi.resetAllMocks(); localStorage.clear();
  vi.mocked(api.getLibraryRuntime).mockResolvedValue({ library_root: "D:/managed", projects_root: "D:/managed/Projects", data_root: "D:/managed/Data", database_path: "D:/managed/Data/test.sqlite3", configured: true, format_version: 1 });
  vi.mocked(api.pickLibraryFolder).mockResolvedValue(path);
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [candidate], warnings: [], truncated: false });
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ plan_id: "plan", fingerprint: "verified", items: [item], warnings: [] });
  vi.mocked(api.startLibraryBatch).mockResolvedValue({ batch_id: "batch", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: path, status: "added", message: "Added", member_id: "member" }] });
  vi.mocked(api.getLibraryMember).mockResolvedValue({ member_id: "member", project_id: "verified-project", ltr_number: candidate.ltr_number, title: candidate.title, folder_path: item.target_path, revision: 1, batch_id: "batch", snapshot_status: "missing", snapshot_created_at: null, warnings: [], can_continue: true });
});

it("automatically receives one safe folder and opens its verified workspace", async () => {
  const user = userEvent.setup(), open = vi.fn();
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={open} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  await waitFor(() => expect(open).toHaveBeenCalledWith("verified-project"));
  expect(api.scanLibrarySources).toHaveBeenCalledWith([path], expect.any(AbortSignal), true);
  expect(api.startLibraryBatch).toHaveBeenCalledExactlyOnceWith(expect.objectContaining({ selected: [path], plan_id: "plan", fingerprint: "verified" }));
  expect(screen.queryByRole("checkbox")).toBeNull();
  expect(screen.queryByRole("button", { name: "Add Folder" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Find Projects Inside" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Confirm Import", exact: true })).toBeNull();
});

it("requires one explicit confirmation before adopting an authoritative existing LTR", async () => {
  const user = userEvent.setup();
  vi.mocked(api.planLibraryIntake).mockResolvedValue({
    plan_id: "authority-plan", fingerprint: "authority-fingerprint", warnings: [],
    items: [{
      ...item,
      authority_status: "found",
      authority_message: "The LTR exists in the authoritative workbook.",
    }],
  });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={vi.fn()} />);

  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  expect(await screen.findByRole("button", { name: "Confirm Import", exact: true })).toBeTruthy();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();

  await user.click(screen.getByRole("button", { name: "Confirm Import", exact: true }));
  await waitFor(() => expect(api.startLibraryBatch).toHaveBeenCalledOnce());
});

it("asks for the actual project when an upper folder is selected and creates no import review", async () => {
  const user = userEvent.setup();
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [], warnings: ["Choose the one project you want to import."], truncated: false, selection_issue: "choose_project" } as api.LibraryScan);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  expect(await screen.findByText("Choose the one project you want to import.")).toBeTruthy();
  expect(api.planLibraryIntake).not.toHaveBeenCalled();
  expect(screen.queryByRole("button", { name: "Confirm Import" })).toBeNull();
});

it("requests a missing LTR only when needed and then completes the same automatic intake", async () => {
  const user = userEvent.setup(), open = vi.fn();
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [{ ...candidate, ltr_number: null }], warnings: [], truncated: false, selection_issue: "needs_ltr" } as api.LibraryScan);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={open} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  const number = await screen.findByRole("textbox", { name: "LTR number" });
  expect(api.planLibraryIntake).not.toHaveBeenCalled();
  expect(screen.getByRole("button", { name: "Check Project" })).toHaveProperty("disabled", true);
  await user.type(number, "DL-2026-09-032");
  await user.click(screen.getByRole("button", { name: "Check Project" }));
  await waitFor(() => expect(open).toHaveBeenCalledWith("verified-project"));
  expect(api.planLibraryIntake).toHaveBeenLastCalledWith([path], expect.any(AbortSignal), [{ source_path: path, ltr_number: "DL-2026-09-032" }]);
  expect(api.startLibraryBatch).toHaveBeenCalledOnce();
  expect(screen.queryByRole("button", { name: "Confirm Import" })).toBeNull();
});

it("replaces the reviewed source rather than accumulating a batch", async () => {
  const user = userEvent.setup(), next = "D:/old/DL-2026-09-033 Another project";
  vi.mocked(api.pickLibraryFolder).mockResolvedValueOnce(path).mockResolvedValue(next);
  vi.mocked(api.scanLibrarySources).mockImplementation(async roots => ({ items: [{ ...candidate, source_path: roots[0] }], warnings: [], truncated: false }));
  vi.mocked(api.planLibraryIntake).mockImplementation(async sources => ({ plan_id: "checked", fingerprint: "verified", items: [{ ...item, source_path: sources[0] }], warnings: [] }));
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  await user.click(await screen.findByRole("button", { name: "Change Folder" }));
  await screen.findByRole("button", { name: "Confirm Import" });
  expect(api.scanLibrarySources).toHaveBeenLastCalledWith([next], expect.any(AbortSignal), true);
  await user.click(screen.getByRole("button", { name: "Confirm Import" }));
  await waitFor(() => expect(api.startLibraryBatch).toHaveBeenCalledWith(expect.objectContaining({ selected: [next] })));
});

it("does not expose a batch when a stale or incompatible scanner expands the selection", async () => {
  const user = userEvent.setup();
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [candidate, { ...candidate, source_path: "D:/other" }], warnings: [], truncated: false });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  expect(await screen.findByRole("alert")).toHaveProperty("textContent", "Choose one complete project folder at a time.");
  expect(api.planLibraryIntake).not.toHaveBeenCalled();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it("opens an already received project without creating another batch", async () => {
  const user = userEvent.setup(), open = vi.fn();
  vi.mocked(api.planLibraryIntake).mockResolvedValue({
    plan_id: "duplicate-plan", fingerprint: "duplicate-fingerprint", warnings: [],
    items: [{ ...item, status: "already_added", existing_member_id: "existing-member" }],
  });
  vi.mocked(api.getLibraryMember).mockResolvedValue({
    member_id: "existing-member", project_id: "existing-project", ltr_number: candidate.ltr_number,
    title: candidate.title, folder_path: item.target_path, revision: 2, batch_id: "older-batch",
    snapshot_status: "missing", snapshot_created_at: null, warnings: [], can_continue: true,
  });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={open} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  await waitFor(() => expect(open).toHaveBeenCalledExactlyOnceWith("existing-project"));
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  expect(screen.queryByRole("button", { name: "Confirm Import" })).toBeNull();
});

it("restores trusted saved data and opens the project while retaining non-blocking warnings", async () => {
  const user = userEvent.setup(), open = vi.fn();
  const saved: api.PortableRestorePlan = {
    plan_id: "saved-plan", fingerprint: "saved-fingerprint", project_id: "saved-project",
    ltr_number: candidate.ltr_number, title: candidate.title, source_path: path, target_path: item.target_path,
    resolution_options: [], resolution: null, source_signature: "source-signature", target_revision: null,
    backup_path: null, status: "ready", created_at: "2026-11-01T00:00:00Z", record_counts: { matrices: 1 },
    file_count: 8, warnings: ["One original source file is unavailable."], blockers: [],
  };
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [{ ...candidate, has_portable: true }], warnings: [], truncated: false });
  vi.mocked(api.inspectPortableProject).mockResolvedValue(saved);
  vi.mocked(api.restorePortableProject).mockResolvedValue({
    status: "restored", warnings: saved.warnings,
    member: { member_id: "saved-member", project_id: "saved-project", ltr_number: candidate.ltr_number,
      title: candidate.title, folder_path: item.target_path, revision: 1, batch_id: "saved-batch",
      snapshot_status: "current", snapshot_created_at: saved.created_at, warnings: saved.warnings, can_continue: true },
  });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={open} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  await waitFor(() => expect(open).toHaveBeenCalledExactlyOnceWith("saved-project"));
  expect(api.restorePortableProject).toHaveBeenCalledExactlyOnceWith({ plan_id: "saved-plan", fingerprint: "saved-fingerprint" });
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});


it("shows the blocking LTR reason before details and offers recovery without importing", async () => {
  const user = userEvent.setup(), settings = vi.fn();
  const reason = `${candidate.ltr_number} was not found in the configured LTR workbook.`;
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ plan_id: "blocked", fingerprint: "blocked", warnings: [],
    items: [{ ...item, status: "unavailable", warnings: [reason, reason] }] });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={vi.fn()} onOpenSettings={settings} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  expect(await screen.findByText("Not imported")).toBeTruthy();
  expect(screen.getAllByText(reason)).toHaveLength(1);
  expect(screen.getByText(reason).closest("details")).toBeNull();
  expect(screen.getByText("Planned save location")).toBeTruthy();
  expect(screen.queryByText("Save location", { exact: true })).toBeNull();
  expect(screen.queryByRole("button", { name: "Confirm Import" })).toBeNull();
  await user.click(screen.getByRole("button", { name: "Open Settings" }));
  expect(settings).toHaveBeenCalledOnce();
  await user.click(screen.getByRole("button", { name: "Check and Continue" }));
  expect(await screen.findByText("Not imported")).toBeTruthy();
  expect(api.planLibraryIntake).toHaveBeenCalledTimes(2);
  expect(api.pickLibraryFolder).toHaveBeenCalledOnce();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  expect(api.restorePortableProject).not.toHaveBeenCalled();
  expect(screen.getByRole("button", { name: "Change Folder" })).toBeTruthy();
  let finishPicker!: (value: string | null) => void;
  vi.mocked(api.pickLibraryFolder).mockImplementationOnce(() => new Promise(resolve => { finishPicker = resolve; }));
  await user.click(screen.getByRole("button", { name: "Change Folder" }));
  expect(screen.getByRole("button", { name: "Open Settings" })).toHaveProperty("disabled", true);
  expect(screen.getByRole("button", { name: "Check and Continue" })).toHaveProperty("disabled", true);
  await act(async () => finishPicker(null));
  expect(screen.getByRole("button", { name: "Check and Continue" })).toHaveProperty("disabled", false);
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it("rechecks a blocked project and still requires confirmation after LTR authority succeeds", async () => {
  const user = userEvent.setup();
  vi.mocked(api.planLibraryIntake).mockResolvedValueOnce({ plan_id: "blocked", fingerprint: "blocked", warnings: [],
    items: [{ ...item, status: "unavailable", warnings: ["LTR verification is unavailable."] }] });
  let finishCheck!: (value: api.LibraryIntakePlan) => void;
  vi.mocked(api.planLibraryIntake).mockImplementationOnce(() => new Promise(resolve => { finishCheck = resolve; }));
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={vi.fn()} onOpenSettings={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  await user.click(await screen.findByRole("button", { name: "Check and Continue" }));
  await waitFor(() => expect(api.planLibraryIntake).toHaveBeenCalledTimes(2));
  expect(screen.getByRole("button", { name: "Choose Project Folder" })).toHaveProperty("disabled", true);
  expect(screen.getByRole("button", { name: "Back to Projects" })).toHaveProperty("disabled", true);
  expect(screen.queryByRole("button", { name: "Check and Continue" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Open Settings" })).toBeNull();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  await act(async () => finishCheck({ plan_id: "authority-plan", fingerprint: "authority-verified", warnings: [],
    items: [{ ...item, authority_status: "found" }] }));
  expect(await screen.findByRole("button", { name: "Confirm Import" })).toBeTruthy();
  expect(screen.queryByText("Not imported")).toBeNull();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "Confirm Import" }));
  await waitFor(() => expect(api.startLibraryBatch).toHaveBeenCalledExactlyOnceWith(expect.objectContaining({
    plan_id: "authority-plan", fingerprint: "authority-verified", selected: [path],
  })));
});

it("provides a useful unavailable fallback when the check returns no reason", async () => {
  const user = userEvent.setup();
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ plan_id: "blocked", fingerprint: "blocked", warnings: [],
    items: [{ ...item, ltr_number: null, status: "unavailable", warnings: [] }] });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  expect(await screen.findByText("Not imported")).toBeTruthy();
  expect(screen.getByRole("alert").textContent).toContain("The project check did not complete.");
  expect(screen.getByText("Resolve the problem above, then check this project again or choose a different folder.")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Check and Continue" })).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Open Settings" })).toBeNull();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});


it("labels an already imported project's existing location without presenting a planned import", async () => {
  const user = userEvent.setup();
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ plan_id: "existing", fingerprint: "existing", warnings: [],
    items: [{ ...item, status: "already_added", existing_member_id: "member" }] });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  expect(await screen.findByText("Existing location")).toBeTruthy();
  expect(screen.queryByText("Planned save location")).toBeNull();
  expect(screen.queryByText("Not imported")).toBeNull();
  expect(screen.getByRole("button", { name: "Open Existing Connector" })).toBeTruthy();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it.each(["incomplete", "upgrade_required"])("keeps %s recovery guidance beside visible unavailable reasons", async sourceState => {
  const user = userEvent.setup(), reason = "The selected project data cannot be used yet.";
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ plan_id: "blocked", fingerprint: "blocked", warnings: [],
    items: [{ ...item, source_state: sourceState, status: "unavailable", warnings: [reason] }] });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  expect(await screen.findByText("Not imported")).toBeTruthy();
  expect(screen.getByText(reason).closest("details")).toBeNull();
  if (sourceState === "incomplete") expect(screen.getByRole("button", { name: "Import Files Only" })).toBeTruthy();
  else expect(screen.getByText("Update ConnLab before importing this project.")).toBeTruthy();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});
