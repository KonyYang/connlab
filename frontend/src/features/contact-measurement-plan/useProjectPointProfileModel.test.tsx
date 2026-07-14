import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { useProjectPointProfileModel } from "./useProjectPointProfileModel";

vi.mock("../../api/client", async (original) => ({ ...(await original<typeof import("../../api/client")>()), fetchProjectPointProfileWorkspace: vi.fn(), confirmProjectPointProfile: vi.fn() }));
const apiMocks = vi.mocked(api);

describe("useProjectPointProfileModel", () => {
  beforeEach(() => vi.resetAllMocks());
  it("keeps edits local until one direct confirm command", async () => {
    apiMocks.fetchProjectPointProfileWorkspace.mockResolvedValue(workspace());
    apiMocks.confirmProjectPointProfile.mockResolvedValue(revision());
    const { result } = renderHook(() => useProjectPointProfileModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.loading).toBe(false));
    act(() => result.current.updateRow(0, { prefix: "HP", point_expression: "1-4" }));
    expect(apiMocks.confirmProjectPointProfile).not.toHaveBeenCalled();
    await act(async () => { await result.current.confirm(); });
    expect(apiMocks.confirmProjectPointProfile).toHaveBeenCalledWith("P1", expect.objectContaining({ categories: [{ category_id: null, prefix: "HP", point_expression: "1-4" }] }));
  });

  it("blocks a hydrated 257th category before confirming and disables further adds", async () => {
    apiMocks.fetchProjectPointProfileWorkspace.mockResolvedValue(workspaceWithCategories(257));
    const { result } = renderHook(() => useProjectPointProfileModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.rows).toHaveLength(257);
    expect(result.current.validation).toMatch(/256/i);
    act(() => result.current.addCategory());
    expect(result.current.rows).toHaveLength(257);
    await act(async () => { await result.current.confirm(); });
    expect(apiMocks.confirmProjectPointProfile).not.toHaveBeenCalled();
  });
});

function revision() { return { revision_id: "R1", revision_sequence: 1, state: "confirmed", fingerprint: "F1", created_at: "", confirmed_at: "", categories: [], points_per_sample: 0 }; }
function workspace() { return { status: "not_started", project_id: "P1", editable_revision: null, confirmed_revision: null, has_unconfirmed_draft: false, legacy_uniform_suggestion: null, diagnostics: [] }; }
function workspaceWithCategories(length: number) {
  const categories = Array.from({ length }, (_, index) => ({
    category_id: `ppc-${index + 1}`, category_ordinal: index, label: `P${index + 1}`,
    count_per_sample: 1, record_prefix: `P${index + 1}`, included: true, point_expression: "1",
  }));
  return {
    status: "confirmed", project_id: "P1", editable_revision: null,
    confirmed_revision: { ...revision(), categories, points_per_sample: length },
    has_unconfirmed_draft: false, legacy_uniform_suggestion: null, diagnostics: [],
  };
}
