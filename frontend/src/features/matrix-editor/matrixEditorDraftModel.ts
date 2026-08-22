import type {
  MatrixDurationAuthority,
  MatrixEditorSessionDraft,
  MatrixEditorSessionDurationAuthority,
  MatrixEditorSessionSeed,
  MatrixEditorTestRecordDraftRequest,
  MatrixPreviewResponse,
  ProjectMatrixDraft,
  ProjectMatrixDraftSaveRequest,
} from "../../api/client";
import { emptySchedulePlan, type MatrixSchedulePlan } from "./matrixSchedulePlanning";

export type GroupColumn = {
  id: string;
  name: string;
  draftGroupId: string | null;
  sourceGroupSnapshotId: string | null;
  groupKey: string;
  isSelected: boolean;
  isSourceBacked: boolean;
  sampleNote: string | null;
};

export type EditableMatrixRow = {
  id: string;
  draftRowId: string | null;
  sourceRowSnapshotId: string | null;
  isSampleRow: boolean;
  item: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  dayExpression: string;
  initialMethod: string;
  initialCondition: string;
  initialRequirement: string;
  detailExtractionStatus: string | null;
  detailExtractionNotes: string[];
  groups: Record<string, string>;
};

export function normalizeGroupDisplayName(rawLabel: string | null | undefined, fallback: string): string {
  const normalized = (rawLabel ?? "").trim();
  if (normalized.length === 0) {
    return fallback;
  }
  const withoutPrefix = normalized.replace(/^group[\s_-]*/i, "").trim();
  return withoutPrefix.length > 0 ? withoutPrefix : fallback;
}

export function buildInitialMatrixRows(): EditableMatrixRow[] {
  return [
    {
      id: "matrix-row-0",
      draftRowId: null,
      sourceRowSnapshotId: null,
      isSampleRow: false,
      item: "Visual Examination",
      section: "",
      method: "EIA-364-18B",
      condition: "10x min magnification",
      requirement: "No detrimental condition",
      dayExpression: "",
      initialMethod: "EIA-364-18B",
      initialCondition: "10x min magnification",
      initialRequirement: "No detrimental condition",
      detailExtractionStatus: "missing",
      detailExtractionNotes: ["template-fallback-visual"],
      groups: { "group-1": "1" }
    },
    {
      id: "matrix-row-1",
      draftRowId: null,
      sourceRowSnapshotId: null,
      isSampleRow: false,
      item: "",
      section: "",
      method: "",
      condition: "",
      requirement: "",
      dayExpression: "",
      initialMethod: "",
      initialCondition: "",
      initialRequirement: "",
      detailExtractionStatus: "missing",
      detailExtractionNotes: [],
      groups: { "group-1": "" }
    }
  ];
}

export function cloneRows(rows: EditableMatrixRow[]): EditableMatrixRow[] {
  return rows.map((row) => ({
    ...row,
    groups: { ...row.groups }
  }));
}

export function buildEmptyRow(groups: string[], rowIndex: number): EditableMatrixRow {
  const groupValues: Record<string, string> = {};
  groups.forEach((group) => {
    groupValues[group] = "";
  });
  return {
    id: `matrix-row-new-${Date.now()}-${rowIndex}`,
    draftRowId: null,
    sourceRowSnapshotId: null,
    isSampleRow: false,
    item: "",
    section: "",
    method: "",
    condition: "",
    requirement: "",
    dayExpression: "",
    initialMethod: "",
    initialCondition: "",
    initialRequirement: "",
    detailExtractionStatus: "missing",
    detailExtractionNotes: [],
    groups: groupValues
  };
}

export function buildInitialGroupColumns(): GroupColumn[] {
  return [
    {
      id: "group-1",
      name: "1",
      draftGroupId: null,
      sourceGroupSnapshotId: null,
      groupKey: "g1",
      isSelected: true,
      isSourceBacked: false,
      sampleNote: null,
    },
  ];
}

function previewRowIdentity(
  row: Pick<MatrixPreviewResponse["rows"][number], "test_item" | "source_section">
): string {
  return `${row.test_item.trim().toLowerCase()}|${(row.source_section ?? "").trim().toLowerCase()}`;
}

function editorRowIdentity(row: EditableMatrixRow): string {
  return `${row.item.trim().toLowerCase()}|${row.section.trim().toLowerCase()}`;
}

