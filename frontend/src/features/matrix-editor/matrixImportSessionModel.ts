import { type MatrixPreviewResponse } from "../../api/client";

export type MatrixImportSessionActionState = {
  hasLivePreview: boolean;
  changeSelectedGroupsDisabled: boolean;
  changeSelectedGroupsDisabledReason: string;
};

export function buildMatrixImportSessionActionState(
  preview: MatrixPreviewResponse | null,
  hasDraftSelectionSource: boolean,
  sourceUnavailableMessage?: string | null
): MatrixImportSessionActionState {
  const hasLivePreview = preview !== null;
  if (sourceUnavailableMessage && sourceUnavailableMessage.trim().length > 0) {
    return {
      hasLivePreview,
      changeSelectedGroupsDisabled: true,
      changeSelectedGroupsDisabledReason: sourceUnavailableMessage.trim(),
    };
  }
  const canChangeSelectedGroups = hasLivePreview || hasDraftSelectionSource;
  return {
    hasLivePreview,
    changeSelectedGroupsDisabled: !canChangeSelectedGroups,
    changeSelectedGroupsDisabledReason: canChangeSelectedGroups
      ? ""
      : "No group selection source is available. Import source matrix to start group selection.",
  };
}

export function preserveSelectedGroupKeys(input: {
  availableGroupKeys: string[];
  previousSelectedGroupKeys: string[];
}): string[] {
  const available = new Set(input.availableGroupKeys);
  const preserved = input.previousSelectedGroupKeys.filter((groupKey) => available.has(groupKey));
  return preserved.length > 0 ? preserved : input.availableGroupKeys;
}
