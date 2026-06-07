import type { FeeEvaluationDraft, FeeEvaluationLineItem } from "../../api/client";

export const FEE_UNIT_TYPE_OPTIONS = [
  "per sample",
  "per reading",
  "per contact",
  "per cycle",
  "per time",
  "per hour",
  "per day",
  "per photo",
  "per report",
] as const;

export type FeeEvaluationEditableField =
  | "spendTime"
  | "unitPrice"
  | "unitType"
  | "units"
  | "baseFee"
  | "discount"
  | "notes";

export type FeeEvaluationRowEdits = Partial<
  Record<FeeEvaluationEditableField, string>
>;

export type FeeEvaluationPreviewEditState = Record<
  string,
  FeeEvaluationRowEdits
>;

export type FeeEvaluationPreviewRow = {
  lineId: string;
  sourceLineId: string;
  groupLabel: string;
  stepToken: string;
  spendTime: string;
  description: string;
  unitPrice: string;
  unitType: string;
  units: string;
  baseFee: string;
  discount: string;
  testingFee: string;
  notes: string;
  status: "confirmed" | "pending";
  reviewReason: string | null;
  rowKind: "matrix_step" | "manual_trailing";
  groupTone: "tone-a" | "tone-b" | "manual";
};

export type FeeEvaluationPreviewTotals = {
  testFeeTotal: string;
  workingHours: string;
  labManpowerCost: string;
  externalCost: string;
  grandCost: string;
  preparedBy: string;
  approvedBy: string;
  confirmationLabel: string;
};

export type FeeEvaluationPreviewHeader = {
  ltrNumber: string;
  testDescription: string;
  requestor: string;
  site: string;
};

export type FeeEvaluationCostRisk = {
  severity: "none" | "loss_warning";
  message: string | null;
};

type ExpandedStepRow = FeeEvaluationPreviewRow & {
  stepSortValue: number | null;
  sourceLineOrder: number;
  sourceTokenOrder: number;
};

export function buildFeeEvaluationPreviewHeader(input: {
  ltrNumber: string | null;
  requestor: string | null | undefined;
}): FeeEvaluationPreviewHeader {
  return {
    ltrNumber: displayOrPending(input.ltrNumber),
    testDescription: "Pending",
    requestor: displayOrPending(input.requestor),
    site: "Pending",
  };
}

export function buildFeeEvaluationPreviewRows(
  draft: FeeEvaluationDraft | null
): FeeEvaluationPreviewRow[] {
  const rows =
    draft?.groups.flatMap((group, groupIndex) => {
      const groupTone = groupIndex % 2 === 0 ? "tone-a" : "tone-b";
      return group.line_items
        .flatMap((line, lineIndex) => buildMatrixStepRows(line, groupTone, lineIndex))
        .sort(comparePreviewRows)
        .map(stripPreviewSortMetadata);
    }) ?? [];
  return [...rows, ...buildManualTrailingRows()];
}

export function buildFeeEvaluationPreviewTotals(
  draft: FeeEvaluationDraft | null,
  approvedBy: string
): FeeEvaluationPreviewTotals {
  const normalizedApprovedBy = approvedBy.trim();
  return {
    testFeeTotal: draft?.total_fee ?? "Pending Excel confirmation",
    workingHours: "0.0",
    labManpowerCost: "0",
    externalCost: "0",
    grandCost: "Pending",
    preparedBy: "Default on export",
    approvedBy: normalizedApprovedBy.length > 0 ? normalizedApprovedBy : "Pending",
    confirmationLabel:
      draft?.draft_status === "ready" ? "Pricing confirmed" : "Pricing needs completion",
  };
}

export function buildFeeEvaluationPreviewScopeTotal(
  rows: FeeEvaluationPreviewRow[],
  groupFilter: string
): string {
  const scopedRows = filterFeeEvaluationPreviewRowsForScope(rows, groupFilter);
  if (scopedRows.length === 0) {
    return "Pending";
  }
  let total = 0;
  for (const row of scopedRows) {
    const parsed = Number(row.testingFee);
    if (!Number.isFinite(parsed)) {
      return "Pending";
    }
    total += parsed;
  }
  return total.toFixed(2);
}

export function filterFeeEvaluationPreviewRowsForScope(
  rows: FeeEvaluationPreviewRow[],
  groupFilter: string
): FeeEvaluationPreviewRow[] {
  if (groupFilter === "all") {
    return rows;
  }
  return rows.filter(
    (row) => row.rowKind === "matrix_step" && row.groupLabel === groupFilter
  );
}