function readPreviewGroupToken(
  row: MatrixPreviewResponse["rows"][number] | undefined,
  group: MatrixPreviewResponse["groups"][number]
): string {
  if (!row) {
    return "";
  }
  return row.group_tokens[group.group_label] ?? row.group_tokens[group.group_key] ?? "";
}

function readPreviewSampleValue(
  preview: MatrixPreviewResponse,
  group: MatrixPreviewResponse["groups"][number]
): string {
  const sampleRows = [...preview.rows]
    .sort((left, right) => left.source_row_index - right.source_row_index)
    .filter((row) => row.is_sample_row);
  const sampleEntries = sampleRows
    .map((row) => readPreviewGroupToken(row, group).trim())
    .filter((value) => value.length > 0);
  const uniqueSampleValues = [...new Set(sampleEntries)];
  if (uniqueSampleValues.length === 1) {
    return uniqueSampleValues[0];
  }
  return sampleEntries[0] ?? group.sample_quantity_expression ?? "";
}

export function cloneGroups(groups: GroupColumn[]): GroupColumn[] {
  return groups.map((group) => ({ ...group }));
}

function buildMatrixFromProjectMatrixDraft(
  draft: MatrixEditorSessionDraft
): {
  groups: GroupColumn[];
  rows: EditableMatrixRow[];
  samples: Record<string, string>;
} {
  const groups: GroupColumn[] = draft.groups
    .slice()
    .sort((left, right) => left.group_order - right.group_order)
    .map((group) => ({
      id: group.draft_group_id,
      name: normalizeGroupDisplayName(group.group_label, `${group.group_order}`),
      draftGroupId: group.draft_group_id,
      sourceGroupSnapshotId: group.source_group_snapshot_id ?? null,
      groupKey: group.group_key,
      isSelected: group.is_selected,
      isSourceBacked: group.source_group_snapshot_id != null,
      sampleNote: group.sample_note ?? null,
    }));
  const rows: EditableMatrixRow[] = draft.rows
    .slice()
    .sort((left, right) => left.row_order - right.row_order)
    .filter((row) => !row.is_sample_row)
    .map((row) => {
      const groupValues: Record<string, string> = {};
      groups.forEach((group) => {
        groupValues[group.id] = "";
      });
      return {
        id: row.draft_row_id,
        draftRowId: row.draft_row_id,
        sourceRowSnapshotId: row.source_row_snapshot_id ?? null,
        isSampleRow: row.is_sample_row,
        item: row.test_item,
        section: row.source_section ?? "",
        method: row.method ?? "",
        condition: row.condition ?? "",
        requirement: row.requirement ?? "",
        dayExpression: row.day_expression ?? "",
        initialMethod: row.method ?? "",
        initialCondition: row.condition ?? "",
        initialRequirement: row.requirement ?? "",
        detailExtractionStatus: null,
        detailExtractionNotes: [],
        groups: groupValues,
      };
    });
  const rowByDraftId = new Map(rows.map((row) => [row.draftRowId ?? "", row]));
  draft.cells.forEach((cell) => {
    const targetRow = rowByDraftId.get(cell.draft_row_id);
    if (!targetRow) {
      return;
    }
    targetRow.groups[cell.draft_group_id] = cell.cell_value;
  });
  const samples: Record<string, string> = {};
  groups.forEach((group) => {
    samples[group.id] = draft.groups.find((item) => item.draft_group_id === group.id)?.sample_quantity_expression ?? "";
  });
  return { groups, rows, samples };
}

