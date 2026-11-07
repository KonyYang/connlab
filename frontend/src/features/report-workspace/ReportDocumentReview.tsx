import { useEffect, useRef, useState } from 'react';
import { confirmReportPhotoPlan, confirmReportRegions, getReportDocumentReview,
  type ReportAuthoringState, type ReportDocumentReviewData } from '../../api/reportAuthoring';
import { ReportPhotoPlan } from './ReportPhotoPlan';
import { ReportVisualPreview } from './ReportVisualPreview';

export function ReportDocumentReview({ projectId, state, disabled, beginOperation, onChanged }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean;
  beginOperation?: () => (() => void) | null; onChanged: (state: ReportAuthoringState) => void;
}) {
  const [review, setReview] = useState<ReportDocumentReviewData | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [regionId, setRegionId] = useState('');
  const [sourceId, setSourceId] = useState('');
  const [locator, setLocator] = useState('');
  const [reason, setReason] = useState('');
  const [filter, setFilter] = useState('');
  const epoch = useRef(0);
  const output = state.outputs.at(-1);
  useEffect(() => { epoch.current++; setReview(null); setBusy(false); setError(''); setRegionId(''); setSourceId(''); setLocator(''); setReason(''); }, [projectId, state.revision]);
  useEffect(() => () => { epoch.current++; }, []);
  async function run(work: () => Promise<ReportAuthoringState | ReportDocumentReviewData>) {
    if (disabled || busy || state.project_id !== projectId) return;
    const release = beginOperation ? beginOperation() : () => undefined; if (!release) return;
    const token = ++epoch.current; setBusy(true); setError('');
    try {
      const value = await work();
      if (token !== epoch.current) return;
      if ('project_id' in value) { if (value.project_id === projectId) onChanged(value); }
      else if (value.output_id === output?.output_id && value.output_sha256 === output?.artifact?.sha256) setReview(value);
    } catch (cause) { if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Report review failed. Original files remain unchanged.'); }
    finally { release(); if (token === epoch.current) setBusy(false); }
  }
  if (!output?.artifact) return null;
  const identity = { expected_revision: state.revision, output_id: output.output_id, output_sha256: output.artifact.sha256 };
  const region = review?.region_groups.find(item => item.region_id === regionId);
  const matching = review?.region_groups.filter(item => !filter || `${item.kind} ${item.text} ${item.status}`.toLowerCase().includes(filter.toLowerCase())) || [];
  return <section className="report-document-review" aria-label="Approved original and visual review">
    <h4>Approved original, photos and Word preview</h4>
    <p>Working copy: {output.file_name}. Review inherited project content separately from layout. No global acknowledgement marks unknown content complete.</p>
    <button type="button" disabled={disabled || busy} onClick={() => void run(() => getReportDocumentReview(projectId, output.output_id, state.revision))}>Inspect original coverage and photo candidates</button>
    {busy && <p role="status">Checking this exact working version…</p>}{error && <p role="alert">{error}</p>}
    {review && <>
      <p role="status">{review.complete ? 'Evidence coverage checked — not release approval' : 'Content still needs verification'} · source role: {review.base_role}</p>
      {review.findings.length > 0 && <details><summary>{review.findings.length} unresolved findings</summary><ul>{review.findings.map((item, index) => <li key={index}>{item.location}: {item.message}</li>)}</ul></details>}
      <details><summary>Regional content checklist ({review.region_groups.length} sections; {review.regions.length} paragraphs inventoried)</summary>
        <label>Filter report regions<input value={filter} onChange={event => setFilter(event.target.value)} placeholder="identity, date, samples, results, conclusions…" /></label>
        <div className="report-review-scroll"><table><thead><tr><th>Region / role</th><th>Current text</th><th>Evidence status</th></tr></thead><tbody>
          {matching.map(item => <tr key={item.region_id}><td>{item.kind}<br />{item.paragraph_count} paragraphs</td><td><details><summary>{item.text.slice(0, 180)}</summary><pre style={{ whiteSpace: 'pre-wrap' }}>{item.text}</pre></details></td><td>{item.status}{item.reasons.map(message => <p key={message}>{message}</p>)}</td></tr>)}
        </tbody></table></div>
        <fieldset disabled={disabled || busy} className="report-review-fields"><legend>Confirm one exact inherited region against evidence</legend>
          <label>Report region<select value={regionId} onChange={event => setRegionId(event.target.value)}><option value="">Choose an unverified region</option>
            {review.region_groups.filter(item => item.status !== 'verified' && item.status !== 'conflict').map(item => <option key={item.region_id} value={item.region_id}>{item.kind} — {item.paragraph_count} paragraphs</option>)}</select></label>
          <label>Supporting source<select value={sourceId} onChange={event => setSourceId(event.target.value)}><option value="">Choose current project evidence</option>
            {state.sources.filter(item => item.source_id !== state.base_source_id).map(item => <option key={item.source_id} value={item.source_id}>{item.file_name}</option>)}</select></label>
          <label>Evidence location<input value={locator} onChange={event => setLocator(event.target.value)} placeholder="Sheet / cell / page / scope" /></label>
          <label>Applicability reason<input value={reason} onChange={event => setReason(event.target.value)} /></label>
          <button type="button" disabled={!region || !sourceId || !locator.trim() || !reason.trim()} onClick={() => void run(() => confirmReportRegions(projectId,
            { ...identity, review_sha256: review.review_sha256, confirmed_by: 'Lab User', decisions: [{ region_id: regionId, region_sha256: region!.sha256, source_id: sourceId, locator, reason }] }))}>Save this regional decision</button>
        </fieldset>
      </details>
      <details><summary>Figure numbering and reference preview</summary>
        <p>{review.numbering.ready ? 'Numbering can be selected in Prepare report batch.' : 'Some numbering needs Word review. Uncertain order is not guessed.'}</p>
        <ul>{review.figures.map(item => <li key={item.figure_id}>{item.caption} — {item.slot_ids.length} photo slot(s){item.reason && ` — ${item.reason}`}</li>)}</ul>
        <ul>{review.numbering.issues.map((item, index) => <li key={index}>{item.message}</li>)}</ul>
        <table><thead><tr><th>Existing label</th><th>Proposed label</th><th>Exact location</th></tr></thead><tbody>
          {review.numbering.replacements.map((item, index) => <tr key={index}><td>{item.old}</td><td>{item.new}</td><td>{item.target.part} / {item.target.paragraph}</td></tr>)}
        </tbody></table>
      </details>
      <ReportPhotoPlan key={`${projectId}/${output.output_id}`} projectId={projectId} state={state} review={review} disabled={disabled || busy}
        onConfirm={assignments => run(() => confirmReportPhotoPlan(projectId, { ...identity, review_sha256: review.review_sha256, confirmed_by: 'Lab User', assignments }))} />
    </>}
    <ReportVisualPreview projectId={projectId} state={state} disabled={disabled || busy} beginOperation={beginOperation} onChanged={onChanged} />
  </section>;
}
