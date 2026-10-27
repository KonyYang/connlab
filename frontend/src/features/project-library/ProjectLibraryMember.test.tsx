import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProjectLibraryMember } from "./ProjectLibraryMember";
import { PortableCoverage, PortableRestore } from "./PortableRestore";
import * as api from "../../api/projectLibrary";

vi.mock("../../api/projectLibrary", () => ({
  getLibraryMember: vi.fn(), getLibraryFiles: vi.fn(), openLibraryFolder: vi.fn(), getPortableInfo: vi.fn(),
  planLibraryTitle: vi.fn(), updateLibraryTitle: vi.fn(), planLibraryLocation: vi.fn(), updateLibraryLocation: vi.fn(),
  preparePortableProject: vi.fn(), planLibraryTakeover: vi.fn(), takeoverLibraryProject: vi.fn(), pickLibraryFolder: vi.fn(),
  inspectPortableProject: vi.fn(), planPortableRestore: vi.fn(), restorePortableProject: vi.fn(),
}));
const member: api.LibraryMember = { member_id: "member-1", project_id: null, ltr_number: "DL-2026-09-032", title: "CPI-450", folder_path: "D:/library/DL-2026-09-032 CPI-450", revision: 1, batch_id: "batch-1", snapshot_status: "missing", snapshot_created_at: null, warnings: [], can_continue: false };
const portable: api.PortableInfo = { status: "stale", fingerprint: "data-now", created_at: "2026-10-26T08:00:00Z", format_version: 1, record_counts: { projects: 1, confirmed_matrix_versions: 2, result_dataset_revisions: 1 }, file_count: 8, warnings: ["Project data changed after this snapshot."], blockers: [] };
const restore: api.PortableRestorePlan = { plan_id: "restore-1", fingerprint: "restore-proof", project_id: "project-1", ltr_number: "DL-2026-09-032", title: "CPI-450", source_path: "E:/received", target_path: "D:/library/CPI-450", status: "ready", created_at: "2026-10-26T08:00:00Z", record_counts: { projects: 1, confirmed_matrix_versions: 2 }, file_count: 8, warnings: [], blockers: [] };

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(api.getLibraryMember).mockResolvedValue(member);
  vi.mocked(api.getLibraryFiles).mockResolvedValue({ items: [{ name: "Test results", relative_path: "Test results", is_directory: true, size_bytes: null }], warnings: [] });
  vi.mocked(api.getPortableInfo).mockResolvedValue(portable);
  vi.mocked(api.inspectPortableProject).mockResolvedValue(restore);
  vi.mocked(api.planPortableRestore).mockResolvedValue(restore);
});

