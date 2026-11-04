import { act, render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ProjectLibraryImport } from "./ProjectLibraryImport";
import * as api from "../../api/projectLibrary";

vi.mock("../../api/projectLibrary", () => ({
  getLibraryRuntime: vi.fn(), getLibraryMember: vi.fn(), scanLibrarySources: vi.fn(), planLibraryIntake: vi.fn(), listLibraryMembers: vi.fn(),
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
const manualMember: api.LibraryMember = { member_id: "member-1", project_id: "manual-project", ltr_number: plan.items[0].ltr_number,
  title: "Force test", folder_path: "D:/managed/projects/DL-2021-01-030A1", revision: 2, batch_id: "batch-1",
  snapshot_status: "missing", snapshot_created_at: null, warnings: [], can_continue: true };

async function enterSources(user: ReturnType<typeof userEvent.setup>, value: string) {
  vi.mocked(api.pickLibraryFolder).mockRejectedValueOnce(new Error("System folder picker unavailable"));
  await user.click(await screen.findByRole("button", { name: "Choose Project Folder", exact: true }));
  const editor = await screen.findByLabelText("Source path");
  await user.type(editor, value);
}
async function chooseFolder(user: ReturnType<typeof userEvent.setup>) {
  await waitFor(() => expect(screen.queryByRole("button", {name:"Choose Project Folder", exact:true}) || screen.queryByRole("button", {name:"Change Folder"})).toBeTruthy());
  const chooser = screen.queryByRole("button", {name:"Choose Project Folder", exact:true});
  await user.click(chooser ?? await screen.findByRole("button", {name:"Change Folder"}));
}

beforeEach(() => {
  vi.resetAllMocks();
  localStorage.clear();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old/Force");
  vi.mocked(api.getLibraryRuntime).mockResolvedValue({ library_root: "D:/managed", projects_root: "D:/managed/projects", data_root: "D:/managed/data", database_path: "D:/managed/data/connlab.sqlite3", configured: true, format_version: 1 });
  vi.mocked(api.getLibraryMember).mockResolvedValue(manualMember);
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [plan.items[0]].map(row => ({ source_path: row.source_path, title: row.title, ltr_number: row.ltr_number, kind: "project", warnings: [], child_folders: [] })), warnings: [], truncated: false });
  vi.mocked(api.planLibraryIntake).mockResolvedValue({...plan, items:[plan.items[0]]} as api.LibraryIntakePlan);
  vi.mocked(api.startLibraryBatch).mockResolvedValue({ batch_id: "batch-1", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "added", message: "Added", member_id: "member-1" }] });
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

it("presents one project without batch selection or a repeated source editor", async () => {
  const user = userEvent.setup();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old/Force");
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: [plan.items[0]] } as api.LibraryIntakePlan);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await chooseFolder(user);
  await screen.findByRole("button", { name: "Confirm Import", exact: true });
  expect(screen.queryByRole("checkbox")).toBeNull();
  expect(screen.queryByText(/found;.*selected/)).toBeNull();
  expect(screen.queryByRole("button", { name: "Choose Project Folder" })).toBeNull();
  expect(screen.getByRole("button", { name: "Change Folder" })).toBeTruthy();
  expect(screen.getByText("Import existing files. Project information can be completed later.")).toBeTruthy();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it("continues directly into a single imported project using its verified identity", async () => {
  const user=userEvent.setup(), open=vi.fn();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old/Force");
  vi.mocked(api.planLibraryIntake).mockResolvedValue({...plan,items:[plan.items[0]]} as api.LibraryIntakePlan);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={open} />);
  await user.click(await screen.findByRole("button",{name:"Choose Project Folder"}));
  await waitFor(()=>expect(open).toHaveBeenCalledExactlyOnceWith("manual-project"));
  expect(api.startLibraryBatch).toHaveBeenCalledTimes(1);
});

