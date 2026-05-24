import { type MatrixPreviewResponse } from "../../api/client";

export type MatrixImportSessionActionState = {
  hasLivePreview: boolean;
  changeSelectedGroupsDisabled: boolean;
  changeSelectedGroupsDisabledReason: string;
};

export function buildMatrixImportSessionActionState(
  preview: MatrixPreviewResponse | null
): MatrixImportSessionActionState {
  const hasLivePreview = preview !== null;
  return {
    hasLivePreview,
    changeSelectedGroupsDisabled: !hasLivePreview,
    changeSelectedGroupsDisabledReason: hasLivePreview
      ? ""
      : "Source preview session unavailable. Use Change Source Matrix to start a new source session.",
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
