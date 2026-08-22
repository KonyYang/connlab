import type { MatrixPreviewResponse } from "../../api/client";
import {
  normalizeGroupDisplayName,
  type EditableMatrixRow,
  type GroupColumn,
} from "./matrixEditorDraftModel";

export type StepOutputOverride = {
  requirement?: string;
  description?: string;
};

export type StepPreviewRow = {
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

type StepDescriptionFamily = "LLCR" | "CR" | "IR" | "DWV" | "MATING";

type ParsedStepToken = {
  sequence: number;
  rawToken: string;
  suffixNote: string | null;
};

export function parseStepTokens(rawValue: string): { isValid: boolean; numbers: number[]; tokens: ParsedStepToken[]; errorMessage: string } {
  const normalized = rawValue
    .trim()
    .replaceAll("（", "(")
    .replaceAll("）", ")")
    .replaceAll("，", ",")
    .replaceAll("、", ",")
    .replaceAll("\u040e\u045e", ",");
  if (normalized === "") {
    return { isValid: true, numbers: [], tokens: [], errorMessage: "" };
  }
  const normalizedForSplit = normalized
    .replaceAll("\n", ",")
    .replaceAll(";", ",")
    .replace(/(\d|\)|[*#])\s+(?=\d)/g, "$1,");
  const parts = normalizedForSplit.split(",").map((part) => part.trim()).filter((part) => part.length > 0);
  const tokens: ParsedStepToken[] = [];
  for (const part of parts) {
    const match = part.match(/^(\d+)\s*(\((?:\d+|[a-zA-Z])\)|[*#])?$/);
    if (!match) {
      return {
        isValid: false,
        numbers: [],
        tokens: [],
        errorMessage: "Only digits, commas, Chinese commas, and spaces are allowed (extended tokens: 3(a), 4(1), 6#, 10*).",
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
  LLCR: [
    "llcr",
    "low level contact resistance",
    "contact resistance low level",
    "contact resistance (low level)",
    "contact resistance at low level signal",
  ],
  CR: ["cr", "contact resistance", "contact resistance (power)"],
  IR: ["ir", "insulation resistance"],
  DWV: ["dwv", "dielectric withstanding voltage"],
  MATING: ["mating", "un-mating", "mating/un-mating"],
};

const STEP_DESCRIPTION_FAMILY_LABELS: Record<StepDescriptionFamily, string> = {
  LLCR: "LLCR",
  CR: "CR",
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
  const hasContactResistance = containsAliasToken(normalized, "contact resistance");
  const hasLowLevel = containsAliasToken(normalized, "low level");
  if (STEP_DESCRIPTION_FAMILY_ALIASES.LLCR.some((alias) => containsAliasToken(normalized, alias))) {
    return "LLCR";
  }
  if (hasContactResistance && hasLowLevel) {
    return "LLCR";
  }
  if (STEP_DESCRIPTION_FAMILY_ALIASES.CR.some((alias) => containsAliasToken(normalized, alias))) {
    return "CR";
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
  const normalizeInitialPart = (value: string): string => {
    const trimmed = value.trim().replace(/[;:\s]+$/g, "");
    const withoutInitial = trimmed.replace(/^initial\b[\s:,-]*/i, "").trim();
    return withoutInitial.length > 0 ? withoutInitial : trimmed;
  };
  const normalizeFollowPart = (value: string): string => {
    const trimmed = value.trim().replace(/^[;:\s]+/g, "").replace(/[;:\s]+$/g, "");
    const withoutAfter = trimmed.replace(/^after(?:\s+test)?\b[\s:,-]*/i, "").trim();
    const normalizedFollow = withoutAfter.replace(/\s+/g, " ");
    if (/^(?:Δ\s*)?R\s*(?:<=|≤)/i.test(normalizedFollow)) {
      const right = normalizedFollow.replace(/^(?:Δ\s*)?R\s*/i, "").trim();
      return `ΔR ${right}`;
    }
    if (/^(?:<=|≤)/.test(normalizedFollow)) {
      return `ΔR ${normalizedFollow}`;
    }
    return normalizedFollow;
  };
  const semicolonSplit = normalized.match(
    /^(?<initial>initial\b.*?)[;,]\s*(?<follow>(?:(?:Δ\s*)?R|R)?\s*(?:<=|≤).*)$/i,
  );
  if (semicolonSplit?.groups?.initial && semicolonSplit?.groups?.follow) {
    const initialPart = normalizeInitialPart(semicolonSplit.groups.initial);
    const followPart = normalizeFollowPart(semicolonSplit.groups.follow);
    if (initialPart.length > 0 && followPart.length > 0) {
      return { initialPart, followPart };
    }
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
  const initialPart = normalizeInitialPart(normalized.slice(initialStart, afterStart));
  const followPart = normalizeFollowPart(normalized.slice(afterStart + afterMatch[0].length));
  if (!/^initial\b/i.test(initialPart)) {
    if (!/^(?:<=|≤)/.test(initialPart)) {
      return null;
    }
  }
  if (followPart.length === 0) {
    return null;
  }
  return { initialPart, followPart };
}

export function buildSelectedGroupStepPreviewRows(
  rows: EditableMatrixRow[],
  selectedGroup: GroupColumn | null,
  stepOutputOverrides: Record<string, StepOutputOverride>
): StepPreviewRow[] {
  if (!selectedGroup) {
    return [];
  }
  const baseRows = rows
    .filter((row) => !row.isSampleRow)
    .flatMap((row, rowIndex) => {
      const parsed = parseStepTokens(row.groups[selectedGroup.id] ?? "");
      if (!parsed.isValid) {
        return [];
      }
      return parsed.numbers.map((stepNo) => {
        const token = parsed.tokens.find((item) => item.sequence === stepNo);
        const key = stepOutputKey(selectedGroup.id, stepNo, row.id);
        const override = stepOutputOverrides[key];
        const itemSectionMarker = row.section.match(/([*#]|[\uFF08(](?:\d+|[a-zA-Z])[\uFF09)])/)?.[1] ?? row.item.match(/([*#]|[\uFF08(](?:\d+|[a-zA-Z])[\uFF09)])/)?.[1] ?? null;
        const stepMarker = token?.suffixNote ?? token?.rawToken.match(/([*#]|[\uFF08(](?:\d+|[a-zA-Z])[\uFF09)])/)?.[1] ?? null;
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

export function extractMarkerKey(token: string | null | undefined): string | null {
  if (!token) {
    return null;
  }
  const markerMatch = token.match(/[锛?](\d+|[a-zA-Z])[锛?]|([*#])/);
  if (!markerMatch) {
    return null;
  }
  if (markerMatch[1]) {
    return markerMatch[1].toLowerCase();
  }
  return markerMatch[2] ?? null;
}

export function buildPreviewStepNoteLookup(
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
    previewGroup = importPreview.groups.find(
      (group, index) =>
        normalizeGroupDisplayName(group.group_label, `${index + 1}`) === selectedGroup.name
    );
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

export function formatConciseItemSectionNote(stepNo: number, noteText: string): string {
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

export function stripLeadingMarkerPrefix(noteText: string): string {
  return noteText
    .trim()
    .replace(/^\((?:\d*\s*)?[a-z]\)\s*/i, "")
    .replace(/^\(\d+\)\s*/, "")
    .replace(/^[*#]\s*/, "")
    .trim();
}

export function replaceItemSectionNoteSection(noteText: string, sourceSection: string): string {
  const body = noteText
    .replace(/^Section:\s*[^*#()]+(?:[*#]|\((?:\d*\s*)?[a-z]\))?\s*/i, "")
    .trim();
  return body.length > 0 ? `Section: ${sourceSection} ${body}` : `Section: ${sourceSection}`;
}
