import type { FeeEvaluationEditedFileExportRequest } from "../../api/client";
import type {
  FeeEvaluationPreviewFieldMetadata,
  FeeEvaluationPreviewRow,
  FeeEvaluationSavedDraftHydrationResult,
} from "./feeEvaluationPreviewModel";

export type FeeEvaluationPricingDraftHydrationMode =
  | "current_v2_compatibility"
  | "server_rebase_candidate";

export function hydrateFeeEvaluationPricingDraft(
  previewRows: FeeEvaluationPreviewRow[],
  savedDraft: FeeEvaluationEditedFileExportRequest,
  mode: FeeEvaluationPricingDraftHydrationMode
): FeeEvaluationSavedDraftHydrationResult {
  const byIdentity = new Map(
    previewRows
      .filter((row) => row.rowKind === "matrix_step")
      .map((row) => [stableIdentity(row), row])
  );
  const samplePreparationRows = previewRows.filter(
    (row) => row.rowKind === "sample_preparation"
  );
  const edits: FeeEvaluationSavedDraftHydrationResult["edits"] = {};
  let appliedRowCount = 0;
  let unmatchedRowCount = 0;

  for (const row of savedDraft.rows) {
    const previewRow = byIdentity.get(savedIdentity(row));
    if (!previewRow) {
      unmatchedRowCount += 1;
      continue;
    }
    if (
      mode === "current_v2_compatibility" &&
      savedMatrixRowIsLegacyPlaceholder(row) &&
      previewRowHasDefaultPricing(previewRow)
    ) {
      continue;
    }
    edits[previewRow.lineId] = hydrateRow(previewRow, row, mode);
    appliedRowCount += 1;
  }

  for (const row of savedDraft.manual_rows ?? []) {
    const previewRow =
      row.row_kind === "sample_preparation"
        ? samplePreparationRows.find((candidate) =>
            samplePreparationRowMatches(candidate, row)
          )
        : row.row_kind === "report_preparation"
          ? previewRows.find(
              (candidate) =>
                candidate.rowKind === "manual_trailing" &&
                candidate.lineId === "manual-report-preparation"
            )
          : undefined;
    if (!previewRow) {
      unmatchedRowCount += 1;
      continue;
    }
    edits[previewRow.lineId] = hydrateRow(previewRow, row, mode);
    appliedRowCount += 1;
  }

  return {
    edits,
    costPreviewValues:
      mode === "server_rebase_candidate"
        ? exactCandidateSummary(savedDraft.summary)
        : compatibilitySummary(savedDraft.summary),
    appliedRowCount,
    unmatchedRowCount,
  };
}

