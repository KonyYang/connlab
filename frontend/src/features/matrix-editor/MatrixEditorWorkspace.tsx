import { useEffect, useLayoutEffect, useRef, useState, type ChangeEvent, type MouseEvent, type ReactElement } from "react";
import { LoadingState } from "../../components/common/LoadingState";
import { useProjectRuntimeConsoleModel } from "../project-workbench/useProjectRuntimeConsoleModel";
import {
  commitMatrixImport,
  confirmProjectMatrixDraft,
  confirmProjectMatrixRevisionDraft,
  createMatrixRevisionDraft,
  fetchActiveConfirmedMatrixSnapshot,
  getProjectMatrixDraft,
  listProjectMatrixDrafts,
  matrixPreviewPdfUrl,
  previewProjectTestPlanMatrixFromUpload,
  saveProjectMatrixDraft,
  type ConfirmedMatrixSnapshot,
  type MatrixPreviewResponse,
  type MatrixImportCommitResponse,
  type ProjectMatrixDraft,
  type ProjectMatrixDraftSaveRequest,
} from "../../api/client";
import { MatrixImportSelectionMode } from "./MatrixImportSelectionMode";
import {
  buildMatrixImportSessionActionState,
  preserveSelectedGroupKeys,
} from "./matrixImportSessionModel";
import { MatrixWorkspaceActionGroups } from "./MatrixWorkspaceActionGroups";
import {
  buildDefaultSelectedGroupKeys,
  buildMatrixImportSelectionViewModel,
  buildMatrixImportSelectionDisabledReason,
  type MatrixImportSelectionViewModel,
} from "./matrixImportSelectionSelectors";
import "../../workbench.css";

type MatrixEditorWorkspaceProps = {
  projectId: string;
  onBackToWorkbench: () => void;
};

type GroupColumn = {
  id: string;
  name: string;
  draftGroupId: string | null;
  sourceGroupSnapshotId: string | null;
  groupKey: string;
  isSelected: boolean;
  sampleNote: string | null;
};

type EditableMatrixRow = {
  id: string;
  draftRowId: string | null;
  sourceRowSnapshotId: string | null;
  isSampleRow: boolean;
  item: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  groups: Record<string, string>;
};

type MatrixSnapshot = {
  rows: EditableMatrixRow[];
  groups: GroupColumn[];
};

type MatrixSaveState = "idle" | "dirty" | "saving" | "saved" | "error";
type MatrixPublishState = "idle" | "loading" | "success" | "error";
type MatrixPublishMode = "first_authority" | "revision_authority";

const AUTO_SAVE_DEBOUNCE_MS = 600;

const AUTO_SAVE_STATUS_COPY: Record<MatrixSaveState, string> = {
  idle: "Saved",
  dirty: "Unsaved changes",
  saving: "Saving...",
  saved: "Saved",
  error: "Save failed. Retry before confirming.",
};

type StepOutputOverride = {
  requirement?: string;
  description?: string;
};

type StepPreviewRow = {
  key: string;
  stepNo: number;
  rawToken: string;
  suffixNote: string | null;
  rowId: string;
  sourceRequirement: string;
  sourceTestItem: string;
  sourceSection: string;
  sourceItemSectionNote: string | null;
  sourceStepNote: string | null;
  requirementValue: string;
  descriptionValue: string;
};

type PreviewStepNotePayload = {
  sourceNote: string | null;
  sourceItemSectionNote: string | null;
};

type StepDescriptionFamily = "LLCR" | "IR" | "DWV" | "MATING";

type MatrixContextMenu =
  | { kind: "row"; rowIndex: number; x: number; y: number }
  | { kind: "group"; groupId: string; x: number; y: number };

type MatrixAutoGrowTextareaProps = {
  ariaLabel: string;
  className?: string;
  errorMessage?: string;
  value: string;
  onFocus?: () => void;
  onChange: (value: string) => void;
};

function buildInitialMatrixRows(): EditableMatrixRow[] {
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
      groups: { "group-1": "" }
    }
  ];
}

function cloneRows(rows: EditableMatrixRow[]): EditableMatrixRow[] {
  return rows.map((row) => ({
    ...row,
    groups: { ...row.groups }
  }));
}

function buildEmptyRow(groups: string[], rowIndex: number): EditableMatrixRow {
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
    groups: groupValues
  };
}

function buildInitialGroupColumns(): GroupColumn[] {
  return [
    {
      id: "group-1",
      name: "1",
      draftGroupId: null,
      sourceGroupSnapshotId: null,
      groupKey: "g1",
      isSelected: true,
      sampleNote: null,
    },
  ];
}

function buildMatrixFromPreview(
  preview: MatrixPreviewResponse
): {
  groups: GroupColumn[];
  rows: EditableMatrixRow[];
  samples: Record<string, string>;
  sampleMergeNotes: Record<string, string>;
} {
  const groups: GroupColumn[] = preview.groups.map((group, index) => ({
    id: `group-${index + 1}`,
    name: group.group_label,
    draftGroupId: null,
    sourceGroupSnapshotId: null,
    groupKey: group.group_key || `g${index + 1}`,
    isSelected: true,
    sampleNote: group.sample_note ?? null,
  }));
  const sourceRows = [...preview.rows].sort((a, b) => a.source_row_index - b.source_row_index);
  const dataRows = sourceRows.filter((row) => !row.is_sample_row);
  const sampleRows = sourceRows.filter((row) => row.is_sample_row);
  const rows: EditableMatrixRow[] = dataRows.map((row, index) => {
    const groupValues: Record<string, string> = {};
    preview.groups.forEach((previewGroup, groupIndex) => {
      const groupId = `group-${groupIndex + 1}`;
      groupValues[groupId] = row.group_tokens[previewGroup.group_label] ?? "";
    });
    return {
      id: `matrix-import-row-${index + 1}`,
      draftRowId: null,
      sourceRowSnapshotId: null,
      isSampleRow: false,
      item: row.test_item,
      section: row.source_section ?? "",
      method: "",
      condition: "",
      requirement: "",
      groups: groupValues,
    };
  });
  const samples: Record<string, string> = {};
  const sampleMergeNotes: Record<string, string> = {};
  preview.groups.forEach((group, groupIndex) => {
    const groupId = `group-${groupIndex + 1}`;
    const label = group.group_label;
    const sampleEntries = sampleRows
      .map((row) => ({
        label: (row.source_section ?? row.test_item).trim(),
        value: (row.group_tokens[label] ?? "").trim(),
      }))
      .filter((entry) => entry.value.length > 0);
    const uniqueSampleValues = [...new Set(sampleEntries.map((entry) => entry.value))];
    const sampleFromRow = sampleEntries[0]?.value ?? "";
    samples[groupId] = uniqueSampleValues.length === 1 ? uniqueSampleValues[0] : sampleFromRow || (group.sample_quantity_expression ?? "");
    const uniqueLabels = [...new Set(sampleEntries.map((entry) => entry.label).filter((entryLabel) => entryLabel.length > 0))];
    if (uniqueSampleValues.length === 1 && uniqueLabels.length > 1) {
      sampleMergeNotes[groupId] = `${uniqueLabels.join(" / ")} share the same sample quantity.`;
    }
  });
  return { groups, rows, samples, sampleMergeNotes };
}

function cloneGroups(groups: GroupColumn[]): GroupColumn[] {
  return groups.map((group) => ({ ...group }));
}

function buildMatrixFromProjectMatrixDraft(
  draft: ProjectMatrixDraft
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
      name: group.group_label,
      draftGroupId: group.draft_group_id,
      sourceGroupSnapshotId: group.source_group_snapshot_id ?? null,
      groupKey: group.group_key,
      isSelected: group.is_selected,
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

function buildDraftSavePayload(
  rows: EditableMatrixRow[],
  groups: GroupColumn[],
  samples: Record<string, string>
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
    groups: payloadGroups,
    rows: payloadRows,
    cells: payloadCells,
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
      cells: groups.map((_, groupIndex) => cellMap.get(`${rowIndex}:${groupIndex}`) ?? ""),
    })),
  });
}

function buildAuthorityComparableSignatureFromDraft(
  draft: ProjectMatrixDraft
): string {
  const mapped = buildMatrixFromProjectMatrixDraft(draft);
  const payload = buildDraftSavePayload(mapped.rows, mapped.groups, mapped.samples);
  return buildAuthorityComparableSignatureFromDraftPayload(payload);
}

function buildAuthorityComparableSignatureFromConfirmedSnapshot(
  snapshot: ConfirmedMatrixSnapshot
): string {
  const groups: Array<
    AuthorityComparableGroup & { confirmedGroupId: string }
  > = [...snapshot.groups]
    .map((group) => ({
      confirmedGroupId: group.confirmed_group_id,
      groupOrder: group.group_order,
      groupKey: group.group_key ?? "",
      groupLabel: group.group_label ?? "",
      sampleQuantityExpression: group.sample_quantity_expression ?? "",
      sampleNote: group.sample_note ?? "",
      isSelected: true,
    }))
    .sort((left, right) => left.groupOrder - right.groupOrder);

  const rows: Array<AuthorityComparableRow & { confirmedRowId: string }> = [
    ...snapshot.rows,
  ]
    .map((row) => ({
      confirmedRowId: row.confirmed_row_id,
      rowOrder: row.row_order,
      testItem: row.test_item ?? "",
      sourceSection: row.source_section ?? "",
      method: row.method ?? "",
      condition: row.condition ?? "",
      requirement: row.requirement ?? "",
    }))
    .sort((left, right) => left.rowOrder - right.rowOrder);

  const groupIndexById = new Map<string, number>();
  groups.forEach((group, index) => {
    groupIndexById.set(group.confirmedGroupId, index);
  });
  const rowIndexById = new Map<string, number>();
  rows.forEach((row, index) => {
    rowIndexById.set(row.confirmedRowId, index);
  });

  const cellMap = new Map<string, string>();
  snapshot.cells.forEach((cell) => {
    const rowIndex = rowIndexById.get(cell.confirmed_row_id ?? "");
    const groupIndex = groupIndexById.get(cell.confirmed_group_id ?? "");
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
      isSelected: true,
    })),
    rows: rows.map((row, rowIndex) => ({
      rowOrder: row.rowOrder,
      testItem: row.testItem.trim(),
      sourceSection: row.sourceSection.trim(),
      method: row.method.trim(),
      condition: row.condition.trim(),
      requirement: row.requirement.trim(),
      cells: groups.map((_, groupIndex) => cellMap.get(`${rowIndex}:${groupIndex}`) ?? ""),
    })),
  });
}

const MVP_REVISION_CONFIRMED_BY = "connlab-operator";

function parseRequestError(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message;
  }
  return fallback;
}

function parsePositiveInteger(input: string): number | null {
  const normalized = input.trim();
  if (!normalized) {
    return null;
  }
  const parsed = Number.parseInt(normalized, 10);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return null;
  }
  return parsed;
}

function buildManualPreviewPayloadFromDraftPayload(
  payload: ProjectMatrixDraftSaveRequest
): MatrixPreviewResponse {
  const tokenByRowGroup = new Map<string, string>();
  payload.cells.forEach((cell) => {
    const value = (cell.cell_value ?? "").trim();
    if (!value) {
      return;
    }
    tokenByRowGroup.set(`${cell.draft_row_id}:${cell.draft_group_id}`, value);
  });

  const groups = [...payload.groups]
    .sort((left, right) => left.group_order - right.group_order)
    .map((group) => ({
      group_key: group.group_key ?? "",
      group_label: group.group_label ?? "",
      source_table_index: 0,
      extraction_status: "manual",
      sample_size: null,
      sample_quantity_expression: group.sample_quantity_expression ?? null,
      sample_note: group.sample_note ?? null,
      steps: [],
    }));

  const rows = [...payload.rows]
    .sort((left, right) => left.row_order - right.row_order)
    .map((row) => {
      const group_tokens: Record<string, string> = {};
      payload.groups.forEach((group) => {
        const value = tokenByRowGroup.get(`${row.draft_row_id}:${group.draft_group_id}`) ?? "";
        const groupLabel = (group.group_label ?? "").trim();
        const groupKey = (group.group_key ?? "").trim();
        if (groupLabel) {
          group_tokens[groupLabel] = value;
        }
        if (groupKey) {
          group_tokens[groupKey] = value;
        }
      });
      return {
        source_row_index: row.row_order,
        test_item: row.test_item ?? "",
        source_section: row.source_section ?? null,
        group_tokens,
        is_sample_row: Boolean(row.is_sample_row),
      };
    });

  return {
    project_id: null,
    source_document_path: "manual://matrix-editor",
    source_document_name: "Matrix Editor Manual Draft",
    source_format: "manual",
    capability_status: "supported",
    generated_at: new Date().toISOString(),
    selected_table_index: 0,
    selected_page_number: 1,
    selected_page_table_index: 1,
    candidate_tables: [],
    preview_pdf_token: null,
    rows,
    groups,
    warnings: [],
    blockers: [],
  };
}

