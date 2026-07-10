import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
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
  it("requires a ready preview before generating the specialized workbook", async () => {
    apiMocks.preview.mockResolvedValue({
      project_id: "P1",
      status: "ready",
      confirmed_matrix_id: "cmv-1",
      confirmed_revision: 1,
      preview_fingerprint: "fingerprint-1",
      row_count: 2,
      sections: [],
      diagnostics: [],
    });
    apiMocks.generate.mockResolvedValue({
      project_id: "P1",
      confirmed_matrix_id: "cmv-1",
      confirmed_revision: 1,
      artifact_id: "artifact-1",
      file_name: "record.xlsx",
      download_url: "/download/artifact-1",
    });
    const { result } = renderHook(() => useLlcrCrSpecializedRecordWorkbookModel("P1"));

    await act(async () => {
      await result.current.previewWorkbook();
    });
    expect(result.current.canGenerate).toBe(true);

    await act(async () => {
      await result.current.generateWorkbook();
    });
    expect(apiMocks.generate).toHaveBeenCalledWith("P1", {
      preview_fingerprint: "fingerprint-1",
    });
    expect(result.current.generated?.artifact_id).toBe("artifact-1");
  });
});
