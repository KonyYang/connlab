import type { LlcrCrRecordType } from "../../api/client";
import { useLlcrCrSpecializedRecordWorkbookModel } from "./useLlcrCrSpecializedRecordWorkbookModel";
import "../../contact-measurement-plan.css";

export function LlcrCrRecordWorkbookPanel({ projectId }: { projectId: string }) {
  const llcr = useLlcrCrSpecializedRecordWorkbookModel(projectId, "llcr");
  const cr = useLlcrCrSpecializedRecordWorkbookModel(projectId, "cr");

  return <section className="llcr-cr-record-panel" aria-label="LLCR and CR tables">
    <header className="llcr-cr-record-panel-header">
      <div><h3>LLCR/CR表</h3><p>Generate separate test-entry workbooks from the confirmed Matrix and Test points.</p></div>
    </header>
    <div className="llcr-cr-record-grid">
      <RecordCard recordType="llcr" model={llcr} />
      <RecordCard recordType="cr" model={cr} />
    </div>
  </section>;
}

function RecordCard({ recordType, model }: {
  recordType: LlcrCrRecordType;
  model: ReturnType<typeof useLlcrCrSpecializedRecordWorkbookModel>;
}) {
  const label = recordType.toUpperCase();
  const preview = model.preview;
  const categoryCount = new Set(preview?.sections.map((section) => section.category_id)).size;
  const groupCount = new Set(preview?.sections.map((section) => section.confirmed_group_id)).size;
  const status = !preview
    ? "Preview the current confirmed authorities."
    : preview.status === "empty"
      ? `Not required by the confirmed Matrix.`
      : preview.status === "ready"
        ? `${preview.row_count} entry rows${recordType === "llcr" ? ` · ΔR ${preview.delta_r_enabled ? "on" : "off"}` : ""}`
        : preview.diagnostics.map((item) => item.message).join(" ") || "Review the confirmed authorities before generating.";

  return <article className="llcr-cr-record-card" aria-label={`${label} table`}>
    <div className="llcr-cr-record-card-heading"><h4>{label}</h4><span className={`llcr-cr-record-status is-${preview?.status ?? "unchecked"}`}>{preview?.status === "ready" ? "Ready" : preview?.status === "empty" ? "Not needed" : preview ? "Review" : "Unchecked"}</span></div>
    <p className="llcr-cr-record-card-status">{status}</p>
    {preview?.status === "ready" ? <p className="llcr-cr-record-card-facts">{categoryCount} {categoryCount === 1 ? "category" : "categories"} · {groupCount} {groupCount === 1 ? "group" : "groups"} · Matrix r{preview.confirmed_revision}</p> : null}
    {model.error ? <p className="llcr-cr-record-error" role="alert">{model.error}</p> : null}
    <div className="llcr-cr-record-actions">
      <button type="button" disabled={Boolean(model.busy)} onClick={() => void model.previewWorkbook()} aria-label={`Preview ${label} table`}>{model.busy === "preview" ? "Previewing..." : "Preview"}</button>
      {preview?.status === "ready" ? <button type="button" disabled={!model.canGenerate || Boolean(model.busy)} onClick={() => void model.generateWorkbook()} aria-label={`Generate ${label} file`}>{model.busy === "generate" ? "Generating..." : "Generate file"}</button> : null}
      {model.generated ? <button className="is-primary" type="button" disabled={Boolean(model.busy)} onClick={() => void model.downloadWorkbook()} aria-label={`Download ${label} file`}>{model.busy === "download" ? "Downloading..." : "Download"}</button> : null}
    </div>
  </article>;
}
