import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useMatrixEditorXlsxExport } from "./useMatrixEditorXlsxExport";

const request = {
  source: "matrix_editor_current_ui_state" as const,
  project_reference: "DL-1",
  groups: [],
  rows: [],
};

function installDownloadSpies() {
  const create = vi.fn(() => "blob:live");
  const revoke = vi.fn();
  Object.defineProperty(URL, "createObjectURL", { configurable: true, value: create });
  Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revoke });
  const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  return { click, create, revoke };
}

describe("useMatrixEditorXlsxExport", () => {
  it("keeps the existing draft download when publication preview selects download mode", async () => {
    const apis = {
      preview: vi.fn().mockResolvedValue({
        mode: "download", status: "ready", existing_file: false,
        existing_modified_at: null, blockers: [], preview_token: "draft-token",
      }),
      publish: vi.fn(),
      download: vi.fn().mockResolvedValue({ blob: new Blob(["xlsx"]), fileName: "live.xlsx" }),
    };
    const { click, create, revoke } = installDownloadSpies();
    const { result } = renderHook(() => useMatrixEditorXlsxExport("p1", apis));

    await act(() => result.current.exportSnapshot(request));

    expect(apis.preview).toHaveBeenCalledWith("p1", request);
    expect(apis.download).toHaveBeenCalledWith("p1", request);
    expect(apis.publish).not.toHaveBeenCalled();
    expect(click).toHaveBeenCalledOnce();
    expect(create).toHaveBeenCalledOnce();
    expect(revoke).toHaveBeenCalledWith("blob:live");
    expect(result.current.message).toBe("Matrix Draft downloaded.");
  });

  it("publishes a matching confirmed Matrix directly to Source Book", async () => {
    const apis = {
      preview: vi.fn().mockResolvedValue({
        mode: "official", status: "ready", existing_file: false,
        existing_modified_at: null, blockers: [], preview_token: "official-token",
      }),
      publish: vi.fn().mockResolvedValue({ file_name: "DL-1 Matrix.xlsx", archive_path: null }),
      download: vi.fn(),
    };
    const { result } = renderHook(() => useMatrixEditorXlsxExport("p1", apis));

    await act(() => result.current.exportSnapshot(request));

    expect(apis.publish).toHaveBeenCalledWith("p1", {
      ...request, preview_token: "official-token", conflict_action: "none",
    });
    expect(apis.download).not.toHaveBeenCalled();
    expect(result.current.message).toBe("Saved DL-1 Matrix.xlsx to Source Book.");
  });

  it("waits for an explicit choice before replacing an existing formal Matrix", async () => {
    const apis = {
      preview: vi.fn().mockResolvedValue({
        mode: "official", status: "conflict", existing_file: true,
        existing_modified_at: "2026-08-29T10:30:00+08:00", blockers: [],
        preview_token: "conflict-token",
      }),
      publish: vi.fn().mockResolvedValue({
        file_name: "DL-1 Matrix.xlsx", archive_path: "history.xlsx",
      }),
      download: vi.fn(),
    };
    const { result } = renderHook(() => useMatrixEditorXlsxExport("p1", apis));

    await act(() => result.current.exportSnapshot(request));
    expect(result.current.conflict?.preview_token).toBe("conflict-token");
    expect(apis.publish).not.toHaveBeenCalled();

    await act(() => result.current.resolveConflict("archive"));
    expect(apis.publish).toHaveBeenCalledWith("p1", {
      ...request, preview_token: "conflict-token", conflict_action: "archive",
    });
    expect(result.current.conflict).toBeNull();
    expect(result.current.message).toBe(
      "Saved DL-1 Matrix.xlsx; archived the previous file in History."
    );
  });

  it("exposes an error and allows retry", async () => {
    const apis = {
      preview: vi.fn().mockRejectedValueOnce(new Error("offline")).mockResolvedValueOnce({
        mode: "download", status: "ready", existing_file: false,
        existing_modified_at: null, blockers: [], preview_token: "retry-token",
      }),
      publish: vi.fn(),
      download: vi.fn().mockResolvedValue({ blob: new Blob(["xlsx"]), fileName: "live.xlsx" }),
    };
    installDownloadSpies();
    const { result } = renderHook(() => useMatrixEditorXlsxExport("p1", apis));

    await act(() => result.current.exportSnapshot(request));
    expect(result.current.error).toBe("offline");
    await act(() => result.current.exportSnapshot(request));
    expect(apis.preview).toHaveBeenCalledTimes(2);
    expect(result.current.error).toBe("");
  });
});
