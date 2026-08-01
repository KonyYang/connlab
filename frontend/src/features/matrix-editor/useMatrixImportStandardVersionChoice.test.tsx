import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useMatrixImportStandardVersionChoice } from "./useMatrixImportStandardVersionChoice";

const apiMocks = vi.hoisted(() => ({
  listExternalResources: vi.fn(),
  saveExternalResource: vi.fn(),
  validateExternalResource: vi.fn(),
}));
const pickerMocks = vi.hoisted(() => ({
  hasDesktopPathPickerBridge: vi.fn(),
  pickExternalResourcePathFromDesktop: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/client")>()),
  ...apiMocks,
}));
vi.mock("../../desktop/pathPickerBridge", () => pickerMocks);

const detail = {
  code: "matrix_import_standard_version_action_required" as const,
  reason_code: "standard_version_not_configured" as const,
  message: "Standard version file unavailable.",
};

describe("useMatrixImportStandardVersionChoice", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    pickerMocks.hasDesktopPathPickerBridge.mockReturnValue(true);
    apiMocks.listExternalResources.mockResolvedValue([]);
    apiMocks.saveExternalResource.mockResolvedValue({});
    apiMocks.validateExternalResource.mockResolvedValue({ validation_status: "valid" });
  });

  it("keeps the choice open and writes nothing when file selection is cancelled", async () => {
    pickerMocks.pickExternalResourcePathFromDesktop.mockResolvedValue(null);
    const retry = vi.fn();
    const { result } = renderHook(() => useMatrixImportStandardVersionChoice());
    act(() => result.current.open(detail, retry));

    await act(() => result.current.chooseFile());

    expect(result.current.isOpen).toBe(true);
    expect(apiMocks.saveExternalResource).not.toHaveBeenCalled();
    expect(apiMocks.validateExternalResource).not.toHaveBeenCalled();
    expect(retry).not.toHaveBeenCalled();
  });

  it("saves and validates the chosen path before retrying normal Replace", async () => {
    pickerMocks.pickExternalResourcePathFromDesktop.mockResolvedValue("D:/standards.xlsx");
    apiMocks.listExternalResources.mockResolvedValue([
      { resource_type: "standard_record_excel", worksheet_name: "认可标准" },
    ]);
    const retry = vi.fn().mockResolvedValue(undefined);
    const { result } = renderHook(() => useMatrixImportStandardVersionChoice());
    act(() => result.current.open(detail, retry));

    await act(() => result.current.chooseFile());

    expect(apiMocks.saveExternalResource).toHaveBeenCalledWith("standard_record_excel", {
      path: "D:/standards.xlsx",
      active: true,
      worksheet_name: "认可标准",
    });
    expect(apiMocks.validateExternalResource).toHaveBeenCalledWith("standard_record_excel");
    expect(retry).toHaveBeenCalledWith("prompt_if_unavailable");
    expect(result.current.isOpen).toBe(false);
  });

  it("keeps validation failure recoverable without committing Matrix import", async () => {
    pickerMocks.pickExternalResourcePathFromDesktop.mockResolvedValue("D:/bad.xlsx");
    apiMocks.validateExternalResource.mockResolvedValue({
      validation_status: "invalid",
      validation_failure_reason: "Configured worksheet was not found.",
    });
    const retry = vi.fn();
    const { result } = renderHook(() => useMatrixImportStandardVersionChoice());
    act(() => result.current.open(detail, retry));

    await act(() => result.current.chooseFile());

    expect(result.current.error).toBe("Configured worksheet was not found.");
    expect(result.current.isOpen).toBe(true);
    expect(retry).not.toHaveBeenCalled();
  });

  it("retries immediately with preserve policy when Skip is explicit", async () => {
    const retry = vi.fn().mockResolvedValue(undefined);
    const { result } = renderHook(() => useMatrixImportStandardVersionChoice());
    act(() => result.current.open(detail, retry));

    await act(() => result.current.skip());

    expect(retry).toHaveBeenCalledWith("preserve_imported_methods");
    expect(result.current.isOpen).toBe(false);
  });
});
