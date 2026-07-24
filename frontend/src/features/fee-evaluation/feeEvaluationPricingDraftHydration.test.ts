import { describe, expect, it } from "vitest";
import type { FeeEvaluationEditedFileExportRequest } from "../../api/client";
import type { FeeEvaluationPreviewRow } from "./feeEvaluationPreviewModel";
import { hydrateFeeEvaluationPricingDraft } from "./feeEvaluationPricingDraftHydration";

describe("feeEvaluationPricingDraftHydration", () => {
  it("keeps compatibility placeholders from replacing current automatic defaults", () => {
    const row = previewRow({
      unitPrice: "25",
      unitType: "per sample",
      units: "5",
      testingFee: "125",
    });

    const result = hydrateFeeEvaluationPricingDraft(
      [row],
      savedPayload({
        spend_time: "0",
        unit_price: "0",
        unit_type: "Pending",
        units: "1",
        base_fee: "0",
        discount: "0%",
        testing_fee: "0",
        notes: "",
      }),
      "current_v2_compatibility"
    );

    expect(result).toMatchObject({
      edits: {},
      appliedRowCount: 0,
      unmatchedRowCount: 0,
    });
  });

  it("preserves the server reviewed-rebase candidate without browser fallback", () => {
    const row = previewRow({
      spendTime: "2",
      unitPrice: "25",
      unitType: "per sample",
      units: "5",
      baseFee: "50",
      discount: "5%",
      notes: "browser default",
    });

    const result = hydrateFeeEvaluationPricingDraft(
      [row],
      savedPayload({
        spend_time: "",
        unit_price: "77",
        unit_type: "Pending",
        units: "",
        base_fee: "0",
        discount: "12%",
        testing_fee: "",
        notes: "",
      }, {
        condition_confirmation_spend_time: "",
        external_cost: "0",
        external_cost_note: "",
        lab_manpower_hourly_rate: "",
      }),
      "server_rebase_candidate"
    );

    expect(result.edits[row.lineId]).toEqual({
      spendTime: "",
      unitPrice: "77",
      unitType: "Pending",
      units: "",
      baseFee: "0",
      discount: "12%",
      notes: "",
    });
    expect(result.costPreviewValues).toEqual({
      conditionConfirmationSpendTime: "",
      externalCost: "0",
      externalCostNote: "",
      labManpowerHourlyRate: "",
    });
    expect(result.appliedRowCount).toBe(1);
    expect(result.unmatchedRowCount).toBe(0);
  });

  it("keeps manual-required blanks blank in compatibility mode", () => {
    const row = previewRow({
      unitPrice: "",
      units: "",
      fieldMetadata: [
        metadata("unitPrice", "manual_required"),
        metadata("units", "manual_required"),
      ],
    });

    const result = hydrateFeeEvaluationPricingDraft(
      [row],
      savedPayload({
        unit_price: "",
        units: "",
      }),
      "current_v2_compatibility"
    );

    expect(result.edits[row.lineId]).toMatchObject({
      unitPrice: "",
      units: "",
    });
  });

  it("does not apply a saved row to a different stable identity", () => {
    const row = previewRow();
    const payload = savedPayload();
    payload.rows[0].confirmed_row_id = "other-row";

    const result = hydrateFeeEvaluationPricingDraft(
      [row],
      payload,
      "server_rebase_candidate"
    );

    expect(result.edits).toEqual({});
    expect(result.appliedRowCount).toBe(0);
    expect(result.unmatchedRowCount).toBe(1);
  });
});

function previewRow(
  overrides: Partial<FeeEvaluationPreviewRow> = {}
): FeeEvaluationPreviewRow {
  return {
    lineId: "cmv-1:g1:row-1:1:0",
    sourceLineId: "cmv-1:g1:row-1:1:0",
    confirmedGroupId: "group-1",
    confirmedRowId: "row-1",
    groupKey: "g1",
    groupLabel: "Group 1",
    stepToken: "1",
    stepIndex: 0,
    spendTime: "1",
    description: "Visual Examination",
    unitPrice: "10",
    unitType: "per sample",
    units: "1",
    baseFee: "0",
    discount: "0%",
    testingFee: "10",
    notes: "",
    status: "confirmed",
    reviewReason: null,
    fieldMetadata: [],
    rowKind: "matrix_step",
    groupTone: "tone-a",
    ...overrides,
  };
}

function metadata(
  field: "unitPrice" | "units",
  state: "manual_required"
): FeeEvaluationPreviewRow["fieldMetadata"][number] {
  return { field, state, source: "Confirmed authority", message: "Review required." };
}

function savedPayload(
  rowOverrides: Partial<FeeEvaluationEditedFileExportRequest["rows"][number]> = {},
  summaryOverrides: Partial<FeeEvaluationEditedFileExportRequest["summary"]> = {}
): FeeEvaluationEditedFileExportRequest {
  return {
    rows: [
      {
        source_line_id: "cmv-1:g1:row-1:1:0",
        confirmed_group_id: "group-1",
        confirmed_row_id: "row-1",
        step_token: "1",
        step_index: 0,
        spend_time: "1",
        unit_price: "10",
        unit_type: "per sample",
        units: "1",
        base_fee: "0",
        discount: "0%",
        testing_fee: "10",
        notes: "saved",
        ...rowOverrides,
      },
    ],
    manual_rows: [],
    summary: {
      condition_confirmation_spend_time: "0",
      external_cost: "0",
      external_cost_note: "",
      lab_manpower_hourly_rate: "200",
      ...summaryOverrides,
    },
  };
}
