import { useEffect, useRef, useState } from 'react';
import { applyReportResult, getReportResultTargets, type ReportAuthoringState, type ResultTargets } from '../../api/reportAuthoring';

export function ReportResultUpdate({ projectId, state, disabled, onChanged }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean; onChanged: (state: ReportAuthoringState) => void;
}) {
  const [resultId, setResultId] = useState('');
  const [targets, setTargets] = useState<ResultTargets | null>(null);
  const [row, setRow] = useState(-1);
  const [appendix, setAppendix] = useState('');
  const [title, setTitle] = useState('');
  const [destination, setDestination] = useState<'appendix' | 'region'>('appendix');
  const [regionStart, setRegionStart] = useState('');
  const [regionEnd, setRegionEnd] = useState('');
  const [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const epoch = useRef(0);
  const output = state.outputs.at(-1);
  useEffect(() => { epoch.current++; setTargets(null); setConfirmed(false); setBusy(false); }, [projectId, state.revision]);
  useEffect(() => () => { epoch.current++; }, []);
  async function inspect() {
    if (!output || !resultId) return;
    const token = ++epoch.current; setBusy(true); setError(''); setConfirmed(false);
    try { const result = await getReportResultTargets(projectId, output.output_id, resultId, state.revision);
      if (token === epoch.current) { setTargets(result); setRow(result.result_rows.length === 1 ? 0 : -1); setAppendix(''); setTitle('');
        setDestination(result.unreconciled_temperature_evidence ? 'region' : 'appendix'); setRegionStart(''); setRegionEnd(''); }
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Unable to inspect report locations.'); }
    finally { if (token === epoch.current) setBusy(false); }
  }
  async function update() {
    if (!output || !targets || row < 0 || !confirmed) return;
    const token = ++epoch.current; setBusy(true); setError('');
    try { const updated = await applyReportResult(projectId, { expected_revision: state.revision, output_id: output.output_id,
      output_sha256: targets.output_sha256, result_id: targets.result_id,
      result_table: targets.result_rows[row].table_index, result_row: targets.result_rows[row].row_index,
      appendix_table: destination === 'region' || appendix === 'new' ? null : Number(appendix), appendix_title: destination === 'region' ? '' : title,
      evidence_start: destination === 'region' ? Number(regionStart) : null, evidence_end: destination === 'region' ? Number(regionEnd) : null,
      evidence_selection_confirmed: destination === 'region' && confirmed });
      if (token === epoch.current) onChanged(updated);
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Unable to update the report copy.'); }
    finally { if (token === epoch.current) setBusy(false); }
  }
  if (!output || !state.results?.length) return null;
  return <section aria-label="Update confirmed report results"><h4>Update results in the report copy</h4>
    <fieldset disabled={disabled || busy}>
      <label>Confirmed measurements <select value={resultId} onChange={event => { setResultId(event.target.value); setTargets(null); }}>
        <option value="">Select result</option>{state.results.map(result => <option key={result.result_id} value={result.result_id}>
          Group {result.target.group_label} / {result.target.step_token} / {result.kind} / {result.data.quantity}</option>)}
      </select></label>
      <button type="button" disabled={!resultId} onClick={() => void inspect()}>Inspect report destinations</button>
      {targets && <>
        <label>Report result row <select value={row} onChange={event => { setRow(Number(event.target.value)); setConfirmed(false); }}>
          <option value={-1}>Choose matching row</option>{targets.result_rows.map((item, index) => <option key={index} value={index}>Step {item.step}: {item.test_item}</option>)}
        </select></label>
        {!targets.result_rows.length && <p role="alert">No matching Group/Step result row. Correct the report mapping first; no contents were changed.</p>}
        {!!targets.evidence_blocks?.length && <label>Measurement evidence destination <select value={destination} onChange={event => { setDestination(event.target.value as typeof destination); setConfirmed(false); }}>
          <option value="region">Replace existing temperature evidence region</option><option value="appendix">Appendix table</option>
        </select></label>}
        {targets.unreconciled_temperature_evidence && <p role="alert">Old temperature evidence remains in this Group. Select the complete old table, curve and associated conclusion; adding an appendix alone will not permit customer conversion.</p>}
        {destination === 'region' ? <>
          <p>Only the explicitly selected blocks are replaced in a new copy. Setup photos and the next Group must remain outside the selection. No new current-rating conclusion is inferred.</p>
          <label>First evidence block <select value={regionStart} onChange={event => { setRegionStart(event.target.value); setConfirmed(false); }}>
            <option value="">Choose start</option>{targets.evidence_blocks?.map(block => <option key={block.block_index} value={block.block_index} disabled={block.protected_other_step}>
              {block.block_index}: {block.kind} — {block.text.slice(0, 80) || `${block.drawing_count} image/object(s)`}</option>)}
          </select></label>
          <label>Last evidence block <select value={regionEnd} onChange={event => { setRegionEnd(event.target.value); setConfirmed(false); }}>
            <option value="">Choose end</option>{targets.evidence_blocks?.map(block => <option key={block.block_index} value={block.block_index} disabled={block.protected_other_step}>
              {block.block_index}: {block.kind} — {block.text.slice(0, 80) || `${block.drawing_count} image/object(s)`}</option>)}
          </select></label>
          {regionStart !== '' && regionEnd !== '' && <ul aria-label="Selected evidence blocks">{targets.evidence_blocks?.filter(block => block.block_index >= Number(regionStart) && block.block_index <= Number(regionEnd)).map(block => <li key={block.block_index}>
            Block {block.block_index} ({block.kind}, {block.drawing_count} image/object(s)): {block.text || '(no text)'}</li>)}</ul>}
        </> : <><label>Appendix destination <select value={appendix} onChange={event => { setAppendix(event.target.value); setConfirmed(false);
          setTitle(targets.appendix_tables.find(item => String(item.table_index) === event.target.value)?.title || ''); }}>
          <option value="">Choose explicitly</option><option value="new">Add a new appendix</option>
          {targets.appendix_tables.map(item => <option key={item.table_index} value={item.table_index}>{item.title} — {item.headers.join(' / ')}</option>)}
        </select></label>
        <label>Appendix identifier (for example Appendix C)<input value={title} onChange={event => { setTitle(event.target.value); setConfirmed(false); }} /></label>
        <p>The title is generated from the confirmed measurement type and colors; old Mating/Orange labels are not reused for different results.</p>
        </>}
        <p>The selected result cells and {destination === 'region' ? 'complete evidence region' : 'appendix table'} will be replaced in a new copy. Unrelated content is retained. Pending outcomes leave Comment blank.</p>
        <label><input type="checkbox" checked={confirmed} onChange={event => setConfirmed(event.target.checked)} />{destination === 'region'
          ? 'I checked the result row and complete old temperature evidence region, including table, curve and conclusion'
          : 'I checked the result row, appendix, title and measurement meaning'}</label>
        <button type="button" disabled={!confirmed || row < 0 || (destination === 'region'
          ? regionStart === '' || regionEnd === '' || Number(regionStart) > Number(regionEnd)
          : !appendix || !title.trim())} onClick={() => void update()}>Update report copy</button>
      </>}
    </fieldset>{error && <p role="alert">{error}</p>}
  </section>;
}