export function buildFeeEvaluationPreviewGrandCost(
  rows: FeeEvaluationPreviewRow[],
  externalCost: string,
  pendingLabel = "Pending"
): string {
  if (rows.length === 0) {
    return pendingLabel;
  }
  let total = 0;
  for (const row of rows) {
    const parsed = Number(row.testingFee);
    if (!Number.isFinite(parsed)) {
      return pendingLabel;
    }
    total += parsed;
  }
  const external =
    externalCost.trim().length > 0
      ? parsePreviewNumber(externalCost)
      : 0;
  if (external === null) {
    return pendingLabel;
  }
  return (total + external).toFixed(2);
}

export function buildFeeEvaluationLabManpowerCost(
  workingHours: string,
  hourlyRate: string
): string {
  const parsedWorkingHours = parsePreviewNumber(workingHours);
  const parsedHourlyRate = parsePreviewNumber(hourlyRate);
  if (parsedWorkingHours === null || parsedHourlyRate === null) {
    return "Pending";
  }
  return formatPreviewWholeAmount(parsedWorkingHours * parsedHourlyRate);
}

export function buildFeeEvaluationPreviewWorkingHours(
  rows: FeeEvaluationPreviewRow[],
  conditionConfirmationSpendTime: string
): string {
  let total = 0;
  for (const row of rows) {
    const parsed = parsePreviewNumber(row.spendTime);
    if (parsed === null) {
      return "Pending";
    }
    total += parsed;
  }
  const conditionSpendTime =
    conditionConfirmationSpendTime.trim().length > 0
      ? parsePreviewNumber(conditionConfirmationSpendTime)
      : 0;
  if (conditionSpendTime === null) {
    return "Pending";
  }
  return (total + conditionSpendTime).toFixed(1);
}

export function applyFeeEvaluationPreviewEdits(
  rows: FeeEvaluationPreviewRow[],
  edits: FeeEvaluationPreviewEditState
): FeeEvaluationPreviewRow[] {
  return rows.map((row) => {
    const rowEdits = edits[row.lineId] ?? {};
    const unitPrice = rowEdits.unitPrice ?? editableDefault(row.unitPrice, "0");
    const units = rowEdits.units ?? editableDefault(row.units, "1");
    const baseFee = rowEdits.baseFee ?? editableDefault(row.baseFee, "0");
    const discount = rowEdits.discount ?? editableDefault(row.discount, "0%");
    return {
      ...row,
      spendTime: rowEdits.spendTime ?? editableDefault(row.spendTime, "0"),
      unitPrice,
      unitType: rowEdits.unitType ?? formatUnitTypeForPreview(row.unitType),
      units,
      baseFee,
      discount,
      testingFee: calculateFeePreviewTestingFee({
        unitPrice,
        units,
        baseFee,
        discount,
      }),
      notes: rowEdits.notes ?? row.notes,
    };
  });
}

export function calculateFeePreviewTestingFee(input: {
  unitPrice: string;
  units: string;
  baseFee: string;
  discount: string;
}): string {
  const unitPrice = parseRequiredEditableNumber(input.unitPrice);
  const units = parseRequiredEditableNumber(input.units);
  const baseFee = parseOptionalEditableNumber(input.baseFee);
  const discount = parseEditableDiscount(input.discount);
  if (
    unitPrice === null ||
    units === null ||
    baseFee === null ||
    discount === null
  ) {
    return "Pending";
  }
  return formatPreviewWholeAmount(unitPrice * units * (1 - discount) + baseFee);
}

export function buildFeeEvaluationCostRisk(input: {
  grandCost: string;
  labManpowerCost: string;
}): FeeEvaluationCostRisk {
  const grandCost = parsePreviewNumber(input.grandCost);
  const labManpowerCost = parsePreviewNumber(input.labManpowerCost);
  if (grandCost === null || labManpowerCost === null) {
    return { severity: "none", message: null };
  }
  if (labManpowerCost > grandCost) {
    return {
      severity: "loss_warning",
      message:
        "Lab manpower cost exceeds Grand Cost. Review pricing before sending the fee form.",
    };
  }
  return { severity: "none", message: null };
}

function buildMatrixStepRows(
  line: FeeEvaluationLineItem,
  groupTone: "tone-a" | "tone-b",
  sourceLineOrder: number
): ExpandedStepRow[] {
  const stepTokens = line.step_tokens.length > 0 ? line.step_tokens : [""];
  return stepTokens.map((stepToken, index) => {
    const normalizedStepToken = stepToken.trim();
    const stepDisplay = normalizedStepToken.length > 0 ? normalizedStepToken : "-";
    const lineIdToken =
      normalizedStepToken.length > 0 ? normalizedStepToken : "no-step";
    return {
      lineId: `${line.line_id}:${lineIdToken}:${index}`,
      sourceLineId: line.line_id,
      groupLabel: line.group_label,
      stepToken: stepDisplay,
      spendTime: "Pending",
      description: line.test_item,
      unitPrice: pendingValue(line.unit_price),
      unitType: line.unit_label || line.calculation_strategy || "Pending",
      units: pendingValue(line.units),
      baseFee: blankValue(line.base_fee),
      discount: formatDiscount(line.discount_percent),
      testingFee: pendingValue(line.testing_fee),
      notes: "",
      status: line.review_required ? "pending" : "confirmed",
      reviewReason: line.review_reason,
      rowKind: "matrix_step" as const,
      groupTone,
      stepSortValue: parseStepSortValue(stepDisplay),
      sourceLineOrder,
      sourceTokenOrder: index,
    };
  });
}

