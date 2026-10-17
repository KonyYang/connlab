import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { LegacyProjectPreview } from "./LegacyProjectPreview";
import { pickLegacyProjectDirectory, previewLegacyProjects, type LegacyProjectPreviewResult } from "../../api/legacyProjects";

vi.mock("../../api/legacyProjects", () => ({
  pickLegacyProjectDirectory: vi.fn(), previewLegacyProjects: vi.fn(),
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

  it("picks a directory, previews a batch, selects only clear projects and offers no import action", async () => {
    const user = userEvent.setup();
    vi.mocked(pickLegacyProjectDirectory).mockResolvedValue("D:/old");
    vi.mocked(previewLegacyProjects).mockResolvedValue(result);
    render(<LegacyProjectPreview onBack={vi.fn()} />);
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
    expect(screen.queryByRole("button", { name: /Confirm Import|Import Selected|Register Projects/i })).toBeNull();
    expect(previewLegacyProjects).toHaveBeenCalledWith(["D:/old"], expect.any(AbortSignal));
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
