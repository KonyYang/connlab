import type {
  DraftPrecheckIssue,
  IntakeCaseReview,
  IntakeCaseReviewField,
  IntakeCaseReviewItem,
  IntakePrecheckLookupOptions
} from "../../api/client";
import {
  emptyPrecheckSampleRow,
  PRECHECK_SAMPLE_COLUMNS,
  type PrecheckFieldSpec,
  type PrecheckSampleRow
} from "./precheckFieldConfig";

export function buildConfirmationBlockedReason(
  activeCase: IntakeCaseReviewItem,
  operatorConfirmed: boolean
): string | null {
  if (activeCase.confirmed_project_id) {
    return `Already confirmed into project ${activeCase.confirmed_project_id}.`;
  }
  if (!activeCase.confirm_allowed) {
    return "Required project request information is still missing.";
  }
  if (!operatorConfirmed) {
    return "Operator confirmation is required before project creation.";
  }
  return null;
}

export function preferredCaseId(
  review: IntakeCaseReview,
  initialCaseId?: string | null,
  currentCaseId?: string | null
): string | null {
  if (initialCaseId && review.cases.some((item) => item.case_id === initialCaseId)) {
    return initialCaseId;
  }
  if (currentCaseId && review.cases.some((item) => item.case_id === currentCaseId)) {
    return currentCaseId;
  }
  return review.cases[0]?.case_id ?? null;
}

export function editableKey(key: string, fields: IntakeCaseReviewField[]): boolean {
  return fields.some((field) => field.key === key);
}

export function editableValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }
  return typeof value === "object" ? JSON.stringify(value) : String(value);
}

export function fallbackValue(key: string, fields: IntakeCaseReviewField[]): string {
  const match = fields.find((field) => field.key === key);
  return match ? editableValue(match.value) : "";
}

export function fieldsWithLookupOptions(
  fields: PrecheckFieldSpec[],
  lookups: IntakePrecheckLookupOptions | null
): PrecheckFieldSpec[] {
  return fields.map((field) => {
    if (!field.lookupGroup || !lookups) {
      return field;
    }
    return {
      ...field,
      options: lookups[field.lookupGroup].map((option) => option.value)
    };
  });
}

export function issueLevelMap(issues: DraftPrecheckIssue[]): Map<string, string> {
  const levels = new Map<string, string>();
  for (const issue of issues) {
    if (!levels.has(issue.field_key) || issue.level === "error") {
      levels.set(issue.field_key, issue.level);
    }
  }
  return levels;
}

export function normalizedOptions(options: string[], value: string): string[] {
  if (!value || options.includes(value)) {
    return options;
  }
  return [value, ...options];
}

export function fieldClassName(issueLevel?: string): string {
  if (issueLevel === "error") {
    return "precheck-field precheck-field-error";
  }
  if (issueLevel === "warning") {
    return "precheck-field precheck-field-warning";
  }
  return "precheck-field";
}

export function dateInputValue(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) {
    return "";
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
    return trimmed;
  }
  const slashMatch = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(trimmed);
  if (!slashMatch) {
    return "";
  }
  const [, month, day, year] = slashMatch;
  return `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`;
}

export function normalizedSampleRows(rows: Record<string, unknown>[]): PrecheckSampleRow[] {
  if (rows.length === 0) {
    return [emptyPrecheckSampleRow()];
  }
  return rows.map((row) => ({
    ...Object.fromEntries(PRECHECK_SAMPLE_COLUMNS.map((column) => [column.key, cellText(row[column.key])])),
    part_number: mergedPartNumberRevision(row),
    lot_or_traceability: mergedTraceabilityLotInfo(row)
  }));
}

export function updateSampleRow(
  rows: PrecheckSampleRow[],
  rowIndex: number,
  key: string,
  value: string
): PrecheckSampleRow[] {
  return rows.map((row, index) => (index === rowIndex ? { ...row, [key]: value } : row));
}

export function copySampleRow(rows: PrecheckSampleRow[], rowIndex: number): PrecheckSampleRow[] {
  const copied = { ...(rows[rowIndex] ?? emptyPrecheckSampleRow()) };
  return [...rows.slice(0, rowIndex + 1), copied, ...rows.slice(rowIndex + 1)];
}

export function deleteSampleRow(rows: PrecheckSampleRow[], rowIndex: number): PrecheckSampleRow[] {
  if (rows.length <= 1) {
    return rows;
  }
  return rows.filter((_, index) => index !== rowIndex);
}

export function focusSampleRow(rowIndex: number): void {
  document
    .querySelector<HTMLInputElement>(
      `[data-sample-row="${rowIndex}"][data-sample-column="product_name"]`
    )
    ?.focus();
}

export function formatStatus(status: string): string {
  return status.split("_").filter(Boolean).map((part) => part[0]?.toUpperCase() + part.slice(1)).join(" ");
}

export function formatSourceType(sourceType: string): string {
  if (sourceType === "manual" || sourceType === "manual_entry") {
    return "Manual entry";
  }
  if (sourceType === "msg_import") {
    return "MSG package";
  }
  return formatStatus(sourceType);
}

function cellText(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }
  return String(value);
}

function mergedPartNumberRevision(row: Record<string, unknown>): string {
  const partNumber = cellText(row.part_number);
  const revision = cellText(row.revision);
  if (!partNumber || !revision || partNumber.toLowerCase().includes(revision.toLowerCase())) {
    return partNumber;
  }
  return `${partNumber} ${revision}`;
}

function mergedTraceabilityLotInfo(row: Record<string, unknown>): string {
  const traceability = cellText(row.lot_or_traceability);
  const manufacturingLot = cellText(row.manufacturing_lot_no);
  if (!traceability || !manufacturingLot || traceability.includes(manufacturingLot)) {
    return traceability;
  }
  return `${traceability} ${manufacturingLot}`;
}