export function formatUnitTypeForPreview(value: string): string {
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

export function editableDefault(value: string, fallback: string): string {
  const normalized = value.trim();
  if (!normalized || normalized.toLowerCase() === "pending") {
    return fallback;
  }
  return normalized;
}

export function fieldIsManualRequired(
  row: FeeEvaluationPreviewRow,
  field: FeeEvaluationPreviewFieldMetadata["field"]
): boolean {
  return row.fieldMetadata.some(
    (metadata) => metadata.field === field && metadata.state === "manual_required"
  );
}

function stableIdentity(row: FeeEvaluationPreviewRow): string {
  return JSON.stringify([
    row.sourceLineId,
    row.confirmedGroupId,
    row.confirmedRowId,
    row.stepToken === "-" ? "" : row.stepToken,
    row.stepIndex,
  ]);
}

function savedIdentity(
  row: FeeEvaluationEditedFileExportRequest["rows"][number]
): string {
  return JSON.stringify([
    row.source_line_id,
    row.confirmed_group_id,
    row.confirmed_row_id,
    row.step_token,
    row.step_index,
  ]);
}

function samplePreparationRowMatches(
  previewRow: FeeEvaluationPreviewRow,
  savedRow: NonNullable<FeeEvaluationEditedFileExportRequest["manual_rows"]>[number]
): boolean {
  const savedGroupId = (savedRow.confirmed_group_id ?? "").trim();
  if (savedGroupId && previewRow.confirmedGroupId === savedGroupId) {
    return true;
  }
  const savedGroupKey = (savedRow.group_key ?? "").trim();
  if (savedGroupKey && previewRow.groupKey === savedGroupKey) {
    return true;
  }
  const savedGroupLabel = (savedRow.group_label ?? "").trim();
  return Boolean(savedGroupLabel && previewRow.groupLabel === savedGroupLabel);
}

function hydrateRow(
  previewRow: FeeEvaluationPreviewRow,
  row:
    | FeeEvaluationEditedFileExportRequest["rows"][number]
    | NonNullable<FeeEvaluationEditedFileExportRequest["manual_rows"]>[number],
  mode: FeeEvaluationPricingDraftHydrationMode
) {
  const units =
    previewRow.rowKind === "sample_preparation" &&
    !fieldIsManualRequired(previewRow, "units")
      ? previewRow.units
      : mode === "server_rebase_candidate"
        ? exactCandidateValue(row.units)
        : hydratedPreviewNumber(row.units, previewRow, "units", "1");
  if (mode === "server_rebase_candidate") {
    return {
      spendTime: exactCandidateValue(row.spend_time),
      unitPrice: exactCandidateValue(row.unit_price),
      unitType: formatUnitTypeForPreview(row.unit_type),
      units,
      baseFee: exactCandidateValue(row.base_fee),
      discount: exactCandidateValue(row.discount),
      notes: row.notes,
    };
  }
  return {
    spendTime: hydratedEditableNumber(row.spend_time, previewRow.spendTime, "0"),
    unitPrice: hydratedPreviewNumber(
      row.unit_price,
      previewRow,
      "unitPrice",
      "0"
    ),
    unitType: hydratedUnitType(row.unit_type, previewRow.unitType),
    units,
    baseFee: hydratedPreviewNumber(row.base_fee, previewRow, "baseFee", "0"),
    discount: hydratedEditableDiscount(row.discount, previewRow.discount),
    notes: row.notes,
  };
}

function exactCandidateSummary(
  summary: FeeEvaluationEditedFileExportRequest["summary"]
): FeeEvaluationSavedDraftHydrationResult["costPreviewValues"] {
  return {
    conditionConfirmationSpendTime: exactCandidateValue(
      summary.condition_confirmation_spend_time
    ),
    externalCost: exactCandidateValue(summary.external_cost),
    externalCostNote: summary.external_cost_note,
    labManpowerHourlyRate: exactCandidateValue(summary.lab_manpower_hourly_rate),
  };
}

function compatibilitySummary(
  summary: FeeEvaluationEditedFileExportRequest["summary"]
): FeeEvaluationSavedDraftHydrationResult["costPreviewValues"] {
  return {
    conditionConfirmationSpendTime: editableDefault(
      summary.condition_confirmation_spend_time,
      "0"
    ),
    externalCost: editableDefault(summary.external_cost, "0"),
    externalCostNote: summary.external_cost_note,
    labManpowerHourlyRate: editableDefault(
      summary.lab_manpower_hourly_rate,
      "200"
    ),
  };
}

function exactCandidateValue(value: string): string {
  return value.trim();
}

function hydratedUnitType(value: string, fallback: string): string {
  const normalized = value.trim();
  return normalized.length > 0
    ? formatUnitTypeForPreview(normalized)
    : formatUnitTypeForPreview(fallback);
}

function hydratedEditableNumber(
  value: string,
  fallback: string,
  defaultValue: string
): string {
  const normalized = editableDefault(value, "");
  return normalized.length > 0
    ? normalized
    : editableDefault(fallback, defaultValue);
}

function hydratedPreviewNumber(
  value: string,
  previewRow: FeeEvaluationPreviewRow,
  field: "unitPrice" | "units" | "baseFee",
  defaultValue: string
): string {
  return hydratedEditableNumber(
    value,
    previewRow[field],
    fieldIsManualRequired(previewRow, field) ? "" : defaultValue
  );
}

function hydratedEditableDiscount(value: string, fallback: string): string {
  const normalized = editableDefault(value, "");
  return normalized.length > 0 ? normalized : editableDefault(fallback, "0%");
}

function savedMatrixRowIsLegacyPlaceholder(
  row: FeeEvaluationEditedFileExportRequest["rows"][number]
): boolean {
  return (
    editableDefault(row.spend_time, "0") === "0" &&
    editableDefault(row.unit_price, "0") === "0" &&
    formatUnitTypeForPreview(row.unit_type) === "Pending" &&
    editableDefault(row.units, "1") === "1" &&
    editableDefault(row.base_fee, "0") === "0" &&
    hydratedEditableDiscount(row.discount, "0%") === "0%" &&
    row.notes.trim().length === 0
  );
}

function previewRowHasDefaultPricing(row: FeeEvaluationPreviewRow): boolean {
  return (
    editableDefault(row.unitPrice, "0") !== "0" ||
    formatUnitTypeForPreview(row.unitType) !== "Pending" ||
    editableDefault(row.units, "1") !== "1" ||
    editableDefault(row.baseFee, "0") !== "0" ||
    hydratedEditableDiscount(row.discount, "0%") !== "0%"
  );
}
