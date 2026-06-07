import type { FeeEvaluationDraft, FeeEvaluationLineItem } from "../../api/client";

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
    workingHours: "Pending",
    labManpowerCost: "Pending",
    externalCost: "Pending",
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
  const scopedRows =
    groupFilter === "all"
      ? rows.filter((row) => row.rowKind === "matrix_step")
      : rows.filter(
          (row) => row.rowKind === "matrix_step" && row.groupLabel === groupFilter
        );
  if (scopedRows.length === 0) {
    return "Pending";
  }
  let total = 0;
  const countedSourceLines = new Set<string>();
  for (const row of scopedRows) {
    if (countedSourceLines.has(row.sourceLineId)) {
      continue;
    }
    const parsed = Number(row.testingFee);
    if (!Number.isFinite(parsed)) {
      return "Pending";
    }
    countedSourceLines.add(row.sourceLineId);
    total += parsed;
  }
  return total.toFixed(2);
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

function parsePreviewNumber(value: string): number | null {
  const normalized = value.trim().replace(/[$,\s]/g, "");
  if (!normalized) {
    return null;
  }
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}
