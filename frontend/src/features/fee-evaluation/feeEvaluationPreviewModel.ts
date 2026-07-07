import type {
  FeeEvaluationDraft,
  FeeEvaluationEditedFileExportRequest,
  FeeEvaluationFieldMetadata,
  FeeEvaluationLineItem,
} from "../../api/client";

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
  confirmedGroupId: string;
  confirmedRowId: string;
  groupKey: string;
  groupLabel: string;
  stepToken: string;
  stepIndex: number;
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
  fieldMetadata: FeeEvaluationPreviewFieldMetadata[];
  rowKind: "matrix_step" | "sample_preparation" | "manual_trailing";
  groupTone: "tone-a" | "tone-b" | "manual";
};

export type FeeEvaluationPreviewFieldMetadata = {
  field:
    | "spendTime"
    | "unitPrice"
    | "unitType"
    | "units"
    | "baseFee"
    | "discount"
    | "testingFee";
  state: FeeEvaluationFieldMetadata["state"];
  source: string | null;
  message: string | null;
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

export type FeeEvaluationUpdateBlocker = {
  rowId: string | null;
  rowLabel: string;
  fields: string[];
  message: string;
  rowMessage: string;
};

export type FeeEvaluationSavedDraftHydrationResult = {
  edits: FeeEvaluationPreviewEditState;
  costPreviewValues: {
    conditionConfirmationSpendTime: string;
    externalCost: string;
    externalCostNote: string;
    labManpowerHourlyRate: string;
  };
  appliedRowCount: number;
  unmatchedRowCount: number;
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
      const matrixRows = group.line_items
        .flatMap((line, lineIndex) => buildMatrixStepRows(line, groupTone, lineIndex))
        .sort(comparePreviewRows)
        .map(stripPreviewSortMetadata);
      const firstLine = group.line_items[0];
      const sampleRows =
        group.manual_line_items?.length
          ? group.manual_line_items.map((line) =>
              buildManualDefaultRow(line, "sample_preparation", groupTone, "0")
            )
          : [
              buildSamplePreparationFallbackRow(
                group.group_key,
                group.group_label,
                firstLine?.confirmed_group_id ?? "",
                groupTone
              ),
            ];
      return [
        ...sampleRows,
        ...matrixRows,
      ];
    }) ?? [];
  const manualRows =
    draft?.manual_line_items?.length
      ? draft.manual_line_items.map((line) =>
          buildManualDefaultRow(line, "manual_trailing", "manual", "-")
        )
      : [buildReportPreparationFallbackRow()];
  return [...rows, ...manualRows];
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
    (row) =>
      (row.rowKind === "matrix_step" || row.rowKind === "sample_preparation") &&
      row.groupLabel === groupFilter
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
      unitType: editableUnitType(rowEdits.unitType, row.unitType),
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

export function buildFeeEvaluationPreviewStableIdentity(
  row: FeeEvaluationPreviewRow
): string {
  return JSON.stringify([
    row.sourceLineId,
    row.confirmedGroupId,
    row.confirmedRowId,
    row.stepToken === "-" ? "" : row.stepToken,
    row.stepIndex,
  ]);
}