function comparePreviewRows(a: ExpandedStepRow, b: ExpandedStepRow): number {
  if (a.stepSortValue !== null && b.stepSortValue !== null) {
    if (a.stepSortValue !== b.stepSortValue) {
      return a.stepSortValue - b.stepSortValue;
    }
  } else if (a.stepSortValue !== null) {
    return -1;
  } else if (b.stepSortValue !== null) {
    return 1;
  }
  if (a.sourceLineOrder !== b.sourceLineOrder) {
    return a.sourceLineOrder - b.sourceLineOrder;
  }
  return a.sourceTokenOrder - b.sourceTokenOrder;
}

function stripPreviewSortMetadata(row: ExpandedStepRow): FeeEvaluationPreviewRow {
  const { stepSortValue, sourceLineOrder, sourceTokenOrder, ...previewRow } = row;
  return previewRow;
}

function parseStepSortValue(value: string): number | null {
  const normalized = value.trim();
  if (!/^\d+$/.test(normalized)) {
    return null;
  }
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function buildManualTrailingRows(): FeeEvaluationPreviewRow[] {
  return [
    buildManualTrailingRow("manual-report-preparation", "Report preparation"),
  ];
}

function buildManualTrailingRow(
  lineId: string,
  description: string
): FeeEvaluationPreviewRow {
  return {
    lineId,
    sourceLineId: lineId,
    groupLabel: "",
    stepToken: "-",
    spendTime: "Pending",
    description,
    unitPrice: "Pending",
    unitType: "Pending",
    units: "Pending",
    baseFee: "",
    discount: "",
    testingFee: "Pending",
    notes: "",
    status: "pending",
    reviewReason: "Manual completion in Fee Form.",
    rowKind: "manual_trailing",
    groupTone: "manual",
  };
}

function pendingValue(value: string | null | undefined): string {
  const normalized = value?.trim() ?? "";
  return normalized.length > 0 ? normalized : "Pending";
}

function blankValue(value: string | null | undefined): string {
  return value?.trim() ?? "";
}

function formatDiscount(value: string | null | undefined): string {
  const normalized = value?.trim() ?? "";
  return normalized.length > 0 ? `${normalized}%` : "";
}

function displayOrPending(value: string | null | undefined): string {
  const normalized = value?.trim() ?? "";
  return normalized.length > 0 ? normalized : "Pending";
}

function formatUnitTypeForPreview(value: string): string {
  const normalized = value.trim().toLowerCase();
  if (!normalized || normalized === "pending") {
    return "Pending";
  }
  const map: Record<string, string> = {
    sample: "per sample",
    specimen: "per sample",
    reading: "per reading",
    contact: "per contact",
    cycle: "per cycle",
    time: "per time",
    hour: "per hour",
    day: "per day",
    photo: "per photo",
    report: "per report",
    "per sample": "per sample",
    "per reading": "per reading",
    "per contact": "per contact",
    "per cycle": "per cycle",
    "per time": "per time",
    "per hour": "per hour",
    "per day": "per day",
    "per photo": "per photo",
    "per report": "per report",
  };
  return map[normalized] ?? value.trim();
}

function parseRequiredEditableNumber(value: string): number | null {
  const normalized = normalizeEditableNumber(value);
  if (!normalized) {
    return null;
  }
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function parseOptionalEditableNumber(value: string): number | null {
  const normalized = normalizeEditableNumber(value);
  if (!normalized) {
    return 0;
  }
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function parseEditableDiscount(value: string): number | null {
  const normalized = normalizeEditableNumber(value.replace(/%/g, ""));
  if (!normalized) {
    return 0;
  }
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed / 100 : null;
}

function normalizeEditableNumber(value: string): string {
  const normalized = value.trim();
  if (!normalized || normalized.toLowerCase() === "pending") {
    return "";
  }
  return normalized.replace(/[$,\s]/g, "");
}

function editableDefault(value: string, fallback: string): string {
  const normalized = value.trim();
  if (!normalized || normalized.toLowerCase() === "pending") {
    return fallback;
  }
  return normalized;
}

function parsePreviewNumber(value: string): number | null {
  const normalized = value.trim().replace(/[$,\s]/g, "");
  if (!normalized) {
    return null;
  }
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function formatPreviewWholeAmount(value: number): string {
  if (!Number.isFinite(value)) {
    return "Pending";
  }
  return value.toFixed(0);
}
