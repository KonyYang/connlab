import { useRef } from "react";
import type { ResultDatasetRevision } from "../../api/client";
import { LlcrReadings } from "./LlcrReadings";

type Props = {
  dataset: ResultDatasetRevision | null;
  busy: boolean;
  inspecting: boolean;
  updating: boolean;
  workingCopy: boolean;
  updateBlocked: boolean;
  blocker: string | null;
  onInspect: (file: File) => void;
  onUpdate: () => void;
};

export function LlcrSection({ dataset, busy, inspecting, updating, workingCopy, updateBlocked, blocker, onInspect, onUpdate }: Props) {
  const filePicker = useRef<HTMLInputElement>(null);
  return <div className="llcr-section">
    <h3>LLCR results</h3>
    <input aria-label="LLCR result workbook" type="file" accept=".xlsx" ref={filePicker} hidden disabled={busy}
      onChange={event => {
        const file = event.target.files?.[0];
        event.target.value = "";
        if (file) onInspect(file);
      }} />
    {dataset && <dl className="llcr-source">
      <dt>Source</dt><dd>{dataset.source_file_name}</dd>
      <dt>Report location</dt><dd>LLCR Result and Comment cells and Appendix A</dd>
    </dl>}
    <button type="button" disabled={busy} className={dataset ? "ui-secondary-action" : "primary-action"} onClick={() => filePicker.current?.click()}>
      {inspecting ? "Reading workbook…" : dataset ? "Choose another workbook…" : "Import LLCR workbook…"}
    </button>
    {dataset && <>
      {dataset.readings?.length ? <LlcrReadings readings={dataset.readings} /> :
        <p className="report-workspace-note">This dataset has no saved sample readings. Import its workbook to view them.</p>}
      {blocker && <p className="report-workspace-blocker">{blocker}</p>}
      <button type="button" className="primary-action" disabled={busy || updateBlocked} onClick={onUpdate}>
        {updating ? "Updating…" : workingCopy ? "Update LLCR in working copy" : "Update LLCR Results"}
      </button>
    </>}
  </div>;
}
