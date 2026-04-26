import type { FormEvent, ReactElement } from "react";
import type { ApplicationForm } from "../../api/client";

type ApplicationFormActionPanelProps = {
  formRecord: ApplicationForm | null;
  onSubmitForm: (event: FormEvent<HTMLFormElement>) => Promise<void>;
};

export function ApplicationFormActionPanel({
  formRecord,
  onSubmitForm
}: ApplicationFormActionPanelProps): ReactElement {
  return (
    <div className="action-panel-body">
      <div className="operator-panel">
        <div>
          <p className="eyebrow">Application intake</p>
          <h4>{formRecord ? "Application form uploaded" : "Upload application form"}</h4>
          <p>
            {formRecord
              ? "Next action: review the extracted metadata, then continue to deterministic precheck."
              : "Use the current MVP DOCX parser. Email and Word intake automation are future work."}
          </p>
        </div>
        <form className="card-form upload-panel" onSubmit={onSubmitForm}>
          <input name="applicationForm" type="file" accept=".docx" />
          <button className="primary-action" type="submit">Upload form</button>
        </form>
      </div>

      {formRecord && (
        <dl className="metadata-grid">
          <div>
            <dt>Form</dt>
            <dd>{formRecord.form_no} Rev {formRecord.revision}</dd>
          </div>
          <div>
            <dt>Requester</dt>
            <dd>{formRecord.requester}</dd>
          </div>
          <div>
            <dt>Email</dt>
            <dd>{formRecord.email || "Not found"}</dd>
          </div>
          <div>
            <dt>Project Number</dt>
            <dd>{formRecord.project_number || "Not found"}</dd>
          </div>
          <div className="metadata-wide">
            <dt>Requested Testing</dt>
            <dd>{formRecord.requested_testing || "Not found"}</dd>
          </div>
        </dl>
      )}
    </div>
  );
}
