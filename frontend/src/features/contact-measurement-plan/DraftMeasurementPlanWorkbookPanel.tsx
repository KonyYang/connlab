import { useEffect } from "react";
import { useDraftMeasurementPlanWorkbookModel } from "./useDraftMeasurementPlanWorkbookModel";

type Props = {
  projectId: string;
  revisionId: string | null;
  disabled: boolean;
  onBusyChange: (busy: boolean) => void;
};

export function DraftMeasurementPlanWorkbookPanel({ projectId, revisionId, disabled, onBusyChange }: Props) {
  const model = useDraftMeasurementPlanWorkbookModel({ projectId, revisionId });
  useEffect(() => onBusyChange(model.busy), [model.busy, onBusyChange]);

  return <section className="contact-measurement-draft-output" aria-label="Draft measurement workbook">
    <header><h3>Draft measurement workbook</h3>{model.preview?.output_label ? <strong>{model.preview.output_label}</strong> : null}</header>
    <p>Uses the current editable Measurement Plan only.</p>
    {model.preview ? <p>{`Plan ${model.preview.revision_sequence ?? "-"}, Matrix ${model.preview.matrix_revision ?? "-"}, ${model.preview.row_count} rows`}</p> : null}
    {model.preview?.preview_fingerprint ? <p>{`Preview ${model.preview.preview_fingerprint.slice(0, 12)}`}</p> : null}
    {model.preview?.diagnostics.map((item) => <p key={item.code} role="status">{item.message}</p>)}
    {model.error ? <p role="alert">{model.error}</p> : null}
    {model.artifact?.cleanup_warning ? <p role="status">{model.artifact.cleanup_warning}</p> : null}
    <div>
      <button type="button" disabled={!revisionId || disabled || model.busy} onClick={() => void model.previewDraft()}>Preview draft workbook</button>
      <button type="button" disabled={!model.preview?.generate_allowed || disabled || model.busy} onClick={() => void model.generateDraft()}>Generate draft workbook</button>
      {model.artifact ? <a href={model.artifact.download_url} download={model.artifact.file_name}>Download {model.artifact.output_label.toLowerCase()} workbook</a> : null}
    </div>
  </section>;
}
