import type { IntakeCaseReviewField } from "../../api/client";
import {
  PRECHECK_SAMPLE_COLUMNS,
  type PrecheckFieldSpec,
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
  projectFields: PrecheckFieldSpec[],
  sourceFields: IntakeCaseReviewField[],
  values: Record<string, string>,
  sampleRows: PrecheckSampleRow[],
  requestedTestingRows: PrecheckRequestedTestingRow[]
): NewProjectRequiredState {
  const missingFieldKeys = new Set<string>();
  const missingSampleCells = new Set<string>();

  for (const field of projectFields) {
    if (field.required && !validFieldValue(field, values, sourceFields).trim()) {
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
  const rowsWithAnyContent = sampleRows
    .map((row, rowIndex) => ({ row, rowIndex }))
    .filter(({ row }) => rowHasAnySampleValue(row));
  const rowsToValidate = rowsWithAnyContent.length > 0
    ? rowsWithAnyContent
    : [{ row: sampleRows[0] ?? ({} as PrecheckSampleRow), rowIndex: 0 }];

  for (const { row, rowIndex } of rowsToValidate) {
    if (!String(row.product_name ?? "").trim()) {
      missingSampleCells.add(`${rowIndex}:product_name`);
    }
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

function validFieldValue(
  field: PrecheckFieldSpec,
  values: Record<string, string>,
  sourceFields: IntakeCaseReviewField[]
): string {
  const value = fieldValue(field.key, values, sourceFields).trim();
  if (!value || field.kind !== "select" || !field.options?.length) {
    return value;
  }
  return field.options.includes(value) ? value : "";
}

function rowHasAnySampleValue(row: PrecheckSampleRow): boolean {
  return PRECHECK_SAMPLE_COLUMNS.some((column) => String(row[column.key] ?? "").trim());
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
