import { describe, expect, it } from "vitest";

import type { IntakeCaseReviewField } from "../../api/client";
import type { PrecheckFieldSpec } from "../precheck/precheckFieldConfig";
import { buildNewProjectRequiredState } from "./newProjectRequiredState";

describe("buildNewProjectRequiredState", () => {
  it("treats parsed select values outside lookup options as missing", () => {
    const fields: PrecheckFieldSpec[] = [
      {
        key: "business_unit",
        label: "Business Unit",
        kind: "select",
        required: true,
        options: ["Power Solutions", "Other"]
      },
      {
        key: "manufacturing_site",
        label: "Mfg. Site",
        kind: "select",
        required: true,
        options: ["Nantong", "Dongguan"]
      }
    ];
    const sourceFields: IntakeCaseReviewField[] = [
      field("business_unit", "Business Unit", "Power"),
      field("manufacturing_site", "Mfg. Site", "Nantong"),
      field("confidential", "Confidential", "No"),
      field("subcontract", "Subcontract", "Yes")
    ];

    const result = buildNewProjectRequiredState(
      fields,
      sourceFields,
      {},
      [{ product_name: "Connector", quantity: "2" }],
      [{ test_to_be_performed: "Qualification", applicable_specification: "Customer" }]
    );

    expect(result.missingFieldKeys.has("business_unit")).toBe(true);
    expect(result.missingFieldKeys.has("manufacturing_site")).toBe(false);
  });
});

function field(key: string, label: string, value: string): IntakeCaseReviewField {
  return {
    key,
    label,
    value,
    required: true,
    missing: false
  };
}
