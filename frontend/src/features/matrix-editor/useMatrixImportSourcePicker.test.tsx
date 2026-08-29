import { beforeEach, describe, expect, it, vi } from "vitest";

const apiMocks = vi.hoisted(() => ({ listProjectTestPlanSourceCandidates: vi.fn() }));
const bridgeMocks = vi.hoisted(() => ({
  hasMatrixImportSourcePicker: vi.fn(),
  pickMatrixImportSourceFromDesktop: vi.fn(),
}));

vi.mock("../../api/client", () => apiMocks);
vi.mock("../../desktop/pathPickerBridge", () => bridgeMocks);

import { chooseMatrixImportSource } from "./useMatrixImportSourcePicker";

describe("chooseMatrixImportSource", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    bridgeMocks.hasMatrixImportSourcePicker.mockReturnValue(true);
    apiMocks.listProjectTestPlanSourceCandidates.mockResolvedValue({
      view: "registered_assets",
      preferred_import_directory: "D:/projects/DL/Submitted Material",
    });
  });

  it("passes the projected directory to the desktop picker", async () => {
    bridgeMocks.pickMatrixImportSourceFromDesktop.mockResolvedValue("D:/projects/DL/Submitted Material/spec.pdf");
    await expect(chooseMatrixImportSource("P1")).resolves.toEqual({
      kind: "selected",
      path: "D:/projects/DL/Submitted Material/spec.pdf",
    });
    expect(bridgeMocks.pickMatrixImportSourceFromDesktop).toHaveBeenCalledWith(
      "D:/projects/DL/Submitted Material"
    );
  });

  it("keeps browser upload when the desktop bridge is unavailable", async () => {
    bridgeMocks.hasMatrixImportSourcePicker.mockReturnValue(false);
    apiMocks.listProjectTestPlanSourceCandidates.mockResolvedValue({
      view: "resolved_directory",
      source_title: "Submitted Material files",
      candidates: [{ candidate_id: "source-1", file_name: "matrix.docx" }],
      warnings: ["Review source"],
    });
    await expect(chooseMatrixImportSource("P1")).resolves.toEqual({
      kind: "browser",
      sourceTitle: "Submitted Material files",
      candidates: [{ candidate_id: "source-1", file_name: "matrix.docx" }],
      warnings: ["Review source"],
      error: null,
    });
    expect(apiMocks.listProjectTestPlanSourceCandidates).toHaveBeenCalledWith(
      "P1",
      "resolved_directory"
    );
  });

  it("opens the OS default when directory projection fails", async () => {
    apiMocks.listProjectTestPlanSourceCandidates.mockRejectedValue(new Error("offline"));
    bridgeMocks.pickMatrixImportSourceFromDesktop.mockResolvedValue(null);
    await expect(chooseMatrixImportSource("P1")).resolves.toEqual({ kind: "cancelled" });
    expect(bridgeMocks.pickMatrixImportSourceFromDesktop).toHaveBeenCalledWith(null);
  });

  it("preserves upload conversion fallback for legacy doc", async () => {
    bridgeMocks.pickMatrixImportSourceFromDesktop.mockResolvedValue("D:/source/spec.doc");
    await expect(chooseMatrixImportSource("P1")).resolves.toEqual({ kind: "browser" });
  });

  it("accepts ConnLab xlsx from the desktop picker", async () => {
    bridgeMocks.pickMatrixImportSourceFromDesktop.mockResolvedValue(
      "D:/projects/DL/Source Book/DL-2026-08-004 Matrix.xlsx",
    );
    await expect(chooseMatrixImportSource("P1")).resolves.toEqual({
      kind: "selected",
      path: "D:/projects/DL/Source Book/DL-2026-08-004 Matrix.xlsx",
    });
  });
});
