import type {
  LlcrCrRecordType,
  MatrixEditorTestRecordDraftRequest,
} from "../../api/client";
import "../../contact-measurement-plan.css";
import { useLlcrCrSpecializedRecordWorkbookModel } from "./useLlcrCrSpecializedRecordWorkbookModel";

export function LlcrCrRecordDownloadAction({ projectId, recordType, draftRequest }: {
  projectId: string;
  recordType: LlcrCrRecordType;
  draftRequest: MatrixEditorTestRecordDraftRequest;
}) {
  const model = useLlcrCrSpecializedRecordWorkbookModel(
    projectId,
    recordType,
    draftRequest,
  );
  const label = recordType.toUpperCase();
  return <div className="llcr-cr-record-download">
    <button
      className="contact-measurement-button is-compact"
      type="button"
      disabled={model.busy}
      title={`Download an unconfirmed ${label} preview workbook from the current Matrix draft and Test points.`}
      onClick={() => void model.downloadWorkbook()}
    >
      {model.busy ? `Generating ${label}...` : `Download ${label}`}
    </button>
    {model.error ? <p className="llcr-cr-record-error" role="alert">{model.error}</p> : null}
    {model.message ? <p className="llcr-cr-record-success" role="status">{model.message}</p> : null}
  </div>;
}
