import type {
  MatrixEditorRecordType,
  MatrixEditorTestRecordDraftRequest,
} from "../../api/client";
import "../../contact-measurement-plan.css";
import { useLlcrCrSpecializedRecordWorkbookModel } from "./useLlcrCrSpecializedRecordWorkbookModel";

export function LlcrCrRecordDownloadAction({ projectId, recordType, getDraftRequest, matrixHasPendingChanges = false }: {
  projectId: string;
  recordType: MatrixEditorRecordType;
  getDraftRequest: () => MatrixEditorTestRecordDraftRequest;
  matrixHasPendingChanges?: boolean;
}) {
  const model = useLlcrCrSpecializedRecordWorkbookModel(
    projectId,
    recordType,
    getDraftRequest,
    matrixHasPendingChanges,
  );
  const label = recordType === "ir_dwv" ? "IR&DWV" : recordType.toUpperCase();
  return <div className="llcr-cr-record-download">
    <button
      className="contact-measurement-button is-compact"
      type="button"
      disabled={model.busy || Boolean(model.pending)}
      title={`Check whether the current ${label} form belongs in Downloads or the project Test results folder.`}
      onClick={() => void model.downloadWorkbook()}
    >
      {model.busy ? `Checking ${label}...` : `${label} Form`}
    </button>
    {model.error ? <p className="llcr-cr-record-error" role="alert">{model.error}</p> : null}
    {model.message ? <p className="llcr-cr-record-success" role="status">{model.message}</p> : null}
    {!model.pending && model.information.length ? <ul aria-label={`${label} source information`}>
      {model.information.map((item) => <li key={item}>{item}</li>)}
    </ul> : null}
    {model.pending ? <div className="official-output-conflict-backdrop">
      <section
        className="official-output-conflict-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby={`${recordType}-form-confirm-title`}
      >
        <h3 id={`${recordType}-form-confirm-title`}>
          {model.pending.mode === "download"
            ? `Download ${label} preview?`
            : `Update existing ${label} Form?`}
        </h3>
        <p>
          {model.pending.mode === "download"
            ? `This ${label} preview will be saved to your browser Downloads, not the project folder. ${model.pending.authority_status === "unconfirmed" ? "It uses the current unconfirmed Matrix draft." : "The official project folder is not available."}`
            : `The existing ${label} form may contain measured results. It will be preserved in History/Test results before a new blank form is saved to Test results.`}
        </p>
        {model.information.length ? <ul>{model.information.map((item) => <li key={item}>{item}</li>)}</ul> : null}
        <div className="official-output-conflict-actions">
          {model.pending.mode === "download" ? (
            <button className="contact-measurement-button" type="button" disabled={model.busy}
              onClick={() => void model.confirmDownload()}>Download preview</button>
          ) : (
            <button className="contact-measurement-button" type="button" disabled={model.busy}
              onClick={() => void model.archiveAndPublish()}>Archive old file and save new</button>
          )}
          <button className="contact-measurement-button" type="button" disabled={model.busy}
            onClick={model.cancel}>Cancel</button>
        </div>
      </section>
    </div> : null}
  </div>;
}
