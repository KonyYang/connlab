// Shared acceptance samples for the Fee Evaluation summary derivation seam.
//
// Authority: docs/fee_confirmation_contract.md. The JSON fixture in
// tests/contract_fixtures is the common acceptance oracle: backend and
// frontend both independently derive the five summary fields and both must
// reproduce these samples.
//
// This test drives the real client data path at model level:
// preview rows -> applyFeeEvaluationPreviewEdits (default edit pass) ->
// buildFeeEvaluationEditedExportPayload (the confirm request payload) and
// the same label builders the page uses for the Confirm summary.
// Numeric fields are compared after normalizing $ , and blanks; display
// fields use exact strings per contract display rules.

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import {
  applyFeeEvaluationPreviewEdits,
  buildFeeEvaluationEditedExportPayload,
  buildFeeEvaluationLabManpowerCost,
  buildFeeEvaluationPreviewGrandCost,
  buildFeeEvaluationPreviewScopeTotal,
  buildFeeEvaluationPreviewWorkingHours,
  type FeeEvaluationPreviewRow,
} from "./feeEvaluationPreviewModel";

type AcceptanceRow = {
  row_kind?: string;
  unit_price: string;
  units: string;
  base_fee: string;
  discount: string;
  testing_fee: string;
  spend_time: string;
  confirmed_group_id?: string;
  group_label?: string;
};

type AcceptanceCase = {
  id: string;
  matrix_rows: AcceptanceRow[];
  manual_rows: AcceptanceRow[];
  condition_confirmation_spend_time: string;
  external_cost: string;
  lab_manpower_hourly_rate: string;
  expected_summary: Record<string, string>;
  covers: string;
};

const fixturePath = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../../../../tests/contract_fixtures/fee_summary_acceptance_cases.json"
);
const cases = (JSON.parse(readFileSync(fixturePath, "utf-8")) as { cases: AcceptanceCase[] }).cases;

function numeric(value: string): number {
  const normalized = value.trim().replace(/[$,\s]/g, "");
  return Number(normalized === "" ? "0" : normalized);
}

function previewRow(overrides: Partial<FeeEvaluationPreviewRow> & { lineId: string }): FeeEvaluationPreviewRow {
  return {
    sourceLineId: overrides.lineId,
    confirmedGroupId: "cmg-1",
    confirmedRowId: "row-1",
    groupKey: "g1",
    groupLabel: "Group 1",
    stepToken: "1",
    stepIndex: 0,
    spendTime: "0",
    description: "Acceptance sample row",
    unitPrice: "0",
    unitType: "hour",
    units: "1",
    baseFee: "0",
    discount: "0%",
    testingFee: "0",
    notes: "",
    status: "confirmed",
    reviewReason: null,
    fieldMetadata: [],
    rowKind: "matrix_step",
    groupTone: "tone-a",
    ...overrides,
  };
}

function previewRowsFromCase(testCase: AcceptanceCase): FeeEvaluationPreviewRow[] {
  const matrixRows = testCase.matrix_rows.map((row, index) =>
    previewRow({
      lineId: `line-${index + 1}`,
      sourceLineId: `line-${index + 1}`,
      confirmedGroupId: row.confirmed_group_id ?? `cmg-${index + 1}`,
      confirmedRowId: `row-${index + 1}`,
      groupLabel: row.group_label ?? "Group 1",
      spendTime: row.spend_time,
      unitPrice: row.unit_price,
      units: row.units,
      baseFee: row.base_fee,
      discount: row.discount,
      testingFee: row.testing_fee,
      groupTone: index % 2 === 0 ? "tone-a" : "tone-b",
    })
  );
  const manualRows = testCase.manual_rows.map((row, index) =>
    previewRow({
      lineId:
        row.row_kind === "report_preparation"
          ? "manual-report-preparation"
          : `sample-preparation:${index + 1}`,
      rowKind:
        row.row_kind === "report_preparation" ? "manual_trailing" : "sample_preparation",
      groupTone: "manual",
      confirmedGroupId: row.confirmed_group_id ?? "",
      groupKey: "",
      groupLabel: row.group_label ?? "",
      spendTime: row.spend_time,
      unitPrice: row.unit_price,
      units: row.units,
      baseFee: row.base_fee,
      discount: row.discount,
      testingFee: row.testing_fee,
    })
  );
  return [...matrixRows, ...manualRows];
}

describe("Fee summary acceptance samples (frontend model path)", () => {
  it.each(cases.map((testCase) => [testCase.id, testCase] as const))(
    "%s: preview rows -> payload and summary labels match the shared sample",
    (_id, testCase) => {
      const editedRows = applyFeeEvaluationPreviewEdits(previewRowsFromCase(testCase), {});
      const costValues = {
        conditionConfirmationSpendTime: testCase.condition_confirmation_spend_time,
        externalCost: testCase.external_cost,
        externalCostNote: "",
        labManpowerHourlyRate: testCase.lab_manpower_hourly_rate,
      };
      const payload = buildFeeEvaluationEditedExportPayload(editedRows, costValues);
      const expected = testCase.expected_summary;

      // Display-format labels exactly as the page sends them on Confirm.
      const testingFeeTotal = buildFeeEvaluationPreviewScopeTotal(editedRows, "all");
      const workingHours = buildFeeEvaluationPreviewWorkingHours(
        editedRows,
        costValues.conditionConfirmationSpendTime
      );
      const rawHours = buildFeeEvaluationPreviewWorkingHours(
        editedRows,
        costValues.conditionConfirmationSpendTime,
        false
      );
      const labManpowerCost = buildFeeEvaluationLabManpowerCost(
        rawHours,
        costValues.labManpowerHourlyRate
      );
      const grandCost = buildFeeEvaluationPreviewGrandCost(editedRows, costValues.externalCost);

      expect(testingFeeTotal).toBe(expected.testing_fee_total);
      expect(workingHours).toBe(expected.working_hours);
      expect(labManpowerCost).toBe(expected.lab_manpower_cost);
      expect(grandCost).toBe(expected.grand_cost);

      // The confirm request payload derives from the same edited rows.
      const allRowFees = [
        ...testCase.matrix_rows.map((row) => row.testing_fee),
        ...testCase.manual_rows.map((row) => row.testing_fee),
      ];
      const payloadRowFees = [
        ...payload.rows.map((row) => row.testing_fee),
        ...payload.manual_rows.map((row) => row.testing_fee),
      ];
      expect(payloadRowFees).toEqual(allRowFees);
      expect(numeric(payload.summary.external_cost)).toBe(numeric(expected.external_cost));
      expect(payload.summary.condition_confirmation_spend_time).toBe(
        testCase.condition_confirmation_spend_time.trim() || "0"
      );
      expect(payload.summary.lab_manpower_hourly_rate).toBe(testCase.lab_manpower_hourly_rate);

      // Payload spends round-trip so the backend recomputes the same totals.
      const payloadSpends = [
        ...payload.rows.map((row) => row.spend_time),
        ...payload.manual_rows.map((row) => row.spend_time),
      ];
      const allSpends = [
        ...testCase.matrix_rows.map((row) => row.spend_time),
        ...testCase.manual_rows.map((row) => row.spend_time),
      ];
      expect(payloadSpends).toEqual(allSpends);
    }
  );
});
