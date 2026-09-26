import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useMatrixMethodVersionSync } from "./useMatrixMethodVersionSync";

const apiMocks = vi.hoisted(() => ({ suggest: vi.fn() }));

vi.mock("../../api/client", () => ({
  suggestMatrixMethodVersions: apiMocks.suggest,
}));

const methodRows = [{ row_id: "R1", method: "EIA-364-18B" }];

describe("useMatrixMethodVersionSync", () => {
  beforeEach(() => vi.clearAllMocks());

  it("applies safe Excel suggestions as local Method edits in one action", async () => {
    const onApply = vi.fn();
    apiMocks.suggest.mockResolvedValue({ rows: [
      { row_id: "R1", current_method: "EIA-364-18B", proposed_method: "EIA-364-18C", selectable: true },
      { row_id: "R2", current_method: "IEC 60512", proposed_method: null, selectable: false },
    ] });
    const { result } = renderHook(() => useMatrixMethodVersionSync({
      projectId: "P1", rows: methodRows, currentSignature: "S1", disabled: false, onApply,
    }));

    await act(async () => result.current.syncMethods());

    expect(apiMocks.suggest).toHaveBeenCalledWith("P1", { rows: methodRows });
    expect(onApply).toHaveBeenCalledWith([
      { row_id: "R1", current_method: "EIA-364-18B", proposed_method: "EIA-364-18C" },
    ]);
    expect(result.current.message).toMatch(/1 Method version updated/i);
  });

  it("leaves the Matrix untouched when all versions are current or unmatchable", async () => {
    const onApply = vi.fn();
    apiMocks.suggest.mockResolvedValue({ rows: [
      { row_id: "R1", current_method: "EIA-364-18B", proposed_method: null, selectable: false },
    ] });
    const { result } = renderHook(() => useMatrixMethodVersionSync({
      projectId: "P1", rows: methodRows, currentSignature: "S1", disabled: false, onApply,
    }));

    await act(async () => result.current.syncMethods());

    expect(onApply).not.toHaveBeenCalled();
    expect(result.current.message).toMatch(/No applicable Method version updates/i);
  });

  it("does not overwrite a Method changed by the user while Excel was loading", async () => {
    const onApply = vi.fn();
    let resolveSuggestion: (value: unknown) => void = () => {};
    apiMocks.suggest.mockReturnValue(new Promise((resolve) => { resolveSuggestion = resolve; }));
    const { result, rerender } = renderHook(
      ({ rows, currentSignature }) => useMatrixMethodVersionSync({
        projectId: "P1", rows, currentSignature, disabled: false, onApply,
      }),
      { initialProps: { rows: methodRows, currentSignature: "S1" } },
    );

    let pending: Promise<void> = Promise.resolve();
    act(() => { pending = result.current.syncMethods(); });
    rerender({ rows: [{ row_id: "R1", method: "EIA-364-18D" }], currentSignature: "S2" });
    await act(async () => {
      resolveSuggestion({ rows: [
        { row_id: "R1", current_method: "EIA-364-18B", proposed_method: "EIA-364-18C", selectable: true },
      ] });
      await pending;
    });

    expect(onApply).not.toHaveBeenCalled();
    expect(result.current.error).toMatch(/changed while checking/i);
  });

  it("reports Excel read failures without changing Method cells", async () => {
    const onApply = vi.fn();
    apiMocks.suggest.mockRejectedValue(new Error("Standard record Excel is unavailable."));
    const { result } = renderHook(() => useMatrixMethodVersionSync({
      projectId: "P1", rows: methodRows, currentSignature: "S1", disabled: false, onApply,
    }));

    await act(async () => result.current.syncMethods());

    expect(onApply).not.toHaveBeenCalled();
    expect(result.current.error).toMatch(/Excel is unavailable/i);
  });
});
