import type { ReactElement } from "react";

import type { ConfirmIntakeCase, IntakeCaseReviewItem } from "../../api/client";

type PrecheckMessagesProps = {
  activeCase: IntakeCaseReviewItem;
  confirmationBlockedReason: string | null;
  confirmError: string | null;
  confirmResult: ConfirmIntakeCase | null;
  fieldSaveError: string | null;
  fieldSaveMessage: string | null;
};

export function PrecheckMessages(props: PrecheckMessagesProps): ReactElement {
  return (
    <div className="precheck-messages">
      {props.activeCase.missing_required_fields.length > 0 ? <p>Confirmation blockers: {props.activeCase.missing_required_fields.join(", ")}. Backend confirmation rejects missing required project request fields. missing_required_fields</p> : null}
      {props.confirmationBlockedReason ? <p>{props.confirmationBlockedReason}</p> : null}
      {props.confirmError ? <p>{props.confirmError}</p> : null}
      {props.fieldSaveError ? <p>{props.fieldSaveError}</p> : null}
      {props.fieldSaveMessage ? <p>{props.fieldSaveMessage}</p> : null}
      {props.confirmResult ? <p className="confirmation-result">Project created: {props.confirmResult.project_id}. Confirm into project completed.</p> : null}
    </div>
  );
}