export function buildMatrixFromSessionSeedDraft(
  draft: MatrixEditorSessionDraft,
  sourcePreview: MatrixPreviewResponse | null
): {
  groups: GroupColumn[];
  rows: EditableMatrixRow[];
  samples: Record<string, string>;
} {
  const mapped = buildMatrixFromProjectMatrixDraft(draft);
  if (!sourcePreview) {
    return mapped;
  }

  const currentGroupByKey = new Map(
    mapped.groups.map((group) => [group.groupKey, group])
  );
  const nextGroups: GroupColumn[] = sourcePreview.groups.map((previewGroup, index) => {
    const existing = currentGroupByKey.get(previewGroup.group_key);
    if (existing) {
      return {
        ...existing,
        name: normalizeGroupDisplayName(previewGroup.group_label, existing.name),
        sampleNote: previewGroup.sample_note ?? existing.sampleNote,
      };
    }
    return {
      id: `source-group-${index + 1}`,
      name: normalizeGroupDisplayName(previewGroup.group_label, `${index + 1}`),
      draftGroupId: null,
      sourceGroupSnapshotId: null,
      groupKey: previewGroup.group_key,
      isSelected: false,
      isSourceBacked: true,
      sampleNote: previewGroup.sample_note ?? null,
    };
  });
  mapped.groups.forEach((group) => {
    if (!nextGroups.some((nextGroup) => nextGroup.groupKey === group.groupKey)) {
      nextGroups.push(group);
    }
  });

  const previewRows = [...sourcePreview.rows]
    .sort((left, right) => left.source_row_index - right.source_row_index)
    .filter((row) => !row.is_sample_row);
  const currentRowByIdentity = new Map(
    mapped.rows.map((row) => [editorRowIdentity(row), row])
  );
  const consumedRowIds = new Set<string>();
  const previewGroupByKey = new Map(
    sourcePreview.groups.map((group) => [group.group_key, group])
  );
  const nextRows: EditableMatrixRow[] = previewRows.map((previewRow, rowIndex) => {
    const identity = previewRowIdentity(previewRow);
    const existing = currentRowByIdentity.get(identity) ?? mapped.rows[rowIndex] ?? null;
    if (existing) {
      consumedRowIds.add(existing.id);
    }
    const groupValues: Record<string, string> = {};
    nextGroups.forEach((group) => {
      const existingGroup = currentGroupByKey.get(group.groupKey);
      if (existing && existingGroup && existing.groups[existingGroup.id] !== undefined) {
        groupValues[group.id] = existing.groups[existingGroup.id];
        return;
      }
      const previewGroup = previewGroupByKey.get(group.groupKey);
      groupValues[group.id] = previewGroup ? readPreviewGroupToken(previewRow, previewGroup) : "";
    });
    return {
      id: existing?.id ?? `source-row-${rowIndex + 1}`,
      draftRowId: existing?.draftRowId ?? null,
      sourceRowSnapshotId: existing?.sourceRowSnapshotId ?? null,
      isSampleRow: false,
      item: existing?.item ?? previewRow.test_item,
      section: existing?.section ?? previewRow.source_section ?? "",
      method: existing?.method?.trim() ? existing.method : previewRow.method ?? "",
      condition: existing?.condition?.trim() ? existing.condition : previewRow.condition ?? "",
      requirement: existing?.requirement?.trim() ? existing.requirement : previewRow.requirement ?? "",
      dayExpression: existing?.dayExpression ?? "",
      initialMethod: existing?.initialMethod ?? (existing?.method?.trim() ? existing.method : previewRow.method ?? ""),
      initialCondition: existing?.initialCondition ?? (existing?.condition?.trim() ? existing.condition : previewRow.condition ?? ""),
      initialRequirement: existing?.initialRequirement ?? (existing?.requirement?.trim() ? existing.requirement : previewRow.requirement ?? ""),
      detailExtractionStatus: previewRow.detail_extraction_status ?? existing?.detailExtractionStatus ?? null,
      detailExtractionNotes: previewRow.detail_extraction_notes ?? existing?.detailExtractionNotes ?? [],
      groups: groupValues,
    };
  });
  mapped.rows.forEach((row) => {
    if (consumedRowIds.has(row.id)) {
      return;
    }
    const groupValues: Record<string, string> = {};
    nextGroups.forEach((group) => {
      const existingGroup = currentGroupByKey.get(group.groupKey);
      groupValues[group.id] = existingGroup ? row.groups[existingGroup.id] ?? "" : "";
    });
    nextRows.push({ ...row, groups: groupValues });
  });

  const samples: Record<string, string> = {};
  nextGroups.forEach((group) => {
    const existingGroup = currentGroupByKey.get(group.groupKey);
    if (existingGroup && mapped.samples[existingGroup.id] !== undefined) {
      samples[group.id] = mapped.samples[existingGroup.id];
      return;
    }
    const previewGroup = previewGroupByKey.get(group.groupKey);
    samples[group.id] = previewGroup ? readPreviewSampleValue(sourcePreview, previewGroup) : "";
  });

  return { groups: nextGroups, rows: nextRows, samples };
}

