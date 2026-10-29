import { act, render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProjectLibraryImport } from "./ProjectLibraryImport";
import * as api from "../../api/projectLibrary";

vi.mock("../../api/projectLibrary", () => ({
  getLibraryRuntime: vi.fn(), scanLibrarySources: vi.fn(), planLibraryIntake: vi.fn(), listLibraryMembers: vi.fn(),
  startLibraryBatch: vi.fn(), getLibraryBatch: vi.fn(), resumeLibraryBatch: vi.fn(),
  pickLibraryFolder: vi.fn(), inspectPortableProject: vi.fn(), planPortableRestore: vi.fn(), restorePortableProject: vi.fn(),
  saveLibraryDestination: vi.fn(), openLibraryDestination: vi.fn(), pickLibraryDestination: vi.fn(),
}));
const plan = {
  plan_id: "plan-1", fingerprint: "verified", warnings: [], items: [
    { source_path: "D:/old/Force", target_path: "D:/managed/Force", title: "Force test", ltr_number: "DL-2021-01-030A1", status: "ready", warnings: [], can_keep_separate: false },
    { source_path: "D:/old/Cable", target_path: "D:/managed/Cable", title: "Cable test", ltr_number: "DL-2026-07-013A", status: "conflict", warnings: ["Another project uses this LTR."], can_keep_separate: true },
  ],
};

async function enterSources(user: ReturnType<typeof userEvent.setup>, value: string) {
  const editor = await screen.findByLabelText("Source paths");
  const section = editor.closest("details");
  if (section && !section.open) await user.click(screen.getByText("Advanced"));
  await user.type(editor, value);
}

beforeEach(() => {
  vi.resetAllMocks();
  localStorage.clear();
  vi.mocked(api.getLibraryRuntime).mockResolvedValue({ library_root: "D:/managed", projects_root: "D:/managed/projects", data_root: "D:/managed/data", database_path: "D:/managed/data/connlab.sqlite3", configured: true, format_version: 1 });
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: plan.items.map(row => ({ source_path: row.source_path, title: row.title, ltr_number: row.ltr_number, kind: "project", warnings: [], child_folders: [] })), warnings: [], truncated: false });
  vi.mocked(api.planLibraryIntake).mockResolvedValue(plan as api.LibraryIntakePlan);
  vi.mocked(api.startLibraryBatch).mockResolvedValue({ batch_id: "batch-1", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "added", message: "Added", member_id: "member-1" }] });
});

it("checks selected folders automatically and copies nothing before the final confirmation", async () => {
  const user = userEvent.setup();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old");
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: /^Choose (Project Folders|Folder)$/ }));
  await screen.findByRole("table", { name: "Projects to receive" });
  expect(api.scanLibrarySources).toHaveBeenCalledWith(["D:/old"], expect.any(AbortSignal));
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: /^Import Projects \(\d+\)$/ }));
  const confirmation = screen.getByRole("dialog", { name: "Confirm Import" });
  expect(confirmation.textContent).toContain("D:/managed/projects");
  expect(document.activeElement).toBe(within(confirmation).getByRole("heading", { name: "Confirm Import" }));
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  await user.click(within(confirmation).getByRole("button", { name: "Cancel" }));
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it("uses the server-reviewed location in confirmation when Settings changed after the page loaded", async () => {
  const user = userEvent.setup();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old");
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, projects_root: "D:/Current Save Location", items: [{ ...plan.items[0], target_path: "D:/Current Save Location/Force" }] } as api.LibraryIntakePlan);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folders" }));
  await user.click(await screen.findByRole("button", { name: "Import Projects (1)" }));
  const confirmation = screen.getByRole("dialog", { name: "Confirm Import" });
  expect(confirmation.textContent).toContain("D:/Current Save Location");
  expect(confirmation.textContent).not.toContain("D:/managed/projects");
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

const savedProject: api.PortableRestorePlan = {
  plan_id: "portable-plan", fingerprint: "snapshot-fingerprint", project_id: "saved-project",
  ltr_number: "DL-2026-07-006", title: "Snapshot project", source_path: "D:/snapshot", target_path: "D:/managed/projects/Snapshot project",
  resolution_options: [], resolution: null, source_signature: "source-version", target_revision: null, backup_path: null,
  status: "ready", created_at: "2026-10-29T10:00:00Z", record_counts: { confirmed_matrix_versions: 2, result_dataset_revisions: 6 },
  file_count: 7, warnings: ["One original source file is unavailable."], blockers: [],
};
const savedResult: api.PortableRestoreResult = { status: "restored", warnings: savedProject.warnings, member: {
  member_id: "saved-member", project_id: "saved-project", ltr_number: savedProject.ltr_number, title: savedProject.title,
  folder_path: savedProject.target_path, revision: 1, batch_id: "restore-batch", snapshot_status: "current", snapshot_created_at: savedProject.created_at,
  warnings: savedProject.warnings, can_continue: true,
} };

