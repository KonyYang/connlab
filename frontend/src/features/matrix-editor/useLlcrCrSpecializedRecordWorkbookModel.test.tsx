import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useLlcrCrSpecializedRecordWorkbookModel } from "./useLlcrCrSpecializedRecordWorkbookModel";

const apiMocks = vi.hoisted(() => ({
  generateDraft: vi.fn(),
}));

vi.mock("../../api/client", () => ({
  generateMatrixEditorLlcrCrRecordDraftDownload: apiMocks.generateDraft,
}));

describe("useLlcrCrSpecializedRecordWorkbookModel", () => {
  beforeEach(() => vi.resetAllMocks());

  it("shows the current-draft generation error when CR is not required", async () => {
    apiMocks.generateDraft.mockRejectedValue(
      new Error("Current Matrix draft does not require CR."),
    );
    const draftRequest = {
      source: "matrix_editor_current_ui_state" as const,
      groups: [{
        group_key: "g1",
        group_label: "1",
        sample_quantity_expression: "5",
        sample_note: null,
      }],
      rows: [],
    };
    const { result } = renderHook(() => useLlcrCrSpecializedRecordWorkbookModel(
      "P1",
      "cr",
      draftRequest,
    ));

    await act(async () => {
      await result.current.downloadWorkbook();
    });

    expect(apiMocks.generateDraft).toHaveBeenCalledWith("P1", {
      ...draftRequest,
      record_type: "cr",
    });
    expect(result.current.error).toBe("Current Matrix draft does not require CR.");
  });
});
