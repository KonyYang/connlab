import { useLayoutEffect, useRef, useState, type MouseEvent, type ReactElement } from "react";
import { LoadingState } from "../../components/common/LoadingState";
import { useProjectRuntimeConsoleModel } from "../project-workbench/useProjectRuntimeConsoleModel";
import "../../workbench.css";

type MatrixEditorWorkspaceProps = {
  projectId: string;
  onBackToWorkbench: () => void;
};

const HEADER_METRICS = [
  { label: "Groups", value: "1" },
  { label: "Steps", value: "1" },
  { label: "Items", value: "2" }
];

type GroupColumn = {
  id: string;
  name: string;
};

type EditableMatrixRow = {
  id: string;
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

type StepOutputOverride = {
  requirement?: string;
  description?: string;
};

type StepPreviewRow = {
  key: string;
  stepNo: number;
  rowId: string;
  sourceRequirement: string;
  sourceTestItem: string;
  requirementValue: string;
  descriptionValue: string;
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
      item: "Visual Examination",
      section: "",
      method: "EIA-364-18B",
      condition: "10x min magnification",
      requirement: "No detrimental condition",
      groups: { "group-1": "1" }
    },
    {
      id: "matrix-row-1",
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
    item: "",
    section: "",
    method: "",
    condition: "",
    requirement: "",
    groups: groupValues
  };
}

function buildInitialGroupColumns(): GroupColumn[] {
  return [{ id: "group-1", name: "1" }];
}

function cloneGroups(groups: GroupColumn[]): GroupColumn[] {
  return groups.map((group) => ({ ...group }));
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

function parseStepTokens(rawValue: string): { isValid: boolean; numbers: number[]; errorMessage: string } {
  const normalized = rawValue.trim();
  if (normalized === "") {
    return { isValid: true, numbers: [], errorMessage: "" };
  }
  if (!/^\d+(,\d+)*$/.test(normalized)) {
    const invalidCharacters = Array.from(
      new Set(
        normalized
          .split("")
          .filter((char) => !/[0-9,]/.test(char))
      )
    );
    const invalidCharsText =
      invalidCharacters.length > 0 ? ` Invalid characters: ${invalidCharacters.join(" ")}` : "";
    return {
      isValid: false,
      numbers: [],
      errorMessage: `Only digits and commas are allowed (example: 1,2,3).${invalidCharsText}`,
    };
  }
  return {
    isValid: true,
    numbers: normalized.split(",").map((token) => Number(token)),
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
        const key = stepOutputKey(selectedGroup.id, stepNo, row.id);
        const override = stepOutputOverrides[key];
        return {
          key,
          stepNo,
          rowId: row.id,
          sourceRequirement: row.requirement,
          sourceTestItem: row.item,
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

  if (!model.project && !model.error) {
    return <LoadingState label="Loading matrix editor..." />;
  }

  const projectLabel = model.project?.product_name ?? "Connector Project";
  const ltr = model.latestLtr ?? "Not registered";
  const bu = model.project?.business_unit || "Not set";
  const requester = model.project?.requestor || "Not set";
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
    setEditableRows((previous) =>
      previous.map((row, index) => (index === rowIndex ? { ...row, [field]: value } : row))
    );
  };

  const updateGroupField = (rowIndex: number, groupId: string, value: string): void => {
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
    pushSnapshot();
    setEditableRows((previous) => [...previous, buildEmptyRow(groupColumns.map((group) => group.id), previous.length)]);
    setLastMessage("Test item row added");
  };

  const insertRow = (rowIndex: number, direction: "above" | "below"): void => {
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
    pushSnapshot();
    setEditableRows((previous) => {
      const next = [...previous];
      const source = previous[rowIndex];
      const duplicated: EditableMatrixRow = {
        ...source,
        id: `matrix-row-copy-${Date.now()}-${rowIndex}`,
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
    pushSnapshot();
    const nextId = nextGroupId(groupColumns);
    setGroupColumns((previous) => [...previous, { id: nextId, name: "" }]);
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
    pushSnapshot();
    const nextId = nextGroupId(groupColumns);
    const insertAt = direction === "left" ? currentIndex : currentIndex + 1;
    setGroupColumns((previous) => {
      const next = [...previous];
      next.splice(insertAt, 0, { id: nextId, name: "" });
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
    pushSnapshot();
    const sourceGroup = groupColumns[currentIndex];
    const nextId = nextGroupId(groupColumns);
    setGroupColumns((previous) => {
      const next = [...previous];
      next.splice(currentIndex + 1, 0, { id: nextId, name: sourceGroup.name });
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

  return (
    <section className="workbench-page matrix-editor-shell matrix-editor-target-shell" onClick={() => setContextMenu(null)}>
      <section className="matrix-editor-target-header">
        <div className="matrix-editor-target-title">
          <button className="matrix-editor-link-button" type="button" onClick={onBackToWorkbench}>
            Back to Workbench
          </button>
          <h2>Matrix Editor</h2>
          <p>Definition Studio</p>
        </div>
        <div className="matrix-editor-target-project">
          <strong>{projectLabel}</strong>
          <span>LTR Registered</span>
          <p>LTR: {ltr}</p>
          <p>BU: {bu}</p>
          <p>Requester: {requester}</p>
        </div>
        <div className="matrix-editor-target-metrics">
          {HEADER_METRICS.map((metric) => (
            <article key={metric.label}>
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </article>
          ))}
        </div>
        <div className="matrix-editor-target-actions">
          <button disabled type="button">Save</button>
          <button
            className="matrix-editor-primary-action"
            disabled
            title={hasMatrixValidationError ? groupNameErrorMessage || stepTokenErrorMessage : ""}
            type="button"
          >
            Publish for approval
          </button>
          <button disabled type="button">More</button>
        </div>
      </section>

      <section className="matrix-editor-actionbar">
        <div className="matrix-editor-actionbar-main">
          <button type="button" onClick={addRow}>Add test item</button>
          <button
            type="button"
            onClick={addGroup}
          >
            Add group
          </button>
          <button type="button" onClick={undoLast} disabled={undoStack.length === 0}>Undo</button>
        </div>
        <div className="matrix-editor-actionbar-side">
          <button disabled type="button">Display options</button>
          <button disabled type="button">Filter</button>
          <input placeholder="Search conditions/items..." type="text" />
        </div>
      </section>

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
          <header>
            <p>{selectedGroup ? selectedGroup.name || "Unnamed group" : "No group selected"}</p>
            <h3>Step preview</h3>
          </header>
          <div className="matrix-editor-step-meta">
            <span>{selectedGroupStepRows.length} steps</span>
            <em>{selectedGroup ? "Selected group" : "Select group"}</em>
          </div>
          {!selectedGroup ? (
            <div className="matrix-editor-step-empty">Select a group header to preview steps.</div>
          ) : selectedGroupStepRows.length === 0 ? (
            <div className="matrix-editor-step-empty">No steps in this group.</div>
          ) : (
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
          )}
        </aside>
      </section>

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
    </section>
  );
}