it("does not turn an already confirmed local-data link into another review step", async () => {
  const user=userEvent.setup(), open=vi.fn();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old/Force");
  vi.mocked(api.planLibraryIntake).mockResolvedValue({...plan,items:[{...plan.items[0],source_state:"local_project",warnings:["Link the existing project and retain its data."]}]} as api.LibraryIntakePlan);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={open} />);
  await chooseFolder(user);
  await waitFor(()=>expect(open).toHaveBeenCalledExactlyOnceWith("manual-project"));
  expect(api.startLibraryBatch).toHaveBeenCalledTimes(1);
});

it("requires an explicit files-only choice for a ConnLab project without saved data", async () => {
  const user=userEvent.setup();
  const incomplete={...plan.items[0],status:"conflict" as const,source_state:"incomplete",warnings:["Export the project from the original computer."]};
  const files={...incomplete,status:"ready" as const,source_state:"files_only",warnings:["Only files will be imported. Existing ConnLab test data will not be restored."]};
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old/Force");
  vi.mocked(api.planLibraryIntake).mockResolvedValueOnce({...plan,items:[incomplete]}).mockResolvedValue({...plan,items:[files]});
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button",{name:"Choose Project Folder"}));
  await user.click(await screen.findByRole("button",{name:"Import Files Only"}));
  expect(api.planLibraryIntake).toHaveBeenLastCalledWith(["D:/old/Force"],expect.any(AbortSignal),[{source_path:"D:/old/Force",files_only:true}]);
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  expect(screen.queryByRole("checkbox")).toBeNull();
  await user.click(await screen.findByRole("button",{name:"Confirm Import",exact:true}));
  await screen.findByRole("button",{name:"Open Force test"});
  expect(api.restorePortableProject).not.toHaveBeenCalled();
  expect(screen.getByText("Only files will be imported. Existing ConnLab test data will not be restored.")).toBeTruthy();
});

it("offers one direct conflict decision without a disabled single-project checkbox", async () => {
  const user=userEvent.setup();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old/Cable");
  vi.mocked(api.planLibraryIntake).mockResolvedValue({...plan,items:[plan.items[1]]} as api.LibraryIntakePlan);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button",{name:"Choose Project Folder"}));
  await screen.findByRole("button",{name:"Keep Another Copy"});
  expect(screen.queryByRole("checkbox")).toBeNull();
  expect(screen.queryByText("Needs Review")).toBeNull();
  expect(screen.queryByRole("button",{name:/Resolve Conflict/})).toBeNull();
  expect(screen.queryByRole("button",{name:"Confirm Import",exact:true})).toBeNull();
  await user.click(screen.getByRole("button",{name:"Keep Another Copy"}));
  await user.click(screen.getByRole("button",{name:"Confirm Import",exact:true}));
  await waitFor(()=>expect(api.startLibraryBatch).toHaveBeenCalledWith(expect.objectContaining({selected:["D:/old/Cable"],keep_separate:["D:/old/Cable"]})));
});

