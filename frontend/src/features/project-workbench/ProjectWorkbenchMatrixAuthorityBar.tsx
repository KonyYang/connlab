import type { ReactElement } from "react";
import type { ProjectTestPlanDraft } from "../../api/client";

type ProjectWorkbenchMatrixAuthorityBarProps = {
  authorityDraft: ProjectTestPlanDraft | null;
  candidateDraft: ProjectTestPlanDraft | null;
  hasBlockers: boolean;
};

export function ProjectWorkbenchMatrixAuthorityBar({
  authorityDraft,
  candidateDraft,
  hasBlockers
}: ProjectWorkbenchMatrixAuthorityBarProps): ReactElement {
  return (
    <div className="matrix-authority-bar">
      {authorityDraft ? (
        <p className="fine-print">
          Confirmed authority v{authorityDraft.version}
          {candidateDraft ? ` | Editing candidate v${candidateDraft.version}` : ""}
        </p>
      ) : (
        <p className="fine-print">No confirmed authority yet. Confirm the draft when blockers are resolved.</p>
      )}
      <span className="status-chip">
        {hasBlockers ? "Validation blockers present" : "Ready for authority confirm"}
      </span>
    </div>
  );
}