describe("Library project management", () => {
  it("clears pending local operations when navigating to a different member and ignores a late title plan", async () => {
    const user = userEvent.setup();
    let resolvePlan!: (value: api.LibraryLocationPlan) => void;
    vi.mocked(api.getLibraryMember).mockResolvedValueOnce(member).mockResolvedValueOnce({ ...member, member_id: "member-2", title: "Other project" });
    vi.mocked(api.planLibraryTitle).mockImplementation(() => new Promise(resolve => { resolvePlan = resolve; }));
    const view = render(<ProjectLibraryMember memberId="member-1" onBack={vi.fn()} onOpenProject={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Edit Title" }));
    await user.click(screen.getByRole("button", { name: "Review Title" }));
    view.rerender(<ProjectLibraryMember memberId="member-2" onBack={vi.fn()} onOpenProject={vi.fn()} />);
    await screen.findByRole("heading", { name: "Other project" });
    expect(screen.getByRole("button", { name: "Edit Title" })).toHaveProperty("disabled", false);
    await act(async () => { resolvePlan({ plan_id: "old", fingerprint: "old", source_path: "D:/old", target_path: "D:/changed", warnings: [] }); });
    expect(screen.queryByRole("dialog", { name: "Confirm Title" })).toBeNull();
  });

  it("requires takeover before opening test workspaces when a project identity is not yet usable", async () => {
    vi.mocked(api.getLibraryMember).mockResolvedValue({ ...member, project_id: "identity-hint", can_continue: false });
    const openProject = vi.fn();
    render(<ProjectLibraryMember memberId="member-1" onBack={vi.fn()} onOpenProject={openProject} />);
    expect(await screen.findByRole("button", { name: "Continue Testing" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Matrix" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Report" })).toBeNull();
    expect(openProject).not.toHaveBeenCalled();
  });

  it("keeps the LTR read-only and confirms a reviewed title change without hiding changed-file warnings", async () => {
    const user = userEvent.setup();
    vi.mocked(api.planLibraryTitle).mockResolvedValue({ plan_id: "rename-1", fingerprint: "rename-proof", source_path: member.folder_path, target_path: "D:/library/DL-2026-09-032 Revised", warnings: ["A referenced file is missing; project identity is unchanged."] });
    vi.mocked(api.updateLibraryTitle).mockResolvedValue({ ...member, title: "Revised", revision: 2 });
    render(<ProjectLibraryMember memberId="member-1" onBack={vi.fn()} onOpenProject={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Edit Title" }));
    const title = screen.getByLabelText("Project title");
    await user.clear(title); await user.type(title, "Revised");
    await user.click(screen.getByRole("button", { name: "Review Title" }));
    expect(await screen.findByText("A referenced file is missing; project identity is unchanged.")).toBeTruthy();
    expect(api.updateLibraryTitle).not.toHaveBeenCalled();
    expect(screen.queryByRole("textbox", { name: "LTR" })).toBeNull();
    await user.click(screen.getByRole("button", { name: "Confirm Title" }));
    expect(await screen.findByRole("heading", { name: "Revised" })).toBeTruthy();
    expect(screen.getByText("DL-2026-09-032")).toBeTruthy();
    expect(api.updateLibraryTitle).toHaveBeenCalledWith("member-1", { plan_id: "rename-1", fingerprint: "rename-proof" });
  });

  it("refreshes ordinary files and explicitly updates a stale portable snapshot", async () => {
    const user = userEvent.setup();
    vi.mocked(api.preparePortableProject).mockResolvedValue({ ...portable, status: "current", warnings: [] });
    render(<ProjectLibraryMember memberId="member-1" onBack={vi.fn()} onOpenProject={vi.fn()} />);
    expect(await screen.findByText("Project data changed after this snapshot.")).toBeTruthy();
    vi.mocked(api.getLibraryFiles).mockResolvedValue({ items: [{ name: "New measurement.xlsx", relative_path: "New measurement.xlsx", is_directory: false, size_bytes: 2048 }], warnings: ["Old report is missing."] });
    await user.click(screen.getByRole("button", { name: "Refresh Files" }));
    expect(await screen.findByText("New measurement.xlsx")).toBeTruthy();
    expect(screen.getByText("Old report is missing.")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Prepare to Take" }));
    expect(api.preparePortableProject).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Confirm Snapshot" }));
    expect(await screen.findByText("Ready to Take")).toBeTruthy();
    expect(api.preparePortableProject).toHaveBeenCalledWith("member-1", "data-now");
  });

  it("refreshes snapshot eligibility and files immediately after takeover", async () => {
    const user = userEvent.setup();
    const blocker = "Take over this project before preparing test-data portability.";
    vi.mocked(api.getPortableInfo).mockResolvedValueOnce({ ...portable, status: "unavailable", created_at: null, blockers: [blocker], record_counts: {}, file_count: 0 }).mockResolvedValue({ ...portable, status: "missing", created_at: null, fingerprint: "after-takeover", blockers: [], warnings: [] });
    vi.mocked(api.planLibraryTakeover).mockResolvedValue({ plan_id: "take-1", fingerprint: "take-proof", project_id: null, ltr_number: member.ltr_number, title: member.title, status: "needs_information", missing: ["Confirm sample information"], warnings: [], blockers: [] });
    vi.mocked(api.takeoverLibraryProject).mockResolvedValue({ member: { ...member, project_id: "project-1", can_continue: true }, project_id: "project-1", warnings: [] });
    render(<ProjectLibraryMember memberId="member-1" onBack={vi.fn()} onOpenProject={vi.fn()} />);
    expect(await screen.findByText(blocker)).toBeTruthy();
    vi.mocked(api.getLibraryFiles).mockResolvedValue({ items: [{ name: "Project data", relative_path: "Project data", is_directory: true, size_bytes: null }], warnings: [] });
    await user.click(screen.getByRole("button", { name: "Continue Testing" }));
    await user.click(await screen.findByRole("button", { name: "Confirm Takeover" }));
    expect(await screen.findByText("No Snapshot")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Prepare to Take" })).toHaveProperty("disabled", false);
    expect(screen.queryByText(blocker)).toBeNull();
    expect(screen.getByText("Project data")).toBeTruthy();
    expect(screen.getByText(/Data to Prepare/)).toBeTruthy();
  });

  it("keeps saved coverage separate from new files until the latest snapshot is prepared", async () => {
    const user = userEvent.setup();
    vi.mocked(api.getPortableInfo).mockResolvedValue({ ...portable, record_counts: { result_dataset_revisions: 1 }, file_count: 8, warnings: [] });
    vi.mocked(api.preparePortableProject).mockResolvedValue({ ...portable, status: "current", record_counts: { result_dataset_revisions: 2 }, file_count: 9, warnings: [] });
    render(<ProjectLibraryMember memberId="member-1" onBack={vi.fn()} onOpenProject={vi.fn()} />);
    expect(await screen.findByText(/Saved Snapshot Data.*8 files/)).toBeTruthy();
    vi.mocked(api.getLibraryFiles).mockResolvedValue({ items: [{ name: "New measurement.xlsx", relative_path: "New measurement.xlsx", is_directory: false, size_bytes: 2048 }], warnings: [] });
    await user.click(screen.getByRole("button", { name: "Refresh Files" }));
    expect(await screen.findByText("New measurement.xlsx")).toBeTruthy();
    expect(screen.getByText("1 records")).toBeTruthy();
    expect(screen.getByText(/Saved Snapshot Data.*8 files/)).toBeTruthy();
    expect(screen.getByText("Saved snapshot does not include the latest project changes. Prepare again before taking this project to another computer.")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Prepare to Take" }));
    await user.click(screen.getByRole("button", { name: "Confirm Snapshot" }));
    expect(await screen.findByText(/Saved Snapshot Data.*9 files/)).toBeTruthy();
    expect(screen.getByText("2 records")).toBeTruthy();
    expect(screen.queryByText("Saved snapshot does not include the latest project changes. Prepare again before taking this project to another computer.")).toBeNull();
  });

  it.each(["title", "location"] as const)("refreshes snapshot coverage and file browsing after a confirmed %s change", async kind => {
    const user = userEvent.setup();
    const plan = { plan_id: "change-1", fingerprint: "change-proof", source_path: member.folder_path, target_path: "D:/library/Revised", warnings: [] };
    vi.mocked(api.planLibraryTitle).mockResolvedValue(plan);
    vi.mocked(api.planLibraryLocation).mockResolvedValue(plan);
    vi.mocked(api.updateLibraryTitle).mockResolvedValue({ ...member, title: "Revised" });
    vi.mocked(api.updateLibraryLocation).mockResolvedValue({ ...member, folder_path: plan.target_path });
    const initialPortable = { ...portable, status: "current" as const, warnings: [] };
    vi.mocked(api.getPortableInfo).mockResolvedValueOnce(initialPortable).mockResolvedValue({ ...portable, warnings: ["Review the updated project before preparing again."] });
    render(<ProjectLibraryMember memberId="member-1" onBack={vi.fn()} onOpenProject={vi.fn()} />);
    expect(await screen.findByText("Ready to Take")).toBeTruthy();
    const label = kind === "title" ? "Title" : "Location";
    await user.click(screen.getByRole("button", { name: kind === "title" ? "Edit Title" : "Locate Folder" }));
    const input = screen.getByRole("textbox");
    await user.clear(input); await user.type(input, kind === "title" ? "Revised" : plan.target_path);
    await user.click(screen.getByRole("button", { name: `Review ${label}` }));
    vi.mocked(api.getLibraryFiles).mockResolvedValue({ items: [{ name: "Updated files", relative_path: "Updated files", is_directory: true, size_bytes: null }], warnings: [] });
    await user.click(await screen.findByRole("button", { name: `Confirm ${label}` }));
    expect(await screen.findByText("Needs Update")).toBeTruthy();
    expect(screen.getByText("Review the updated project before preparing again.")).toBeTruthy();
    expect(screen.getByText("Updated files")).toBeTruthy();
  });

  it("ignores snapshot and file refreshes from a takeover after navigation to another member", async () => {
    const user = userEvent.setup();
    let resolveSnapshot!: (value: api.PortableInfo) => void;
    let resolveFiles!: (value: api.LibraryFiles) => void;
    vi.mocked(api.getLibraryMember).mockResolvedValueOnce(member).mockResolvedValueOnce({ ...member, member_id: "member-2", title: "Other project" });
    vi.mocked(api.getPortableInfo).mockResolvedValueOnce(portable).mockImplementationOnce(() => new Promise(resolve => { resolveSnapshot = resolve; })).mockResolvedValue({ ...portable, status: "current", file_count: 20, warnings: [] });
    vi.mocked(api.getLibraryFiles).mockResolvedValueOnce({ items: [], warnings: [] }).mockImplementationOnce(() => new Promise(resolve => { resolveFiles = resolve; })).mockResolvedValue({ items: [], warnings: [] });
    vi.mocked(api.planLibraryTakeover).mockResolvedValue({ plan_id: "take-1", fingerprint: "take-proof", project_id: null, ltr_number: member.ltr_number, title: member.title, status: "ready", missing: [], warnings: [], blockers: [] });
    vi.mocked(api.takeoverLibraryProject).mockResolvedValue({ member: { ...member, project_id: "project-1", can_continue: true }, project_id: "project-1", warnings: [] });
    const view = render(<ProjectLibraryMember memberId="member-1" onBack={vi.fn()} onOpenProject={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Continue Testing" }));
    await user.click(await screen.findByRole("button", { name: "Confirm Takeover" }));
    await screen.findByRole("button", { name: "Matrix" });
    view.rerender(<ProjectLibraryMember memberId="member-2" onBack={vi.fn()} onOpenProject={vi.fn()} />);
    await screen.findByRole("heading", { name: "Other project" });
    await act(async () => { resolveSnapshot({ ...portable, warnings: ["Old project warning"] }); resolveFiles({ items: [{ name: "Old project file", relative_path: "old", is_directory: false, size_bytes: 1 }], warnings: [] }); });
    expect(screen.queryByText("Old project warning")).toBeNull();
    expect(screen.queryByText("Old project file")).toBeNull();
    expect(screen.getByText(/Saved Snapshot Data.*20 files/)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Edit Title" })).toHaveProperty("disabled", false);
  });

  it("shows missing facts before takeover and then uses the existing Matrix and Report routes", async () => {
    const user = userEvent.setup();
    const onOpenProject = vi.fn();
    vi.mocked(api.planLibraryTakeover).mockResolvedValue({ plan_id: "take-1", fingerprint: "take-proof", project_id: null, ltr_number: member.ltr_number, title: member.title, status: "needs_information", missing: ["Confirm sample information"], warnings: ["Existing LTR is a hint until checked."], blockers: [] });
    vi.mocked(api.takeoverLibraryProject).mockResolvedValue({ member: { ...member, project_id: "project-1", can_continue: true }, project_id: "project-1", warnings: [] });
    render(<ProjectLibraryMember memberId="member-1" onBack={vi.fn()} onOpenProject={onOpenProject} />);
    await user.click(await screen.findByRole("button", { name: "Continue Testing" }));
    expect(await screen.findByText("Confirm sample information")).toBeTruthy();
    expect(api.takeoverLibraryProject).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Confirm Takeover" }));
    await user.click(await screen.findByRole("button", { name: "Matrix" }));
    expect(onOpenProject).toHaveBeenCalledWith("project-1", "matrix");
    await user.click(screen.getByRole("button", { name: "Report" }));
    expect(onOpenProject).toHaveBeenCalledWith("project-1", "report");
  });
});

describe("Portable project restore", () => {
  it("shows the carried data and confirms restore before opening the recovered member", async () => {
    const user = userEvent.setup();
    const onOpenMember = vi.fn();
    vi.mocked(api.restorePortableProject).mockResolvedValue({ status: "restored", member: { ...member, project_id: "project-1" }, warnings: [] });
    render(<PortableRestore onOpenMember={onOpenMember} />);
    await user.click(screen.getByText("Take Over a Portable Project"));
    await user.type(screen.getByLabelText("Portable project folder"), "E:/received");
    await user.click(screen.getByRole("button", { name: "Inspect Project" }));
    expect(await screen.findByText(/8 files/)).toBeTruthy();
    expect(screen.getByText("Matrix")).toBeTruthy();
    expect(api.restorePortableProject).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Review Restore" }));
    await user.click(await screen.findByRole("button", { name: "Confirm Restore" }));
    expect(api.restorePortableProject).toHaveBeenCalledWith({ plan_id: "restore-1", fingerprint: "restore-proof" });
    await user.click(await screen.findByRole("button", { name: "Open Recovered Project" }));
    expect(onOpenMember).toHaveBeenCalledWith("member-1");
  });

  it("blocks conflicting data and invalidates an inspection when the folder changes", async () => {
    const user = userEvent.setup();
    vi.mocked(api.inspectPortableProject).mockResolvedValue({ ...restore, status: "conflict", blockers: ["Both copies contain changes. Choose the correct source before restoring."] });
    render(<PortableRestore onOpenMember={vi.fn()} />);
    await user.click(screen.getByText("Take Over a Portable Project"));
    await user.type(screen.getByLabelText("Portable project folder"), "E:/received");
    await user.click(screen.getByRole("button", { name: "Inspect Project" }));
    expect(await screen.findByText("Both copies contain changes. Choose the correct source before restoring.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Review Restore" })).toHaveProperty("disabled", true);
    await user.type(screen.getByLabelText("Portable project folder"), "/other");
    expect(screen.queryByRole("button", { name: "Review Restore" })).toBeNull();
    expect(api.restorePortableProject).not.toHaveBeenCalled();
  });
});


it("summarizes carried data by business category and keeps storage names in collapsed diagnostics", () => {
  render(<PortableCoverage counts={{ projects: 1, confirmed_matrix_versions: 2, result_dataset_revisions: 3, report_draft_revisions: 4, file_assets: 5 }} fileCount={8} />);
  expect(screen.getByText("Matrix")).toBeTruthy();
  expect(screen.getByText("Test Results")).toBeTruthy();
  expect(screen.getByText("Reports")).toBeTruthy();
  expect(screen.getByText("Source Materials")).toBeTruthy();
  expect(screen.getByText("Snapshot Diagnostics").closest("details")).toHaveProperty("open", false);
});
