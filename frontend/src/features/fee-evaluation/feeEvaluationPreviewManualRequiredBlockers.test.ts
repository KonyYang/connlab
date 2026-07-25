import { describe, expect, it } from "vitest";
import type {
  FeeEvaluationDraft,
  FeeEvaluationLineItem,
} from "../../api/client";
import {
  applyFeeEvaluationPreviewEdits,
  buildFeeEvaluationPreviewRows,
  buildFeeEvaluationUpdateBlockers,
} from "./feeEvaluationPreviewModel";

function completeLine(
  overrides: Partial<FeeEvaluationLineItem>
): FeeEvaluationLineItem {
  return {
    line_id: "line",
    status: "calculated",
    review_required: false,
    review_reason: null,
    confirmed_matrix_id: "cmv-1",
    confirmed_revision: 1,
    group_key: "g1",
    group_label: "Group 1",
    confirmed_group_id: "cmg-1",
    sample_quantity_expression: "1",
    confirmed_row_id: "row-1",
    source_row_id: "source-row-1",
    row_order: 1,
    test_item: "Line",
    section: "6.1",
    method: "",
    condition: "",
    requirement: "",
    step_tokens: ["1"],
    matched_rule_id: null,
    matched_rule_version_id: null,
    matched_rule_name: null,
    match_reason: "fixture",
    calculation_strategy: null,
    spend_time: "0",
    unit_label: "reading",
    unit_price: "1",
    units: "1",
    base_fee: "0",
    discount_percent: "0",
    testing_fee: "1",
    field_metadata: [],
    warnings: [],
    ...overrides,
  };
}

function createDraft(): FeeEvaluationDraft {
  const samplePreparation = completeLine({
    line_id: "sample-preparation:g1",
    test_item: "Sample preparation",
    confirmed_row_id: "",
    source_row_id: null,
    row_order: 0,
    step_tokens: [],
    spend_time: "0.5",
    unit_label: "sample",
    unit_price: "50",
    units: "1",
    base_fee: "0",
    discount_percent: "100",
    testing_fee: "0",
  });
  const dwvLine = completeLine({
    line_id: "manual-unit-price",
    status: "review_required",
    review_required: true,
    review_reason: "Confirm 1-minute/2-minute price.",
    test_item: "DIELECTRIC WITHSTANDING VOLTAGE",
    method: "DWV",
    step_tokens: ["1"],
    match_reason: "manual review",
    unit_price: null,
    testing_fee: null,
    field_metadata: [
      {
        field: "unit_price",
        state: "manual_required",
        source: "DWV",
        message: "Confirm 1-minute/2-minute price.",
      },
      {
        field: "testing_fee",
        state: "manual_required",
        source: "DWV",
        message: "Confirm 1-minute/2-minute price.",
      },
    ],
  });
  const reportPreparation = completeLine({
    line_id: "manual-report-preparation",
    group_key: "",
    group_label: "",
    confirmed_group_id: "",
    sample_quantity_expression: "",
    confirmed_row_id: "",
    source_row_id: null,
    row_order: 0,
    test_item: "Report preparation",
    step_tokens: [],
    spend_time: "4",
    unit_label: "report",
    unit_price: "600",
    units: "1",
    base_fee: "0",
    discount_percent: "100",
    testing_fee: "0",
  });

  return {
    header: {
      project_id: "P1",
      confirmed_matrix_id: "cmv-1",
      confirmed_revision: 1,
      pricing_rule_version_id: "fee_rules_fixture",
      pricing_source_file_name: "fixture.json",
      pricing_source_hash: "sha256:fixture",
      pricing_effective_from: null,
      generated_at: "2026-07-25T00:00:00Z",
    },
    draft_status: "needs_review",
    total_fee: null,
    review_required_count: 1,
    groups: [
      {
        group_key: "g1",
        group_label: "Group 1",
        sample_quantity_expression: "1",
        manual_line_items: [samplePreparation],
        line_items: [dwvLine],
      },
    ],
    manual_line_items: [reportPreparation],
    warnings: [],
  };
}

describe("Fee Evaluation manual-required blockers", () => {
  it("reports Unit Price as the only blocker for a manual-required DWV line", () => {
    const rows = applyFeeEvaluationPreviewEdits(
      buildFeeEvaluationPreviewRows(createDraft()),
      {}
    );

    expect(rows.map((row) => row.lineId)).toEqual([
      "sample-preparation:g1",
      "manual-unit-price:1:0",
      "manual-report-preparation",
    ]);
    expect(rows.find((row) => row.lineId === "manual-unit-price:1:0")).toMatchObject({
      unitPrice: "",
      unitType: "per reading",
      units: "1",
      baseFee: "0",
      testingFee: "Pending",
    });

    const blockers = buildFeeEvaluationUpdateBlockers({
      rows,
      totals: {
        testingFeeTotal: "1",
        workingHours: "1",
        labManpowerCost: "1",
        externalCost: "0",
        grandCost: "1",
      },
    });

    expect(blockers).toHaveLength(1);
    expect(blockers[0]).toMatchObject({
      rowLabel: "Group 1, Step 1, DIELECTRIC WITHSTANDING VOLTAGE",
      fields: ["Unit Price"],
      rowMessage: "Complete Unit Price.",
    });
  });
});
