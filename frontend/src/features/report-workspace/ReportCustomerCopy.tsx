import { useEffect, useRef, useState } from 'react';
import { generateCustomerReviewCopy, downloadCustomerPart, downloadReportArtifact,
  type CustomerReportOutput, type ReportAuthoringState } from '../../api/reportAuthoring';
import { CustomerDisclosureReview } from './CustomerDisclosureReview';
import { ReportDelivery } from './ReportDelivery';
import type { ReportIssueSection } from './ReportIssueActions';
import './reportCustomerCopy.css';

type Props = {
  projectId: string; state: ReportAuthoringState; disabled: boolean; onChanged: (state: ReportAuthoringState) => void;
  beginOperation?: () => (() => void) | null;
  onOpenSection?: (section: ReportIssueSection) => void;
};

export function ReportCustomerCopy(props: Props) {
  const { projectId, state, disabled, onChanged, beginOperation } = props;
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [editingReview, setEditingReview] = useState(false);
  const epoch = useRef(0);
  const output = state.outputs.at(-1);
  const previous = state.customer_outputs?.at(-1);
  const customer = state.customer_outputs?.slice().reverse().find(item => item.parent_output_id === output?.output_id);
  const interrupted = !!state.delivery && state.delivery.status !== 'completed';
  useEffect(() => {
    setBusy(false); setError(''); setEditingReview(false);
    return () => { epoch.current++; };
  }, [projectId, state.revision]);

  async function run(action: () => Promise<void>) {
    if (disabled || busy || state.project_id !== projectId) return;
    const release = beginOperation ? beginOperation() : () => undefined;
    if (!release) return;
    const token = epoch.current;
    setBusy(true); setError('');
    try { await action(); }
    catch (cause) {
      if (token === epoch.current) setError(cause instanceof Error ? cause.message : 'Unable to complete the customer copy action.');
    } finally { release(); if (token === epoch.current) setBusy(false); }
  }
  function update(action: () => Promise<ReportAuthoringState>) {
    const token = epoch.current;
    void run(async () => {
      const next = await action();
      if (token === epoch.current && next.project_id === projectId) onChanged(next);
    });
  }
  function download(copy: CustomerReportOutput, part?: string) {
    const token = epoch.current;
    void run(async () => {
      const file = part ? await downloadCustomerPart(projectId, copy.output_id, part) : await downloadReportArtifact(copy.download_url);
      if (token !== epoch.current) return;
      const url = URL.createObjectURL(file.blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.fileName || part?.split('/').at(-1) || copy.file_name;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  }
  if (interrupted) return <ReportDelivery {...props} />;
  if (!output) return null;
  const checked = customer?.status === 'package_checked' && customer.audit?.passed;
  const reviewContextChanged = customer?.audit?.issues.some(issue => issue.code === 'review_context_changed') ?? false;
  const temperatures = (state.results || []).filter(item => item.kind === 'temperature' && state.applied_result_ids?.includes(item.result_id!));
  function generate() {
    if (!output?.artifact) return;
    const request = { expected_revision: state.revision, output_id: output.output_id, output_sha256: output.artifact.sha256,
      temperature_result_ids: temperatures.map(result => result.result_id!) };
    update(() => generateCustomerReviewCopy(projectId, request));
  }
  const regenerate = <details><summary>Generate another copy</summary>
    <p>Create a fresh customer copy from {output.file_name} using the current template.</p>
    <button type="button" className="secondary-action" disabled={disabled || busy || !output.artifact} onClick={generate}>Generate again</button>
  </details>;
  return <section className="report-customer-copy" aria-label="Customer report review copy">
    {!customer ? <>
      <h3>{previous ? 'Update the customer copy' : 'Create a customer copy'}</h3>
      <p>{previous ? 'The existing copy was generated from an earlier working version.' : 'Generate a review copy using the E-4515 template.'}</p>
      <p className="report-customer-copy-source">Internal report · <strong>{output.file_name}</strong></p>
      {temperatures.length > 0 && <p>Includes temperature tables and curves for {temperatures.map(result =>
        `Group ${result.target.group_label} / Step ${result.target.step_token}`).join(', ')}.</p>}
      <div className="report-customer-copy-actions">
        <button className="primary-action" type="button" disabled={disabled || busy || !output.artifact} onClick={generate}>
          {previous ? 'Generate updated customer copy' : 'Generate customer review copy'}</button>
        {previous && <button className="report-editor-link" type="button" disabled={disabled || busy} onClick={() => download(previous)}>Download previous customer copy</button>}
      </div>
    </> : <>
      <header className="report-customer-copy-header">
        <strong>{customer.file_name}</strong>
        <button className="report-editor-link" type="button" disabled={disabled || busy} onClick={() => download(customer)}>Download customer review copy</button>
      </header>
      {checked && !editingReview ?
        <ReportDelivery {...props} disabled={disabled || busy}>
          <button className="report-editor-link" type="button" disabled={disabled || busy} onClick={() => setEditingReview(true)}>Review disclosure checks again</button>
          {regenerate}
        </ReportDelivery> :
        <>
          <CustomerDisclosureReview key={`${projectId}/${customer.output_id}/${state.revision}/${reviewContextChanged}`}
            projectId={projectId} revision={state.revision} internal={output} customer={customer}
            disabled={disabled || busy} check={update} downloadPart={part => download(customer, part)} onOpenSection={props.onOpenSection} />
          {editingReview && <button type="button" className="report-editor-link" disabled={disabled || busy} onClick={() => setEditingReview(false)}>Discard review edits</button>}
          {regenerate}
        </>}
    </>}
    {busy && <p role="status">Preparing customer copy…</p>}
    {error && <p className="report-customer-copy-error" role="alert">{error}</p>}
  </section>;
}
