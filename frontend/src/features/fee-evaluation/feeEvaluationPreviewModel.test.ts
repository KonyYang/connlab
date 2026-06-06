import { describe, expect, it } from "vitest";
import type { FeeEvaluationDraft, FeeEvaluationLineItem } from "../../api/client";
import {
  buildFeeEvaluationPreviewHeader,
  buildFeeEvaluationPreviewRows,
  buildFeeEvaluationPreviewTotals,
} from "./feeEvaluationPreviewModel";

describe("feeEvaluationPreviewModel", () => {
  it("maps fee draft rows into Testing Prices preview rows", () => {
    const rows = buildFeeEvaluationPreviewRows(createDraft());

    expect(rows).toEqual([
      {
        lineId: "fixture",
        groupLabel: "Group 1",
        spendTime: "Pending",
        description: "Fixture setup",
        unitPrice: "100.00",
        unitType: "group",
        units: "1",
        baseFee: "0.00",
        discount: "0%",
        testingFee: "100.00",
        status: "confirmed",
        reviewReason: null,
      },
      {
        lineId: "visual",
        groupLabel: "Group 1",
        spendTime: "Pending",
        description: "Visual Examination",
        unitPrice: "10.00",
        unitType: "photo",
        units: "Pending",
        baseFee: "",
        discount: "",
        testingFee: "Pending",
        status: "pending",
        reviewReason: "Photo count is not available from Matrix authority.",
      },
    ]);
  });

  it("builds totals that mirror the Excel completion state", () => {
    expect(buildFeeEvaluationPreviewTotals(createDraft(), "")).toEqual({
      testFeeTotal: "Pending Excel confirmation",
      workingHours: "Pending",
      labManpowerCost: "Pending",
      externalCost: "Pending",
      grandCost: "Pending",
      preparedBy: "Default on export",
      approvedBy: "Pending",
      confirmationLabel: "Pricing needs completion",
    });

    expect(
      buildFeeEvaluationPreviewTotals(
        { ...createDraft(), draft_status: "ready", total_fee: "125.00" },
        "Gentle Zeng"
      )
    ).toMatchObject({
      testFeeTotal: "125.00",
      approvedBy: "Gentle Zeng",
      confirmationLabel: "Pricing confirmed",
    });
  });

  it("builds the Testing Prices header from available frontend context", () => {
    expect(
      buildFeeEvaluationPreviewHeader({
        ltrNumber: "DL-2026-001",
        requestor: "Lab User",
      })
    ).toEqual({
      ltrNumber: "DL-2026-001",
      testDescription: "Pending",
      requestor: "Lab User",
      site: "Pending",
    });
  });
});

function createDraft(): FeeEvaluationDraft {
  return {
    header: {
      project_id: "P1",
      confirmed_matrix_id: "cmv-1",
      confirmed_revision: 1,
      pricing_rule_version_id: "fee_rules_v2026_06_03",
      pricing_source_file_name: "Testing Fee Evaluation-Even.xls",
      pricing_source_hash: "sha256:abc",
      pricing_effective_from: "2026-06-03",
      generated_at: "2026-06-04T10:00:00+08:00",
    },
    draft_status: "needs_review",
    total_fee: null,
    review_required_count: 1,
    warnings: [],
    groups: [
      {
        group_key: "g1",
        group_label: "Group 1",
        sample_quantity_expression: "5",
        line_items: [
          createLine({
            line_id: "fixture",
            review_required: false,
            test_item: "Fixture setup",
            unit_label: "group",
            unit_price: "100.00",
            units: "1",
            base_fee: "0.00",
            discount_percent: "0",
            testing_fee: "100.00",
          }),
          createLine({
            line_id: "visual",
            status: "review_required",
            review_required: true,
            review_reason: "Photo count is not available from Matrix authority.",
            test_item: "Visual Examination",
            calculation_strategy: "per_photo",
            unit_label: "photo",
            unit_price: "10.00",
            units: null,
            base_fee: null,
            discount_percent: null,
            testing_fee: null,
          }),
        ],
      },
    ],
  };
}

function createLine(overrides: Partial<FeeEvaluationLineItem>): FeeEvaluationLineItem {
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
    sample_quantity_expression: "5",
    confirmed_row_id: "row-1",
    source_row_id: "source-row-1",
    row_order: 1,
    test_item: "Fixture setup",
    section: "6.1",
    method: "Fixture",
    condition: "",
    requirement: "",
    step_tokens: ["1"],
    matched_rule_id: "fee_rule_fixture",
    matched_rule_version_id: "fee_rules_v2026_06_03",
    matched_rule_name: "Fixture setup",
    match_reason: "exact",
    calculation_strategy: "fixed_per_group",
    unit_label: "group",
    unit_price: "100.00",
    units: "1",
    base_fee: "0.00",
    discount_percent: "0",
    testing_fee: "100.00",
    warnings: [],
    ...overrides,
  };
}
