import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { useContactMeasurementPlanModel } from "./useContactMeasurementPlanModel";

vi.mock("../../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/client")>()),
  fetchContactMeasurementPlanWorkspace: vi.fn(),
  openContactMeasurementPlanRevision: vi.fn(),
}));

const apiMocks = vi.mocked(api);

describe("useContactMeasurementPlanModel target hydration", () => {
  beforeEach(() => vi.resetAllMocks());

  it("replaces a retained but ineligible preferred key with the eligible fallback starter", async () => {
    const current = workspace("fingerprint-current", [target("old-key", "Old target", true)]);
    const draft = workspace("fingerprint-draft", [
      target("old-key", "Old target unavailable", false),
      target("new-key", "Group 1", true),
    ]);
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(current)
      .mockResolvedValueOnce(draft);
    apiMocks.openContactMeasurementPlanRevision.mockResolvedValue({
      status: "opened",
      revision_id: "draft-1",
    });
    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget?.stable_target_key).toBe("old-key"));

    await act(async () => { await result.current.openDraft(); });

    await waitFor(() => expect(result.current.selectedTarget).toMatchObject({
      stable_target_key: "new-key",
      group_label: "Group 1",
    }));
    expect(result.current.selectedTarget?.families).toEqual([
      expect.objectContaining({
        family_id: "ff-llcr-1",
        count_per_sample: 1,
        record_prefix: "C1",
      }),
    ]);
  });

  it("clears a retained but ineligible preferred key when a reload has no eligible target", async () => {
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(workspace("fingerprint-current", [target("old-key", "Old target", true)]))
      .mockResolvedValueOnce(workspace("fingerprint-none", [target("old-key", "Old target unavailable", false)]));
    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget?.stable_target_key).toBe("old-key"));

    await act(async () => { await result.current.reloadLatest(); });

    expect(result.current.selectedTarget).toBeNull();
    expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-none");
  });
});

function workspace(
  fingerprint: string,
  targets: api.ContactMeasurementPlanWorkspace["targets"]
): api.ContactMeasurementPlanWorkspace {
  return {
    status: "draft",
    project_id: "P1",
    active_confirmed_revision_id: "confirmed-1",
    editable_revision_id: "draft-1",
    editable_revision_state: "draft",
    editable_revision_fingerprint: fingerprint,
    revision: { revision_id: "draft-1", revision_sequence: 1, state: "draft", fingerprint },
    matrix_binding: {
      base_confirmed_matrix_id: "cmv-1",
      base_matrix_revision: 1,
      current_confirmed_matrix_id: "cmv-1",
      current_matrix_revision: 1,
      matrix_binding_fingerprint: "cmv-1:1",
    },
    targets,
    impacts: [],
    summary: {
      included_target_count: targets.filter((item) => item.included).length,
      total_target_count: targets.length,
      needs_review_count: 0,
      readings_by_kind: { llcr: null, cr_specified_current: null },
    },
    diagnostics: [],
    family_id_high_water_by_kind: { llcr: 0, cr_specified_current: 0 },
  };
}

function target(stableTargetKey: string, groupLabel: string, eligible: boolean) {
  return {
    stable_target_key: stableTargetKey,
    group_label: groupLabel,
    test_item: "LLCR",
    contact_kind: "llcr" as const,
    step_sequence: 1,
    step_suffix_note: "",
    sample_quantity_expression: "1",
    eligible,
    included: eligible,
    exclusion_reason: null,
    is_override: false,
    coverage_state: eligible ? "included" : "excluded",
    readings_per_sample: 0,
    target_review_state: "unchanged",
    target_review_reason: null,
    families: [],
  };
}
