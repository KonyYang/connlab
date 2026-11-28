import type { IntakeCaseReviewField } from "../../api/client";
import {
  PRECHECK_CONSENT_LABELS,
  PRECHECK_REQUESTED_TESTING_COLUMNS,
  PRECHECK_SAMPLE_COLUMNS,
  type PrecheckFieldSpec,
  type PrecheckRequestedTestingRow,
  type PrecheckSampleRow
} from "../precheck/precheckFieldConfig";
import { editableValue, requestedTestingText } from "../precheck/precheckReviewSelectors";
import {
  NEW_PROJECT_SETUP_LABELS,
  type NewProjectSetupConfirmationValues
} from "./NewProjectSetupConfirmationPanel";

export type RequiredAction = { targetId: string; label: string };

export type NewProjectRequiredState = {
  actions: RequiredAction[];
  missingFieldKeys: Set<string>;
  missingSampleCells: Set<string>;
  missingCount: number;
};

export function buildSetupRequiredActions(
  values: NewProjectSetupConfirmationValues
): Array<RequiredAction & { key: string }> {
  const actions: Array<RequiredAction & { key: string }> = [];
  const fields = [
    ["sample_description", values.sampleDescription, "Enter"],
    ["test_item", values.testItem, "Enter"],
    ["test_type_in_sheet", values.testTypeInSheet, "Select"],
    ["project_leader", values.projectLeader, "Enter"],
    ["lab_performing_tests", values.labPerformingTests, "Select"]
  ] as const;
  for (const [key, value, verb] of fields) {
    if (!value.trim()) {
      actions.push({
        key,
        targetId: `intake-setup-${key}`,
        label: `${verb} ${NEW_PROJECT_SETUP_LABELS[key]}`
      });
    }
  }
  if (values.ltrMode === "specified" && !isValidSpecifiedLtrInput(values.specifiedLtrNumber)) {
    actions.push({
      key: "specified_ltr_number",
      targetId: "intake-setup-specified_ltr_number",
      label: values.specifiedLtrNumber.trim()
        ? "Correct LTR number (e.g. DL-2026-05-001 or A1)"
        : "Enter specified LTR number"
    });
  }
  return actions;
}

export function isValidSpecifiedLtrInput(value: string): boolean {
  const input = value.trim();
  if (!input) {
    return false;
  }
  const baseOrFull = /^DL-(\d{4})-(\d{2})-(\d{3})([A-Z][A-Z0-9]*)?$/i.exec(input);
  if (baseOrFull) {
    const year = Number(baseOrFull[1]);
    const month = Number(baseOrFull[2]);
    const sequence = Number(baseOrFull[3]);
    return year >= 2000 && month >= 1 && month <= 12 && sequence >= 1;
  }
  return /^[A-Z][A-Z0-9]*$/i.test(input);
}

export function buildNewProjectRequiredState(
  projectFields: PrecheckFieldSpec[],
  sourceFields: IntakeCaseReviewField[],
  values: Record<string, string>,
  sampleRows: PrecheckSampleRow[],
  requestedTestingRows: PrecheckRequestedTestingRow[]
): NewProjectRequiredState {
  const actions: RequiredAction[] = [];
  const missingFieldKeys = new Set<string>();
  const missingSampleCells = new Set<string>();

  function addFieldAction(key: string, label: string) {
    missingFieldKeys.add(key);
    actions.push({ targetId: `intake-application-${key}`, label });
  }

  for (const field of projectFields) {
    if (field.required && !validFieldValue(field, values, sourceFields).trim()) {
      const verb = field.kind === "select" ? "Select" : "Enter";
      addFieldAction(field.key, field.requiredActionLabel ?? `${verb} ${field.label}`);
    }
  }
  const rowsWithAnyContent = sampleRows
    .map((row, rowIndex) => ({ row, rowIndex }))
    .filter(({ row }) => rowHasAnySampleValue(row));
  const rowsToValidate = rowsWithAnyContent.length > 0
    ? rowsWithAnyContent
    : [{ row: sampleRows[0] ?? ({} as PrecheckSampleRow), rowIndex: 0 }];

  for (const { row, rowIndex } of rowsToValidate) {
    for (const column of PRECHECK_SAMPLE_COLUMNS) {
      if (column.key !== "product_name" && column.key !== "quantity") continue;
      const value = String(row[column.key] ?? "").trim();
      const needsNumber = column.key === "quantity" && value !== "" && !/\d/.test(value);
      if (!value || needsNumber) {
        missingSampleCells.add(`${rowIndex}:${column.key}`);
        actions.push({
          targetId: `intake-sample-${rowIndex}-${column.key}`,
          label: `Sample ${rowIndex + 1} · Enter ${column.label}${needsNumber ? " with a number" : ""}`
        });
      }
    }
  }
  for (const [key, question] of Object.entries(PRECHECK_CONSENT_LABELS)) {
    if (!fieldValue(key, values, sourceFields).trim()) {
      addFieldAction(key, `Choose Yes or No · ${question}`);
    }
  }
  if (!requestedTestingText(requestedTestingRows).trim()) {
    addFieldAction("requested_testing", `Enter ${PRECHECK_REQUESTED_TESTING_COLUMNS[0].label}`);
  }
  return {
    actions,
    missingFieldKeys,
    missingSampleCells,
    missingCount: actions.length
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
