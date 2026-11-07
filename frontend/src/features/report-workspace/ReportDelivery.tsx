import { useEffect, useRef, useState } from 'react';
import { getReportDelivery, confirmReportRetainedContent, saveReviewedReports, resumeReviewedReportSave,
  type ReportDeliveryPreview } from '../../api/reportAuthoringDelivery';
import type { ReportAuthoringState } from '../../api/reportAuthoring';
import { ReportVisualPreview } from './ReportVisualPreview';

export function ReportDelivery({ projectId, state, disabled, onChanged, beginOperation }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean; onChanged: (state: ReportAuthoringState) => void;
  beginOperation?: () => (() => void) | null;
}) {
  const [preview, setPreview] = useState<ReportDeliveryPreview | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [contentChecked, setContentChecked] = useState(false);
  const [notes, setNotes] = useState('');
  const sequence = useRef(0);
  const inspectedProject = useRef('');
  const dialog = useRef<HTMLDivElement>(null);
  const saveButton = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (confirming) dialog.current?.querySelector<HTMLButtonElement>('button')?.focus();
    else if (saveButton.current && !saveButton.current.disabled) saveButton.current.focus();
  }, [confirming]);
  useEffect(() => {
    const token = ++sequence.current;
    setPreview(null); setError(''); setConfirming(false); setContentChecked(false); setNotes(''); setBusy(false);
    if (inspectedProject.current === projectId) {
      void getReportDelivery(projectId).then(value => { if (token === sequence.current) setPreview(value); })
        .catch(cause => { if (token === sequence.current) setError(cause instanceof Error ? cause.message : 'Delivery checks unavailable.'); });
    }
    return () => { sequence.current++; };
  }, [projectId, state.revision]);
  async function inspect() {
    if (disabled || busy) return;
    inspectedProject.current = projectId;
    const token = ++sequence.current; setBusy(true); setError('');
    try {
      const value = await getReportDelivery(projectId);
      if (token === sequence.current) setPreview(value);
    } catch (cause) { if (token === sequence.current) setError(cause instanceof Error ? cause.message : 'Delivery checks unavailable.'); }
    finally { if (token === sequence.current) setBusy(false); }
  }
  async function run(work: () => Promise<ReportAuthoringState>) {
    if (disabled || busy || state.project_id !== projectId) return;
    const release = beginOperation ? beginOperation() : () => undefined; if (!release) return;
    const token = ++sequence.current; setBusy(true); setError('');
    try {
      const next = await work();
      if (token === sequence.current && next.project_id === projectId) { setConfirming(false); onChanged(next); }
    } catch (cause) {
      if (token === sequence.current) {
        setError(cause instanceof Error ? cause.message : 'Report save did not finish. Check status and resume.');
        const latest = await getReportDelivery(projectId).catch(() => null);
        if (token === sequence.current && latest) setPreview(latest);
      }
    } finally { release(); if (token === sequence.current) setBusy(false); }
  }
  const internal = state.outputs.at(-1);
  const customer = state.customer_outputs?.find(item => item.output_id === preview?.customer_output_id);
  if (!internal?.artifact) return null;
  const identity = { expected_revision: state.revision, output_id: internal.output_id, output_sha256: internal.artifact.sha256 };
  const operation = preview?.operation;
  return <section className="report-delivery" aria-label="Review and save reports"><h4>Review and save</h4>
    <p>Save this exact reviewed Internal Report and its matching customer copy to the registered project folder. This does not formally issue either report.</p>
    <p>Internal: {internal.file_name}{customer ? ` · Customer: ${customer.file_name}` : ' · Matching customer copy needed'}</p>
    <button type="button" disabled={disabled || busy} onClick={() => void inspect()}>Inspect delivery checks</button>
    {preview?.issues.length ? <ul>{preview.issues.map((issue, index) => <li key={`${issue.code}-${index}`}>{issue.message}</li>)}</ul> : preview && <p role="status">Delivery checks passed for the selected pair.</p>}
    {preview?.issues.some(item => item.code === 'content_review_required') && <fieldset disabled={disabled || busy}>
      <legend>Retained content of this project</legend><p>This confirmation cannot clear conflicting facts, missing results or inherited content from another project.</p>
      <label className="report-batch-check"><input type="checkbox" checked={contentChecked} onChange={event => setContentChecked(event.target.checked)} />I checked the retained content of this exact project report</label>
      <label>Content review notes<textarea value={notes} onChange={event => setNotes(event.target.value)} /></label>
      <button type="button" disabled={!contentChecked || !notes.trim() || !preview.review_sha256} onClick={() => void run(() => confirmReportRetainedContent(projectId,
        { ...identity, review_sha256: preview.review_sha256!, confirmed_by: 'Lab User', notes }))}>Record retained-content review</button>
    </fieldset>}
    {customer && <ReportVisualPreview projectId={projectId} state={state} outputId={customer.output_id}
      disabled={disabled || busy} beginOperation={beginOperation} onChanged={onChanged} />}
    {preview?.workspace && <ul>{preview.workspace.files.map(file => <li key={file.role}>{file.role}: {file.file_name}
      {file.archive_required ? ' — existing file retained in History/Report' : ' — new file'}</li>)}</ul>}
    {operation && <div role="status"><p>{operation.status === 'completed' ? (preview?.operation_matches_current
      ? 'Selected report pair saved — not formally issued.' : 'An earlier report version was saved; current delivery checks are separate.') : 'Report save unfinished; preserve the existing result and resume this operation.'}</p>
      <ul>{operation.items.map(item => <li key={item.role}>{item.file_name}: {item.status}</li>)}</ul>
      {operation.status !== 'completed' && <button type="button" disabled={disabled || busy} onClick={() => void run(() => resumeReviewedReportSave(projectId, operation.operation_id))}>Resume this report save</button>}
    </div>}
    <button ref={saveButton} type="button" disabled={disabled || busy || !preview?.can_save} onClick={() => setConfirming(true)}>Save reviewed reports to project folder</button>
    {confirming && preview?.can_save && <div className="report-workspace-dialog-backdrop"><div ref={dialog} className="report-workspace-dialog" role="dialog" aria-modal="true" aria-label="Confirm saving reviewed reports"
      onKeyDown={event => {
        if (event.key === 'Escape' && !busy) { event.preventDefault(); setConfirming(false); }
        if (event.key !== 'Tab') return;
        const controls = Array.from(event.currentTarget.querySelectorAll<HTMLButtonElement>('button:not(:disabled)'));
        const first = controls[0], last = controls.at(-1);
        if (!first) event.preventDefault();
        else if (event.shiftKey && document.activeElement === first && last) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }}>
      <h5>Save the reviewed pair?</h5><p>Only the two files listed above will be saved. Existing reports are preserved in History/Report. No report is formally issued.</p>
      <button type="button" disabled={busy} onClick={() => setConfirming(false)}>Cancel</button>
      <button type="button" disabled={disabled || busy || !customer || !preview.preview_sha256} onClick={() => void run(() => saveReviewedReports(projectId,
        { ...identity, customer_output_id: customer!.output_id, preview_sha256: preview.preview_sha256!, confirmed_by: 'Lab User' }))}>Confirm save</button>
    </div></div>}
    {busy && <p role="status">Saving reviewed report files…</p>}{error && <p role="alert">{error}</p>}
  </section>;
}
