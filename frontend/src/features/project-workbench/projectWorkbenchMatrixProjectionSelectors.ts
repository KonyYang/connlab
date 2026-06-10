import {
  type ConfirmedMatrixTestRecordPreview,
  type ConfirmedMatrixTestRecordPreviewGroup,
  type ConfirmedMatrixTestRecordPreviewStep,
} from "../../api/client";

export type MatrixProjectionStatusTone =
  | "not_started"
  | "in_progress"
  | "passed"
  | "failed"
  | "review"
  | "retest";

export type MatrixProjectionVisibleStatusTone =
  | "not_started"
  | "in_progress"
  | "passed"
  | "failed";

export type MatrixProjectionGroupColumn = {
  groupKey: string;
  groupLabel: string;
  sampleQuantityExpression: string;
};

export type MatrixProjectionTokenCell = {
  tokenReference: string;
  groupKey: string;
  groupLabel: string;
  rawToken: string;
  sequence: number;
  statusTone: MatrixProjectionStatusTone;
  sampleQuantityExpression: string;
  testItem: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
};

export type MatrixProjectionRow = {
  rowKey: string;
  sequence: number;
  testItem: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  cellsByGroupKey: Record<string, MatrixProjectionTokenCell[]>;
};

export type MatrixProjectionViewModel = {
  confirmedMatrixId: string;
  groupColumns: MatrixProjectionGroupColumn[];
  rows: MatrixProjectionRow[];
  totalTokenCount: number;
};

function normalizeText(value: string | null | undefined): string {
  return (value ?? "").trim();
}

function buildRowKey(step: ConfirmedMatrixTestRecordPreviewStep): string {
  return [
    normalizeText(step.test_item),
    normalizeText(step.section),
    normalizeText(step.method),
    normalizeText(step.condition),
  ].join("::");
}

export function deriveMatrixProjectionStatusTone(
  sequence: number
): MatrixProjectionStatusTone {
  if (sequence % 6 === 0) {
    return "review";
  }
  if (sequence % 5 === 0) {
    return "retest";
  }
  if (sequence % 4 === 0) {
    return "failed";
  }
  if (sequence % 3 === 0) {
    return "passed";
  }
  if (sequence % 2 === 0) {
    return "in_progress";
  }
  return "not_started";
}

export function toVisibleMatrixProjectionStatusTone(
  tone: MatrixProjectionStatusTone
): MatrixProjectionVisibleStatusTone {
  if (tone === "failed") {
    return "failed";
  }
  if (tone === "passed") {
    return "passed";
  }
  if (tone === "not_started") {
    return "not_started";
  }
  return "in_progress";
}

function buildTokenCell(
  rowKey: string,
  group: ConfirmedMatrixTestRecordPreviewGroup,
  step: ConfirmedMatrixTestRecordPreviewStep
): MatrixProjectionTokenCell {
  const visibleToken = `${step.sequence}`;
  return {
    tokenReference: `${rowKey}:${group.group_key}:${step.sequence}:${step.raw_token}`,
    groupKey: group.group_key,
    groupLabel: group.group_label,
    rawToken: visibleToken,
    sequence: step.sequence,
    statusTone: deriveMatrixProjectionStatusTone(step.sequence),
    sampleQuantityExpression: group.sample_quantity_expression || "-",
    testItem: step.test_item,
    section: step.section,
    method: step.method,
    condition: step.condition,
    requirement: step.requirement,
  };
}

export function buildMatrixProjectionViewModel(
  preview: ConfirmedMatrixTestRecordPreview
): MatrixProjectionViewModel {
  const groupColumns = preview.groups.map((group) => ({
    groupKey: group.group_key,
    groupLabel: group.group_label,
    sampleQuantityExpression: group.sample_quantity_expression || "-",
  }));
  const rowsByKey = new Map<string, MatrixProjectionRow>();
  let totalTokenCount = 0;

  preview.groups.forEach((group) => {
    group.steps.forEach((step) => {
      const rowKey = buildRowKey(step);
      const existingRow = rowsByKey.get(rowKey);
      const row = existingRow ?? {
        rowKey,
        sequence: step.sequence,
        testItem: step.test_item,
        section: step.section,
        method: step.method,
        condition: step.condition,
        requirement: step.requirement,
        cellsByGroupKey: {},
      };
      row.sequence = Math.min(row.sequence, step.sequence);
      const cell = buildTokenCell(rowKey, group, step);
      row.cellsByGroupKey[group.group_key] = [
        ...(row.cellsByGroupKey[group.group_key] ?? []),
        cell,
      ];
      rowsByKey.set(rowKey, row);
      totalTokenCount += 1;
    });
  });

  return {
    confirmedMatrixId: preview.confirmed_matrix_id,
    groupColumns,
    rows: Array.from(rowsByKey.values()).sort(
      (left, right) => left.sequence - right.sequence
    ),
    totalTokenCount,
  };
}

export function findMatrixProjectionToken(
  viewModel: MatrixProjectionViewModel,
  tokenReference: string | null
): MatrixProjectionTokenCell | null {
  if (!tokenReference) {
    return null;
  }
  for (const row of viewModel.rows) {
    for (const cells of Object.values(row.cellsByGroupKey)) {
      const match = cells.find((cell) => cell.tokenReference === tokenReference);
      if (match) {
        return match;
      }
    }
  }
  return null;
}