export function hydrateFeeEvaluationPreviewEditsFromSavedDraft(
  previewRows: FeeEvaluationPreviewRow[],
  savedDraft: FeeEvaluationEditedFileExportRequest
): FeeEvaluationSavedDraftHydrationResult {
  const byIdentity = new Map(
    previewRows
      .filter((row) => row.rowKind === "matrix_step")
      .map((row) => [buildFeeEvaluationPreviewStableIdentity(row), row])
  );
  const samplePreparationRows = previewRows.filter(
    (row) => row.rowKind === "sample_preparation"
  );
  const edits: FeeEvaluationPreviewEditState = {};
  let appliedRowCount = 0;
  let unmatchedRowCount = 0;

  for (const row of savedDraft.rows) {
    const identity = JSON.stringify([
      row.source_line_id,
      row.confirmed_group_id,
      row.confirmed_row_id,
      row.step_token,
      row.step_index,
    ]);
    const previewRow = byIdentity.get(identity);
    if (!previewRow) {
      unmatchedRowCount += 1;
      continue;
    }
    edits[previewRow.lineId] = {
      spendTime: hydratedEditableNumber(row.spend_time, previewRow.spendTime, "0"),
      unitPrice: hydratedEditableNumber(row.unit_price, previewRow.unitPrice, "0"),
      unitType: hydratedUnitType(row.unit_type, previewRow.unitType),
      units: hydratedEditableNumber(row.units, previewRow.units, "1"),
      baseFee: hydratedEditableNumber(row.base_fee, previewRow.baseFee, "0"),
      discount: hydratedEditableDiscount(row.discount, previewRow.discount),
      notes: row.notes,
    };
    appliedRowCount += 1;
  }

  for (const row of savedDraft.manual_rows ?? []) {
    if (row.row_kind === "sample_preparation") {
      const previewRow = samplePreparationRows.find((candidate) =>
        samplePreparationRowMatches(candidate, row)
      );
      if (!previewRow) {
        unmatchedRowCount += 1;
        continue;
      }
      edits[previewRow.lineId] = {
        spendTime: hydratedEditableNumber(row.spend_time, previewRow.spendTime, "0"),
        unitPrice: hydratedEditableNumber(row.unit_price, previewRow.unitPrice, "0"),
        unitType: hydratedUnitType(row.unit_type, previewRow.unitType),
        units: hydratedEditableNumber(row.units, previewRow.units, "1"),
        baseFee: hydratedEditableNumber(row.base_fee, previewRow.baseFee, "0"),
        discount: hydratedEditableDiscount(row.discount, previewRow.discount),
        notes: row.notes,
      };
      appliedRowCount += 1;
      continue;
    }
    if (row.row_kind !== "report_preparation") {
      unmatchedRowCount += 1;
      continue;
    }
    const previewRow = previewRows.find(
      (candidate) =>
        candidate.rowKind === "manual_trailing" &&
        candidate.lineId === "manual-report-preparation"
    );
    if (!previewRow) {
      unmatchedRowCount += 1;
      continue;
    }
    edits[previewRow.lineId] = {
      spendTime: hydratedEditableNumber(row.spend_time, previewRow.spendTime, "0"),
      unitPrice: hydratedEditableNumber(row.unit_price, previewRow.unitPrice, "0"),
      unitType: hydratedUnitType(row.unit_type, previewRow.unitType),
      units: hydratedEditableNumber(row.units, previewRow.units, "1"),
      baseFee: hydratedEditableNumber(row.base_fee, previewRow.baseFee, "0"),
      discount: hydratedEditableDiscount(row.discount, previewRow.discount),
      notes: row.notes,
    };
    appliedRowCount += 1;
  }

  return {
    edits,
    costPreviewValues: {
      conditionConfirmationSpendTime:
        hydratedSummaryNumber(
          savedDraft.summary.condition_confirmation_spend_time,
          "0"
        ),
      externalCost: hydratedSummaryNumber(savedDraft.summary.external_cost, "0"),
      externalCostNote: savedDraft.summary.external_cost_note,
      labManpowerHourlyRate: hydratedSummaryNumber(
        savedDraft.summary.lab_manpower_hourly_rate,
        "200"
      ),
    },
    appliedRowCount,
    unmatchedRowCount,
  };
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

export function buildFeeEvaluationUpdateBlockers(input: {
  rows: FeeEvaluationPreviewRow[];
  totals: {
    testingFeeTotal: string;
    workingHours: string;
    labManpowerCost: string;
    externalCost: string;
    grandCost: string;
  };
}): FeeEvaluationUpdateBlocker[] {
  const blockers: FeeEvaluationUpdateBlocker[] = [];
  for (const row of input.rows) {
    const fields = incompleteUpdateFields(row);
    if (fields.length === 0) {
      continue;
    }
    const rowLabel = updateRowLabel(row);
    blockers.push({
      rowId: row.lineId,
      rowLabel,
      fields,
      message: updateBlockerMessage(rowLabel, fields),
      rowMessage: `Complete ${formatFieldList(fields)} before Update Fee.`,
    });
  }
  if (blockers.length > 0) {
    return blockers;
  }
  for (const [field, value] of [
    ["Total Testing Fee", input.totals.testingFeeTotal],
    ["Working hours", input.totals.workingHours],
    ["Lab manpower cost", input.totals.labManpowerCost],
    ["External Cost", input.totals.externalCost],
    ["Grand Cost", input.totals.grandCost],
  ] as const) {
    if (!isCompleteNumber(value)) {
      blockers.push({
        rowId: null,
        rowLabel: field,
        fields: [field],
        message: updateBlockerMessage(field, [field]),
        rowMessage: `Complete ${field} before Update Fee.`,
      });
    }
  }
  return blockers;
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
    const backendLineId =
      normalizedStepToken.length > 0
        ? `${line.line_id}:${normalizedStepToken}:${index}`
        : line.line_id;
    return {
      lineId: `${line.line_id}:${lineIdToken}:${index}`,
      sourceLineId: backendLineId,
      confirmedGroupId: line.confirmed_group_id,
      confirmedRowId: line.confirmed_row_id,
      groupKey: line.group_key,
      groupLabel: line.group_label,
      stepToken: stepDisplay,
      stepIndex: index,
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
      fieldMetadata: mapFieldMetadata(line.field_metadata ?? []),
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

function buildSamplePreparationFallbackRow(
  groupKey: string,
  groupLabel: string,
  confirmedGroupId: string,
  groupTone: "tone-a" | "tone-b"
): FeeEvaluationPreviewRow {
  return {
    lineId: `sample-preparation:${groupKey || groupLabel}`,
    sourceLineId: `sample-preparation:${groupKey || groupLabel}`,
    confirmedGroupId,
    confirmedRowId: "",
    groupKey,
    groupLabel,
    stepToken: "0",
    stepIndex: 0,
    spendTime: "Pending",
    description: "Sample preparation",
    unitPrice: "Pending",
    unitType: "Pending",
    units: "Pending",
    baseFee: "Pending",
    discount: "Pending",
    testingFee: "Pending",
    notes: "",
    status: "pending",
    reviewReason: "Backend sample preparation default is unavailable.",
    fieldMetadata: [
      reviewMetadata("unitPrice", "Backend sample preparation default is unavailable."),
      reviewMetadata("units", "Backend sample preparation default is unavailable."),
      reviewMetadata("testingFee", "Backend sample preparation default is unavailable."),
    ],
    rowKind: "sample_preparation",
    groupTone,
  };
}

function parseStepSortValue(value: string): number | null {
  const normalized = value.trim();
  if (!/^\d+$/.test(normalized)) {
    return null;
  }
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function buildReportPreparationFallbackRow(): FeeEvaluationPreviewRow {
  return {
    lineId: "manual-report-preparation",
    sourceLineId: "manual-report-preparation",
    confirmedGroupId: "",
    confirmedRowId: "",
    groupKey: "",
    groupLabel: "",
    stepToken: "-",
    stepIndex: 0,
    description: "Report preparation",
    spendTime: "Pending",
    unitPrice: "Pending",
    unitType: "Pending",
    units: "Pending",
    baseFee: "Pending",
    discount: "Pending",
    testingFee: "Pending",
    notes: "",
    status: "pending",
    reviewReason: "Backend report preparation default is unavailable.",
    fieldMetadata: [
      reviewMetadata("unitPrice", "Backend report preparation default is unavailable."),
      reviewMetadata("testingFee", "Backend report preparation default is unavailable."),
    ],
    rowKind: "manual_trailing",
    groupTone: "manual",
  };
}

function buildManualDefaultRow(
  line: FeeEvaluationLineItem,
  rowKind: "sample_preparation" | "manual_trailing",
  groupTone: "tone-a" | "tone-b" | "manual",
  stepToken: string
): FeeEvaluationPreviewRow {
  return {
    lineId: line.line_id,
    sourceLineId: line.line_id,
    confirmedGroupId: line.confirmed_group_id,
    confirmedRowId: line.confirmed_row_id,
    groupKey: line.group_key,
    groupLabel: line.group_label,
    stepToken,
    stepIndex: 0,
    spendTime: pendingValue(line.spend_time),
    description: line.test_item,
    unitPrice: pendingValue(line.unit_price),
    unitType: formatUnitTypeForPreview(line.unit_label || line.calculation_strategy || "Pending"),
    units: pendingValue(line.units),
    baseFee: pendingValue(line.base_fee),
    discount: formatDiscount(line.discount_percent),
    testingFee: pendingValue(line.testing_fee),
    notes: "",
    status: line.review_required ? "pending" : "confirmed",
    reviewReason: line.review_reason,
    fieldMetadata: mapFieldMetadata(line.field_metadata ?? []),
    rowKind,
    groupTone,
  };
}

function mapFieldMetadata(
  metadata: FeeEvaluationFieldMetadata[]
): FeeEvaluationPreviewFieldMetadata[] {
  return metadata
    .map((entry) => {
      const field = mapMetadataField(entry.field);
      if (!field) {
        return null;
      }
      return {
        field,
        state: entry.state,
        source: entry.source,
        message: entry.message,
      };
    })
    .filter((entry): entry is FeeEvaluationPreviewFieldMetadata => entry !== null);
}

function mapMetadataField(
  field: FeeEvaluationFieldMetadata["field"]
): FeeEvaluationPreviewFieldMetadata["field"] | null {
  const map: Record<
    FeeEvaluationFieldMetadata["field"],
    FeeEvaluationPreviewFieldMetadata["field"] | null
  > = {
    spend_time: "spendTime",
    unit_price: "unitPrice",
    unit_label: "unitType",
    units: "units",
    base_fee: "baseFee",
    discount_percent: "discount",
    testing_fee: "testingFee",
  };
  return map[field] ?? null;
}

function reviewMetadata(
  field: FeeEvaluationPreviewFieldMetadata["field"],
  message: string
): FeeEvaluationPreviewFieldMetadata {
  return {
    field,
    state: "manual_required",
    source: "Fee rule default",
    message,
  };
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

function hydratedUnitType(value: string, fallback: string): string {
  const normalized = value.trim();
  return normalized.length > 0 ? normalized : formatUnitTypeForPreview(fallback);
}

function hydratedEditableNumber(
  value: string,
  fallback: string,
  defaultValue: string
): string {
  const normalized = editableDefault(value, "");
  if (normalized.length > 0) {
    return normalized;
  }
  return editableDefault(fallback, defaultValue);
}

function hydratedEditableDiscount(value: string, fallback: string): string {
  const normalized = editableDefault(value, "");
  if (normalized.length > 0) {
    return normalized;
  }
  return editableDefault(fallback, "0%");
}

function hydratedSummaryNumber(value: string, defaultValue: string): string {
  return editableDefault(value, defaultValue);
}

function editableUnitType(value: string | undefined, fallback: string): string {
  if (value === undefined) {
    return formatUnitTypeForPreview(fallback);
  }
  return hydratedUnitType(value, fallback);
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

function incompleteUpdateFields(row: FeeEvaluationPreviewRow): string[] {
  const fields: string[] = [];
  if (!isCompleteNumber(row.spendTime)) {
    fields.push("Man-hour");
  }
  if (!isCompleteNumber(row.unitPrice)) {
    fields.push("Unit Price");
  }
  if (!isCompleteUnitType(row.unitType)) {
    fields.push("Unit Type");
  }
  if (!isCompleteNumber(row.units)) {
    fields.push("Units");
  }
  if (!isCompleteOptionalNumber(row.baseFee)) {
    fields.push("Base Fee");
  }
  if (!isCompleteDiscount(row.discount)) {
    fields.push("Discount");
  }
  if (!isCompleteNumber(row.testingFee)) {
    fields.push("Testing Fee");
  }
  return fields;
}

function updateRowLabel(row: FeeEvaluationPreviewRow): string {
  if (row.rowKind === "manual_trailing") {
    return row.description;
  }
  const group = row.groupLabel.trim();
  const step = row.stepToken.trim();
  const prefix = [
    group ? formatGroupLabel(group) : "",
    step && step !== "-" ? `Step ${step}` : "",
  ].filter(Boolean);
  return [...prefix, row.description].join(", ") || row.description;
}

function formatGroupLabel(group: string): string {
  return group.toLowerCase().startsWith("group ") ? group : `Group ${group}`;
}

function updateBlockerMessage(rowLabel: string, fields: string[]): string {
  return `Complete Fee Evaluation pricing before Update Fee. First blocker: ${rowLabel} has incomplete ${formatFieldList(fields)}.`;
}

function formatFieldList(fields: string[]): string {
  if (fields.length <= 1) {
    return fields[0] ?? "fee fields";
  }
  if (fields.length === 2) {
    return `${fields[0]} and ${fields[1]}`;
  }
  return `${fields.slice(0, -1).join(", ")}, and ${fields.at(-1)}`;
}

function isCompleteNumber(value: string): boolean {
  return parsePreviewNumber(value) !== null;
}

function isCompleteOptionalNumber(value: string): boolean {
  return parseOptionalEditableNumber(value) !== null;
}

function isCompleteDiscount(value: string): boolean {
  return parseEditableDiscount(value) !== null;
}

function isCompleteUnitType(value: string): boolean {
  const normalized = value.trim();
  return normalized.length > 0 && normalized.toLowerCase() !== "pending";
}
