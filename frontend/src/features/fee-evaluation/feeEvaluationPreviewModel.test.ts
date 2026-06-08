import { describe, expect, it } from "vitest";
import type { FeeEvaluationDraft, FeeEvaluationLineItem } from "../../api/client";
import {
  applyFeeEvaluationPreviewEdits,
  buildFeeEvaluationCostRisk,
  buildFeeEvaluationLabManpowerCost,
  buildFeeEvaluationPreviewHeader,
  buildFeeEvaluationPreviewGrandCost,
  buildFeeEvaluationPreviewRows,
  buildFeeEvaluationPreviewScopeTotal,
  buildFeeEvaluationPreviewTotals,
  buildFeeEvaluationPreviewWorkingHours,
  calculateFeePreviewTestingFee,
  FEE_UNIT_TYPE_OPTIONS,
  filterFeeEvaluationPreviewRowsForScope,
  hydrateFeeEvaluationPreviewEditsFromSavedDraft,
} from "./feeEvaluationPreviewModel";

describe("feeEvaluationPreviewModel", () => {
  it("maps fee draft rows into Testing Prices preview rows", () => {
    const rows = buildFeeEvaluationPreviewRows(createDraft());

    expect(rows.map((row) => [row.groupLabel, row.stepToken, row.description])).toEqual([
      ["Group 1", "1", "Fixture setup"],
      ["Group 1", "2", "Visual Examination"],
      ["Group 1", "3", "Visual Examination"],
      ["", "-", "Report preparation"],
    ]);
    expect(rows[0]).toMatchObject({
      lineId: "fixture:1:0",
      sourceLineId: "fixture:1:0",
      confirmedGroupId: "cmg-1",
      confirmedRowId: "row-1",
      stepIndex: 0,
      rowKind: "matrix_step",
      groupTone: "tone-a",
      unitPrice: "100.00",
      unitType: "group",
      units: "1",
      baseFee: "0.00",
      discount: "0%",
      testingFee: "100.00",
      status: "confirmed",
      reviewReason: null,
    });
    expect(rows[1]).toMatchObject({
      lineId: "visual:2:0",
      rowKind: "matrix_step",
      groupTone: "tone-a",
      unitPrice: "10.00",
      unitType: "photo",
      units: "Pending",
      baseFee: "",
      discount: "",
      testingFee: "Pending",
      status: "pending",
      reviewReason: "Photo count is not available from Matrix authority.",
    });
    expect(rows.at(-1)).toMatchObject({
      rowKind: "manual_trailing",
      groupTone: "manual",
      reviewReason: "Manual completion in Fee Form.",
    });
  });

  it("builds totals that mirror the Excel completion state", () => {
    expect(buildFeeEvaluationPreviewTotals(createDraft(), "")).toEqual({
      testFeeTotal: "Pending Excel confirmation",
      workingHours: "0.0",
      labManpowerCost: "0",
      externalCost: "0",
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

  it("summarizes the selected preview group only when the scope is fully priced", () => {
    const rows = buildFeeEvaluationPreviewRows({
      ...createDraft(),
      groups: [
        {
          group_key: "g1",
          group_label: "Group 1",
          sample_quantity_expression: "5",
          line_items: [
            createLine({
              line_id: "group-1-fixture",
              group_label: "Group 1",
              testing_fee: "100.00",
            }),
          ],
        },
        {
          group_key: "g2",
          group_label: "Group 2",
          sample_quantity_expression: "5",
          line_items: [
            createLine({
              line_id: "group-2-visual",
              group_label: "Group 2",
              review_required: true,
              testing_fee: null,
            }),
          ],
        },
      ],
    });

    expect(buildFeeEvaluationPreviewScopeTotal(rows, "Group 1")).toBe("100.00");
    expect(buildFeeEvaluationPreviewScopeTotal(rows, "Group 2")).toBe("Pending");
    expect(buildFeeEvaluationPreviewScopeTotal(rows, "all")).toBe("Pending");
  });

  it("calculates local editable Testing Fee from unit price, units, discount, and base fee", () => {
    expect(
      calculateFeePreviewTestingFee({
        unitPrice: "100",
        units: "2",
        baseFee: "5",
        discount: "10",
      })
    ).toBe("185");
    expect(
      calculateFeePreviewTestingFee({
        unitPrice: "100",
        units: "2",
        baseFee: "5",
        discount: "10%",
      })
    ).toBe("185");
    expect(
      calculateFeePreviewTestingFee({
        unitPrice: "100",
        units: "2",
        baseFee: "",
        discount: "",
      })
    ).toBe("200");
    expect(
      calculateFeePreviewTestingFee({
        unitPrice: "Pending",
        units: "2",
        baseFee: "",
        discount: "",
      })
    ).toBe("Pending");
  });

  it("applies local row edits and maps canonical unit labels to operator labels", () => {
    const rows = buildFeeEvaluationPreviewRows(createDraft());
    const editedRows = applyFeeEvaluationPreviewEdits(rows, {
      "visual:2:0": {
        unitPrice: "10",
        unitType: "per time",
        units: "3",
        baseFee: "2",
        discount: "10%",
      },
    });

    expect(FEE_UNIT_TYPE_OPTIONS).toContain("per time");
    expect(editedRows.find((row) => row.lineId === "fixture:1:0")).toMatchObject({
      unitType: "group",
      testingFee: "100",
    });
    expect(editedRows.find((row) => row.lineId === "visual:2:0")).toMatchObject({
      unitType: "per time",
      testingFee: "29",
    });
    expect(editedRows.find((row) => row.lineId === "visual:3:1")).toMatchObject({
      unitType: "per photo",
      testingFee: "10",
    });
  });

  it("defaults editable preview rows to zero-cost calculable values", () => {
    const rows = applyFeeEvaluationPreviewEdits(buildFeeEvaluationPreviewRows(createDraft()), {});

    expect(rows.find((row) => row.lineId === "visual:2:0")).toMatchObject({
      spendTime: "0",
      unitPrice: "10.00",
      units: "1",
      baseFee: "0",
      discount: "0%",
      testingFee: "10",
    });
    expect(rows.find((row) => row.lineId === "manual-report-preparation")).toMatchObject({
      spendTime: "0",
      unitPrice: "0",
      units: "1",
      baseFee: "0",
      discount: "0%",
      testingFee: "0",
    });
  });

  it("builds working hours from row spend time and condition confirmation time", () => {
    const rows = applyFeeEvaluationPreviewEdits(buildFeeEvaluationPreviewRows(createDraft()), {
      "fixture:1:0": { spendTime: "1.5" },
      "visual:2:0": { spendTime: "2" },
    });

    expect(buildFeeEvaluationPreviewWorkingHours(rows, "0.5")).toBe("4.0");
  });

  it("filters preview totals to the selected Matrix group scope", () => {
    const rows = applyFeeEvaluationPreviewEdits(
      buildFeeEvaluationPreviewRows(createDraftWithTwoGroups()),
      {
        "fixture:1:0": { spendTime: "1" },
        "visual:2:0": { spendTime: "2" },
        "group-2-fixture:1:0": { spendTime: "3" },
      }
    );

    expect(filterFeeEvaluationPreviewRowsForScope(rows, "Group 1")).toHaveLength(3);
    expect(filterFeeEvaluationPreviewRowsForScope(rows, "Group 2")).toHaveLength(1);
    expect(
      buildFeeEvaluationPreviewWorkingHours(
        filterFeeEvaluationPreviewRowsForScope(rows, "Group 2"),
        "0"
      )
    ).toBe("3.0");
  });

  it("calculates Lab manpower cost from scoped working hours and editable hourly rate", () => {
    expect(buildFeeEvaluationLabManpowerCost("13.0", "200")).toBe("2600");
    expect(buildFeeEvaluationLabManpowerCost("13", "225.5")).toBe("2932");
    expect(buildFeeEvaluationLabManpowerCost("Pending", "200")).toBe("Pending");
  });

  it("uses edited step rows for scope totals and Grand Cost", () => {
    const rows = applyFeeEvaluationPreviewEdits(buildFeeEvaluationPreviewRows(createDraft()), {
      "visual:2:0": { unitPrice: "10", units: "2", baseFee: "", discount: "" },
      "visual:3:1": { unitPrice: "10", units: "3", baseFee: "", discount: "" },
      "manual-report-preparation": { unitPrice: "5", units: "1", baseFee: "", discount: "" },
    });

    expect(buildFeeEvaluationPreviewScopeTotal(rows, "Group 1")).toBe("150.00");
    expect(buildFeeEvaluationPreviewScopeTotal(rows, "all")).toBe("155.00");
    expect(buildFeeEvaluationPreviewGrandCost(rows, "25")).toBe("180.00");
  });

  it("treats expanded step rows as independent pricing rows for preview totals", () => {
    const rows = buildFeeEvaluationPreviewRows({
      ...createDraft(),
      groups: [
        {
          group_key: "g1",
          group_label: "Group 1",
          sample_quantity_expression: "5",
          line_items: [
            createLine({
              line_id: "multi-step-priced",
              step_tokens: ["1", "2"],
              testing_fee: "10.00",
            }),
          ],
        },
      ],
    });

    expect(buildFeeEvaluationPreviewScopeTotal(rows, "Group 1")).toBe("20.00");
  });

  it("keeps one fallback preview row when a Matrix line has no step tokens", () => {
    const rows = buildFeeEvaluationPreviewRows({
      ...createDraft(),
      groups: [
        {
          group_key: "g1",
          group_label: "Group 1",
          sample_quantity_expression: "5",
          line_items: [createLine({ line_id: "no-step", step_tokens: [] })],
        },
      ],
    });

    expect(rows[0]).toMatchObject({
      lineId: "no-step:no-step:0",
      stepToken: "-",
      description: "Fixture setup",
    });
  });

  it("assigns alternating group tones by Matrix group block", () => {
    const rows = buildFeeEvaluationPreviewRows(createDraftWithTwoGroups());

    expect(rows.find((row) => row.groupLabel === "Group 1")?.groupTone).toBe("tone-a");
    expect(rows.find((row) => row.groupLabel === "Group 2")?.groupTone).toBe("tone-b");
    expect(rows.at(-1)?.groupTone).toBe("manual");
  });

  it("sorts Matrix preview rows by numeric step token inside each group", () => {
    const rows = buildFeeEvaluationPreviewRows(createDraftWithUnsortedStepTokens());
    const matrixRows = rows.filter((row) => row.rowKind === "matrix_step");

    expect(
      matrixRows
        .filter((row) => row.groupLabel === "Group 1")
        .map((row) => row.stepToken)
    ).toEqual(["1", "2", "3", "4", "5", "6", "7", "8", "9"]);
    expect(
      matrixRows
        .filter((row) => row.groupLabel === "Group 2")
        .map((row) => row.stepToken)
    ).toEqual(["1", "2", "11"]);
    expect(rows.slice(-1).map((row) => row.description)).toEqual([
      "Report preparation",
    ]);
  });

  it("keeps non-numeric step tokens stable after numeric tokens", () => {
    const rows = buildFeeEvaluationPreviewRows({
      ...createDraft(),
      groups: [
        {
          group_key: "g1",
          group_label: "Group 1",
          sample_quantity_expression: "5",
          line_items: [
            createLine({ line_id: "marker", step_tokens: ["A", "2", "1(a)", "1"] }),
          ],
        },
      ],
    });

    expect(
      rows.filter((row) => row.rowKind === "matrix_step").map((row) => row.stepToken)
    ).toEqual(["1", "2", "A", "1(a)"]);
  });

  it("hydrates saved pricing draft rows through stable backend identity", () => {
    const rows = buildFeeEvaluationPreviewRows(createDraft());
    const result = hydrateFeeEvaluationPreviewEditsFromSavedDraft(rows, {
      rows: [
        {
          source_line_id: "visual:2:0",
          confirmed_group_id: "cmg-1",
          confirmed_row_id: "row-1",
          step_token: "2",
          step_index: 0,
          spend_time: "1.5",
          unit_price: "25",
          unit_type: "per sample",
          units: "2",
          base_fee: "5",
          discount: "10%",
          testing_fee: "50",
          notes: "saved note",
        },
      ],
      manual_rows: [
        {
          row_kind: "report_preparation",
          spend_time: "0.5",
          unit_price: "100",
          unit_type: "per report",
          units: "1",
          base_fee: "0",
          discount: "0%",
          testing_fee: "100",
          notes: "",
        },
      ],
      summary: {
        condition_confirmation_spend_time: "0.25",
        external_cost: "150",
        external_cost_note: "tooling",
        lab_manpower_hourly_rate: "220",
      },
    });

    expect(result.unmatchedRowCount).toBe(0);
    expect(result.appliedRowCount).toBe(2);
    expect(result.edits["visual:2:0"]).toMatchObject({
      spendTime: "1.5",
      unitPrice: "25",
      notes: "saved note",
    });
    expect(result.edits["manual-report-preparation"]).toMatchObject({
      unitType: "per report",
    });
    expect("testingFee" in result.edits["manual-report-preparation"]).toBe(false);
    expect(result.costPreviewValues).toEqual({
      conditionConfirmationSpendTime: "0.25",
      externalCost: "150",
      externalCostNote: "tooling",
      labManpowerHourlyRate: "220",
    });
  });

  it("does not apply saved pricing draft rows that no longer match the preview", () => {
    const result = hydrateFeeEvaluationPreviewEditsFromSavedDraft(
      buildFeeEvaluationPreviewRows(createDraft()),
      {
        rows: [
          {
            source_line_id: "missing",
            confirmed_group_id: "cmg-1",
            confirmed_row_id: "missing",
            step_token: "1",
            step_index: 0,
            spend_time: "1",
            unit_price: "10",
            unit_type: "per sample",
            units: "1",
            base_fee: "0",
            discount: "0%",
            testing_fee: "10",
            notes: "",
          },
        ],
        summary: {
          condition_confirmation_spend_time: "0",
          external_cost: "0",
          external_cost_note: "",
          lab_manpower_hourly_rate: "200",
        },
      }
    );

    expect(result.appliedRowCount).toBe(0);
    expect(result.unmatchedRowCount).toBe(1);
    expect(result.edits).toEqual({});
  });

  it("builds a loss warning only from local preview numeric costs", () => {
    expect(
      buildFeeEvaluationCostRisk({
        grandCost: "100",
        labManpowerCost: "125",
      })
    ).toEqual({
      severity: "loss_warning",
      message: "Lab manpower cost exceeds Grand Cost. Review pricing before sending the fee form.",
    });

    expect(
      buildFeeEvaluationCostRisk({
        grandCost: "200",
        labManpowerCost: "125",
      })
    ).toEqual({ severity: "none", message: null });

    expect(
      buildFeeEvaluationCostRisk({
        grandCost: "",
        labManpowerCost: "125",
      })
    ).toEqual({ severity: "none", message: null });
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
            step_tokens: ["2", "3"],
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

function createDraftWithTwoGroups(): FeeEvaluationDraft {
  const draft = createDraft();
  return {
    ...draft,
    groups: [
      draft.groups[0],
      {
        group_key: "g2",
        group_label: "Group 2",
        sample_quantity_expression: "3",
        line_items: [
          createLine({
            line_id: "group-2-fixture",
            group_key: "g2",
            group_label: "Group 2",
            confirmed_group_id: "cmg-2",
            confirmed_row_id: "row-2",
            step_tokens: ["1"],
          }),
        ],
      },
    ],
  };
}

function createDraftWithUnsortedStepTokens(): FeeEvaluationDraft {
  return {
    ...createDraft(),
    groups: [
      {
        group_key: "g1",
        group_label: "Group 1",
        sample_quantity_expression: "5",
        line_items: [
          createLine({ line_id: "g1-s1", test_item: "Step 1", step_tokens: ["1"] }),
          createLine({ line_id: "g1-s9", test_item: "Step 9", step_tokens: ["9"] }),
          createLine({ line_id: "g1-s2", test_item: "Step 2", step_tokens: ["2"] }),
          createLine({ line_id: "g1-s4", test_item: "Step 4", step_tokens: ["4"] }),
          createLine({ line_id: "g1-s6", test_item: "Step 6", step_tokens: ["6"] }),
          createLine({ line_id: "g1-s8", test_item: "Step 8", step_tokens: ["8"] }),
          createLine({ line_id: "g1-s3", test_item: "Step 3", step_tokens: ["3"] }),
          createLine({ line_id: "g1-s7", test_item: "Step 7", step_tokens: ["7"] }),
          createLine({ line_id: "g1-s5", test_item: "Step 5", step_tokens: ["5"] }),
        ],
      },
      {
        group_key: "g2",
        group_label: "Group 2",
        sample_quantity_expression: "3",
        line_items: [
          createLine({
            line_id: "g2-s1",
            group_key: "g2",
            group_label: "Group 2",
            step_tokens: ["1"],
          }),
          createLine({
            line_id: "g2-s11",
            group_key: "g2",
            group_label: "Group 2",
            step_tokens: ["11"],
          }),
          createLine({
            line_id: "g2-s2",
            group_key: "g2",
            group_label: "Group 2",
            step_tokens: ["2"],
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
