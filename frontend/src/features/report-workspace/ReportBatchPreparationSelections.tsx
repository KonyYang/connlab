import type { ReportAuthoringState, ReportPhotoSlot, ResultTargets } from '../../api/reportAuthoring';
import type { ReportAssemblyPhoto, ReportAssemblyResult, ReportLlcrDataset } from '../../api/reportAuthoringBatch';

export type ResultChoice = { selected: boolean; row: string; appendix: string; title: string;
  destination: 'automatic' | 'appendix' | 'region'; start: string; end: string; regionConfirmed: boolean };
export function initialResultChoice(targets?: ResultTargets): ResultChoice {
  return { selected: false, row: targets?.result_rows.length === 1 ? '0' : '', appendix: '', title: '',
    destination: targets?.unreconciled_temperature_evidence ? 'region' : targets?.result_rows.length === 1 ? 'automatic' : 'appendix',
    start: '', end: '', regionConfirmed: false };
}
export function selectedResultRequest(resultId: string, choice: ResultChoice, targets?: ResultTargets): ReportAssemblyResult | null {
  const row = targets?.result_rows[Number(choice.row)];
  if (!choice.selected || choice.row === '' || !row) return null;
  if (choice.destination === 'automatic') return targets?.result_rows.length === 1 && !targets.unreconciled_temperature_evidence ? { result_id: resultId } : null;
  if (choice.destination === 'region') {
    if (!choice.regionConfirmed || choice.start === '' || choice.end === '' || Number(choice.start) > Number(choice.end)) return null;
    return { result_id: resultId, result_table: row.table_index, result_row: row.row_index, appendix_table: null, appendix_title: '',
      evidence_start: Number(choice.start), evidence_end: Number(choice.end), evidence_selection_confirmed: true };
  }
  if (!choice.appendix || !choice.title.trim()) return null;
  return { result_id: resultId, result_table: row.table_index, result_row: row.row_index,
    appendix_table: choice.appendix === 'new' ? null : Number(choice.appendix), appendix_title: choice.title.trim() };
}