export function buildSessionDraftFromProjectMatrixDraft(
  draft: ProjectMatrixDraft
): MatrixEditorSessionDraft {
  return {
    groups: draft.groups.map((group) => ({
      draft_group_id: group.draft_group_id,
      source_group_snapshot_id: group.source_group_snapshot_id ?? null,
      group_order: group.group_order,
      group_key: group.group_key,
      group_label: group.group_label,
      is_selected: group.is_selected,
      sample_quantity_expression: group.sample_quantity_expression ?? null,
      sample_note: group.sample_note ?? null,
    })),
    rows: draft.rows.map((row) => ({
      draft_row_id: row.draft_row_id,
      source_row_snapshot_id: row.source_row_snapshot_id ?? null,
      row_order: row.row_order,
      test_item: row.test_item,
      source_section: row.source_section ?? null,
      method: row.method ?? null,
      condition: row.condition ?? null,
      requirement: row.requirement ?? null,
      day_expression: row.day_expression ?? null,
      is_sample_row: row.is_sample_row,
    })),
    cells: draft.cells.map((cell) => ({
      draft_row_id: cell.draft_row_id,
      draft_group_id: cell.draft_group_id,
      cell_value: cell.cell_value,
    })),
    duration_authorities: mapProjectDurationAuthoritiesForSession(
      draft.duration_authorities
    ),
  };
}

export function mapProjectDurationAuthoritiesForSession(
  authorities: MatrixDurationAuthority[] | undefined
): MatrixEditorSessionDurationAuthority[] {
  return (authorities ?? []).map((item) => ({
    draft_duration_authority_id: item.duration_authority_id,
    draft_group_id: item.group_id,
    draft_row_id: item.row_id,
    step_sequence: item.step_sequence,
    step_suffix_note: item.step_suffix_note,
    duration_value: item.duration_value,
    duration_unit: item.duration_unit,
    normalized_hours: item.normalized_hours,
    source_kind: item.source_kind,
    source_field: item.source_field,
    source_import_id: item.source_import_id ?? null,
    source_fingerprint: item.source_fingerprint,
    lineage_fingerprint: item.lineage_fingerprint,
    authority_revision: item.authority_revision,
    status: item.status,
  }));
}

export function buildDraftSavePayload(
  rows: EditableMatrixRow[],
  groups: GroupColumn[],
  samples: Record<string, string>,
  schedulePlan: MatrixSchedulePlan,
  durationAuthorities: MatrixEditorSessionDurationAuthority[] = []
): ProjectMatrixDraftSaveRequest {
  const payloadGroups = groups.map((group, index) => ({
    draft_group_id: group.draftGroupId ?? group.id,
    source_group_snapshot_id: group.sourceGroupSnapshotId,
    group_order: index + 1,
    group_key: group.groupKey.trim() || `g${index + 1}`,
    group_label: group.name.trim() || `${index + 1}`,
    is_selected: group.isSelected,
    sample_quantity_expression: samples[group.id]?.trim() ? samples[group.id].trim() : null,
    sample_note: group.sampleNote,
  }));
  const payloadRows = rows.map((row, index) => ({
    draft_row_id: row.draftRowId ?? row.id,
    source_row_snapshot_id: row.sourceRowSnapshotId,
    row_order: index + 1,
    test_item: row.item,
    source_section: row.section.trim() ? row.section : null,
    method: row.method.trim() ? row.method : null,
    condition: row.condition.trim() ? row.condition : null,
    requirement: row.requirement.trim() ? row.requirement : null,
    day_expression: row.dayExpression.trim() ? row.dayExpression.trim() : null,
    is_sample_row: row.isSampleRow,
  }));
  const payloadCells: ProjectMatrixDraftSaveRequest["cells"] = [];
  rows.forEach((row) => {
    groups.forEach((group) => {
      const cellValue = (row.groups[group.id] ?? "").trim();
      if (!cellValue) {
        return;
      }
      payloadCells.push({
        draft_row_id: row.draftRowId ?? row.id,
        draft_group_id: group.draftGroupId ?? group.id,
        cell_value: cellValue,
      });
    });
  });
  return {
    post_test_buffer_days: schedulePlan.postTestBufferDays.trim() || null,
    sample_received_date: schedulePlan.sampleReceivedDate.trim() || null,
    planned_test_start_date: schedulePlan.plannedTestStartDate.trim() || null,
    planned_test_complete_date: schedulePlan.plannedTestCompleteDate.trim() || null,
    estimated_completion_date: schedulePlan.estimatedCompletionDate.trim() || null,
    groups: payloadGroups,
    rows: payloadRows,
    cells: payloadCells,
    duration_authorities: durationAuthorities.map((item) => ({
      draft_duration_authority_id: item.draft_duration_authority_id ?? null,
      draft_group_id: item.draft_group_id,
      draft_row_id: item.draft_row_id,
      step_sequence: item.step_sequence,
      step_suffix_note: item.step_suffix_note,
      duration_value: item.duration_value,
      duration_unit: item.duration_unit,
      source_kind: item.source_kind,
      source_field: item.source_field,
      source_import_id: item.source_import_id ?? null,
      source_fingerprint: item.source_fingerprint,
      lineage_fingerprint: item.lineage_fingerprint,
      authority_revision: item.authority_revision,
    })),
  };
}

