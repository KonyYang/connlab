export type MatrixWorkspaceMode = "draft" | "activeAuthority" | "revisionDraft";

export type MatrixWorkspaceBannerModel = {
  mode: MatrixWorkspaceMode;
  title: string;
  consequence: string;
  tone: "draft" | "authority" | "revision";
};

export type MatrixActionCopy = {
  revertDraftChanges: string;
  changeSelectedGroups: string;
  changeSourceMatrix: string;
  confirmAsActiveMatrix: string;
  createRevisionDraft: string;
  confirmRevision: string;
};

export const MATRIX_WORKSPACE_ACTION_COPY: MatrixActionCopy = {
  revertDraftChanges: "Discard local unsaved edits and reload the last saved draft.",
  changeSelectedGroups: "Adjust execution groups for this matrix configuration. This is not a new source import.",
  changeSourceMatrix: "Replace the current source matrix session. Unsaved draft edits may be discarded.",
  confirmAsActiveMatrix: "Publish this saved draft as the current authority used by Project Workbench and Test Record generation.",
  createRevisionDraft: "Start an editable copy from the active authority. The current active matrix remains in use.",
  confirmRevision: "Replace the active authority with this saved revision draft.",
};

export function buildMatrixWorkspaceBannerModel(input: {
  hasPersistedDraft: boolean;
  baseConfirmedMatrixId: string | null;
  activeAuthorityConfirmed: boolean;
}): MatrixWorkspaceBannerModel {
  if (input.activeAuthorityConfirmed) {
    return {
      mode: "activeAuthority",
      title: "Current Active Matrix Authority",
      consequence: "Used by Project Workbench and Test Record generation",
      tone: "authority",
    };
  }
  if (input.hasPersistedDraft && input.baseConfirmedMatrixId) {
    return {
      mode: "revisionDraft",
      title: "Editing Revision Draft",
      consequence: "Changes are not active until confirmed",
      tone: "revision",
    };
  }
  return {
    mode: "draft",
    title: "Editing Draft",
    consequence: "Not active for downstream outputs",
    tone: "draft",
  };
}
