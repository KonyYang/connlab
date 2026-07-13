import { describe, expect, it } from "vitest";
import type { ContactMeasurementPlanWorkspace } from "../../api/client";
import {
  addFreeformContactFamily,
  ensureDefaultFreeformFamily,
  initializeFreeformRecordLabelsForOrigins,
  moveFreeformFamilyOrigin,
  moveContactFamily,
  resolveFreeformPrefix,
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

  it("issues freeform ids from high water after removal without reusing them", () => {
    const initialTarget = target("llcr", 2);
    const first = addFreeformContactFamily(initialTarget, { llcr: 0, cr_specified_current: 0 }, "high_power");
    const second = addFreeformContactFamily(first, { llcr: 1, cr_specified_current: 0 }, "low_power");
    const afterRemoval = { ...second, families: second.families.slice(1) };
    const third = addFreeformContactFamily(afterRemoval, { llcr: 2, cr_specified_current: 0 }, "signal");

    expect(third.families.map((family) => family.family_id)).toEqual([
      "ff-llcr-2",
      "ff-llcr-3",
    ]);
    expect(validateContactMeasurementFamilies(third.families)).toBeNull();
    expect(
      validateContactMeasurementFamilies([
        ...third.families,
        { ...third.families[0] },
      ])
    ).toBe("Contact family ids must be unique.");
  });

  it("keeps a resolved blank prefix stable through reorder and label rename", () => {
    const blank = ensureDefaultFreeformFamily(target("llcr", 0), { llcr: 4, cr_specified_current: 0 });
    const first = { ...blank.families[0], label: "Renamed", record_label: "Renamed" };
    const withSecond = { ...blank, families: [first, { ...first, family_id: "ff-llcr-6", family_ordinal: 1, label: "Second", record_label: "Second", record_prefix: "S2" }] };

    expect(blank.families[0]).toMatchObject({ family_id: "ff-llcr-5", label: "", record_prefix: "C5" });
    expect(moveContactFamily(withSecond, "ff-llcr-6", -1).families[1].record_prefix).toBe("C5");
    expect(resolveFreeformPrefix("", "High Power", 7)).toBe("HIGHPOWER");
    expect(resolveFreeformPrefix(" hp-1 ", "Ignored", 7)).toBe("HP1");
  });

  it("initializes record labels only for local freeform origins", () => {
    const source = {
      ...target("llcr", 0),
      families: [
        { family_id: "ff-llcr-1", family_ordinal: 0, label: "Legacy", count_per_sample: 1, record_label: "", record_prefix: "LEG", included: true, is_custom: true },
        { family_id: "ff-llcr-2", family_ordinal: 1, label: "Starter", count_per_sample: 1, record_label: "", record_prefix: "NEW", included: true, is_custom: true },
        { family_id: "ff-llcr-3", family_ordinal: 2, label: "Added", count_per_sample: 1, record_label: "", record_prefix: "ADD", included: true, is_custom: true },
        { family_id: "ff-llcr-4", family_ordinal: 3, label: "Template", count_per_sample: 1, record_label: "", record_prefix: "TMP", included: true, is_custom: true },
      ],
    };

    const initialized = initializeFreeformRecordLabelsForOrigins(source, {
      "ff-llcr-1": "persisted",
      "ff-llcr-2": "starter",
      "ff-llcr-3": "added",
      "ff-llcr-4": "template",
    });

    expect(initialized.families.map((family) => family.record_label)).toEqual([
      "", "Starter", "Added", "Template",
    ]);
  });

  it("preserves persisted provenance across prefix renewal and stale reapply normalization", () => {
    const renewedOrigins = moveFreeformFamilyOrigin(
      { "ff-llcr-1": "persisted" },
      "ff-llcr-1",
      "ff-llcr-2"
    );
    const staleLocalTarget = {
      ...target("llcr", 0),
      families: [{
        family_id: "ff-llcr-2",
        family_ordinal: 0,
        label: "Renamed legacy",
        count_per_sample: 1,
        record_label: "",
        record_prefix: "LEG2",
        included: true,
        is_custom: true,
      }],
    };

    const normalizedForReapply = initializeFreeformRecordLabelsForOrigins(
      staleLocalTarget,
      renewedOrigins
    );

    expect(renewedOrigins["ff-llcr-2"]).toBe("persisted");
    expect(normalizedForReapply.families[0].record_label).toBe("");
  });

  it("blocks a normalized duplicate prefix before a target command", () => {
    const families = [
      { family_id: "ff-llcr-1", family_ordinal: 0, label: "A", count_per_sample: 1, record_label: "A", record_prefix: "HP", included: true, is_custom: true },
      { family_id: "ff-llcr-2", family_ordinal: 1, label: "B", count_per_sample: 1, record_label: "B", record_prefix: "hp", included: true, is_custom: true },
    ];

    expect(validateContactMeasurementFamilies(families)).toBe("Contact family prefixes must be unique.");
  });

  it("blocks normalized duplicate freeform labels before a target command", () => {
    const families = [
      { family_id: "ff-llcr-1", family_ordinal: 0, label: "High Power", count_per_sample: 1, record_label: "First", record_prefix: "HP", included: true, is_custom: true },
      { family_id: "ff-llcr-2", family_ordinal: 1, label: " high power ", count_per_sample: 1, record_label: "Second", record_prefix: "SIG", included: true, is_custom: true },
    ];

    expect(validateContactMeasurementFamilies(families)).toBe("Contact family labels must be unique.");
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
    family_id_high_water_by_kind: { llcr: 0, cr_specified_current: 0 },
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
