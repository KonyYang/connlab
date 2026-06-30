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
  | "lifecycle"
  | "lifecycleLoading"
  | "lifecycleError"
  | "activeConfirmedMatrixSnapshot"
  | "activeConfirmedMatrixLoading"
  | "basicInformation"
  | "basicInformationLoading"
  | "basicInformationError"
  | "confirmedFeeLatest"
  | "matrixAuthorityDraft"
  | "matrixCandidateDraft"
  | "matrixDraft"
  | "matrixDraftError"
  | "matrixDraftLoading"
  | "message"
  | "outputStatusSummary"
  | "packagePreview"
  | "packagePreviewError"
  | "packagePreviewLoading"
  | "officialWorkspacePreview"
  | "officialWorkspaceLoading"
  | "officialWorkspaceCreating"
  | "officialWorkspaceProgressLabel"
  | "officialWorkspaceError"
  | "officialWorkspaceResult"
  | "officialFolderCheckPreview"
  | "officialFolderCheckLoading"
  | "officialFolderCheckRepairing"
  | "officialFolderCheckError"
  | "officialFolderRepairResult"
  | "publicDriveUploadPreview"
  | "publicDriveUploadLoading"
  | "publicDriveUploading"
  | "publicDriveUploadError"
  | "publicDriveUploadResult"
  | "publicFolderWorkflowContext"
  | "publicFolderWorkflowContextLoading"
  | "publicFolderWorkflowContextError"
  | "publicFolderWorkflowPreviews"
  | "publicFolderWorkflowResults"
  | "publicFolderWorkflowBusyOperation"
  | "publicFolderWorkflowConfirmingOperation"
  | "publicFolderWorkflowError"
  | "publicFolderWorkflowMessage"
  | "publicFolderWorkflowAutoSyncBusy"
  | "requestMaterialPreview"
  | "requestMaterialLoading"
  | "requestMaterialCollecting"
  | "requestMaterialError"
  | "requiredFormsPreview"
  | "requiredFormsLoading"
  | "requiredFormsGenerating"
  | "requiredFormsError"
  | "requiredFormsResult"
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
  | "onRefreshLifecycle"
  | "onActivateLifecycle"
  | "onCloseLifecycle"
  | "onRefreshPackagePreview"
  | "onRefreshOfficialWorkspacePreview"
  | "onCreateOfficialWorkspace"
  | "onRefreshOfficialFolderCheck"
  | "onRepairOfficialFolderStructure"
  | "onRefreshPublicDriveUploadPreview"
  | "onRefreshPublicFolderWorkflowContext"
  | "onSetPublicFolderWorkflowAutoSync"
  | "onPreviewPublicFolderWorkflowOperation"
  | "onConfirmPublicFolderWorkflowOperation"
  | "onCancelPublicFolderWorkflowOperation"
  | "onRefreshBasicInformation"
  | "onUploadPublicDriveProjectFolder"
  | "onRefreshRequestMaterial"
  | "onCollectRequestMaterial"
  | "onRefreshRequiredForms"
  | "onGenerateRequiredForms"
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
    lifecycle: model.lifecycle,
    lifecycleLoading: model.lifecycleLoading,
    lifecycleError: model.lifecycleError,
    activeConfirmedMatrixSnapshot: model.activeConfirmedMatrixSnapshot,
    activeConfirmedMatrixLoading: model.activeConfirmedMatrixLoading,
    basicInformation: model.basicInformation,
    basicInformationLoading: model.basicInformationLoading,
    basicInformationError: model.basicInformationError,
    confirmedFeeLatest: model.confirmedFeeLatest,
    matrixAuthorityDraft: model.matrixAuthorityDraft,
    matrixCandidateDraft: model.matrixCandidateDraft,
    matrixDraft: model.matrixDraft,
    matrixDraftError: model.matrixDraftError,
    matrixDraftLoading: model.matrixDraftLoading,
    message: model.message,
    outputStatusSummary: model.outputStatusSummary,
    packagePreview: model.packagePreview,
    packagePreviewError: model.packagePreviewError,
    packagePreviewLoading: model.packagePreviewLoading,
    officialWorkspacePreview: model.officialWorkspacePreview,
    officialWorkspaceLoading: model.officialWorkspaceLoading,
    officialWorkspaceCreating: model.officialWorkspaceCreating,
    officialWorkspaceProgressLabel: model.officialWorkspaceProgressLabel,
    officialWorkspaceError: model.officialWorkspaceError,
    officialWorkspaceResult: model.officialWorkspaceResult,
    officialFolderCheckPreview: model.officialFolderCheckPreview,
    officialFolderCheckLoading: model.officialFolderCheckLoading,
    officialFolderCheckRepairing: model.officialFolderCheckRepairing,
    officialFolderCheckError: model.officialFolderCheckError,
    officialFolderRepairResult: model.officialFolderRepairResult,
    publicDriveUploadPreview: model.publicDriveUploadPreview,
    publicDriveUploadLoading: model.publicDriveUploadLoading,
    publicDriveUploading: model.publicDriveUploading,
    publicDriveUploadError: model.publicDriveUploadError,
    publicDriveUploadResult: model.publicDriveUploadResult,
    publicFolderWorkflowContext: model.publicFolderWorkflowContext,
    publicFolderWorkflowContextLoading: model.publicFolderWorkflowContextLoading,
    publicFolderWorkflowContextError: model.publicFolderWorkflowContextError,
    publicFolderWorkflowPreviews: model.publicFolderWorkflowPreviews,
    publicFolderWorkflowResults: model.publicFolderWorkflowResults,
    publicFolderWorkflowBusyOperation: model.publicFolderWorkflowBusyOperation,
    publicFolderWorkflowConfirmingOperation:
      model.publicFolderWorkflowConfirmingOperation,
    publicFolderWorkflowError: model.publicFolderWorkflowError,
    publicFolderWorkflowMessage: model.publicFolderWorkflowMessage,
    publicFolderWorkflowAutoSyncBusy: model.publicFolderWorkflowAutoSyncBusy,
    requestMaterialPreview: model.requestMaterialPreview,
    requestMaterialLoading: model.requestMaterialLoading,
    requestMaterialCollecting: model.requestMaterialCollecting,
    requestMaterialError: model.requestMaterialError,
    requiredFormsPreview: model.requiredFormsPreview,
    requiredFormsLoading: model.requiredFormsLoading,
    requiredFormsGenerating: model.requiredFormsGenerating,
    requiredFormsError: model.requiredFormsError,
    requiredFormsResult: model.requiredFormsResult,
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
    onRefreshLifecycle: model.onRefreshLifecycle,
    onActivateLifecycle: model.onActivateLifecycle,
    onCloseLifecycle: model.onCloseLifecycle,
    onRefreshPackagePreview: model.onRefreshPackagePreview,
    onRefreshOfficialWorkspacePreview: model.onRefreshOfficialWorkspacePreview,
    onCreateOfficialWorkspace: model.onCreateOfficialWorkspace,
    onRefreshOfficialFolderCheck: model.onRefreshOfficialFolderCheck,
    onRepairOfficialFolderStructure: model.onRepairOfficialFolderStructure,
    onRefreshPublicDriveUploadPreview: model.onRefreshPublicDriveUploadPreview,
    onRefreshPublicFolderWorkflowContext: model.onRefreshPublicFolderWorkflowContext,
    onSetPublicFolderWorkflowAutoSync: model.onSetPublicFolderWorkflowAutoSync,
    onPreviewPublicFolderWorkflowOperation:
      model.onPreviewPublicFolderWorkflowOperation,
    onConfirmPublicFolderWorkflowOperation:
      model.onConfirmPublicFolderWorkflowOperation,
    onCancelPublicFolderWorkflowOperation:
      model.onCancelPublicFolderWorkflowOperation,
    onRefreshBasicInformation: model.onRefreshBasicInformation,
    onUploadPublicDriveProjectFolder: model.onUploadPublicDriveProjectFolder,
    onRefreshRequestMaterial: model.onRefreshRequestMaterial,
    onCollectRequestMaterial: model.onCollectRequestMaterial,
    onRefreshRequiredForms: model.onRefreshRequiredForms,
    onGenerateRequiredForms: model.onGenerateRequiredForms,
    onRefreshSection2Sync: model.onRefreshSection2Sync,
    onSyncSection2: model.onSyncSection2,
    versionStatus: model.versionStatus
  };
}

export function useProjectRuntimeConsoleModel(projectId: string): ProjectRuntimeConsoleModel {
  const model = useProjectWorkbenchModel(projectId);
  return selectProjectRuntimeConsoleModel(model);
}