it("uses the server-reviewed location in confirmation when Settings changed after the page loaded", async () => {
  const user = userEvent.setup();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old");
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, projects_root: "D:/Current Save Location", items: [{ ...plan.items[0], target_path: "D:/Current Save Location/Force" }] } as api.LibraryIntakePlan);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await chooseFolder(user);
  await screen.findByRole("button", { name: "Confirm Import" });
  const confirmation = screen.getByRole("region", { name: "Confirm import selection" });
  expect(confirmation.textContent).toContain("Will copy to Current Save Location.");
  expect(within(confirmation).getByTitle("D:/Current Save Location")).toBeTruthy();
  expect(confirmation.textContent).not.toContain("D:/managed/projects");
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it("reviews one saved project without bulk controls and explains its use before confirmation", async () => {
  const user = userEvent.setup();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue(savedProject.source_path);
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [{ ...savedProject, kind: "project", child_folders: [], has_portable: true }], warnings: [], truncated: false });
  vi.mocked(api.inspectPortableProject).mockResolvedValue(savedProject);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await chooseFolder(user);
  const table = await screen.findByRole("article", { name: "Project to import" });
  expect(within(table).queryByRole("checkbox")).toBeNull();
  expect(within(table).getByText("Restore existing project data and continue working.")).toBeTruthy();
  expect(screen.queryByRole("combobox", { name: "Show" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Select Ready Projects" })).toBeNull();
  expect(screen.queryByRole("navigation", { name: "Project review pages" })).toBeNull();
  expect(screen.getByRole("button", { name: "Confirm Import" })).toHaveProperty("disabled", false);
  expect(api.restorePortableProject).not.toHaveBeenCalled();
});

it("opens a fully restored single project automatically when no source review remains", async () => {
  const user=userEvent.setup(), open=vi.fn();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue(savedProject.source_path);
  vi.mocked(api.scanLibrarySources).mockResolvedValue({items:[{...savedProject,kind:"project",child_folders:[],has_portable:true}],warnings:[],truncated:false});
  vi.mocked(api.inspectPortableProject).mockResolvedValue({...savedProject,warnings:[]});
  vi.mocked(api.restorePortableProject).mockResolvedValue({...savedResult,warnings:[],member:{...savedResult.member,warnings:[]}});
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={open} />);
  await chooseFolder(user);
  await waitFor(()=>expect(open).toHaveBeenCalledExactlyOnceWith("saved-project"));
  expect(api.restorePortableProject).toHaveBeenCalledTimes(1);
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it("uses Settings as the only destination editor and blocks import until it is configured", async () => {
  vi.mocked(api.getLibraryRuntime).mockResolvedValue({ library_root: "D:/app", projects_root: "D:/unused-default", data_root: "D:/app/Data", database_path: "D:/app/Data/connlab.sqlite3", configured: false, format_version: 1 });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  expect(await screen.findByText(/Project default save location in Settings/)).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Choose Project Folder" })).toBeNull();
  expect(screen.queryByLabelText("Save imported projects to")).toBeNull();
  expect(screen.queryByText("D:/unused-default")).toBeNull();
  expect(api.saveLibraryDestination).not.toHaveBeenCalled();
  expect(api.scanLibrarySources).not.toHaveBeenCalled();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it.each(["files", "restored", "history"] as const)("explains the fallback next step after importing one %s project", async kind => {
  const user = userEvent.setup(), onOpenMember = vi.fn();
  const isSaved = kind !== "files";
  const candidate = isSaved ? savedProject : plan.items[0];
  vi.mocked(api.pickLibraryFolder).mockResolvedValue(candidate.source_path);
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [{ ...candidate, kind: "project", child_folders: [], has_portable: isSaved }], warnings: [], truncated: false });
  vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: [plan.items[0]] } as api.LibraryIntakePlan);
  vi.mocked(api.inspectPortableProject).mockResolvedValue({ ...savedProject, resolution: kind === "history" ? "keep_as_history" : null });
  vi.mocked(api.restorePortableProject).mockResolvedValue(kind === "history" ? { ...savedResult, status: "history_kept", member: { ...savedResult.member, is_history: true, can_continue: false } } : savedResult);
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} />);
  await chooseFolder(user);
  await user.click(await screen.findByRole("button", { name: "Confirm Import" }));
  const results = await screen.findByRole("region", { name: "Import results" });
  expect(within(results).getByText(kind === "files" ? "Project files imported." : kind === "history" ? "Historical copy saved for browsing." : "Project and saved test data restored.")).toBeTruthy();
  expect(within(results).getByText(kind === "files" ? /complete missing project information/ : kind === "history" ? /current working project is unchanged/ : /review its data and continue testing/)).toBeTruthy();
  expect(within(results).getByRole("heading", { name: `${candidate.ltr_number} ${candidate.title}` })).toBeTruthy();
  if (isSaved) {
    const issues = within(results).getByText("1 item needs review").closest("details")!;
    expect(issues.open).toBe(true);
    expect(within(issues).getByText(savedProject.warnings[0])).toBeTruthy();
  }
  const open = within(results).getByRole("button", { name: `Open ${candidate.title}` });
  expect(open.textContent).toBe("Open Project");
  await user.click(open);
  expect(onOpenMember).toHaveBeenCalledWith(isSaved ? "saved-member" : "member-1");
});

