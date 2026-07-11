import { describe, expect, it } from "vitest";
import type { MatrixStepContactPlan, MatrixStepQuantityItem } from "../../api/client";
import {
  DEFAULT_CONTACT_PLAN_PROFILES,
  addCustomContactFamily,
  applyContactPlanToBlankTargets,
  contactMeasurementKindForItem,
  filterNonContactStepQuantities,
  hydrateUniformContactPlanProfiles,
  removeCustomContactFamily,
  updateContactTargetCoverage,
  updateContactFamilyCount,
  updateContactFamilyIncluded,
} from "./matrixContactMeasurementPlanSelectors";

describe("matrixContactMeasurementPlanSelectors", () => {
  it("detects LLCR and CR specified-current targets only", () => {
    expect(contactMeasurementKindForItem(item({ test_item: "LLCR" }))).toBe("llcr");
    expect(
      contactMeasurementKindForItem(item({ test_item: "Contact Resistance (Power)" }))
    ).toBe("cr_specified_current");
    expect(contactMeasurementKindForItem(item({ test_item: "Visual Examination" }))).toBeNull();
  });

  it("applies contact family readings only to blank contact targets", () => {
    let profiles = updateContactFamilyCount(
      DEFAULT_CONTACT_PLAN_PROFILES,
      "llcr",
      "high_power_pin",
      "2"
    );
    profiles = updateContactFamilyCount(profiles, "llcr", "low_power_pin", "3");
    profiles = updateContactFamilyCount(profiles, "llcr", "signal_pin", "4");
    const result = applyContactPlanToBlankTargets(
      [
        item({ draft_row_id: "llcr-row", test_item: "LLCR" }),
        item({
          draft_row_id: "manual-row",
          test_item: "LLCR",
          test_points_per_sample: "8",
          readings_per_point: "1",
          contact_points_per_sample: "8",
          total_readings: "8",
        }),
        item({ draft_row_id: "visual-row", test_item: "Visual Examination" }),
      ],
      profiles
    );

    expect(result.changed).toBe(true);
    expect(result.items[0]).toMatchObject({
      test_points_per_sample: "9",
      readings_per_point: "1",
      contact_points_per_sample: "9",
      total_readings: "9",
      source: "matrix_contact_plan",
      review_required: false,
    });
    expect(result.items[1].test_points_per_sample).toBe("8");
    expect(result.items[2].source).toBe("manual_required");
  });

  it("keeps contact targets out of the legacy Step quantity panel", () => {
    const items = [
      item({ draft_row_id: "llcr-row", test_item: "Low Level Contact Resistance" }),
      item({ draft_row_id: "visual-row", test_item: "Visual Examination" }),
    ];

    expect(filterNonContactStepQuantities(items).map((entry) => entry.draft_row_id)).toEqual([
      "visual-row",
    ]);
  });

  it("adds a custom family and preserves an excluded target without applying counts", () => {
    const profiles = addCustomContactFamily(DEFAULT_CONTACT_PLAN_PROFILES, "llcr");
    const custom = profiles.llcr.at(-1);
    expect(custom).toMatchObject({
      familyLabel: "Custom contact",
      recordPrefix: "CUSTOM",
      isCustom: true,
    });

    const selected = updateContactTargetCoverage(
      [item({ test_item: "LLCR" })],
      {
        draft_group_id: "group-1",
        draft_row_id: "row-1",
        step_sequence: 1,
        step_suffix_note: null,
      },
      false,
      "Not applicable to this group."
    );
    expect(selected[0].contact_plan).toMatchObject({
      included: false,
      coverage_status: "excluded",
      exclusion_reason: "Not applicable to this group.",
    });
    expect(
      applyContactPlanToBlankTargets(selected, profiles).items[0].test_points_per_sample
    ).toBeNull();
  });

  it("assigns monotonic custom family IDs across removal and persisted draft reload", () => {
    let profiles = addCustomContactFamily(DEFAULT_CONTACT_PLAN_PROFILES, "llcr");
    const firstId = profiles.llcr.at(-1)?.familyId;
    profiles = addCustomContactFamily(profiles, "llcr");
    const secondId = profiles.llcr.at(-1)?.familyId;
    profiles = removeCustomContactFamily(profiles, "llcr", firstId ?? "");
    profiles = addCustomContactFamily(profiles, "llcr");
    const thirdId = profiles.llcr.at(-1)?.familyId;

    expect([firstId, secondId, thirdId]).toEqual([
      "custom-llcr-1",
      "custom-llcr-2",
      "custom-llcr-3",
    ]);
    const reloaded = addCustomContactFamily(
      DEFAULT_CONTACT_PLAN_PROFILES,
      "llcr",
      ["custom-llcr-3"]
    );
    expect(reloaded.llcr.at(-1)?.familyId).toBe("custom-llcr-4");

    profiles = updateContactFamilyCount(profiles, "llcr", "high_power_pin", "1");
    profiles = updateContactFamilyIncluded(profiles, "llcr", "low_power_pin", false);
    profiles = updateContactFamilyIncluded(profiles, "llcr", "signal_pin", false);
    const savedPlan = applyContactPlanToBlankTargets([item({ test_item: "LLCR" })], profiles)
      .items[0].contact_plan;
    const savedIds = savedPlan?.families.map((family) => family.family_id) ?? [];
    expect(new Set(savedIds).size).toBe(savedIds.length);
  });

  it("hydrates a uniform persisted contact plan without collapsing divergent targets", () => {
    const uniformPlan: MatrixStepContactPlan = {
      contact_kind: "llcr" as const,
      coverage_status: "eligible",
      included: true,
      exclusion_reason: null,
      is_override: false,
      readings_per_sample: "9",
      families: [
        {
          family_id: "high_power_pin",
          family_label: "High Power Pin",
          count_per_sample: "4",
          record_label: "High Power Pin contact",
          record_prefix: "HP",
          included: true,
          is_custom: false,
        },
      ],
    };
    const hydrated = hydrateUniformContactPlanProfiles([
      item({ draft_row_id: "llcr-1", contact_plan: uniformPlan }),
      item({ draft_row_id: "llcr-2", contact_plan: uniformPlan }),
    ]);

    const uniformProfiles = hydrated.profiles;
    expect(uniformProfiles?.llcr).toBeDefined();
    if (!uniformProfiles?.llcr) {
      throw new Error("Expected the uniform LLCR profile to hydrate.");
    }
    expect(uniformProfiles.llcr[0]).toMatchObject({
      familyId: "high_power_pin",
      countPerSample: "4",
      recordPrefix: "HP",
    });
    expect(hydrated.reviewMessage).toBeNull();

    const divergent = hydrateUniformContactPlanProfiles([
      item({ draft_row_id: "llcr-1", contact_plan: uniformPlan }),
      item({
        draft_row_id: "llcr-2",
        contact_plan: {
          ...uniformPlan,
          readings_per_sample: "5",
          families: [{ ...uniformPlan.families[0], count_per_sample: "5" }],
        },
      }),
    ]);

    expect(divergent.profiles).toBeNull();
    expect(divergent.reviewMessage).toBe("Contact plans differ by target. Review target coverage.");
  });

  it("keeps override targets out of the common profile and requests review", () => {
    const persistedPlan: MatrixStepContactPlan = {
      contact_kind: "llcr",
      coverage_status: "eligible",
      included: true,
      exclusion_reason: null,
      is_override: false,
      readings_per_sample: "4",
      families: [
        {
          family_id: "high_power_pin",
          family_label: "High Power Pin",
          count_per_sample: "4",
          record_label: "High Power Pin contact",
          record_prefix: "HP",
          included: true,
          is_custom: false,
        },
      ],
    };
    const expectedReview = "Contact plans differ by target. Review target coverage.";

    const normalWithOverride = hydrateUniformContactPlanProfiles([
      item({ draft_row_id: "llcr-normal", contact_plan: persistedPlan }),
      item({
        draft_row_id: "llcr-override",
        contact_plan: { ...persistedPlan, is_override: true },
      }),
    ]);
    expect(normalWithOverride.profiles).toBeNull();
    expect(normalWithOverride.reviewMessage).toBe(expectedReview);

    const overrideOnly = hydrateUniformContactPlanProfiles([
      item({
        draft_row_id: "llcr-override",
        contact_plan: { ...persistedPlan, is_override: true },
      }),
    ]);
    expect(overrideOnly.profiles).toBeNull();
    expect(overrideOnly.reviewMessage).toBe(expectedReview);
  });
});

function item(overrides: Partial<MatrixStepQuantityItem>): MatrixStepQuantityItem {
  return {
    draft_group_id: "group-1",
    draft_row_id: "row-1",
    step_sequence: 1,
    step_suffix_note: null,
    raw_token: "1",
    test_item: "LLCR",
    test_points_per_sample: null,
    readings_per_point: null,
    contact_points_per_sample: null,
    total_readings: null,
    source: "manual_required",
    review_required: true,
    review_reason: "Confirm Step quantity values.",
    ...overrides,
  };
}