export function buildMatrixEditorTestRecordDraftRequest(
  rows: EditableMatrixRow[],
  groups: GroupColumn[],
  samples: Record<string, string>
): MatrixEditorTestRecordDraftRequest {
  const selectedGroups = groups.filter((group) => group.isSelected);
  return {
    source: "matrix_editor_current_ui_state",
    groups: selectedGroups.map((group, index) => ({
      group_key: group.groupKey.trim() || `g${index + 1}`,
      group_label: group.name.trim() || `${index + 1}`,
      sample_quantity_expression: samples[group.id]?.trim() ?? "",
    })),
    rows: rows.map((row) => {
      const groupValues: Record<string, string> = {};
      selectedGroups.forEach((group, index) => {
        const groupKey = group.groupKey.trim() || `g${index + 1}`;
        groupValues[groupKey] = row.groups[group.id] ?? "";
      });
      return {
        test_item: row.item,
        section: row.section,
        method: row.method,
        condition: row.condition,
        requirement: row.requirement,
        is_sample_row: row.isSampleRow,
        group_values: groupValues,
      };
    }),
  };
}

type AuthorityComparableGroup = {
  groupOrder: number;
  groupKey: string;
  groupLabel: string;
  sampleQuantityExpression: string;
  sampleNote: string;
  isSelected: boolean;
};

type AuthorityComparableRow = {
  rowOrder: number;
  testItem: string;
  sourceSection: string;
  method: string;
  condition: string;
  requirement: string;
  dayExpression: string;
};

type AuthorityComparableDraftGroup = AuthorityComparableGroup & {
  draftGroupId: string;
};

type AuthorityComparableDraftRow = AuthorityComparableRow & {
  draftRowId: string;
};

