import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useLlcrCrSpecializedRecordWorkbookModel } from "./useLlcrCrSpecializedRecordWorkbookModel";

const apiMocks = vi.hoisted(() => ({
  preview: vi.fn(),
  generate: vi.fn(),
  download: vi.fn(),
}));

vi.mock("../../api/client", () => ({
  previewLlcrCrRecordWorkbook: apiMocks.preview,
  generateLlcrCrRecordWorkbook: apiMocks.generate,
  downloadLlcrCrRecordWorkbook: apiMocks.download,
}));

describe("useLlcrCrSpecializedRecordWorkbookModel", () => {
  beforeEach(() => vi.resetAllMocks());

  it("stops the one-click download when the confirmed Matrix does not require the record", async () => {
    apiMocks.preview.mockResolvedValue({
      project_id: "P1",
      status: "empty",
      record_type: "cr",
      confirmed_matrix_id: "cmv-1",
      confirmed_revision: 1,
      preview_fingerprint: null,
      row_count: 0,
      sections: [],
      diagnostics: [],
      delta_r_enabled: false,
    });
    const { result } = renderHook(() => useLlcrCrSpecializedRecordWorkbookModel("P1", "cr"));

    await act(async () => {
      await result.current.downloadWorkbook();
    });

    expect(apiMocks.preview).toHaveBeenCalledWith("P1", "cr");
    expect(apiMocks.generate).not.toHaveBeenCalled();
    expect(apiMocks.download).not.toHaveBeenCalled();
    expect(result.current.error).toBe("CR is not required by the confirmed Matrix.");
  });
});
