import { useEffect, useRef, useState } from 'react';
import { getReportPhotoSlots, getReportResultTargets, type ReportAuthoringState, type ReportPhotoSlot,
  type ReportSourceRole, type ResultTargets } from '../../api/reportAuthoring';
import { applyReportAssembly, getReportCoverage, getReportInventory, previewReportAssembly, retainReportInventory,
  type ReportAssemblyPhoto, type ReportAssemblyRequest, type ReportCoverage, type ReportInventory } from '../../api/reportAuthoringBatch';
import { ReportBatchPreparationInventory } from './ReportBatchPreparationInventory';
import { initialResultChoice, restoreResultChoice, ReportBatchPreparationSelections, selectedResultRequest, type ResultChoice } from './ReportBatchPreparationSelections';
import './ReportBatchPreparation.css';

type ReadResult<T> = { value: T; error?: never } | { value?: never; error: string };
async function read<T>(request: Promise<T>): Promise<ReadResult<T>> {
  try { return { value: await request }; }
  catch (cause) { return { error: cause instanceof Error ? cause.message : 'Inspection failed. Retry after resolving the issue.' }; }
}

export function ReportBatchPreparation({ projectId, state, disabled, onChanged, beginOperation }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean;
  onChanged: (state: ReportAuthoringState) => void; beginOperation?: () => (() => void) | null;
}) {
  const [inventory, setInventory] = useState<ReportInventory | null>(null);
  const [coverage, setCoverage] = useState<ReportCoverage | null>(null);
  const [retainedSelection, setRetainedSelection] = useState<Record<string, ReportSourceRole>>({});
  const [targets, setTargets] = useState<Record<string, ResultTargets>>({});
  const [targetErrors, setTargetErrors] = useState<Record<string, string>>({});
  const [slots, setSlots] = useState<ReportPhotoSlot[]>([]);
  const [choices, setChoices] = useState<Record<string, ResultChoice>>({});
  const [mappingIds, setMappingIds] = useState<string[]>([]);
  const [llcrDatasetId, setLlcrDatasetId] = useState('');
  const [usePhotoPlan, setUsePhotoPlan] = useState(false);
  const [renumberFigures, setRenumberFigures] = useState(false);
  const [assignments, setAssignments] = useState<Record<string, ReportAssemblyPhoto>>({});
  const [inspected, setInspected] = useState(false);
  const [readErrors, setReadErrors] = useState<string[]>([]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [draftChanged, setDraftChanged] = useState(false);
  const epoch = useRef(0);
  const releaseCurrent = useRef<(() => void) | null>(null);
  const identity = `${projectId}/${state.revision}`;
  const currentIdentity = useRef(identity); currentIdentity.current = identity;
  const output = state.outputs.at(-1);
  const plan = state.assembly_plan;
  const planMatches = !!plan && plan.base_output_id === output?.output_id && plan.output_sha256 === output?.artifact?.sha256;
  const locked = disabled || busy;

  useEffect(() => {
    epoch.current++; releaseCurrent.current?.(); releaseCurrent.current = null;
    setInventory(null); setCoverage(null); setRetainedSelection({}); setTargets({}); setTargetErrors({}); setSlots([]);
    setChoices({}); setMappingIds([]); setLlcrDatasetId(''); setAssignments({}); setInspected(false); setReadErrors([]); setError('');
    setBusy(false); setConfirmed(false); setDraftChanged(false);
    setUsePhotoPlan(false); setRenumberFigures(false);
  }, [identity]);
  useEffect(() => () => { epoch.current++; releaseCurrent.current?.(); }, []);

  async function run(operation: (isCurrent: () => boolean) => Promise<void>) {
    if (locked || releaseCurrent.current || currentIdentity.current !== identity || state.project_id !== projectId) return;
    const outside = beginOperation ? beginOperation() : () => undefined; if (!outside) return;
    let released = false;
    const release = () => { if (released) return; released = true; outside(); if (releaseCurrent.current === release) releaseCurrent.current = null; };
    releaseCurrent.current = release;
    const token = ++epoch.current;
    const isCurrent = () => token === epoch.current && identity === currentIdentity.current;
    setBusy(true); setError('');
    try { await operation(isCurrent); }
    catch (cause) { if (isCurrent()) setError(cause instanceof Error ? cause.message : 'Report batch preparation failed. No original was changed.'); }
    finally { release(); if (isCurrent()) setBusy(false); }
  }

  async function inspect(restorePreview = false) {
    await run(async isCurrent => {
      setConfirmed(false);
      setDraftChanged(true);
      const [scan, cover, photo, resultReads] = await Promise.all([
        read(getReportInventory(projectId)), read(getReportCoverage(projectId)),
        output ? read(getReportPhotoSlots(projectId, output.output_id, state.revision)) : Promise.resolve(null),
        Promise.all((output ? state.results || [] : []).filter(result => !!result.result_id).map(async result => ({
          id: result.result_id!, response: await read(getReportResultTargets(projectId, output!.output_id, result.result_id!, state.revision)),
        }))),
      ]);
      if (!isCurrent()) return;
      const errors: string[] = [];
      setInventory(scan.value || null); if (scan.error) errors.push(`Materials: ${scan.error}`);
      setCoverage(cover.value || null); if (cover.error) errors.push(`Coverage: ${cover.error}`);
      const nextTargets: Record<string, ResultTargets> = {}; const nextErrors: Record<string, string> = {};
      const usable = cover.value ? new Set(cover.value.rows.flatMap(row => row.usable_result_ids)) : null;
      for (const result of resultReads) {
        if (result.response.error) nextErrors[result.id] = result.response.error;
        else if (result.response.value?.output_sha256 !== output?.artifact?.sha256) nextErrors[result.id] = 'Working copy changed. Reload saved evidence and inspect again.';
        else if (usable && !usable.has(result.id)) nextErrors[result.id] = 'Source or Matrix mapping needs review before this result can be assembled.';
        else if (result.response.value) nextTargets[result.id] = result.response.value;
      }
      setTargets(nextTargets); setTargetErrors(nextErrors);
      const saved = restorePreview && planMatches && plan?.status === 'prepared' ? plan.request : null;
      setChoices(Object.fromEntries(Object.entries(nextTargets).map(([id, target]) => {
        const selection = saved?.results.find(item => item.result_id === id);
        return [id, selection ? restoreResultChoice(selection, target) : initialResultChoice(target)];
      })));
      if (saved?.results.some(item => !nextTargets[item.result_id])) errors.push('Some saved result locations cannot be restored. Resolve their inspection errors; these results remain unselected.');
      if (photo?.error) errors.push(`Photo slots: ${photo.error}`);
      const validPhoto = photo?.value?.output_sha256 === output?.artifact?.sha256;
      if (photo?.value && !validPhoto) errors.push('Photo slots no longer match the working copy. Reload saved evidence.');
      setSlots(validPhoto ? photo?.value?.slots || [] : []);
      setReadErrors(errors); setRetainedSelection({}); setMappingIds(saved?.mapping_ids || []); setLlcrDatasetId(saved?.llcr_dataset_id || '');
      setAssignments(Object.fromEntries((saved?.assignments || []).map(item => [item.slot_id, item])));
      setUsePhotoPlan(!!saved?.photo_plan_id); setRenumberFigures(!!saved?.renumber_figures); setInspected(true);
    });
  }

  async function retain() {
    if (!inventory?.root_token) return;
    const items = inventory.items.flatMap(item => item.status === 'candidate' && item.file_token && retainedSelection[item.relative_path]
      ? [{ relative_path: item.relative_path, file_token: item.file_token, role: retainedSelection[item.relative_path] }] : []);
    if (!items.length) return;
    await run(async isCurrent => {
      const next = await retainReportInventory(projectId, { expected_revision: state.revision, root_token: inventory.root_token!, items });
      if (isCurrent() && next.project_id === projectId) onChanged(next);
    });
  }

  function changed() { setConfirmed(false); setDraftChanged(true); }
  const selectedResults = Object.entries(choices).filter(([, choice]) => choice.selected);
  const selectedRequests = selectedResults.map(([id, choice]) => selectedResultRequest(id, choice, targets[id]));
  const invalidResult = selectedRequests.some(request => request === null);
  const invalidPhoto = Object.values(assignments).some(assignment => {
    const slot = slots.find(item => item.slot_id === assignment.slot_id);
    return !slot?.supported || ((slot.rotation !== 0 || slot.flip_horizontal || slot.flip_vertical) && !assignment.accept_slot_transform);
  });
  const hasSelection = mappingIds.length + selectedResults.length + Object.keys(assignments).length > 0 || !!llcrDatasetId || usePhotoPlan || renumberFigures;
  const invalidLlcr = !!llcrDatasetId && coverage?.llcr_dataset?.dataset_id !== llcrDatasetId;
  const previewReady = inspected && !!output?.artifact?.sha256 && hasSelection && !invalidResult && !invalidPhoto && !invalidLlcr;

  async function preview() {
    if (!previewReady || !output?.artifact?.sha256) return;
    const request: ReportAssemblyRequest = { expected_revision: state.revision, output_id: output.output_id,
      output_sha256: output.artifact.sha256, mapping_ids: mappingIds,
      results: selectedRequests.filter((item): item is NonNullable<typeof item> => item !== null), assignments: Object.values(assignments),
      ...(usePhotoPlan && output.photo_plan ? { photo_plan_id: output.photo_plan.plan_id } : {}),
      ...(renumberFigures ? { renumber_figures: true } : {}),
      ...(llcrDatasetId ? { llcr_dataset_id: llcrDatasetId } : {}) };
    await run(async isCurrent => {
      const next = await previewReportAssembly(projectId, request);
      if (isCurrent() && next.project_id === projectId) onChanged(next);
    });
  }

  async function apply() {
    if (!plan || plan.status !== 'prepared' || !plan.can_apply || !planMatches || !confirmed || draftChanged) return;
    await run(async isCurrent => {
      const next = await applyReportAssembly(projectId, { expected_revision: state.revision,
        plan_id: plan.plan_id, preview_sha256: plan.preview_sha256 });
      if (isCurrent() && next.project_id === projectId) onChanged(next);
    });
  }

  return <section className="report-batch" aria-label="Prepare report batch">
    <h4>Prepare report batch</h4>
    <p>Inspect project materials and gaps, select updates, then preview one batch. A single new working copy is produced; original and official reports stay unchanged.</p>
    <button type="button" disabled={locked} onClick={() => void inspect()}>Inspect materials and coverage</button>
    {busy && <p role="status">Preparing report batch…</p>}
    {error && <p role="alert">{error}</p>}
    {readErrors.map((message, index) => <p role="alert" key={index}>{message}</p>)}
    <ReportBatchPreparationInventory inventory={inventory} coverage={coverage} selected={retainedSelection} disabled={locked}
      onSelect={(path, role) => setRetainedSelection(previous => { const next = { ...previous }; if (role) next[path] = role; else delete next[path]; return next; })}
      onRetain={() => void retain()} />
    {inspected && !output && <p>Choose a report base before preparing content updates. Retained material copies remain available.</p>}
    {inspected && output && <>
      {output.photo_plan && <label className="report-batch-check"><input type="checkbox" checked={usePhotoPlan} disabled={locked || Object.keys(assignments).length > 0}
        onChange={event => { changed(); setUsePhotoPlan(event.target.checked); }} />Use saved confirmed photo mapping ({output.photo_plan.assignments.length} slots)</label>}
      <label className="report-batch-check"><input type="checkbox" checked={renumberFigures} disabled={locked}
        onChange={event => { changed(); setRenumberFigures(event.target.checked); }} />Renumber supported photo captions and exact references in visible order</label>
      <p>Inspect the figure preview in Approved original, photos and Word preview. Ambiguous floating order and field references stay pending.</p>
      <ReportBatchPreparationSelections state={state} mappingIds={mappingIds} onMappings={ids => { changed(); setMappingIds(ids); }}
        choices={choices} targets={targets} targetErrors={targetErrors} slots={slots} assignments={assignments} disabled={locked}
        llcr={{ dataset: coverage?.llcr_dataset || null, unavailableReason: coverage?.llcr_unavailable_reason || '', selectedId: llcrDatasetId,
          onSelect: id => { changed(); setLlcrDatasetId(id); } }}
        onResult={(id, choice) => { changed(); setChoices(previous => ({ ...previous, [id]: choice })); }}
        onPhoto={(id, assignment) => { changed(); setUsePhotoPlan(false); setAssignments(previous => { const next = { ...previous }; if (assignment) next[id] = assignment; else delete next[id]; return next; }); }} />
      {invalidResult && <p role="status">Choose the result location and complete evidence destination for each selected result.</p>}
      {invalidLlcr && <div role="status"><p>The saved LLCR dataset is no longer available as the current dataset. Select the current dataset explicitly, or leave that update pending.</p>
        <button type="button" disabled={locked} onClick={() => { changed(); setLlcrDatasetId(''); }}>Leave the saved LLCR update out</button></div>}
      {invalidPhoto && <p role="status">Review the selected photo slot and its rotation/flips before previewing.</p>}
      <button type="button" disabled={locked || !previewReady} onClick={() => void preview()}>Preview selected updates</button>
    </>}
    {plan && <section className="report-batch-plan" aria-label="Saved batch preview"><h5>Saved batch preview</h5>
      {plan.status === 'completed' ? <p role="status">This batch already produced a working copy. Inspect again to prepare a different batch; do not replay completed updates.</p> : <>
        <button type="button" disabled={locked || !planMatches} onClick={() => void inspect(true)}>Edit result and appendix locations</button>
        <p>Reopen the saved selections against this working copy. Preview again after editing; the old confirmation cannot generate changed selections.</p>
        <p>Base: {output?.file_name || plan.base_output_id}. {plan.changes.length} selected change(s). This is a review copy, not a complete-report or Pass declaration.</p>
        <ul>{plan.changes.map((change, index) => <li key={index}>{change.label}</li>)}</ul>
        {!!plan.document_plan?.facts.length && <div className="report-batch-table-wrap"><table aria-label="Exact fact replacements"><thead><tr><th>Existing text</th><th>Replacement</th><th>Occurrences / locations</th></tr></thead>
          <tbody>{plan.document_plan.facts.map((fact, index) => <tr key={index}><td>{fact.old}</td><td>{fact.new}</td><td>{fact.occurrences} — {fact.parts.join(', ')}</td></tr>)}</tbody></table></div>}
        {!!plan.document_plan?.results.length && <div className="report-batch-table-wrap"><table aria-label="Resolved batch result locations"><thead><tr><th>Result</th><th>Word row</th><th>Existing result / comment</th><th>New result / comment</th><th>Evidence destination</th></tr></thead>
          <tbody>{plan.document_plan.results.map(item => <tr key={item.result_id}><td>{plan.changes.find(change => change.result_id === item.result_id)?.label || item.result_id}</td>
            <td>{item.target ? `Table ${item.target.result_table}, row ${item.target.result_row}` : 'Needs review'}</td>
            <td>{item.current_result === undefined ? 'Not recorded in this preview' : item.current_result || '—'}<small>Comment: {item.current_comment === undefined ? 'Not recorded in this preview' : item.current_comment || '—'}</small></td>
            <td>{item.new_result === undefined ? 'Not recorded in this preview' : item.new_result || '—'}<small>Comment: {item.new_comment === undefined ? 'Not recorded in this preview' : item.new_comment || '—'}</small></td>
            <td>{item.target?.evidence_start != null ? `Evidence blocks ${item.target.evidence_start}–${item.target.evidence_end}` : item.target?.appendix_title
              ? item.target.appendix_table != null ? `Update existing ${item.target.appendix_title} (table ${item.target.appendix_table})` : `Add new ${item.target.appendix_title}` : 'Needs review'}</td></tr>)}</tbody></table></div>}
        {plan.document_plan?.llcr && <section aria-label="LLCR batch preview"><h5>LLCR dataset revision {plan.document_plan.llcr.revision}</h5>
          <p>Appendix A: {plan.document_plan.llcr.appendix.action} — {plan.document_plan.llcr.appendix.summary_rows} summary rows. No measurement recalculation.</p>
          <div className="report-batch-table-wrap"><table aria-label="LLCR exact result changes"><thead><tr><th>Group / Step / Word row</th><th>Requirement</th><th>Existing result / comment</th><th>New result / comment</th></tr></thead>
            <tbody>{plan.document_plan.llcr.rows.map(row => <tr key={row.result_id}><td>Group {row.group_label} / {row.step_token}<small>Table {row.table_index}, row {row.row_index}{row.changed ? '' : ' — unchanged'}</small></td>
              <td>{row.requirement || '—'}</td><td>{row.current_result || '—'}<small>Comment: {row.current_comment || '—'}</small></td>
              <td>{row.new_result || '—'}<small>Comment: {row.new_comment || '—'}</small></td></tr>)}</tbody></table></div>
        </section>}
        {plan.request.assignments.length > 0 && <div className="report-batch-table-wrap"><table aria-label="Batch photo assignments"><thead><tr><th>Retained photo</th><th>Slot</th><th>Fit / orientation</th></tr></thead>
          <tbody>{plan.request.assignments.map(item => <tr key={item.slot_id}><td>{state.sources.find(source => source.source_id === item.source_id)?.file_name || item.source_id}</td>
            <td>{item.slot_id}</td><td>{item.crop_mode === 'preserve' ? 'Preserve approved crop' : 'Centre-crop without stretching'}; rotation/flips {item.accept_slot_transform ? 'accepted' : 'not authorized'}</td></tr>)}</tbody></table></div>}
        {plan.issues.length > 0 && <div role={plan.can_apply ? 'status' : 'alert'}><h5>{plan.can_apply ? 'Review notes / unresolved decisions' : 'Resolve before generation'}</h5>
          <ul>{plan.issues.map((issue, index) => <li key={index}>{issue}</li>)}</ul></div>}
        {plan.omitted.length > 0 && <div><h5>Not included / still pending</h5><ul>{plan.omitted.map((item, index) => <li key={index}>{item}</li>)}</ul></div>}
        {!planMatches && <p role="alert">Preview no longer matches the selected working copy. Inspect and preview again.</p>}
        {draftChanged && <p role="status">Selections changed. Preview the new selection before generating.</p>}
        <label className="report-batch-check"><input type="checkbox" disabled={locked || !plan.can_apply || !planMatches || draftChanged}
          checked={confirmed} onChange={event => setConfirmed(event.target.checked)} />I checked this batch preview; unresolved items remain pending</label>
        <button type="button" disabled={locked || !confirmed || !plan.can_apply || !planMatches || draftChanged} onClick={() => void apply()}>Generate one working copy</button>
      </>}
    </section>}
  </section>;
}
