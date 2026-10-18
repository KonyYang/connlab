import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { LegacyProjectPreview } from "./LegacyProjectPreview";
import { pickLegacyProjectDirectory, previewLegacyProjects, planLegacyRegistration, importLegacyProjects, type LegacyProjectPreviewResult } from "../../api/legacyProjects";

vi.mock("../../api/legacyProjects", () => ({
  pickLegacyProjectDirectory: vi.fn(), previewLegacyProjects: vi.fn(),
  planLegacyRegistration: vi.fn(), importLegacyProjects: vi.fn(),
}));

const result: LegacyProjectPreviewResult = {
  read_only: true, scanned_folders: 4, duplicate_roots: 1, truncated: false, diagnostics: [],
  projects: [
    { folder: "D:/old/DL-2021-01-030A1", number: "DL-2021-01-030A1", name: "Force test", status: "ready", notes: [], duplicate_folders: [], duplicate_count: 0 },
    { folder: "D:/old/DL-2026-07-013A", number: "DL-2026-07-013A", name: "Cable test", status: "review", notes: ["Conflicting numbers in the folder or legacy files"], duplicate_folders: [], duplicate_count: 0 },
  ],
};

describe("LegacyProjectPreview", () => {
  beforeEach(() => { vi.resetAllMocks(); });

  it("previews without writing and requires a registration check and explicit confirmation before import", async () => {
    const user = userEvent.setup();
    vi.mocked(pickLegacyProjectDirectory).mockResolvedValue("D:/old");
    vi.mocked(previewLegacyProjects).mockResolvedValue(result);
    vi.mocked(planLegacyRegistration).mockResolvedValue({ projects: result.projects.map(item => ({ ...item, fingerprint: "checked", can_keep_separate: item.status === "review" })) });
    vi.mocked(importLegacyProjects).mockResolvedValue({ counts: { added: 1, already_added: 0, review: 0, failed: 0 }, items: [] });
    const viewImported = vi.fn();
    render(<LegacyProjectPreview onBack={vi.fn()} onViewImported={viewImported} />);
    const chooseButton = screen.getByRole("button", { name: "Choose Folder" });
    expect(chooseButton.title).toContain("up to 20 locations");
    expect(screen.queryByText(chooseButton.title)).toBeNull();
    expect(screen.getByRole("button", { name: "Start Preview" }).title).toContain("Read-only preview");
    await user.click(chooseButton);
    await user.click(screen.getByRole("button", { name: "Start Preview" }));
    const table = await screen.findByRole("table", { name: "Legacy project preview" });
    expect(within(table).getByText("Force test")).toBeTruthy();
    expect(screen.getByLabelText("Select Force test").getAttribute("type")).toBe("checkbox");
    expect((screen.getByLabelText("Select Force test") as HTMLInputElement).checked).toBe(true);
    expect((screen.getByLabelText("Select Cable test") as HTMLInputElement).checked).toBe(false);
    expect(screen.getByText("Conflicting numbers in the folder or legacy files")).toBeTruthy();
    expect(screen.getByText(/1 selected/)).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Import Selected" })).toBeNull();
    expect(previewLegacyProjects).toHaveBeenCalledWith(["D:/old"], expect.any(AbortSignal));
    await user.click(screen.getByRole("button", { name: "Check Registration" }));
    await user.click(await screen.findByRole("button", { name: "Import Selected" }));
    expect(importLegacyProjects).not.toHaveBeenCalled();
    expect(screen.getByRole("dialog", { name: "Confirm Import" })).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Confirm Import" }));
    expect(await screen.findByText(/1 added/)).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "View Imported Projects" }));
    expect(viewImported).toHaveBeenCalledOnce();
  });

  it("preserves chosen directories after failure and ignores a late response after stop", async () => {
    const user = userEvent.setup();
    let resolve!: (value: typeof result) => void;
    vi.mocked(pickLegacyProjectDirectory).mockResolvedValue("D:/old");
    vi.mocked(previewLegacyProjects).mockRejectedValueOnce(new Error("Temporarily unavailable"))
      .mockImplementationOnce(() => new Promise(done => { resolve = done; }));
    render(<LegacyProjectPreview onBack={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Choose Folder" }));
    await user.click(screen.getByRole("button", { name: "Start Preview" }));
    expect(await screen.findByRole("alert")).toHaveProperty("textContent", "Temporarily unavailable");
    expect(screen.getByText("D:/old")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Start Preview" }));
    await user.click(screen.getByRole("button", { name: "Stop Preview" }));
    await act(async () => { resolve(result); });
    expect(screen.queryByRole("table")).toBeNull();
    expect(screen.getByText(/Preview stopped/)).toBeTruthy();
  });

  it("keeps registered folders unselectable and requires Keep Separate for conflicting folders", async () => {
    const user = userEvent.setup();
    vi.mocked(pickLegacyProjectDirectory).mockResolvedValue("D:/old");
    vi.mocked(previewLegacyProjects).mockResolvedValue(result);
    vi.mocked(planLegacyRegistration).mockResolvedValue({ projects: result.projects.map((item, index) => ({ ...item, status: index === 0 ? "already_added" : "review", fingerprint: "checked", can_keep_separate: index === 1 })) });
    render(<LegacyProjectPreview onBack={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Choose Folder" }));
    await user.click(screen.getByRole("button", { name: "Start Preview" }));
    await user.click(await screen.findByRole("button", { name: "Check Registration" }));
    expect(await screen.findByText("Already Added")).toBeTruthy();
    expect(screen.getByRole("checkbox", { name: "Select Force test" })).toHaveProperty("disabled", true);
    expect(screen.getByRole("checkbox", { name: "Select Cable test" })).toHaveProperty("disabled", true);
    await user.click(screen.getByRole("checkbox", { name: "Keep Separate" }));
    expect(screen.getByRole("checkbox", { name: "Select Cable test" })).toHaveProperty("checked", true);
    expect(screen.getByRole("button", { name: "Import Selected" })).toHaveProperty("disabled", false);
    await user.click(screen.getByRole("checkbox", { name: "Keep Separate" }));
    expect(screen.getByRole("checkbox", { name: "Select Cable test" })).toHaveProperty("checked", false);
  });

  it("picker cancellation is idle, manual paths work, and a changed root invalidates results", async () => {
    const user = userEvent.setup();
    vi.mocked(pickLegacyProjectDirectory).mockResolvedValue(null);
    vi.mocked(previewLegacyProjects).mockResolvedValue({ ...result, truncated: true });
    render(<LegacyProjectPreview onBack={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "Choose Folder" }));
    expect(previewLegacyProjects).not.toHaveBeenCalled();
    await user.click(screen.getByText("Enter Folder Path Manually"));
    await user.type(screen.getByLabelText("Folder Path"), "D:/old");
    await user.click(screen.getByRole("button", { name: "Add Folder" }));
    await user.click(screen.getByRole("button", { name: "Start Preview" }));
    expect(await screen.findByText(/Incomplete results/)).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Remove D:/old" }));
    expect(screen.queryByRole("table")).toBeNull();
  });
});
