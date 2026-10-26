import { useEffect, useRef, useState } from "react";
import { applyReportFacts, previewReportFacts, type FactPreview, type ReportAuthoringState } from "../../api/reportAuthoring";

export function ReportFactUpdates({ projectId, state, disabled, onChanged }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean; onChanged: (state: ReportAuthoringState) => void;
}) {
  const [preview, setPreview] = useState<FactPreview | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<string[] | null>(null);
  const epoch = useRef(0);
  useEffect(() => { epoch.current += 1; setPreview(null); setSelected(null); setError(""); setBusy(false);
    return () => { epoch.current += 1; }; }, [projectId, state.revision]);
  const output = state.outputs[state.outputs.length - 1];
  const candidates = state.mappings.filter(item => item.status === "confirmed" && item.report_text && ["identity", "specification"].includes(item.kind));
  const chosen = selected ?? candidates.map(item => item.mapping_id);
  async function perform(apply: boolean) {
    if (!output) return;
    const request = ++epoch.current; setBusy(true); setError("");
    try {
      if (apply && preview) {
        const result = await applyReportFacts(projectId, output.output_id, preview.mapping_ids, state.revision, preview.preview_sha256);
        if (request === epoch.current) { onChanged(result); setPreview(null); }
      } else {
        const result = await previewReportFacts(projectId, output.output_id, chosen, state.revision);
        if (request === epoch.current) setPreview(result);
      }
    } catch (reason) { if (request === epoch.current) setError(reason instanceof Error ? reason.message : "Unable to prepare fact updates."); }
    finally { if (request === epoch.current) setBusy(false); }
  }
  return <section aria-label="Confirmed report text updates">
    {candidates.length > 0 && <fieldset disabled={disabled || busy}><legend>Text updates for this copy</legend>
      {candidates.map(item => <label key={item.mapping_id}><input type="checkbox" checked={chosen.includes(item.mapping_id)} onChange={event => {
        setSelected(event.target.checked ? [...chosen, item.mapping_id] : chosen.filter(id => id !== item.mapping_id)); setPreview(null);
      }} />{item.label}: {item.report_text} → {item.value}</label>)}
    </fieldset>}
    <button type="button" disabled={disabled || busy || !output || !chosen.length} onClick={() => void perform(false)}>Preview confirmed text replacements</button>
    {error && <p role="alert">{error}</p>}
    {preview && <div>
      <p>Only these exact text fragments change. Fixed wording and unrelated report parts remain.</p>
      <ul>{preview.changes.map(change => <li key={change.old}>{change.old} → {change.new} ({change.occurrences} occurrences)</li>)}</ul>
      {!preview.changes.length && <p>These unchanged confirmed mappings are already applied. No new report version is needed.</p>}
      <button type="button" disabled={disabled || busy || !preview.changes.length} onClick={() => void perform(true)}>Apply to a new working copy</button>
      <button type="button" disabled={busy} onClick={() => setPreview(null)}>Cancel</button>
    </div>}
  </section>;
}