it.each([
  { can_continue: false },
  { project_id: null },
  { is_history: true },
])("keeps restored projects without workbench eligibility in their details: %j", async override => {
  const user = userEvent.setup(), onOpenProject = vi.fn(), onOpenMember = vi.fn();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue(savedProject.source_path);
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [{ ...savedProject, kind: "project", child_folders: [], has_portable: true }], warnings: [], truncated: false });
  vi.mocked(api.inspectPortableProject).mockResolvedValue(savedProject);
  vi.mocked(api.restorePortableProject).mockResolvedValue({ ...savedResult, member: { ...savedResult.member, ...override } });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} onOpenProject={onOpenProject} />);
  await chooseFolder(user);
  if ("is_history" in override) await user.click(await screen.findByRole("button", { name: "Open Snapshot project" }));
  await waitFor(() => expect(onOpenMember).toHaveBeenCalledWith("saved-member"));
  expect(onOpenProject).not.toHaveBeenCalled();
});

it.each([{ can_continue: false }, { project_id: null }, { is_history: true }])("opens details when an ordinary import is not eligible for workbench navigation: %j", async override => {
  const user = userEvent.setup(), onOpenProject = vi.fn(), onOpenMember = vi.fn();
  vi.mocked(api.getLibraryMember).mockResolvedValue({ ...manualMember, ...override });
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old");
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} onOpenProject={onOpenProject} />);
  await chooseFolder(user);
  await waitFor(() => expect(onOpenMember).toHaveBeenCalledWith("member-1"));
  expect(onOpenProject).not.toHaveBeenCalled();
});

it("keeps the imported result available when resolving its workspace fails, then retries without importing again", async () => {
  const user = userEvent.setup(), onOpenProject = vi.fn();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old");
  vi.mocked(api.getLibraryMember).mockRejectedValueOnce(new Error("Project lookup unavailable"));
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onOpenProject={onOpenProject} />);
  await chooseFolder(user);
  expect(await screen.findByText("Project lookup unavailable")).toBeTruthy();
  expect(onOpenProject).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "Open Force test" }));
  await waitFor(() => expect(onOpenProject).toHaveBeenCalledWith("manual-project"));
  expect(api.startLibraryBatch).toHaveBeenCalledTimes(1);
});

it("ignores a late workspace lookup after leaving the import page", async () => {
  const user = userEvent.setup(), onOpenProject = vi.fn(), onOpenMember = vi.fn();
  let resolve!: (member: api.LibraryMember) => void;
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/old");
  vi.mocked(api.getLibraryMember).mockImplementation(() => new Promise(done => { resolve = done; }));
  const view = render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} onOpenProject={onOpenProject} />);
  await chooseFolder(user);
  await waitFor(() => expect(api.getLibraryMember).toHaveBeenCalledWith("member-1"));
  expect(screen.getByRole("button", { name: "Open Force test" })).toHaveProperty("disabled", true);
  view.unmount();
  await act(async () => { resolve(manualMember); });
  expect(onOpenProject).not.toHaveBeenCalled();
  expect(onOpenMember).not.toHaveBeenCalled();
});

it("does not offer destination controls when Settings already supplies the location", async () => {
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await screen.findByRole("button", { name: "Choose Project Folder" });
  expect(screen.queryByRole("heading", { name: "Save imported projects to" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Change" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Open Folder" })).toBeNull();
});

it("can retry a failed initial setup load without reloading or writing project data", async () => {
  const user = userEvent.setup();
  vi.mocked(api.getLibraryRuntime).mockRejectedValueOnce(new Error("Request failed with 500"));
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "Retry Setup" }));
  expect(await screen.findByRole("button", { name: "Choose Project Folder" })).toBeTruthy();
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
  expect(api.scanLibrarySources).not.toHaveBeenCalled();
});

