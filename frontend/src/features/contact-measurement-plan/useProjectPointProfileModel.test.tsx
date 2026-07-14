import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import type { ProjectPointProfileCategory, ProjectPointProfileWorkspace } from "../../api/client";
import { useProjectPointProfileModel } from "./useProjectPointProfileModel";

vi.mock("../../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/client")>()),
  fetchProjectPointProfileWorkspace: vi.fn(),
  saveProjectPointProfileDraft: vi.fn(),
  confirmProjectPointProfile: vi.fn(),
}));

const apiMocks = vi.mocked(api);

describe("useProjectPointProfileModel", () => {
  beforeEach(() => vi.resetAllMocks());

  it("restores the confirmed baseline after local delete and saves every confirmed row", async () => {
    const confirmed = categories();
    apiMocks.fetchProjectPointProfileWorkspace
      .mockResolvedValueOnce(workspace(confirmed))
      .mockResolvedValueOnce(workspace(confirmed));
    apiMocks.saveProjectPointProfileDraft.mockResolvedValue(revision(confirmed));

    const { result } = renderHook(() => useProjectPointProfileModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.rows).toHaveLength(2));

    act(() => {
      result.current.updateRow(0, { label: "Changed", count_per_sample: "9", record_prefix: "CH" });
      result.current.removeCategory(1);
      result.current.discard();
    });

    expect(result.current.rows).toEqual(confirmed);
    await act(async () => { await result.current.saveDraft(); });
    expect(apiMocks.saveProjectPointProfileDraft).toHaveBeenCalledWith("P1", expect.objectContaining({
      categories: confirmed,
    }));
  });

  it("serializes raw whole-number input as a number and includes it in the live total", async () => {
    apiMocks.fetchProjectPointProfileWorkspace
      .mockResolvedValueOnce(workspace([]))
      .mockResolvedValueOnce(workspace([]));
    apiMocks.saveProjectPointProfileDraft.mockResolvedValue(revision([]));
    const { result } = renderHook(() => useProjectPointProfileModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => result.current.updateRow(0, { label: "High Power", count_per_sample: "4", record_prefix: "HP" }));
    expect(result.current.total).toBe(4);
    await act(async () => { await result.current.saveDraft(); });
    expect(apiMocks.saveProjectPointProfileDraft).toHaveBeenLastCalledWith("P1", expect.objectContaining({
      categories: [expect.objectContaining({ count_per_sample: 4 })],
    }));
  });

  it("keeps invalid raw count formats from writing", async () => {
    apiMocks.fetchProjectPointProfileWorkspace.mockResolvedValue(workspace([]));
    const { result } = renderHook(() => useProjectPointProfileModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.loading).toBe(false));
    act(() => result.current.updateRow(0, { label: "High Power", record_prefix: "HP" }));

    for (const invalid of ["1.5", "", " ", "0", "-1", "1e2", "+4", "4x", "9007199254740992"]) {
      act(() => result.current.updateRow(0, { count_per_sample: invalid }));
      await act(async () => { await result.current.saveDraft(); });
    }
    expect(apiMocks.saveProjectPointProfileDraft).not.toHaveBeenCalled();
  });
});

function categories(): ProjectPointProfileCategory[] {
  return [
    { category_id: "ppc-1", category_ordinal: 0, label: "High Power", count_per_sample: 4, record_prefix: "HP", included: true },
    { category_id: "ppc-2", category_ordinal: 1, label: "Signal", count_per_sample: 24, record_prefix: "SIG", included: true },
  ];
}

function revision(categories: ProjectPointProfileCategory[]) {
  return {
    revision_id: "profile-revision-1", revision_sequence: 1, state: "draft", fingerprint: "fingerprint-1",
    created_at: "2026-07-14T00:00:00Z", confirmed_at: null, categories, points_per_sample: 28,
  };
}

function workspace(confirmedCategories: ProjectPointProfileCategory[]): ProjectPointProfileWorkspace {
  return {
    status: "ready", project_id: "P1", editable_revision: null,
    confirmed_revision: confirmedCategories.length ? { ...revision(confirmedCategories), state: "confirmed", confirmed_at: "2026-07-14T00:00:00Z" } : null,
    has_unconfirmed_draft: false, legacy_uniform_suggestion: null, diagnostics: [],
  };
}