function buildConfirmRevisionGuard(input: {
  hasProjectId: boolean;
  projectMatrixDraftId: string | null;
  draftBaseConfirmedMatrixId: string | null;
  hasUnsavedChanges: boolean;
  hasMatrixValidationError: boolean;
  hasPersistedDraft: boolean;
  busy: boolean;
  alreadyConfirmed: boolean;
  validationMessage: string;
}): ConfirmRevisionGuard {
  if (!input.hasProjectId) {
    return { canConfirm: false, reason: "No project id." };
  }
  if (input.alreadyConfirmed) {
    return { canConfirm: false, reason: "Revision already confirmed." };
  }
  if (input.busy) {
    return { canConfirm: false, reason: "Action in progress." };
  }
  if (!input.projectMatrixDraftId || !input.hasPersistedDraft) {
    return { canConfirm: false, reason: "No persisted matrix draft target." };
  }
  if (!input.draftBaseConfirmedMatrixId) {
    return { canConfirm: false, reason: "Current draft is not a revision draft." };
  }
  if (input.hasUnsavedChanges) {
    return { canConfirm: false, reason: "Save changes before confirming revision." };
  }
  if (input.hasMatrixValidationError) {
    return {
      canConfirm: false,
      reason: input.validationMessage || "Resolve matrix validation errors before confirming revision.",
    };
  }
  return { canConfirm: true, reason: "" };
}

function buildRevisionConfirmedMessage(snapshot: ConfirmedMatrixSnapshot): string {
  const revision = snapshot.version.confirmed_revision;
  return `Revision confirmed (v${revision}).`;
}

function buildActiveMatrixConfirmedMessage(snapshot: ConfirmedMatrixSnapshot): string {
  const revision = snapshot.version.confirmed_revision;
  return `Active matrix confirmed (v${revision}).`;
}

