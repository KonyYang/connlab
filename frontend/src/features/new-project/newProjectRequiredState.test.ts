import { describe, expect, it } from "vitest";

import type { IntakeCaseReviewField } from "../../api/client";
import type { PrecheckFieldSpec } from "../precheck/precheckFieldConfig";
import type { NewProjectSetupConfirmationValues } from "./NewProjectSetupConfirmationPanel";
import { buildNewProjectRequiredState, buildSetupRequiredActions } from "./newProjectRequiredState";

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
    expect(result.actions).toEqual([
      { targetId: "intake-application-business_unit", label: "Select Business Unit" }
    ]);
  });

  it("locates missing data by the displayed sample row and distinguishes empty from invalid quantity", () => {
    const state = buildNewProjectRequiredState(
      [{ key: "email", label: "Email", required: true }],
      [field("email", "Email", "a@example.com")],
      { email: "" },
      [{}, { part_number: "A" }, { product_name: "B", quantity: "TBD" }],
      [{ test_to_be_performed: "", applicable_specification: "Customer" }]
    );
    expect(state.actions).toEqual([
      { targetId: "intake-application-email", label: "Enter Email" },
      { targetId: "intake-sample-1-product_name", label: "Sample 2 · Enter Product Name" },
      { targetId: "intake-sample-1-quantity", label: "Sample 2 · Enter Quantity" },
      { targetId: "intake-sample-2-quantity", label: expect.stringMatching(/Sample 3.*Quantity.*number/i) },
      { targetId: "intake-application-confidential", label: expect.stringMatching(/yes or no.*confidential/i) },
      { targetId: "intake-application-subcontract", label: expect.stringMatching(/yes or no.*subcontract/i) },
      { targetId: "intake-application-requested_testing", label: "Enter Tests to be Performed" }
    ]);
    expect(state.missingCount).toBe(state.actions.length);
  });

  it("asks for the first sample when every row is empty", () => {
    const state = buildNewProjectRequiredState([], [], { confidential: "No", subcontract: "Yes" }, [{}, {}], [
      { test_to_be_performed: "Visual inspection", applicable_specification: "" }
    ]);
    expect(state.actions.map((action) => action.targetId)).toEqual([
      "intake-sample-0-product_name", "intake-sample-0-quantity"
    ]);
  });
});

describe("buildSetupRequiredActions", () => {
  const ready: NewProjectSetupConfirmationValues = {
    sampleDescription: "Connector", testItem: "Inspection", testTypeInSheet: "Qualification",
    projectLeader: "Lee", labPerformingTests: "Dongguan", ltrMode: "auto", specifiedLtrNumber: ""
  };

  it("shows an action for each missing setup control in form order", () => {
    const actions = buildSetupRequiredActions({
      ...ready, sampleDescription: " ", testItem: "", testTypeInSheet: "", projectLeader: "", labPerformingTests: ""
    });
    expect(actions.map(({ key, targetId, label }) => [key, targetId, label])).toEqual([
      ["sample_description", "intake-setup-sample_description", "Enter Sample Description"],
      ["test_item", "intake-setup-test_item", "Enter Test Item"],
      ["test_type_in_sheet", "intake-setup-test_type_in_sheet", "Select Test Type in sheet"],
      ["project_leader", "intake-setup-project_leader", "Enter Project Leader"],
      ["lab_performing_tests", "intake-setup-lab_performing_tests", "Select Lab Performing the Tests"]
    ]);
  });

  it("asks for a specified LTR only when selected and gives a format example for invalid input", () => {
    expect(buildSetupRequiredActions({ ...ready, specifiedLtrNumber: "123" })).toEqual([]);
    const specified = { ...ready, ltrMode: "specified" as const };
    expect(buildSetupRequiredActions(specified)).toEqual([{
      key: "specified_ltr_number", targetId: "intake-setup-specified_ltr_number", label: "Enter specified LTR number"
    }]);
    expect(buildSetupRequiredActions({ ...specified, specifiedLtrNumber: "123" })).toEqual([{
      key: "specified_ltr_number", targetId: "intake-setup-specified_ltr_number", label: expect.stringMatching(/LTR.*DL-\d{4}-\d{2}-\d{3}.*A1/i)
    }]);
    expect(buildSetupRequiredActions({ ...specified, specifiedLtrNumber: "A1" })).toEqual([]);
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
