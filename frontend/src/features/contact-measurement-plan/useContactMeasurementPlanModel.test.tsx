import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { useContactMeasurementPlanModel } from "./useContactMeasurementPlanModel";

vi.mock("../../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/client")>()),
  fetchContactMeasurementPlanWorkspace: vi.fn(),
  patchContactMeasurementPlanTarget: vi.fn(),
}));

const apiMocks = vi.mocked(api);

describe("useContactMeasurementPlanModel", () => {
  it("reloads the workspace fingerprint after one target command", async () => {
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(workspace("fingerprint-1"))
      .mockResolvedValueOnce(workspace("fingerprint-2"));
    apiMocks.patchContactMeasurementPlanTarget.mockResolvedValue({
      status: "updated",
      revision_id: "draft-1",
    });

    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-1"));

    await act(async () => {
      await result.current.saveSelectedTarget();
    });

    expect(apiMocks.patchContactMeasurementPlanTarget).toHaveBeenCalledWith(
      "P1",
      "draft-1",
      expect.objectContaining({ expected_revision_fingerprint: "fingerprint-1" })
    );
    expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-2");
  });

  it("reloads latest then explicitly reapplies saved local target edits after stale", async () => {
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(workspace("fingerprint-1"))
      .mockResolvedValueOnce(workspace("fingerprint-2"))
      .mockResolvedValueOnce(workspace("fingerprint-3"));
    apiMocks.patchContactMeasurementPlanTarget.mockRejectedValue(
      new api.ApiRequestError("stale", 409, { code: "contact_measurement_plan_conflict" })
    );

    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.workspace).not.toBeNull());

    await act(async () => {
      await result.current.saveSelectedTarget();
    });

    expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-1");
    expect(result.current.error).toBe("Contact measurement plan changed. Reload before continuing.");
    expect(result.current.staleLocalTarget?.stable_target_key).toContain("cmp-target:v1");

    apiMocks.patchContactMeasurementPlanTarget.mockResolvedValueOnce({
      status: "updated",
      revision_id: "draft-1",
    });
    await act(async () => {
      await result.current.reapplySavedEdits();
    });

    expect(apiMocks.patchContactMeasurementPlanTarget).toHaveBeenLastCalledWith(
      "P1",
      "draft-1",
      expect.objectContaining({ expected_revision_fingerprint: "fingerprint-2" })
    );
    expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-3");
    expect(result.current.staleLocalTarget).toBeNull();
  });
});

function workspace(fingerprint: string): api.ContactMeasurementPlanWorkspace {
  return {
    status: "draft",
    project_id: "P1",
    active_confirmed_revision_id: "confirmed-1",
    editable_revision_id: "draft-1",
    editable_revision_state: "draft",
    editable_revision_fingerprint: fingerprint,
    revision: { revision_id: "draft-1", revision_sequence: 2, state: "draft", fingerprint },
    matrix_binding: {
      base_confirmed_matrix_id: "cmv-1",
      base_matrix_revision: 1,
      current_confirmed_matrix_id: "cmv-1",
      current_matrix_revision: 1,
      matrix_binding_fingerprint: "cmv-1:1",
    },
    targets: [
      {
        stable_target_key: "cmp-target:v1|group:cg-1|row:cr-1|step:1|suffix:",
        group_label: "Group 1",
        test_item: "LLCR",
        contact_kind: "llcr",
        step_sequence: 1,
        step_suffix_note: "",
        sample_quantity_expression: "2",
        eligible: true,
        included: true,
        exclusion_reason: null,
        is_override: false,
        coverage_state: "included",
        readings_per_sample: 2,
        target_review_state: "unchanged",
        target_review_reason: null,
        families: [],
      },
    ],
    impacts: [],
    summary: {
      included_target_count: 1,
      total_target_count: 1,
      needs_review_count: 0,
      readings_by_kind: { llcr: 2, cr_specified_current: null },
    },
    diagnostics: [],
  };
}
