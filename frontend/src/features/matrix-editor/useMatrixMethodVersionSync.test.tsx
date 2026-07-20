import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useMatrixMethodVersionSync } from "./useMatrixMethodVersionSync";

const apiMocks = vi.hoisted(() => ({ preview: vi.fn(), apply: vi.fn() }));

vi.mock("../../api/client", () => ({
  previewMatrixMethodVersionSync: apiMocks.preview,
  applyMatrixMethodVersionSync: apiMocks.apply,
}));

describe("useMatrixMethodVersionSync", () => {
  beforeEach(() => vi.clearAllMocks());

  it("applies selected proposals and requests an authoritative session reload", async () => {
    const onApplied = vi.fn();
    apiMocks.preview.mockResolvedValue({
      preview_fingerprint: "PF1",
      rows: [{ draft_row_id: "R1", selectable: true }],
    });
    apiMocks.apply.mockResolvedValue({
      project_matrix_draft_id: "D1",
      saved_payload_signature: "SIG2",
      applied_row_ids: ["R1"],
    });
    const { result } = renderHook(() =>
      useMatrixMethodVersionSync({
        projectId: "P1",
        draftId: "D1",
        savedPayloadSignature: "SIG1",
        disabled: false,
        onApplied,
      })
    );

    await act(async () => result.current.previewMethods());
    expect(result.current.selectedRowIds).toEqual(new Set(["R1"]));
    await act(async () => result.current.applySelected());

    expect(apiMocks.apply).toHaveBeenCalledWith("P1", {
      project_matrix_draft_id: "D1",
      expected_saved_payload_signature: "SIG1",
      preview_fingerprint: "PF1",
      selected_draft_row_ids: ["R1"],
      applied_by: "operator",
    });
    expect(onApplied).toHaveBeenCalledWith("SIG2");
  });
});
