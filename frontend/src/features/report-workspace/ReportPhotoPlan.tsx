import { useEffect, useRef, useState } from 'react';
import { downloadReportArtifact, getReportPhotoImage, type ConfirmedPhotoAssignment, type ReportAuthoringState,
  type ReportDocumentReviewData } from '../../api/reportAuthoring';

export function ReportPhotoPlan({ projectId, state, review, disabled, onConfirm }: {
  projectId: string; state: ReportAuthoringState; review: ReportDocumentReviewData; disabled: boolean;
  onConfirm: (assignments: ConfirmedPhotoAssignment[]) => Promise<void>;
}) {
  const output = state.outputs.at(-1)!;
  const [draft, setDraft] = useState<Record<string, ConfirmedPhotoAssignment>>({});
  const [confirmed, setConfirmed] = useState(false);
  const [images, setImages] = useState<Record<string, string[]>>({});
  const [error, setError] = useState('');
  const [comparing, setComparing] = useState(false);
  const urls = useRef<string[]>([]);
  const epoch = useRef(0);
  useEffect(() => {
    const saved = output.photo_plan?.output_sha256 === review.output_sha256 ? output.photo_plan.assignments : [];
    epoch.current++; urls.current.forEach(url => URL.revokeObjectURL(url)); urls.current = [];
    setDraft(Object.fromEntries(saved.map(item => [item.slot_id, item]))); setConfirmed(false); setImages({}); setComparing(false);
  }, [projectId, review.output_sha256, output.photo_plan?.plan_id]);
  useEffect(() => () => { epoch.current++; urls.current.forEach(url => URL.revokeObjectURL(url)); }, []);
  function update(slot: string, values: Partial<ConfirmedPhotoAssignment>) {
    setConfirmed(false);
    const initial: ConfirmedPhotoAssignment = { slot_id: slot, source_id: '', crop_mode: 'preserve',
      scope: 'step', accept_slot_transform: false, group_id: '', row_id: '', step_token: '', sample_ids: [], stage: '', reason: '', reuse_reason: '',
    };
    setDraft(previous => ({ ...previous, [slot]: { ...(previous[slot] || initial), ...values } }));
    setImages(previous => { const next = { ...previous }; delete next[slot]; return next; });
  }
  const selected = Object.values(draft).filter(item => item.source_id);
  const samePhotoCount = (id: string) => {
    const digest = review.photo_candidates.find(item => item.source_id === id)?.source_sha256;
    return selected.filter(item => digest ? review.photo_candidates.find(candidate => candidate.source_id === item.source_id)?.source_sha256 === digest : item.source_id === id).length;
  };
  const valid = selected.length > 0 && selected.every(item => (item.scope !== 'step' || (item.group_id && item.row_id && item.step_token)) && (item.scope === 'project_context' || item.sample_ids.length)
    && item.stage.trim() && item.reason.trim() && (samePhotoCount(item.source_id) === 1 || item.reuse_reason.trim()));
  async function compare() {
    if (disabled || comparing) return;
    setComparing(true); setError(''); setConfirmed(false);
    const token = ++epoch.current;
    try {
      const next: Record<string, string[]> = {};
      for (const item of selected) {
        const source = state.sources.find(candidate => candidate.source_id === item.source_id)!;
        const [old, replacement] = await Promise.all([getReportPhotoImage(projectId, output.output_id, item.slot_id), downloadReportArtifact(source.download_url)]);
        if (token !== epoch.current) return;
        next[item.slot_id] = [URL.createObjectURL(old.blob), URL.createObjectURL(replacement.blob)];
        urls.current.push(...next[item.slot_id]);
      }
      setImages(next);
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Photo comparison failed.'); }
    finally { if (token === epoch.current) setComparing(false); }
  }
  return <section className="report-photo-plan" aria-label="Batch photo mapping"><h5>Confirm photos once for this working copy</h5>
    <p>Filename matches are suggestions, not identity evidence. Select Group / Step, specimens and stage. This saves decisions only; use Prepare report batch to generate one copy.</p>
    {output.photo_plan && <p role="status">Saved photo mapping: {output.photo_plan.assignments.length} slot(s), confirmed by {output.photo_plan.confirmed_by}.</p>}
    <fieldset disabled={disabled || comparing}>
      {review.slots.map(slot => <details className="report-photo-card" key={slot.slot_id}><summary>{slot.slot_id} — {slot.caption || 'Uncaptioned photograph'} — {slot.coverage}</summary>
        {!slot.supported ? <p>{slot.reason}</p> : <>
          <label>Replacement for {slot.slot_id}<select value={draft[slot.slot_id]?.source_id || ''} onChange={event => update(slot.slot_id, { source_id: event.target.value })}>
            <option value="">Leave this slot unchanged</option>{[...review.photo_candidates].sort((left, right) =>
              (right.suggestions.find(item => item.slot_id === slot.slot_id)?.score || 0) - (left.suggestions.find(item => item.slot_id === slot.slot_id)?.score || 0)).map(candidate => <option key={candidate.source_id} value={candidate.source_id}>
              {candidate.file_name}{candidate.suggestions.find(hint => hint.slot_id === slot.slot_id && hint.score > 0) ? ' — filename hint' : ''}</option>)}</select></label>
          {draft[slot.slot_id]?.source_id && <div className="report-review-fields">
            <label>Scope for {slot.slot_id}<select value={draft[slot.slot_id].scope || 'step'} onChange={event => update(slot.slot_id,
              { scope: event.target.value as ConfirmedPhotoAssignment['scope'], group_id: '', row_id: '', step_token: '' })}>
              <option value="step">Specific test Group / Step</option><option value="sample_overview">Specimen overview</option><option value="project_context">Project / equipment setup</option></select></label>
            {(draft[slot.slot_id].scope || 'step') === 'step' && <label>Group / Step for {slot.slot_id}<select value={JSON.stringify([draft[slot.slot_id].group_id, draft[slot.slot_id].row_id, draft[slot.slot_id].step_token])}
              onChange={event => { const [group_id, row_id, step_token] = JSON.parse(event.target.value) as string[]; update(slot.slot_id, { group_id, row_id, step_token }); }}>
              <option value={'["","",""]'}>Choose confirmed Matrix step</option>{state.context.steps.map(step => <option key={JSON.stringify([step.group_id, step.row_id, step.step_token])}
                value={JSON.stringify([step.group_id, step.row_id, step.step_token])}>Group {step.group_label} / Step {step.step_token} — {step.test_item}</option>)}</select></label>}
            <label>Specimen IDs for {slot.slot_id}<input value={draft[slot.slot_id].sample_ids.join(', ')} onChange={event => update(slot.slot_id, { sample_ids: event.target.value.split(',').map(value => value.trim()).filter(Boolean) })} /></label>
            <label>Stage for {slot.slot_id}<input placeholder="Before / after the named test" value={draft[slot.slot_id].stage} onChange={event => update(slot.slot_id, { stage: event.target.value })} /></label>
            <label>Evidence reason for {slot.slot_id}<input value={draft[slot.slot_id].reason} onChange={event => update(slot.slot_id, { reason: event.target.value })} /></label>
            <label className="report-batch-check"><input type="checkbox" checked={draft[slot.slot_id].accept_context_change || false}
              onChange={event => update(slot.slot_id, { accept_context_change: event.target.checked })} />I checked any intentional Group change from the old caption for {slot.slot_id}; the caption is not automatically rewritten</label>
            <label>Reuse reason for {slot.slot_id}<input placeholder="Required only when using this image more than once" value={draft[slot.slot_id].reuse_reason} onChange={event => update(slot.slot_id, { reuse_reason: event.target.value })} /></label>
            <label>Fit for {slot.slot_id}<select value={draft[slot.slot_id].crop_mode} onChange={event => update(slot.slot_id, { crop_mode: event.target.value as 'preserve' | 'centre_crop' })}>
              <option value="preserve">Preserve approved crop / aspect ratio</option><option value="centre_crop">Centre crop without stretching</option></select></label>
            {(slot.rotation !== 0 || slot.flip_horizontal || slot.flip_vertical) && <label className="report-batch-check"><input type="checkbox" checked={draft[slot.slot_id].accept_slot_transform}
              onChange={event => update(slot.slot_id, { accept_slot_transform: event.target.checked })} />Accept existing slot rotation/flips for {slot.slot_id}</label>}
          </div>}
          {images[slot.slot_id] && <div className="report-photo-comparison"><figure><img src={images[slot.slot_id][0]} alt={`Old source ${slot.slot_id}`} /><figcaption>Old source</figcaption></figure>
            <figure><img src={images[slot.slot_id][1]} alt={`New source ${slot.slot_id}`} /><figcaption>New source — confirm final crop in Word preview</figcaption></figure></div>}
        </>}
      </details>)}
      <button type="button" disabled={!valid} onClick={() => void compare()}>Compare all selected photos</button>
      <label className="report-batch-check"><input type="checkbox" checked={confirmed} disabled={!valid || selected.some(item => !images[item.slot_id])}
        onChange={event => setConfirmed(event.target.checked)} />I checked the selected photos, specimens, stages and any intentional reuse</label>
      <button type="button" disabled={!valid || !confirmed} onClick={() => void onConfirm(selected)}>Save confirmed photo mapping</button>
    </fieldset>{error && <p role="alert">{error}</p>}
  </section>;
}
