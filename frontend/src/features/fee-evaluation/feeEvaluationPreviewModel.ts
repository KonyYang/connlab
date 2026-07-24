import type {
  FeeEvaluationDraft,
  FeeEvaluationEditedFileExportRequest,
  FeeEvaluationFieldMetadata,
  FeeEvaluationLineItem,
  FeeEvaluationPricingDraftResponse,
  FeeEvaluationPricingDraftSaveRequest,
} from "../../api/client";
import {
  editableDefault,
  fieldIsManualRequired,
  formatUnitTypeForPreview,
  hydrateFeeEvaluationPricingDraft,
} from "./feeEvaluationPricingDraftHydration";

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

export type FeeEvaluationPricingDraftCas = { draftEditId: string; generation: number; payloadFingerprint: string; updatedAt: string; validationToken: string };

export type FeeEvaluationPricingDraftContext = { confirmedMatrixId: string; confirmedRevision: number; feeRuleVersionId: string };

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
    const unitPriceRequired = fieldIsManualRequired(row, "unitPrice");
    const unitPrice =
      rowEdits.unitPrice ??
      editableDefault(row.unitPrice, unitPriceRequired ? "" : "0");
    const unitsRequired = fieldIsManualRequired(row, "units");
    const units =
      rowEdits.units ?? editableDefault(row.units, unitsRequired ? "" : "1");
    const baseFeeRequired = fieldIsManualRequired(row, "baseFee");
    const baseFee =
      rowEdits.baseFee ?? editableDefault(row.baseFee, baseFeeRequired ? "" : "0");
    const discount = rowEdits.discount ?? editableDefault(row.discount, "0%");
    return {
      ...row,
      spendTime: rowEdits.spendTime ?? editableDefault(row.spendTime, "0"),
      unitPrice,
      unitType: editableUnitType(rowEdits.unitType, row.unitType),
      units,
      baseFee,
      discount,
      testingFee:
        baseFeeRequired && baseFee.trim().length === 0
          ? "Pending"
          : calculateFeePreviewTestingFee({
              unitPrice,
              units,
              baseFee,
              discount,
            }),
      notes: rowEdits.notes ?? row.notes,
    };
  });
}

export function hydrateFeeEvaluationPreviewEditsFromSavedDraft(
  previewRows: FeeEvaluationPreviewRow[],
  savedDraft: FeeEvaluationEditedFileExportRequest
): FeeEvaluationSavedDraftHydrationResult {
  return hydrateFeeEvaluationPricingDraft(
    previewRows,
    savedDraft,
    "current_v2_compatibility"
  );
}

export function hydrateFeeEvaluationPreviewEditsFromServerRebaseCandidate(
  previewRows: FeeEvaluationPreviewRow[],
  candidate: FeeEvaluationEditedFileExportRequest
): FeeEvaluationSavedDraftHydrationResult {
  return hydrateFeeEvaluationPricingDraft(
    previewRows,
    candidate,
    "server_rebase_candidate"
  );
}

export function buildFeeEvaluationEditedExportPayload(
  rows: FeeEvaluationPreviewRow[],
  costValues: FeeEvaluationSavedDraftHydrationResult["costPreviewValues"]
): FeeEvaluationEditedFileExportRequest {
  const rowValues = (row: FeeEvaluationPreviewRow) => ({
    spend_time: row.spendTime, unit_price: row.unitPrice,
    unit_type: row.unitType, units: row.units,
    base_fee: row.baseFee, discount: row.discount,
    testing_fee: row.testingFee, notes: row.notes,
  });
  return {
    rows: rows
      .filter((row) => row.rowKind === "matrix_step")
      .map((row) => ({
        source_line_id: row.sourceLineId,
        confirmed_group_id: row.confirmedGroupId,
        confirmed_row_id: row.confirmedRowId,
        step_token: row.stepToken === "-" ? "" : row.stepToken,
        step_index: row.stepIndex,
        ...rowValues(row),
      })),
    summary: {
      condition_confirmation_spend_time: costValues.conditionConfirmationSpendTime,
      external_cost: costValues.externalCost,
      external_cost_note: costValues.externalCostNote,
      lab_manpower_hourly_rate: costValues.labManpowerHourlyRate,
    },
    manual_rows: rows
      .filter((row) =>
        row.rowKind === "sample_preparation" ||
        (row.rowKind === "manual_trailing" &&
          row.lineId === "manual-report-preparation")
      )
      .map((row) => ({
        row_kind: row.rowKind === "sample_preparation"
          ? ("sample_preparation" as const)
          : ("report_preparation" as const),
        confirmed_group_id: row.rowKind === "sample_preparation"
          ? row.confirmedGroupId
          : undefined,
        group_key: row.rowKind === "sample_preparation" ? row.groupKey : undefined,
        group_label: row.rowKind === "sample_preparation" ? row.groupLabel : undefined,
        ...rowValues(row),
      })),
  };
}