it("offers first-use location setup before allowing any source checks", async () => {
  const user = userEvent.setup();
  const runtime: api.LibraryRuntime = { library_root: "D:/app", projects_root: "D:/unused-default", data_root: "D:/app/Data", database_path: "D:/app/Data/connlab.sqlite3", configured: false, format_version: 1 };
  vi.mocked(api.getLibraryRuntime).mockResolvedValue(runtime);
  vi.mocked(api.saveLibraryDestination).mockResolvedValue({ ...runtime, configured: true, projects_root: "D:/Projects Dev" });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  const input = await screen.findByLabelText("Save imported projects to");
  expect(screen.queryByText("D:/unused-default")).toBeNull();
  expect(screen.queryByRole("button", { name: "Choose Project Folders" })).toBeNull();
  await user.type(input, "D:/Projects Dev");
  expect(api.saveLibraryDestination).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "Use This Location" }));
  expect(await screen.findByRole("button", { name: "Choose Project Folders" })).toBeTruthy();
  expect(screen.getByText("D:/Projects Dev")).toBeTruthy();
  expect(api.scanLibrarySources).not.toHaveBeenCalled();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it("can retry a failed initial setup load without reloading or writing project data", async () => {
  const user = userEvent.setup();
  vi.mocked(api.getLibraryRuntime).mockRejectedValueOnce(new Error("Request failed with 500"));
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Retry Setup" }));
  expect(await screen.findByRole("button", { name: "Choose Project Folders" })).toBeTruthy();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  expect(api.scanLibrarySources).not.toHaveBeenCalled();
});

it("blocks mixed overlapping boundaries even when another folder sorts between their names", async () => {
  const user = userEvent.setup();
  const root = { ...savedProject, source_path: "D:/a" };
  const ordinary = [{ ...plan.items[0], source_path: "D:/a/sub", ltr_number: "DL-2026-10-001" }, { ...plan.items[0], source_path: "D:/a-foo", ltr_number: "DL-2026-10-002" }];
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/selection");
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [
    ...ordinary.map(row => ({ source_path: row.source_path, title: row.title, ltr_number: row.ltr_number, kind: "project" as const, warnings: [], child_folders: [] })),
    { source_path: root.source_path, title: root.title, ltr_number: root.ltr_number, kind: "project", warnings: [], child_folders: [], has_portable: true },
  ], warnings: [], truncated: false });
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: ordinary } as api.LibraryIntakePlan);
  vi.mocked(api.inspectPortableProject).mockResolvedValue(root);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folders" }));
  expect(await screen.findByRole("button", { name: "Import Projects (3)" })).toHaveProperty("disabled", true);
  expect(screen.getByRole("alert").textContent).toContain("contain one another");
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  expect(api.restorePortableProject).not.toHaveBeenCalled();
});

it("requires a fresh backend conflict review before selecting a saved project for retention", async () => {
  const user = userEvent.setup();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/snapshot");
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [{ source_path: "D:/snapshot", title: savedProject.title, ltr_number: savedProject.ltr_number, kind: "project", warnings: [], child_folders: [], has_portable: true }], warnings: [], truncated: false });
  vi.mocked(api.inspectPortableProject).mockResolvedValue({ ...savedProject, status: "conflict", resolution_options: ["keep_as_history"] });
  vi.mocked(api.planPortableRestore).mockResolvedValue({ ...savedProject, resolution: "keep_as_history", fingerprint: "retention-review" });
  vi.mocked(api.restorePortableProject).mockResolvedValue({ ...savedResult, status: "history_kept", member: { ...savedResult.member, is_history: true, can_continue: false } });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folders" }));
  await user.click(await screen.findByRole("radio", { name: "Keep as History" }));
  expect(api.planPortableRestore).toHaveBeenCalledWith("D:/snapshot", "keep_as_history", expect.any(AbortSignal));
  await user.click(await screen.findByRole("button", { name: "Import Projects (1)" }));
  expect(screen.getByRole("dialog", { name: "Confirm Import" }).textContent).toContain("current LTR owner stays unchanged");
  expect(api.restorePortableProject).not.toHaveBeenCalled();
  await user.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Confirm Import" }));
  await screen.findByRole("button", { name: "Open Snapshot project" });
  expect(api.restorePortableProject).toHaveBeenCalledWith({ plan_id: "portable-plan", fingerprint: "retention-review", resolution: "keep_as_history" });
});