it("requires a fresh backend conflict review before selecting a saved project for retention", async () => {
  const user = userEvent.setup();
  vi.mocked(api.pickLibraryFolder).mockResolvedValue("D:/snapshot");
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: [{ source_path: "D:/snapshot", title: savedProject.title, ltr_number: savedProject.ltr_number, kind: "project", warnings: [], child_folders: [], has_portable: true }], warnings: [], truncated: false });
  vi.mocked(api.inspectPortableProject).mockResolvedValue({ ...savedProject, status: "conflict", resolution_options: ["keep_as_history"] });
  vi.mocked(api.planPortableRestore).mockResolvedValue({ ...savedProject, resolution: "keep_as_history", fingerprint: "retention-review" });
  vi.mocked(api.restorePortableProject).mockResolvedValue({ ...savedResult, status: "history_kept", member: { ...savedResult.member, is_history: true, can_continue: false } });
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
  await chooseFolder(user);
  await user.click(await screen.findByRole("button", { name: "Keep Another Copy" }));
  expect(api.planPortableRestore).toHaveBeenCalledWith("D:/snapshot", "keep_as_history", expect.any(AbortSignal));
  await screen.findByRole("button", { name: "Confirm Import" });
  expect(screen.getByText("Keep this copy for browsing. The current working project stays unchanged.")).toBeTruthy();
  expect(api.restorePortableProject).not.toHaveBeenCalled();
  await user.click(within(screen.getByRole("region", { name: "Confirm import selection" })).getByRole("button", { name: "Confirm Import" }));
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
  await chooseFolder(user);
  await waitFor(() => expect(api.inspectPortableProject).toHaveBeenCalledWith("D:/snapshot", expect.any(AbortSignal)));
  expect(api.planLibraryIntake).not.toHaveBeenCalled();
  expect(api.restorePortableProject).not.toHaveBeenCalled();
  await screen.findByRole("button", { name: "Confirm Import" });
  const confirmation = screen.getByRole("region", { name: "Confirm import selection" });
  expect(screen.getByText("Restore existing project data and continue working.")).toBeTruthy();
  expect(screen.getByText("One original source file is unavailable.")).toBeTruthy();
  expect(api.restorePortableProject).not.toHaveBeenCalled();
  await user.click(within(confirmation).getByRole("button", { name: "Confirm Import" }));
  await screen.findByRole("button", { name: "Open Snapshot project" });
  expect(api.restorePortableProject).toHaveBeenCalledWith({ plan_id: "portable-plan", fingerprint: "snapshot-fingerprint" });
  expect(api.startLibraryBatch).not.toHaveBeenCalled();
});

it("shows fresh completion directly and clears the old source when importing again", async () => {
    const user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Folder" }));
    await screen.findByRole("article", { name: "Project to import" });
    await screen.findByRole("button", { name: "Confirm Import" });
    await user.click(screen.getByRole("button", { name: "Confirm Import" }));
    await screen.findByRole("button", { name: "Open Force test" });
    expect(screen.queryByText(/^Last Import/)).toBeNull();
    expect(screen.queryByRole("button", { name: "Choose Project Folder", exact: true })).toBeNull();
    expect(screen.queryByText("Enter Path Manually")).toBeNull();
    expect(screen.getByRole("button", { name: "View Projects" })).toHaveProperty("disabled", false);
    await user.click(screen.getByRole("button", { name: "Import More" }));
    expect(screen.queryByLabelText("Source path")).toBeNull();
    expect(screen.getByRole("button", { name: "Choose Project Folder", exact: true })).toBeTruthy();
    expect(screen.queryByRole("region", { name: "Import results" })).toBeNull();
    expect(screen.queryByRole("table", { name: "Projects to receive" })).toBeNull();
    expect(api.startLibraryBatch).toHaveBeenCalledTimes(1);
  });

it("keeps a successful previous batch collapsed with readable project names when reopened", async () => {
    localStorage.setItem("connlab.projectLibrary.lastBatch:D:/managed/projects", "previous-completed");
    vi.mocked(api.getLibraryBatch).mockResolvedValue({ batch_id: "previous-completed", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:\\old\\DL-2026-09-032 CPI-450", status: "added", message: "Added", member_id: "existing-cpi" }] });
    const onOpenMember = vi.fn();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} />);
    const history = await screen.findByText(/^Last Import/);
    expect(history.closest("details")).toHaveProperty("open", false);
    expect(screen.getByRole("button", { name: "Choose Project Folder", exact: true })).toBeTruthy();
    await userEvent.setup().click(history);
    await userEvent.setup().click(screen.getByRole("button", { name: "Open DL-2026-09-032 CPI-450" }));
    expect(onOpenMember).toHaveBeenCalledWith("existing-cpi");
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
    expect(api.resumeLibraryBatch).not.toHaveBeenCalled();
  });