export function ReportBatchPreparationSelections({ state, mappingIds, onMappings, choices, targets, targetErrors,
  onResult, slots, assignments, onPhoto, llcr, disabled }: {
  state: ReportAuthoringState; mappingIds: string[]; onMappings: (ids: string[]) => void;
  choices: Record<string, ResultChoice>; targets: Record<string, ResultTargets>; targetErrors: Record<string, string>;
  onResult: (id: string, choice: ResultChoice) => void; slots: ReportPhotoSlot[];
  assignments: Record<string, ReportAssemblyPhoto>; onPhoto: (slotId: string, assignment: ReportAssemblyPhoto | null) => void;
  llcr: { dataset: ReportLlcrDataset | null; unavailableReason: string; selectedId: string; onSelect: (id: string) => void };
  disabled: boolean;
}) {
  const facts = state.mappings.filter(mapping => mapping.status === 'confirmed' && mapping.report_text && ['identity', 'specification'].includes(mapping.kind));
  const photos = state.sources.filter(source => source.role === 'photo');
  return <fieldset disabled={disabled} className="report-batch-selection"><legend>Select updates for one working copy</legend>
    <p>Only selected, confirmed facts and source-backed results are used. Outcomes stay as recorded; pending never becomes Pass.</p>
    <fieldset className="report-batch-result"><legend>Existing LLCR dataset</legend>
      {llcr.dataset ? <>
        <label className="report-batch-check"><input type="checkbox" aria-label="Include current LLCR dataset"
          checked={llcr.selectedId === llcr.dataset.dataset_id}
          onChange={event => llcr.onSelect(event.target.checked ? llcr.dataset!.dataset_id : '')} />
          <span>Include current LLCR dataset — revision {llcr.dataset.revision}</span></label>
        <p>{llcr.dataset.source_file_name}</p>
        <p>One dataset updates its result rows and shared Appendix A. Existing measurements are reused without recalculation; this does not edit the dataset or approve pending outcomes.</p>
        <div className="report-batch-table-wrap"><table aria-label="Existing LLCR measurements"><thead><tr><th>Group / Step</th><th>Quantity / stage</th><th>Recorded summary</th><th>Outcome</th></tr></thead>
          <tbody>{llcr.dataset.entries.map(entry => <tr key={entry.entry_id}><td>{entry.group_label} / {entry.step_token}</td>
            <td>{entry.stage_label || entry.stage}</td><td>Min {entry.summary.min}; max {entry.summary.max}; average {entry.summary.average} {entry.summary.unit}</td>
            <td>{entry.outcome === 'not_determined' ? 'pending' : entry.outcome}</td></tr>)}</tbody></table></div>
      </> : <p>{llcr.unavailableReason || 'No reusable LLCR dataset is available. Use the existing LLCR import workflow; other selected updates can continue.'}</p>}
    </fieldset>
    {facts.length > 0 && <div><h5>Confirmed project facts</h5>{facts.map(mapping => <label key={mapping.mapping_id} className="report-batch-check">
      <input type="checkbox" checked={mappingIds.includes(mapping.mapping_id)} onChange={event => onMappings(event.target.checked
        ? [...mappingIds, mapping.mapping_id] : mappingIds.filter(id => id !== mapping.mapping_id))} />
      <span>{mapping.label}: {mapping.report_text} → {mapping.value}<small>{mapping.source_locator}</small></span>
    </label>)}</div>}
    {(state.results || []).map(result => {
      const id = result.result_id; if (!id) return null;
      const target = targets[id]; const choice = choices[id] || initialResultChoice(target);
      const label = `Group ${result.target.group_label} / ${result.target.step_token} / ${result.kind}`;
      function edit(patch: Partial<ResultChoice>) { onResult(id!, { ...choice, ...patch, regionConfirmed: patch.regionConfirmed ?? false }); }
      return <fieldset key={id} className="report-batch-result"><legend>{label}</legend>
        <label className="report-batch-check"><input type="checkbox" aria-label={`Include ${label}`} checked={choice.selected}
          disabled={!target || !!targetErrors[id]} onChange={event => edit({ selected: event.target.checked })} />
          <span>Include result — {result.data.quantity}; outcome: {result.outcome}</span></label>
        <p>Source: {state.sources.find(source => source.source_id === result.source_id)?.file_name || result.source_id}
          {result.data.sheet_name && ` — ${result.data.sheet_name}`}<small>Retained result: {id}</small></p>
        {result.data.summary && <p>Confirmed summary: min {result.data.summary.min}, max {result.data.summary.max}, average {result.data.summary.average} {result.data.unit}.</p>}
        {targetErrors[id] && <p role="alert">{targetErrors[id]}</p>}
        {choice.selected && target && <div className="report-batch-fields">
          <label>Evidence destination<select value={choice.destination}
            onChange={event => edit({ destination: event.target.value as ResultChoice['destination'] })}>
            {target.result_rows.length === 1 && !target.unreconciled_temperature_evidence && <option value="automatic">Automatic matching — inspect exact placement in preview</option>}
            {!!target.evidence_blocks?.length && <option value="region">Replace existing temperature evidence region</option>}
            <option value="appendix">Choose appendix destination</option>
          </select></label>
          {choice.destination === 'automatic' ? <p>One exact Group / Step row matches. The preview will allocate an unused appendix identifier and show the destination before generation.</p> : <>
          <label>Report result row<select value={choice.row} onChange={event => edit({ row: event.target.value })}>
            <option value="">Choose matching row</option>{target.result_rows.map((row, index) => <option key={index} value={index}>Step {row.step}: {row.test_item} (table {row.table_index}, row {row.row_index})</option>)}
          </select></label>
          {!target.result_rows.length && <p role="alert">No matching result row. Keep this item pending until its report location is corrected.</p>}
          {target.unreconciled_temperature_evidence && <p className="report-batch-wide">This Group contains old temperature evidence. Select its complete table, curve and associated conclusion; an appended table alone does not clear old evidence.</p>}
          {choice.destination === 'region' ? <>
            <label>First evidence block<select value={choice.start} onChange={event => edit({ start: event.target.value })}>
              <option value="">Choose start</option>{target.evidence_blocks?.map(block => <option key={block.block_index} value={block.block_index} disabled={block.protected_other_step}>
                {block.block_index}: {block.kind} — {block.text.slice(0, 90) || `${block.drawing_count} images`}</option>)}
            </select></label>
            <label>Last evidence block<select value={choice.end} onChange={event => edit({ end: event.target.value })}>
              <option value="">Choose end</option>{target.evidence_blocks?.map(block => <option key={block.block_index} value={block.block_index} disabled={block.protected_other_step}>
                {block.block_index}: {block.kind} — {block.text.slice(0, 90) || `${block.drawing_count} images`}</option>)}
            </select></label>
            {choice.start !== '' && choice.end !== '' && <ul className="report-batch-wide">{target.evidence_blocks?.filter(block => block.block_index >= Number(choice.start) && block.block_index <= Number(choice.end))
              .map(block => <li key={block.block_index}>Block {block.block_index}: {block.text || '(no text)'} ({block.drawing_count} images)</li>)}</ul>}
            <label className="report-batch-check report-batch-wide"><input type="checkbox" checked={choice.regionConfirmed}
              onChange={event => edit({ regionConfirmed: event.target.checked })} />I checked the complete old evidence region; setup photos and other Groups are excluded</label>
          </> : <><label>Appendix destination<select value={choice.appendix} onChange={event => edit({ appendix: event.target.value,
              title: target.appendix_tables.find(item => String(item.table_index) === event.target.value)?.title || '' })}>
              <option value="">Choose explicitly</option><option value="new">Add a new appendix</option>
              {target.appendix_tables.map(item => <option key={item.table_index} value={item.table_index}>{item.title} — {item.headers.join(' / ')}</option>)}
            </select></label><label>Appendix identifier<input value={choice.title} placeholder="Appendix C" onChange={event => edit({ title: event.target.value })} /></label></>}
          </>}
        </div>}
      </fieldset>;
    })}
    {slots.length > 0 && <details className="report-batch-section"><summary>Photo assignments — {Object.keys(assignments).length} selected</summary>
      <p>Preserve captions and slot dimensions. Verify the generated Word copy before delivery; source images do not show Word cropping.</p>
      {slots.map((slot, index) => {
        const assignment = assignments[slot.slot_id];
        const transformed = slot.rotation !== 0 || slot.flip_horizontal || slot.flip_vertical;
        return <fieldset className="report-batch-result" key={slot.slot_id} disabled={!slot.supported}><legend>Photo {index + 1}: {slot.caption || 'Uncaptioned slot'}</legend>
          {!slot.supported && <p>{slot.reason}</p>}
          <div className="report-batch-fields"><label>Replacement photo<select value={assignment?.source_id || ''} onChange={event => onPhoto(slot.slot_id,
            event.target.value ? { slot_id: slot.slot_id, source_id: event.target.value, crop_mode: 'preserve', accept_slot_transform: false } : null)}>
            <option value="">Leave unchanged</option>{photos.map(source => <option key={source.source_id} value={source.source_id}>{source.file_name}</option>)}
          </select></label>
          {assignment && <><label>Photo fit<select value={assignment.crop_mode} onChange={event => onPhoto(slot.slot_id, { ...assignment, crop_mode: event.target.value as ReportAssemblyPhoto['crop_mode'] })}>
            <option value="preserve">Keep approved crop; matching aspect ratio</option><option value="centre_crop">Centre-crop without stretching</option></select></label>
            <p className="report-batch-wide">Slot: {(slot.width_emu / 360000).toFixed(1)} × {(slot.height_emu / 360000).toFixed(1)} cm; rotation {slot.rotation / 60000}°; horizontal flip {String(slot.flip_horizontal)}; vertical flip {String(slot.flip_vertical)}.</p>
            {transformed && <label className="report-batch-check report-batch-wide"><input type="checkbox" checked={assignment.accept_slot_transform}
              onChange={event => onPhoto(slot.slot_id, { ...assignment, accept_slot_transform: event.target.checked })} />I accept this slot's existing rotation and flips for this photo</label>}
          </>}</div>
        </fieldset>;
      })}
    </details>}
    {!facts.length && !state.results?.length && !photos.length && !llcr.dataset && <p>No confirmed updates yet. Retain evidence and confirm its project mapping above or import a reviewed Tools package below.</p>}
  </fieldset>;
}
