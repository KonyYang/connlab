import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useMatrixEditorXlsxExport } from "./useMatrixEditorXlsxExport";

const request = {
  source: "matrix_editor_current_ui_state" as const,
  project_reference: "DL-1",
  groups: [],
  rows: [],
};

describe("useMatrixEditorXlsxExport", () => {
  it("downloads one snapshot and revokes the Blob URL", async () => {
    const api = vi.fn().mockResolvedValue({ blob: new Blob(["xlsx"]), fileName: "live.xlsx" });
    const create = vi.fn(() => "blob:live");
    const revoke = vi.fn();
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: create });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revoke });
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    const { result } = renderHook(() => useMatrixEditorXlsxExport("p1", api));
    await act(() => result.current.exportSnapshot(request));
    expect(api).toHaveBeenCalledOnce();
    expect(click).toHaveBeenCalledOnce();
    expect(create).toHaveBeenCalledOnce();
    expect(revoke).toHaveBeenCalledWith("blob:live");
    expect(result.current.busy).toBe(false);
  });

  it("exposes an error and allows retry", async () => {
    const api = vi.fn()
      .mockRejectedValueOnce(new Error("offline"))
      .mockResolvedValueOnce({ blob: new Blob(["xlsx"]), fileName: "live.xlsx" });
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: vi.fn(() => "blob:retry") });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: vi.fn() });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    const { result } = renderHook(() => useMatrixEditorXlsxExport("p1", api));
    await act(() => result.current.exportSnapshot(request));
    expect(result.current.error).toBe("offline");
    await act(() => result.current.exportSnapshot(request));
    expect(api).toHaveBeenCalledTimes(2);
    expect(result.current.error).toBe("");
  });
});
