import type { LlcrCrRecordType } from "../../api/client";
import "../../contact-measurement-plan.css";
import { useLlcrCrSpecializedRecordWorkbookModel } from "./useLlcrCrSpecializedRecordWorkbookModel";

export function LlcrCrRecordWorkbookPanel({ projectId }: { projectId: string }) {
  return <section className="llcr-cr-record-panel" aria-label="LLCR and CR tables">
    <header className="llcr-cr-record-panel-header">
      <div>
        <h3>LLCR/CR表</h3>
        <p>Generate and download a separate workbook from the confirmed Matrix and Test points.</p>
      </div>
    </header>
    <div className="llcr-cr-record-downloads">
      <RecordDownload projectId={projectId} recordType="llcr" />
      <RecordDownload projectId={projectId} recordType="cr" />
    </div>
  </section>;
}

function RecordDownload({ projectId, recordType }: {
  projectId: string;
  recordType: LlcrCrRecordType;
}) {
  const model = useLlcrCrSpecializedRecordWorkbookModel(projectId, recordType);
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