it("recognizes saved test data from the ordinary chooser and restores only after explicit confirmation", async () => {
  const user = userEvent.setup();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/snapshot");
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [{ source_path: "D:/snapshot", title: "Snapshot project", ltr_number: savedProject.ltr_number, kind: "project", warnings: [], child_folders: [], has_portable: true }], warnings: [], truncated: false });
  vi.mocked(api.inspectPortableProject).mockResolvedValue(savedProject);
  vi.mocked(api.restorePortableProject).mockResolvedValue(savedResult);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folders" }));
  await waitFor(() => expect(api.inspectPortableProject).toHaveBeenCalledWith("D:/snapshot", expect.any(AbortSignal)));
  expect(api.planLibraryIntake).not.toHaveBeenCalled();
  expect(api.restorePortableProject).not.toHaveBeenCalled();
  await user.click(await screen.findByRole("button", { name: "Import Projects (1)" }));
  const confirmation = screen.getByRole("dialog", { name: "Confirm Import" });
  expect(confirmation.textContent).toContain("saved test data");
  expect(confirmation.textContent).toContain("One original source file is unavailable.");
  expect(api.restorePortableProject).not.toHaveBeenCalled();
  await user.click(within(confirmation).getByRole("button", { name: "Confirm Import" }));
  await screen.findByRole("button", { name: "Open Snapshot project" });
  expect(api.restorePortableProject).toHaveBeenCalledWith({ plan_id: "portable-plan", fingerprint: "snapshot-fingerprint" });
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it("imports a mixed selection through one confirmation without sending snapshots to file-only intake", async () => {
  const user = userEvent.setup();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/mixed");
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [
    { source_path: "D:/old/Force", title: "Force test", ltr_number: plan.items[0].ltr_number, kind: "project", warnings: [], child_folders: [] },
    { source_path: "D:/snapshot", title: savedProject.title, ltr_number: savedProject.ltr_number, kind: "project", warnings: [], child_folders: [], has_portable: true },
  ], warnings: [], truncated: false });
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: [plan.items[0]] } as api.LibraryIntakePlan);
  vi.mocked(api.inspectPortableProject).mockResolvedValue(savedProject);
  vi.mocked(api.restorePortableProject).mockResolvedValue(savedResult);
  const onView = vi.fn();
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={onView} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folders" }));
  await user.click(await screen.findByRole("button", { name: "Import Projects (2)" }));
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  expect(api.restorePortableProject).not.toHaveBeenCalled();
  await user.click(within(screen.getByRole("dialog", { name: "Confirm Import" })).getByRole("button", { name: "Confirm Import" }));
  await screen.findByRole("button", { name: "Open Snapshot project" });
  expect(screen.getByRole("button", { name: "Open Force test" })).toBeTruthy();
  expect(api.planLibraryIntake).toHaveBeenCalledWith(["D:/old/Force"], expect.any(AbortSignal));
  expect(api.startLibraryBatch).toHaveBeenCalledWith(expect.objectContaining({ selected: ["D:/old/Force"] }));
  await user.click(screen.getByRole("button", { name: "View Imported Projects" }));
  expect(onView).toHaveBeenCalledWith();
});

it("rechecks only a failed saved project and never repeats successful file intake", async () => {
  const user = userEvent.setup();
  const ordinary = { source_path: "D:/old/Force", title: "Force test", ltr_number: plan.items[0].ltr_number, kind: "project" as const, warnings: [], child_folders: [] };
  const snapshot = { source_path: "D:/snapshot", title: savedProject.title, ltr_number: savedProject.ltr_number, kind: "project" as const, warnings: [], child_folders: [], has_portable: true };
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/mixed");
  vi.mocked(api.scanLibrarySources).mockResolvedValueOnce({ items: [ordinary, snapshot], warnings: [], truncated: false }).mockResolvedValue({ items: [snapshot], warnings: [], truncated: false });
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: [plan.items[0]] } as api.LibraryIntakePlan);
  vi.mocked(api.inspectPortableProject).mockResolvedValueOnce(savedProject).mockResolvedValue({ ...savedProject, fingerprint: "fresh-retry-review" });
  vi.mocked(api.restorePortableProject).mockRejectedValueOnce(new Error("The source became unavailable.")).mockResolvedValue(savedResult);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Choose Project Folders" }));
  await user.click(await screen.findByRole("button", { name: "Import Projects (2)" }));
  await user.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Confirm Import" }));
  expect(await screen.findByRole("button", { name: "Open Force test" })).toBeTruthy();
  expect(screen.getByText("The source became unavailable.")).toBeTruthy();
  await user.click(screen.getByRole("button", { name: "Check Failed Projects Again" }));
  await user.click(await screen.findByRole("button", { name: "Import Projects (1)" }));
  expect(api.restorePortableProject).toHaveBeenCalledTimes(1);
  await user.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Confirm Import" }));
  await screen.findByRole("button", { name: "Open Snapshot project" });
  expect(api.startLibraryBatch).toHaveBeenCalledTimes(1);
  expect(api.restorePortableProject).toHaveBeenLastCalledWith({ plan_id: "portable-plan", fingerprint: "fresh-retry-review" });
});

