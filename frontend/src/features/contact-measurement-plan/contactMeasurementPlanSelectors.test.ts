import { describe, expect, it } from "vitest";
import type { ContactMeasurementPlanWorkspace } from "../../api/client";
import {
  addCustomContactFamily,
  selectContactMeasurementPlanSummary,
  validateContactMeasurementFamilies,
} from "./contactMeasurementPlanSelectors";

describe("selectContactMeasurementPlanSummary", () => {
  it("reports multiple readings without aggregating targets", () => {
    const summary = selectContactMeasurementPlanSummary(workspace());

    expect(summary.statusLabel).toBe("Needs review");
    expect(summary.readings.llcr).toBe("Multiple");
    expect(summary.readings.crSpecifiedCurrent).toBe("2");
    expect(summary.warning).toBe("1 contact measurement change requires review.");
    expect(summary.canOpenSetup).toBe(true);
  });

  it("keeps custom family ids unique after removal and validates duplicate payloads", () => {
    const initialTarget = target("llcr", 2);
    const first = addCustomContactFamily(initialTarget);
    const second = addCustomContactFamily(first);
    const afterRemoval = { ...second, families: second.families.slice(1) };
    const third = addCustomContactFamily(afterRemoval);

    expect(third.families.map((family) => family.family_id)).toEqual([
      "custom-2",
      "custom-3",
    ]);
    expect(validateContactMeasurementFamilies(third.families)).toBeNull();
    expect(
      validateContactMeasurementFamilies([
        ...third.families,
        { ...third.families[0] },
      ])
    ).toBe("Contact family ids must be unique.");
  });
});

function workspace(): ContactMeasurementPlanWorkspace {
  return {
    status: "needs_review",
    project_id: "P1",
    active_confirmed_revision_id: "confirmed-1",
    editable_revision_id: "draft-2",
    editable_revision_state: "needs_review",
    editable_revision_fingerprint: "fingerprint-2",
    revision: {
      revision_id: "draft-2",
      revision_sequence: 2,
      state: "needs_review",
      fingerprint: "fingerprint-2",
    },
    matrix_binding: {
      base_confirmed_matrix_id: "cmv-1",
      base_matrix_revision: 1,
      current_confirmed_matrix_id: "cmv-2",
      current_matrix_revision: 2,
      matrix_binding_fingerprint: "cmv-2:2",
    },
    targets: [target("llcr", 2), target("llcr", 4), target("cr_specified_current", 2)],
    impacts: [],
    summary: {
      included_target_count: 2,
      total_target_count: 3,
      needs_review_count: 1,
      readings_by_kind: { llcr: null, cr_specified_current: 2 },
    },
    diagnostics: ["Contact measurement changes require review."],
  };
}

function target(
  contact_kind: "llcr" | "cr_specified_current",
  readings_per_sample: number
): ContactMeasurementPlanWorkspace["targets"][number] {
  return {
    stable_target_key: `${contact_kind}-${readings_per_sample}`,
    group_label: "Group",
    test_item: contact_kind,
    contact_kind,
    step_sequence: 1,
    step_suffix_note: "",
    sample_quantity_expression: "1",
    eligible: true,
    included: true,
    exclusion_reason: null,
    is_override: false,
    coverage_state: "included",
    readings_per_sample,
    target_review_state: "unchanged",
    target_review_reason: null,
    families: [],
  };
}