export function feeEvaluationPricingDraftContext(
  response: FeeEvaluationPricingDraftResponse
): FeeEvaluationPricingDraftContext {
  return { confirmedMatrixId: response.current_confirmed_matrix_id,
    confirmedRevision: response.current_confirmed_revision,
    feeRuleVersionId: response.current_fee_rule_version_id };
}

export function feeEvaluationPricingDraftCas(
  response: FeeEvaluationPricingDraftResponse
): FeeEvaluationPricingDraftCas | null {
  const draftEditId = response.saved_draft_edit_id;
  const generation = response.saved_generation;
  const payloadFingerprint = response.saved_payload_fingerprint;
  const updatedAt = response.saved_updated_at;
  const validationToken = response.saved_validation_token;
  if (!draftEditId || generation == null || !payloadFingerprint || !updatedAt || !validationToken) {
    return null;
  }
  return { draftEditId, generation, payloadFingerprint, updatedAt, validationToken };
}

export function feeEvaluationPricingDraftCasRequest(
  state: FeeEvaluationPricingDraftCas | null
): Partial<FeeEvaluationPricingDraftSaveRequest> {
  if (!state) return {};
  return {
    expected_pricing_draft_edit_id: state.draftEditId,
    expected_generation: state.generation,
    expected_payload_fingerprint: state.payloadFingerprint,
    expected_updated_at: state.updatedAt,
  };
}

export function feeEvaluationPricingDraftContextEquals(
  left: FeeEvaluationPricingDraftContext,
  right: FeeEvaluationPricingDraftContext
): boolean {
  return left.confirmedMatrixId === right.confirmedMatrixId &&
    left.confirmedRevision === right.confirmedRevision &&
    left.feeRuleVersionId === right.feeRuleVersionId;
}

export function feeEvaluationPricingDraftCasEquals(
  left: FeeEvaluationPricingDraftCas,
  right: FeeEvaluationPricingDraftCas
): boolean {
  return left.draftEditId === right.draftEditId &&
    left.generation === right.generation &&
    left.payloadFingerprint === right.payloadFingerprint &&
    left.updatedAt === right.updatedAt &&
    left.validationToken === right.validationToken;
}

export const feeEvaluationPricingDraftSignature = (payload: FeeEvaluationEditedFileExportRequest): string => JSON.stringify(payload);

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
      rowMessage: `Complete ${formatFieldList(fields)}.`,
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

function editableUnitType(value: string | undefined, fallback: string): string {
  if (value === undefined) {
    return formatUnitTypeForPreview(fallback);
  }
  const normalized = value.trim();
  return normalized.length > 0
    ? formatUnitTypeForPreview(normalized)
    : formatUnitTypeForPreview(fallback);
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
  const baseFeeIncomplete = fieldIsManualRequired(row, "baseFee")
    ? !isCompleteNumber(row.baseFee)
    : !isCompleteOptionalNumber(row.baseFee);
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
  if (baseFeeIncomplete) {
    fields.push("Base Fee");
  }
  if (!isCompleteDiscount(row.discount)) {
    fields.push("Discount");
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
