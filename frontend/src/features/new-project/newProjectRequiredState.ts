import type { IntakeCaseReviewField } from "../../api/client";
import {
  PRECHECK_PROJECT_FIELDS,
  PRECHECK_SAMPLE_COLUMNS,
  type PrecheckRequestedTestingRow,
  type PrecheckSampleRow
} from "../precheck/precheckFieldConfig";
import { editableValue, requestedTestingText } from "../precheck/precheckReviewSelectors";

export type NewProjectRequiredState = {
  missingFieldKeys: Set<string>;
  missingSampleCells: Set<string>;
  missingCount: number;
};

const LOWER_REQUIRED_KEYS = ["requested_testing", "confidential", "subcontract"] as const;

export function buildNewProjectRequiredState(
  sourceFields: IntakeCaseReviewField[],
  values: Record<string, string>,
  sampleRows: PrecheckSampleRow[],
  requestedTestingRows: PrecheckRequestedTestingRow[]
): NewProjectRequiredState {
  const missingFieldKeys = new Set<string>();
  const missingSampleCells = new Set<string>();

  for (const field of PRECHECK_PROJECT_FIELDS) {
    if (field.required && !fieldValue(field.key, values, sourceFields).trim()) {
      missingFieldKeys.add(field.key);
    }
  }
  for (const key of LOWER_REQUIRED_KEYS) {
    if (key === "requested_testing") {
      if (!requestedTestingText(requestedTestingRows).trim()) {
        missingFieldKeys.add(key);
      }
    } else if (!fieldValue(key, values, sourceFields).trim()) {
      missingFieldKeys.add(key);
    }
  }
  const rowsWithProduct = sampleRows
    .map((row, rowIndex) => ({ row, rowIndex }))
    .filter(({ row }) => String(row.product_name ?? "").trim());
  if (rowsWithProduct.length === 0) {
    missingSampleCells.add("0:product_name");
  }
  for (const { row, rowIndex } of rowsWithProduct) {
    if (!/\d/.test(String(row.quantity ?? ""))) {
      missingSampleCells.add(`${rowIndex}:quantity`);
    }
  }
  return {
    missingFieldKeys,
    missingSampleCells,
    missingCount: missingFieldKeys.size + missingSampleCells.size
  };
}

function fieldValue(
  key: string,
  values: Record<string, string>,
  sourceFields: IntakeCaseReviewField[]
): string {
  if (key in values) {
    return values[key] ?? "";
  }
  const source = sourceFields.find((field) => field.key === key);
  return source ? editableValue(source.value) : "";
}
