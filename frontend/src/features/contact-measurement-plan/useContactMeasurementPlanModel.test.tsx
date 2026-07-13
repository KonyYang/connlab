import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import * as selectors from "./contactMeasurementPlanSelectors";
import { useContactMeasurementPlanModel } from "./useContactMeasurementPlanModel";

vi.mock("../../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/client")>()),
  fetchContactMeasurementPlanWorkspace: vi.fn(),
  patchContactMeasurementPlanTarget: vi.fn(),
}));

const apiMocks = vi.mocked(api);

describe("useContactMeasurementPlanModel", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });
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
    await waitFor(() => expect(result.current.busy).toBeNull());

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

  it("keeps freeform ids monotonic after removal and starts an empty target with one blank row", async () => {
    const initial = workspace("fingerprint-1");
    initial.targets[0].families = [];
    initial.family_id_high_water_by_kind = { llcr: 1, cr_specified_current: 0 };
    apiMocks.fetchContactMeasurementPlanWorkspace.mockResolvedValue(initial);

    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]?.family_id).toBe("ff-llcr-2"));

    act(() => result.current.addFreeformFamily("signal"));
    act(() => result.current.removeFamily("ff-llcr-2"));
    act(() => result.current.addFreeformFamily("signal"));

    expect(result.current.selectedTarget?.families.map((family) => family.family_id)).toEqual([
      "ff-llcr-3",
      "ff-llcr-4",
    ]);
  });

  it("clears project-scoped freeform workflow state before loading a new project's persisted family", async () => {
    const projectA = workspace("fingerprint-a", "PA");
    projectA.targets[0].families = [];
    const projectB = workspace("fingerprint-b", "PB");
    projectB.targets[0].families[0].record_label = "";
    projectB.family_id_high_water_by_kind = { llcr: 0, cr_specified_current: 0 };
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(projectA)
      .mockResolvedValueOnce(projectB);
    const { result, rerender } = renderHook(
      ({ projectId }) => useContactMeasurementPlanModel({ projectId }),
      { initialProps: { projectId: "PA" } }
    );
    await waitFor(() => expect(result.current.selectedTarget?.families[0]?.family_id).toBe("ff-llcr-1"));
    act(() => result.current.addFreeformFamily("signal"));
    await waitFor(() => expect(result.current.selectedTarget?.families.at(-1)?.family_id).toBe("ff-llcr-2"));

    rerender({ projectId: "PB" });
    await waitFor(() => expect(result.current.workspace?.project_id).toBe("PB"));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]?.record_label).toBe(""));

    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({ ...family, label: "Project B legacy" })),
    })));
    act(() => result.current.finalizeSelectedFamilyLabel("ff-llcr-1"));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]).toMatchObject({
      family_id: "ff-llcr-2",
      record_label: "",
    }));

    await act(async () => {
      await result.current.saveSelectedTarget();
    });

    expect(result.current.error).toBe("Contact family label and prefix are required.");
    expect(apiMocks.patchContactMeasurementPlanTarget).not.toHaveBeenCalled();
  });

  it("initializes a new blank category record label from the visible label before save", async () => {
    const initial = workspace("fingerprint-1");
    initial.targets[0].families = [];
    const saved = structuredClone(initial);
    saved.targets[0].families = [{
      family_id: "ff-llcr-2",
      family_ordinal: 0,
      label: "P1 contact",
      count_per_sample: 2,
      record_label: "P1 contact",
      record_prefix: "PX",
      included: true,
      is_custom: true,
    }];
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(initial)
      .mockResolvedValueOnce(saved);
    apiMocks.patchContactMeasurementPlanTarget.mockResolvedValue({ status: "updated", revision_id: "draft-1" });
    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]?.family_id).toBe("ff-llcr-1"));

    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({
        ...family,
        label: "P1 contact",
        count_per_sample: 2,
        record_prefix: "PX",
      })),
    })));
    act(() => result.current.finalizeSelectedFamilyLabel("ff-llcr-1"));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]?.family_id).toBe("ff-llcr-2"));

    await act(async () => {
      await result.current.saveSelectedTarget();
    });

    expect(result.current.error).toBeNull();
    expect(apiMocks.patchContactMeasurementPlanTarget).toHaveBeenCalledWith(
      "P1",
      "draft-1",
      expect.objectContaining({
        families: [expect.objectContaining({
          family_id: "ff-llcr-2",
          label: "P1 contact",
          record_label: "P1 contact",
          record_prefix: "PX",
        })],
      })
    );

    await waitFor(() => expect(result.current.selectedTarget?.families[0]?.record_label).toBe("P1 contact"));
    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({ ...family, label: "P1 revised" })),
    })));
    act(() => result.current.finalizeSelectedFamilyLabel("ff-llcr-2"));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]).toMatchObject({
      family_id: "ff-llcr-3",
      record_label: "P1 contact",
    }));
    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({ ...family, record_prefix: "PX2" })),
    })));
    act(() => result.current.resolveSelectedFamilyPrefix("ff-llcr-3"));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]).toMatchObject({
      family_id: "ff-llcr-4",
      record_label: "P1 contact",
    }));
  });

  it("does not infer a record label for a persisted empty-label family after semantic id renewal", async () => {
    const initial = workspace("fingerprint-1");
    initial.targets[0].families[0].record_label = "";
    apiMocks.fetchContactMeasurementPlanWorkspace.mockResolvedValue(initial);
    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget).not.toBeNull());

    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({ ...family, label: "Renamed legacy" })),
    })));
    act(() => result.current.finalizeSelectedFamilyLabel("ff-llcr-1"));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]).toMatchObject({
      family_id: "ff-llcr-2",
      record_label: "",
    }));
    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({ ...family, record_prefix: "LEG2" })),
    })));
    act(() => result.current.resolveSelectedFamilyPrefix("ff-llcr-2"));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]).toMatchObject({
      family_id: "ff-llcr-3",
      record_label: "",
    }));

    await act(async () => {
      await result.current.saveSelectedTarget();
    });

    expect(result.current.error).toBe("Contact family label and prefix are required.");
    expect(apiMocks.patchContactMeasurementPlanTarget).not.toHaveBeenCalled();
  });

  it("keeps a persisted empty record label through prefix renewal, stale response, and reapply", async () => {
    const initial = workspace("fingerprint-1");
    initial.targets[0].families[0].record_label = "";
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(initial)
      .mockResolvedValueOnce(workspace("fingerprint-2"))
      .mockResolvedValueOnce(workspace("fingerprint-3"));
    apiMocks.patchContactMeasurementPlanTarget
      .mockRejectedValueOnce(
        new api.ApiRequestError("stale", 409, { code: "contact_measurement_plan_conflict" })
      )
      .mockResolvedValueOnce({ status: "updated", revision_id: "draft-1" });
    const validation = vi.spyOn(selectors, "validateContactMeasurementFamilies").mockReturnValue(null);
    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget).not.toBeNull());

    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({ ...family, record_prefix: "HP2" })),
    })));
    act(() => result.current.resolveSelectedFamilyPrefix("ff-llcr-1"));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]).toMatchObject({
      family_id: "ff-llcr-2",
      record_label: "",
      record_prefix: "HP2",
    }));

    await act(async () => {
      await result.current.saveSelectedTarget();
    });
    await waitFor(() => expect(result.current.staleLocalTarget?.families[0]?.family_id).toBe("ff-llcr-2"));
    await waitFor(() => expect(result.current.busy).toBeNull());
    await act(async () => {
      await result.current.reapplySavedEdits();
    });

    expect(apiMocks.patchContactMeasurementPlanTarget).toHaveBeenLastCalledWith(
      "P1",
      "draft-1",
      expect.objectContaining({
        expected_revision_fingerprint: "fingerprint-2",
        families: [expect.objectContaining({ family_id: "ff-llcr-2", record_label: "" })],
      })
    );
    validation.mockRestore();
  });

  it("applies an initialized blank category to blank eligible targets", async () => {
    const initial = workspace("fingerprint-1");
    initial.targets[0].families = [];
    initial.targets.push({
      ...initial.targets[0],
      stable_target_key: "cmp-target:v1|group:cg-2|row:cr-1|step:1|suffix:",
      families: [],
    });
    const latest = structuredClone(initial);
    const reloaded = structuredClone(initial);
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(initial)
      .mockResolvedValueOnce(latest)
      .mockResolvedValueOnce(reloaded);
    apiMocks.patchContactMeasurementPlanTarget.mockResolvedValue({ status: "updated", revision_id: "draft-1" });
    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]?.family_id).toBe("ff-llcr-1"));

    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({
        ...family,
        label: "P1 contact",
        count_per_sample: 2,
        record_prefix: "PX",
      })),
    })));
    act(() => result.current.finalizeSelectedFamilyLabel("ff-llcr-1"));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]?.family_id).toBe("ff-llcr-2"));

    await act(async () => {
      await result.current.applySelectedFamiliesToBlankTargets();
    });

    expect(result.current.error).toBeNull();
    expect(apiMocks.patchContactMeasurementPlanTarget).toHaveBeenCalledWith(
      "P1",
      "draft-1",
      expect.objectContaining({
        stable_target_key: initial.targets[1].stable_target_key,
        families: [expect.objectContaining({ record_label: "P1 contact" })],
      })
    );
  });

  it("blocks a normalized duplicate prefix before sending the existing target patch", async () => {
    apiMocks.fetchContactMeasurementPlanWorkspace.mockResolvedValue(workspace("fingerprint-1"));
    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget).not.toBeNull());
    act(() => result.current.addFreeformFamily("signal"));
    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family, index) => index === 1 ? { ...family, record_prefix: "hp" } : family),
    })));

    await act(async () => {
      await result.current.saveSelectedTarget();
    });

    expect(result.current.error).toBe("Contact family prefixes must be unique.");
    expect(apiMocks.patchContactMeasurementPlanTarget).not.toHaveBeenCalled();
  });

  it("renews semantic freeform ids without overwriting an existing record label", async () => {
    const initial = workspace("fingerprint-1");
    initial.targets[0].families[0].record_label = "Legacy record label";
    apiMocks.fetchContactMeasurementPlanWorkspace.mockResolvedValue(initial);
    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget).not.toBeNull());

    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({ ...family, label: "Renamed High Power" })),
    })));
    act(() => result.current.finalizeSelectedFamilyLabel("ff-llcr-1"));

    await waitFor(() => expect(result.current.selectedTarget?.families[0]).toMatchObject({
      family_id: "ff-llcr-2",
      label: "Renamed High Power",
      record_label: "Legacy record label",
    }));

    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({ ...family, record_prefix: "hp2" })),
    })));
    act(() => result.current.resolveSelectedFamilyPrefix("ff-llcr-2"));

    await waitFor(() => expect(result.current.selectedTarget?.families[0]).toMatchObject({
      family_id: "ff-llcr-3",
      record_prefix: "HP2",
      record_label: "Legacy record label",
    }));
  });

  it("reapplies a renewed freeform identity after a stale reload without reusing it", async () => {
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(workspace("fingerprint-1"))
      .mockResolvedValueOnce(workspace("fingerprint-2"))
      .mockResolvedValueOnce(workspace("fingerprint-3"));
    apiMocks.patchContactMeasurementPlanTarget
      .mockRejectedValueOnce(
        new api.ApiRequestError("stale", 409, { code: "contact_measurement_plan_conflict" })
      )
      .mockResolvedValueOnce({ status: "updated", revision_id: "draft-1" });
    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget).not.toBeNull());

    act(() => result.current.updateSelectedTarget((target) => ({
      ...target,
      families: target.families.map((family) => ({ ...family, label: "Stale rename" })),
    })));
    act(() => result.current.finalizeSelectedFamilyLabel("ff-llcr-1"));
    await waitFor(() => expect(result.current.selectedTarget?.families[0]?.family_id).toBe("ff-llcr-2"));

    await act(async () => {
      await result.current.saveSelectedTarget();
    });
    await waitFor(() => expect(result.current.staleLocalTarget?.families[0]?.family_id).toBe("ff-llcr-2"));
    await waitFor(() => expect(result.current.busy).toBeNull());
    await act(async () => {
      await result.current.reapplySavedEdits();
    });

    expect(apiMocks.patchContactMeasurementPlanTarget).toHaveBeenLastCalledWith(
      "P1",
      "draft-1",
      expect.objectContaining({
        expected_revision_fingerprint: "fingerprint-2",
        families: [expect.objectContaining({ family_id: "ff-llcr-2" })],
      })
    );
  });

  it("applies the selected profile only to blank non-override targets through existing single-target patches", async () => {
    const initial = workspace("fingerprint-1");
    initial.targets.push(
      { ...initial.targets[0], stable_target_key: "cmp-target:v1|group:cg-2|row:cr-1|step:1|suffix:", families: [], is_override: false },
      { ...initial.targets[0], stable_target_key: "cmp-target:v1|group:cg-3|row:cr-1|step:1|suffix:", families: [], is_override: true },
    );
    const latest = structuredClone(initial);
    const reloaded = structuredClone(initial);
    reloaded.targets[1].families = structuredClone(initial.targets[0].families);
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(initial)
      .mockResolvedValueOnce(latest)
      .mockResolvedValueOnce(reloaded);
    apiMocks.patchContactMeasurementPlanTarget.mockResolvedValue({ status: "updated", revision_id: "draft-1" });

    const { result } = renderHook(() => useContactMeasurementPlanModel({ projectId: "P1" }));
    await waitFor(() => expect(result.current.selectedTarget).not.toBeNull());
    await act(async () => {
      await result.current.applySelectedFamiliesToBlankTargets();
    });

    expect(apiMocks.patchContactMeasurementPlanTarget).toHaveBeenCalledTimes(1);
    expect(apiMocks.patchContactMeasurementPlanTarget).toHaveBeenCalledWith(
      "P1",
      "draft-1",
      expect.objectContaining({ stable_target_key: initial.targets[1].stable_target_key })
    );
  });
});

function workspace(fingerprint: string, projectId = "P1"): api.ContactMeasurementPlanWorkspace {
  return {
    status: "draft",
    project_id: projectId,
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
        families: [{
          family_id: "ff-llcr-1",
          family_ordinal: 0,
          label: "High Power",
          count_per_sample: 2,
          record_label: "High Power",
          record_prefix: "HP",
          included: true,
          is_custom: true,
        }],
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
    family_id_high_water_by_kind: { llcr: 0, cr_specified_current: 0 },
  };
}