describe("ProjectLibraryImport", () => {
  it("shows fresh completion directly and clears the old sources when receiving more projects", async () => {
    const user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    await user.click(screen.getByRole("button", { name: /^Import Projects \(\d+\)$/ }));
    await user.click(screen.getByRole("button", { name: "Confirm Import" }));
    await screen.findByRole("button", { name: "Open Force test" });
    expect(screen.queryByText(/^Last Import/)).toBeNull();
    expect(screen.queryByRole("button", { name: "Choose Project Folders", exact: true })).toBeNull();
    expect(screen.queryByText("Advanced")).toBeNull();
    expect(screen.getByRole("button", { name: "View Imported Projects" })).toHaveProperty("disabled", false);
    await user.click(screen.getByRole("button", { name: "Import More" }));
    expect(screen.getByLabelText("Source paths")).toHaveProperty("value", "");
    expect(screen.queryByRole("region", { name: "Import results" })).toBeNull();
    expect(screen.queryByRole("table", { name: "Projects to receive" })).toBeNull();
    expect(screen.getByRole("button", { name: "Check Paths" })).toHaveProperty("disabled", true);
    expect(api.startLibraryBatch).toHaveBeenCalledTimes(1);
  });

  it("keeps a successful previous batch collapsed with readable project names when reopened", async () => {
    localStorage.setItem("connlab.projectLibrary.lastBatch:D:/managed/projects", "previous-completed");
    vi.mocked(api.getLibraryBatch).mockResolvedValue({ batch_id: "previous-completed", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:\\old\\DL-2026-09-032 CPI-450", status: "added", message: "Added", member_id: "existing-cpi" }] });
    const onOpenMember = vi.fn();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} />);
    const history = await screen.findByText(/^Last Import/);
    expect(history.closest("details")).toHaveProperty("open", false);
    expect(screen.getByRole("button", { name: "Choose Project Folders", exact: true })).toBeTruthy();
    await userEvent.setup().click(history);
    await userEvent.setup().click(screen.getByRole("button", { name: "Open DL-2026-09-032 CPI-450" }));
    expect(onOpenMember).toHaveBeenCalledWith("existing-cpi", "previous-completed");
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
    expect(api.resumeLibraryBatch).not.toHaveBeenCalled();
  });

  it.each(["running", "interrupted", "completed"] as const)("keeps recovered %s work with unresolved items visible", async status => {
    localStorage.setItem("connlab.projectLibrary.lastBatch:D:/managed/projects", "unfinished");
    vi.mocked(api.getLibraryBatch).mockResolvedValue({ batch_id: "unfinished", status, counts: { added: 0, already_added: 0, review: 1, failed: 1 }, items: [{ source_path: "D:/old/problem", status: "failed", message: "The source folder is unavailable.", member_id: null }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    expect(await screen.findByText("The source folder is unavailable.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Choose Project Folders", exact: true })).toBeTruthy();
    expect(screen.queryByText(/^Last Import/)).toBeNull();
    expect(api.resumeLibraryBatch).not.toHaveBeenCalled();
  });

  it("pages a large recovered result and puts items needing attention on the first page", async () => {
    localStorage.setItem("connlab.projectLibrary.lastBatch:D:/managed/projects", "large-result");
    const items = Array.from({ length: 24 }, (_, i) => ({ source_path: `D:/old/Project ${i + 1}`, status: "added", message: "Added", member_id: `member-${i + 1}` }));
    vi.mocked(api.getLibraryBatch).mockResolvedValue({ batch_id: "large-result", status: "completed", counts: { added: 24, already_added: 0, review: 0, failed: 1 }, items: [...items, { source_path: "D:/old/problem", status: "failed", message: "Review this source folder.", member_id: null }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    expect(await screen.findByText("Review this source folder.")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Open Project 24", exact: true })).toBeNull();
    await userEvent.setup().click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByRole("button", { name: "Open Project 24", exact: true })).toBeTruthy();
    expect(api.resumeLibraryBatch).not.toHaveBeenCalled();
  });

  it("simplifies a single-project preview while retaining its selection and final confirmation", async () => {
    vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: [plan.items[0]] } as api.LibraryIntakePlan);
    const user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    expect(await screen.findByRole("heading", { name: "Choose projects" })).toBeTruthy();
    expect(screen.getByText(/Original files stay in place/)).toBeTruthy();
    await enterSources(user, "D:/old/Force");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    expect(screen.queryByRole("button", { name: "Select Ready Projects" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Clear Selection" })).toBeNull();
    expect(screen.queryByRole("combobox", { name: "Show" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Previous" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Next" })).toBeNull();
    await user.click(screen.getByRole("checkbox", { name: "Select Force test" }));
    expect(screen.getByRole("button", { name: "Import Projects (0)" })).toHaveProperty("disabled", true);
    await user.click(screen.getByRole("checkbox", { name: "Select Force test" }));
    await user.click(screen.getByRole("button", { name: "Import Projects (1)" }));
    expect(screen.getByRole("dialog", { name: "Confirm Import" })).toBeTruthy();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("shows a new single-project preview after a previous batch filter excluded it", async () => {
    const user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await user.selectOptions(await screen.findByRole("combobox", { name: "Show" }), "conflict");
    vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: [plan.items[0]] } as api.LibraryIntakePlan);
    await user.clear(screen.getByLabelText("Source paths"));
    await enterSources(user, "D:/old/Force");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    expect(await screen.findByRole("checkbox", { name: "Select Force test" })).toHaveProperty("checked", true);
    expect(screen.queryByRole("combobox", { name: "Show" })).toBeNull();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("retains bulk selection and pagination for a large preview", async () => {
    const items = Array.from({ length: 21 }, (_, i) => ({ ...plan.items[0], source_path: `D:/old/project-${i}`, title: `Project ${i}` }));
    vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items } as api.LibraryIntakePlan);
    const user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("button", { name: "Import Projects (21)" });
    await user.click(screen.getByRole("button", { name: "Clear Selection" }));
    expect(screen.getByRole("button", { name: "Import Projects (0)" })).toHaveProperty("disabled", true);
    await user.click(screen.getByRole("button", { name: "Select Ready Projects" }));
    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByRole("checkbox", { name: "Select Project 20" })).toHaveProperty("checked", true);
    expect(screen.getByRole("button", { name: "Import Projects (21)" })).toBeTruthy();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("opens verified duplicate projects directly without selecting or receiving them", async () => {
    vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: [
      { ...plan.items[0], status: "already_added", existing_member_id: "existing-1" },
      { ...plan.items[1], status: "already_added", can_keep_separate: false },
    ] } as api.LibraryIntakePlan);
    const onOpenMember = vi.fn(), user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    expect(screen.getByText(/Nothing needs to be imported/)).toBeTruthy();
    expect(screen.getByRole("button", { name: /^Import Projects \(\d+\)$/ })).toHaveProperty("disabled", true);
    expect(screen.queryByRole("button", { name: "Open Existing Cable test" })).toBeNull();
    await user.click(screen.getByRole("button", { name: "Open Existing Force test" }));
    expect(onOpenMember).toHaveBeenCalledWith("existing-1");
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it.each(["ready", "conflict", "unavailable"] as const)("does not offer an existing-project link for %s rows", async status => {
    vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: [{ ...plan.items[0], status, existing_member_id: "unverified-link" }] } as api.LibraryIntakePlan);
    const user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    expect(screen.queryByRole("button", { name: "Open Existing Force test" })).toBeNull();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("receives only selected new projects in a mixed preview and locks navigation during confirmation", async () => {
    vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: [plan.items[0], { ...plan.items[1], status: "already_added", can_keep_separate: false, existing_member_id: "old-cable" }] } as api.LibraryIntakePlan);
    const user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    expect(screen.getByText(/Already added projects will be kept/)).toBeTruthy();
    expect(screen.getByRole("checkbox", { name: "Select Cable test" })).toHaveProperty("checked", false);
    await user.click(screen.getByRole("button", { name: /^Import Projects \(\d+\)$/ }));
    expect(screen.getByRole("button", { name: "Open Existing Cable test" })).toHaveProperty("disabled", true);
    await user.click(screen.getByRole("button", { name: "Confirm Import" }));
    await screen.findByText(/1 added/);
    expect(api.startLibraryBatch).toHaveBeenCalledWith(expect.objectContaining({ selected: ["D:/old/Force"], keep_separate: [] }));
  });

  it("lets the user add, review and remove source folders without editing paths", async () => {
    const user = userEvent.setup();
    vi.mocked(api.pickLibraryFolder).mockResolvedValueOnce("D:/one").mockResolvedValueOnce("D:/two").mockResolvedValueOnce("D:/two");
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Choose Project Folders", exact: true }));
    await user.click(await screen.findByRole("button", { name: "Choose Project Folders", exact: true }));
    await user.click(await screen.findByRole("button", { name: "Choose Project Folders", exact: true }));
    expect(screen.getByText("2 locations selected")).toBeTruthy();
    expect(within(screen.getByRole("list", { name: "Selected sources" })).getAllByRole("listitem")).toHaveLength(2);
    await user.click(screen.getByRole("button", { name: "Remove D:/one from selection" }));
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    expect(api.scanLibrarySources).toHaveBeenCalledWith(["D:/two"], expect.any(AbortSignal));
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
    vi.mocked(api.pickLibraryFolder).mockResolvedValueOnce("D:/two");
    await user.click(await screen.findByRole("button", { name: "Choose Project Folders", exact: true }));
    expect(screen.getByRole("table", { name: "Projects to receive" })).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Remove D:/two from selection" }));
    expect(screen.queryByRole("table", { name: "Projects to receive" })).toBeNull();
    expect(screen.getByRole("button", { name: "Import Projects (0)" })).toHaveProperty("disabled", true);
    expect(screen.getByRole("button", { name: "Check Paths" })).toHaveProperty("disabled", true);
  });

  it("keeps manual entry optional and clears all selected locations without writing", async () => {
    const user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    expect((await screen.findByLabelText("Source paths")).closest("details")).toHaveProperty("open", false);
    await enterSources(user, '"D:/one"\n D:/two ');
    expect(screen.getByText("2 locations selected")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Clear All" }));
    expect(screen.queryByRole("list", { name: "Selected sources" })).toBeNull();
    expect(screen.getByLabelText("Source paths")).toHaveProperty("value", "");
    expect(api.scanLibrarySources).not.toHaveBeenCalled();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("locks the selection during the folder picker and preserves the reviewed plan on cancellation", async () => {
    const user = userEvent.setup();
    await act(async () => {
      render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    });
    await enterSources(user, "D:/one\nD:/two");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    let cancel!: (path: null) => void;
    vi.mocked(api.pickLibraryFolder).mockReturnValueOnce(new Promise(resolve => { cancel = resolve; }));
    await user.click(await screen.findByRole("button", { name: "Choose Project Folders", exact: true }));
    expect(screen.getByRole("button", { name: "Remove D:/one from selection" })).toHaveProperty("disabled", true);
    expect(screen.getByRole("button", { name: "Clear All" })).toHaveProperty("disabled", true);
    await act(async () => cancel(null));
    expect(screen.getByRole("table", { name: "Projects to receive" })).toBeTruthy();
    expect(screen.getByText("2 locations selected")).toBeTruthy();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("keeps an explicitly chosen manual project root while checking its saved-data metadata", async () => {
    const user = userEvent.setup();
    const root: api.LibraryCandidate = { source_path: "D:/Manual project", title: "Manual project", ltr_number: null, kind: "project", warnings: [], child_folders: ["D:/Manual project/Photos", "D:/Manual project/Results"] };
    vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [{ ...root, source_path: root.child_folders[1], title: "Results", child_folders: [] }], boundary_roots: [root], warnings: [], truncated: false });
    vi.mocked(api.planLibraryIntake).mockResolvedValueOnce(plan as api.LibraryIntakePlan).mockResolvedValue({ plan_id: "manual-root", fingerprint: "root-proof", warnings: [], items: [{ ...plan.items[0], source_path: root.source_path, title: root.title, ltr_number: null, status: "ready" }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, root.source_path);
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    const boundary = screen.getByRole("group", { name: "Project boundary Manual project" });
    expect(within(boundary).getByText(/complete folder/)).toBeTruthy();
    await user.click(within(boundary).getByRole("button", { name: "Import as One Project" }));
    expect(await screen.findByRole("checkbox", { name: "Select Manual project" })).toHaveProperty("checked", true);
    expect(api.scanLibrarySources).toHaveBeenCalled();
    expect(api.planLibraryIntake).toHaveBeenLastCalledWith([root.source_path], expect.any(AbortSignal));
    await user.click(screen.getByRole("button", { name: /^Import Projects \(\d+\)$/ }));
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("uses all immediate subfolders as explicit project boundaries in one preview and supports older scan responses", async () => {
    const user = userEvent.setup();
    const children = Array.from({ length: 300 }, (_, index) => `D:/Collection/Project ${index + 1}`);
    const root: api.LibraryCandidate = { source_path: "D:/Collection", title: "Collection", ltr_number: null, kind: "project", warnings: [], child_folders: children };
    vi.mocked(api.scanLibrarySources).mockResolvedValueOnce({ items: [root], warnings: [], truncated: false }).mockResolvedValue({ items: children.map((path, index) => ({ ...root, source_path: path, title: `Project ${index + 1}`, child_folders: [] })), warnings: [], truncated: false });
    vi.mocked(api.planLibraryIntake).mockResolvedValueOnce(plan as api.LibraryIntakePlan).mockResolvedValue({ plan_id: "all-children", fingerprint: "children-proof", warnings: [], items: children.map((path, index) => ({ ...plan.items[0], source_path: path, title: `Project ${index + 1}`, status: "ready" })) });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, root.source_path);
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    await user.click(screen.getByRole("button", { name: "Find Projects Inside" }));
    expect(await screen.findByText("300 found; 300 selected.")).toBeTruthy();
    expect(screen.getByText("Page 1 of 15")).toBeTruthy();
    expect(api.planLibraryIntake).toHaveBeenLastCalledWith(children, expect.any(AbortSignal));
    expect(api.scanLibrarySources).toHaveBeenCalled();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("replaces incomplete automatic suggestions with a complete explicit-root preview", async () => {
    const user = userEvent.setup();
    const root: api.LibraryCandidate = { source_path: "D:/Whole project", title: "Whole project", ltr_number: null, kind: "project", warnings: [], child_folders: ["D:/Whole project/Source Book"] };
    vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [], boundary_roots: [root], warnings: [], truncated: true });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, root.source_path);
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    expect(await screen.findByText(/Incomplete results/)).toBeTruthy();
    expect(api.planLibraryIntake).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Import as One Project" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    expect(screen.queryByText(/Incomplete results/)).toBeNull();
    expect(screen.queryByText(/No projects found/)).toBeNull();
    expect(api.planLibraryIntake).toHaveBeenCalledWith([root.source_path], expect.any(AbortSignal));
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("locks boundary changes during preview and ignores a late result after leaving the import page", async () => {
    const user = userEvent.setup();
    const root: api.LibraryCandidate = { source_path: "D:/Manual", title: "Manual", ltr_number: null, kind: "project", warnings: [], child_folders: ["D:/Manual/Results"] };
    vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [root], boundary_roots: [root], warnings: [], truncated: false });
    let finish!: (value: api.LibraryIntakePlan) => void;
    let boundarySignal: AbortSignal | undefined;
    const fresh = { plan_id: "fresh", fingerprint: "fresh-proof", warnings: [], items: [{ ...plan.items[0], source_path: "D:/Fresh", title: "Fresh project", status: "ready" as const }] };
    vi.mocked(api.planLibraryIntake).mockResolvedValueOnce(plan as api.LibraryIntakePlan).mockImplementationOnce((_paths, signal) => { boundarySignal = signal; return new Promise(resolve => { finish = resolve; }); }).mockResolvedValue(fresh);
    const view = render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, root.source_path);
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    await user.click(screen.getByRole("button", { name: "Import as One Project" }));
    expect(screen.getByLabelText("Source paths")).toHaveProperty("disabled", true);
    expect(screen.getByRole("button", { name: "Import as One Project" })).toHaveProperty("disabled", true);
    expect(screen.getByRole("button", { name: "Find Projects Inside" })).toHaveProperty("disabled", true);
    expect(screen.getByRole("button", { name: "Import Projects (0)" })).toHaveProperty("disabled", true);
    await user.click(screen.getByRole("button", { name: "Find Projects Inside" }));
    expect(api.planLibraryIntake).toHaveBeenCalledTimes(2);
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
    view.unmount();
    expect(boundarySignal?.aborted).toBe(true);
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/Fresh");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("checkbox", { name: "Select Fresh project" });
    await act(async () => { finish({ ...fresh, items: [{ ...fresh.items[0], title: "Late old project" }] }); });
    expect(screen.queryByRole("checkbox", { name: "Select Late old project" })).toBeNull();
    expect(screen.getByRole("checkbox", { name: "Select Fresh project" })).toHaveProperty("checked", true);
  });

  it("does not let late previous-batch recovery replace a newly reviewed source selection", async () => {
    let finish!: (value: api.LibraryBatch) => void;
    vi.mocked(api.getLibraryBatch).mockImplementation(() => new Promise(resolve => { finish = resolve; }));
    localStorage.setItem("connlab.projectLibrary.lastBatch:D:/managed/projects", "old-batch");
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await screen.findByText("D:/managed/projects");
    const user = userEvent.setup();
    await enterSources(user, "D:/fresh");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    await act(async () => { finish({ batch_id: "old-batch", status: "interrupted", counts: { added: 0, already_added: 0, review: 0, failed: 1 }, items: [{ source_path: "D:/old", status: "failed", message: "Old batch", member_id: null }] }); });
    expect(screen.getByRole("table", { name: "Projects to receive" })).toBeTruthy();
    expect(screen.queryByText("Old batch")).toBeNull();
  });

  it("persists a client batch identity before submission and reuses it after a lost response", async () => {
    const user = userEvent.setup();
    let submittedId = "";
    vi.mocked(api.startLibraryBatch).mockImplementationOnce(async request => {
      submittedId = request.batch_id!;
      expect(submittedId).toMatch(/^[a-f0-9]{32}$/);
      expect(localStorage.getItem("connlab.projectLibrary.lastBatch:D:/managed/projects")).toBe(submittedId);
      throw new Error("The connection was interrupted.");
    }).mockImplementationOnce(async request => {
      expect(request.batch_id).toBe(submittedId);
      return { batch_id: submittedId, status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [] };
    });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await user.click(await screen.findByRole("button", { name: /^Import Projects \(\d+\)$/ }));
    await user.click(screen.getByRole("button", { name: "Confirm Import" }));
    await screen.findByText("The connection was interrupted.");
    await user.click(screen.getByRole("button", { name: "Retry Batch Submission" }));
    expect(await screen.findByText(/1 added/)).toBeTruthy();
  });

  it("recovers an interrupted batch after reopening and resumes only on explicit request", async () => {
    localStorage.setItem("connlab.projectLibrary.lastBatch:D:/managed/projects", "previous-batch");
    vi.mocked(api.getLibraryBatch).mockResolvedValue({ batch_id: "previous-batch", status: "interrupted", counts: { added: 0, already_added: 0, review: 0, failed: 1 }, items: [{ source_path: "D:/old/Force", status: "failed", message: "Copy interrupted.", member_id: null }] });
    vi.mocked(api.resumeLibraryBatch).mockResolvedValue({ batch_id: "previous-batch", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "added", message: "Added", member_id: "member-1" }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await screen.findByText("Copy interrupted.");
    expect(api.resumeLibraryBatch).not.toHaveBeenCalled();
    await userEvent.setup().click(screen.getByRole("button", { name: "Resume Batch" }));
    expect(await screen.findByText(/1 added/)).toBeTruthy();
    expect(api.resumeLibraryBatch).toHaveBeenCalledWith("previous-batch");
  });

  it("requires explicit ownership for loose files before planning their reception", async () => {
    const user = userEvent.setup();
    vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [{ source_path: "D:/loose/result.xlsx", title: "result.xlsx", ltr_number: null, kind: "file", warnings: [], child_folders: [] }], warnings: [], truncated: false });
    const active: api.LibraryMember = { member_id: "existing-1", project_id: "project-1", ltr_number: "DL-2026-09-032", title: "CPI-450", folder_path: "D:/managed/CPI", revision: 1, batch_id: null, snapshot_status: "current", snapshot_created_at: null, warnings: [], can_continue: true };
    vi.mocked(api.listLibraryMembers).mockResolvedValue({ items: [active, { ...active, member_id: "history-1", title: "Historical CPI", is_history: true, can_continue: false }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/loose/result.xlsx");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    const assignment = await screen.findByLabelText("Assign result.xlsx");
    expect(api.planLibraryIntake).not.toHaveBeenCalled();
    expect(within(assignment).queryByRole("option", { name: /Historical CPI/ })).toBeNull();
    await user.selectOptions(assignment, "existing-1");
    await user.click(screen.getByRole("button", { name: "Review File Assignments" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    expect(api.planLibraryIntake).toHaveBeenCalledWith(["D:/loose/result.xlsx"], expect.any(AbortSignal), [{ source_path: "D:/loose/result.xlsx", target_member_id: "existing-1" }]);
  });

  it("checks the whole selection automatically and writes only after explicit confirmation", async () => {
    const user = userEvent.setup();
    const onOpenMember = vi.fn();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    const table = await screen.findByRole("table", { name: "Projects to receive" });
    expect(within(table).getByText("Force test")).toBeTruthy();
    expect(screen.getByRole("checkbox", { name: "Select Force test" })).toHaveProperty("checked", true);
    expect(screen.getByRole("checkbox", { name: "Select Cable test" })).toHaveProperty("checked", false);
    expect(screen.getByText("Another project uses this LTR.")).toBeTruthy();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: /^Import Projects \(\d+\)$/ }));
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: /^Import Projects \(\d+\)$/ }));
    await user.click(screen.getByRole("button", { name: "Confirm Import" }));
    expect(await screen.findByText(/1 added/)).toBeTruthy();
    expect(api.startLibraryBatch).toHaveBeenCalledWith(expect.objectContaining({ batch_id: expect.stringMatching(/^[a-f0-9]{32}$/), plan_id: "plan-1", fingerprint: "verified", selected: ["D:/old/Force"], keep_separate: [] }));
    await user.click(screen.getByRole("button", { name: "Open Force test" }));
    expect(onOpenMember).toHaveBeenCalledWith("member-1", "batch-1");
  });

  it("requires a separate choice for number conflicts and invalidates results when sources change", async () => {
    const user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await screen.findByRole("checkbox", { name: "Select Force test" });
    await user.click(screen.getByRole("checkbox", { name: "Keep Cable test separate" }));
    expect(screen.getByRole("checkbox", { name: "Select Cable test" })).toHaveProperty("checked", true);
    await enterSources(user, "/different");
    expect(screen.queryByRole("table")).toBeNull();
    expect(screen.getByRole("button", { name: "Import Projects (0)" })).toHaveProperty("disabled", true);
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("keeps failed batches available for an explicit retry", async () => {
    const user = userEvent.setup();
    vi.mocked(api.startLibraryBatch).mockResolvedValue({ batch_id: "batch-1", status: "interrupted", counts: { added: 0, already_added: 0, review: 0, failed: 1 }, items: [{ source_path: "D:/old/Force", status: "failed", message: "File is locked. Retry when available.", member_id: null }] });
    vi.mocked(api.resumeLibraryBatch).mockResolvedValue({ batch_id: "batch-1", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "added", message: "Added", member_id: "member-1" }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Paths" }));
    await user.click(await screen.findByRole("button", { name: /^Import Projects \(\d+\)$/ }));
    await user.click(screen.getByRole("button", { name: "Confirm Import" }));
    expect(await screen.findByText("File is locked. Retry when available.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Choose Project Folders", exact: true })).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Resume Batch" }));
    expect(await screen.findByText(/1 added/)).toBeTruthy();
  });
});
it("keeps one project chooser and moves manual entry and in-place linking into Advanced", async () => {
  const onLegacyPreview = vi.fn();
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onLegacyPreview={onLegacyPreview} />);
  await screen.findByRole("heading", { name: "Save imported projects to" });
  expect(screen.getByRole("button", { name: "Choose Project Folders", exact: true })).toBeTruthy();
  const options = screen.getByText("Advanced").closest("details");
  expect(options).toHaveProperty("open", false);
  expect(screen.queryByText("Legacy", { exact: true })).toBeNull();
  await userEvent.setup().click(screen.getByText("Advanced"));
  expect(options).toHaveProperty("open", true);
  expect(screen.queryByRole("heading", { name: "Restore Project Data" })).toBeNull();
  expect(screen.queryByRole("textbox", { name: "Portable project folder" })).toBeNull();
  expect(api.inspectPortableProject).not.toHaveBeenCalled();
  expect(api.restorePortableProject).not.toHaveBeenCalled();
  await userEvent.setup().click(screen.getByRole("button", { name: "Link Folders Without Copying" }));
  expect(onLegacyPreview).toHaveBeenCalledOnce();
});

it("opens an already registered result without attaching it to a new batch", async () => {
  vi.mocked(api.startLibraryBatch).mockResolvedValue({ batch_id: "duplicate-batch", status: "completed", counts: { added: 0, already_added: 1, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "already_added", message: "Already added", member_id: "existing-member" }] });
  const onOpenMember = vi.fn(), user = userEvent.setup();
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} />);
  await enterSources(user, "D:/old");
  await user.click(screen.getByRole("button", { name: "Check Paths" }));
  await user.click(await screen.findByRole("button", { name: /^Import Projects \(\d+\)$/ }));
  await user.click(screen.getByRole("button", { name: "Confirm Import" }));
  await user.click(await screen.findByRole("button", { name: "Open Force test" }));
  expect(onOpenMember).toHaveBeenCalledWith("existing-member", undefined);
  expect(screen.getByRole("button", { name: "View Imported Projects" })).toHaveProperty("disabled", true);
});
