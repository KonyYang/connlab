import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProjectLibraryImport } from "./ProjectLibraryImport";
import * as api from "../../api/projectLibrary";

vi.mock("../../api/projectLibrary", () => ({
  getLibraryRuntime: vi.fn(), scanLibrarySources: vi.fn(), planLibraryIntake: vi.fn(), listLibraryMembers: vi.fn(),
  startLibraryBatch: vi.fn(), getLibraryBatch: vi.fn(), resumeLibraryBatch: vi.fn(),
  pickLibraryFolder: vi.fn(), inspectPortableProject: vi.fn(), planPortableRestore: vi.fn(), restorePortableProject: vi.fn(),
}));
const plan = {
  plan_id: "plan-1", fingerprint: "verified", warnings: [], items: [
    { source_path: "D:/old/Force", target_path: "D:/managed/Force", title: "Force test", ltr_number: "DL-2021-01-030A1", status: "ready", warnings: [], can_keep_separate: false },
    { source_path: "D:/old/Cable", target_path: "D:/managed/Cable", title: "Cable test", ltr_number: "DL-2026-07-013A", status: "conflict", warnings: ["Another project uses this LTR."], can_keep_separate: true },
  ],
};

beforeEach(() => {
  vi.resetAllMocks();
  localStorage.clear();
  vi.mocked(api.getLibraryRuntime).mockResolvedValue({ library_root: "D:/managed", projects_root: "D:/managed/projects", data_root: "D:/managed/data", database_path: "D:/managed/data/connlab.sqlite3", configured: true, format_version: 1 });
  vi.mocked(api.scanLibrarySources).mockResolvedValue({ items: plan.items.map(row => ({ source_path: row.source_path, title: row.title, ltr_number: row.ltr_number, kind: "project", warnings: [], child_folders: [] })), warnings: [], truncated: false });
  vi.mocked(api.planLibraryIntake).mockResolvedValue(plan as api.LibraryIntakePlan);
  vi.mocked(api.startLibraryBatch).mockResolvedValue({ batch_id: "batch-1", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "added", message: "Added", member_id: "member-1" }] });
});

describe("ProjectLibraryImport", () => {
  it("does not let late previous-batch recovery replace a newly reviewed source selection", async () => {
    let finish!: (value: api.LibraryBatch) => void;
    vi.mocked(api.getLibraryBatch).mockImplementation(() => new Promise(resolve => { finish = resolve; }));
    localStorage.setItem("connlab.projectLibrary.lastBatch:D:/managed/projects", "old-batch");
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await screen.findByText("D:/managed/projects");
    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Source paths"), "D:/fresh");
    await user.click(screen.getByRole("button", { name: "Review Projects" }));
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
    await user.type(screen.getByLabelText("Source paths"), "D:/old");
    await user.click(screen.getByRole("button", { name: "Review Projects" }));
    await user.click(await screen.findByRole("button", { name: "Add Selected" }));
    await user.click(screen.getByRole("button", { name: "Confirm Add" }));
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
    vi.mocked(api.listLibraryMembers).mockResolvedValue({ items: [{ member_id: "existing-1", project_id: "project-1", ltr_number: "DL-2026-09-032", title: "CPI-450", folder_path: "D:/managed/CPI", revision: 1, batch_id: null, snapshot_status: "current", snapshot_created_at: null, warnings: [], can_continue: true }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await user.type(screen.getByLabelText("Source paths"), "D:/loose/result.xlsx");
    await user.click(screen.getByRole("button", { name: "Review Projects" }));
    const assignment = await screen.findByLabelText("Assign result.xlsx");
    expect(api.planLibraryIntake).not.toHaveBeenCalled();
    await user.selectOptions(assignment, "existing-1");
    await user.click(screen.getByRole("button", { name: "Review File Assignments" }));
    await screen.findByRole("table", { name: "Projects to receive" });
    expect(api.planLibraryIntake).toHaveBeenCalledWith(["D:/loose/result.xlsx"], expect.any(AbortSignal), [{ source_path: "D:/loose/result.xlsx", target_member_id: "existing-1" }]);
  });

  it("checks the whole selection automatically and writes only after explicit confirmation", async () => {
    const user = userEvent.setup();
    const onOpenMember = vi.fn();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={onOpenMember} />);
    await user.type(screen.getByLabelText("Source paths"), "D:/old");
    await user.click(screen.getByRole("button", { name: "Review Projects" }));
    const table = await screen.findByRole("table", { name: "Projects to receive" });
    expect(within(table).getByText("Force test")).toBeTruthy();
    expect(screen.getByRole("checkbox", { name: "Select Force test" })).toHaveProperty("checked", true);
    expect(screen.getByRole("checkbox", { name: "Select Cable test" })).toHaveProperty("checked", false);
    expect(screen.getByText("Another project uses this LTR.")).toBeTruthy();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Add Selected" }));
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Add Selected" }));
    await user.click(screen.getByRole("button", { name: "Confirm Add" }));
    expect(await screen.findByText(/1 added/)).toBeTruthy();
    expect(api.startLibraryBatch).toHaveBeenCalledWith(expect.objectContaining({ batch_id: expect.stringMatching(/^[a-f0-9]{32}$/), plan_id: "plan-1", fingerprint: "verified", selected: ["D:/old/Force"], keep_separate: [] }));
    await user.click(screen.getByRole("button", { name: "Open Force test" }));
    expect(onOpenMember).toHaveBeenCalledWith("member-1");
  });

  it("requires a separate choice for number conflicts and invalidates results when sources change", async () => {
    const user = userEvent.setup();
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await user.type(screen.getByLabelText("Source paths"), "D:/old");
    await user.click(screen.getByRole("button", { name: "Review Projects" }));
    await screen.findByText("Force test");
    await user.click(screen.getByRole("checkbox", { name: "Keep Cable test separate" }));
    expect(screen.getByRole("checkbox", { name: "Select Cable test" })).toHaveProperty("checked", true);
    await user.type(screen.getByLabelText("Source paths"), "/different");
    expect(screen.queryByRole("table")).toBeNull();
    expect(screen.queryByRole("button", { name: "Add Selected" })).toBeNull();
    expect(api.startLibraryBatch).not.toHaveBeenCalled();
  });

  it("keeps failed batches available for an explicit retry", async () => {
    const user = userEvent.setup();
    vi.mocked(api.startLibraryBatch).mockResolvedValue({ batch_id: "batch-1", status: "interrupted", counts: { added: 0, already_added: 0, review: 0, failed: 1 }, items: [{ source_path: "D:/old/Force", status: "failed", message: "File is locked. Retry when available.", member_id: null }] });
    vi.mocked(api.resumeLibraryBatch).mockResolvedValue({ batch_id: "batch-1", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [{ source_path: "D:/old/Force", status: "added", message: "Added", member_id: "member-1" }] });
    render(<ProjectLibraryImport onBack={vi.fn()} onViewLibrary={vi.fn()} onOpenMember={vi.fn()} />);
    await user.type(screen.getByLabelText("Source paths"), "D:/old");
    await user.click(screen.getByRole("button", { name: "Review Projects" }));
    await user.click(await screen.findByRole("button", { name: "Add Selected" }));
    await user.click(screen.getByRole("button", { name: "Confirm Add" }));
    expect(await screen.findByText("File is locked. Retry when available.")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Resume Batch" }));
    expect(await screen.findByText(/1 added/)).toBeTruthy();
  });
});