import { type MatrixPreviewResponse } from "../../api/client";

export type MatrixImportSelectableGroup = {
  groupKey: string;
  groupLabel: string;
  sampleQuantityExpression: string | null;
  sampleNote: string | null;
  stepCount: number | null;
};

export type MatrixImportSelectionRow = {
  rowId: string;
  testItem: string;
  tokensByGroupKey: Record<string, string>;
};

export type MatrixImportSelectionViewModel = {
  sourceDocumentName: string;
  groups: MatrixImportSelectableGroup[];
  rows: MatrixImportSelectionRow[];
};

export type MatrixImportSelectionSummary = {
  selectedGroupCount: number;
  totalGroupCount: number;
  selectedStepCount: number | null;
  hasStepCounts: boolean;
  selectedGroupLabels: string[];
  selectedSampleQuantities: Array<{
    groupKey: string;
    groupLabel: string;
    sampleQuantityExpression: string;
  }>;
};

function normalizeGroupKey(rawKey: string | null | undefined, index: number): string {
  const normalized = (rawKey ?? "").trim();
  if (normalized.length > 0) {
    return normalized;
  }
  return `group_${index + 1}`;
}

function normalizeGroupLabel(rawLabel: string | null | undefined, index: number): string {
  const normalized = (rawLabel ?? "").trim();
  if (normalized.length === 0) {
    return `Group ${index + 1}`;
  }
  const withoutPrefix = normalized.replace(/^group[\s_-]*/i, "").trim();
  return withoutPrefix.length > 0 ? withoutPrefix : `Group ${index + 1}`;
}

export function buildMatrixImportSelectableGroups(
  preview: MatrixPreviewResponse | null
): MatrixImportSelectableGroup[] {
  if (!preview) {
    return [];
  }
  return preview.groups.map((group, index) => ({
    groupKey: normalizeGroupKey(group.group_key, index),
    groupLabel: normalizeGroupLabel(group.group_label, index),
    sampleQuantityExpression: group.sample_quantity_expression ?? null,
    sampleNote: group.sample_note ?? null,
    stepCount: Array.isArray(group.steps) ? group.steps.length : null,
  }));
}

export function formatMatrixImportSampleQuantity(value: string | null): string {
  const normalized = (value ?? "").trim();
  return normalized.length > 0 ? normalized : "Not specified";
}

export function buildMatrixImportSelectionSummary(input: {
  groups: MatrixImportSelectableGroup[];
  selectedGroupKeys: string[];
}): MatrixImportSelectionSummary {
  const selectedKeys = new Set(input.selectedGroupKeys);
  const selectedGroups = input.groups.filter((group) => selectedKeys.has(group.groupKey));
  const hasStepCounts = selectedGroups.every((group) => group.stepCount !== null);
  const selectedStepCount = hasStepCounts
    ? selectedGroups.reduce((total, group) => total + (group.stepCount ?? 0), 0)
    : null;

  return {
    selectedGroupCount: selectedGroups.length,
    totalGroupCount: input.groups.length,
    selectedStepCount,
    hasStepCounts,
    selectedGroupLabels: selectedGroups.map((group) => group.groupLabel),
    selectedSampleQuantities: selectedGroups.map((group) => ({
      groupKey: group.groupKey,
      groupLabel: group.groupLabel,
      sampleQuantityExpression: formatMatrixImportSampleQuantity(group.sampleQuantityExpression),
    })),
  };
}

export function buildMatrixImportSelectionViewModel(
  preview: MatrixPreviewResponse | null
): MatrixImportSelectionViewModel | null {
  if (!preview) {
    return null;
  }
  const groups = buildMatrixImportSelectableGroups(preview);
  const rows: MatrixImportSelectionRow[] = preview.rows
    .filter((row) => !row.is_sample_row)
    .map((row, rowIndex) => {
      const tokensByGroupKey: Record<string, string> = {};
      groups.forEach((group, groupIndex) => {
        const previewGroup = preview.groups[groupIndex];
        const token = previewGroup ? row.group_tokens[previewGroup.group_label] ?? "" : "";
        tokensByGroupKey[group.groupKey] = token;
      });
      return {
        rowId: `selection-row-${row.source_row_index}-${rowIndex}`,
        testItem: row.test_item,
        tokensByGroupKey,
      };
    });
  return {
    sourceDocumentName: preview.source_document_name,
    groups,
    rows,
  };
}

export function buildDefaultSelectedGroupKeys(
  groups: MatrixImportSelectableGroup[]
): string[] {
  return groups.map((group) => group.groupKey);
}

export function buildMatrixImportSelectionDisabledReason(input: {
  groups: MatrixImportSelectableGroup[];
  selectedGroupKeys: string[];
  committing: boolean;
  importError: string | null;
}): string {
  if (input.committing) {
    return "Creating project draft...";
  }
  if (input.importError) {
    return input.importError;
  }
  if (input.groups.length === 0) {
    return "No groups found in import preview.";
  }
  if (input.selectedGroupKeys.length === 0) {
    return "Select at least one group.";
  }
  return "";
}
