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
    { folder: "D:/old/DL-2026-07-013A", number: "DL-2026-07-013A", name: "Cable test", status: "review", notes: ["目录和旧资料编号不一致"], duplicate_folders: [], duplicate_count: 0 },
  ],
};

describe("LegacyProjectPreview", () => {
  beforeEach(() => { vi.resetAllMocks(); });

  it("picks a directory, previews a batch, selects only clear projects and offers no import action", async () => {
    const user = userEvent.setup();
    vi.mocked(pickLegacyProjectDirectory).mockResolvedValue("D:/old");
    vi.mocked(previewLegacyProjects).mockResolvedValue(result);
    render(<LegacyProjectPreview onBack={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "选择目录" }));
    await user.click(screen.getByRole("button", { name: "开始预览" }));
    const table = await screen.findByRole("table", { name: "旧项目预览" });
    expect(within(table).getByText("Force test")).toBeTruthy();
    expect(screen.getByLabelText("选择 Force test").getAttribute("type")).toBe("checkbox");
    expect((screen.getByLabelText("选择 Force test") as HTMLInputElement).checked).toBe(true);
    expect((screen.getByLabelText("选择 Cable test") as HTMLInputElement).checked).toBe(false);
    expect(screen.getByText("目录和旧资料编号不一致")).toBeTruthy();
    expect(screen.getByText(/已选 1 个/)).toBeTruthy();
    expect(screen.queryByRole("button", { name: /确认导入|正式导入|导入已选/ })).toBeNull();
    expect(previewLegacyProjects).toHaveBeenCalledWith(["D:/old"], expect.any(AbortSignal));
  });

  it("preserves chosen directories after failure and ignores a late response after stop", async () => {
    const user = userEvent.setup();
    let resolve!: (value: typeof result) => void;
    vi.mocked(pickLegacyProjectDirectory).mockResolvedValue("D:/old");
    vi.mocked(previewLegacyProjects).mockRejectedValueOnce(new Error("暂时无法读取"))
      .mockImplementationOnce(() => new Promise(done => { resolve = done; }));
    render(<LegacyProjectPreview onBack={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "选择目录" }));
    await user.click(screen.getByRole("button", { name: "开始预览" }));
    expect(await screen.findByRole("alert")).toHaveProperty("textContent", "暂时无法读取");
    expect(screen.getByText("D:/old")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "开始预览" }));
    await user.click(screen.getByRole("button", { name: "停止预览" }));
    await act(async () => { resolve(result); });
    expect(screen.queryByRole("table")).toBeNull();
    expect(screen.getByText(/已停止预览/)).toBeTruthy();
  });

  it("picker cancellation is idle, manual paths work, and a changed root invalidates results", async () => {
    const user = userEvent.setup();
    vi.mocked(pickLegacyProjectDirectory).mockResolvedValue(null);
    vi.mocked(previewLegacyProjects).mockResolvedValue({ ...result, truncated: true });
    render(<LegacyProjectPreview onBack={vi.fn()} />);
    await user.click(screen.getByRole("button", { name: "选择目录" }));
    expect(previewLegacyProjects).not.toHaveBeenCalled();
    await user.click(screen.getByText("手动填写目录"));
    await user.type(screen.getByLabelText("目录位置"), "D:/old");
    await user.click(screen.getByRole("button", { name: "添加目录" }));
    await user.click(screen.getByRole("button", { name: "开始预览" }));
    expect(await screen.findByText(/结果不完整/)).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "移除 D:/old" }));
    expect(screen.queryByRole("table")).toBeNull();
  });
});