it.each(["running", "interrupted", "completed"] as const)("keeps recovered %s work with unresolved items visible", async status => {
    localStorage.setItem("connlab.projectLibrary.lastBatch:D:/managed/projects", "unfinished");
    vi.mocked(api.getLibraryBatch).mockResolvedValue({ batch_id: "unfinished", status, counts: { added: 0, already_added: 0, review: 1, failed: 1 }, items: [{ source_path: "D:/old/problem", status: "failed", message: "The source folder is unavailable.", member_id: null }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    expect(await screen.findByText("The source folder is unavailable.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Choose Project Folder", exact: true })).toBeTruthy();
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
    expect(await screen.findByRole("heading", { name: "Choose a project" })).toBeTruthy();
    expect(screen.getByText(/LTR folder/)).toBeTruthy();
    await enterSources(user, "D:/old/Force");
    await user.click(screen.getByRole("button", { name: "Check Folder" }));
    await screen.findByRole("article", { name: "Project to import" });
    expect(screen.queryByRole("button", { name: "Select Ready Projects" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Clear Selection" })).toBeNull();
    expect(screen.queryByRole("combobox", { name: "Show" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Previous" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Next" })).toBeNull();
    expect(screen.queryByRole("checkbox")).toBeNull();
    await screen.findByRole("button", { name: "Confirm Import" });
    expect(screen.getByRole("region", { name: "Confirm import selection" })).toBeTruthy();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Back to Projects" }));
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

it("opens verified duplicate projects directly without selecting or receiving them", async () => {
    vi.mocked(api.planLibraryIntake).mockResolvedValue({ ...plan, items: [
      { ...plan.items[0], status: "already_added", existing_member_id: "existing-1" },
    ] } as api.LibraryIntakePlan);
    const onOpenMember = vi.fn(), user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Folder" }));
    await screen.findByRole("article", { name: "Project to import" });
    expect(screen.queryByRole("button", { name: "Confirm Import" })).toBeNull();
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
    await user.click(screen.getByRole("button", { name: "Check Folder" }));
    await screen.findByRole("article", { name: "Project to import" });
    expect(screen.queryByRole("button", { name: "Open Existing Force test" })).toBeNull();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

it("locks the selection during the folder picker and preserves the reviewed plan on cancellation", async () => {
    const user = userEvent.setup();
    await act(async () => {
      render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    });
    await enterSources(user, "D:/old/Force");
    await user.click(screen.getByRole("button", { name: "Check Folder" }));
    await screen.findByRole("article", { name: "Project to import" });
    let cancel!: (path: null) => void;
    vi.mocked(api.pickLibraryFolder).mockReturnValueOnce(new Promise(resolve => { cancel = resolve; }));
    await chooseFolder(user);
    expect(screen.getByRole("button", { name: "Change Folder" })).toHaveProperty("disabled", true);
    expect(screen.getByRole("button", { name: "Confirm Import" })).toHaveProperty("disabled", true);
    await act(async () => cancel(null));
    expect(screen.getByRole("article", { name: "Project to import" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Confirm Import" })).toHaveProperty("disabled", false);
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

it("does not let late previous-batch recovery replace a newly reviewed source selection", async () => {
    let finish!: (value: api.LibraryBatch) => void;
    vi.mocked(api.getLibraryBatch).mockImplementation(() => new Promise(resolve => { finish = resolve; }));
    localStorage.setItem("connlab.projectLibrary.lastBatch:D:/managed/projects", "old-batch");
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await screen.findByRole("button", { name: "Choose Project Folder" });
    const user = userEvent.setup();
    await enterSources(user, "D:/fresh");
    await user.click(screen.getByRole("button", { name: "Check Folder" }));
    await screen.findByRole("article", { name: "Project to import" });
    await act(async () => { finish({ batch_id: "old-batch", status: "interrupted", counts: { added: 0, already_added: 0, review: 0, failed: 1 }, items: [{ source_path: "D:/old", status: "failed", message: "Old batch", member_id: null }] }); });
    expect(screen.getByRole("article", { name: "Project to import" })).toBeTruthy();
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
      return { batch_id: submittedId, status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "added", message: "Added", member_id: "member-1" }] };
    });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Folder" }));
    await screen.findByRole("button", { name: "Confirm Import" });
    await user.click(screen.getByRole("button", { name: "Confirm Import" }));
    await screen.findByText("The connection was interrupted.");
    await user.click(screen.getByRole("button", { name: "Retry Batch Submission" }));
    expect(await screen.findByText("Import complete.")).toBeTruthy();
  });

it.each(["interrupted", "running"] as const)("recovers a %s batch after reopening and resumes only on explicit request", async status => {
    localStorage.setItem("connlab.projectLibrary.lastBatch:D:/managed/projects", "previous-batch");
    vi.mocked(api.getLibraryBatch).mockResolvedValue({ batch_id: "previous-batch", status, counts: { added: 0, already_added: 0, review: 0, failed: 1 }, items: [{ source_path: "D:/old/Force", status: "failed", message: "Copy interrupted.", member_id: null }] });
    vi.mocked(api.resumeLibraryBatch).mockResolvedValue({ batch_id: "previous-batch", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "added", message: "Added", member_id: "member-1" }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await screen.findByText("Copy interrupted.");
    expect(api.resumeLibraryBatch).not.toHaveBeenCalled();
    await userEvent.setup().click(screen.getByRole("button", { name: "Resume Batch" }));
    expect(await screen.findByText("Import complete.")).toBeTruthy();
    expect(api.resumeLibraryBatch).toHaveBeenCalledWith("previous-batch");
  });

it("keeps failed batches available for an explicit retry", async () => {
    const user = userEvent.setup();
    vi.mocked(api.startLibraryBatch).mockResolvedValue({ batch_id: "batch-1", status: "interrupted", counts: { added: 0, already_added: 0, review: 0, failed: 1 }, items: [{ source_path: "D:/old/Force", status: "failed", message: "File is locked. Retry when available.", member_id: null }] });
    vi.mocked(api.resumeLibraryBatch).mockResolvedValue({ batch_id: "batch-1", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "added", message: "Added", member_id: "member-1" }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await enterSources(user, "D:/old");
    await user.click(screen.getByRole("button", { name: "Check Folder" }));
    await screen.findByRole("button", { name: "Confirm Import" });
    await user.click(screen.getByRole("button", { name: "Confirm Import" }));
    expect(await screen.findByText("File is locked. Retry when available.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Change Folder", exact: true })).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Resume Batch" }));
    expect(await screen.findByText("Import complete.")).toBeTruthy();
  });

it("shows one project-folder action without exposing implementation options", async () => {
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} onLegacyPreview={vi.fn()} />);
  await screen.findByRole("button", { name: "Choose Project Folder" });
  expect(screen.getByRole("button", { name: "Choose Project Folder", exact: true })).toBeTruthy();
  expect(screen.queryByText("Enter Path Manually")).toBeNull();
  expect(screen.queryByText("More Options")).toBeNull();
  expect(screen.queryByText(/Save to:/)).toBeNull();
  expect(screen.queryByRole("button", { name: "Link Folders Without Copying" })).toBeNull();
});

it("opens an already registered result without attaching it to a new batch", async () => {
  vi.mocked(api.startLibraryBatch).mockResolvedValue({ batch_id: "duplicate-batch", status: "completed", counts: { added: 0, already_added: 1, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "already_added", message: "Already added", member_id: "existing-member" }] });
  const onOpenMember = vi.fn(), user = userEvent.setup();
  render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} />);
  await enterSources(user, "D:/old");
  await user.click(screen.getByRole("button", { name: "Check Folder" }));
  await screen.findByRole("button", { name: "Confirm Import" });
  await user.click(screen.getByRole("button", { name: "Confirm Import" }));
  await user.click(await screen.findByRole("button", { name: "Open Force test" }));
  expect(onOpenMember).toHaveBeenCalledWith("existing-member");
  expect(screen.getByRole("button", { name: "View Projects" })).toHaveProperty("disabled", false);
});