function buildAuthorityComparableSignatureFromDraftPayload(
  payload: ProjectMatrixDraftSaveRequest
): string {
  const groups: AuthorityComparableDraftGroup[] = payload.groups
    .map((group) => ({
      groupOrder: group.group_order,
      groupKey: group.group_key ?? "",
      groupLabel: group.group_label ?? "",
      sampleQuantityExpression: group.sample_quantity_expression ?? "",
      sampleNote: group.sample_note ?? "",
      isSelected: Boolean(group.is_selected),
      draftGroupId: group.draft_group_id ?? "",
    }))
    .sort((left, right) => left.groupOrder - right.groupOrder);

  const rows: AuthorityComparableDraftRow[] = payload.rows
    .filter((row) => !row.is_sample_row)
    .map((row) => ({
      rowOrder: row.row_order,
      testItem: row.test_item ?? "",
      sourceSection: row.source_section ?? "",
      method: row.method ?? "",
      condition: row.condition ?? "",
      requirement: row.requirement ?? "",
      dayExpression: row.day_expression ?? "",
      draftRowId: row.draft_row_id ?? "",
    }))
    .sort((left, right) => left.rowOrder - right.rowOrder);

  const groupIndexByDraftGroupId = new Map<string, number>();
  groups.forEach((group, index) => {
    groupIndexByDraftGroupId.set(group.draftGroupId, index);
  });
  const rowIndexByDraftRowId = new Map<string, number>();
  rows.forEach((row, index) => {
    rowIndexByDraftRowId.set(row.draftRowId, index);
  });

  const cellMap = new Map<string, string>();
  payload.cells.forEach((cell) => {
    const rowIndex = rowIndexByDraftRowId.get(cell.draft_row_id ?? "");
    const groupIndex = groupIndexByDraftGroupId.get(cell.draft_group_id ?? "");
    if (rowIndex === undefined || groupIndex === undefined) {
      return;
    }
    const value = (cell.cell_value ?? "").trim();
    if (!value) {
      return;
    }
    cellMap.set(`${rowIndex}:${groupIndex}`, value);
  });

  return JSON.stringify({
    groups: groups.map((group) => ({
      groupOrder: group.groupOrder,
      groupKey: group.groupKey.trim(),
      groupLabel: group.groupLabel.trim(),
      sampleQuantityExpression: group.sampleQuantityExpression.trim(),
      sampleNote: group.sampleNote.trim(),
      isSelected: group.isSelected,
    })),
    rows: rows.map((row, rowIndex) => ({
      rowOrder: row.rowOrder,
      testItem: row.testItem.trim(),
      sourceSection: row.sourceSection.trim(),
      method: row.method.trim(),
      condition: row.condition.trim(),
      requirement: row.requirement.trim(),
      dayExpression: row.dayExpression.trim(),
      cells: groups.map((_, groupIndex) => cellMap.get(`${rowIndex}:${groupIndex}`) ?? ""),
    })),
    schedule: {
      postTestBufferDays: payload.post_test_buffer_days ?? "",
      sampleReceivedDate: payload.sample_received_date ?? "",
      plannedTestStartDate: payload.planned_test_start_date ?? "",
      plannedTestCompleteDate: payload.planned_test_complete_date ?? "",
      estimatedCompletionDate: payload.estimated_completion_date ?? "",
    },
  });
}

export function buildAuthorityComparableSignatureFromDraft(
  draft: MatrixEditorSessionDraft,
  schedulePlan: MatrixSchedulePlan
): string {
  const mapped = buildMatrixFromProjectMatrixDraft(draft);
  const payload = buildDraftSavePayload(mapped.rows, mapped.groups, mapped.samples, schedulePlan);
  return buildAuthorityComparableSignatureFromDraftPayload(payload);
}

export function schedulePlanFromSeed(seed: MatrixEditorSessionSeed): MatrixSchedulePlan {
  return {
    postTestBufferDays: seed.post_test_buffer_days ?? "",
    sampleReceivedDate: seed.sample_received_date ?? "",
    plannedTestStartDate: seed.planned_test_start_date ?? "",
    plannedTestCompleteDate: seed.planned_test_complete_date ?? "",
    estimatedCompletionDate: seed.estimated_completion_date ?? "",
  };
}

export function schedulePlanFromProjectMatrixDraft(draft: ProjectMatrixDraft): MatrixSchedulePlan {
  return {
    postTestBufferDays: draft.record.post_test_buffer_days ?? "",
    sampleReceivedDate: draft.record.sample_received_date ?? "",
    plannedTestStartDate: draft.record.planned_test_start_date ?? "",
    plannedTestCompleteDate: draft.record.planned_test_complete_date ?? "",
    estimatedCompletionDate: draft.record.estimated_completion_date ?? "",
  };
}

export function nextGroupId(groups: GroupColumn[]): string {
  let max = 0;
  groups.forEach((group) => {
    const match = group.id.match(/^group-(\d+)$/i);
    if (!match) {
      return;
    }
    const value = Number(match[1]);
    if (value > max) {
      max = value;
    }
  });
  return `group-${max + 1}`;
}

export function normalizeGroupName(name: string): string {
  return name.trim().toLowerCase();
}

function sampleQuantityHasDigit(value: string | null | undefined): boolean {
  return /\d/.test((value ?? "").trim());
}

export function buildInvalidSelectedSampleGroupIds(
  groups: GroupColumn[],
  samples: Record<string, string>
): Set<string> {
  return new Set(
    groups
      .filter((group) => group.isSelected)
      .filter((group) => !sampleQuantityHasDigit(samples[group.id]))
      .map((group) => group.id)
  );
}
