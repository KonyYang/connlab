import { useEffect, useRef, useState, type ReactNode } from 'react';
import { getReportDelivery, confirmReportRetainedContent, saveReviewedReports, resumeReviewedReportSave,
  type ReportDeliveryPreview } from '../../api/reportAuthoringDelivery';
import type { ReportAuthoringState } from '../../api/reportAuthoring';
import { ReportVisualPreview } from './ReportVisualPreview';
import { ReportIssueActions, type ReportIssueSection } from './ReportIssueActions';

export function ReportDelivery({ projectId, state, disabled, onChanged, beginOperation, children, onOpenSection }: {
  projectId: string; state: ReportAuthoringState; disabled: boolean; onChanged: (state: ReportAuthoringState) => void;
  beginOperation?: () => (() => void) | null;
  children?: ReactNode;
  onOpenSection?: (section: ReportIssueSection) => void;
}) {
  const [preview, setPreview] = useState<ReportDeliveryPreview | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [contentChecked, setContentChecked] = useState(false);
  const [notes, setNotes] = useState('');
  const sequence = useRef(0);
  const [refresh, setRefresh] = useState(0);
  const dialog = useRef<HTMLDivElement>(null);
  const saveButton = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (confirming) dialog.current?.querySelector<HTMLButtonElement>('button')?.focus();
  }, [confirming]);
  function cancelSave() {
    setConfirming(false);
    saveButton.current?.focus();
  }
  useEffect(() => {
    const token = ++sequence.current;
    setPreview(null); setError(''); setConfirming(false); setContentChecked(false); setNotes(''); setBusy(false);
    if (state.project_id === projectId && (!state.delivery || state.delivery.status === 'completed')) {
      void getReportDelivery(projectId).then(value => { if (token === sequence.current) setPreview(value); })
        .catch(cause => { if (token === sequence.current) setError(cause instanceof Error ? cause.message : 'Delivery checks unavailable.'); });
    }
    return () => { sequence.current++; };
  }, [projectId, state.revision, refresh]);
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
        if (token === sequence.current) {
          setConfirming(false);
          setPreview(previous => latest ?? (previous?.operation && previous.operation.status !== 'completed' ? previous : null));
        }
      }
    } finally { release(); if (token === sequence.current) setBusy(false); }
  }
  const internal = state.outputs.at(-1);
  const customer = state.customer_outputs?.find(item => item.output_id === preview?.customer_output_id);
  const pending = state.delivery && state.delivery.status !== 'completed' ? state.delivery : null;
  const operation = pending || preview?.operation || state.delivery;
  if (operation && operation.status !== 'completed') return <section className="report-delivery" aria-label="Resume report save">
    <h3>Finish the previous save</h3>
    <ul>{operation.items.map(item => <li key={item.role}>{item.file_name} · {item.status}</li>)}</ul>
    <button type="button" className="primary-action" disabled={disabled || busy}
      onClick={() => void run(() => resumeReviewedReportSave(projectId, operation.operation_id))}>Resume this report save</button>
    {busy && <p role="status">Resuming report save…</p>}{error && <p role="alert">{error}</p>}
  </section>;
  if (!internal?.artifact) return null;
  const identity = { expected_revision: state.revision, output_id: internal.output_id, output_sha256: internal.artifact.sha256 };
  const saved = operation?.status === 'completed' && preview?.operation_matches_current;
  if (saved) return <section className="report-delivery" aria-label="Saved reports">
    <h3>Saved to the project folder</h3><p role="status">Selected report pair saved — not formally issued.</p>
    <ul>{operation.items.map(item => <li key={item.role}>{item.file_name}</li>)}</ul>
    {children}
  </section>;
  const ready = !!(preview?.can_save && customer && preview.preview_sha256);
  return <section className="report-delivery" aria-label="Review and save reports">
    <h3>{ready ? 'Save reviewed reports' : 'Checks before saving'}</h3>
    {!preview && !error && <p role="status">Checking the current report pair…</p>}
    {preview?.issues.length ? <ul aria-label="Required before saving">{preview.issues.map((issue, index) =>
      <li key={`${issue.code}-${index}`}>{issue.message}</li>)}</ul> : ready && <p role="status">Delivery checks passed for the selected pair.</p>}
    <ReportIssueActions issues={preview?.issues || []} onOpenSection={onOpenSection} disabled={disabled || busy} />
    {preview?.issues.some(item => item.code === 'content_review_required') && <fieldset disabled={disabled || busy}>
      <legend>Retained content of this project</legend><p>This confirmation cannot clear conflicting facts, missing results or inherited content from another project.</p>
      <label className="report-batch-check"><input type="checkbox" checked={contentChecked} onChange={event => setContentChecked(event.target.checked)} />I checked the retained content of this exact project report</label>
      <label>Content review notes<textarea value={notes} onChange={event => setNotes(event.target.value)} /></label>
      <button type="button" disabled={!contentChecked || !notes.trim() || !preview.review_sha256} onClick={() => void run(() => confirmReportRetainedContent(projectId,
        { ...identity, review_sha256: preview.review_sha256!, confirmed_by: 'Lab User', notes }))}>Record retained-content review</button>
    </fieldset>}
    {preview?.issues.some(issue => issue.code === 'internal_visual_required') &&
      <details><summary>Review Internal Report pages</summary><ReportVisualPreview projectId={projectId} state={state} outputId={internal.output_id}
        disabled={disabled || busy} beginOperation={beginOperation} onChanged={onChanged} /></details>}
    {customer && preview?.issues.some(issue => issue.code === 'customer_visual_required') &&
      <details><summary>Review customer copy pages</summary><ReportVisualPreview projectId={projectId} state={state} outputId={customer.output_id}
        disabled={disabled || busy} beginOperation={beginOperation} onChanged={onChanged} /></details>}
    {preview && operation?.status === 'completed' && <p>An earlier report version was saved; current delivery checks are separate.</p>}
    {ready && <button ref={saveButton} className="primary-action" type="button" disabled={disabled || busy} onClick={() => setConfirming(true)}>Save reviewed reports to project folder</button>}
    {(error || preview && !ready) && <button type="button" className="report-editor-link" disabled={disabled || busy} onClick={() => setRefresh(value => value + 1)}>Refresh save checks</button>}
    {confirming && ready && preview && <div className="report-workspace-dialog-backdrop"><div ref={dialog} className="report-workspace-dialog" role="dialog" aria-modal="true" aria-label="Confirm saving reviewed reports"
      onKeyDown={event => {
        if (event.key === 'Escape' && !busy) { event.preventDefault(); cancelSave(); }
        if (event.key !== 'Tab') return;
        const controls = Array.from(event.currentTarget.querySelectorAll<HTMLButtonElement>('button:not(:disabled)'));
        const first = controls[0], last = controls.at(-1);
        if (!first) event.preventDefault();
        else if (event.shiftKey && document.activeElement === first && last) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }}>
      <h4>Save these reports to the project folder?</h4>
      <ul>{preview.workspace?.files.map(file => <li key={file.role}>{file.destination || file.file_name}
        {file.archive_required ? ' — existing report will move to History/Report' : ' — new file'}</li>)}</ul>
      <p>Both documents will be saved as reviewed copies. Formal issue is a separate step.</p>
      <button type="button" disabled={busy} onClick={cancelSave}>Cancel</button>
      <button type="button" disabled={disabled || busy || !customer || !preview.preview_sha256} onClick={() => void run(() => saveReviewedReports(projectId,
        { ...identity, customer_output_id: customer!.output_id, preview_sha256: preview.preview_sha256!, confirmed_by: 'Lab User' }))}>Confirm save</button>
    </div></div>}
    {busy && <p role="status">Saving report review…</p>}{error && <p role="alert">{error}</p>}
    {preview && !busy && children}
  </section>;
}
