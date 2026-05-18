import {
  useProjectWorkbenchModel,
  type ProjectWorkbenchModel
} from "./useProjectWorkbenchModel";

export type ProjectRuntimeConsoleModel = Pick<
  ProjectWorkbenchModel,
  | "baselineItems"
  | "error"
  | "folderReady"
  | "latestLtr"
  | "matrixAuthorityDraft"
  | "matrixCandidateDraft"
  | "matrixDraft"
  | "matrixDraftError"
  | "matrixDraftLoading"
  | "message"
  | "project"
  | "projectId"
  | "runtimeAuthoritySync"
  | "runtimeProjectionError"
  | "runtimeProjectionLoading"
  | "runtimeProjectionSnapshot"
  | "runtimeSelectedTokenReference"
  | "setRuntimeSelectedTokenReference"
  | "versionStatus"
>;

export function selectProjectRuntimeConsoleModel(
  model: ProjectWorkbenchModel
): ProjectRuntimeConsoleModel {
  return {
    baselineItems: model.baselineItems,
    error: model.error,
    folderReady: model.folderReady,
    latestLtr: model.latestLtr,
    matrixAuthorityDraft: model.matrixAuthorityDraft,
    matrixCandidateDraft: model.matrixCandidateDraft,
    matrixDraft: model.matrixDraft,
    matrixDraftError: model.matrixDraftError,
    matrixDraftLoading: model.matrixDraftLoading,
    message: model.message,
    project: model.project,
    projectId: model.projectId,
    runtimeAuthoritySync: model.runtimeAuthoritySync,
    runtimeProjectionError: model.runtimeProjectionError,
    runtimeProjectionLoading: model.runtimeProjectionLoading,
    runtimeProjectionSnapshot: model.runtimeProjectionSnapshot,
    runtimeSelectedTokenReference: model.runtimeSelectedTokenReference,
    setRuntimeSelectedTokenReference: model.setRuntimeSelectedTokenReference,
    versionStatus: model.versionStatus
  };
}

export function useProjectRuntimeConsoleModel(projectId: string): ProjectRuntimeConsoleModel {
  const model = useProjectWorkbenchModel(projectId);
  return selectProjectRuntimeConsoleModel(model);
}