function nextGroupId(groups: GroupColumn[]): string {
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

function normalizeGroupName(name: string): string {
  return name.trim().toLowerCase();
}

type ParsedStepToken = {
  sequence: number;
  rawToken: string;
  suffixNote: string | null;
};

type ConfirmRevisionGuard = {
  canConfirm: boolean;
  reason: string;
};

function parseStepTokens(rawValue: string): { isValid: boolean; numbers: number[]; tokens: ParsedStepToken[]; errorMessage: string } {
  const normalized = rawValue.trim();
  if (normalized === "") {
    return { isValid: true, numbers: [], tokens: [], errorMessage: "" };
  }
  const normalizedForSplit = normalized.replaceAll("\n", ",").replaceAll("，", ",").replaceAll(";", ",");
  const parts = normalizedForSplit.split(",").map((part) => part.trim()).filter((part) => part.length > 0);
  const tokens: ParsedStepToken[] = [];
  for (const part of parts) {
    const match = part.match(/^(\d+)\s*(\([a-zA-Z]\)|[*#])?$/);
    if (!match) {
      return {
        isValid: false,
        numbers: [],
        tokens: [],
        errorMessage: "Only digits and commas are allowed (extended tokens: 3(a), 6#, 10*).",
      };
    }
    tokens.push({
      sequence: Number(match[1]),
      rawToken: part,
      suffixNote: match[2] ?? null
    });
  }
  return {
    isValid: true,
    numbers: tokens.map((token) => token.sequence),
    tokens,
    errorMessage: "",
  };
}

function stepOutputKey(groupId: string, stepNo: number, rowId: string): string {
  return `${groupId}:${stepNo}:${rowId}`;
}

const STEP_DESCRIPTION_FAMILY_ALIASES: Record<StepDescriptionFamily, string[]> = {
  LLCR: ["llcr", "cr", "low level contact resistance"],
  IR: ["ir", "insulation resistance"],
  DWV: ["dwv", "dielectric withstanding voltage"],
  MATING: ["mating", "un-mating", "mating/un-mating"],
};

const STEP_DESCRIPTION_FAMILY_LABELS: Record<StepDescriptionFamily, string> = {
  LLCR: "LLCR",
  IR: "IR",
  DWV: "DWV",
  MATING: "Mating/Un-mating",
};

function normalizeStepItemForMatch(text: string): string {
  return text.trim().toLowerCase().replace(/[^a-z0-9]+/g, " ");
}

function containsAliasToken(normalizedText: string, alias: string): boolean {
  const aliasNormalized = normalizeStepItemForMatch(alias);
  if (aliasNormalized.length === 0) {
    return false;
  }
  return ` ${normalizedText} `.includes(` ${aliasNormalized} `);
}

function detectStepDescriptionFamily(testItem: string): StepDescriptionFamily | null {
  const normalized = normalizeStepItemForMatch(testItem);
  if (normalized.length === 0) {
    return null;
  }
  if (STEP_DESCRIPTION_FAMILY_ALIASES.LLCR.some((alias) => containsAliasToken(normalized, alias))) {
    return "LLCR";
  }
  if (STEP_DESCRIPTION_FAMILY_ALIASES.IR.some((alias) => containsAliasToken(normalized, alias))) {
    return "IR";
  }
  if (STEP_DESCRIPTION_FAMILY_ALIASES.DWV.some((alias) => containsAliasToken(normalized, alias))) {
    return "DWV";
  }
  if (STEP_DESCRIPTION_FAMILY_ALIASES.MATING.some((alias) => containsAliasToken(normalized, alias))) {
    return "MATING";
  }
  return null;
}

function trySplitInitialAfterRequirement(rawRequirement: string): { initialPart: string; followPart: string } | null {
  const normalized = rawRequirement.replace(/\r?\n+/g, " ").trim();
  if (normalized.length === 0) {
    return null;
  }
  const initialMatch = normalized.match(/initial\b/i);
  if (!initialMatch) {
    return null;
  }
  const afterMarkerRegex = /\bafter(?:\s+test)?\b\s*:?/i;
  const afterMatch = afterMarkerRegex.exec(normalized);
  if (!afterMatch) {
    return null;
  }
  const initialStart = initialMatch.index ?? 0;
  const afterStart = afterMatch.index ?? -1;
  if (afterStart <= initialStart) {
    return null;
  }
  const initialPart = normalized.slice(initialStart, afterStart).trim().replace(/[;:\s]+$/g, "");
  const followPart = normalized.slice(afterStart + afterMatch[0].length).trim().replace(/^[;:\s]+/g, "");
  if (!/^initial\b/i.test(initialPart)) {
    return null;
  }
  if (followPart.length === 0) {
    return null;
  }
  return { initialPart, followPart };
}

function buildSelectedGroupStepPreviewRows(
  rows: EditableMatrixRow[],
  selectedGroup: GroupColumn | null,
  stepOutputOverrides: Record<string, StepOutputOverride>
): StepPreviewRow[] {
  if (!selectedGroup) {
    return [];
  }
  const baseRows = rows
    .flatMap((row, rowIndex) => {
      const parsed = parseStepTokens(row.groups[selectedGroup.id] ?? "");
      if (!parsed.isValid) {
        return [];
      }
      return parsed.numbers.map((stepNo) => {
        const token = parsed.tokens.find((item) => item.sequence === stepNo);
        const key = stepOutputKey(selectedGroup.id, stepNo, row.id);
        const override = stepOutputOverrides[key];
        const itemSectionMarker = row.section.match(/([*#]|\([a-zA-Z]\))/)?.[1] ?? row.item.match(/([*#]|\([a-zA-Z]\))/)?.[1] ?? null;
        const stepMarker = token?.suffixNote ?? token?.rawToken.match(/([*#]|\([a-zA-Z]\))/)?.[1] ?? null;
        return {
          key,
          stepNo,
          rawToken: token?.rawToken ?? `${stepNo}`,
          suffixNote: token?.suffixNote ?? null,
          rowId: row.id,
          sourceRequirement: row.requirement,
          sourceTestItem: row.item,
          sourceSection: row.section,
          sourceItemSectionNote: itemSectionMarker ? `Section: ${row.section}` : null,
          sourceStepNote: stepMarker ? `Step ${stepNo}${stepMarker}` : null,
          requirementValue: override?.requirement ?? row.requirement,
          descriptionValue: override?.description ?? row.item,
          rowIndex
        };
      });
    })
    .sort((left, right) => left.stepNo - right.stepNo || left.rowIndex - right.rowIndex);
  const dedupedBaseRows = baseRows.filter((row, index, allRows) => allRows.findIndex((candidate) => candidate.stepNo === row.stepNo) === index);

  const stepItemByNumber = new Map<number, string>();
  dedupedBaseRows.forEach((row) => {
    if (!stepItemByNumber.has(row.stepNo)) {
      stepItemByNumber.set(row.stepNo, row.sourceTestItem);
    }
  });

  const specialFamilyRowIndexes = new Map<StepDescriptionFamily, number[]>();
  dedupedBaseRows.forEach((row, index) => {
    const family = detectStepDescriptionFamily(row.sourceTestItem);
    if (!family) {
      return;
    }
    const indexes = specialFamilyRowIndexes.get(family);
    if (indexes) {
      indexes.push(index);
      return;
    }
    specialFamilyRowIndexes.set(family, [index]);
  });

  specialFamilyRowIndexes.forEach((indexes, family) => {
    const familyLabel = STEP_DESCRIPTION_FAMILY_LABELS[family];
    const splitByRowId = new Map<string, { initialPart: string; followPart: string }>();
    indexes.forEach((rowIndex) => {
      const row = dedupedBaseRows[rowIndex];
      const split = trySplitInitialAfterRequirement(row.sourceRequirement);
      if (split) {
        splitByRowId.set(row.rowId, split);
      }
    });
    if (indexes.length === 1) {
      const rowIndex = indexes[0];
      const row = dedupedBaseRows[rowIndex];
      if (!stepOutputOverrides[row.key]?.description) {
        row.descriptionValue = familyLabel;
      }
      if (!stepOutputOverrides[row.key]?.requirement) {
        const split = splitByRowId.get(row.rowId);
        if (split) {
          row.requirementValue = split.initialPart;
        }
      }
      return;
    }
    indexes.forEach((rowIndex, indexInFamily) => {
      const row = dedupedBaseRows[rowIndex];
      const split = splitByRowId.get(row.rowId);
      if (stepOutputOverrides[row.key]?.description) {
      } else if (indexInFamily === 0) {
        row.descriptionValue = `Initial ${familyLabel}`;
      } else if (indexInFamily === indexes.length - 1) {
        row.descriptionValue = `Final ${familyLabel}`;
      } else {
        const previousStepItem = stepItemByNumber.get(row.stepNo - 1)?.trim();
        row.descriptionValue =
          previousStepItem && previousStepItem.length > 0 ? `After ${previousStepItem}` : familyLabel;
      }
      if (stepOutputOverrides[row.key]?.requirement || !split) {
        return;
      }
      row.requirementValue = indexInFamily === 0 ? split.initialPart : split.followPart;
    });
  });

  return dedupedBaseRows.map(({ rowIndex: _rowIndex, ...row }) => row);
}

function extractMarkerKey(token: string | null | undefined): string | null {
  if (!token) {
    return null;
  }
  const markerMatch = token.match(/\(([a-zA-Z])\)|([*#])/);
  if (!markerMatch) {
    return null;
  }
  if (markerMatch[1]) {
    return markerMatch[1].toLowerCase();
  }
  return markerMatch[2] ?? null;
}

function buildPreviewStepNoteLookup(
  importPreview: MatrixPreviewResponse | null,
  selectedGroup: GroupColumn | null
): {
  byStepAndMarker: Map<string, PreviewStepNotePayload>;
  byStep: Map<number, PreviewStepNotePayload>;
  itemSectionByMarker: Map<string, string>;
  sampleNote: string | null;
} {
  const empty = {
    byStepAndMarker: new Map<string, PreviewStepNotePayload>(),
    byStep: new Map<number, PreviewStepNotePayload>(),
    itemSectionByMarker: new Map<string, string>(),
    sampleNote: null,
  };
  if (!importPreview || !selectedGroup) {
    return empty;
  }
  let groupIndex = -1;
  const groupIdMatch = selectedGroup.id.match(/^group-(\d+)$/i);
  if (groupIdMatch) {
    const value = Number(groupIdMatch[1]);
    if (Number.isInteger(value) && value > 0) {
      groupIndex = value - 1;
    }
  }
  let previewGroup = groupIndex >= 0 ? importPreview.groups[groupIndex] : undefined;
  if (!previewGroup) {
    previewGroup = importPreview.groups.find((group) => group.group_label === selectedGroup.name);
  }
  if (!previewGroup) {
    return empty;
  }
  const byStepAndMarker = new Map<string, PreviewStepNotePayload>();
  const byStep = new Map<number, PreviewStepNotePayload>();
  const itemSectionByMarker = new Map<string, string>();
  importPreview.groups.forEach((group) => {
    group.steps.forEach((step) => {
      const itemSectionNote = step.source_item_section_note ?? null;
      const sectionMarker = extractMarkerKey(step.source_section ?? null);
      if (itemSectionNote && sectionMarker && !itemSectionByMarker.has(sectionMarker)) {
        itemSectionByMarker.set(sectionMarker, itemSectionNote);
      }
    });
  });
  previewGroup.steps.forEach((step) => {
    const payload = {
      sourceNote: step.source_note ?? null,
      sourceItemSectionNote: step.source_item_section_note ?? null,
    };
    const marker = extractMarkerKey(step.raw_token) ?? extractMarkerKey(step.suffix_note ?? null);
    if (marker) {
      byStepAndMarker.set(`${step.sequence}|${marker}`, payload);
    }
    if (!byStep.has(step.sequence)) {
      byStep.set(step.sequence, payload);
    }
  });
  return { byStepAndMarker, byStep, itemSectionByMarker, sampleNote: previewGroup.sample_note ?? null };
}

function formatConciseItemSectionNote(stepNo: number, noteText: string): string {
  const normalized = noteText.replace(/\s+/g, " ").trim();
  if (normalized.length === 0) {
    return "";
  }
  const withoutTestItem = normalized.replace(/^Test Item:\s*[^|]+(?:\|\s*)?/i, "");
  const sectionMatch = withoutTestItem.match(/^Section:\s*(.+)$/i);
  if (!sectionMatch) {
    return `Step ${stepNo} | ${withoutTestItem}`;
  }
  const sectionPayload = sectionMatch[1].trim().replace(/([*#])\s+/g, "$1");
  return `Step ${stepNo} | Section:${sectionPayload}`;
}

function stripLeadingMarkerPrefix(noteText: string): string {
  return noteText
    .trim()
    .replace(/^\((?:\d*\s*)?[a-z]\)\s*/i, "")
    .replace(/^[*#]\s*/, "")
    .trim();
}

function replaceItemSectionNoteSection(noteText: string, sourceSection: string): string {
  const body = noteText
    .replace(/^Section:\s*[^*#()]+(?:[*#]|\((?:\d*\s*)?[a-z]\))?\s*/i, "")
    .trim();
  return body.length > 0 ? `Section: ${sourceSection} ${body}` : `Section: ${sourceSection}`;
}

function MatrixAutoGrowTextarea({
  ariaLabel,
  className,
  errorMessage,
  value,
  onFocus,
  onChange
}: MatrixAutoGrowTextareaProps): ReactElement {
  const ref = useRef<HTMLTextAreaElement | null>(null);

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) {
      return;
    }
    element.style.height = "auto";
    element.style.height = `${element.scrollHeight + 4}px`;
  }, [value]);

  return (
    <textarea
      ref={ref}
      aria-label={ariaLabel}
      className={className ? `matrix-editor-inline-textarea ${className}` : "matrix-editor-inline-textarea"}
      rows={1}
      title={errorMessage || undefined}
      value={value}
      onFocus={onFocus}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}

const TEMPLATE_CARDS = [
  { name: "EIA-364 Connector Template", summary: "20 items / 12 groups / 186 steps", tags: ["General"] },
  { name: "High Current Connector", summary: "18 items / 10 groups / 152 steps", tags: ["Power"] },
  { name: "General Qualification", summary: "16 items / 8 groups / 120 steps", tags: ["Qual"] }
];

const REFERENCE_ROWS = [
  { name: "EIA-364-23E LLCR method", type: "Method", source: "EIA-364", updated: "2024-12-01" },
  { name: "EIA-364-21F insulation method", type: "Method", source: "EIA-364", updated: "2024-11-20" },
  { name: "20mV max, 100mA max condition", type: "Condition", source: "EIA-364-23E", updated: "2024-10-15" },
  { name: "Initial <= 0.40mO", type: "Requirement", source: "Customer spec", updated: "2025-01-10" }
];

export function MatrixEditorWorkspace({
  projectId,
  onBackToWorkbench
}: MatrixEditorWorkspaceProps): ReactElement {
  const model = useProjectRuntimeConsoleModel(projectId);
  const [editableRows, setEditableRows] = useState<EditableMatrixRow[]>(() => buildInitialMatrixRows());
  const [groupColumns, setGroupColumns] = useState<GroupColumn[]>(() => buildInitialGroupColumns());
  const [selectedRowId, setSelectedRowId] = useState<string | null>(null);
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [, setLastMessage] = useState<string>("");
  const [undoStack, setUndoStack] = useState<MatrixSnapshot[]>([]);
  const [contextMenu, setContextMenu] = useState<MatrixContextMenu | null>(null);
  const [stepOutputOverrides, setStepOutputOverrides] = useState<Record<string, StepOutputOverride>>({});
  const [sampleValues, setSampleValues] = useState<Record<string, string>>({ "group-1": "" });
  const [sampleMergeNotes, setSampleMergeNotes] = useState<Record<string, string>>({});
  const [importPreview, setImportPreview] = useState<MatrixPreviewResponse | null>(null);
  const [importPreviewPdfToken, setImportPreviewPdfToken] = useState<string | null>(null);
  const [importingPreview, setImportingPreview] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [importLookupMessage, setImportLookupMessage] = useState<string>("");
  const [importLookupTone, setImportLookupTone] = useState<"success" | "error" | "idle">("idle");
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showImportSelectionMode, setShowImportSelectionMode] = useState(false);
  const [groupSelectionKeys, setGroupSelectionKeys] = useState<string[]>([]);
  const [groupSelectionStatus, setGroupSelectionStatus] = useState("");
  const [groupSelectionViewModel, setGroupSelectionViewModel] = useState<MatrixImportSelectionViewModel | null>(null);
  const [committingImport, setCommittingImport] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [locatorPage, setLocatorPage] = useState("");
  const [locatorTableOnPage, setLocatorTableOnPage] = useState("");
  const [locatorKeyword, setLocatorKeyword] = useState("");
  const [hasPersistedDraft, setHasPersistedDraft] = useState(false);
  const [projectMatrixDraftId, setProjectMatrixDraftId] = useState<string | null>(null);
  const [, setProjectMatrixDraftUpdatedAt] = useState<string | null>(null);
  const [projectMatrixDraftBaseConfirmedMatrixId, setProjectMatrixDraftBaseConfirmedMatrixId] = useState<string | null>(null);
  const [draftLoading, setDraftLoading] = useState(false);
  const [saveState, setSaveState] = useState<MatrixSaveState>("idle");
  const [saveBaselineSignature, setSaveBaselineSignature] = useState<string | null>(null);
  const [confirmActiveState, setConfirmActiveState] = useState<MatrixPublishState>("idle");
  const [confirmActiveMessage, setConfirmActiveMessage] = useState<string>("");
  const [activeAuthorityConfirmed, setActiveAuthorityConfirmed] = useState(false);
  const [activeAuthorityBaselineSignature, setActiveAuthorityBaselineSignature] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const autoSaveTimerRef = useRef<number | null>(null);
  const hasRuntimeAuthorityAvailable = Boolean(model.runtimeAuthoritySync.authorityVersion);

  const applyDraftSnapshotToEditor = (draft: ProjectMatrixDraft): void => {
    const mapped = buildMatrixFromProjectMatrixDraft(draft);
    const nextGroups = mapped.groups.length > 0 ? mapped.groups : buildInitialGroupColumns();
    const nextRows = mapped.rows.length > 0 ? mapped.rows : buildInitialMatrixRows();
    const nextSamples = mapped.samples;
    setGroupColumns(nextGroups);
    setEditableRows(nextRows);
    setSampleValues(nextSamples);
    setSampleMergeNotes({});
    setSelectedGroupId(nextGroups[0]?.id ?? null);
    setSelectedRowId(null);
    setProjectMatrixDraftId(draft.record.project_matrix_draft_id);
    setProjectMatrixDraftUpdatedAt(draft.record.updated_at);
    setProjectMatrixDraftBaseConfirmedMatrixId(draft.record.base_confirmed_matrix_id ?? null);
    const baselinePayload = buildDraftSavePayload(nextRows, nextGroups, nextSamples);
    setSaveBaselineSignature(JSON.stringify(baselinePayload));
    setSaveState("saved");
    setActiveAuthorityConfirmed(false);
    setConfirmActiveState("idle");
    setConfirmActiveMessage("");
  };

  const resolveActiveAuthorityBaselineSignature = async (
    input: {
      fallbackDraft?: ProjectMatrixDraft | null;
      allowDraftFallback: boolean;
    }
  ): Promise<string | null> => {
    try {
      const snapshot = await fetchActiveConfirmedMatrixSnapshot(projectId);
      return buildAuthorityComparableSignatureFromConfirmedSnapshot(snapshot);
    } catch (error) {
      if (input.allowDraftFallback && input.fallbackDraft) {
        return buildAuthorityComparableSignatureFromDraft(input.fallbackDraft);
      }
      return null;
    }
  };

  useEffect(() => {
    let cancelled = false;
    const loadDraft = async (): Promise<void> => {
      setDraftLoading(true);
      try {
        const summaries = await listProjectMatrixDrafts(projectId);
        if (cancelled) {
          return;
        }
        if (summaries.length === 0) {
          setHasPersistedDraft(false);
          setProjectMatrixDraftId(null);
          setProjectMatrixDraftUpdatedAt(null);
          setProjectMatrixDraftBaseConfirmedMatrixId(null);
          setSaveBaselineSignature(null);
          setActiveAuthorityBaselineSignature(null);
          setSaveState("idle");
          return;
        }
        setHasPersistedDraft(true);
        const targetId = summaries[0].project_matrix_draft_id;
        const draft = await getProjectMatrixDraft(projectId, targetId);
        if (cancelled) {
          return;
        }
        applyDraftSnapshotToEditor(draft);
        const shouldResolveAuthorityBaseline =
          Boolean(draft.record.base_confirmed_matrix_id) ||
          hasRuntimeAuthorityAvailable;
        if (!shouldResolveAuthorityBaseline) {
          setActiveAuthorityBaselineSignature(null);
          return;
        }
        const baselineSignature = await resolveActiveAuthorityBaselineSignature({
          allowDraftFallback: false,
        });
        if (cancelled) {
          return;
        }
        setActiveAuthorityBaselineSignature(baselineSignature);
      } catch (error) {
        if (cancelled) {
          return;
        }
        setHasPersistedDraft(false);
        setProjectMatrixDraftId(null);
        setProjectMatrixDraftBaseConfirmedMatrixId(null);
        setActiveAuthorityBaselineSignature(null);
        setSaveState("error");
      } finally {
        if (!cancelled) {
          setDraftLoading(false);
        }
      }
    };
    void loadDraft();
    return () => {
      cancelled = true;
    };
  }, [projectId, hasRuntimeAuthorityAvailable]);

  useLayoutEffect(() => {
    setSampleValues((previous) => {
      const next: Record<string, string> = {};
      groupColumns.forEach((group) => {
        next[group.id] = previous[group.id] ?? "";
      });
      return next;
    });
    setSampleMergeNotes((previous) => {
      const next: Record<string, string> = {};
      groupColumns.forEach((group) => {
        if (previous[group.id]) {
          next[group.id] = previous[group.id];
        }
      });
      return next;
    });
  }, [groupColumns]);

  const projectLabel = model.project?.product_name ?? "Connector Project";
  const ltr = model.latestLtr ?? `Temporary project ${projectId.slice(0, 8)}`;
  const testDescription = model.matrixAuthorityDraft?.source_document_name?.trim()
    ? model.matrixAuthorityDraft.source_document_name.trim()
    : "Test description unavailable";
  const matrixEditorIdentityLine = `${ltr} | ${projectLabel} | ${testDescription}`;
  const projectionRef = model.runtimeAuthoritySync.projectionMatrixReference ?? "not loaded";
  const normalizedNameMap = new Map<string, string[]>();
  const emptyGroupIds = new Set<string>();
  groupColumns.forEach((group) => {
    const normalized = normalizeGroupName(group.name);
    if (normalized === "") {
      emptyGroupIds.add(group.id);
      return;
    }
    const existing = normalizedNameMap.get(normalized);
    if (existing) {
      existing.push(group.id);
      return;
    }
    normalizedNameMap.set(normalized, [group.id]);
  });
  const duplicateGroupIds = new Set<string>();
  const duplicateNames: string[] = [];
  normalizedNameMap.forEach((groupIds, normalizedName) => {
    if (groupIds.length <= 1) {
      return;
    }
    groupIds.forEach((groupId) => duplicateGroupIds.add(groupId));
    duplicateNames.push(normalizedName.toUpperCase());
  });
  const hasGroupNameError = emptyGroupIds.size > 0 || duplicateGroupIds.size > 0;
  const groupNameErrorMessage =
    duplicateNames.length > 0
      ? `Group names duplicated: ${duplicateNames.join(", ")}`
      : emptyGroupIds.size > 0
        ? "Group name is required"
        : "";
  const invalidStepFormatCellKeys = new Set<string>();
  const stepCellErrorMessageByKey = new Map<string, string>();
  const groupStepSequenceErrorIds = new Set<string>();
  const groupStepSequenceErrorCellKeys = new Set<string>();
  const groupStepSequenceErrorMessageById = new Map<string, string>();
  groupColumns.forEach((group) => {
    const validNonEmptyCellKeys: string[] = [];
    const groupNumbers: number[] = [];
    editableRows.forEach((row, rowIndex) => {
      const value = row.groups[group.id] ?? "";
      const parsed = parseStepTokens(value);
      const cellKey = `${group.id}-${rowIndex}`;
      if (!parsed.isValid) {
        invalidStepFormatCellKeys.add(cellKey);
        stepCellErrorMessageByKey.set(cellKey, parsed.errorMessage);
        return;
      }
      if (parsed.numbers.length === 0) {
        return;
      }
      validNonEmptyCellKeys.push(cellKey);
      groupNumbers.push(...parsed.numbers);
    });
    if (groupNumbers.length === 0) {
      return;
    }
    const sortedNumbers = [...groupNumbers].sort((a, b) => a - b);
    const hasDuplicate = sortedNumbers.some((value, index) => index > 0 && value === sortedNumbers[index - 1]);
    const uniqueSortedNumbers = [...new Set(sortedNumbers)];
    const startsFromOne = uniqueSortedNumbers[0] === 1;
    const hasGap = uniqueSortedNumbers.some((value, index) => index > 0 && value !== uniqueSortedNumbers[index - 1] + 1);
    if (!startsFromOne || hasGap || hasDuplicate) {
      const duplicates = sortedNumbers.filter((value, index) => index > 0 && value === sortedNumbers[index - 1]);
      const duplicateSet = [...new Set(duplicates)];
      const max = uniqueSortedNumbers[uniqueSortedNumbers.length - 1];
      const expected = new Set<number>();
      for (let value = 1; value <= max; value += 1) {
        expected.add(value);
      }
      uniqueSortedNumbers.forEach((value) => expected.delete(value));
      const missing = [...expected];
      const detailParts: string[] = [];
      if (!startsFromOne) {
        detailParts.push("must start at 1");
      }
      if (missing.length > 0) {
        detailParts.push(`missing: ${missing.join(",")}`);
      }
      if (duplicateSet.length > 0) {
        detailParts.push(`duplicates: ${duplicateSet.join(",")}`);
      }
      const groupDisplay = group.name.trim() || "(unnamed group)";
      const detailText = detailParts.join("; ");
      const sequenceErrorMessage = `${groupDisplay} sequence error: ${detailText}`;
      groupStepSequenceErrorIds.add(group.id);
      validNonEmptyCellKeys.forEach((cellKey) => groupStepSequenceErrorCellKeys.add(cellKey));
      groupStepSequenceErrorMessageById.set(group.id, sequenceErrorMessage);
      validNonEmptyCellKeys.forEach((cellKey) => {
        if (!stepCellErrorMessageByKey.has(cellKey)) {
          stepCellErrorMessageByKey.set(cellKey, sequenceErrorMessage);
        }
      });
    }
  });
  const hasStepTokenError = invalidStepFormatCellKeys.size > 0 || groupStepSequenceErrorIds.size > 0;
  const hasMatrixValidationError = hasGroupNameError || hasStepTokenError;
  const firstStepCellError = [...stepCellErrorMessageByKey.values()][0] ?? "";
  const stepTokenErrorMessage = hasStepTokenError ? firstStepCellError : "";
  const selectedGroup = groupColumns.find((group) => group.id === selectedGroupId) ?? null;
  const selectedGroupStepRows = buildSelectedGroupStepPreviewRows(
    editableRows,
    selectedGroup,
    stepOutputOverrides
  );
  const selectedGroupPreviewNotes = buildPreviewStepNoteLookup(importPreview, selectedGroup);
  const selectedGroupSamplesValue = selectedGroup ? sampleValues[selectedGroup.id] ?? "" : "";
  const selectedGroupStepNotes = selectedGroupStepRows
    .map((row) => {
      const marker = extractMarkerKey(row.rawToken) ?? extractMarkerKey(row.suffixNote);
      const mapped = marker
        ? selectedGroupPreviewNotes.byStepAndMarker.get(`${row.stepNo}|${marker}`) ?? null
        : selectedGroupPreviewNotes.byStep.get(row.stepNo) ?? null;
      const rawNote = mapped?.sourceNote ?? row.sourceStepNote;
      if (!rawNote) {
        return null;
      }
      const body = stripLeadingMarkerPrefix(rawNote);
      return body.length > 0 ? `${row.rawToken} ${body}` : row.rawToken;
    })
    .filter((note): note is string => Boolean(note));
  const dedupedSelectedGroupStepNotes = [...new Set(selectedGroupStepNotes)];
  const selectedGroupItemSectionNotes = selectedGroupStepRows
    .map((row) => {
      const marker = extractMarkerKey(row.rawToken) ?? extractMarkerKey(row.suffixNote);
      const mapped = marker
        ? selectedGroupPreviewNotes.byStepAndMarker.get(`${row.stepNo}|${marker}`) ?? null
        : selectedGroupPreviewNotes.byStep.get(row.stepNo) ?? null;
      const markerNote = marker ? selectedGroupPreviewNotes.itemSectionByMarker.get(marker) ?? null : null;
      const rawNote = mapped?.sourceItemSectionNote ?? (markerNote ? replaceItemSectionNoteSection(markerNote, row.sourceSection) : row.sourceItemSectionNote);
      if (!rawNote) {
        return null;
      }
      const concise = formatConciseItemSectionNote(row.stepNo, rawNote);
      return concise.length > 0 ? concise : null;
    })
    .filter((note): note is string => Boolean(note));
  const sampleMarker = selectedGroupSamplesValue.match(/\(([a-zA-Z])\)|([*#])/);
  const selectedGroupSampleMergeNote = selectedGroup ? sampleMergeNotes[selectedGroup.id] ?? null : null;
  const selectedGroupSampleNotes = [
    selectedGroupPreviewNotes.sampleNote ?? (sampleMarker ? `${sampleMarker[0]}` : null),
    selectedGroupSampleMergeNote,
  ].filter((note): note is string => Boolean(note));
  const currentSavePayload = buildDraftSavePayload(
    editableRows,
    groupColumns,
    sampleValues
  );
  const currentSaveSignature = JSON.stringify(currentSavePayload);
  const hasUnsavedChanges =
    saveBaselineSignature !== null && currentSaveSignature !== saveBaselineSignature;
  const hasAnyStepTokenValue = currentSavePayload.cells.some(
    (cell) => (cell.cell_value ?? "").trim().length > 0
  );
  const hasProjectId = projectId.trim().length > 0;
  const hasActiveAuthorityFromWorkbench = hasRuntimeAuthorityAvailable;
  const isPublishBusy = confirmActiveState === "loading";
  const hasNoAuthorityChanges =
    activeAuthorityBaselineSignature !== null &&
    buildAuthorityComparableSignatureFromDraftPayload(currentSavePayload) ===
      activeAuthorityBaselineSignature;
  const publishDisabledReason =
    !hasProjectId
      ? "No project id."
      : hasMatrixValidationError
        ? groupNameErrorMessage || stepTokenErrorMessage
        : saveState === "saving" || isPublishBusy
          ? "Action in progress."
          : !projectMatrixDraftId &&
            !hasActiveAuthorityFromWorkbench &&
            !hasAnyStepTokenValue
            ? "Add at least one step token before first confirm."
            : hasNoAuthorityChanges
              ? "No Matrix changes to publish."
              : "";
  const canPublishActiveMatrix = publishDisabledReason.length === 0;
  const saveStatusLabel =
    !hasPersistedDraft || projectMatrixDraftId === null
      ? "No persisted draft target."
      : saveState === "error"
        ? AUTO_SAVE_STATUS_COPY.error
        : hasUnsavedChanges || saveState === "dirty"
        ? AUTO_SAVE_STATUS_COPY.dirty
        : AUTO_SAVE_STATUS_COPY[saveState];
  const canAutoSave =
    hasPersistedDraft &&
    projectMatrixDraftId !== null &&
    hasUnsavedChanges &&
    !hasMatrixValidationError &&
    saveState === "dirty" &&
    !isPublishBusy;

  useEffect(() => {
    if (autoSaveTimerRef.current !== null) {
      window.clearTimeout(autoSaveTimerRef.current);
      autoSaveTimerRef.current = null;
    }
    if (!canAutoSave || !projectMatrixDraftId) {
      return;
    }
    autoSaveTimerRef.current = window.setTimeout(() => {
      autoSaveTimerRef.current = null;
      setSaveState("saving");
      void saveProjectMatrixDraft(projectId, projectMatrixDraftId, currentSavePayload)
        .then((saved) => {
          setHasPersistedDraft(true);
          applyDraftSnapshotToEditor(saved);
          setSaveState("saved");
        })
        .catch((error: unknown) => {
          console.error("Matrix draft auto-save failed.", error);
          setSaveState("error");
        });
    }, AUTO_SAVE_DEBOUNCE_MS);
    return () => {
      if (autoSaveTimerRef.current !== null) {
        window.clearTimeout(autoSaveTimerRef.current);
        autoSaveTimerRef.current = null;
      }
    };
  }, [canAutoSave, currentSavePayload, currentSaveSignature, projectId, projectMatrixDraftId]);

  const openChooseDocx = (): void => {
    fileInputRef.current?.click();
  };

  const onChangeSourceMatrix = (): void => {
    if (hasPersistedDraft) {
      const warning = hasUnsavedChanges
        ? "Change Source Matrix will replace the current source session. Unsaved edits will be lost. Continue?"
        : "Change Source Matrix will replace the current source session. Continue?";
      if (!window.confirm(warning)) {
        return;
      }
    }
    openChooseDocx();
  };

  const markUnsaved = (): void => {
    setActiveAuthorityConfirmed(false);
    if (saveState !== "saving") {
      setSaveState("dirty");
    }
  };

  const buildDraftSelectionViewModel = (): MatrixImportSelectionViewModel | null => {
    if (groupColumns.length === 0) {
      return null;
    }
    const groups = groupColumns.map((group, index) => ({
      groupKey: group.groupKey || `group_${index + 1}`,
      groupLabel: group.name.trim().length > 0 ? group.name.trim() : `Group ${index + 1}`,
      sampleQuantityExpression: sampleValues[group.id] || null,
      sampleNote: group.sampleNote,
      stepCount: null,
    }));
    const rows = editableRows
      .filter((row) => !row.isSampleRow)
      .map((row, rowIndex) => {
        const tokensByGroupKey: Record<string, string> = {};
        groupColumns.forEach((group, groupIndex) => {
          tokensByGroupKey[groups[groupIndex].groupKey] = row.groups[group.id] ?? "";
        });
        return {
          rowId: row.id || `draft-selection-row-${rowIndex + 1}`,
          testItem: row.item || `Row ${rowIndex + 1}`,
          tokensByGroupKey,
        };
      });
    return {
      sourceDocumentName: "Current persisted draft",
      groups,
      rows,
    };
  };

  const resolveGroupSelectionViewModel = (): MatrixImportSelectionViewModel | null => {
    const previewModel = buildMatrixImportSelectionViewModel(importPreview);
    if (previewModel && previewModel.groups.length > 0) {
      return previewModel;
    }
    return buildDraftSelectionViewModel();
  };

  const openGroupSelection = (): void => {
    const selectionViewModel = buildMatrixImportSelectionViewModel(importPreview);
    setGroupSelectionKeys(buildDefaultSelectedGroupKeys(selectionViewModel?.groups ?? []));
    setGroupSelectionViewModel(selectionViewModel);
    if (!selectionViewModel || selectionViewModel.groups.length === 0) {
      setGroupSelectionStatus("No valid Matrix was found from reparse. Continue with manual group setup from default editor.");
    } else {
      setGroupSelectionStatus("");
    }
    setShowImportDialog(false);
    setShowImportSelectionMode(true);
  };

  const onToggleGroupSelection = (groupKey: string): void => {
    setGroupSelectionKeys((previous) => (
      previous.includes(groupKey)
        ? previous.filter((item) => item !== groupKey)
        : [...previous, groupKey]
    ));
  };

  const onCancelGroupSelection = (): void => {
    setShowImportSelectionMode(false);
    setGroupSelectionStatus("");
    setGroupSelectionViewModel(null);
    setCommittingImport(false);
  };

  const clearImportSession = (): void => {
    setImportFile(null);
    setImportPreview(null);
    setImportPreviewPdfToken(null);
    setLocatorPage("");
    setLocatorTableOnPage("");
    setLocatorKeyword("");
    setImportError(null);
    setImportLookupMessage("");
    setImportLookupTone("idle");
    setGroupSelectionKeys([]);
    setGroupSelectionStatus("");
    setGroupSelectionViewModel(null);
    setCommittingImport(false);
    setShowImportDialog(false);
    setShowImportSelectionMode(false);
  };

  const onBackToMatrixCandidateSelection = (): void => {
    setShowImportSelectionMode(false);
    setShowImportDialog(true);
    setGroupSelectionStatus("");
    setGroupSelectionViewModel(null);
    setCommittingImport(false);
  };

  const onChangeSelectedGroups = (): void => {
    const selectionViewModel = resolveGroupSelectionViewModel();
    if (!selectionViewModel || selectionViewModel.groups.length === 0) {
      setGroupSelectionStatus("No group selection source is available. Import source matrix or build draft groups first.");
      return;
    }
    const availableGroupKeys = selectionViewModel.groups.map((group) => group.groupKey);
    const previewModel = buildMatrixImportSelectionViewModel(importPreview);
    if (!previewModel || previewModel.groups.length === 0) {
      const currentlySelected = groupColumns
        .filter((group) => group.isSelected)
        .map((group) => group.groupKey)
        .filter((groupKey) => availableGroupKeys.includes(groupKey));
      setGroupSelectionKeys(currentlySelected.length > 0 ? currentlySelected : availableGroupKeys);
    } else {
      setGroupSelectionKeys((previous) =>
        preserveSelectedGroupKeys({
          availableGroupKeys,
          previousSelectedGroupKeys: previous,
        })
      );
    }
    setGroupSelectionViewModel(selectionViewModel);
    setGroupSelectionStatus("");
    setShowImportDialog(false);
    setShowImportSelectionMode(true);
  };

  const onCommitImportedGroups = async (): Promise<void> => {
    if (groupSelectionKeys.length === 0) {
      setGroupSelectionStatus("Select at least one group.");
      return;
    }
    const selectionFromPreview = buildMatrixImportSelectionViewModel(importPreview);
    if (!selectionFromPreview || selectionFromPreview.groups.length === 0) {
      const selectedSet = new Set(groupSelectionKeys);
      markUnsaved();
      setGroupColumns((previous) =>
        previous.map((group) => ({
          ...group,
          isSelected: selectedSet.has(group.groupKey),
        }))
      );
      setShowImportSelectionMode(false);
      setGroupSelectionStatus("");
      setGroupSelectionViewModel(null);
      return;
    }
    setCommittingImport(true);
    setGroupSelectionStatus("");
    try {
      const response: MatrixImportCommitResponse = await commitMatrixImport(projectId, {
        source_document_path: importPreview!.source_document_path,
        source_document_name: importPreview!.source_document_name,
        source_format: importPreview!.source_format,
        preview_payload: importPreview!,
        selected_group_keys: groupSelectionKeys,
      });
      applyDraftSnapshotToEditor(response.project_matrix_draft);
      setHasPersistedDraft(true);
      setSaveState("saved");
      setShowImportSelectionMode(false);
      setGroupSelectionKeys(response.selected_group_keys_committed);
      setGroupSelectionStatus("");
      setGroupSelectionViewModel(null);
      setImportError(null);
    } catch (error) {
      setGroupSelectionStatus(parseRequestError(error, "Failed to create project draft from selected groups."));
    } finally {
      setCommittingImport(false);
    }
  };

  const onImportFileChange = async (event: ChangeEvent<HTMLInputElement>): Promise<void> => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) {
      return;
    }
    setImportFile(file);
    setLocatorPage("");
    setLocatorTableOnPage("");
    setLocatorKeyword("");
    setImportError(null);
    setImportLookupMessage("");
    setImportLookupTone("idle");
    setImportPreview(null);
    setGroupSelectionViewModel(null);
    setImportPreviewPdfToken(null);
    setImportingPreview(true);
    try {
      const preview = await previewProjectTestPlanMatrixFromUpload(file, projectId);
      setImportPreview(preview);
      setImportPreviewPdfToken(preview.preview_pdf_token ?? null);
      setLocatorPage(preview.selected_page_number != null ? String(preview.selected_page_number) : "");
      setLocatorTableOnPage(preview.selected_page_table_index != null ? String(preview.selected_page_table_index) : "");
      setLocatorKeyword("");
      setShowImportDialog(true);
      if (preview.blockers.length > 0) {
        setImportError(preview.blockers[0]);
        setImportLookupMessage("No matching matrix found. Adjust page/table and reparse.");
        setImportLookupTone("error");
      } else if (preview.groups.length === 0) {
        setImportError("No matching matrix found.");
        setImportLookupMessage("No matching matrix found. You can reparse or continue to manual group setup.");
        setImportLookupTone("error");
      } else {
        setImportError(null);
        setImportLookupMessage(`Matrix found: ${preview.groups.length} groups detected.`);
        setImportLookupTone("success");
      }
    } catch (error) {
      setImportPreview(null);
      setImportPreviewPdfToken(null);
      setImportError(error instanceof Error ? error.message : "Import preview failed.");
      setImportLookupMessage("No matching matrix found. Adjust page/table and reparse.");
      setImportLookupTone("error");
    } finally {
      setImportingPreview(false);
    }
  };

  const reparseImportPreview = async (): Promise<void> => {
    if (!importFile) {
      return;
    }
    const requestedPageNumber = parsePositiveInteger(locatorPage);
    const requestedTableIndex = parsePositiveInteger(locatorTableOnPage);
    if (locatorPage.trim() && requestedPageNumber === null) {
      setImportError("Page must be a positive integer.");
      setImportLookupMessage("No matching matrix found. Adjust page/table and reparse.");
      setImportLookupTone("error");
      setImportPreview(null);
      return;
    }
    if (locatorTableOnPage.trim() && requestedTableIndex === null) {
      setImportError("Table on page must be a positive integer.");
      setImportLookupMessage("No matching matrix found. Adjust page/table and reparse.");
      setImportLookupTone("error");
      setImportPreview(null);
      return;
    }
    setImportingPreview(true);
    setImportError(null);
    setImportLookupMessage("");
    setImportLookupTone("idle");
    setImportPreview(null);
    setGroupSelectionViewModel(null);
    try {
      const preview = await previewProjectTestPlanMatrixFromUpload(importFile, projectId, {
        pageNumber: requestedPageNumber,
        pageTableIndex: requestedTableIndex,
        tableTextQuery: locatorKeyword.trim() || null,
      });
      if (preview.preview_pdf_token) {
        setImportPreviewPdfToken(preview.preview_pdf_token);
      }
      const pageMismatch = requestedPageNumber != null && preview.selected_page_number !== requestedPageNumber;
      const tableMismatch = requestedTableIndex != null && preview.selected_page_table_index !== requestedTableIndex;
      if (pageMismatch || tableMismatch) {
        setImportPreview(null);
        setImportError("Requested page/table did not match a matrix.");
        setImportLookupMessage("No matching matrix found at requested page/table. Reparse or edit manually.");
        setImportLookupTone("error");
        return;
      }
      setImportPreview(preview);
      if (preview.blockers.length > 0) {
        setImportError(preview.blockers[0]);
        setImportLookupMessage("No matching matrix found. Adjust page/table and reparse.");
        setImportLookupTone("error");
      } else if (preview.groups.length === 0) {
        setImportError("No matching matrix found.");
        setImportLookupMessage("No matching matrix found. You can reparse or continue to manual group setup.");
        setImportLookupTone("error");
      } else {
        setImportLookupMessage(`Matrix found: ${preview.groups.length} groups detected.`);
        setImportLookupTone("success");
      }
    } catch (error) {
      setImportPreview(null);
      setImportError(error instanceof Error ? error.message : "Reparse failed.");
      setImportLookupMessage("No matching matrix found. Adjust page/table and reparse.");
      setImportLookupTone("error");
    } finally {
      setImportingPreview(false);
    }
  };

  const importPreviewPageNumber = Number.parseInt(locatorPage.trim(), 10);
  const previewOpenPage = Number.isFinite(importPreviewPageNumber) && importPreviewPageNumber > 0 ? importPreviewPageNumber : 1;
  const previewPdfSrc = importPreviewPdfToken
    ? `${matrixPreviewPdfUrl(importPreviewPdfToken)}#page=${previewOpenPage}&zoom=page-width&pagemode=thumbs`
    : null;
  const draftSelectionViewModel = buildDraftSelectionViewModel();
  const importSelectionViewModel =
    groupSelectionViewModel ?? buildMatrixImportSelectionViewModel(importPreview) ?? draftSelectionViewModel;
  const hasLiveSelectionPreview = Boolean(importPreview && buildMatrixImportSelectionViewModel(importPreview));
  const importSessionActionState = buildMatrixImportSessionActionState(
    importPreview,
    Boolean(draftSelectionViewModel && draftSelectionViewModel.groups.length > 0)
  );
  const groupSelectionDisabledReason = buildMatrixImportSelectionDisabledReason({
    groups: importSelectionViewModel?.groups ?? [],
    selectedGroupKeys: groupSelectionKeys,
    committing: committingImport,
    importError: hasLiveSelectionPreview ? importError : null,
  });

  if ((!model.project && !model.error) || draftLoading) {
    return <LoadingState label="Loading matrix editor..." />;
  }

  const pushSnapshot = (): void => {
    setUndoStack((previous) => [
      ...previous,
      {
        rows: cloneRows(editableRows),
        groups: cloneGroups(groupColumns)
      }
    ]);
  };

  const getSelectedRowIndex = (): number => editableRows.findIndex((row) => row.id === selectedRowId);

  const updateTextField = (
    rowIndex: number,
    field: keyof Omit<EditableMatrixRow, "groups" | "id">,
    value: string
  ): void => {
    markUnsaved();
    setEditableRows((previous) =>
      previous.map((row, index) => (index === rowIndex ? { ...row, [field]: value } : row))
    );
  };

  const updateGroupField = (rowIndex: number, groupId: string, value: string): void => {
    markUnsaved();
    setEditableRows((previous) =>
      previous.map((row, index) =>
        index === rowIndex
          ? {
              ...row,
              groups: {
                ...row.groups,
                [groupId]: value
              }
            }
          : row
      )
    );
  };

  const updateGroupName = (groupId: string, name: string): void => {
    markUnsaved();
    setGroupColumns((previous) =>
      previous.map((group) => (group.id === groupId ? { ...group, name } : group))
    );
  };

  const updateStepOutputOverride = (
    key: string,
    field: keyof StepOutputOverride,
    value: string
  ): void => {
    setStepOutputOverrides((previous) => ({
      ...previous,
      [key]: {
        ...previous[key],
        [field]: value
      }
    }));
  };

  const addRow = (): void => {
    markUnsaved();
    pushSnapshot();
    setEditableRows((previous) => [...previous, buildEmptyRow(groupColumns.map((group) => group.id), previous.length)]);
    setLastMessage("Test item row added");
  };

  const insertRow = (rowIndex: number, direction: "above" | "below"): void => {
    markUnsaved();
    pushSnapshot();
    const insertAt = direction === "above" ? rowIndex : rowIndex + 1;
    setEditableRows((previous) => {
      const next = [...previous];
      next.splice(insertAt, 0, buildEmptyRow(groupColumns.map((group) => group.id), insertAt));
      return next;
    });
    setLastMessage(direction === "above" ? "Row inserted above" : "Row inserted below");
  };

  const duplicateRow = (rowIndex: number): void => {
    markUnsaved();
    pushSnapshot();
    setEditableRows((previous) => {
      const next = [...previous];
      const source = previous[rowIndex];
      const duplicated: EditableMatrixRow = {
        ...source,
        id: `matrix-row-copy-${Date.now()}-${rowIndex}`,
        draftRowId: null,
        sourceRowSnapshotId: null,
        groups: { ...source.groups }
      };
      next.splice(rowIndex + 1, 0, duplicated);
      return next;
    });
    setLastMessage("Row duplicated");
  };

  const deleteRow = (rowIndex: number): void => {
    if (editableRows.length <= 1) {
      setLastMessage("At least one test item row is required");
      return;
    }
    markUnsaved();
    pushSnapshot();
    const deletingId = editableRows[rowIndex].id;
    setEditableRows((previous) => previous.filter((row) => row.id !== deletingId));
    setSelectedRowId((previous) => (previous === deletingId ? null : previous));
    setLastMessage("Row deleted");
  };

  const moveRow = (rowIndex: number, direction: "up" | "down"): void => {
    if (direction === "up" && rowIndex === 0) {
      setLastMessage("First row cannot move up");
      return;
    }
    if (direction === "down" && rowIndex === editableRows.length - 1) {
      setLastMessage("Last row cannot move down");
      return;
    }
    markUnsaved();
    pushSnapshot();
    setEditableRows((previous) => {
      const next = [...previous];
      const target = direction === "up" ? rowIndex - 1 : rowIndex + 1;
      const [row] = next.splice(rowIndex, 1);
      next.splice(target, 0, row);
      return next;
    });
    setLastMessage(direction === "up" ? "Row moved up" : "Row moved down");
  };

  const addGroup = (): void => {
    markUnsaved();
    pushSnapshot();
    const nextId = nextGroupId(groupColumns);
    setGroupColumns((previous) => [
      ...previous,
      {
        id: nextId,
        name: "",
        draftGroupId: null,
        sourceGroupSnapshotId: null,
        groupKey: `g${previous.length + 1}`,
        isSelected: true,
        sampleNote: null,
      },
    ]);
    setEditableRows((previous) =>
      previous.map((row) => ({
        ...row,
        groups: {
          ...row.groups,
          [nextId]: ""
        }
      }))
    );
    setLastMessage("Group column added");
  };

  const insertGroup = (groupId: string, direction: "left" | "right"): void => {
    const currentIndex = groupColumns.findIndex((group) => group.id === groupId);
    if (currentIndex < 0) {
      return;
    }
    markUnsaved();
    pushSnapshot();
    const nextId = nextGroupId(groupColumns);
    const insertAt = direction === "left" ? currentIndex : currentIndex + 1;
    setGroupColumns((previous) => {
      const next = [...previous];
      next.splice(insertAt, 0, {
        id: nextId,
        name: "",
        draftGroupId: null,
        sourceGroupSnapshotId: null,
        groupKey: `g${insertAt + 1}`,
        isSelected: true,
        sampleNote: null,
      });
      return next;
    });
    setEditableRows((previous) =>
      previous.map((row) => ({
        ...row,
        groups: {
          ...row.groups,
          [nextId]: ""
        }
      }))
    );
    setLastMessage("Group column inserted");
  };

  const duplicateGroup = (groupId: string): void => {
    const currentIndex = groupColumns.findIndex((group) => group.id === groupId);
    if (currentIndex < 0) {
      return;
    }
    markUnsaved();
    pushSnapshot();
      const sourceGroup = groupColumns[currentIndex];
      const nextId = nextGroupId(groupColumns);
      setGroupColumns((previous) => {
        const next = [...previous];
      next.splice(currentIndex + 1, 0, {
        id: nextId,
        name: sourceGroup.name,
        draftGroupId: null,
        sourceGroupSnapshotId: null,
        groupKey: sourceGroup.groupKey,
        isSelected: sourceGroup.isSelected,
        sampleNote: sourceGroup.sampleNote,
      });
        return next;
      });
    setEditableRows((previous) =>
      previous.map((row) => ({
        ...row,
        groups: {
          ...row.groups,
          [nextId]: row.groups[groupId]
        }
      }))
    );
    setLastMessage("Group column duplicated");
  };

  const deleteGroup = (groupId: string): void => {
    if (groupColumns.length <= 1) {
      setLastMessage("At least one group column is required");
      return;
    }
    markUnsaved();
    pushSnapshot();
    setGroupColumns((previous) => previous.filter((group) => group.id !== groupId));
    setEditableRows((previous) =>
      previous.map((row) => {
        const groups = { ...row.groups };
        delete groups[groupId];
        return { ...row, groups };
      })
    );
    setSelectedGroupId((previous) => (previous === groupId ? null : previous));
    setLastMessage("Group column deleted");
  };

  const moveGroup = (groupId: string, direction: "left" | "right"): void => {
    const currentIndex = groupColumns.findIndex((group) => group.id === groupId);
    if (currentIndex < 0) {
      return;
    }
    if (direction === "left" && currentIndex === 0) {
      setLastMessage("First group cannot move left");
      return;
    }
    if (direction === "right" && currentIndex === groupColumns.length - 1) {
      setLastMessage("Last group cannot move right");
      return;
    }
    markUnsaved();
    pushSnapshot();
    setGroupColumns((previous) => {
      const next = [...previous];
      const target = direction === "left" ? currentIndex - 1 : currentIndex + 1;
      const [item] = next.splice(currentIndex, 1);
      next.splice(target, 0, item);
      return next;
    });
    setLastMessage(direction === "left" ? "Group column moved left" : "Group column moved right");
  };

  const undoLast = (): void => {
    setUndoStack((previous) => {
      if (previous.length === 0) {
        setLastMessage("Nothing to undo");
        return previous;
      }
      const snapshot = previous[previous.length - 1];
      setEditableRows(cloneRows(snapshot.rows));
      setGroupColumns(cloneGroups(snapshot.groups));
      setSelectedRowId(null);
      setSelectedGroupId(null);
      setLastMessage("Last structural action reverted");
      return previous.slice(0, -1);
    });
  };

  const openRowContextMenu = (event: MouseEvent, rowIndex: number): void => {
    event.preventDefault();
    setSelectedRowId(editableRows[rowIndex].id);
    setSelectedGroupId(null);
    setContextMenu({ kind: "row", rowIndex, x: event.clientX, y: event.clientY });
  };

  const openGroupContextMenu = (event: MouseEvent, groupId: string): void => {
    event.preventDefault();
    setSelectedGroupId(groupId);
    setSelectedRowId(null);
    setContextMenu({ kind: "group", groupId, x: event.clientX, y: event.clientY });
  };

  const runContextAction = (action: () => void): void => {
    action();
    setContextMenu(null);
  };

  const selectRow = (rowId: string): void => {
    setSelectedRowId(rowId);
    setSelectedGroupId(null);
    setContextMenu(null);
  };

  const selectGroup = (groupId: string): void => {
    setSelectedGroupId(groupId);
    setSelectedRowId(null);
    setContextMenu(null);
  };

  const ensureEditableDraft = async (): Promise<ProjectMatrixDraft | null> => {
    if (projectMatrixDraftId) {
      return null;
    }
    if (!hasProjectId) {
      return null;
    }
    if (hasActiveAuthorityFromWorkbench) {
      const draft = await createMatrixRevisionDraft(projectId);
      setHasPersistedDraft(true);
      applyDraftSnapshotToEditor(draft);
      const baselineSignature = await resolveActiveAuthorityBaselineSignature({
        fallbackDraft: draft,
        allowDraftFallback: true,
      });
      setActiveAuthorityBaselineSignature(baselineSignature);
      setSaveState("saved");
      return draft;
    }
    const selectedGroupKeys = currentSavePayload.groups
      .filter((group) => group.is_selected)
      .map((group) => group.group_key.trim())
      .filter((groupKey) => groupKey.length > 0);
    const groupKeysForCommit =
      selectedGroupKeys.length > 0
        ? selectedGroupKeys
        : currentSavePayload.groups
            .map((group) => group.group_key.trim())
            .filter((groupKey) => groupKey.length > 0);
    if (groupKeysForCommit.length === 0) {
      throw new Error("At least one selected group is required before first confirm.");
    }
    const previewPayload = buildManualPreviewPayloadFromDraftPayload(currentSavePayload);
    const commitResponse: MatrixImportCommitResponse = await commitMatrixImport(projectId, {
      source_document_path: previewPayload.source_document_path,
      source_document_name: previewPayload.source_document_name,
      source_format: previewPayload.source_format,
      preview_payload: previewPayload,
      selected_group_keys: groupKeysForCommit,
    });
    const draft = commitResponse.project_matrix_draft;
    setHasPersistedDraft(true);
    applyDraftSnapshotToEditor(draft);
    setActiveAuthorityBaselineSignature(null);
    setSaveState("saved");
    return draft;
  };

  const saveCurrentDraftNow = async (
    draftIdOverride?: string | null,
    options?: { force?: boolean }
  ): Promise<ProjectMatrixDraft | null> => {
    const targetDraftId = draftIdOverride ?? projectMatrixDraftId;
    const force = options?.force ?? false;
    if (!projectId.trim() || !targetDraftId) {
      return null;
    }
    if (autoSaveTimerRef.current !== null) {
      window.clearTimeout(autoSaveTimerRef.current);
      autoSaveTimerRef.current = null;
    }
    if (!force && saveState !== "dirty" && !hasUnsavedChanges && saveState !== "error") {
      return null;
    }
    setSaveState("saving");
    const saved = await saveProjectMatrixDraft(projectId, targetDraftId, currentSavePayload);
    setHasPersistedDraft(true);
    applyDraftSnapshotToEditor(saved);
    setSaveState("saved");
    return saved;
  };

  const onConfirmAsActiveMatrix = async (): Promise<void> => {
    if (!canPublishActiveMatrix) {
      if (publishDisabledReason) {
        setConfirmActiveMessage(publishDisabledReason);
      }
      return;
    }
    setConfirmActiveState("loading");
    setConfirmActiveMessage("Confirming active matrix...");
    try {
      const ensuredDraft = await ensureEditableDraft();
      const targetDraftId = ensuredDraft?.record.project_matrix_draft_id ?? projectMatrixDraftId;
      if (!targetDraftId) {
        setConfirmActiveState("error");
        setConfirmActiveMessage("No persisted matrix draft target.");
        return;
      }

      let authorityComparableSignatureAfterSave =
        buildAuthorityComparableSignatureFromDraftPayload(currentSavePayload);
      let savedDraft: ProjectMatrixDraft | null = null;
      try {
        const requiresInitialDraftSync = Boolean(
          ensuredDraft &&
          !hasActiveAuthorityFromWorkbench &&
          projectMatrixDraftId === null
        );
        savedDraft = await saveCurrentDraftNow(targetDraftId, {
          force: requiresInitialDraftSync,
        });
      } catch (error) {
        setSaveState("error");
        setConfirmActiveState("error");
        setConfirmActiveMessage(
          parseRequestError(error, "Save failed. Confirm was not published.")
        );
        return;
      }
      if (savedDraft) {
        authorityComparableSignatureAfterSave =
          buildAuthorityComparableSignatureFromDraft(savedDraft);
      } else if (ensuredDraft) {
        authorityComparableSignatureAfterSave =
          buildAuthorityComparableSignatureFromDraft(ensuredDraft);
      }
      const authorityBaselineSignature =
        activeAuthorityBaselineSignature ??
        (ensuredDraft?.record.base_confirmed_matrix_id
          ? buildAuthorityComparableSignatureFromDraft(ensuredDraft)
          : null);
      if (
        authorityBaselineSignature !== null &&
        authorityComparableSignatureAfterSave === authorityBaselineSignature
      ) {
        setConfirmActiveState("error");
        setConfirmActiveMessage("No Matrix changes to publish.");
        return;
      }

      const publishMode: MatrixPublishMode =
        (savedDraft?.record.base_confirmed_matrix_id ??
          ensuredDraft?.record.base_confirmed_matrix_id ??
          projectMatrixDraftBaseConfirmedMatrixId)
          ? "revision_authority"
          : "first_authority";
      const confirmed =
        publishMode === "revision_authority"
          ? await confirmProjectMatrixRevisionDraft(projectId, targetDraftId, {
              confirmed_by: MVP_REVISION_CONFIRMED_BY,
            })
          : await confirmProjectMatrixDraft(projectId, targetDraftId, {
              confirmed_by: MVP_REVISION_CONFIRMED_BY,
            });
      setConfirmActiveState("success");
      setActiveAuthorityConfirmed(true);
      setConfirmActiveMessage(
        publishMode === "revision_authority"
          ? buildRevisionConfirmedMessage(confirmed)
          : buildActiveMatrixConfirmedMessage(confirmed)
      );
      onBackToWorkbench();
    } catch (error) {
      setConfirmActiveState("error");
      setConfirmActiveMessage(parseRequestError(error, "Confirm failed."));
    }
  };

  return (
    <section className="workbench-page matrix-editor-shell matrix-editor-target-shell" onClick={() => setContextMenu(null)}>
      <section className="matrix-editor-target-header">
        <div className="matrix-editor-target-title matrix-editor-target-title-compact">
          <button className="matrix-editor-link-button" type="button" onClick={onBackToWorkbench}>
            Back to Workbench
          </button>
          <h2>Matrix Editor</h2>
          <p className="matrix-editor-project-identity" title={matrixEditorIdentityLine}>
            {matrixEditorIdentityLine}
          </p>
        </div>
        <section className="matrix-editor-save-status">{saveStatusLabel}</section>
        {showImportSelectionMode ? (
          <div className="matrix-editor-target-actions">
            <span className="matrix-editor-selection-mode-pill">Import selection in progress</span>
          </div>
        ) : null}
      </section>

      {confirmActiveMessage && (
        <section className="matrix-editor-save-status">
          {confirmActiveMessage}
        </section>
      )}

      <section className="matrix-editor-actionbar">
        <div className="matrix-editor-actionbar-main">
          {importFile ? <span className="matrix-editor-import-file-name" title={importFile.name}>{importFile.name}</span> : null}
          <button type="button" onClick={undoLast} disabled={undoStack.length === 0 || showImportSelectionMode}>Undo</button>
          {!showImportSelectionMode ? (
            <MatrixWorkspaceActionGroups
              changeSelectedGroupsDisabled={importSessionActionState.changeSelectedGroupsDisabled}
              changeSelectedGroupsDisabledReason={importSessionActionState.changeSelectedGroupsDisabledReason}
              publishDisabled={!canPublishActiveMatrix}
              publishDisabledReason={publishDisabledReason}
              publishBusy={confirmActiveState === "loading"}
              onChangeSelectedGroups={onChangeSelectedGroups}
              onChangeSourceMatrix={() => void onChangeSourceMatrix()}
              onPublishActiveMatrix={() => void onConfirmAsActiveMatrix()}
            />
          ) : null}
          <button
            type="button"
            className="matrix-editor-import-secondary-button"
            disabled
            title="Append Matrix requires multi-source lineage and is not active in this task."
          >
            Append Matrix (Future)
          </button>
          <input
            ref={fileInputRef}
            accept=".docx"
            style={{ display: "none" }}
            type="file"
            onChange={(event) => void onImportFileChange(event)}
          />
        </div>
      </section>
      {showImportDialog ? (
        <section className="matrix-editor-import-modal-backdrop">
          <article className="matrix-editor-import-modal" onClick={(event) => event.stopPropagation()}>
            <header>
              <div className="matrix-editor-import-header-inline">
                <h3>Import Matrix</h3>
                <p title={importPreview?.source_document_name ?? importFile?.name ?? "Selected file"}>
                  {importPreview?.source_document_name ?? importFile?.name ?? "Selected file"}
                </p>
              </div>
            </header>
            <div className="matrix-editor-import-modal-body">
              <div className="matrix-editor-import-pdf-pane">
                {previewPdfSrc ? (
                  <iframe title="Word PDF Preview" src={previewPdfSrc} />
                ) : (
                  <div className="matrix-editor-step-empty">PDF preview unavailable.</div>
                )}
              </div>
              <div className="matrix-editor-import-controls-pane">
                <div className="matrix-editor-import-controls-row">
                  <label>
                    <span>Page</span>
                    <input value={locatorPage} onChange={(event) => setLocatorPage(event.target.value)} />
                  </label>
                  <label>
                    <span>Table on page</span>
                    <input value={locatorTableOnPage} onChange={(event) => setLocatorTableOnPage(event.target.value)} />
                  </label>
                </div>
                <label>
                  <span>Table Title / Content Keyword</span>
                  <input value={locatorKeyword} onChange={(event) => setLocatorKeyword(event.target.value)} />
                </label>
                <button className="matrix-editor-import-reparse-button" type="button" onClick={() => void reparseImportPreview()} disabled={importingPreview || !importFile}>
                  {importingPreview ? "Reparsing..." : "Reparse"}
                </button>
                {importingPreview ? <p>Reparsing...</p> : null}
                {importLookupMessage ? (
                  <p className={importLookupTone === "success" ? "matrix-editor-import-status-success" : importLookupTone === "error" ? "matrix-editor-import-status-error" : ""}>
                    {importLookupMessage}
                  </p>
                ) : null}
                {importError ? <p className="error">{importError}</p> : null}
                <footer className="matrix-editor-import-controls-footer">
                  <button className="matrix-editor-import-secondary-button" type="button" onClick={() => setShowImportDialog(false)}>Cancel</button>
                  <button
                    className="matrix-editor-import-commit-button"
                    type="button"
                    disabled={importingPreview}
                    onClick={() => {
                      openGroupSelection();
                    }}
                  >
                    Replace
                  </button>
                  <button
                    className="matrix-editor-import-commit-button"
                    type="button"
                    disabled={importingPreview}
                    onClick={() => {
                      openGroupSelection();
                    }}
                  >
                    Append
                  </button>
                </footer>
              </div>
            </div>
          </article>
        </section>
      ) : null}
      {showImportSelectionMode ? (
        importSelectionViewModel && importSelectionViewModel.groups.length > 0 ? (
          <MatrixImportSelectionMode
            viewModel={importSelectionViewModel}
            selectedGroupKeys={groupSelectionKeys}
            disabledReason={groupSelectionDisabledReason}
            statusMessage={groupSelectionStatus}
            onToggleGroup={onToggleGroupSelection}
            onBackToCandidateSelection={onBackToMatrixCandidateSelection}
            onCancel={onCancelGroupSelection}
            onCancelSession={clearImportSession}
            onConfirm={() => void onCommitImportedGroups()}
          />
        ) : (
          <section className="matrix-editor-selection-mode" aria-label="Matrix import selection mode">
            <header className="matrix-editor-selection-mode-header">
              <div className="matrix-editor-selection-mode-meta">
                <h3>Import Selection Mode</h3>
                <p>No valid matrix found from reparse.</p>
              </div>
              <div className="matrix-editor-selection-mode-actions">
                <button type="button" className="matrix-editor-import-secondary-button" onClick={onBackToMatrixCandidateSelection}>
                  Back to matrix candidate selection
                </button>
                <button type="button" className="matrix-editor-import-secondary-button" onClick={onCancelGroupSelection}>
                  Back to editor
                </button>
                <button type="button" className="matrix-editor-import-secondary-button" onClick={clearImportSession}>
                  Cancel import session
                </button>
              </div>
            </header>
            <p className="matrix-editor-group-selection-status" aria-live="polite">
              No matrix detected. Continue from default editor and add groups manually.
            </p>
          </section>
        )
      ) : null}

      {!showImportSelectionMode ? (
        <section className="matrix-editor-studio">
        <section className="matrix-editor-grid-surface">
          <div className="matrix-editor-main-table-wrap">
            <table className="matrix-editor-main-table">
              <thead>
                <tr>
                  <th className="matrix-editor-row-selector-head">No.</th>
                  <th>Test Item</th>
                  <th>Section</th>
                  <th>Method</th>
                  <th>Condition</th>
                  <th>Requirement</th>
                  {groupColumns.map((group) => (
                    <th
                      className={`matrix-editor-group-band${selectedGroupId === group.id ? " matrix-editor-group-selected" : ""}`}
                      key={group.id}
                      onClick={() => selectGroup(group.id)}
                      onContextMenu={(event) => openGroupContextMenu(event, group.id)}
                    >
                      <input
                        className={`matrix-editor-group-name-input${group.name.trim() === "" ? " is-empty" : ""}${duplicateGroupIds.has(group.id) ? " is-duplicate" : ""}`}
                        type="text"
                        value={group.name}
                        onClick={(event) => {
                          event.stopPropagation();
                          setSelectedGroupId(group.id);
                          setSelectedRowId(null);
                          setContextMenu(null);
                        }}
                        onFocus={() => {
                          setSelectedGroupId(group.id);
                          setSelectedRowId(null);
                          setContextMenu(null);
                        }}
                        onChange={(event) => updateGroupName(group.id, event.target.value)}
                      />
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {editableRows.map((row, rowIndex) => (
                  (() => {
                    const rowHasNoGroupSteps = groupColumns.every((group) => (row.groups[group.id] ?? "").trim() === "");
                    return (
                      <tr
                        className={selectedRowId === row.id ? "matrix-editor-row-selected" : undefined}
                        key={row.id}
                      >
                        <td className="matrix-editor-row-selector-cell">
                          <button
                            type="button"
                            className={`matrix-editor-row-selector-button${rowHasNoGroupSteps ? " is-step-missing" : ""}`}
                            aria-label={`Select row ${rowIndex + 1}`}
                            title={rowHasNoGroupSteps ? "Missing step number" : undefined}
                            onClick={() => selectRow(row.id)}
                            onContextMenu={(event) => openRowContextMenu(event, rowIndex)}
                          >
                            {rowIndex + 1}
                          </button>
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} test item`}
                            className={row.item.trim() === "" ? "is-empty-required" : undefined}
                            value={row.item}
                            onChange={(value) => updateTextField(rowIndex, "item", value)}
                          />
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} section`}
                            value={row.section}
                            onChange={(value) => updateTextField(rowIndex, "section", value)}
                          />
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} method`}
                            className={row.method.trim() === "" ? "is-empty-required" : undefined}
                            value={row.method}
                            onChange={(value) => updateTextField(rowIndex, "method", value)}
                          />
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} condition`}
                            className={row.condition.trim() === "" ? "is-empty-required" : undefined}
                            value={row.condition}
                            onChange={(value) => updateTextField(rowIndex, "condition", value)}
                          />
                        </td>
                        <td>
                          <MatrixAutoGrowTextarea
                            ariaLabel={`Row ${rowIndex + 1} requirement`}
                            className={row.requirement.trim() === "" ? "is-empty-required" : undefined}
                            value={row.requirement}
                            onChange={(value) => updateTextField(rowIndex, "requirement", value)}
                          />
                        </td>
                        {groupColumns.map((group) => {
                          const cellKey = `${group.id}-${rowIndex}`;
                          const cellErrorMessage = stepCellErrorMessageByKey.get(cellKey) ?? "";
                          const groupCellClass = `matrix-editor-inline-input${
                            invalidStepFormatCellKeys.has(cellKey) || groupStepSequenceErrorCellKeys.has(cellKey)
                              ? " is-invalid"
                                : ""
                          }`;
                          return (
                            <td
                              className={selectedGroupId === group.id ? "matrix-editor-group-selected-cell" : undefined}
                              key={`${group.id}-${rowIndex}`}
                            >
                              <MatrixAutoGrowTextarea
                                ariaLabel={`Row ${rowIndex + 1} ${group.name || "Group"}`}
                                className={groupCellClass}
                                errorMessage={cellErrorMessage}
                                value={row.groups[group.id] ?? ""}
                                onFocus={() => {
                                  setSelectedGroupId(group.id);
                                  setSelectedRowId(null);
                                  setContextMenu(null);
                                }}
                                onChange={(value) => {
                                  markUnsaved();
                                  setSelectedGroupId(group.id);
                                  updateGroupField(rowIndex, group.id, value);
                                }}
                              />
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })()
                ))}
                <tr>
                  <td />
                  <td className="matrix-editor-sample-label-cell">Samples Quantity (PCS)</td>
                  <td />
                  <td />
                  <td />
                  <td />
                  {groupColumns.map((group) => (
                    <td key={`sample-${group.id}`}>
                      <MatrixAutoGrowTextarea
                        ariaLabel={`Samples ${group.name || "group"}`}
                        className="matrix-editor-sample-textarea"
                        value={sampleValues[group.id] ?? ""}
                        onFocus={() => {
                          setSelectedGroupId(group.id);
                          setSelectedRowId(null);
                          setContextMenu(null);
                        }}
                        onChange={(value) => {
                          markUnsaved();
                          setSampleValues((previous) => ({ ...previous, [group.id]: value }));
                          setSampleMergeNotes((previous) => {
                            const { [group.id]: _removed, ...next } = previous;
                            return next;
                          });
                        }}
                      />
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
            {contextMenu ? (
              <div
                className="matrix-editor-context-menu"
                style={{ left: contextMenu.x, top: contextMenu.y }}
                onClick={(event) => event.stopPropagation()}
              >
                {contextMenu.kind === "row" ? (
                  <>
                    <button type="button" onClick={() => runContextAction(() => insertRow(contextMenu.rowIndex, "above"))}>Insert above</button>
                    <button type="button" onClick={() => runContextAction(() => insertRow(contextMenu.rowIndex, "below"))}>Insert below</button>
                    <button type="button" onClick={() => runContextAction(() => duplicateRow(contextMenu.rowIndex))}>Duplicate row</button>
                    <button
                      type="button"
                      disabled={contextMenu.rowIndex === 0}
                      title={contextMenu.rowIndex === 0 ? "First row cannot move up" : ""}
                      onClick={() => runContextAction(() => moveRow(contextMenu.rowIndex, "up"))}
                    >
                      Move up
                    </button>
                    <button
                      type="button"
                      disabled={contextMenu.rowIndex === editableRows.length - 1}
                      title={contextMenu.rowIndex === editableRows.length - 1 ? "Last row cannot move down" : ""}
                      onClick={() => runContextAction(() => moveRow(contextMenu.rowIndex, "down"))}
                    >
                      Move down
                    </button>
                    <button
                      type="button"
                      disabled={editableRows.length <= 1}
                      title={editableRows.length <= 1 ? "At least one test item row is required" : ""}
                      onClick={() => runContextAction(() => deleteRow(contextMenu.rowIndex))}
                    >
                      Delete row
                    </button>
                  </>
                ) : (
                  <>
                    <button type="button" onClick={() => runContextAction(() => insertGroup(contextMenu.groupId, "left"))}>Insert left</button>
                    <button type="button" onClick={() => runContextAction(() => insertGroup(contextMenu.groupId, "right"))}>Insert right</button>
                    <button
                      type="button"
                      onClick={() => runContextAction(() => duplicateGroup(contextMenu.groupId))}
                    >
                      Duplicate group
                    </button>
                    <button
                      type="button"
                      disabled={groupColumns.findIndex((group) => group.id === contextMenu.groupId) === 0}
                      title={groupColumns.findIndex((group) => group.id === contextMenu.groupId) === 0 ? "First group cannot move left" : ""}
                      onClick={() => runContextAction(() => moveGroup(contextMenu.groupId, "left"))}
                    >
                      Move left
                    </button>
                    <button
                      type="button"
                      disabled={groupColumns.findIndex((group) => group.id === contextMenu.groupId) === groupColumns.length - 1}
                      title={groupColumns.findIndex((group) => group.id === contextMenu.groupId) === groupColumns.length - 1 ? "Last group cannot move right" : ""}
                      onClick={() => runContextAction(() => moveGroup(contextMenu.groupId, "right"))}
                    >
                      Move right
                    </button>
                    <button
                      type="button"
                      disabled={groupColumns.length <= 1}
                      title={groupColumns.length <= 1 ? "At least one group column is required" : ""}
                      onClick={() => runContextAction(() => deleteGroup(contextMenu.groupId))}
                    >
                      Delete group
                    </button>
                  </>
                )}
              </div>
            ) : null}
          </div>
        </section>

        <aside className="matrix-editor-step-workspace" aria-label="Group Step Workspace">
          <header className="matrix-editor-step-header">
            <h3 className="matrix-editor-step-header-text">
              {`Group ${selectedGroup ? selectedGroup.name || "Unnamed" : "-"}: ${selectedGroupStepRows.length} steps`}
            </h3>
          </header>
          {!selectedGroup ? (
            <div className="matrix-editor-step-empty">Select a group header to preview steps.</div>
          ) : selectedGroupStepRows.length === 0 ? (
            <div className="matrix-editor-step-empty">No steps in this group.</div>
          ) : (
            <>
              <table className="matrix-editor-step-output-table">
                <thead>
                  <tr>
                    <th>Step</th>
                    <th>Requirement</th>
                    <th>Step Description</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedGroupStepRows.map((row) => (
                    <tr key={row.key}>
                      <td>{row.stepNo}</td>
                      <td>
                        <MatrixAutoGrowTextarea
                          ariaLabel={`Step ${row.stepNo} requirement`}
                          className="matrix-editor-step-output-textarea"
                          value={row.requirementValue}
                          onChange={(value) => updateStepOutputOverride(row.key, "requirement", value)}
                        />
                      </td>
                      <td>
                        <MatrixAutoGrowTextarea
                          ariaLabel={`Step ${row.stepNo} description`}
                          className="matrix-editor-step-output-textarea"
                          value={row.descriptionValue}
                          onChange={(value) => updateStepOutputOverride(row.key, "description", value)}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {selectedGroupStepNotes.length > 0 ? (
                <section className="matrix-editor-notes-card matrix-editor-notes-card-step">
                  <h4>Step Notes</h4>
                  {dedupedSelectedGroupStepNotes.map((note, index) => <p key={`${note}-${index}`}>{note}</p>)}
                </section>
              ) : null}
              {selectedGroupItemSectionNotes.length > 0 ? (
                <section className="matrix-editor-notes-card matrix-editor-notes-card-item-section">
                  <h4>Item/Section Notes</h4>
                  {selectedGroupItemSectionNotes.map((note, index) => <p key={`${note}-${index}`}>{note}</p>)}
                </section>
              ) : null}
              <section className="matrix-editor-notes-card matrix-editor-notes-card-samples">
                <div className="matrix-editor-samples-inline">
                  <h4>Samples</h4>
                  <input
                    className="matrix-editor-inline-input matrix-editor-samples-inline-input"
                    value={selectedGroupSamplesValue}
                    onChange={(event) => {
                      if (!selectedGroup) {
                        return;
                      }
                      markUnsaved();
                      const value = event.target.value;
                      setSampleValues((previous) => ({ ...previous, [selectedGroup.id]: value }));
                      setSampleMergeNotes((previous) => {
                        const { [selectedGroup.id]: _removed, ...next } = previous;
                        return next;
                      });
                    }}
                  />
                </div>
                {selectedGroupSampleNotes.length > 0 ? (
                  <>
                    <h5>Notes</h5>
                    {selectedGroupSampleNotes.map((note, index) => <p key={`${note}-${index}`}>{note}</p>)}
                  </>
                ) : null}
              </section>
            </>
          )}
        </aside>
      </section>
      ) : null}

      {!showImportSelectionMode ? (
      <section className="matrix-editor-supporting">
        <section className="matrix-editor-templates" aria-label="Templates">
          <header>
            <h3>Templates</h3>
            <button disabled type="button">More templates</button>
          </header>
          <input placeholder="Search templates..." type="text" />
          <div className="matrix-editor-template-grid">
            {TEMPLATE_CARDS.map((card) => (
              <article key={card.name}>
                <h4>{card.name}</h4>
                <p>{card.summary}</p>
                <div>
                  {card.tags.map((tag) => (
                    <span key={tag}>{tag}</span>
                  ))}
                </div>
                <footer>
                  <button disabled type="button">Preview</button>
                  <button disabled type="button">Use</button>
                </footer>
              </article>
            ))}
            <article className="matrix-editor-template-create">
              <h4>Create custom template</h4>
            </article>
          </div>
        </section>

        <section className="matrix-editor-reference-library" aria-label="Reference Library">
          <header>
            <h3>Reference Library</h3>
            <button disabled type="button">More references</button>
          </header>
          <nav>
            {["Method standards", "Conditions", "Requirements", "Spec clauses"].map((tab, index) => (
              <button className={index === 0 ? "is-active" : ""} disabled key={tab} type="button">
                {tab}
              </button>
            ))}
          </nav>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Source</th>
                <th>Updated</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {REFERENCE_ROWS.map((row) => (
                <tr key={row.name}>
                  <td>{row.name}</td>
                  <td>{row.type}</td>
                  <td>{row.source}</td>
                  <td>{row.updated}</td>
                  <td>
                    <button disabled type="button">Use</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="matrix-editor-projection-note">
            Projection Ref: {projectionRef}
          </p>
        </section>
      </section>
      ) : null}
    </section>
  );
}


