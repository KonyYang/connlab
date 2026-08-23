import type {
  LlcrCrRecordType,
  MatrixEditorTestRecordDraftRequest,
} from "../../api/client";
import "../../contact-measurement-plan.css";
import { useLlcrCrSpecializedRecordWorkbookModel } from "./useLlcrCrSpecializedRecordWorkbookModel";

export function LlcrCrRecordWorkbookPanel({ projectId, draftRequest }: {
  projectId: string;
  draftRequest: MatrixEditorTestRecordDraftRequest;
}) {
  return <section className="llcr-cr-record-panel" aria-label="LLCR and CR tables">
    <header className="llcr-cr-record-panel-header">
      <div>
        <h3>LLCR/CR表</h3>
        <p>Generate and download a preview workbook from the current Matrix draft and Test points.</p>
      </div>
    </header>
    <div className="llcr-cr-record-downloads">
      <RecordDownload projectId={projectId} recordType="llcr" draftRequest={draftRequest} />
      <RecordDownload projectId={projectId} recordType="cr" draftRequest={draftRequest} />
    </div>
  </section>;
}

function RecordDownload({ projectId, recordType, draftRequest }: {
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
      className="is-primary"
      type="button"
      disabled={model.busy}
      onClick={() => void model.downloadWorkbook()}
    >
      {model.busy ? `Generating ${label}...` : `Download ${label}`}
    </button>
    {model.error ? <p className="llcr-cr-record-error" role="alert">{model.error}</p> : null}
    {model.message ? <p className="llcr-cr-record-success" role="status">{model.message}</p> : null}
  </div>;
}
