import {
  useProjectWorkbenchModel,
  type ProjectWorkbenchModel
} from "./useProjectWorkbenchModel";

export type ProjectWorkbenchSupportModel = Pick<
  ProjectWorkbenchModel,
  | "approvalInput"
  | "approvalInputSources"
  | "approvalPreview"
  | "approvalResult"
  | "evidencePlan"
  | "evidenceResult"
  | "executingApprovalPackage"
  | "folderReady"
  | "folderResources"
  | "placingEvidence"
  | "previewingApprovalPackage"
  | "previewingEvidence"
  | "setApprovalInput"
  | "onExecuteApprovalPackage"
  | "onFolderCreated"
  | "onPlaceEvidence"
  | "onPreviewApprovalPackage"
  | "onPreviewEvidence"
>;

export function selectProjectWorkbenchSupportModel(
  model: ProjectWorkbenchModel
): ProjectWorkbenchSupportModel {
  return {
    approvalInput: model.approvalInput,
    approvalInputSources: model.approvalInputSources,
    approvalPreview: model.approvalPreview,
    approvalResult: model.approvalResult,
    evidencePlan: model.evidencePlan,
    evidenceResult: model.evidenceResult,
    executingApprovalPackage: model.executingApprovalPackage,
    folderReady: model.folderReady,
    folderResources: model.folderResources,
    placingEvidence: model.placingEvidence,
    previewingApprovalPackage: model.previewingApprovalPackage,
    previewingEvidence: model.previewingEvidence,
    setApprovalInput: model.setApprovalInput,
    onExecuteApprovalPackage: model.onExecuteApprovalPackage,
    onFolderCreated: model.onFolderCreated,
    onPlaceEvidence: model.onPlaceEvidence,
    onPreviewApprovalPackage: model.onPreviewApprovalPackage,
    onPreviewEvidence: model.onPreviewEvidence
  };
}

export function useProjectWorkbenchSupportModel(projectId: string): ProjectWorkbenchSupportModel {
  const model = useProjectWorkbenchModel(projectId);
  return selectProjectWorkbenchSupportModel(model);
}
