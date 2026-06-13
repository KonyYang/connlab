import {
  useProjectWorkbenchModel,
  type ProjectWorkbenchModel
} from "./useProjectWorkbenchModel";

export type ProjectRuntimeConsoleModel = Pick<
  ProjectWorkbenchModel,
  | "baselineItems"
  | "error"
  | "folderReady"
  | "folderResources"
  | "latestLtr"
  | "activeConfirmedMatrixSnapshot"
  | "activeConfirmedMatrixLoading"
  | "matrixAuthorityDraft"
  | "matrixCandidateDraft"
  | "matrixDraft"
  | "matrixDraftError"
  | "matrixDraftLoading"
  | "message"
  | "packagePreview"
  | "packagePreviewError"
  | "packagePreviewLoading"
  | "officialWorkspacePreview"
  | "officialWorkspaceLoading"
  | "officialWorkspaceCreating"
  | "officialWorkspaceError"
  | "officialWorkspaceResult"
  | "officialFolderCheckPreview"
  | "officialFolderCheckLoading"
  | "officialFolderCheckRepairing"
  | "officialFolderCheckError"
  | "officialFolderRepairResult"
  | "requestMaterialPreview"
  | "requestMaterialLoading"
  | "requestMaterialCollecting"
  | "requestMaterialError"
  | "project"
  | "projectId"
  | "runtimeAuthoritySync"
  | "runtimeProjectionError"
  | "runtimeProjectionLoading"
  | "runtimeProjectionSnapshot"
  | "runtimeSelectedTokenReference"
  | "section2SyncError"
  | "section2SyncLoading"
  | "section2SyncPreview"
  | "section2SyncSyncing"
  | "setRuntimeSelectedTokenReference"
  | "onFolderCreated"
  | "onRefreshPackagePreview"
  | "onRefreshOfficialWorkspacePreview"
  | "onCreateOfficialWorkspace"
  | "onRefreshOfficialFolderCheck"
  | "onRepairOfficialFolderStructure"
  | "onRefreshRequestMaterial"
  | "onCollectRequestMaterial"
  | "onRefreshSection2Sync"
  | "onSyncSection2"
  | "versionStatus"
>;

export function selectProjectRuntimeConsoleModel(
  model: ProjectWorkbenchModel
): ProjectRuntimeConsoleModel {
  return {
    baselineItems: model.baselineItems,
    error: model.error,
    folderReady: model.folderReady,
    folderResources: model.folderResources,
    latestLtr: model.latestLtr,
    activeConfirmedMatrixSnapshot: model.activeConfirmedMatrixSnapshot,
    activeConfirmedMatrixLoading: model.activeConfirmedMatrixLoading,
    matrixAuthorityDraft: model.matrixAuthorityDraft,
    matrixCandidateDraft: model.matrixCandidateDraft,
    matrixDraft: model.matrixDraft,
    matrixDraftError: model.matrixDraftError,
    matrixDraftLoading: model.matrixDraftLoading,
    message: model.message,
    packagePreview: model.packagePreview,
    packagePreviewError: model.packagePreviewError,
    packagePreviewLoading: model.packagePreviewLoading,
    officialWorkspacePreview: model.officialWorkspacePreview,
    officialWorkspaceLoading: model.officialWorkspaceLoading,
    officialWorkspaceCreating: model.officialWorkspaceCreating,
    officialWorkspaceError: model.officialWorkspaceError,
    officialWorkspaceResult: model.officialWorkspaceResult,
    officialFolderCheckPreview: model.officialFolderCheckPreview,
    officialFolderCheckLoading: model.officialFolderCheckLoading,
    officialFolderCheckRepairing: model.officialFolderCheckRepairing,
    officialFolderCheckError: model.officialFolderCheckError,
    officialFolderRepairResult: model.officialFolderRepairResult,
    requestMaterialPreview: model.requestMaterialPreview,
    requestMaterialLoading: model.requestMaterialLoading,
    requestMaterialCollecting: model.requestMaterialCollecting,
    requestMaterialError: model.requestMaterialError,
    project: model.project,
    projectId: model.projectId,
    runtimeAuthoritySync: model.runtimeAuthoritySync,
    runtimeProjectionError: model.runtimeProjectionError,
    runtimeProjectionLoading: model.runtimeProjectionLoading,
    runtimeProjectionSnapshot: model.runtimeProjectionSnapshot,
    runtimeSelectedTokenReference: model.runtimeSelectedTokenReference,
    section2SyncError: model.section2SyncError,
    section2SyncLoading: model.section2SyncLoading,
    section2SyncPreview: model.section2SyncPreview,
    section2SyncSyncing: model.section2SyncSyncing,
    setRuntimeSelectedTokenReference: model.setRuntimeSelectedTokenReference,
    onFolderCreated: model.onFolderCreated,
    onRefreshPackagePreview: model.onRefreshPackagePreview,
    onRefreshOfficialWorkspacePreview: model.onRefreshOfficialWorkspacePreview,
    onCreateOfficialWorkspace: model.onCreateOfficialWorkspace,
    onRefreshOfficialFolderCheck: model.onRefreshOfficialFolderCheck,
    onRepairOfficialFolderStructure: model.onRepairOfficialFolderStructure,
    onRefreshRequestMaterial: model.onRefreshRequestMaterial,
    onCollectRequestMaterial: model.onCollectRequestMaterial,
    onRefreshSection2Sync: model.onRefreshSection2Sync,
    onSyncSection2: model.onSyncSection2,
    versionStatus: model.versionStatus
  };
}

export function useProjectRuntimeConsoleModel(projectId: string): ProjectRuntimeConsoleModel {
  const model = useProjectWorkbenchModel(projectId);
  return selectProjectRuntimeConsoleModel(model);
}
