import type { FeeEvaluationDraft, FeeEvaluationLineItem } from "../../api/client";

export type FeeEvaluationPreviewRow = {
  lineId: string;
  groupLabel: string;
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
  return flattenDraftLines(draft).map((line) => ({
    lineId: line.line_id,
    groupLabel: line.group_label,
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
  }));
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

function flattenDraftLines(draft: FeeEvaluationDraft | null): FeeEvaluationLineItem[] {
  return draft?.groups.flatMap((group) => group.line_items) ?? [];
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
